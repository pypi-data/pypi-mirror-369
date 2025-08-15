import collections.abc
import re


def multi_split(s: str, extra_sep: collections.abc.Iterable = None, maxsplit: int = 0) -> collections.abc.Iterable[str]:
    """ Split a string on multiple separators.

    Only splits on whitespace by default, but `extra_sep` can provide other separators to split the string on.
    If `maxsplit` is nonzero, at most maxsplit splits occur, and the remainder of the string is returned as the
    final element.

    :param s: string to process
    :param extra_sep: extra separators to split the string on
    :param maxsplit: maximum number of splits
    :return:


    >>> list(multi_split('testing'))
    ['testing']

    >>> list(multi_split('testing one two three'))
    ['testing', 'one', 'two', 'three']

    >>> list(multi_split('testing,one two three'))
    ['testing,one', 'two', 'three']

    >>> list(multi_split('testing,one two three', ','))
    ['testing', 'one', 'two', 'three']

    >>> list(multi_split('testing,one two three', ',', 1))
    ['testing', 'one two three']

    >>> list(multi_split('testing,, one   two ,, three', ','))
    ['testing', 'one', 'two', 'three']

    >>> list(multi_split('   testing,, one   two ,, three   ', ','))
    ['testing', 'one', 'two', 'three']

    """
    separators = [r'\s']
    if extra_sep is not None:
        separators.extend([re.escape(c) for c in extra_sep])

    pattern = '(?:' + '|'.join(separators) + ')+'

    return re.split(pattern, s.strip(), maxsplit)
