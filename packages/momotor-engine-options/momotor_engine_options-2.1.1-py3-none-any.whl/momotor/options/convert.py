from __future__ import annotations

import collections
import logging
import typing
import warnings

logger = logging.getLogger(__name__)


def convert_duration(t: str | int | float | None) -> float | None:
    """ Convert a string containing a duration into a float. The duration is defined as "hh:mm:ss"
    (hours, minutes, seconds). The seconds can contain decimals.

    >>> convert_duration('1')
    1.0

    >>> convert_duration('1.5')
    1.5

    >>> convert_duration('10')
    10.0

    >>> convert_duration('100')
    100.0

    >>> convert_duration('1:00')
    60.0

    >>> convert_duration('10:00')
    600.0

    >>> convert_duration('100:00')
    6000.0

    >>> convert_duration('1:00:00')
    3600.0

    >>> convert_duration('1:00:00')
    3600.0

    >>> convert_duration('10:00:00')
    36000.0

    >>> convert_duration('100:00:00')
    360000.0

    >>> convert_duration('123:45:67.89')
    445567.89

    >>> convert_duration(1)
    1.0

    >>> convert_duration(1.0)
    1.0

    :param t:
    :return:
    """
    if t is None:
        return t

    try:
        return float(t)
    except ValueError:
        pass

    # noinspection PyBroadException
    try:
        parts = t.split(':')
        if len(parts) > 3:
            raise ValueError

        result = 0.0
        for part in parts:
            result = result * 60.0 + float(part)

    except:
        msg = f'{t!r} is not a valid duration'
        warnings.warn(msg)
        raise ValueError(msg)

    return result


SIZE_FACTOR: dict[str, int] = {
    'k': 1,
    'm': 2,
    'g': 3,
    't': 4,
    'p': 5,
    'e': 6,
    'z': 7,
    'y': 8,
}


def convert_size(t: str | int | None) -> int | None:
    """ Convert a size into an integer. If size ends with "i" or "ib", the value is a
    binary (IEC) value, otherwise it is a decimal (SI) value.
    (See https://en.wikipedia.org/wiki/Binary_prefix)

    Supported unit prefixes are:

    .. |zwsp| unicode:: U+200B
       :trim:

    +-----------------------------------+-----------------------------------+
    + Decimal                           | Binary                            |
    +-----------------------+-----------+-----------------------+-----------+
    + Value                 | SI        | Value                 | IEC       |
    +=======================+===========+=======================+===========+
    | 1                     | (none)    | 1                     | (none)    |
    +-----------------------+---+-------+-----------------------+----+------+
    | 1000                  | k | kilo  | 1024                  | Ki | kibi |
    +-----------------------+---+-------+-----------------------+----+------+
    | 1000 |zwsp| :sup:`2`  | M | mega  | 1024 |zwsp| :sup:`2`  | Mi | mebi |
    +-----------------------+---+-------+-----------------------+----+------+
    | 1000 |zwsp| :sup:`3`  | G | giga  | 1024 |zwsp| :sup:`3`  | Gi | gibi |
    +-----------------------+---+-------+-----------------------+----+------+
    | 1000 |zwsp| :sup:`4`  | T | tera  | 1024 |zwsp| :sup:`4`  | Ti | tebi |
    +-----------------------+---+-------+-----------------------+----+------+
    | 1000 |zwsp| :sup:`5`  | P | peta  | 1024 |zwsp| :sup:`5`  | Pi | pebi |
    +-----------------------+---+-------+-----------------------+----+------+
    | 1000 |zwsp| :sup:`6`  | E | exa   | 1024 |zwsp| :sup:`6`  | Ei | exbi |
    +-----------------------+---+-------+-----------------------+----+------+
    | 1000 |zwsp| :sup:`7`  | Z | zetta | 1024 |zwsp| :sup:`7`  | Zi | zebi |
    +-----------------------+---+-------+-----------------------+----+------+
    | 1000 |zwsp| :sup:`8`  | Y | yotta | 1024 |zwsp| :sup:`8`  | Yi | yobi |
    +-----------------------+---+-------+-----------------------+----+------+

    Case of unit is ignored, i.e. MiB == mib == MIB

    >>> convert_size('16')
    16

    >>> convert_size('16B')
    16

    >>> convert_size('16 B')
    16

    >>> convert_size('16k')
    16000

    >>> convert_size('16kb')
    16000

    >>> convert_size('16ki')
    16384

    >>> convert_size('16kib')
    16384

    >>> convert_size('16MiB')
    16777216

    >>> convert_size('16gib')
    17179869184

    >>> convert_size('16TIB')
    17592186044416

    :param t:
    :return: 
    """
    if t is None:
        return t

    base = 1000
    try:
        if isinstance(t, str):
            t = t.strip().lower()

            if t.endswith('b'):
                t = t[:-1]

            if t.endswith('i'):
                base = 1024
                t = t[:-1]

        try:
            return int(t)
        except ValueError:
            return int(t[:-1]) * (base ** SIZE_FACTOR[t[-1]])

    except:
        msg = f'{t!r} is not a valid size'
        warnings.warn(msg)
        raise ValueError(msg)


