from __future__ import annotations

import collections
import collections.abc
import dataclasses
import functools
import logging
import os
import pathlib
import typing
from string import Template

from typing_extensions import TypeAlias  # Python 3.10+

from .version import ToolVersion, default_tool_version

if typing.TYPE_CHECKING:
    from .types import StrPathOrToolName, ToolRequirements, ToolSet

__all__ = ['ToolName', 'Tool', 'match_tool', 'match_tool_requirements']

logger = logging.getLogger(__name__)


TN = typing.TypeVar('TN', bound="ToolName")

ToolVersions: TypeAlias = tuple[ToolVersion, ...]


@functools.total_ordering
@dataclasses.dataclass(frozen=True, init=False)
class ToolName:
    """ Represents a tool name as a tuple of :py:class:`~momotor.options.tools.version.ToolVersion` objects

    Instantiated from a tool file name (either a :py:class:`str`, :py:class:`pathlib.PurePath`, or another
    :py:class:`ToolName`), it splits all the parts of the tool name and represents each part as a
    :py:class:`~momotor.options.tools.version.ToolVersion`, and allows these names to be compared and ordered.

    >>> ToolName('test') == ToolName('test/_')
    True

    >>> ToolName('test/1.0') < ToolName('test/2.0')
    True

    """

    #: Constant for the separator between name elements
    SEPARATOR: typing.ClassVar[str] = '/'

    #: Constant for the default file name
    DEFAULT_FILENAME: typing.ClassVar[str] = '_default'

    #: The tool name
    name: str

    _versions: ToolVersions = dataclasses.field(repr=False)

    def __init__(self, name: "StrPathOrToolName"):
        if isinstance(name, str):
            versions = None

        elif isinstance(name, ToolName):
            name, versions = name.name, name._versions

        elif isinstance(name, pathlib.PurePath):
            if name.is_absolute():
                raise ValueError

            name, versions = self.SEPARATOR.join(
                ToolVersion.DEFAULT if part == self.DEFAULT_FILENAME else part
                for part in name.parts
            ), None

        else:
            raise TypeError

        object.__setattr__(self, 'name', name)
        object.__setattr__(self, '_versions', versions)

    @classmethod
    @typing.overload
    def factory(cls: type[TN], name: "StrPathOrToolName") -> TN:
        ...

    @classmethod
    @typing.overload
    def factory(cls: type[TN], name: typing.Union[str, ToolVersion],
                *parts: str | ToolVersion) -> TN:
        ...

    @classmethod
    def factory(cls: type[TN], name: typing.Union["StrPathOrToolName", ToolVersion],
                *parts: str | ToolVersion) -> TN:
        """ Helper factory to create a :py:class:`ToolName` from a :py:class:`str`, :py:class:`pathlib.PurePath`,
        another :py:class:`ToolName`, or a sequence of :py:class:`str` or
        :py:class:`~momotor.options.tools.version.ToolVersion` elements.

        If **name** is a :py:class:`ToolName`, returns **name** unmodified, otherwise instantiates
        a new :py:class:`ToolName` object for the given name.
        """
        if parts or isinstance(name, ToolVersion) or (isinstance(name, str) and cls.SEPARATOR not in name):
            if not isinstance(name, (ToolVersion, str)):
                raise TypeError
            return cls(cls.SEPARATOR.join([str(name)] + [str(part) for part in parts]))
        elif isinstance(name, cls):
            return name
        else:
            return cls(name)

    @property
    def versions(self) -> ToolVersions:
        """ A tuple representing the :py:attr:`name` split on the :py:const:`~ToolName.SEPARATOR`
        and each part converted to a :py:class:`~momotor.options.tools.version.ToolVersion`.
        """
        if self._versions is None:
            versions = tuple(
                ToolVersion(part)
                for part in self.name.split(self.SEPARATOR)
            )
            object.__setattr__(self, '_versions', versions)

        return self._versions

    def __pad_versions(self, other: "StrPathOrToolName") -> tuple[ToolVersions, ToolVersions]:
        """ Get the versions tuples from `self` and `other`, making them the exact same size by
        padding the shortest version with the default
        """
        self_versions = self.versions
        other_versions = ToolName.factory(other).versions

        size_diff = len(self_versions) - len(other_versions)
        if size_diff:
            padding = tuple([default_tool_version] * abs(size_diff))
            if size_diff > 0:
                other_versions += padding
            else:
                self_versions += padding

        return self_versions, other_versions

    def is_partial(self, other: "StrPathOrToolName") -> bool:
        """ Checks if all elements of :py:attr:`self.versions <versions>` are the same or a partial version of
        :py:attr:`other.versions <versions>`.

        >>> ToolName('test').is_partial(ToolName('test/1.0'))
        True

        >>> ToolName('test/1').is_partial(ToolName('test/1.0'))
        True

        >>> ToolName('test/1.0').is_partial(ToolName('test/1.0'))
        True

        >>> ToolName('test/1.0').is_partial(ToolName('test'))
        False

        >>> ToolName('test').is_partial(ToolName('test.1'))
        False

        """
        self_versions, other_versions = self.__pad_versions(other)
        if self_versions[0] != other_versions[0]:
            return False

        for si, oi in zip(self_versions[1:], other_versions[1:]):
            if not si.is_partial(oi):
                return False

        return True

    def __eq__(self, other: "StrPathOrToolName") -> bool:
        self_versions, other_versions = self.__pad_versions(other)
        return self_versions == other_versions

    def __lt__(self, other: "StrPathOrToolName") -> bool:
        self_versions, other_versions = self.__pad_versions(other)
        return self_versions < other_versions

    def __hash__(self):
        return hash(self.versions)

    def __str__(self):
        return self.name


