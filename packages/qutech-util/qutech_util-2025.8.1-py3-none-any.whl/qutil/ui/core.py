"""This module contains UI utility functions."""
from __future__ import annotations

import logging
import os
import socketserver
import sys
import webbrowser
from collections.abc import Iterable
from http.server import SimpleHTTPRequestHandler
from threading import Thread
from typing import Optional, TextIO

from ..functools import wraps

__all__ = ['progressbar', 'progressbar_range']


def _in_spyder_kernel():
    """Determine if we are currently running inside spyder on a best effort basis."""
    return 'SPY_PYTHONPATH' in os.environ


def _in_notebook_kernel():
    # https://github.com/jupyterlab/jupyterlab/issues/16282
    return 'JPY_SESSION_NAME' in os.environ and os.environ['JPY_SESSION_NAME'].endswith('.ipynb')


def _in_jupyter_kernel():
    # https://discourse.jupyter.org/t/how-to-know-from-python-script-if-we-are-in-jupyterlab/23993
    return 'JPY_PARENT_PID' in os.environ


if not _in_notebook_kernel():
    if _in_jupyter_kernel():
        # Autonotebook gets confused in jupyter consoles
        from tqdm.std import tqdm, trange
    else:
        from tqdm.autonotebook import tqdm, trange
else:
    from tqdm.notebook import tqdm, trange


class TCPServerThread(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ThreadedWebserver:
    """Serves a simple HTTP server in a background thread.

    If *qcodes_monitor_mode* is true, the port will be grabbed from
    :mod:`qcodes:qcodes.monitor.monitor`.

    Examples
    --------
    Run as server for the qcodes monitor:

    >>> from qcodes.monitor import Monitor
    >>> from qcodes.parameters import ManualParameter
    >>> server = ThreadedWebserver(qcodes_monitor_mode=True)
    >>> server.show()
    >>> monitor = Monitor(ManualParameter('foobar'))

    Join the threads again:

    >>> monitor.stop()
    >>> server.stop()

    """

    def __init__(self, qcodes_monitor_mode: bool = False, url: str = 'localhost',
                 port: int = 3000):
        if qcodes_monitor_mode:
            # Copy stuff from qcodes.monitor.monitor. Purely convenience
            from qcodes.monitor import monitor
            self.port = monitor.SERVER_PORT
            self.log = monitor.log
            self.static_dir = STATIC_DIR = os.path.join(os.path.dirname(monitor.__file__), "dist")

            class HTTPRequestHandler(SimpleHTTPRequestHandler):
                def __init__(self, *args, directory: str | None = ..., **kwargs):
                    super().__init__(*args, directory=STATIC_DIR, **kwargs)

        else:
            self.port = port
            self.log = logging.getLogger(__name__)

            class HTTPRequestHandler(SimpleHTTPRequestHandler):
                ...
        self.url = url

        self.log.info(f"Starting HTTP Server at http://{self.url}:{self.port}")
        self.server = TCPServerThread(("", self.port), HTTPRequestHandler)
        self.thread = self.server.server_thread = Thread(target=self.server.serve_forever)
        self.thread.start()

    def __del__(self):
        self.stop()

    def stop(self):
        self.log.info("Shutting Down HTTP Server")
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def show(self, new=0, autoraise=True):
        """Show the server in a browser.

        See :func:`webbrowser:webrowser.open` for parameters.
        """
        webbrowser.open(f"http://{self.url}:{self.port}", new=new, autoraise=autoraise)

    open = show


def _simple_progressbar(iterable: Iterable, desc: str = "Computing", disable: bool = False,
                        total: int | None = None, size: int = 25, file: TextIO = sys.stdout,
                        *_, **__):
    """https://stackoverflow.com/a/34482761"""
    if disable:
        yield from iterable
        return

    if total is None:
        try:
            total = len(iterable)
        except TypeError:
            raise ValueError(f'{iterable} has no len, please supply the total argument.')

    def show(j):
        x = int(size*j/total)
        file.write("\r{}:\t[{}{}] {} %".format(desc, "#"*x, "."*(size - x),
                   int(100*j/total)))
        file.flush()

    show(0)
    for i, item in enumerate(iterable):
        yield item
        show(i + 1)

    file.write("\n")
    file.flush()


class ProgressbarLock:
    """A global lock for progressbars used as a decorator.

    The intended use case is to keep nested progressbars from interfering in
    non-interactive (notebook) mode.

    Examples
    --------
    >>> import time
    >>> for i in progressbar_range(10, desc='outer', file=sys.stdout):
    ...     for j in progressbar_range(10, desc='inner', file=sys.stdout, leave=False):
    ...         time.sleep(0.05) # doctest: +NORMALIZE_WHITESPACE
    outer: ...
    >>> for i in progressbar_range(10, desc='outer', file=sys.stdout, disable=True):
    ...     for j in progressbar_range(10, desc='inner', file=sys.stdout):
    ...         time.sleep(0.05)  # doctest: +NORMALIZE_WHITESPACE
    inner: ...

    Does nothing on a single, not nested bar:

    >>> for i in progressbar('asdf', desc='only', file=sys.stdout):
    ...     time.sleep(0.05)  # doctest: +NORMALIZE_WHITESPACE
    only: ...

    """
    _stack: list[bool] = []
    DISABLED: bool = False
    """Globally disable the locking mechanism."""

    def __call__(self, func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            # No need to lock if the bar is disabled dynamically.
            disable = kwargs.get('disable', False)

            if not self.DISABLED and (disable or not all(self._stack)):
                self.lock(True)
            else:
                self.lock(False)

            kwargs['disable'] = self.locked
            try:
                yield from func(*args, **kwargs)
            finally:
                self.release()

        return wrapper

    @property
    def locked(self) -> bool:
        try:
            return self._stack[-1]
        except IndexError:
            return False

    def lock(self, val: bool):
        """Lock the bar in the current loop if True."""
        self._stack.append(val)

    def release(self):
        self._stack.pop()


def auto_progress_bar_lock(pbar_function: callable) -> callable:
    """Enable progress bar lock for the given progress bar if a qtconsole kernel is detected."""
    # The second condition should also fire if in a spyder kernel, so technically doppelt-gemoppelt
    if _in_spyder_kernel() or (_in_jupyter_kernel() and not _in_notebook_kernel()):
        return ProgressbarLock()(pbar_function)
    else:
        return pbar_function


@auto_progress_bar_lock
def progressbar(iterable: Iterable, *args, **kwargs):
    """
    Progress bar for loops. Uses tqdm if available or a quick-and-dirty
    implementation from stackoverflow.

    Usage::

        for i in progressbar(range(10)):
            do_something()

    See :class:`~tqdm.tqdm` or :func:`_simple_progressbar` for possible
    args and kwargs.
    """
    if tqdm is not None:
        return tqdm(iterable, *args, **kwargs)
    else:
        return _simple_progressbar(iterable, *args, **kwargs)


@auto_progress_bar_lock
def progressbar_range(*args, **kwargs):
    if tqdm is not None:
        return trange(*args, **kwargs)
    else:
        return _simple_progressbar(range(*args), **kwargs)
