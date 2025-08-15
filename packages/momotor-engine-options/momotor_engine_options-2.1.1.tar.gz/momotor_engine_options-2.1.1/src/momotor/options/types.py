from __future__ import annotations

import collections.abc
import typing

from typing_extensions import TypeAlias  # Python 3.10+


StepTasksType: TypeAlias = collections.abc.Sequence[int]
StepTaskNumberType: TypeAlias = "StepTasksType | None"

#: A list of all valid option type literals
OptionTypeLiteral: TypeAlias = typing.Literal['string', 'boolean', 'integer', 'float']

#: A list of all deprecated option type literals
OptionDeprecatedTypeLiteral: TypeAlias = typing.Literal['str', 'bool', 'int']

#: A list of all valid option location literals
LocationLiteral: TypeAlias = typing.Literal['step', 'recipe', 'config', 'product']

#: Type alias for subdomain definition
SubDomainDefinitionType: TypeAlias = collections.abc.Mapping[
    LocationLiteral,
    "str | collections.abc.Sequence[str| None] | None"
]