@functools.total_ordering
@dataclasses.dataclass(frozen=True)
class Tool:
    """ Data class representing the contents of a tool registry file.
    """

    #: Canonical name of the tool after resolving soft links
    name: ToolName

    #: Environment variables for the tool as indicated by the tool file
    environment: collections.abc.Mapping[str, str]

    #: Path to the tool as indicated by the tool file
    path: pathlib.Path

    # Cached `path.exists`
    _exists_cache: bool = dataclasses.field(init=False, hash=False, default=None)

    @classmethod
    def from_file_factory(cls, registry_path: pathlib.Path, tool_file_path: pathlib.PurePath) -> "Tool":
        """ Read a :ref:`tool registry file <tool registry file>` file and return a populated :py:class:`Tool`
        dataclass.

        :param registry_path: path to the registry
        :param tool_file_path: path to the tool file, relative to `registry_path`
        :return: the tool
        """
        path = registry_path / tool_file_path
        tool_name = ToolName(tool_file_path)

        lines = path.read_text().splitlines()

        tool_path = None
        while not tool_path:
            try:
                tool_path = _unquote(lines.pop(-1).strip())
            except IndexError:
                break

        environment = collections.ChainMap({}, os.environ)
        for lineno, env_line in enumerate(lines):
            key, sep, value = env_line.partition('=')
            if sep:
                # noinspection PyBroadException
                try:
                    environment[key.strip()] = Template(
                        _unquote(value.strip())
                    ).safe_substitute(
                        environment
                    ) or None
                except Exception:
                    pass
                else:
                    continue

            logger.warning(f'invalid environment definition ignored ({path!s}:{lineno + 1}) {env_line!r}')

        tool_path = pathlib.Path(
            Template(tool_path).safe_substitute(environment)
        ).expanduser().resolve()

        # if logger.isEnabledFor(logging.DEBUG):
        #     logger.debug(f'tool {tool_name!r} resolved to {tool_path!s} (using {path!s})')
        #     for key, value in environment.items():
        #         logger.debug(f'tool {tool_name!r} environment {key}={value}')

        return cls(tool_name, environment.maps[0], tool_path)

    def exists(self) -> bool:
        """ Shortcut for :py:meth:`path.exists() <pathlib.Path.exists>`. Result is cached.

        :return: `True` if the tool exists.
        """
        exists = self._exists_cache
        if exists is None:
            exists = self.path.exists()
            object.__setattr__(self, '_exists_cache', exists)

        return exists

    def __eq__(self, other: "Tool") -> bool:
        return self.exists() == other.exists() and self.name == other.name

    def __lt__(self, other: "Tool") -> bool:
        self_exists, other_exists = self.exists(), other.exists()
        if self_exists == other_exists:
            return self.name < other.name
        else:
            return other_exists

    def __hash__(self):
        return hash((self.exists(), self.name))


