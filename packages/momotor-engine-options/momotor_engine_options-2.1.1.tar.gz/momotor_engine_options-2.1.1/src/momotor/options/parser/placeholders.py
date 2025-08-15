from __future__ import annotations

import collections.abc
import typing

from momotor.options.providers import Providers
from momotor.options.parser.reference import resolve_reference_value


VT = typing.TypeVar('VT')


def replace_placeholders(
    value: VT, bundles: Providers, *,
    value_processor: collections.abc.Callable[[str | None], str] = None,
    mod: str = 'join'
) -> VT:
    """ Replace all :ref:`placeholders <placeholder>` in `value` with their resolved values.
    Placeholders are resolved recursively, i.e. if a resolved value contains more placeholders,
    these will be resolved as well.

    :param value: the string containing placeholders to resolve. If :py:attr:`value` is not a string,
                  no processing is done and :py:attr:`value` is returned unmodified.
    :param bundles: the bundles to resolve the references to
    :param value_processor: a callable that is called with every resolved value, can be used to modify placeholders.
                            If not supplied, uses :py:obj:`str` to cast the returned value to a string.
    :param mod: the modifier to apply to the resolved values. Defaults to ``'join'``.
    :return: the `value` with all placeholders resolved
    """
    if not isinstance(value, str):
        return value

    if value_processor is None:
        value_processor = str

    remaining = value
    result = ''

    while '${' in remaining:
        prefix, remaining = remaining.split('${', 1)
        result += prefix

        if prefix.endswith('$'):
            result += '{'
            continue

        value, remaining = resolve_reference_value(remaining, bundles, default_mod=mod)

        if value is None:
            result += '${'
            continue

        if '}' not in remaining:
            raise ValueError

        garbage, remaining = remaining.split('}', 1)
        if garbage.strip():
            raise ValueError

        result += replace_placeholders(
            value_processor(value), bundles,
            value_processor=value_processor
        )

    result += remaining

    return result
