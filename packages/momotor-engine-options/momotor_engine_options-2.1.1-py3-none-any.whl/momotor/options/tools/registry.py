import collections.abc
import functools
import logging
import os
import pathlib
import textwrap
import typing

from momotor.options.tools.tool import ToolName, Tool, match_tool

if typing.TYPE_CHECKING:
    from .types import PathList, PathTuple, StrPathOrToolName

__all__ = [
    'tool_registry_paths', 'resolve_tool', 'registered_tools',
    'TOOL_REGISTRY_ENVNAME',
]


TOOL_REGISTRY_ENVNAME = 'TOOLREGISTRY'
DEFAULT_TOOL_REGISTRY_LOCATION = ['~/.toolregistry.d', '/etc/toolregistry.d']

logger = logging.getLogger(__name__)


def need_posix(f: collections.abc.Callable) -> collections.abc.Callable:
    """ Decorator that will throw an assertion error if the current system is not a Posix system
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        assert os.name == 'posix', 'Tool registry only supported on Posix systems'
        return f(*args, **kwargs)

    doc = wrapper.__doc__
    if doc:
        doc = textwrap.dedent(doc) + '\n\n'
    else:
        doc = ''

    wrapper.__doc__ = doc + '*Only available on Posix systems, does not work on Windows*'
    return wrapper


def tool_registry_paths(paths: "PathList" = None, include_default_paths: bool = True) \
        -> collections.abc.Iterable[pathlib.Path]:
    """ Collect the tool registry paths
    """
    paths = list(paths) if paths is not None else list()

    if include_default_paths:
        tool_registry: str = os.environ.get(TOOL_REGISTRY_ENVNAME)
        if tool_registry:
            paths.extend(tool_registry.split(':'))
        elif tool_registry is None:
            paths.extend(DEFAULT_TOOL_REGISTRY_LOCATION)

    logger.debug(f'tool registry locations: {", ".join(str(p) for p in paths)}')

    for path in paths:
        if isinstance(path, str):
            path = path.strip()

        path = pathlib.Path(path).expanduser().absolute()
        if path.exists():
            yield path
        else:
            logger.debug(f'tool registry path does not exist: {path!s}')


def _is_candidate(path: pathlib.Path):
    name = path.name
    return not (name.startswith('.') or name.endswith('~'))


@functools.lru_cache(maxsize=1)
def _registered_tools(
        paths: "PathTuple" = None, *,
        include_default_paths: bool = True,
        include_missing: bool = False,
) -> dict[ToolName, Tool]:
    """ Implementation of :py:func:`registered_tools`
    """
    logger.debug(f'reading tool registries')

    tools: dict[ToolName, Tool] = {}
    for registry_path in tool_registry_paths(paths, include_default_paths):
        logger.debug(f'reading tool registry {registry_path!s}')
        for tool_file_path in registry_path.rglob('*'):
            if not tool_file_path.is_file() or not _is_candidate(tool_file_path):
                continue

            alias_file_name = tool_file_path.relative_to(registry_path)
            try:
                tool_file_name = tool_file_path.resolve(True).relative_to(registry_path)
            except FileNotFoundError:
                logger.warning(f'unable to resolve symlink {alias_file_name!s} in registry {registry_path!s}')
                continue

            tool_name = ToolName(tool_file_name)
            if tool_name not in tools:
                try:
                    tool = Tool.from_file_factory(registry_path, tool_file_name)
                except Exception as e:
                    logger.warning(f'unable to read {tool_file_name!s} in registry {registry_path!s}: {e} ')
                    continue

                if not tool.exists() and not include_missing:
                    logger.warning(f'ignoring tool {tool_file_name!s} in registry {registry_path!s}: tool not found')
                    continue

                assert tool_name == tool.name
                tools[tool.name] = tool

            alias_name = ToolName(alias_file_name)
            if alias_name not in tools:
                tools[alias_name] = tools[tool_name]

    return tools


@need_posix
def registered_tools(
        paths: "PathList" = None, *,
        include_default_paths: bool = True,
        include_missing: bool = False,
) -> dict[ToolName, Tool]:
    """
    Return a mapping with all locally installed tools.

    If **include_default_paths** is `True` (default), this reads the tool registry from `.toolregistry.d` in
    the current user's home directory and `/etc/toolregistry.d`. If **paths** is provided, registry will be read from
    all paths in the path list as well.

    :param paths: paths to read the tool registry from. prepended to the default paths
    :param include_default_paths: include the default paths
    :param include_missing: include tools that are registered but the executable does not actually exist
    :return: a mapping from tool name to tool dataclass
    """

    return _registered_tools(
        tuple(paths) if paths is not None else None,
        include_default_paths=include_default_paths,
        include_missing=include_missing,
    )


@need_posix
def resolve_tool(name: "StrPathOrToolName", *, paths: "PathList" = None, include_default_paths: bool = True) -> Tool:
    """
    Resolve a tool **name** to a :py:class:`~momotor.options.tools.tool.Tool` dataclass.

    If **include_default_paths** is `True` (default), this reads the tool registry from `.toolregistry.d` in
    the current user's home directory and `/etc/toolregistry.d`. If **paths** is provided, registry will be read from
    all paths in the path list as well.

    :param name: Name of the tool to resolve
    :param paths: paths to read the tool registry from. prepended to the default paths
    :param include_default_paths: include the default paths
    :return: The tool info object.
    :raises FileNotFoundError: if the name could not be resolved
    """
    name = ToolName.factory(name)
    registry = registered_tools(
        paths,
        include_default_paths=include_default_paths,
        include_missing=False,
    )

    if name in registry:
        logger.debug(f'tool {name} found in registry')
        return registry[name]

    matched_name = match_tool(name, registry.keys())
    if matched_name:
        logger.debug(f'tool {name} found in registry (as {matched_name})')
        return registry[matched_name]

    logger.warning(f'tool {name} not found in registry')
    raise FileNotFoundError
