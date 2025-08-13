"""Import everything from itertools, more_itertools and some custom functions """
from __future__ import annotations

import warnings
from collections.abc import Iterable, Iterator, Sequence
from itertools import *
from math import inf
from typing import TYPE_CHECKING, Any, Callable, List, Protocol, Tuple, Type, TypeVar

from more_itertools import *

try:
    from typing import ParamSpec, SupportsAbs
except ImportError:
    from typing_extensions import ParamSpec, SupportsAbs

from . import functools as _functools

_T = TypeVar('_T')
_P = ParamSpec('_P')

if TYPE_CHECKING:
    from _typeshed import SupportsAdd, SupportsAllComparisons, SupportsSub

    class SupportsAddSub(SupportsAdd[Any], SupportsSub[Any], Protocol):
        ...

    class SupportsAddSubComparison(SupportsAddSub[Any], SupportsAllComparisons[Any], Protocol):
        ...

    SupportsAddSubT = TypeVar('SupportsAddSubT', bound=SupportsAddSub)
    SupportsAddSubComparisonT = TypeVar('SupportsAddSubComparisonT',
                                        bound=SupportsAddSubComparison)


def _round(x: float, decimals: int | None = None) -> float | int:
    """Overrides builtin round behavior so that decimals==None does not
    round at all."""
    if decimals is None:
        return x
    return round(x, decimals)


def separate_iterator(it: Iterable, sep: Any) -> Iterator:
    """separate_iterator('abcde', ',') --> a , b , c , d , e

    The same as :func:`~more_itertools.intersperse(sep, it, n=1)`. Only here for backwards compability.
    """
    warnings.warn(f"{__name__}.separate_iterator is just a wrapper around intersperse.",
                  DeprecationWarning,
                  stacklevel=2)
    return intersperse(sep, it, n=1)


def flatten_nested(it: Iterable, dtypes: tuple[type[Iterable], ...] = (list,)) -> Iterator:
    """Flattens the given arbitrarily nested iterable. By default, only lists are flattened. Use the optional `dtypes`
    argument to flatten other iterables as well.

    Similar to :func:`~more_itertools.collapse` which works with a blacklist instead of a whitelist.

    Parameters
    ----------
    it: :class:`~typing.Iterable` to flatten
    dtypes: Types that get flattened.

    Returns
    -------
    Objects that are not of a type in `dtypes`
    """
    if isinstance(it, dtypes):
        for x in it:
            yield from flatten_nested(x, dtypes)
    else:
        yield it


def argmin(it: Iterable) -> int:
    """Return index of smallest element by iteration order.

    >>> argmin([1, 3, 2, 4, 0])
    4

    Raises
    --------
    :class:`~ValueError` if the iterable is empty.

    Parameters
    ----------
    it: :class:`~typing.Iterable` to search for minimum

    Returns
    -------
    Index of the smallest element if it by iteration order
    """
    it = enumerate(it)
    try:
        min_idx, current = next(it)
    except StopIteration:
        raise ValueError('Argument was empty')
    for idx, elem in it:
        if elem < current:
            current = elem
            min_idx = idx
    return min_idx


def argmax(it: Iterable) -> int:
    """Return index of largest element by iteration order.

    >>> argmax([1, 3, 2, 4, 0])
    3

    Raises
    --------
    :class:`~ValueError` if the iterable is empty.

    Parameters
    ----------
    it: :class:`~typing.Iterable` to search for maximum

    Returns
    -------
    Index of the largest element if it by iteration order
    """
    it = enumerate(it)
    try:
        max_idx, current = next(it)
    except StopIteration:
        raise ValueError('Argument was empty')
    for idx, elem in it:
        if elem > current:
            current = elem
            max_idx = idx
    return max_idx


