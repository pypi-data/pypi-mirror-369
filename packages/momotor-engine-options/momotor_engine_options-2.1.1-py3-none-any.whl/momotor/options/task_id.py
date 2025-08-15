""" Methods to handle task id's
"""
from __future__ import annotations

import collections.abc
import itertools
import operator
import re
from collections import deque
from dataclasses import dataclass

from momotor.options.exception import InvalidDependencies
from momotor.options.types import StepTasksType, StepTaskNumberType

TASK_OPERATORS: dict[str, collections.abc.Callable[[int, int], int]] = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.floordiv,
    '%': operator.mod,
}
TASK_OPER_RE_STR = "|".join(re.escape(oper) for oper in TASK_OPERATORS.keys())
TASK_OPER_RE = re.compile(rf'({TASK_OPER_RE_STR})')
TASK_REF_RE = re.compile(rf'(\\?\$(?:@|(?:\d+(?:(?<!\\)(?:{TASK_OPER_RE_STR})\$?\d+)*)))')

ID_RE_STR = rf'(?:[\w.$@]|{TASK_OPER_RE_STR})+'


def task_id_from_number(task_number: collections.abc.Iterable[int] | None) -> str:
    """ Convert a task number (tuple of ints) into a task id (dotted string)

    >>> task_id_from_number(None)
    ''

    >>> task_id_from_number((1,))
    '1'

    >>> task_id_from_number((1, 2,))
    '1.2'

    >>> task_id_from_number((1, 2, 3,))
    '1.2.3'

    """
    return '.'.join(str(t) for t in task_number) if task_number else ''


def task_number_from_id(task_id: str | None) -> StepTaskNumberType:
    """ Convert a task_id string into a task number

    >>> task_number_from_id('') is None
    True

    >>> task_number_from_id('1')
    (1,)

    >>> task_number_from_id('1.2')
    (1, 2)

    >>> task_number_from_id('1.2.3')
    (1, 2, 3)
    """
    return tuple(int(p) for p in task_id.split('.')) if task_id else None


@dataclass(frozen=True)
class StepTaskId:
    """ A step-id and task-number pair
    """
    step_id: str
    task_number: StepTaskNumberType

    def __str__(self):
        if self.task_number:
            return self.step_id + '.' + task_id_from_number(self.task_number)
        else:
            return self.step_id


def iter_task_numbers(sub_tasks: StepTasksType | None) -> collections.abc.Generator[StepTaskNumberType, None, None]:
    """ Generate all the task-numbers for the subtasks.
    
    >>> list(iter_task_numbers(None))
    [None]

    >>> list(iter_task_numbers(tuple()))
    [None]

    >>> list(iter_task_numbers((1,)))
    [(0,)]

    >>> list(iter_task_numbers((3,)))
    [(0,), (1,), (2,)]

    >>> list(iter_task_numbers((2, 2)))
    [(0, 0), (0, 1), (1, 0), (1, 1)]

    >>> list(iter_task_numbers((2, 3)))
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]

    :param sub_tasks: sequence of integers with the number of sub-tasks for each level
    :return: the task numbers
    """
    if sub_tasks:
        yield from itertools.product(*(range(st) for st in sub_tasks))
    else:
        yield None


def iter_task_ids(step_id: str, sub_tasks: StepTasksType | None) -> collections.abc.Generator[StepTaskId, None, None]:
    """ Generate all the task-ids for the subtasks.

    >>> list(str(t) for t in iter_task_ids('step', None))
    ['step']

    >>> list(str(t) for t in iter_task_ids('step', tuple()))
    ['step']

    >>> list(str(t) for t in iter_task_ids('step', (2,)))
    ['step.0', 'step.1']

    >>> list(str(t) for t in iter_task_ids('step', (2, 2)))
    ['step.0.0', 'step.0.1', 'step.1.0', 'step.1.1']

    :param step_id: the id of the step
    :param sub_tasks: sequence of integers with the number of sub-tasks for each level
    :return: the task numbers
    """
    if sub_tasks is None:
        yield StepTaskId(step_id, None)
    else:
        for task_number in iter_task_numbers(sub_tasks):
            yield StepTaskId(step_id, task_number)


def get_task_id_lookup(task_ids: collections.abc.Iterable[StepTaskId]) -> dict[str, StepTaskId]:
    """ Convert an iterable of :py:const:`StepTaskId` objects into a lookup table to convert a string representation of
    a task-id to the :py:const:`StepTaskId`

    >>> get_task_id_lookup({StepTaskId('step', (0, 0))})
    {'step.0.0': StepTaskId(step_id='step', task_number=(0, 0))}

    :param task_ids: the task ids to convert
    :return: the lookup table
    """
    return {
        str(task_id): task_id
        for task_id in task_ids
    }


