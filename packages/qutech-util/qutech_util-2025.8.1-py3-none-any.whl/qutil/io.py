from __future__ import annotations

import asyncio
import atexit
import csv
import importlib
import os.path
import pathlib
import pickle
import re
import string
import sys
import textwrap
import warnings
from concurrent.futures import Future
from contextlib import contextmanager
from threading import Lock, Thread
from typing import Union
from unittest import mock

import numpy as np

from .functools import partial

try:
    import dill
except ImportError:
    dill = mock.Mock()
if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if os.name == 'nt':
    _POSIX = False
    import winreg
else:
    _POSIX = True

_VALID_YESNO_ANSWERS = {"yes": True, "y": True, "ye": True,
                        "no": False, "n": False}
_HOST_RE = re.compile(r"(janeway|ag-bluhm-[0-9]+)(?![.\d])", re.IGNORECASE)
_HOST_SUFFIX = '.physik.rwth-aachen.de'

PathType: TypeAlias = Union[str, os.PathLike]


def _host_append_suffix(match: re.Match) -> str:
    return match.group() + _HOST_SUFFIX


@contextmanager
def changed_directory(new_directory: os.PathLike):
    r"""Temporarily change to a new directory.

    Equivalent to::

        pushd new_directory
        ...
        popd

    Examples
    --------
    >>> import tempfile, os
    >>> print(os.getcwd())  # doctest: +SKIP
    Z:\Code\qutil
    >>> with (
    ...         tempfile.TemporaryDirectory() as tempdir,
    ...         changed_directory(tempdir)
    ... ):
    ...     print(os.getcwd())  # doctest: +SKIP
    C:\Users\HANGLE~1\AppData\Local\Temp\tmpwzayb4vq
    >>> print(os.getcwd())  # doctest: +SKIP
    Z:\Code\qutil
    """

    original_directory = os.getcwd()
    try:
        os.chdir(new_directory)
        yield
    finally:
        os.chdir(original_directory)


def show_saved_figure(path):
    """Unpickle and show a pickled matplotlib figure.

    Parameters
    ----------
    path: str | pathlib.Path
        The path where the figure is saved.

    Returns
    -------
    fig: matplotlib.figure.Figure
        The matplotlib figure instance.

    """
    fig = pickle.load(open(path, 'rb'))

    import matplotlib.pyplot as plt
    dummy = plt.figure()
    new_manager = dummy.canvas.manager
    new_manager.canvas.figure = fig
    fig.set_canvas(new_manager.canvas)

    plt.show()
    return fig


