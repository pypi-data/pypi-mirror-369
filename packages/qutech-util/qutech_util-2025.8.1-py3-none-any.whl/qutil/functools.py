"""Import everything from functools and some custom functions."""
import inspect
import numbers
from collections.abc import Iterator
from functools import *
from typing import Any, Callable, Generic, Tuple, TypeVar, Union

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec

_C = TypeVar('_C', bound=Callable)
_T = TypeVar('_T', bound=numbers.Complex)
_S = TypeVar('_S')
_P = ParamSpec('_P')


class FunctionChain(Generic[_C]):
    """Chain of multiple functions. The return value(s) of each previous
    function are the first ``n_args`` positional argument(s) of the next
    function call. This class is for convenient reuse of function chains
    and passing them around as callable objects.

    Similar to :func:`functools.reduce`, but instead of reducing a sequence using
    a single function, this reduces a list of functions by applying them
    iteratively to the output of the function before.

    Example:

    >>> from qutil.functools import chain
    >>> import numpy as np
    >>> x = np.array([1, 4, -6, 8], dtype=float)
    >>> f_chain = FunctionChain(np.abs, np.sqrt)
    >>> f_chain(x, out=x)  # Will write all intermediate results into the same array.
    array([1.        , 2.        , 2.44948974, 2.82842712])

    n_args argument:

    >>> def adder(x, axis):
    ...     return x.sum(axis), axis - 1
    >>> def multiplier(x, axis):
    ...     return x.prod(axis), axis - 1
    >>> x = np.arange(12).reshape(3, 4)
    >>> axis = 1
    >>> f_chain = FunctionChain(adder, multiplier, n_args=2)
    >>> result, axis = f_chain(x, axis)
    >>> print(result)
    5016
    """
    __array_interface__ = {
        'shape': (),
        'typestr': '|O',
        'version': 3
    }
    """Describes to NumPy how to convert this object into an array."""

    def __init__(self, *functions: _C, n_args: int = 1, inspect_kwargs: bool = False):
        self.functions = functions
        self.n_args = n_args
        self.inspect_kwargs = inspect_kwargs
        if self.n_args < 0:
            raise ValueError(f'n_args should be a non-negative integer, not {n_args}.')

    def __getitem__(self, item: Any):
        raise TypeError('The __getitem__ method has been removed. Index into '
                        'FunctionChain.functions instead')

    def __len__(self) -> int:
        return len(self.functions)

    def __iter__(self) -> Iterator[_C]:
        raise TypeError('The __iter__ method has been removed. Iterate over '
                        'FunctionChain.functions instead')

    def __repr__(self) -> str:
        return (
            super().__repr__()
            + ' with functions'
            + ('\n - {}'*len(self)).format(*self.functions)
        )

    def __call__(self, *args, **kwargs):
        """Iteratively apply functions to the return value of the
        previous one, starting with `x` as initial argument.

        Args:
            *args: Positional arguments that get passed to each function besides the previous function's return value.

            **kwargs: Keyword arguments that get passed to each function.

        Returns:
            Return value of the last function
        """
        args = list(args)
        for func in self.functions:
            if self.inspect_kwargs:
                tmp_kwargs, _ = filter_kwargs(func, kwargs)
            else:
                tmp_kwargs = kwargs
            if self.n_args == 0:
                func(*args, **tmp_kwargs)
            elif self.n_args == 1:
                args[0] = func(args[0], *args[1:], **tmp_kwargs)
            else:
                args[:self.n_args] = func(*args, **tmp_kwargs)

        if self.n_args == 0:
            return
        elif self.n_args == 1:
            return args[0]
        else:
            return tuple(args[:self.n_args])


def chain(*functions: _C, n_args: int = 1, inspect_kwargs: bool = False) -> FunctionChain[_C]:
    """Chain multiple functions.

    The return value of each previous function is the first argument of
    the next function call.

    Example:
        >>> from qutil.functools import chain
        >>> import numpy as np
        >>> f_chain = chain(np.diff, np.sum, print)
        >>> f_chain([1, 3, 6])
        5

    Args:
        *functions : callable
            Functions to be chained.

        n_args : int
            Number of arguments accepted and returned by functions.

        inspect_kwargs : bool
            If true, only pass kwargs actually accepted by the functions.
            Inspects the signature and therefore has some overhead.

    Returns:
        Callable object that chains arguments.
    """
    return FunctionChain(*functions, n_args=n_args, inspect_kwargs=inspect_kwargs)


def scaled(scale: numbers.Number) -> Callable:
    """Scale by some factor.

    Can be either used as a decorator, in which case it applies the
    scale to the wrapped function's result, or as a function factory,
    in which case the resulting function simply multiplies its first
    argument by the scale.

    This lets this function be used as a `procfn` for the
    ``python_spectrometer`` package, for example.

    Examples
    --------
    >>> mega = scaled(1e6)
    >>> mega(2)
    2000000.0
    >>> @scaled(0.5)
    ... def mysum(a, b):
    ...     return a + b
    >>> mysum(2, 1.5j)
    (1+0.75j)
    """

    def wrapper(fun: Union[Callable[_P, _T], _T], **__) -> Union[Callable[_P, _T], _T]:
        if not callable(fun):
            return scale * fun

        @wraps(fun)
        def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            return scale * fun(*args, **kwargs)

        return wrapped

    return wrapper


def filter_kwargs(obj: Callable[_P, _T], kwargs: _P.kwargs) -> tuple[Any, Any]:
    r"""Inspect `obj`\s signature and filter the set of kwargs into ones
    that `obj` accepts and remaining.

    Examples
    --------
    >>> def foo(x):
    ...     return x*2
    >>> def bar(a, y=4):
    ...     return a + y/2
    >>> def baz(**kw):
    ...     foo_kw, bar_kw = filter_kwargs(foo, kw)
    ...     return bar(foo(**foo_kw), **bar_kw)
    >>> baz(x=2, y=4)
    6.0

    """
    sig = inspect.signature(obj)
    accepted = {}
    remaining = {}
    for key, val in kwargs.items():
        if (
                key in sig.parameters
                and (param := sig.parameters[key]).kind in (
                    param.KEYWORD_ONLY, param.POSITIONAL_OR_KEYWORD
                )
        ):
            accepted[key] = val
        else:
            remaining[key] = val

    return accepted, remaining


del Iterator, TypeVar, ParamSpec
del numbers