@typing.overload
def convert_intlist(il: str, empty_values: bool = False) -> tuple[int, ...]:
    ...


@typing.overload
def convert_intlist(il: str, empty_values: bool = True) -> tuple[int | None, ...]:
    ...


def convert_intlist(il: str, empty_values: bool = False) -> tuple[int | None, ...]:
    """ Convert a string containing a comma-separated sequence of integer values into a tuple of integers.
    Allows a range to be specified using ``..`` as separator, e.g. "100..109".
    If `empty_values` is ``True``, empty values in the list are allowed and returned as ``None``

    >>> convert_intlist("")
    ()

    >>> convert_intlist("", empty_values=True)
    (None,)

    >>> convert_intlist("0")
    (0,)

    >>> convert_intlist("0,1")
    (0, 1)

    >>> convert_intlist("0,,1")
    Traceback (most recent call last):
    ...
    ValueError: '0,,1' is not a valid list of integers: empty values not allowed

    >>> convert_intlist("0,,1", empty_values=True)
    (0, None, 1)

    >>> convert_intlist("0, ,1", empty_values=True)
    (0, None, 1)

    >>> convert_intlist("0,1,100..109")
    (0, 1, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109)

    >>> convert_intlist("0, 1, 100 .. 109")
    (0, 1, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109)

    >>> convert_intlist("0,", empty_values=True)
    (0, None)

    >>> convert_intlist("0,1,X")
    Traceback (most recent call last):
    ...
    ValueError: '0,1,X' is not a valid list of integers: invalid literal for int() with base 10: 'X'

    >>> convert_intlist("0..")
    Traceback (most recent call last):
    ...
    ValueError: '0..' is not a valid list of integers: incomplete range 0..

    >>> convert_intlist("0..", empty_values=True)
    Traceback (most recent call last):
    ...
    ValueError: '0..' is not a valid list of integers: incomplete range 0..

    :param il: string to convert
    :param empty_values: allow empty values in the list. These will be converted to ``None``
    :return: tuple of integers
    :raises ValueError: if any section of the list cannot be parsed as an integer
    """

    result = collections.deque()
    if il.strip():
        for part in il.split(','):
            try:
                first, sep, last = part.partition('..')
                if sep:
                    if not first.strip() or not last.strip():
                        raise ValueError(f"incomplete range {first.strip()}..{last.strip()}")
                    result.extend(range(int(first), int(last)+1))
                elif first.strip():
                    result.append(int(first))
                elif empty_values:
                    result.append(None)
                else:
                    raise ValueError("empty values not allowed")

            except ValueError as e:
                msg = f'{il!r} is not a valid list of integers: {e!s}'
                warnings.warn(msg)
                raise ValueError(msg) from None
    elif empty_values:
        result.append(None)

    return tuple(result)
