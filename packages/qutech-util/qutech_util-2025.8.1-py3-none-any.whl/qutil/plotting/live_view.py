"""This module provides classes for live-plotting using :mod:`matplotlib:matplotlib`.

See :class:`LiveViewBase` for an overview of the arguments and its
subclasses for examples.
"""
from __future__ import annotations

import abc
import dataclasses
import importlib
import inspect
import json
import logging
import multiprocessing as mp
import queue
import shutil
import sys
import tempfile
import threading
import time
import warnings
import weakref
from collections import deque
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from multiprocessing.managers import SyncManager
from pathlib import Path
from types import ModuleType
from typing import Any, Literal, TypeVar, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from matplotlib import animation, colorbar
from matplotlib import patches as mpatches
from matplotlib import scale
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.backend_bases import KeyEvent, TimerBase
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpecFromSubplotSpec
from matplotlib.widgets import Button

from .. import functools, io, itertools, misc
from .core import assert_interactive_figure, is_using_mpl_gui_backend, norm_to_scale, reformat_axis

if sys.version_info >= (3, 10):
    from typing import ParamSpec, Protocol, TypeAlias
else:
    from typing_extensions import ParamSpec, Protocol, TypeAlias

_LOG = logging.getLogger(__name__)

EVENT_LOOP_TIMEOUT = 1 / 60
"""The time the event loop is spun while waiting for new data.

60 fps seems like a comfortably fast rate for the figure to feel
responsive, but feel free to reduce this at cost of CPU usage.
"""
MAX_CLOCK_LENGTH = 100
"""The maximum number of most recent event times to track."""

P = ParamSpec('P')
T = TypeVar('T')
ArtistT = TypeVar('ArtistT', bound=Artist)
"""A matplotlib artist type."""
ScaleT = TypeVar('ScaleT', bound=scale.ScaleBase)
"""A matplotlib scale type."""
TimerT = TypeVar('TimerT', bound=TimerBase)
"""A matplotlib timer type."""
StyleT: TypeAlias = Union[str, dict[str, Any], Path]
"""A matplotlib style type allowed in
:func:`matplotlib:matplotlib.style.use`."""


class DataSource(Protocol[P, T]):
    """Protocol for data-producing thread target."""

    def __call__(self,
                 data_queue: queue.Queue[T] | mp.JoinableQueue[T],
                 stop_event: threading.Event | mp.Event,
                 **kwargs: P.kwargs) -> None:
        pass


class LineOperation(Protocol):
    """Reduction operation from 2D to 1D."""
    label: str
    """An axis label."""

    def __call__(self, x: npt.ArrayLike) -> npt.NDArray: ...


class Clock(deque):
    """A simple clock that can be used as a callback to store call times."""

    def __call__(self):
        self.append(time.perf_counter())

    def last_dt(self) -> float:
        """The time between the last two calls."""
        if len(self) > 1:
            return self[-1] - self[-2]
        else:
            return np.nan

    def avg_dt(self) -> float:
        """The average time between calls."""
        if len(self) > 1:
            return np.diff(self).mean()
        else:
            return np.nan


@dataclasses.dataclass
class OneTimeFlag:
    """A single-use flag that resets to False if it evaluated to True."""
    _val: bool = False

    def __bool__(self) -> bool:
        if bool(self._val):
            self.unset()
            return True
        return False

    def set(self):
        """Set the flag to True."""
        self._val = True

    def unset(self):
        """Set the flag to False."""
        self._val = False


# TODO: staticmethod when py39 is dropped
def _queue_draw(rescale: Callable[P, bool]) -> Callable[P, None]:
    """Wrap `rescale` to set the flag requesting a draw.

    This decorator is required for rescaling in blitted mode as
    otherwise shadows of old frames are not removed.
    """

    @functools.wraps(rescale)
    def wrapped(self: LiveViewT, *args: P.args, **kwargs: P.kwargs):
        # First unset so that draws are deferred until after rescale() ran
        draw_enqueued = bool(self.animation.draw_enqueued)
        draw_required = rescale(self, *args, **kwargs)
        if draw_required or draw_enqueued:
            self.animation.draw_enqueued.set()

    return wrapped


class FuncAnimation(animation.FuncAnimation):
    """Animation with optional redraw of entire figure.

    Set the :attr:`draw_enqueued` flag using :meth:`OneTimeFlag.set` to
    request a redraw of the entire figure at the next frame update.

    Furthermore, this class modifies matplotlib's implementation to draw
    the first frame immediately after starting instead of waiting for
    one `interval` to pass.

    See :class:`~matplotlib:matplotlib.animation.FuncAnimation` for
    parameters and documentation.
    """

    def __init__(self, fig, func, frames=None, init_func=None, fargs=None,
                 save_count=None, *, cache_frame_data=True, event_source=None, **kwargs):

        self._draw_enqueued = OneTimeFlag()
        self._LOG = logging.getLogger(f'{__name__}.{self.__class__.__qualname__}')
        self._LOG.addFilter(_ProcessNameFilter())

        super().__init__(fig, func, frames, init_func, fargs, save_count,
                         cache_frame_data=cache_frame_data, event_source=event_source, **kwargs)

    @property
    def draw_enqueued(self) -> OneTimeFlag:
        """Flag indicating that the full figure should be drawn at the
        next occasion."""
        return self._draw_enqueued

    def _post_draw(self, framedata, blit):
        if self.draw_enqueued:
            # It's not clear to me why, but a full draw() is required here
            # instead of a draw_idle(). The latter will only paint over old
            # artists but not remove them.
            self._fig.canvas.draw()

        # If blit is not enabled, super()'s method will trigger a draw_idle()
        # but this should not do anything if draw() was called above.
        super()._post_draw(framedata, blit)

    def _start(self, *args):
        # Since _step() is only added right before starting the animation, and
        # we want it to execute once before resetting the interval, we need to
        # add the callback doing that *after* calling super's _start(). This
        # means a tiny delay between starting and drawing the first frame, but
        # oh well.
        self._LOG.debug('Starting animation.')
        super()._start(*args)

    def _stop(self, *args):
        self._LOG.debug('Stopping animation.')
        super()._stop(*args)

    def _step(self, *args):
        # Sometimes the super method returns still_going when the event
        # source has actually already been deleted. Due to the way animations
        # work, at this point in the code we cannot prevent the error from
        # occurring anymore.
        # TODO: obsolete?
        try:
            return super()._step(*args)
        except AttributeError:
            if self.event_source is None:
                self._LOG.error('_step() was called by timer after _stop() had already been '
                                'called. This caused the following error in matplotlib and is '
                                'probably due to timing inaccuracies.')
            raise