def apply_task_number(depend_id: str, task_id: StepTaskId) -> str:
    """ Replace ``$`` references in dependency strings with their value from the `task_id` parameter,
    e.g. ``$0`` in `depend_id` will be replaced with ``task_id.task_number[0]``

    :param depend_id: the dependency string
    :param task_id: the task id to use for the replacement
    :return: the dependency string with the references replaced

    Simple arithmetic on the values can be done, available operators are ``+``, ``-``, ``*``, ``/`` and ``%``, for
    the usual operations `add`, `subtract`, `multiply`, `integer division` and `modulo`.
    Arithmetic operations are evaluated from left to right, there is no operator precedence.

    When subtraction results in a negative value or division in infinity, this will not directly throw an exception,
    but instead will generate an invalid task-id containing ``#NEG`` or ``#INF``.

    Special value ``$@`` will be replaced with the full task number.
    To include a literal ``$`` use ``\\$``. To prevent a character between two ``$`` placeholders
    from being interpreted as an arithmetic operation, use a backslash before the character.
    See the examples below.

    Raises :py:exc:`~momotor.options.exception.InvalidDependencies` if `depend_id` contains invalid
    references or is syntactically incorrect.

    Examples:

    >>> tid = StepTaskId('step', (4, 5, 6))
    >>> apply_task_number('test', tid)
    'test'

    Basic usage

    >>> apply_task_number('test.$0', tid)
    'test.4'

    >>> apply_task_number('test-$0.$1', tid)
    'test-4.5'

    >>> apply_task_number('test$1_$2', tid)
    'test5_6'

    Arithmetic

    >>> apply_task_number('test.$0-5.$1-5.$2-5', tid)
    'test.#NEG.0.1'

    >>> apply_task_number('test.$0+1.$1+1.$2+1', tid)
    'test.5.6.7'

    >>> apply_task_number('test.$0*2.$1*2.$2*2', tid)
    'test.8.10.12'

    >>> apply_task_number('test.$0/2.$1/2.$2/2', tid)
    'test.2.2.3'

    >>> apply_task_number('test.$0%2.$1%2.$2%2', tid)
    'test.0.1.0'

    >>> apply_task_number('test.$0*2+1.$1*2+1.$2*2+1', tid)
    'test.9.11.13'

    >>> apply_task_number('test.$0+1*2.$1+1*2.$2+1*2', tid)
    'test.10.12.14'

    >>> apply_task_number('test.$0+$1+$2', tid)
    'test.15'

    >>> apply_task_number('test.$1/0', tid)
    'test.#INF'

    The $@ placeholder

    >>> apply_task_number('test.$@', tid)
    'test.4.5.6'

    >>> apply_task_number('test-$@tail', tid)
    'test-4.5.6tail'

    >>> apply_task_number('test-$@-tail', tid)
    'test-4.5.6-tail'

    >>> apply_task_number('test-$@.tail', tid)
    'test-4.5.6.tail'

    >>> apply_task_number('test-$@999', tid)
    'test-4.5.6999'

    Escaping $ and operators

    >>> apply_task_number('test-\\\\$0', tid)
    'test-$0'

    >>> apply_task_number('test.$0\\\\-$1', tid)
    'test.4-5'

    Invalid references

    >>> apply_task_number('test.$9', tid)
    Traceback (most recent call last):
    ...
    momotor.options.exception.InvalidDependencies: Task 'step.4.5.6' has invalid dependency 'test.$9'

    Other special cases

    >>> apply_task_number('test-$X', tid)
    'test-$X'

    >>> apply_task_number('test.$1$2', tid)
    'test.56'

    >>> apply_task_number('test.$1^4', tid)
    'test.5^4'

    >>> apply_task_number('test.$0text.$1', tid)
    'test.4text.5'

    >>> apply_task_number('test.$0.text.$1', tid)
    'test.4.text.5'

    >>> apply_task_number('test.$0.999.$1', tid)
    'test.4.999.5'

    """
    if '$' in depend_id:
        task_number = task_id.task_number
        if task_number:
            task_lookup = {
                f'${idx}': value
                for idx, value in enumerate(task_number)
            }
        else:
            task_lookup = {}

        def _replace(section):
            if section.startswith('\\') and len(section) > 1:
                if section[1] in ['$', *TASK_OPERATORS.keys()]:
                    return section[1:]
                return section
            elif not section.startswith('$'):
                return section
            elif section == '$@':
                # expand `$@` into the full task number string
                return task_id_from_number(task_number)

            parts = deque(TASK_OPER_RE.split(section))

            result, oper = None, None
            try:
                while parts:
                    value = parts.popleft()
                    try:
                        value = task_lookup[value]
                    except KeyError:
                        value = int(value)
                        
                    if oper:
                        assert result is not None
                        result = TASK_OPERATORS[oper](result, value)
                    else:
                        result = value

                    if parts:
                        oper = parts.popleft()

            except ZeroDivisionError:
                return '#INF'

            if result is None:
                raise ValueError

            elif result < 0:
                return '#NEG'

            return f'{result}'

        try:
            parts = TASK_REF_RE.split(depend_id)
            return ''.join(_replace(part) for part in parts)
        except (ValueError, IndexError, TypeError):
            raise InvalidDependencies(
                f"Task '{task_id!s}' has invalid dependency '{depend_id!s}'"
            ) from None

    return depend_id
