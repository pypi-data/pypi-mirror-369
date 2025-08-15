import collections.abc
import operator
import re
import typing

from momotor.options.task_id import ID_RE_STR
from typing_extensions import TypeAlias  # Python 3.10+

MOD_RE = re.compile(
    r"^\s*"
    r"(?:%(?P<mod>[\w-]+))?"
)

VALUE_ATTR: dict[typing.Optional[str], str] = {
    'file': 'name',
    'prop': 'value',
    'opt': 'value',
    'result': 'outcome',
    None: 'step_id',  # Outcome types
}

REFERENCE_RE = re.compile(
    r"^\s*"
    r"(?P<type>[\w-]+)"
    r"\s*"
    r"(?P<opt>\[([^]]*)])?"
)

REF_OPTION_RE = re.compile(
    r'^(?:'
        r'@(?P<provider>[\w-]+)'
    r')?'
    r'\s*'
    r'(?:'
        rf'#\s*(?P<ids>{ID_RE_STR}(?:\s*,\s*{ID_RE_STR})*)'
    r')?'
    r'\s*'
    r'(?:'
        r':\s*(?P<name>(?:[^\'",\s]+|"[^"]*"|\'[^\']*\')*)'
    r')?'
)

OperatorCallable: TypeAlias = collections.abc.Callable[[typing.Any, typing.Any], bool]

# All operators and functions to check them
OPERATIONS: dict[typing.Optional[str], OperatorCallable] = {
    None: lambda prop_value, value: True,
    '?': lambda prop_value, value: bool(prop_value),
    '!': lambda prop_value, value: not bool(prop_value),
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le
}

# These operators should have no value
OPERATIONS_WITHOUT_VALUE: frozenset[typing.Optional[str]] = frozenset([None, '!', '?'])

OPERATORS: list[str] = sorted(
    (op for op in OPERATIONS.keys() if op),
    key=lambda op: (len(op), op),
    reverse=True
)

CONDITION_RE = re.compile(
    r"(?P<oper>" + '|'.join(re.escape(op) for op in OPERATORS) + r")?"  # operator
    r"(?(oper)(?P<value>"
        r"[+-]?(?:0|[123456789][\d_]*)(?:\.(?:0|[123456789][\d_]*))?(?:e[+-]?(?:0|[123456789][\d_]*))?"  # int or float
        r"|'[^']*'"  # single-quoted string
        r'|"[^"]*"'  # double-quoted string
        r'|'  # empty                                                         
    r"))"  # value, only if an oper group exists
)