class LiveViewBase(abc.ABC):
    """Base class for live plotting using :mod:`matplotlib`.

    Subclasses can add animated artists by overriding
    :meth:`_add_animated_artists` and define how the artists are
    updated in :meth:`_update`.

    To start the live view, call :meth:`start`.

    .. note::
        Only artists inside axes are animated. Hence, titles and labels
        will not be updated if blitting is enabled.

    Parameters
    ----------
    data_source :
        A callback that puts new data into a :class:`queue.Queue` until
        a :class:`threading.Event` is set. The callback is run in a
        separate thread and should have the following signature::

            (queue.Queue, threading.Event, *, ...) -> None

        That is, they should implement the :class:`DataSource`
        interface.

        The required return value depends on the subclass
        implementation of :meth:`_update`.
    update_interval_ms :
        The interval in milliseconds in which to run the matplotlib
        event loop, i.e., the (maximum) update rate of the plot.
    show_fps :
        Show a text annotation showing current and average frame rate.
    useblit :
        Use blitting to increase performance. Can cause issues with
        when data update rates are low and `autoscale` is enabled. For
        more information on blitting, see the matplotlib documentation
        [1]_.
    blocking_queue :
        Make the queue only accept one item before it is received. This
        results in the data production thread waiting for the plotting
        to catch up if the latter is too slow.
    autoscale :
        Automatically rescale the axes specified. Disabled if None or
        empty string.
    autoscale_interval_ms :
        The interval in milliseconds between automatic rescales. If
        None, rescales every time the plot is updated.
    event_source :
        A timer that triggers an update event. Should not be needed by
        users.
    xlabel :
        The x-axis label of the plot.
    ylabel :
        The y-axis label of the plot.
    units :
        Base SI units of the axes. SI prefixes will automatically be
        added when rescaling.
    xlim :
        Static xlims. If None, the limits are dynamic and can be
        rescaled using the button or the `autoscale` setting.
    ylim :
        Static ylims. If None, the limits are dynamic and can be
        rescaled using the button or the `autoscale` setting.
    xscale :
        Scale of the x-axis.
    yscale :
        Scale of the y-axis.
    style :
        A valid option for :func:`matplotlib:matplotlib.style.use`.
    fig :
        A figure to use for the plot.
    ax :
        An axes to use as the main axes of the plot.
    fig_kw :
        Keyword-arguments passed to the figure constructor.
    log_level :
        If not None, set logging level.
    **data_source_kwargs :
        Keyword arguments forwarded to the data callback.

    Examples
    --------
    For examples, see the implementations of this class in this module
    or in :mod:`mjolnir.plotting`.

    References
    ----------
    .. [1] https://matplotlib.org/stable/tutorials/advanced/blitting.html

    """
    # attributes relevant for subclasses.
    animation: FuncAnimation
    """The animation used to facilitate live plotting."""
    event_sources: dict[str, TimerT | object]
    """Event sources generating events for the animation event loop."""
    axes: dict[str, Axes]
    """The axes hosting artists."""
    animated_artists: dict[str, ArtistT]
    """The artists being animated."""
    static_artists: dict[str, ArtistT | Sequence[ArtistT]]
    """The artists that remain static."""
    buttons: dict[str, Button]
    """Clickable buttons."""
    cids: dict[str, int]
    """Event identifiers to keep track of."""
    data_thread: threading.Thread
    """The thread pushing data to the queue."""
    _xlabel_axes: Axes
    """Subclasses can set this attribute to specify the axes whose
    xlabel should be set."""
    _ylabel_axes: Axes
    """Subclasses can set this attribute to specify the axes whose
    ylabel should be set."""
    _event_clock: Clock
    """Tracks the times at which frames were requested."""

    @dataclasses.dataclass
    class LiveViewProxy:
        """A proxy class returned by :classmethod:`.LiveViewBase.in_process`
        handling communication with the child process."""
        process: mp.Process
        data_thread: threading.Thread
        data_queue: mp.JoinableQueue
        stop_event: mp.Event
        close_event: mp.Event
        """Flag that if set stops the emitting generator from polling the queue
        and spinning the event loop, and finally shuts down the view
        irrevocably."""
        _running: mp.Value = dataclasses.field(repr=False)
        _stopped: mp.Value = dataclasses.field(repr=False)

        def __post_init__(self):
            self._LOG = logging.getLogger(f'{__name__}.{self.__class__.__qualname__}')
            self._LOG.addFilter(_ProcessNameFilter())

        def __del__(self):
            try:
                # Disable logging in case logging system has already been shut down
                with misc.all_logging_disabled():
                    self.stop()
            except OSError:
                # [WinError 6] The handle is invalid
                pass
            finally:
                self.process.terminate()

        def block_until_ready(self):
            """Block the interpreter until the data thread has started."""
            self._LOG.debug('Waiting for data thread to start')
            with misc.timeout(30, raise_exc='thread could not be started in {}s.') as exceeded:
                # Thead is started from the process
                while not self.is_running() and not exceeded:
                    time.sleep(50e-3)
            self._LOG.debug(f'Waited {exceeded.elapsed:.3g}s for thread to start.')

        def is_running(self) -> bool | None:
            """Indicates if the view is currently running.

             - If True, the view is running and updating.
             - If False, the view is paused or stopped.

            """
            # two flags because run_flag can only be bool
            return None if self._stopped.value else bool(self._running.value)

        def stop(self):
            """Stop the data stream from the main process without killing
            the view object."""
            self._LOG.debug('Stopping live view.')
            _stop_safely(self.stop_event, self.data_thread, self.data_queue)
            self._stopped.value = True
            self._running.value = False

        def attach(self, data_source: DataSource, **data_source_kwargs):
            """Attach a new data source to the view and start it in a
            thread of the main process.

            The old thread will be terminated if still running.
            """
            if self.close_event.is_set():
                raise RuntimeError('This view has been closed. Please start a new view.')

            self._LOG.debug(f'Attaching new data source {data_source}')
            if self.data_thread.is_alive():
                self.stop()

            self.stop_event.clear()
            self.data_thread = threading.Thread(target=_safe_data_source(data_source),
                                                args=(self.data_queue, self.stop_event),
                                                kwargs=data_source_kwargs,
                                                daemon=True)
            self.data_thread.start()
            self._stopped.value = False
            self._running.value = True

    def __init__(self, data_source: DataSource, *, update_interval_ms: int = int(1e3 / 60),
                 autoscale: str | None = None, autoscale_interval_ms: int | None = 1000,
                 show_fps: bool = False, useblit: bool = True, blocking_queue: bool = True,
                 event_source: TimerT | None = None, xlabel: str = '', ylabel: str = '',
                 units: Mapping[Literal['x', 'y'], str] | None = None,
                 xlim: tuple[float, float] | None = None, ylim: tuple[float, float] | None = None,
                 xscale: str | ScaleT = 'linear', yscale: str | ScaleT = 'linear',
                 style: StyleT | Sequence[StyleT] = 'fast', fig: Figure | None = None,
                 ax: Axes | None = None, fig_kw: Mapping[str, Any] | None = None,
                 log_level: int | None = None, **data_source_kwargs):

        self._LOG = logging.getLogger(f'{__name__}.{self.__class__.__qualname__}')
        self._LOG.addFilter(_ProcessNameFilter())

        _setup_logging(log_level)

        tic = time.perf_counter()

        self.data_queue: queue.Queue | mp.JoinableQueue = queue.Queue(maxsize=int(blocking_queue))
        self.stop_event: threading.Event | mp.Event = threading.Event()
        # For multiprocessing, we need another event that is set in the on_close hook attached
        # to the figure because the emit generator should keep running when stop() is called but
        # exit when the figure is closed. This is in contrast to the threading scenario where we
        # can restart all GUI-related things when attaching a new data source and can therefore
        # stop emitting when stop() was called.
        self._close_event: mp.Event | None = None

        self.event_sources = {}
        self.update_interval_ms = round(update_interval_ms)
        self.show_fps = show_fps
        self.useblit = useblit
        self.autoscale = autoscale if autoscale is not None else ''
        self.autoscale_interval_ms = (round(autoscale_interval_ms)
                                      if autoscale_interval_ms is not None else None)
        self.fig_kw = fig_kw if fig_kw is not None else {}
        self.units = dict.fromkeys(['x', 'y'], '')
        if units is not None:
            self.units.update(units)
        self.xlim = xlim
        self.ylim = ylim
        self.style = style if isinstance(style, Sequence) else [style]

        self._event_clock = Clock(maxlen=MAX_CLOCK_LENGTH)
        self._first_frame: bool = True
        self._frame_count: int = 0
        self._stopped: mp.Value = mp.Value('b', True)
        self._running: mp.Value = mp.Value('b', False)
        self._text = 'Average fps: {:.1f}\nCurrent fps: {:.1f}'
        self._xlabel_text = xlabel
        self._ylabel_text = ylabel
        if self.units['x'] and xlabel != '':
            self._xlabel_text = self._xlabel_text + ' ({{{}}}{})'.format('', self.units['x'])
        if self.units['y'] and ylabel != '':
            self._ylabel_text = self._ylabel_text + ' ({{{}}}{})'.format('', self.units['y'])
        self._xscale = xscale
        self._yscale = yscale
        self._on_button_color = 'white' if 'dark_background' in self.style else 'black'
        self._off_button_color = 'tab:gray'

        with (plt.style.context(self.style, after_reset=True)):
            if fig is None:
                if ax is None:
                    fig = plt.figure(**self.fig_kw)
                else:
                    fig = ax.figure
            self.fig = fig

            assert_interactive_figure(self.fig)

            self._add_axes(ax)
            self._add_buttons()
            self._add_animated_artists()
            self._add_static_artists()

            # Attach the data source, adding interactive elements and event sources
            self.attach(data_source, **data_source_kwargs)

            self._add_events()
            self._add_event_sources(event_source)

            # We can try
            with misc.filter_warnings(action='ignore', category=UserWarning):
                try:
                    self.fig.tight_layout()
                except RuntimeError:
                    # Different layout engine
                    pass

        toc = time.perf_counter()
        self._LOG.info(f'Took {toc - tic:.2g}s to initialize.')

    @abc.abstractmethod
    def _update_labels(self, axis):
        """Reformat the axis ticks and possibly labels."""
        pass

    def _add_axes(self, ax_main: Axes | None = None):
        """Override and call to add additional axes."""
        # Another view might've already added the dedicated axes, so check first
        if ax_main is None and (ax_main := find_artist_with_label(self.fig.axes, 'main')) is None:
            ax_main = self.fig.add_subplot(label='main')
        elif ax_main.figure is not self.fig:
            raise ValueError('ax is not part of fig')
        if (ax_pause_resume := find_artist_with_label(self.fig.axes, 'pause_resume')) is None:
            ax_pause_resume = self.fig.add_axes((0.025, 0.025, 0.04, 0.04), frameon=False,
                                                label='pause_resume')
        if (ax_stop := find_artist_with_label(self.fig.axes, 'stop')) is None:
            ax_stop = self.fig.add_axes((0.075, 0.025, 0.04, 0.04), frameon=False, label='stop')
        if (ax_rescale := find_artist_with_label(self.fig.axes, 'rescale')) is None:
            ax_rescale = self.fig.add_axes((0.95, 0.025, 0.04, 0.04), frameon=False,
                                           label='rescale')

        ax_main.set_xscale(self._xscale)
        ax_main.set_yscale(self._yscale)

        if self.xlim is not None:
            ax_main.set_xlim(self.xlim)
            if 'x' in self.autoscale:
                warnings.warn('Static xlim given. Removing x from autoscale as it would not do '
                              'anything.')
                self.autoscale = self.autoscale.strip('x')
        if self.ylim is not None:
            ax_main.set_ylim(self.ylim)
            if 'y' in self.autoscale:
                warnings.warn('Static ylim given. Removing y from autoscale as it would not do '
                              'anything.')
                self.autoscale = self.autoscale.strip('y')

        self._xlabel_axes = ax_main
        self._ylabel_axes = ax_main

        self.axes = {'main': ax_main, 'pause_resume': ax_pause_resume, 'stop': ax_stop,
                     'rescale': ax_rescale}

    def _add_animated_artists(self):
        """Override and call to add additional animated artists."""
        self.animated_artists = {}

        if self.show_fps:
            fps = self.axes['main'].text(0.02, 0.02, '', animated=self.useblit,
                                         transform=self.axes['main'].transAxes)
            self.animated_artists['fps'] = fps

    def _add_static_artists(self):
        """Override and call to add additional static artists."""

        xlabel = self._xlabel_axes.set_xlabel(self._xlabel_text.format(''))
        ylabel = self._ylabel_axes.set_ylabel(self._ylabel_text.format(''))

        self.static_artists = {'xlabel': xlabel, 'ylabel': ylabel}

        ax = self.axes['pause_resume']
        # Another view might've already added the patches
        patches = find_artists_with_labels(ax.patches, {'resume', 'pause_1', 'pause_2'}).values()

        if all(patch is None for patch in patches):
            resume = mpatches.Polygon([[-10, -7], [1, 0], [-10, 7]],
                                      closed=True, color=self._off_button_color, label='resume')
            pause_1 = mpatches.Rectangle((3, -6), 2, 12, color=self._on_button_color,
                                         label='pause_1')
            pause_2 = mpatches.Rectangle((8, -6), 2, 12, color=self._on_button_color,
                                         label='pause_2')

            ax.add_patch(resume)
            ax.add_patch(pause_1)
            ax.add_patch(pause_2)

            ax.set_xlim(-10, 10)
            ax.set_ylim(-7, 7)
            ax.set_aspect(1)

            patches = (resume, pause_1, pause_2)

        self.static_artists['pause_resume'] = tuple(patches)

        ax = self.axes['stop']
        patches = find_artists_with_labels(ax.patches, {'stop'}).values()
        if all(patch is None for patch in patches):
            stop = mpatches.Rectangle((-7, -7), 14, 14, color=self._off_button_color,
                                      label='stop')

            ax.add_patch(stop)
            ax.set_xlim(-9, 9)
            ax.set_ylim(-9, 9)
            ax.set_aspect(1)

            patches = (stop,)

        self.static_artists['stop'] = tuple(patches)

        ax = self.axes['rescale']
        patches = find_artists_with_labels(ax.patches, {'up_arrow', 'down_arrow'}).values()

        if all(patch is None for patch in patches):
            up_arrow = mpatches.FancyArrow(0, 0, 0, 7, width=1.0, head_width=4, head_length=4,
                                           color=self._on_button_color, length_includes_head=True,
                                           label='up_arrow')
            down_arrow = mpatches.FancyArrow(0, 0, 0, -7, width=1.0, head_width=4, head_length=4,
                                             color=self._on_button_color,
                                             length_includes_head=True, label='down_arrow')
            ax.add_patch(up_arrow)
            ax.add_patch(down_arrow)

            ax.set_xlim(-10, 10)
            ax.set_ylim(-7, 7)
            ax.set_aspect(1)

            patches = (up_arrow, down_arrow)

        self.static_artists['rescale'] = tuple(patches)

    def _add_buttons(self):
        """Override and call to add additional buttons."""
        button_pause_resume = Button(self.axes['pause_resume'], '', useblit=self.useblit)
        button_stop = Button(self.axes['stop'], '', useblit=self.useblit)
        button_rescale = Button(self.axes['rescale'], '', useblit=self.useblit)
        self.buttons = {'pause_resume': button_pause_resume, 'stop': button_stop,
                        'rescale': button_rescale}

    def _add_events(self):
        """Override and call to add additional interactive events."""

        # Wrap methods that have buttons connected to fire on keys so that they
        # work with both and user code.
        def on_space(event: KeyEvent):
            if event.key == ' ':
                return self.toggle_pause_resume(event)

        def on_r(event: KeyEvent):
            if event.key.lower() == 'r':
                return self.rescale(event)

        cid_on_close = self.fig.canvas.mpl_connect('close_event', self._on_close)
        cid_on_space = self.fig.canvas.mpl_connect('key_press_event', on_space)  # type: ignore[arg-type]
        cid_on_r = self.fig.canvas.mpl_connect('key_press_event', on_r)  # type: ignore[arg-type]
        cid_button_pause_resume = self.buttons['pause_resume'].on_clicked(self.toggle_pause_resume)
        cid_button_stop = self.buttons['stop'].on_clicked(self.stop)
        cid_button_rescale = self.buttons['rescale'].on_clicked(self.rescale)
        self.cids = {'on_close': cid_on_close, 'on_space': cid_on_space, 'on_r': cid_on_r,
                     'pause_resume': cid_button_pause_resume, 'stop': cid_button_stop,
                     'rescale': cid_button_rescale}

    def _add_event_sources(self, default_event_source: TimerT | None = None):
        """Override and call to add additional event sources."""
        if default_event_source is None:
            default_event_source = self.fig.canvas.new_timer()

        default_event_source.interval = self.update_interval_ms
        self.event_sources = {'default': default_event_source}

        if self.autoscale and self.autoscale_interval_ms is not None:
            # If autoscale_interval_ms is None, rescaling is done in _update()
            autoscale_event_source = self.fig.canvas.new_timer(self.autoscale_interval_ms)
            autoscale_event_source.add_callback(self.rescale, None, self.autoscale)
            self.event_sources['autoscale'] = autoscale_event_source

    def _update(self, frame: Any = None) -> set[ArtistT]:
        """Called at each interval of the animation.

        Override and call to update animated artists with new data.

        *frame* is obtained from :meth:`_emit` and can either be data
        fetched from the data source or ``None`` if no new data has been
        put into the queue since the last animation interval.
        Implementations should handle this case accordingly.

        There is a flag :attr:`_first_frame` which can be used to run
        code only on the very first frame. To use this in a subclass,
        be sure to call this method only afterward as the flag is reset
        here.
        """
        if frame is None:
            return set(self.animated_artists.values())

        animated_artists = set()
        if self._first_frame:
            self._first_frame = False

            self.rescale()
            animated_artists.update(self.animated_artists.values())
        else:
            if self.show_fps:
                self.animated_artists['fps'].set_text(self._text.format(
                    1 / self._event_clock.avg_dt(),
                    1 / self._event_clock.last_dt(),
                ))
                animated_artists.add(self.animated_artists['fps'])

            if self.autoscale is not None and self.autoscale_interval_ms is None:
                self.rescale(axis=self.autoscale)
                animated_artists.update(self.animated_artists.values())

        return animated_artists

    def _emit(self) -> Iterator[Any | None]:
        """Queried every :attr:`update_interval_ms` ms to yield a new
        data item.

        Should not need to be overridden by subclasses.
        """
        self._LOG.debug('Emitting.')

        # In single-process mode, stop emitting conditioned on the stop flag. In multiprocess mode,
        # the emitting generator should never stop while the view is alive as we cannot restart the
        # animation. Hence, only stop once the figure close event is set.
        event = self.stop_event if self.is_in_main_process() else self._close_event

        while not event.is_set():
            try:
                yield self.data_queue.get(block=False)
            except queue.Empty:
                yield None
            else:
                self._frame_count += 1
                self._event_clock()
                self.data_queue.task_done()

        self._LOG.debug('Stopped emitting.')
        self.stop('emit')

    def _initialize(self) -> set[ArtistT]:
        """Run once before the animation is started.

        Resize events of the figure will also trigger this method to
        run if blitting is enabled.

        Override and call to initialize elements of the plot.
        """
        self._event_clock.clear()
        self._event_clock()
        self._first_frame = True
        self._frame_count = 0

        return set(self.animated_artists.values())

    def _on_close(self, event=None):
        """Executed when the figure is closed.

        Override and call to add custom cleanup tasks.
        """
        self._LOG.debug(f'on_close called on {event}.')

        if not self.is_in_main_process():
            # If we're running in a child process we need to set this flag to
            # stop the generator from emitting in _emit_multiprocessing().
            # Otherwise the process won't exit
            self._close_event.set()

        self.stop(event)

    def _start_event_sources(self):
        for event_source in (event_source for key, event_source in self.event_sources.items()
                             if key != 'default'):
            try:
                event_source.start()
            except AttributeError:
                # Not a TimerBase event source
                pass

    def _stop_event_sources(self):
        for event_source in (source for key, source in self.event_sources.items()
                             if key != 'default'):
            try:
                event_source.stop()
            except AttributeError:
                # Not a TimerBase event source
                pass

    def _set_pause_resume_state(self, state: Literal['resume', 'pause']):
        play, pause_1, pause_2 = self.static_artists['pause_resume']
        if state == 'resume':
            play.set_color(self._on_button_color)
            pause_1.set_color(self._off_button_color)
            pause_2.set_color(self._off_button_color)
        else:
            play.set_color(self._off_button_color)
            pause_1.set_color(self._on_button_color)
            pause_2.set_color(self._on_button_color)

        self.fig.canvas.draw_idle()

    def _set_stop_start_state(self, state: Literal['stop', 'start']):
        stop, = self.static_artists['stop']
        if state == 'stop':
            stop.set_color(self._on_button_color)
        else:
            stop.set_color(self._off_button_color)

        self.fig.canvas.draw_idle()

    @classmethod
    def in_process(cls, data_source: DataSource, *,
                   context_method: str | None = None, manager: SyncManager | None = None,
                   backend: str | None = 'qtagg', log_level: int = logging.WARNING,
                   **kwargs) -> LiveViewProxy:
        """Run a LiveView in a separate process.

        Parameters
        ----------
        data_source :
            The data source. It is run in a separate thread of the main
            process. See the class docstring for more information.
        context_method :
            The multiprocessing context method. See
            :func:`~multiprocessing.get_context`. On Linux, using 'fork'
            might make problems because it inherits the main process's
            matplotlib backend. Experimentally, using ``%matplotlib qt``
            together with 'fork' does not show the figure window.
        manager :
            A :class:`~multiprocessing.managers.SyncManager` instance to
            use for creating shared resources.
        backend :
            The matplotlib backend to use. Use None for the main process
            backend.
        log_level :
            Level for logging in the child process.
        **kwargs :
            Keyword arguments forwarded to the LiveView constructor.

        Returns
        -------
        process :
            The process running the view.

        """
        # TODO: Is serialization a performance bottleneck? If so, could share a
        #       list for array shapes / type code and use a SharedMemoryManager
        #       to share data buffers.

        def start_thread_on_event(event: mp.Event, thread: threading.Thread):
            """Starts the data thread upon receiving the go-ahead from
            the plot process."""
            _LOG.debug(f'Waiting for {event}')
            event.wait()
            _LOG.debug(f'Starting {thread}')
            thread.start()

        _setup_logging(log_level)

        tic = time.perf_counter()

        ctx = mp.get_context(context_method)
        if manager is None:
            # Use un-managed objects from multiprocessing context.
            manager = ctx
        if backend is None:
            backend = matplotlib.get_backend()

        data_source_kwargs, live_view_kwargs = functools.filter_kwargs(data_source, kwargs)

        stopped = manager.Value('b', True)
        running = manager.Value('b', False)
        # Set up the thread that puts data in a queue in the main process
        data_queue = manager.JoinableQueue(maxsize=int(kwargs.get('blocking_queue', True)))
        stop_event = manager.Event()
        close_event = manager.Event()
        data_thread = threading.Thread(target=_safe_data_source(data_source),
                                       args=(data_queue, stop_event),
                                       kwargs=data_source_kwargs,
                                       daemon=True)

        # Set up a waiter thread that will start the data thread on a signal
        # from a thread started in the child process.
        start_event = manager.Event()
        waiter_thread = threading.Thread(target=start_thread_on_event,
                                         args=(start_event, data_thread),
                                         daemon=True)

        _LOG.debug(f'Starting {waiter_thread}')
        waiter_thread.start()

        if live_view_kwargs.pop('fig', None) is not None:
            _LOG.warning('Dropping fig kwarg for view in separate process')
        if live_view_kwargs.pop('ax', None) is not None:
            _LOG.warning('Dropping ax kwarg for view in separate process')
        live_view_kwargs.update(event=start_event)

        # We temporarily overwrite the qcodes config to not start all the
        # logging etc to save import time (qcodes is only used for axis
        # formatting)
        with io.changed_directory(tmpdir := tempfile.mkdtemp()):
            if (qcodes := _import_qcodes()) is not None:

                rcfile = Path.cwd() / 'qcodesrc.json'
                rcfile.write_text(json.dumps(qcodes.config.defaults))
                schemafile = rcfile.with_stem('qcodesrc_schema')
                schemafile.write_text(json.dumps(qcodes.config.defaults_schema))

            process = ctx.Process(
                target=cls._run_in_process,
                name='LiveViewGUIProcess',
                args=(cls, data_queue, stop_event, backend, close_event, running, stopped,
                      log_level),
                kwargs=live_view_kwargs,
                daemon=True
            )

            _LOG.debug(f'Starting {process}')
            process.start()

        toc = time.perf_counter()
        _LOG.info(f'Took {toc - tic:.2g}s to launch process {process.pid}')

        proxy = cls.LiveViewProxy(process, data_thread, data_queue, stop_event, close_event,
                                  running, stopped)
        # when proxy is dereferenced we can delete the directory (hopefully) because the process
        # touching it is dead
        weakref.finalize(proxy, shutil.rmtree, tmpdir)
        return proxy

    @staticmethod
    def _run_in_process(cls: type[LiveViewT], data_queue: mp.JoinableQueue, stop_event: mp.Event,
                        backend: str, close_event: mp.Event, running: mp.Value, stopped: mp.Value,
                        log_level: int, **kwargs):
        """The plot process target.

        This starts a LiveView instance. Since the data is produced in the main
        process, we cannot pass the data production function to the constructor.
        Instead, we pass a function that emits a signal to the main process
        that the view is ready to receive data in *data_queue*.

        """

        def emit_start_signal(*_, event: mp.Event, **__):
            """Emits a signal to the main process to start the data thread."""
            _LOG.debug('Emitting start signal')
            event.set()

            # Sleep a bit to avoid the thread being joined before the main process
            # had time to enqueue data.
            _LOG.debug(f'Sleeping 100ms in {threading.current_thread()}')
            time.sleep(100e-3)

        _setup_logging(log_level)

        tic = time.perf_counter()
        _LOG.debug('Started process')

        # Need to select an interactive backend, obviously
        _LOG.info(f'Using backend {backend}')
        matplotlib.use(backend)

        view = cls(emit_start_signal, log_level=log_level, **kwargs)
        # Overwrite view's queue and event, which are assigned to the thread
        # that signals the data thread in the main process to start, with the
        # queue and event that are shared by the two processes
        view.data_queue = data_queue
        view.stop_event = stop_event
        view._close_event = close_event
        view._running = running
        view._stopped = stopped

        _LOG.debug(f'Starting {view}')
        view.start()

        toc = time.perf_counter()
        _LOG.info(f'Took {toc - tic:.2g}s to initialize and start.')

        _LOG.debug('Showing figure.')

        if is_using_mpl_gui_backend(view.fig):
            # Important to use block=True, otherwise the process terminates immediately
            plt.show(block=True)
        else:
            # Running in headless mode (likely in CI env). Manually spin the
            # event loop so that the process does not terminate ahead of time.
            _LOG.debug('Spinning event loop in headless mode')
            while not close_event.is_set():
                view.fig.canvas.start_event_loop(EVENT_LOOP_TIMEOUT)

            _LOG.debug('Received close event')

            # Manually run event source callbacks so that stop hook gets called
            with misc.timeout(10) as exceeded:
                while not exceeded:
                    _LOG.debug('Manually running callbacks in headless mode.')
                    try:
                        for fun, args, kwargs in view.animation.event_source.callbacks:
                            fun(*args, **kwargs)
                    except AttributeError:
                        # event_source has been removed
                        break

                if exceeded:
                    _LOG.debug('Event source still had the following callbacks registered: '
                               '\n'.join(view.animation.event_source.callbacks))

        # https://andreas.scherbaum.la/post/2022-03-03_hanging-script-at-the-end-of-python-multiprocessing/
        # python/cpython#90882
        flush_queue(view.data_queue)
        view.data_queue.join()
        view.data_queue = None

        running.value = False
        stopped.value = True
        _LOG.debug('Exited.')

    def is_running(self) -> bool | None:
        """Indicates if the view is currently running.

         - If True, the view is running and updating.
         - If False, the view is running and paused.
         - If None, the view is not running / stopped.

        """
        return None if self._stopped.value else bool(self._running.value)

    @staticmethod
    def is_in_main_process() -> bool:
        """We are running in the main process."""
        return mp.parent_process() is None

    def attach(self, data_source: DataSource, **data_source_kwargs):
        """Attach a data source to this view.

        The data source will be wrapped in a thread that puts data in a
        queue. Currently only a single data source can be attached at a
        time, so if a source is already attached, it will be stopped
        first.

        See :class:`LiveViewBase` for documentation of parameters.
        """
        if self.fig.number not in plt.get_fignums():
            raise RuntimeError('The figure has been closed. Please start a new view.')

        self._LOG.debug(f'Attaching new data source {data_source}')
        was_running = self.is_running()
        self.stop()
        self.stop_event.clear()
        self.data_thread = threading.Thread(target=_safe_data_source(data_source),
                                            args=(self.data_queue, self.stop_event),
                                            kwargs=data_source_kwargs,
                                            daemon=True)
        if was_running:
            self.start()

    def start(self):
        """Start the live view.

        Override this method to configure additional tasks to start.
        """
        if not hasattr(self, 'data_thread') or 'stopped' in repr(self.data_thread):
            # a bit hacky, but there's no public method to tell if a thread has run before.
            raise RuntimeError('No data source attached.')

        self._LOG.debug('Starting view.')
        self._LOG.debug(f'Starting {self.data_thread} from {self}.')

        # Make sure the thread is running.
        with misc.timeout(1, raise_exc='thread could not be started in {}s.') as exceeded:
            self.data_thread.start()
            while not self.data_thread.is_alive() and not exceeded:
                time.sleep(10e-3)

        self._LOG.debug(f'Waited {exceeded.elapsed:.3g}s for thread to start.')

        self.animation = FuncAnimation(
            self.fig, self._update, self._emit, self._initialize,
            interval=self.update_interval_ms,
            blit=self.useblit,
            cache_frame_data=False,
            repeat=False,
            event_source=self.event_sources['default']
        )
        self._start_event_sources()
        self._set_pause_resume_state('resume')
        self._set_stop_start_state('start')
        self._stopped.value = False
        self._running.value = True

    def resume(self, event=None):
        """Resume a paused live view."""
        if self.is_running() is None:
            return self.start()
        self._LOG.debug(f'Resuming view on event {event}.')
        self._set_pause_resume_state('resume')
        self._start_event_sources()
        self.animation.resume()
        self._running.value = True

    def pause(self, event=None):
        """Pause the live view."""
        self._LOG.debug(f'Pausing view on event {event}.')
        self.animation.pause()
        self._stop_event_sources()
        self._set_pause_resume_state('pause')
        self._running.value = False

    def stop(self, event=None):
        """Terminate the live view and interactive elements."""
        if self.is_running() is None:
            return

        self._LOG.debug(f'Stopping view on event {event}.')
        _stop_safely(self.stop_event, self.data_thread, self.data_queue)
        self._stopped.value = True

        if not self.is_in_main_process():
            self._LOG.debug('Returning from stop.')
            # Running in a separate process. Since we cannot restart the view
            # from there, we only stop data production so that LiveViewProxy.attach()
            # can be used to plot new data
            return

        # Set UI state
        self.pause(event)
        self._set_stop_start_state('stop')

        if event is None and self.animation.event_source is not None:
            # handled by Animation's figure close hook else, or animation already stopped
            self.animation._stop()  # noqa

    def toggle_pause_resume(self, event=None):
        """Pause/Resume the live view."""
        if self.is_running() is None:
            self.start()
        elif self.is_running():
            # Pauses 'default' event source
            self.pause()
        else:
            self.resume()

    @_queue_draw
    def rescale(self, event=None, axis: Literal['', 'x', 'y', 'xy'] = 'xy') -> bool:
        """Rescale the main axis.

        This is only actually performed if :attr:`xlim` or :attr:`ylim`
        are not overridden to return not None.

        If subclass implementations do not choose to call this method
        they should be decorated with :func:`_queue_draw` to ensure the
        figure updates.

        Parameters
        ----------
        event :
            Only required for matplotlib internals.
        axis :
            The axis to rescale. Can be any combination of 'x' and 'y'.

        Returns
        -------
        draw_required :
            Boolean indicating that a complete figure redraw is
            required. Handled by the :func:`_queue_draw` decorator.

        """
        # Only rescale where no static limits are defined by overriding the properties
        if 'x' in axis and self.xlim is not None:
            axis = axis.replace('x', '')
        if 'y' in axis and self.ylim is not None:
            axis = axis.replace('y', '')
        if axis == '':
            return False

        self.axes['main'].relim()
        self.axes['main'].autoscale_view(scalex='x' in axis, scaley='y' in axis)

        self._update_labels(axis)

        return True