def next_largest(it: Iterable[SupportsAddSubComparisonT],
                 value: SupportsAddSubT,
                 precision: int | None = None) -> SupportsAddSubT:
    """Return the next-largest element to value from it.

    Parameters
    ----------
    it: Iterable
        The iterable to search.
    value: number-like
        The number to find the next-largest element to.
    precision: int, optional
        The number of decimal places up to which elements are compared.

    Returns
    -------
    The next-largest element to value in it, or the value itself if it
    is empty.

    Examples
    --------
    >>> next_largest([3, 4, 1, -5.0], 2.7)
    3
    >>> next_largest([3, 4, 1, -5.0], 1.01)
    3
    >>> next_largest([3, 4, 1, -5.0], -10)
    -5.0
    >>> next_largest([3, 4, 1, -5.0], 7.123)
    4
    >>> next_largest([1, 2, 10321], inf)
    10321
    >>> next_largest([], 42)
    42
    >>> next_largest([10, 11.0], 10 + 1e-14)
    11.0
    >>> next_largest([10, 11.0], 10 + 1e-14, precision=13)
    10

    """
    empty_sentinel = object()
    pred_false, pred_true = partition(lambda x: _round(x - value, precision) >= 0, it)
    result = min(pred_true, default=empty_sentinel)
    if result is empty_sentinel:
        return max(pred_false, default=value)
    return result


def next_smallest(it: Iterable[SupportsAddSubComparisonT],
                  value: SupportsAddSubT,
                  precision: int | None = None) -> SupportsAddSubT:
    """Return the next-smallest element to value from it.

    Parameters
    ----------
    it: Iterable
        The iterable to search.
    value: number-like
        The number to find the next-largest element to.
    precision: int, optional
        The number of decimal places up to which elements are compared.

    Returns
    -------
    The next-largest element to value in it, or the value itself if it
    is empty.

    Examples
    --------
    >>> next_smallest([3, 4, 1, -5.0], 2.7)
    1
    >>> next_smallest([3, 4, 1, -5.0], 1.01)
    1
    >>> next_smallest([3, 4, 1, -5.0], -10)
    -5.0
    >>> next_smallest([3, 4, 1, -5.0], 7.123)
    4
    >>> next_smallest([1, 2, 10321], inf)
    10321
    >>> next_smallest([], 42)
    42
    >>> next_smallest([10, 11.0], 11 - 1e-14)
    10
    >>> next_smallest([10, 11.0], 11 - 1e-14, precision=13)
    11.0

    """
    empty_sentinel = object()
    pred_false, pred_true = partition(lambda x: _round(x - value, precision) <= 0, it)
    result = max(pred_true, default=empty_sentinel)
    if result is empty_sentinel:
        return min(pred_false, default=value)
    return result


def next_closest(it: Iterable[SupportsAddSubComparisonT],
                 value: SupportsAddSubT,
                 precision: int | None = None) -> SupportsAddSubT:
    """Return the next-closest element to value from it.

    Parameters
    ----------
    it: Iterable
        The iterable to search.
    value: number-like
        The number to find the next-largest element to.
    precision: int, optional
        The number of decimal places up to which elements are compared.

    Returns
    -------
    The next-closest element to value in it, or the value itself if it
    is empty.

    Examples
    --------
    >>> next_closest([3, 4, 1, -5.0], 2.7)
    3
    >>> next_closest([3, 4, 1, -5.0], 1.01)
    1
    >>> next_closest([3, 4, 1, -5.0], -10)
    -5.0
    >>> next_closest([3, 4, 1, -5.0], 7.123)
    4
    >>> next_closest([1, 2, 10321], inf)
    10321
    >>> next_closest([], 42)
    42
    >>> next_closest([10, 11], 10.5 + 1e-14)
    11
    >>> next_closest([10, 11], 10.5 + 1e-14, precision=13)
    10

    """
    if value == -inf:
        return min(it, default=value)
    elif value == inf:
        return max(it, default=value)
    return min(it, key=lambda x: _round(abs(x - value), precision), default=value)