def _unquote(value: str) -> str:
    """

    >>> _unquote('')
    ''

    >>> _unquote('no quotes')
    'no quotes'

    >>> _unquote('  unquoted space is stripped  ')
    'unquoted space is stripped'

    >>> _unquote('"quoted"')
    'quoted'

    >>> _unquote("'quoted'")
    'quoted'

    >>> _unquote('"  quoted keeps all space  "')
    '  quoted keeps all space  '

    >>> _unquote('  "leading and trailing space is ignored"  ')
    'leading and trailing space is ignored'

    >>> _unquote('"quoted" with trailing')
    'quoted'

    >>> _unquote(r'"quoted \\"with escape\\""')
    'quoted "with escape"'

    >>> _unquote('"unbalanced')
    '"unbalanced'

    :param value:
    :return:
    """
    # If value starts with a quote, find the matching end-quote and ignore everything after that,
    # ignoring backslash-escaped quotes
    idx, vl = 0, len(value)
    while idx < vl and value[idx] in ' \t':
        idx += 1

    if idx < vl:
        q = value[idx]
        if q in '"\'':
            c, lc, qv = '', '', ''
            idx += 1
            while idx < vl:
                qv += c
                lc, c = c, value[idx]
                if c == q:
                    if lc != '\\':
                        return qv

                    qv = qv[:-1]

                idx += 1

    return value.strip()


def match_tool(
        name: "StrPathOrToolName",
        tools: collections.abc.Iterable["StrPathOrToolName"]
) -> typing.Optional["StrPathOrToolName"]:
    """
    Match tool **name** with :py:const:`~~momotor.options.tools.version.ToolVersion.DEFAULT` placeholders
    and (partial) version numbers to a tool name in the **tools** container.

    Returns the most specific matched name from **tools**, or `None` if no match could be made.

    :param name: Name of the tool to match
    :param tools: An iterable of tool names to match `name` against
    :return: The matched name from **tools**, or `None`
    """
    name, best_name, best_candidate = ToolName.factory(name), None, None
    for cname in tools:
        candidate = ToolName.factory(cname)
        if name.is_partial(candidate) and (best_candidate is None or candidate > best_candidate):
            best_name, best_candidate = cname, candidate

    return best_name


def match_tool_requirements(
        requirements: "ToolRequirements",
        toolset: "ToolSet"
) -> dict[str, "StrPathOrToolName"]:
    """
    Match tools in **requirements** with tools in **tools** using :py:func:`match_tool` and return
    a sequence with the most specific matched.

    :param requirements: tool requirements
    :param toolset: list of available tools
    :return: mapping of requirement name (key of the `requirements` mapping) to matched tool name
    :raises ValueError: when requirements cannot be fulfilled
    """
    matches: dict[str, "StrPathOrToolName"] = {}

    for req_name, req_tools in requirements.items():
        match: typing.Optional["StrPathOrToolName"] = None

        for req_tool in req_tools:
            match = match_tool(req_tool, toolset)
            if match:
                matches[req_name] = match
                break

        if not match:
            raise ValueError(f"cannot match {req_name!s}")

    return matches