class LiveView1DBase(LiveViewBase, abc.ABC):
    r"""Abstract base class for 1d live views.

    Subclasses implement :meth:`_update_ydata` to define how the 1d
    y-data is updated in each frame. y-data can be returned by the
    `data_source` in the following ways:

        - a 1d array of shape (x.size,), in which case a single line
          will be plotted.
        - a 2d array of shape (x.size, n_lines), in which case
          `n_lines` lines will be plotted.
        - a dictionary ``{label: 1d array}`` in which case a line will
          be drawn for each entry in the dictionary (as long as
          `n_lines` matches).

    Parameters
    ----------
    n_lines :
        The number of lines to plot. Should correspond to y-data's
        second dimension if an array or the size of the dictionary
        else.
    plot_legend :
        Plot a legend. If a string, passed through to
        :meth:`Axes.legend`\ s `loc` parameter. To have meaningful
        line labels, `data_source` should return a dictionary as its
        second return value whose keys will be taken as labels.

    For further parameters, see the base class.

    """
    _ydata: npt.NDArray[np.float64]
    """The data buffer populated at each frame by :meth:`_update_ydata."""

    def __init__(self, data_source: DataSource, *,
                 n_lines: int = 1, plot_legend: bool | str = False,
                 update_interval_ms: int = int(1e3 / 60), autoscale: str | None = None,
                 autoscale_interval_ms: int | None = 1000, show_fps: bool = False,
                 useblit: bool = True, blocking_queue: bool = True,
                 event_source: TimerT | None = None, xlabel: str = '', ylabel: str = '',
                 units: Mapping[Literal['x', 'y'], str] | None = None,
                 xlim: tuple[float, float] | None = None, ylim: tuple[float, float] | None = None,
                 xscale: str | ScaleT = 'linear', yscale: str | ScaleT = 'linear',
                 style: StyleT | Sequence[StyleT] = 'fast', fig: Figure | None = None,
                 ax: Axes | None = None, fig_kw: Mapping[str, Any] | None = None,
                 log_level: int | None = None, **data_source_kwargs):
        self.n_lines = n_lines
        self.plot_legend = plot_legend
        super().__init__(data_source, update_interval_ms=update_interval_ms, autoscale=autoscale,
                         autoscale_interval_ms=autoscale_interval_ms, show_fps=show_fps,
                         useblit=useblit, blocking_queue=blocking_queue, event_source=event_source,
                         xlabel=xlabel, ylabel=ylabel, units=units, xlim=xlim, ylim=ylim,
                         xscale=xscale, yscale=yscale, style=style, fig=fig, ax=ax, fig_kw=fig_kw,
                         log_level=log_level, **data_source_kwargs)

    @abc.abstractmethod
    def _update_ydata(self, frame):
        """Run before updating the line's ydata with :attr:`_ydata`.

        Subclasses should update that array or replace it with data
        from `frame` as needed.
        """
        pass

    @property
    def _line_handles(self) -> list[ArtistT]:
        return [artist for key, artist in self.animated_artists.items() if key.startswith('line')]

    def _add_animated_artists(self):
        super()._add_animated_artists()
        for i in range(self.n_lines):
            line, = self.axes['main'].plot([], [], animated=self.useblit)
            self.animated_artists[f'line_{i}'] = line

    def _add_static_artists(self):
        super()._add_static_artists()
        if self.plot_legend:
            loc = self.plot_legend if isinstance(self.plot_legend, str) else 'best'
            self.static_artists['legend'] = self.axes['main'].legend(
                handles=self._line_handles,
                labels=[''] * len(self._line_handles),
                loc=loc,
                framealpha=1
            )

    def _update(self, frame: tuple | None = None) -> set[ArtistT]:
        if frame is None:
            return set(self.animated_artists.values())

        x, y = frame

        if self._first_frame:
            self._ydata = np.full((len(x), self.n_lines), np.nan)
            if self.plot_legend and isinstance(y, Mapping):
                for txt, key in zip(self.static_artists['legend'].texts, y):
                    txt.set_text(key)

        # Update data before call to super's method so that artist extents are known for
        # rescaling e.g.
        self._update_ydata(frame)
        # Usually, x will not change, so we could use set_ydata(). But it doesn't
        # hurt to allow the possibility of x being dynamic.
        for i in range(self.n_lines):
            self.animated_artists[f'line_{i}'].set_data(x, self._ydata[:, i])

        animated_artists = super()._update(frame)
        animated_artists.update(self._line_handles)

        return animated_artists

    def _update_labels(self, axis):
        if _import_qcodes() is None:
            # reformat_axis() uses qcodes
            return

        if 'x' in axis and self._xlabel_text != '':
            prefix = reformat_axis(self.axes['main'],
                                   [line.get_xdata() for line in self._line_handles],
                                   self.units['x'], which='x', only_SI=True)
            self.static_artists['xlabel'].set_text(self._xlabel_text.format(prefix))
        if 'y' in axis and self._ylabel_text != '':
            prefix = reformat_axis(self.axes['main'],
                                   [line.get_ydata() for line in self._line_handles],
                                   self.units['y'], which='y', only_SI=True)
            self.static_artists['ylabel'].set_text(self._ylabel_text.format(prefix))