def replace_except(it: Iterable, exceptions: Any, replacement: Any = None) -> Iterator:
    """Replace all items that cause the specified exceptions during
    iteration with replacement.

    >>> list(replace_except(map(lambda d: 5 / d, [2, 1, 0, 5]), ZeroDivisionError, inf))
    [2.5, 5.0, inf, 1.0]

    Use a unique object to be able to identify items that errored:

    >>> sentinel = object()
    >>> filtered = list(replace_except(map(lambda d: 5 / d, [2, 1, 0, 5]), ZeroDivisionError,
    ...                                    sentinel))
    >>> filtered.index(sentinel)
    2

    Be aware that some iterators do not allow further iteration if they threw an exception.

    >>> list(ignore_exceptions((5 / d for d in [2, 1, 0, 5]), ZeroDivisionError))
    [2.5, 5.0]

    Parameters
    ----------
    it : :class:`~typing.Iterable` to iterate over.
    exceptions : Valid argument to an ``except`` clause
    replacement : Any object that is yielded whenever a specified exception
                  occurs.

    See Also
    --------
    :func:`ignore_exceptions` : Ignore instead of replace items that errored.

    """
    it = iter(it)
    while True:
        try:
            yield from it
        except exceptions:
            yield replacement
        else:
            return


def ignore_exceptions(it: Iterable, exceptions: Any) -> Iterator:
    """Ignore all specified exceptions during iteration.

    >>> list(ignore_exceptions(map(lambda d: 5 / d, [2, 1, 0, 5]), ZeroDivisionError))
    [2.5, 5.0, 1.0]

    Be aware that some iterators do not allow further iteration if they threw an exception.

    >>> list(ignore_exceptions((5 / d for d in [2, 1, 0, 5]), ZeroDivisionError))
    [2.5, 5.0]

    Parameters
    ----------
    it: :class:`~typing.Iterable` to iterate over.
    exceptions: Valid argument to an ``except`` clause
    """
    it = iter(it)
    while True:
        try:
            yield from it
        except exceptions:
            continue
        else:
            return


def batched_variable(iterable: Iterable[_T], ns: Sequence[int],
                     strict: bool = False) -> Iterator[tuple[_T, ...]]:
    """Break *iterable* into consecutive tuples of *n* items for each
    *n* in *ns*.

    Note that *ns* is repeated to match the length of *iterable*.

    If ``strict=True``, an exception is raised if
    ``len(iterable) != sum(ns)``.

    Examples
    --------
    >>> list(batched_variable(range(12), [2, 3, 1]))
    [(0, 1), (2, 3, 4), (5,), (6, 7), (8, 9, 10), (11,)]
    >>> list(map_if(batched_variable([6, 3, -2, 8, 1, 0], [1, 2]),
    ...             lambda x: len(x) == 2, sum, min))
    [6, 1, 8, 1]
    """
    it = iter(iterable)
    return interleave(*(batched(it, n, strict=strict) for n in ns))


def take_and_consume(n: int, consume_before: int, consume_after: int,
                     iterable: Iterable[_T]) -> list[_T]:
    """Take *n* items from *iterable*, consuming *consume_before* and
    *consume_after* taking.

    Examples
    --------
    >>> it = iter(range(7))
    >>> take_and_consume(2, 1, 3, it)
    [1, 2]
    >>> list(it)
    [6]
    """
    consume(iterable, consume_before)
    vals = take(n, iterable)
    consume(iterable, consume_after)
    return vals


