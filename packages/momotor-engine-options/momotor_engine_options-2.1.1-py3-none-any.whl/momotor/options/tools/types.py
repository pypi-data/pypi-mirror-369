import collections.abc
from os import PathLike

from typing_extensions import TypeAlias  # Python 3.10-3.11

from .tool import ToolName

PathList: TypeAlias = "collections.abc.Iterable[str | PathLike] | None"
PathTuple: TypeAlias = "collections.abc.Sequence[str | PathLike] | None"
StrPathOrToolName: TypeAlias = "str | PathLike | ToolName"
ToolSet: TypeAlias = collections.abc.Set[StrPathOrToolName]
ToolRequirements: TypeAlias = collections.abc.Mapping[str, ToolSet]