class BatchedLiveView1D(LiveView1DBase):
    """A live view for batched 1d data.

    `data_source` should produce a two-tuple of (x, y) data for this
    view, where x is a 1d array and y is

     - a 1d array of shape ``(x.size,)``
     - a 2d array of shape ``(x.size, n_lines)``
     - a dictionary ``{label: 1d array}``

    For parameters, see :class:`LiveView1DBase`.

    Examples
    --------
    Define a function that generates random data. The function will be
    pushed to a background thread so that the interpreter is unblocked.

    >>> def produce_data(interval=1e-1):
    ...     import time  # imports for tests in child process
    ...     import numpy as np
    ...     rng = np.random.default_rng()
    ...     t0 = t1 = time.perf_counter()
    ...     while True:
    ...         dt = time.perf_counter() - t1
    ...         if interval > dt:
    ...             time.sleep(interval - dt)
    ...         t1 = time.perf_counter()
    ...         x = 1 + (t1 - t0) * 100
    ...         yield np.arange(1024), x * rng.standard_normal(1024)

    Wrap produce_data() so that it puts its generated values into a
    queue until an event is set:

    >>> put_data = iterable_data_source_factory(produce_data)

    Instantiate the live view object:

    >>> view = BatchedLiveView1D(put_data, autoscale='y', interval=1e-3,
    ...                          show_fps=True)
    >>> view.start()

    Pause the update (and the data production). This can also be done
    by clicking the play/pause button in the lower left corner:

    >>> view.is_running()
    True
    >>> view.pause()
    >>> view.is_running()
    False

    ... and resume again:

    >>> view.resume()
    >>> view.is_running()
    True

    Rescaling of the data limits can also be triggered manually
    (independent of the `autoscale` setting) by clicking on the up-down
    arrow symbol in the lower left corner or programmatically:

    >>> view.rescale(axis='xy')

    Terminate the data production thread and disable interactive
    elements of the figure:

    >>> view.stop()

    Once a view is stopped, new data sources can be attached to it and
    the live view started again:

    >>> view.attach(put_data, interval=1e-3)
    >>> view.start()

    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()

    If the data update rate is slow, blitting together with automatic
    rescaling might lead to a white canvas being visible between a
    rescale being triggered and new data being drawn. In this case you
    can disable blitting, but note that this will be less performant:

    >>> view = BatchedLiveView1D(put_data, autoscale='y', useblit=False,
    ...                          interval=0.1, show_fps=True)
    >>> view.start()

    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()

    The view can also be run in a separate process. This classmethod
    returns a :class:`LiveViewProxy` object which contains the
    :class:`~multiprocessing.Process` object as well as the
    :class:~multiprocessing.Queue` and :class:`~multiprocessing.Event`
    used for communication (agg backend for doctest):

    >>> import os, time
    >>> # agg backend for headless mode on CI, feel free to change
    >>> backend = 'agg' if 'GITLAB_CI' in os.environ else None
    >>> proxy = BatchedLiveView1D.in_process(put_data, backend=backend,
    ...                                      context_method='spawn')
    >>> proxy.block_until_ready()
    >>> proxy.is_running()
    True

    The data streaming can be stopped without killing the live view:

    >>> proxy.stop()
    >>> print(proxy.is_running())
    None

    Afterwards, a new data source can be attached:

    >>> proxy.attach(put_data)
    >>> proxy.is_running()
    True

    Stop the data production thread and terminate the process:

    >>> proxy.stop()
    >>> print(proxy.is_running())
    None
    >>> proxy.process.terminate()

    Multiple lines are also supported. Define a data source that
    returns a dictionary for y-values:

    >>> def produce_data(interval=1e-1):
    ...     import time  # imports for tests in child process
    ...     import numpy as np
    ...     rng = np.random.default_rng()
    ...     t0 = t1 = time.perf_counter()
    ...     while True:
    ...         dt = time.perf_counter() - t1
    ...         if interval > dt:
    ...             time.sleep(interval - dt)
    ...         t1 = time.perf_counter()
    ...         x = 1 + (t1 - t0) * 100
    ...         y = {'foo': +x * rng.standard_normal(1024),
    ...              'bar': -x * rng.standard_normal(1024)}
    ...         yield np.arange(1024), y
    >>> put_data = iterable_data_source_factory(produce_data)
    >>> view = BatchedLiveView1D(put_data, n_lines=2, plot_legend=True,
    ...                          autoscale='y', interval=1e-3)
    >>> view.start()

    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()

    """

    def _update_ydata(self, frame):
        x, y = frame
        # At first, we assume that the provided data buffer should be used. If
        # that fails because y has the wrong size, we replace the data buffer
        # with it.
        if isinstance(y, Mapping):
            try:
                for i, data in enumerate(y.values()):
                    self._ydata[:, i] = data
            except ValueError:
                self._ydata = np.array([val for val in y.values()]).T
        else:
            y = np.array(y)[:, None] if np.ndim(y) == 1 else y
            try:
                self._ydata[:] = y
            except ValueError:
                self._ydata = y