def distribute_variable_batches(iterable: Iterable[_T],
                                ns: Sequence[int]) -> list[Iterator[list[_T]]]:
    """Returns an iterator for each *n* in *ns* that yields lists of
    *n* items from *iterable*.

    That is, the iterable is distributed on weighted by *n*.

    Uses :py:func:`~itertools.tee`, so might consume a lot of memory.

    Examples
    --------
    >>> list(map(list, distribute_variable_batches(range(6), [1, 2])))
    [[[0], [3]], [[1, 2], [4, 5]]]
    >>> list(map(list, map(collapse, distribute_variable_batches(range(10), [3, 2]))))
    [[0, 1, 2, 5, 6, 7], [3, 4, 8, 9]]
    """
    return [iter(_functools.partial(take_and_consume, ns[i], sum(ns[:i]), sum(ns[i+1:]), it), [])
            for i, it in zip(range(len(ns)), tee(iter(iterable), len(ns)))]


def zipstarmap(funcs: Sequence[Callable[_P, _T]], iterable: Iterable[_P]) -> list[Iterator[_T]]:
    """Apply *funcs* alternatingly on *args from *iterable*.

    Uses :py:func:`~itertools.tee`, so might consume a lot of memory.

    Examples
    --------
    >>> from operator import add
    >>> # [[-3 + -2, 0 + 1], [abs(-1), abs(2)]]
    >>> list(map(list, zipstarmap([add, abs], batched_variable(range(-3, 3), [2, 1]))))
    [[-5, 1], [1, 2]]
    """
    n = len(funcs)
    return [starmap(func, it) for func, it in zip(funcs, distribute(n, iterable))]


def zipmap(funcs: Sequence[Callable[_P, _T]], iterable: Iterable[_P]) -> list[Iterator[_T]]:
    """Apply *funcs* alternatingly on args from *iterable*.

    Uses :py:func:`~itertools.tee`, so might consume a lot of memory.

    Examples
    --------
    >>> # [[-3 + -2, 2 + 3], [min([-1, 0, 1]), min([4, 5, 6])]]
    >>> list(map(list, zipmap([sum, min], batched_variable(range(-3, 7), [2, 3]))))
    [[-5, 5], [-1, 4]]
    """
    n = len(funcs)
    sliced_its = (islice(it, start, None, n) for it, start in zip(tee(iterable, n), range(n)))
    return [map(func, it) for func, it in zip(funcs, sliced_its)]


def absmin(iterable_or_value: SupportsAbs[_T] | Iterable[SupportsAbs[_T]],
           *others: SupportsAbs[_T], default: _T = object(), key=None) -> _T:
    """The absolute-value-wise minimum. See :func:`minmax` for usage.

    This function's NumPy equivalent is::

        np.abs(iterable).min()

    Examples
    --------
    >>> absmin([-7, 3, 1, -1])
    1
    >>> absmin(-7, 3, 1, -1)
    1
    >>> import numpy as np
    >>> x = np.random.default_rng().normal(20)
    >>> print(absmin(x) == np.abs(x).min())
    True
    """
    iterable_or_value = (iterable_or_value, *others) if others else iterable_or_value
    try:
        return min((abs(x) for x in iterable_or_value), default=default, key=key)
    except TypeError:
        return abs(iterable_or_value)


def absmax(iterable_or_value: SupportsAbs[_T] | Iterable[SupportsAbs[_T]],
           *others: SupportsAbs[_T], default: _T = object(), key=None) -> _T:
    """The absolute-value-wise maximum. See :func:`minmax` for usage.

    This function's NumPy equivalent is::

        np.abs(iterable).max()

    Examples
    --------
    >>> absmax([-7, 3, 1, -1])
    7
    >>> absmax(-7, 3, 1, -1)
    7
    >>> import numpy as np
    >>> x = np.random.default_rng().normal(20)
    >>> print(absmax(x) == np.abs(x).max())
    True
    """
    iterable_or_value = (iterable_or_value, *others) if others else iterable_or_value
    try:
        return max((abs(x) for x in iterable_or_value), default=default, key=key)
    except TypeError:
        return abs(iterable_or_value)


del (Iterable, Any, Iterator, Protocol, TypeVar, TYPE_CHECKING, Sequence, Callable, ParamSpec,
     SupportsAbs)
del warnings, annotations
