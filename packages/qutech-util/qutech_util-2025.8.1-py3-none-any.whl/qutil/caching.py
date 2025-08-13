"""Programming tools"""
import dbm
import functools
import inspect
import os.path
import pathlib
import pickle
import shelve
import tempfile
from collections.abc import Mapping
from typing import Any, Callable, Optional

import numpy as np

__all__ = ["file_cache", "lru_cache"]


def to_str_key(obj: Any) -> str:
    """Convert to a string representation that is unique except for
    - lists and ndarrays are treated the same

    :param obj:
    :return:
    """
    if isinstance(obj, tuple):
        return f'({",".join(map(to_str_key, obj))})'
    if isinstance(obj, np.ndarray):
        return to_str_key(obj.tolist())
    elif isinstance(obj, list):
        return f'[{",".join(map(to_str_key, obj))}]'
    elif isinstance(obj, Mapping):
        return '{%s}' % ",".join(f"{to_str_key(key)}: {to_str_key(value)}" for key, value in obj.items())
    elif isinstance(obj, (set, frozenset)):
        return f'{{{",".join(sorted(map(to_str_key, obj)))}}}'
    elif isinstance(obj, (int, float, complex, str, bytes, pathlib.Path)) or obj is None:
        return repr(obj)
    else:
        try:
            if eval(repr(obj)) == obj:
                return repr(obj)
        except RuntimeError:
            pass
        raise TypeError('not handled: ', type(obj))


class _AlwaysOpenCacheWrapper:
    def __init__(self, func: callable, db: shelve.Shelf):
        self.func = func
        self.db = db

    def __call__(self, *args, **kwargs):
        key = to_str_key((args, kwargs))
        if key in self.db:
            result = self.db[key]
        else:
            self.db[key] = result = self.func(*args, **kwargs)
        return result


class CachingWrapper:
    """This object wraps a callable and caches the results in a dbm database on the file system (by default in the temp
    folder). The key is generated via to_key which means that large arguments need a large time to process.

    >>> @file_cache
    ... def my_expensive_fn(a, b):
    ...     # do expensive stuff here
    ...     for x in range(a + b):
    ...         for y in range(x):
    ...             if x * y == a + b:
    ...                return x, y

    >>> my_expensive_fn(10, 5) # does calculation and saves result into default temporary folder
    (5, 3)

    >>> my_expensive_fn(10, 5) # loads result from disk
    (5, 3)

    The returned function can be used as a context manager to avoid reopening and closing the storage backend between
    calls.

    >>> large_list = [(1, 2), (3, 4)]
    >>> with my_expensive_fn as fn:
    ...     results = [fn(x, y) for x, y in large_list]

    This also works if the call is nested

    >>> def my_other_function(c):
    ...     return my_expensive_fn(c, c)

    >>> with my_expensive_fn:
    ...     results = [my_other_function(z) for z in range(1000)]

    The context manager is reentrant.
    """

    DEFAULT_ROOT = os.path.join(tempfile.gettempdir(), 'qutil_cache')
    PICKLE_PROTOCOL = pickle.HIGHEST_PROTOCOL

    def __init__(self, func, storage_path=None):
        self._func = func

        if storage_path is None:
            storage_path = os.path.join(self.DEFAULT_ROOT, self.get_full_function_name(func))

        self.storage_path = storage_path
        self._db: Optional[shelve.Shelf] = None
        self._wrapper = None
        self._entrance_counter = 0

    def __call__(self, *args, **kwargs):
        with self as wrapper:
            return wrapper(*args, **kwargs)

    def clear(self):
        """Clears cache of this function."""
        with self as wrapper:
            wrapper.db.clear()
    
    def __enter__(self) -> callable:
        if self._entrance_counter:
            assert self._db is not None
            assert self._wrapper is not None
        else:
            assert self._db is None
            assert self._wrapper is None
            folder = pathlib.Path(self.storage_path).parent
            if not folder.exists():
                folder.mkdir()
            self._db = shelve.open(self.storage_path, protocol=self.PICKLE_PROTOCOL)
            self._wrapper = _AlwaysOpenCacheWrapper(db=self._db, func=self._func)
        self._entrance_counter += 1
        return self._wrapper

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._entrance_counter > 0
        self._entrance_counter -= 1
        if self._entrance_counter == 0:
            self._db.close()
            self._db = None
            self._wrapper = None

    @classmethod
    def get_full_function_name(cls, func) -> str:
        return f"{inspect.getmodule(func).__name__}.{func.__name__}"

    @classmethod
    def clear_all_default_caches(cls):
        """Clear all caches that are in the default cache directory"""
        root = pathlib.Path(cls.DEFAULT_ROOT)
        if root.exists():
            for bak in root.glob('*.bak'):
                base_name = bak.with_suffix('')

                try:
                    shelve.open(str(base_name), 'r')
                except dbm.error:
                    print('Cannot open', bak.stem, 'and will not delete.')
                else:
                    bak.unlink()
                    base_name.with_suffix('.dir').unlink(missing_ok=True)
                    base_name.with_suffix('.dat').unlink(missing_ok=True)


def file_cache(func: Callable) -> Callable:
    """See doc of CachingWrapper."""
    return CachingWrapper(func)


lru_cache = functools.lru_cache
cache = getattr(functools, 'cache', lru_cache)  # available starting Python 3.9