class IncrementalLiveView1D(LiveView1DBase):
    """A live view for 1d data arriving in single samples.

    `data_source` should produce a two-tuple of (x, y) data for this
    view, where x is a 1d array and y is

     - a number
     - a sequence of length `n_lines`
     - a dictionary ``{label: number}``.

    For parameters, see :class:`LiveView1DBase`.

    Examples
    --------
    >>> rng = np.random.default_rng()
    >>> def produce_data(interval=1e-3):
    ...     t0 = t1 = time.perf_counter()
    ...     while True:
    ...         dt = time.perf_counter() - t1
    ...         if interval > dt:
    ...             time.sleep(interval - dt)
    ...         t1 = time.perf_counter()
    ...         x = 1 + (t1 - t0) * 100
    ...         yield np.arange(128), x * rng.standard_normal()

    >>> put_data = iterable_data_source_factory(produce_data)
    >>> view = IncrementalLiveView1D(put_data, autoscale='y', xlim=(0, 127),
    ...                              autoscale_interval_ms=None)
    >>> view.start()

    Terminate the data production thread and disable interactive
    elements of the figure:

    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()

    Multiple lines are also supported. Define a data source that
    returns a sequence of y-values:

    >>> def produce_data(interval=1e-3):
    ...     t0 = t1 = time.perf_counter()
    ...     while True:
    ...         dt = time.perf_counter() - t1
    ...         if interval > dt:
    ...             time.sleep(interval - dt)
    ...         t1 = time.perf_counter()
    ...         x = 1 + (t1 - t0) * 100
    ...         yield np.arange(1024), x * rng.standard_normal(2)
    >>> put_data = iterable_data_source_factory(produce_data)
    >>> view = IncrementalLiveView1D(put_data, n_lines=2, autoscale='xy',
    ...                              autoscale_interval_ms=None)
    >>> view.start()

    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()
    """

    def _update_ydata(self, frame):
        x, y = frame

        if not (ix := self._frame_count % len(x)):
            # Start of new 1d trace, reset buffer to nans
            self._ydata[1:] = np.nan

        if isinstance(y, Mapping):
            for i, data in enumerate(y.values()):
                self._ydata[ix, i] = data
        else:
            self._ydata[ix] = y


