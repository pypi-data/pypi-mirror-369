from __future__ import annotations

import dataclasses
import logging
import sys
import time
import warnings
from collections.abc import Callable, Hashable, Iterator, Mapping, MutableMapping, Sequence
from contextlib import contextmanager
from importlib import import_module
from types import ModuleType
from typing import Any, Dict, Optional, Union
from unittest import mock

from .functools import wraps

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated


@contextmanager
def all_logging_disabled(highest_level=logging.CRITICAL):
    """
    A context manager that will prevent any logging messages
    triggered during the body from being processed.
    :param highest_level: the maximum logging level in use.
    This would only need to be changed if a custom level greater than CRITICAL
    is defined.

    https://gist.github.com/simon-weber/7853144
    """
    # two kind-of hacks here:
    #    * can't get the highest logging level in effect => delegate to the user
    #    * can't get the current module-level override => use an undocumented
    #       (but non-private!) interface

    previous_level = logging.root.manager.disable

    logging.disable(highest_level)

    try:
        yield
    finally:
        logging.disable(previous_level)


if sys.version_info >= (3, 11):
    _filter_warnings = warnings.catch_warnings
else:
    @contextmanager
    def _filter_warnings(action, category=Warning, lineno=0, append=False, *,
                         record=False, module=None):
        """A context manager that combines catching and filtering warnings."""
        with warnings.catch_warnings(record=record, module=module) as manager:
            warnings.simplefilter(action, category, lineno, append)
            yield manager


@wraps(_filter_warnings)
def filter_warnings(*args, **kwargs):
    if args:
        warnings.warn('Passing positional arguments to filter_warnings is deprecated',
                      DeprecationWarning, stacklevel=2)

        kwarg_names = ['action', 'category', 'lineno', 'append']
        for i, name in enumerate(kwarg_names[:len(args)]):
            if name not in kwargs:
                kwargs[name] = args[i]
            else:
                warnings.warn(f"Ignored arg at position {i} in favor of kwarg '{name}'",
                              UserWarning, stacklevel=2)

    return _filter_warnings(**kwargs)


@deprecated('Use unittest.mock.patch.dict instead')
def key_set_to(dct: MutableMapping, key: Hashable, val: Any):
    """Temporarily set `key` in `dct` to `val`.

    Examples
    --------
    >>> my_dict = {'a': 2, 3: 'b'}
    >>> my_dict['a']
    2
    >>> with key_set_to(my_dict, 'a', 3):
    ...     print(my_dict['a'])
    3
    >>> my_dict['a']
    2

    Also works with previously nonexisting keys:

    >>> with key_set_to(my_dict, 1, 2):
    ...     print(my_dict[1])
    2
    >>> 1 in my_dict
    False

    """
    return mock.patch.dict(dct, {key: val})


@deprecated('Use unittest.mock.patch.object instead')
def attr_set_to(obj: Any, attr: str, val: Any, allow_missing: bool = False):
    """Temporarily set `attr` in `obj` to `val`.

    If `allow_missing` is `True`, `attr` will also be set if it did not
    exist before.

    Examples
    --------
    >>> class Foo:
    ...     a = 3
    >>> foo = Foo()
    >>> foo.a
    3
    >>> with attr_set_to(foo, 'a', 4):
    ...     print(foo.a)
    4
    >>> foo.a
    3
    >>> with attr_set_to(foo, 'b', 1, allow_missing=True):
    ...     print(foo.b)
    1
    >>> hasattr(foo, 'b')
    False

    """
    return mock.patch.object(obj, attr, val, create=allow_missing)


def import_or_mock(
        name: str, package: str | None = None, local_name: str | None = None
) -> dict[str, ModuleType | mock.MagicMock]:
    """Imports a module or, if it cannot be imported, mocks it.

    If it is importable, equivalent to::

        from name import package as local_name

    Parameters
    ----------
    name : str
        See :func:`importlib.import_module`.
    package : str | None
        See :func:`importlib.import_module`.
    local_name : str
        Either the name assigned to the module or the object to be
        imported from the module.

    Returns
    -------
    dict[str, ModuleType | mock.MagicMock]
        A dictionary with the single entry {local_name: module}.

    Examples
    --------
    >>> locals().update(import_or_mock('numpy', None, 'pi'))
    >>> pi
    3.141592653589793
    >>> locals().update(import_or_mock('owiejlkjlqz'))
    >>> owiejlkjlqz
    <MagicMock name='mock.owiejlkjlqz' id='...'>

    """
    local_name = local_name or name
    try:
        module = import_module(name, package)
    except ImportError:
        module = mock.MagicMock(__name__=name)
    return {local_name: getattr(module, local_name, module)}


@dataclasses.dataclass
class TimeoutExceeded:
    """Measures if the given timeout has exceeded since instantiation."""
    timeout: float
    start_time: float = dataclasses.field(default_factory=time.perf_counter)
    stop_time: float = dataclasses.field(init=False)
    frozen: bool = dataclasses.field(default=False, init=False)

    def __bool__(self) -> bool:
        """Has the timeout been exceeded?"""
        return self.elapsed > self.timeout

    @property
    def elapsed(self) -> float:
        """Time elapsed since instantiation."""
        if not self.frozen:
            return time.perf_counter() - self.start_time
        else:
            return self.stop_time - self.start_time

    def freeze(self):
        """Stop the clock."""
        self.stop_time = time.perf_counter()
        self.frozen = True


