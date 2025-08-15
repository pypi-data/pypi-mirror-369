from __future__ import annotations

import dataclasses
import functools
import typing


def _partial_tuple(left: tuple, right: tuple) -> bool:
    """ Returns True if `left` is equal to or a partial version of `right`.
    """
    if len(left) > len(right):
        return False

    for le, re in zip(left, right):
        if le != re:
            if isinstance(le, tuple) and isinstance(re, tuple):
                if not _partial_tuple(le, re):
                    return False
            else:
                return False

    return True


@functools.total_ordering
@dataclasses.dataclass(frozen=True, init=False)
class ToolVersion:
    """ Represents a tool version string (i.e., a string with dotted version-number parts)
    and makes it possible to order these. Also handles sub-version suffixes like 1.0-0, 1.0-1, 1.0-2, etc.

    :py:const:`ToolVersion.DEFAULT` is a version constant which is always better than any other version number.

    >>> _test = lambda x, y: (x < y, x == y, x > y)

    >>> _test(ToolVersion('1'), ToolVersion('2'))
    (True, False, False)

    >>> _test(ToolVersion('1'), ToolVersion('1.1'))
    (True, False, False)

    >>> _test(ToolVersion('1.0'), ToolVersion('1.1'))
    (True, False, False)

    >>> _test(ToolVersion('1.0'), ToolVersion('1.x'))
    (False, False, True)

    >>> _test(ToolVersion('1.x'), ToolVersion('1.x'))
    (False, True, False)

    >>> _test(ToolVersion('1.0'), ToolVersion('1.0'))
    (False, True, False)

    >>> _test(ToolVersion('1.1'), ToolVersion('1.0'))
    (False, False, True)

    >>> _test(ToolVersion('1.1'), ToolVersion('2'))
    (True, False, False)

    >>> _test(ToolVersion('1.00'), ToolVersion('1.0'))
    (False, True, False)

    >>> _test(ToolVersion('1.09'), ToolVersion('1.10'))
    (True, False, False)

    >>> _test(ToolVersion('1.0'), ToolVersion('1.0-0'))
    (True, False, False)

    >>> _test(ToolVersion('1.0'), ToolVersion('1.0-1'))
    (True, False, False)

    >>> _test(ToolVersion('1.0-0'), ToolVersion('1.0-1'))
    (True, False, False)

    >>> _test(ToolVersion('1.0-0'), ToolVersion('1.1'))
    (True, False, False)

    >>> _test(ToolVersion(ToolVersion.DEFAULT), ToolVersion('1'))
    (False, False, True)

    >>> _test(ToolVersion('1'), ToolVersion(ToolVersion.DEFAULT))
    (True, False, False)

    >>> _test(ToolVersion(ToolVersion.DEFAULT), ToolVersion(ToolVersion.DEFAULT))
    (False, True, False)

    """
    #: Constant indicating a default version
    DEFAULT: typing.ClassVar[str] = '_'

    #: The original value
    value: str

    _version: tuple[str | tuple[int, ...]] = dataclasses.field(repr=False)

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError
        elif not value:
            raise ValueError

        object.__setattr__(self, 'value', value)
        object.__setattr__(self, '_version', None)

    @property
    def version(self) -> tuple[str | tuple[int, ...]]:
        """ A tuple representing the :py:attr:`value` split on the dot and dash characters (``.``, ``-``)
        and each part converted to :py:class:`int` if possible, and otherwise a :py:class:`str`.

        The special value :py:const:`~ToolVersion.DEFAULT` is converted into an empty tuple.
        """
        def _convert(value):
            if value != self.DEFAULT:
                for part in value.split('.'):
                    try:
                        yield tuple(int(subpart) for subpart in part.split('-'))
                    except ValueError:
                        yield part

        if self._version is None:
            object.__setattr__(self, '_version', tuple(_convert(self.value)))

        return self._version

    def is_partial(self, other: "ToolVersion") -> bool:
        """ Returns `True` if **self** is equal to or a partial version of **other**.

        >>> ToolVersion('1').is_partial(ToolVersion('1'))
        True

        >>> ToolVersion('1').is_partial(ToolVersion('1.0'))
        True

        >>> ToolVersion('1').is_partial(ToolVersion('1.0-0'))
        True

        >>> ToolVersion('1.0').is_partial(ToolVersion('1.0-0'))
        True

        >>> ToolVersion('1.0').is_partial(ToolVersion('1'))
        False

        >>> ToolVersion('2').is_partial(ToolVersion('1.0'))
        False

        >>> ToolVersion('1').is_partial(default_tool_version)
        False

        >>> default_tool_version.is_partial(ToolVersion('1'))
        True

        >>> default_tool_version.is_partial(default_tool_version)
        True

        """
        return _partial_tuple(self.version, other.version)

    def is_default(self) -> bool:
        return self.value == self.DEFAULT

    def __eq__(self, other: "ToolVersion") -> bool:
        return self.version == other.version

    def __lt__(self, other: "ToolVersion") -> bool:
        # Default version (empty version tuple) is better than any explicit version
        if not self.version:
            return False
        elif not other.version:
            return True

        # Python throws a TypeError when attempting to do __lt__ between different types
        # (i.e., `self.version < other.version` will not work for all cases), so we check each element pair
        # separately
        for el1, el2 in zip(self.version, other.version):
            if el1 != el2:
                if isinstance(el1, tuple) and isinstance(el2, tuple):
                    for p1, p2 in zip(el1, el2):
                        if p1 != p2:
                            return p1 < p2

                    return len(el1) < len(el2)

                elif isinstance(el1, str) and isinstance(el2, str):
                    return el1 < el2

                else:
                    return isinstance(el1, str)  # named versions are less than numeric versions

        return len(self.version) < len(other.version)

    def __hash__(self):
        return hash(self.version)

    def __str__(self):
        return self.value


#: Constant :py:attr:`ToolVersion(ToolVersion.DEFAULT) <ToolVersion.DEFAULT>`
default_tool_version = ToolVersion(ToolVersion.DEFAULT)