class LiveView2DBase(LiveViewBase, abc.ABC):
    """Abstract base class for 2d live views.

    Subclasses implement :meth:`_update_cdata` to define how the 2d
    data is updated in each frame.

    Parameters
    ----------
    autoscale :
        Automatically rescale axes.

         - 'c': rescale the extents and colorbar of the colorplot as
           well as the y-axis of the line plot, if any.

    plot_line :
        Show a line plot with the average along the y-axis.
    clabel :
        The label of the colorbar.
    img_kw :
        Keyword-arguments passed on to
        :meth:`matplotlib:matplotlib.axes.Axes.pcolorfast`. Use this to
        specify a norm, for instance.

    For additional parameters, see :class:`LiveViewBase`.

    """
    _cdata: npt.NDArray[np.float64]
    """The data buffer populated at each frame by :meth:`_update_cdata."""
    cbar: colorbar.Colorbar
    units: dict[Literal['x', 'y', 'c'], str]

    def __init__(self, data_source: DataSource, update_interval_ms: int = int(1e3 / 60),
                 autoscale: Literal['', 'y', 'c', 'yc'] | None = None,
                 autoscale_interval_ms: int | None = 1000, plot_line: bool = False,
                 show_fps: bool = False, useblit: bool = True, blocking_queue: bool = True,
                 event_source: TimerT | None = None, xlabel: str = '', ylabel: str = '',
                 clabel: str = '', units: dict[Literal['x', 'y', 'c'], str] | None = None,
                 xlim: tuple[float, float] | None = None, ylim: tuple[float, float] | None = None,
                 xscale: str | ScaleT = 'linear', yscale: str | ScaleT = 'linear',
                 fig: Figure | None = None, ax: Axes | None = None,
                 img_kw: Mapping[str, Any] | None = None, fig_kw: Mapping[str, Any] | None = None,
                 log_level: int | None = None, **data_source_kwargs):

        # need to define these before calling super()'s init because that calls
        # methods overridden by this class which might need these attributes.
        self.plot_line = plot_line
        self.img_kw = img_kw if img_kw is not None else {}
        animated = self.img_kw.pop('animated', sentinel := object())
        self._clabel_text = clabel
        self._linelabel_text = self.line_operation.label
        units = dict.fromkeys(['x', 'y', 'c'], '') if units is None else units
        if units.setdefault('c', ''):
            self._clabel_text = self._clabel_text + ' ({{{}}}{})'.format('', units['c'])
            self._linelabel_text = self._linelabel_text + ' ({{{}}}{})'.format('', units['c'])

        super().__init__(data_source, update_interval_ms=update_interval_ms, autoscale=autoscale,
                         autoscale_interval_ms=autoscale_interval_ms, show_fps=show_fps,
                         useblit=useblit, blocking_queue=blocking_queue, event_source=event_source,
                         xlabel=xlabel, ylabel=ylabel, units=units, xlim=xlim, ylim=ylim,
                         xscale=xscale, yscale=yscale, fig=fig, ax=ax, fig_kw=fig_kw,
                         log_level=log_level, **data_source_kwargs)

        # Log is instantiated in base constructor
        if animated is not sentinel:
            self._LOG.warning('img_kw `animated` ignored in favor of useblit.')

    @abc.abstractmethod
    def _update_cdata(self, frame):
        """Run before updating the image with :attr:`_cdata`.

        Subclasses should update that array with data from `frame` or
        overwrite it as needed.
        """
        pass

    @property
    @abc.abstractmethod
    def line_operation(self) -> LineOperation:
        """The operation applied to the 2d data to obtain 1d data."""
        pass

    def _add_axes(self, ax=None):
        super()._add_axes(ax)

        # Make room for colorbar
        if self.plot_line:
            gs = _make_subgridspec(self.axes['main'], height_ratios=[3, 1])

            self.axes['cbar'] = self.fig.add_subplot(gs[0, 1], label='<colorbar>')
            self.axes['cbar'].set_anchor((0.0, 0.5))
            self.axes['cbar'].set_box_aspect(20)
            self.axes['cbar'].set_aspect('auto')

            self.axes['line'] = self.fig.add_subplot(gs[1, 0], sharex=self.axes['main'],
                                                     label='line')
            self.axes['line'].yaxis.set_tick_params(which='both', left=True, right=True,
                                                    labelright=True, labelleft=False)
            self.axes['line'].yaxis.set_label_position('right')
            self.axes['line'].set_yscale(norm_to_scale(self.img_kw.get('norm')))
            self.axes['main'].label_outer()
            # Indicate that the line plot is the lowest axes to be used for labeling
            self._xlabel_axes = self.axes['line']
        else:
            self.axes['cbar'], _ = colorbar.make_axes_gridspec(self.axes['main'])

    def _add_animated_artists(self):
        super()._add_animated_artists()

        img = self.axes['main'].pcolorfast(np.full((1, 1), np.nan), animated=self.useblit,
                                           **self.img_kw)
        self.animated_artists['img'] = img

        if self.plot_line:
            line, = self.axes['line'].plot([], [], animated=self.useblit)
            self.animated_artists['line'] = line

    def _add_static_artists(self):
        super()._add_static_artists()

        self.cbar = self.fig.colorbar(self.animated_artists['img'], cax=self.axes['cbar'])
        self.cbar.set_label(self._clabel_text.format(''))

        # The correct Text object is a bit hidden
        self.static_artists['clabel'] = self.cbar.ax.yaxis.label

        if self.plot_line:
            linelabel = self.axes['line'].set_ylabel(self._linelabel_text.format(''))
            self.static_artists['linelabel'] = linelabel

    def _update(self, frame: Any | None = None) -> set[ArtistT]:
        if frame is None:
            return set(self.animated_artists.values())

        x, y, c = frame

        # Do this before call to super()'s because that resets the _first_frame flag
        if self._first_frame:
            self._cdata = np.full((len(y), len(x)), np.nan)

        xext, yext = itertools.split_into(self.animated_artists['img'].get_extent(), (2, 2))
        xlim, ylim = [x[0], x[-1]], [y[0], y[-1]]
        if self._first_frame or self.autoscale and (xext != xlim or yext != ylim):
            # set_extent() deviates in behavior from set_data() in that it automatically
            # relims. Hence, we need to deviate from the design and enqueue the draw here
            # instead of letting rescale() handle it.
            self.animated_artists['img'].set_extent(xlim + ylim)
            self._update_labels('xy')
            self.animation.draw_enqueued.set()

        # Update data before call to super's method so that artist extents are known for
        # rescaling e.g.
        self._update_cdata(frame)
        self.animated_artists['img'].set_data(self._cdata)
        if self.plot_line:
            self.animated_artists['line'].set_data(x, self.line_operation(self._cdata))

        animated_artists = super()._update(frame)
        animated_artists.add(self.animated_artists['img'])
        if self.plot_line:
            animated_artists.add(self.animated_artists['line'])

        return animated_artists

    def _update_labels(self, axis):
        if _import_qcodes() is None:
            # reformat_axis() uses qcodes
            return

        if 'x' in axis:
            # TODO: this is awkward. 'x' means x and y labels of the main plot
            if self._xlabel_text != '':
                prefix = reformat_axis(self.axes['main'],
                                       self.animated_artists['img'].get_extent()[:2],
                                       self.units['x'], which='x', only_SI=True)
                self.static_artists['xlabel'].set_text(self._xlabel_text.format(prefix))
            if self._ylabel_text != '':
                prefix = reformat_axis(self.axes['main'],
                                       self.animated_artists['img'].get_extent()[2:],
                                       self.units['y'], which='y', only_SI=True)
                self.static_artists['ylabel'].set_text(self._ylabel_text.format(prefix))
        if 'c' in axis and self._clabel_text != '':
            # colorbar
            prefix = reformat_axis(self.cbar,
                                   self.animated_artists['img'].get_array(),
                                   self.units['c'], which='c', only_SI=True)
            self.static_artists['clabel'].set_text(self._clabel_text.format(prefix))
        if 'y' in axis and self.plot_line and self._linelabel_text != '':
            # 'y' means the line plot
            prefix = reformat_axis(self.axes['line'], self.animated_artists['line'].get_ydata(),
                                   self.units['c'], which='y', only_SI=True)
            self.static_artists['linelabel'].set_text(self._linelabel_text.format(prefix))

    @_queue_draw
    def rescale(self, event=None, axis: Literal['', 'y', 'c', 'yc'] = 'yc') -> bool:
        if self._first_frame:
            # If _first_frame is still set, no data update took place so there's nothing to be done
            return False

        draw_required = False

        vmin = self.img_kw.get('vmin', False)
        vmax = self.img_kw.get('vmax', False)
        if 'c' in axis:
            if vmin is False or vmax is False:
                # At least one limit dynamic, update
                with self.animated_artists['img'].norm.callbacks.blocked():
                    # Do not use img.autoscale because vmin/max might be given which it ignores
                    if vmin is False:
                        self.animated_artists['img'].norm.vmin = None
                    if vmax is False:
                        self.animated_artists['img'].norm.vmax = None

                self.animated_artists['img'].autoscale_None()

            if self.plot_line:
                # 'x' case is controlled by _update()
                self.axes['line'].relim()
                self.axes['line'].autoscale_view(scalex=False, scaley=True)

            draw_required = True

        self._update_labels(axis)

        return draw_required