@contextmanager
def timeout(value: float, on_exceeded: Callable[[float], None] | None = None,
            raise_exc: bool | str = False) -> Iterator[TimeoutExceeded]:
    """A simple timer that can be used in loops to poll if a timeout has
     elapsed.

     Parameters
     ----------
     value :
        The value of the timeout.
     on_exceeded :
        A callback that is executed in case the timeout has elapsed.
        Gets the elapsed time as a sole argument.
     raise_exc :
        Raise a :class:`TimeoutError` if the timeout was exceeded. The
        exception is raised after *on_exceeded* is run. If a string,
        interpreted as the message for the exception and gets the
        elapsed time as its sole formatting argument.

    Yields
    ------
    exceeded :
        The :class:`.TimeoutExceeded` instance tracking the elapsed
        time.

    Raises
    ------
    TimeoutError :
        If *raise_exc* is true and the timeout was exceeded.

    Examples
    --------
    >>> with timeout(2) as exceeded:
    ...     while not exceeded:
    ...         print('loop body')
    ...         time.sleep(0.5)
    loop body
    loop body
    loop body
    loop body

    Execute code on an exceeded callback:

    >>> def on_exceeded(elapsed):
    ...     print(f'Timeout exceeded after {elapsed:2g} s.')
    >>> with timeout(1, on_exceeded) as exceeded:
    ...     while not exceeded:
    ...         print('Executing')
    ...         time.sleep(1.5)
    Executing
    Timeout exceeded after ... s.

    The time elapsed inside the context can be polled:

    >>> from math import inf
    >>> with timeout(inf) as exceeded:
    ...     while not exceeded:
    ...         if exceeded.elapsed > 1:  # pointless
    ...             break
    >>> print(f'Started at', exceeded.start_time)
    Started at ...
    >>> print(f'Stopped at', exceeded.start_time)
    Stopped at ...
    >>> exceeded.elapsed == exceeded.stop_time - exceeded.start_time
    True

    Raise if exceeded:

    >>> with timeout(0, raise_exc=True) as exceeded:
    ...     while not exceeded:
    ...         pass
    Traceback (most recent call last):
       ...
    TimeoutError: Timeout exceeded after ... seconds.

    >>> with timeout(0, raise_exc='My error message. Elapsed: {}') as exceeded:
    ...     while not exceeded:
    ...         pass
    Traceback (most recent call last):
       ...
    TimeoutError: My error message. Elapsed: ...

    """
    msg = raise_exc if isinstance(raise_exc, str) else 'Timeout exceeded after {:.3g} seconds.'

    exceeded = TimeoutExceeded(value)
    try:
        yield exceeded
    except Exception:
        exceeded.freeze()
        raise
    else:
        exceeded.freeze()
        if not exceeded:
            return
        if on_exceeded is not None:
            on_exceeded(exceeded.elapsed)
        if raise_exc:
            raise TimeoutError(msg.format(exceeded.elapsed))


def deprecate_kwargs(*args, **kwargs):
    """Decorator factory to deprecate keyword arguments.

    Optionally in favor of replacements.

    Parameters
    ----------
    *args :
        Positional arguments should be valid identifiers that will be
        treated as keyword arguments to be deprecated without
        replacement.
    **kwargs :
        Key-value pairs of keyword arguments that should be deprecated
        *with* replacement: ``{old: new}``.

    Examples
    --------
    Deprecate a kwarg in favor of a new name:

    >>> @deprecate_kwargs(old='new')
    ... def foo(new=3):
    ...     print(new)

    Promote warnings to errors for doctest:

    >>> with filter_warnings(action='error', category=DeprecationWarning):
    ...     foo(old=4)
    Traceback (most recent call last):
    ...
    DeprecationWarning: Keyword argument 'old' of foo is deprecated. Use 'new' instead.

    Using the new name works as expected:

    >>> foo(new=5)
    5

    Only deprecate a kwarg without giving a replacement:

    >>> @deprecate_kwargs('old')
    ... def foo(new=3):
    ...     print(new)

    Again promote the warning to an error:

    >>> with filter_warnings(action='error', category=DeprecationWarning):
    ...     foo(old=4)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    DeprecationWarning: Keyword argument 'old' of foo is deprecated.

    Without promoting the warning, a regular :class:`TypeError` is raised:

    >>> foo(old=4)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: foo() got an unexpected keyword argument 'old'

    Multiple deprecations:

    >>> @deprecate_kwargs(old1='new1', old2='new2')
    ... def foo(new1=3, new2=4):
    ...     print(new1, new2)
    >>> with filter_warnings(action='error', category=DeprecationWarning):
    ...     foo(old1=4)
    Traceback (most recent call last):
    ...
    DeprecationWarning: Keyword argument 'old1' of foo is deprecated. Use 'new1' instead.
    >>> with filter_warnings(action='error', category=DeprecationWarning):
    ...     foo(old2=5)
    Traceback (most recent call last):
    ...
    DeprecationWarning: Keyword argument 'old2' of foo is deprecated. Use 'new2' instead.

    """

    def decorator(func):

        @wraps(func)
        def wrapped(*a, **kw):
            def _handle_single(o, n=None):
                if o not in kw:
                    return

                msg = f"Keyword argument '{o}' of {func.__qualname__} is deprecated."
                if n is not None:
                    if n in kw:
                        raise TypeError(msg + f" Cannot also specify '{n}'.")
                    else:
                        msg = msg + f" Use '{n}' instead."
                        kw[n] = kw.pop(o)

                warnings.warn(msg, DeprecationWarning, stacklevel=3)

            for arg in args:
                _handle_single(arg)
            for old, new in kwargs.items():
                _handle_single(old, new)
            return func(*a, **kw)

        return wrapped

    return decorator


@deprecated('Use deprecate_kwargs instead')
def deprecate_kwarg(old: str, new: str | None = None):
    return deprecate_kwargs(old=new)