def save_figure(fig, path):
    """Pickle a matplotlib figure.

    Parameters
    ----------
    fig: matplotlib.figure.Figure
        The matplotlib figure instance to be saved.
    path: str | pathlib.Path
        The path where the figure is saved.

    """
    pickle.dump(fig, open(path, 'wb'))


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be "yes" (the default), "no" or None (meaning
    an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return _VALID_YESNO_ANSWERS[default]
        elif choice in _VALID_YESNO_ANSWERS:
            return _VALID_YESNO_ANSWERS[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def query_overwrite(filepath: str | os.PathLike, default: str = 'no') -> pathlib.Path:
    """Query if file at filepath should be overwritten if it exists.

    Parameters
    ----------
    filepath : Union[str, os.PathLike]
        The file in question.
    default : str, optional
        The default answer. The default is 'no'.

    Returns
    -------
    filepath : pathlib.Path
        The original filepath if the answer was yes. The input path
        else.

    Raises
    ------
    FileExistsError
        If the file exists and the user pressed Ctrl-C to abort.

    """
    overwrite = _VALID_YESNO_ANSWERS[default]
    while not overwrite and (filepath := pathlib.Path(filepath)).is_file():
        if not (overwrite := query_yes_no(f'File {filepath} exists. Overwrite?', default)):
            try:
                filepath = input('Enter a new file name or path or press Ctrl-C to abort: ')
            except KeyboardInterrupt:
                raise FileExistsError(filepath) from None
    return filepath


def to_global_path(path: str | os.PathLike, warn: bool = False) -> pathlib.Path:
    r"""A Path that automatically replaces network drive labels and host names.

    This is useful for saving files in a way that they can be read from
    anywhere, independent of whether the host computer is known in the
    domain or has been mounted as a network share.

    .. note::
        Starting with Python 3.12, subclassing :class:`pathlib.Path` is
        possible, so this functionality could be more nicely
        implemented: https://github.com/python/cpython/pull/31691.

    Parameters
    ----------
    path : str | os.PathLike
        The path to resolve.
    warn : bool, default False
        Warn if on a posix system and mount points cannot be resolved.

    Examples
    --------
    Assuming ``\\janeway.physik.rwth-aachen.de\User AG Bluhm\Common`` is
    mounted as ``Y:\``:

    >>> to_global_path(r'Y:\GaAs')  # doctest: +SKIP
    WindowsPath('//janeway.physik.rwth-aachen.de/User AG Bluhm/Common/GaAs')

    If Y:/ is instead not a network but a local drive, nothing is resolved:

    >>> to_global_path(r'C:\Users\Tobias')  # doctest: +SKIP
    WindowsPath('C:/Users/Tobias')

    Host names are also resolved:

    >>> to_global_path(r'\\ag-bluhm-51\local_share')  # doctest: +SKIP
    WindowsPath('//ag-bluhm-51.physik.rwth-aachen.de/local_share/')

    But if the path is already the full host path, nothing happens:

    >>> to_global_path(r'\\janeway.physik.rwth-aachen.de\User AG Bluhm')  # doctest: +SKIP
    WindowsPath('//janeway.physik.rwth-aachen.de/User AG Bluhm/')

    """
    # TODO: implement as Path subclass for Python 3.12
    path = pathlib.Path(path).expanduser().absolute()
    if isinstance(path, pathlib.PosixPath):
        if warn:
            warnings.warn('Cannot resolve mount points on Unix', UserWarning)
        return path.resolve()

    root, *rest = path.parts
    if root == os.path.sep:
        # Somehow pathlib drops one slash if there is no child
        root = 2 * root + rest[0]
        rest = rest[1:]
    root = _HOST_RE.sub(_host_append_suffix, root)
    if root[0] in string.ascii_uppercase and root[1] == ':':
        # Resolve a mapped network share
        root = os.path.realpath(root)
    if path != (newpath := pathlib.Path(root, *rest)):
        # Recursively resolve hosts
        return to_global_path(newpath, warn)
    return path


def check_path_length(path: str | os.PathLike, ask_for_new: bool = True) -> pathlib.Path:
    """Check whether a path is too long for Windows.

    Parameters
    ----------
    path : Union[str, os.PathLike]
        The path to be checked.
    ask_for_new : bool, optional
        If True, the user is asked to input a new path if the original
        path was too long. Else, this function basically just gives a
        more informative error than by default. The default is True.

    Raises
    ------
    PathTooLongError
        If the path is too long and ask_for_new is False or input was
        aborted.

    Returns
    -------
    path : pathlib.Path
        The valid path.

    """
    path = pathlib.Path(path)
    if _POSIX:
        # For all intents and purposes no length limit (4095 chars)
        return path

    # Windows, check if more than 256 chars are allowed
    sub_key = 'SYSTEM\\CurrentControlSet\\Control\\FileSystem'
    hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key)

    if winreg.QueryValueEx(hkey, 'LongPathsEnabled')[0]:
        return path

    while len(str(path)) > 259:
        try:
            if not ask_for_new:
                raise KeyboardInterrupt
            warnings.warn(
                textwrap.dedent(
                    f"""
                    The path {os.path.sep.join((path.drive, path.parts[1], '...', path.parts[-1]))}
                    is too long. Please specify a new path or press Ctrl-C.

                    Note: On Windows, the maximum length for a path is 260 characters [1]. Thus,
                        excluding the terminating null character, 259 are available. You can
                        increase this limit by setting the following registry value to 1:
                        HKEY_LOCAL_MACHINE\\{sub_key}\\LongPathsEnabled

                    [1]: https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry
                    """
                ),
                UserWarning
            )
            path = to_global_path(input('\nNew path: '))
        except KeyboardInterrupt:
            raise PathTooLongError(path) from None
    return path


class PathTooLongError(FileNotFoundError):
    """Indicates a Windows path is longer than 260(256) characters."""
    pass


class CsvLogger:
    """Logger that only open file for writing. Use pandas.read_csv to read csv files"""
    def __init__(self, filename: str, fieldnames: list, dialect='excel-tab', append=False):
        self.dialect = csv.get_dialect(dialect)
        self.filename = os.path.abspath(filename)
        self.fieldnames = fieldnames

        if os.path.exists(filename):
            if not append:
                raise FileExistsError

            # validate file has the correct header
            with open(filename) as file:
                reader = csv.DictReader(file, dialect=dialect)

                if reader.fieldnames != fieldnames:
                    raise RuntimeError("Existing file has differing fieldnames", reader.fieldnames, fieldnames)

        else:
            with open(self.filename, 'x') as file:
                csv.DictWriter(file, fieldnames=self.fieldnames, dialect=self.dialect).writeheader()

    def write(self, *args):
        with open(self.filename, 'a+') as file:
            csv.DictWriter(file, fieldnames=self.fieldnames, dialect=self.dialect).writerow(dict(zip(self.fieldnames, args)))


class AsyncDatasaver:
    """Class to handle asynchronous data saving using NumPy.

    To save data, either call this class or use :meth:`save_async`.
    Data can also be saved synchronously using :meth:`save_sync`.

    When pickling is enabled, uses :mod:`dill` instead of :mod:`pickle`.

    Parameters
    ----------
    pickle_lib :
        Which library to use for pickling. Defaults to :mod:`pickle`,
        but may also be :mod:`dill`, for instance.
    compress :
        Compress binary data. Uses :func:`numpy:numpy.savez_compressed`
        and :func:`numpy:numpy.savez` otherwise.

    Examples
    --------
    Generate some data and test performance. Set up the datasaver.

    >>> import pathlib, tempfile, time
    >>> tmpdir = pathlib.Path(tempfile.mkdtemp())
    >>> data = np.random.randn(2**20)
    >>> datasaver = AsyncDatasaver()

    Baseline of the synchronous version (which just wraps
    :func:`numpy:numpy.savez`):

    >>> tic = time.perf_counter()
    >>> datasaver.save_sync(tmpdir / 'foo.npz', data=data)
    >>> print(f'Writing took {time.perf_counter() - tic:.2g} seconds.')  # doctest: +ELLIPSIS
    Writing took ... seconds.

    Now the asynchronous version:

    >>> tic = time.perf_counter()
    >>> datasaver.save_async(tmpdir / 'foo.npz', data=data)
    >>> tac = time.perf_counter()
    >>> while datasaver.jobs:
    ...     pass
    >>> toe = time.perf_counter()
    >>> print(f'Blocked for {tac - tic:.2g} seconds.')  # doctest: +ELLIPSIS
    Blocked for ... seconds.
    >>> print(f'Writing took {toe - tic:.2g} seconds.')  # doctest: +ELLIPSIS
    Writing took ... seconds.

    Evidently, there is some tradeoff between total I/O time and
    blocking I/O time.

    On exit, gracefully shut down the datasaver:

    >>> datasaver.shutdown()

    The datasaver can also be used as a context manager, in which case
    cleanup is automatically taken care of. For syntactic sugar, calling
    the datasaver has the same effect as
    :meth:`AsyncDatasaver.save_async`.

    >>> with AsyncDatasaver() as datasaver:
    ...     datasaver(tmpdir / 'foo.npz', data=data/2)
    ...     datasaver(tmpdir / 'bar.npz', data=2*data)

    """
    def __init__(self, pickle_lib: str = 'pickle', compress: bool = False):
        self._pickle_lib = importlib.import_module(pickle_lib)
        self._savefn = np.savez_compressed if compress else np.savez
        self.jobs: dict[Future, PathType] = {}
        self.loop = asyncio.new_event_loop()
        self.lock = Lock()
        self.thread = Thread(target=self._start_loop, daemon=True)
        self.thread.start()
        # Make sure all io tasks are done when shutting down the interpreter
        atexit.register(self.shutdown, timeout=60)

    def __call__(self, file: PathType, **data):
        self.save_async(file, **data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _mark_done(self, future: Future):
        with self.lock:
            try:
                future.result()
            except Exception as e:
                print(f"Error in async task for file {self.jobs.get(future)}: {e}")
            finally:
                self.jobs.pop(future, None)

    async def _save_data(self, file: PathType, allow_pickle: bool = True, **data):
        """Coroutine to asynchronously save data in a thread.

        Use :meth:`py:asyncio.loop.set_default_executor` to set the
        executor used by this function.
        """
        # Use the default executor
        await self.loop.run_in_executor(None, partial(self.save_sync, file,
                                                      allow_pickle=allow_pickle, **data))

    def save_sync(self, file: PathType, allow_pickle: bool = True, **data):
        """Save arbitrary key-val pairs to *file* synchronously.

        See :func:`numpy:numpy.savez` for more information.
        """
        with mock.patch.multiple(
                'pickle',
                Unpickler=self._pickle_lib.Unpickler,
                Pickler=self._pickle_lib.Pickler
        ):
            self._savefn(str(file), allow_pickle=allow_pickle, **data)

    def save_async(self, file: PathType, allow_pickle: bool = True, **data):
        """Save arbitrary key-val pairs to *file* asynchronously.

        See :func:`numpy:numpy.savez` for more information.
        """
        with self.lock:
            self.jobs[
                # parens necessary for py39..
                (future := asyncio.run_coroutine_threadsafe(
                    self._save_data(file, allow_pickle=allow_pickle, **data),
                    self.loop
                ))
            ] = file
        future.add_done_callback(self._mark_done)

    def shutdown(self, timeout: float | None = None):
        """Shut down the object, waiting for all I/O tasks to finish."""
        with self.lock:
            jobs_snapshot = list(self.jobs.items())
        for future, file in jobs_snapshot:
            try:
                future.result(timeout)
            except Exception as e:
                print(f"Exception when waiting for {file} to write, or timeout: {e}")

        self.jobs.clear()
        try:
            self.loop.call_soon_threadsafe(self.loop.stop)
        except RuntimeError:
            # loop already closed
            return
        else:
            self.thread.join(timeout)
            self.loop.close()