class BatchedLiveView2D(LiveView2DBase):
    """A live view for 2d batched data.

    `data_source` should produce a three-tuple of (x, y, c) data for
    this view, where x and y are 1 or 2d arrays and c is a 2d array
    of shape (y_pts, x_pts).

    This class does *not* update x and y extents of the image.

    For parameters, see :class:`LiveView2DBase`.

    Examples
    --------
    >>> rng = np.random.default_rng()
    >>> def produce_data(interval=1e-1):
    ...     t0 = t1 = time.perf_counter()
    ...     x, y = np.linspace(3.2, 5.7, 1920), np.linspace(0, 1, 1080)
    ...     while True:
    ...         dt = time.perf_counter() - t1
    ...         if interval > dt:
    ...             time.sleep(interval - dt)
    ...         t1 = time.perf_counter()
    ...         c = 1 + (t1 - t0) * 100
    ...         yield x, y, c * rng.standard_normal((1080, 1920))

    >>> put_data = iterable_data_source_factory(produce_data)
    >>> view = BatchedLiveView2D(put_data, autoscale='c', interval=1e-3)
    >>> view.start()

    Stop the event loop:

    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()

    Plot the mean of 1d traces along the y axis as a line plot:

    >>> view = BatchedLiveView2D(put_data, autoscale='yc', interval=1e-3,
    ...                          plot_line=True)
    >>> view.start()

    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()

    """

    @functools.cached_property
    def line_operation(self) -> LineOperation:
        def op(data: npt.ArrayLike) -> npt.NDArray:
            return np.nanmean(data, axis=0)

        op.label = 'Mean'
        return op

    def _update_cdata(self, frame):
        x, y, c = frame
        # At first, we assume that the provided data buffer should be used. If
        # that fails because c has the wrong size, we replace the data buffer
        # with it.
        try:
            self._cdata[:] = c
        except ValueError:
            self._cdata = c


