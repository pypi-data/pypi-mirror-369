from __future__ import annotations

import collections.abc


def parse_key_value_list(s: str) \
        -> collections.abc.Generator[tuple[str, str | int | float | bool | None], None, None]:
    """
    Parse a string of key=value pairs into a sequence of (key, value) pairs.

    Value can be a string, integer, float or boolean. If value needs to contain spaces, it must be quoted.

    If the value is empty, but the `=` is present, the value will be `None`.
    A single key (without `=`) will result in a value of `True`
    Constants 'true', 'false', 'null' and 'none' are converted to boolean or `None` values.
    Any other unquoted string is considered a string.

    Examples:

    >>> list(parse_key_value_list(""))
    []

    >>> list(parse_key_value_list("key"))
    [('key', True)]

    >>> list(parse_key_value_list("key=value"))
    [('key', 'value')]

    >>> list(parse_key_value_list("key='value with space'"))
    [('key', 'value with space')]

    >>> list(parse_key_value_list('key="value with space"'))
    [('key', 'value with space')]

    >>> list(parse_key_value_list('key=0'))
    [('key', 0)]

    >>> list(parse_key_value_list('key=1.5'))
    [('key', 1.5)]

    >>> list(parse_key_value_list('key=true'))
    [('key', True)]

    >>> list(parse_key_value_list('key=false'))
    [('key', False)]

    >>> list(parse_key_value_list('key=null'))
    [('key', None)]

    >>> list(parse_key_value_list('key=none'))
    [('key', None)]

    >>> list(parse_key_value_list('key="true"'))
    [('key', 'true')]

    >>> list(parse_key_value_list('key1=value1 key2=value2 key3= key4'))
    [('key1', 'value1'), ('key2', 'value2'), ('key3', None), ('key4', True)]

    >>> list(parse_key_value_list('key1 key2 key3 key4'))
    [('key1', True), ('key2', True), ('key3', True), ('key4', True)]

    >>> type(next(parse_key_value_list('key=1'))[1])
    <class 'int'>

    >>> type(next(parse_key_value_list('key=1.0'))[1])
    <class 'float'>

    >>> type(next(parse_key_value_list('key=x'))[1])
    <class 'str'>

    >>> type(next(parse_key_value_list('key=true'))[1])
    <class 'bool'>

    >>> type(next(parse_key_value_list('key=null'))[1])
    <class 'NoneType'>

    """
    s = s.lstrip()
    while s:
        key, sep, rest = s.partition('=')
        while ' ' in key:
            lone_key, key = key.split(None, 1)
            yield lone_key, True

        key = key.strip()

        if rest and not rest.startswith(' '):
            if rest.startswith('"'):
                value, s = rest[1:].split('"', 1)
            elif rest.startswith("'"):
                value, s = rest[1:].split("'", 1)
            else:
                try:
                    value, s = rest.split(None, 1)
                except ValueError:
                    value, s = rest, ''

                value = value.strip()
                if value:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            if value.lower() == 'true':
                                value = True
                            elif value.lower() == 'false':
                                value = False
                            elif value.lower() in ['null', 'none']:
                                value = None
                else:
                    value = None
        else:
            value = None if sep else True
            s = rest.lstrip()

        yield key.strip(), value