class IncrementalLiveView2D(LiveView2DBase):
    """A live view for 2d data arriving in 1d batches.

    The x-axis is assumed to be the fast axis, meaning the 2d image is
    filled in row-by-row using incoming 1d data batches.

    `data_source` should produce a three-tuple of (x, y, c) data for
    this view, where `c` is 1d with ``len(c) == len(x)``.

    For parameters, see :class:`LiveView2DBase`.

    Examples
    --------
    >>> rng = np.random.default_rng()
    >>> def produce_data(interval=1e-3):
    ...     t0 = t1 = time.perf_counter()
    ...     x, y = np.linspace(3.2, 5.7, 200), np.linspace(0, 1, 20)
    ...     while True:
    ...         dt = time.perf_counter() - t1
    ...         if interval > dt:
    ...             time.sleep(interval - dt)
    ...         t1 = time.perf_counter()
    ...         c = 1 + (t1 - t0) * 100
    ...         yield x, y, c * rng.standard_normal(200)

    >>> put_data = iterable_data_source_factory(produce_data)
    >>> view = IncrementalLiveView2D(put_data, autoscale='c')
    >>> view.start()

    Stop the event loop:

    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()

    Plot the last acquired 1d trace as well:

    >>> view = IncrementalLiveView2D(put_data, autoscale='yc', plot_line=True,
    ...                              clabel='my label')
    >>> view.start()

    >>> plt.pause(1e-3)  # for doctest
    >>> view.stop()

    """

    @functools.cached_property
    def line_operation(self) -> LineOperation:
        def op(data: npt.ArrayLike) -> npt.NDArray:
            return data[self._frame_count % self._cdata.shape[0]]

        op.label = self._clabel_text
        return op

    def _update_cdata(self, frame):
        x, y, c = frame

        if not (ix := self._frame_count % len(y)):
            # Start of new 2d image, reset buffer to nans
            self._cdata[1:] = np.nan

        self._cdata[ix] = c


def _make_subgridspec(ax: Axes, height_ratios: Sequence[float], pad: float = 0.05,
                      fraction: float = 0.15, hspace: float = 0.1) -> GridSpecFromSubplotSpec:
    # Copied from matplotlib.colorbar.make_axes_gridspec()
    wh_space = 2 * pad / (1 - pad)

    gs = ax.get_subplotspec().subgridspec(
        nrows=len(height_ratios), ncols=2, wspace=wh_space, hspace=hspace,
        height_ratios=height_ratios, width_ratios=[1 - fraction - pad, fraction]
    )
    ax.set_subplotspec(gs[0, 0])
    return gs


def iterable_data_source_factory(
        iterable_function: Callable[P.kwargs, Iterable[T]]
) -> DataSource[P, T]:
    """Return a function that puts data from the iterable returned by
    `iterable_function` into a queue until a stop flag is set."""

    def data_source(data_queue: queue.Queue[T], stop_event: threading.Event, **kwargs: P.kwargs):
        it = iter(iterable_function(**kwargs))
        while not stop_event.is_set():
            data_queue.put(next(it))

    # Update the signature so that it can be inspected.
    iterable_signature = inspect.signature(iterable_function)
    original_signature = inspect.signature(data_source)
    data_source = functools.wraps(iterable_function)(data_source)

    data_source.__signature__ = inspect.signature(data_source).replace(
        parameters=[original_signature.parameters['data_queue'],
                    original_signature.parameters['stop_event'],
                    *iterable_signature.parameters.values()]
    )

    return data_source


def find_artist_with_label(artists: Iterable[ArtistT], label: str) -> Artist | None:
    """Find the artist, if any, whose label is `label`.

    Returns None otherwise.
    """
    return itertools.first_true(artists, pred=lambda artist: artist.get_label() == label)


def find_artists_with_labels(artists: Iterable[ArtistT],
                             labels: Iterable[str]) -> dict[str, ArtistT | None]:
    """Find the artists, if any, whose labels are in `labels`.

    Returns a dictionary with keys `labels` and the artist if found and
    None otherwise as values.
    """
    matches = dict.fromkeys(labels)
    for artist in artists:
        if (label := artist.get_label()) in labels:
            matches[label] = artist

    return matches


def _safe_data_source(data_source: DataSource[P, T]) -> DataSource[P, T]:
    """Wraps a data source to set the stop flag on errors."""

    @functools.wraps(data_source)
    def wrapped(data_queue: mp.JoinableQueue[T] | queue.Queue[T],
                stop_event: mp.Event | threading.Event,
                **kwargs: P.kwargs):
        try:
            data_source(data_queue, stop_event, **kwargs)
        except Exception as exc:
            _LOG.exception(
                f'Caught an exception in data source {data_source}. Quitting gracefully.',
                exc_info=exc
            )
            stop_event.set()
        else:
            _LOG.debug(f'Data source thread {threading.current_thread().name} exited gracefully.')

    return wrapped


def flush_queue(q: queue.Queue | mp.JoinableQueue):
    """Flush the queue *q* until it is empty."""
    while True:
        try:
            q.get(block=False)
        except (queue.Empty, OSError):
            # queue is empty / closed
            return
        else:
            q.task_done()


def _stop_safely(stop_event: threading.Event | mp.Event, thread: threading.Thread,
                 q: queue.Queue | mp.JoinableQueue, timeout: float = 1.0) -> None:

    def attempt_join() -> bool:
        # Need to flush the queue in case the thread that puts data is waiting for
        # the queue to be free, preventing it from joining once it encounters the
        # stop flag
        flush_queue(q)
        try:
            thread.join(timeout=timeout)
        except RuntimeError:
            # Thread not started
            pass
        return not thread.is_alive()

    stop_event.set()

    attempt = 1
    while attempt <= 10:
        attempt += 1
        if attempt_join():
            break
    else:
        raise RuntimeError(f'Thread could not be stopped within {timeout}s in {attempt} attempts.')

    # For some reason the thread might push data one last time, so flush again after a short wait
    time.sleep(50e-3)
    flush_queue(q)


def _import_qcodes() -> ModuleType | None:
    if (module := sys.modules.get('qcodes')) is not None:
        return module
    try:
        return importlib.import_module('qcodes')
    except ImportError:
        return None


class _ProcessNameFilter(logging.Filter):
    def filter(self, record):
        record.processname = mp.current_process().name
        return True


def _setup_logging(level: int | None):
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(processname)s - %(message)s'
    )

    root_logger = logging.getLogger('qutil')
    root_logger.setLevel(logging.WARNING)
    root_logger.propagate = False

    logger = logging.getLogger(__name__)
    logger.addFilter(_ProcessNameFilter())
    if level is not None:
        logger.setLevel(level)

    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if level is not None:
        handler.setLevel(level)

    logger.addHandler(handler)


LiveViewT = TypeVar('LiveViewT', bound=LiveViewBase)
