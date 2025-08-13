"""This module contains signal processing functions that work on data in
real space.

For consistency, functions in this module should have the data to be
processed as their first argument while the processed data should be the
sole return argument, i.e.::

    def fun(data, *args, **kwargs) -> processed_data:
        ...

Examples
--------
Compare RC high- and low-pass filters with Butterworth filters:

>>> import numpy as np
>>> import matplotlib.pyplot as plt
>>> fs = 1e3; N = 1000; order = 3
>>> t = np.linspace(0, N/fs, N, endpoint=False)
>>> x_fast = .5*np.sin(2*np.pi*t*65)
>>> x_mid = .5*np.sin(2*np.pi*t*35)
>>> x_slow = .5*np.sin(2*np.pi*t*5)
>>> x = x_slow + x_mid + x_fast

Plot the results:

>>> fig, ax = plt.subplots(4, 2, sharex=True, sharey=True, layout='constrained')
>>> for j, filt in enumerate([RC_filter, butter_filter]):  # doctest: +SKIP
...     _ = ax[0, j].plot(t, x_slow + x_mid)
...     _ = ax[0, j].plot(t, filt(x, fs=fs, order=order, f_max=50))
...     _ = ax[1, j].plot(t, x_mid + x_fast)
...     _ = ax[1, j].plot(t, filt(x, fs=fs, order=order, f_min=20))
...     _ = ax[2, j].plot(t, x_mid)
...     _ = ax[2, j].plot(t, filt(x, fs=fs, order=order, f_min=20, f_max=50))
...     _ = ax[3, j].plot(t, x_slow + x_fast)
...     try:
...         _ = ax[3, j].plot(t, filt(x, fs=fs, order=order, f_min=50, f_max=20))
...     except NotImplementedError:
...         pass
>>> _ = fig.supxlabel('$f$ (Hz)')
>>> _ = ax[0, 0].set_title('RC filters')
>>> _ = ax[0, 1].set_title('Butterworth filters')
>>> _ = ax[0, 0].set_ylabel('Highpass')
>>> _ = ax[1, 0].set_ylabel('Lowpass')
>>> _ = ax[2, 0].set_ylabel('Bandpass')
>>> _ = ax[3, 0].set_ylabel('Bandstop')

Compare the frequency response:

>>> from qutil.signal_processing import fourier_space, real_space
>>> from qutil.functools import partial

Sample the frequency response by computing the filtered FFT:

>>> def sample_tf(filt, f, t):
...     x = np.sin(2 * np.pi * f[:, None] * t)
...     filtered = filt(x)
...     tf = np.fft.rfft(filtered)
...     # fft of unfiltered signal has value fs/2
...     return np.diag(tf) / (.5 * fs)

Run the simulation:

>>> x = np.ones(N)
>>> f = np.fft.rfftfreq(N, 1/fs)
>>> fig, ax = plt.subplots(4, 2, sharex=True, sharey=True, layout='constrained')
>>> for j, typ in enumerate(['RC', 'butter']):
...     tf = getattr(fourier_space, f'{typ}_transfer_function')
...     filt = partial(getattr(real_space, f'{typ}_filter'), order=order, fs=fs)
...     _ = ax[0, j].plot(f, abs(tf(f, order=order, f_max=50)))
...     _ = ax[0, j].plot(f, abs(sample_tf(partial(filt, f_max=50), f, t)))
...     _ = ax[1, j].plot(f, abs(tf(f, order=order, f_min=10)))
...     _ = ax[1, j].plot(f, abs(sample_tf(partial(filt, f_min=10), f, t)))
...     _ = ax[2, j].plot(f, abs(tf(f, order=order, f_min=10, f_max=50)))
...     _ = ax[2, j].plot(f, abs(sample_tf(partial(filt, f_min=10, f_max=50), f, t)))
...     _ = ax[3, j].plot(f, abs(tf(f, order=order, f_min=50, f_max=10)))
...     try:
...         _ = ax[3, j].plot(f, abs(sample_tf(partial(filt, f_min=50, f_max=10), f, t)))
...     except NotImplementedError:
...         pass
>>> _ = fig.supxlabel('$f$ (Hz)')
>>> _ = ax[0, 0].set_title('RC filters')
>>> _ = ax[0, 1].set_title('Butterworth filters')
>>> _ = ax[0, 0].set_ylabel('Highpass')
>>> _ = ax[1, 0].set_ylabel('Lowpass')
>>> _ = ax[2, 0].set_ylabel('Bandpass')
>>> _ = ax[3, 0].set_ylabel('Bandstop')
>>> _ = ax[0, 0].set_ylim(-0.1, 1.1)
>>> _ = ax[0, 0].set_xscale('log')

"""
import inspect
import warnings
from collections.abc import Sequence
from typing import Callable, Literal, Optional, Tuple, TypeVar, Union

import numpy as np
from scipy import fft, signal

from qutil import math
from qutil.functools import chain, partial, wraps
from qutil.signal_processing import fourier_space
from qutil.signal_processing._common import _parse_filter_edges

# TODO: replace unsupported imports
try:
    from scipy.signal.spectral import _median_bias, _triage_segments
except ImportError:
    from scipy.signal._spectral_py import _median_bias, _triage_segments

try:
    import numba
except ImportError:
    numba = None

_T = TypeVar('_T')


def _standardize(function):
    """Adds variadic kwargs."""
    try:
        parameters = inspect.signature(function).parameters
    except ValueError:
        # ufunc, https://numpy.org/doc/stable/reference/ufuncs.html#ufuncs-kwargs
        parameters = {'out', 'where', 'axes', 'axis', 'keepdims', 'casting', 'order', 'dtype',
                      'subok', 'signature', 'extobj'}

    @wraps(function)
    def wrapper(x, *args, **kwargs):
        # Filter kwargs that function actually accepts
        kwargs = {k: v for k, v in kwargs.items() if k in parameters}
        return function(x, *args, **kwargs)

    return wrapper


def Id(x: _T, *_, **__) -> _T:
    """The identity mapping."""
    return x


def rms(x, /, out=None, *, axis: Optional[int] = None, where=True, dtype=None, keepdims=False,
        **_) -> np.ndarray:
    """Compute the RMS (root-mean-square).

    See :class:`numpy.ufunc` and the `NumPy reference`_ for
    documentation of the arguments.

    .. _NumPy reference: https://numpy.org/doc/stable/reference/ufuncs.html/

    Examples
    --------
    >>> t = np.linspace(0, 2*np.pi, 1001)
    >>> x = 2*np.sqrt(2)*np.sin(t)
    >>> r = rms(x)
    >>> print(r)  # doctest: +ELLIPSIS
    1.9990007493755...
    >>> np.allclose(r, np.sqrt(x.mean()**2 + x.var()))
    True
    """
    x = np.asanyarray(x)
    N = np.take(x.shape, axis or range(x.ndim)).prod()

    result = math.abs2(x, where=where, dtype=dtype)
    result = np.sum(result, axis=axis, dtype=dtype, out=out, keepdims=keepdims, where=where)
    result = np.sqrt(result, out=out, dtype=dtype)
    result /= np.sqrt(N)
    return result


if numba is not None:
    # nb.guvectorize generates gufuncs with all the kwargs, so only work and result array required.
    def _rms(x, res):
        res[0] = 0
        if np.iscomplexobj(x):
            for i in range(x.shape[0]):
                xx = x[i]
                real = xx.real
                imag = xx.imag
                res += real * real + imag * imag
        else:
            for i in range(x.shape[0]):
                real = x[i].real
                res += real * real
        res[0] = np.sqrt(res[0] / x.shape[0])

    _rms.__doc__ = rms.__doc__
    # Expose both the generated ufunc and the wrapped version that complies with the signature
    # convention.
    rms_ufunc = numba.guvectorize([(numba.float32[:], numba.float32[:]),
                                   (numba.float64[:], numba.float64[:]),
                                   (numba.complex64[:], numba.float32[:]),
                                   (numba.complex128[:], numba.float64[:])],
                                  '(n)->()',
                                  target='parallel',
                                  cache=True)(_rms)
    try:
        rms = _standardize(rms_ufunc)
    except AssertionError:
        # Could not parse rms_ufunc signature, leave rms alone
        pass


def _sosfilt(sos, x, method: Literal['forward', 'forward-backward'] = 'forward'):
    if method == 'forward':
        zi = signal.sosfilt_zi(sos)
        # Broadcast zi in case x is multi-dimensional
        zi = np.expand_dims(zi, list(range(1, x.ndim)))
        zi = np.broadcast_to(zi, zi.shape[:1] + x.shape[:-1] + zi.shape[-1:])
        return signal.sosfilt(sos, x, axis=-1, zi=zi)[0]
    else:
        return signal.sosfiltfilt(sos, x, axis=-1)


def RC_filter(x, f_min: float = 0, f_max: float = np.inf, fs: float = 2, order: int = 1,
              method: Literal['forward', 'forward-backward'] = 'forward', **_) -> np.ndarray:
    r"""RC-type filter.

    Parameters
    ----------
    x : array_like
        The data to be filtered.
    f_min, f_max : float
        The edges for (low-, band-, high-)pass filtering.
    fs : float, optional
        Sample frequency. If not given, taken to be 2 so that the
        bandwidth ``[f_min, f_max]`` is normalized to the interval
        ``[0, 1]``.
    order : int
        The filter order. Default: 1.
    method :
        Use :func:`~scipy:scipy.signal.sosfilt` (forward) or
        :func:`~scipy:scipy.signal.sosfiltfilt` (forward-backward) to
        filter. Note that the latter impacts the transfer function.

    Notes
    -----
    The discrete-time implementation of a low-pass RC filter is given by
    the exponentially weighted moving average (with
    :math:`\tau = RC = 1/2\pi f_c`, :math:`\Delta t = 1/f_s`) [1]_

    .. math::
        y_i = \alpha x_i + (1 - \alpha)y_{i-1},

    where :math:`\alpha = \Delta t/(\tau + \Delta t)`. For a high-pass
    filter [2]_,

    .. math::

        y_i = \alpha y_{i-1} + \alpha(x_i - x_{i-1}),

    where :math:`\alpha = \tau/(\tau + \Delta t)`.

    See Also
    --------
    :func:`scipy.signal.sosfilt`

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Low-pass_filter#Discrete-time_realization
    .. [2] https://en.wikipedia.org/wiki/High-pass_filter#Discrete-time_realization

    """
    cutoff, btype = _parse_filter_edges(f_min, f_max, fs=fs, N=x.shape[-1])
    if btype is None:
        return x
    elif btype == 'bandstop':
        raise NotImplementedError

    # Normalize frequencies to [0, 1]
    cutoff = cutoff * 2 / fs
    # τ = 1 / πf_c for f_c in units of fs
    tau = 1 / (np.pi * cutoff)
    # Scale factor for cutoff freq of higher-order filters.
    scale = np.sqrt(2 ** (1 / order) - 1)

    z = []
    p = []
    k = 1
    # For bandpass TF is given by product of low- and high-pass, so the
    # zeros, poles and k just mulitply.
    if btype in {'lowpass', 'bandpass'}:
        tau[-1] *= scale
        alpha = 1 / (1 + tau[-1])
        # First-order TF is given by
        #                 z
        # H(z) = α × -----------
        #            z - (1 - α)
        # This has a zero at z = 0 and a pole at z = 1 - α.
        z.append(0)
        p.append(1 - alpha)
        k *= alpha
    if btype in {'highpass', 'bandpass'}:
        tau[0] /= scale
        alpha = 1 / (1 + 1 / tau[0])
        # First-order TF is given by
        #            z - 1
        # H(z) = α × -----
        #            z - α
        # This has a zero at z = 1 and a pole at z = α.
        z.append(1)
        p.append(alpha)
        k *= alpha

    sos = signal.zpk2sos(z * order, p * order, k ** order)
    return _sosfilt(sos, x, method)


def butter_filter(x, f_min: float = 0, f_max: float = np.inf, fs: float = 2, order: int = 5,
                  method: Literal['forward', 'forward-backward'] = 'forward', **_) -> np.ndarray:
    """Apply a digital Butter filter to the data.

    This function provides a simplified interface to SciPy's `signal`
    functionality by abstracting away some of the API.

    Parameters
    ----------
    x : array_like
        The data to be filtered.
    f_min, f_max : float
        The edges for (low-, band-, high-)pass filtering.
    fs : float
        Sample frequency. If not given, taken to be 2 so that the
        bandwidth ``[f_min, f_max]`` is normalized to the interval
        ``[0, 1]``.
    order : int
        The filter order. Default: 1.
    method :
        Use :func:`scipy:~scipy.signal.sosfilt` (forward) or
        :func:`scipy:~scipy.signal.sosfiltfilt` (forward-backward) to
        filter. Note that the latter impacts the transfer function.

    See Also
    --------
    :func:`scipy.signal.butter`
    :func:`scipy.signal.sosfilt`
    """
    cutoff, btype = _parse_filter_edges(f_min, f_max, fs=fs if fs is not None else 2,
                                        N=x.shape[-1])

    if btype is None:
        return x

    sos = signal.butter(order, np.sort(cutoff).squeeze(), btype, analog=False, output='sos', fs=fs)
    return _sosfilt(sos, x, method)


def welch(x, fourier_procfn: Optional[Union[Callable, Sequence[Callable]]] = None, fs: float = 1.0,
          window: Union[str, tuple[np.ndarray, ...]] = 'hann', nperseg: Optional[int] = None,
          noverlap: Optional[int] = None, nfft: Optional[int] = None,
          detrend: Union[str, Callable] = 'constant', normalize: Union[bool, Callable] = False,
          return_onesided: Optional[bool] = None, scaling: str = 'density', axis: int = -1,
          average: str = 'mean', workers: Optional[int] = None,
          **settings) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Use Welch's method to estimate the power spectral density.

    Adapted from :mod:`scipy.signal`, so see that module for parameter
    explanations.

    Unlike the SciPy version, this function allows to perform an
    additional processing step on the Fourier transform of the time data
    ``x``. This is done by applying ``fourier_procfn`` to the FFT'd data
    before the PSD is estimated. ``fourier_procfn`` should be a
    (sequence of) callable(s) with the following signature::

        fourier_procfn(Fx, f, **settings) -> Fxp, fp

    The function defaults to the identity map, so should reproduce the
    SciPy result. If a sequence, functions are applied from left to
    right, i.e., if ``fourier_procfn = [a, b, c]``, then they are
    applied as ``c(b(a(Fx, f, **s), f, **s, f, **s)``.

    By default, the twosided spectrum is computed if x is complex, and
    the transformed data are shifted using :func:`~numpy.fft.fftshift` so
    that they are ordered by monotonously increasing frequencies.

    For undocumented parameters see :func:`scipy.signal.welch`.

    Parameters
    ----------
    fourier_procfn : callable or sequence thereof
        A processing function that acts on the Fourier-transformed
        data (see above).
    normalize : callable or bool, default: False
        Similar to `detrend`, this can be used to normalize each Welch
        segment with some function. If True, the data is normalized by
        its standard deviation (corresponding to the RMS by default as
        the normalization is performed after detrending). This can be
        useful if one wants to compare spectra qualitatively.
    workers : int, optional
        The workers parameter of :func:`scipy:scipy.fft.fft`.

    Returns
    -------
    PSD : ndarray
        The power spectral density.
    f : ndarray
        The discrete FFT frequencies.
    ifft : ndarray
        The timeseries data after processing in Fourier space.

    Examples
    --------
    Same as :func:`scipy.signal.welch` for no fourier_procfn:

    >>> from scipy import signal
    >>> rng = np.random.default_rng()
    >>> x = rng.standard_normal((10, 3, 500))
    >>> np.allclose(signal.welch(x)[1], welch(x)[0])  # returned arguments switched around
    True

    Spectrum of differentiated signal:

    >>> def derivative(x, f, **_):
    ...     return x*2*np.pi*f, f
    >>> S, f, dxdt = welch(x, fourier_procfn=derivative)

    Compare to spectrum of numerical derivative:

    >>> import matplotlib.pyplot as plt
    >>> Sn, fn, dxdtn = welch(np.gradient(x, axis=-1))
    >>> lines = plt.loglog(f, S.mean((0, 1)), fn, Sn.mean((0, 1)))
    """
    if np.iterable(fourier_procfn):
        fourier_procfn = chain(*fourier_procfn, n_args=2)
    else:
        fourier_procfn = chain(fourier_procfn or fourier_space.Id, n_args=2)

    # Default to twosided if x is complex
    return_onesided = return_onesided or not np.iscomplexobj(x)

    axis = int(axis)
    # Ensure we have np.arrays, get outdtype
    # outdtype cannot be complex since we only calculate autocorrelations here.
    x = np.asarray(x)
    outdtype = np.result_type(x.real, np.float32)

    if x.size == 0:
        return (np.empty(x.shape, dtype=outdtype),
                np.empty(x.shape, dtype=outdtype),
                np.empty(x.shape, dtype=outdtype))

    if x.ndim > 1 and axis != -1:
        x = np.moveaxis(x, axis, -1)

    if nperseg is not None:  # if specified by user
        nperseg = int(nperseg)
        if nperseg < 1:
            raise ValueError('nperseg must be a positive integer')

    # parse window; if array like, then set nperseg = win.shape
    win, nperseg = _triage_segments(window, nperseg, input_length=x.shape[-1])

    if nfft is None:
        nfft = nperseg
    elif nfft < nperseg:
        raise ValueError('nfft must be greater than or equal to nperseg.')
    else:
        nfft = int(nfft)

    if noverlap is None:
        noverlap = nperseg//2
    else:
        noverlap = int(noverlap)
    if noverlap >= nperseg:
        raise ValueError('noverlap must be less than nperseg.')

    # Handle detrending and window functions
    if not detrend:
        def detrend_func(d):
            return d
    elif not callable(detrend):
        def detrend_func(d):
            return signal.detrend(d, type=detrend, axis=-1)
    elif axis != -1:
        # Wrap this function so that it receives a shape that it could
        # reasonably expect to receive.
        def detrend_func(d):
            d = np.moveaxis(d, -1, axis)
            d = detrend(d)
            return np.moveaxis(d, axis, -1)
    else:
        detrend_func = detrend

    if not normalize:
        def normalize_func(d):
            return d
    elif not callable(normalize):
        def normalize_func(d):
            # RMS normalization. Assumes detrend has already removed a constant trend.
            return d / rms(d, axis=-1, keepdims=True)
    elif axis != -1:
        def normalize_func(d):
            d = np.moveaxis(d, -1, axis)
            d = normalize(d)
            return np.moveaxis(d, axis, -1)
    else:
        normalize_func = normalize

    if np.result_type(win, np.float32) != outdtype:
        win = win.astype(outdtype)

    if scaling == 'density':
        scale = 1.0 / (fs * (win*win).sum())
    elif scaling == 'spectrum':
        scale = 1.0 / win.sum()**2
    else:
        raise ValueError('Unknown scaling: %r' % scaling)

    if return_onesided:
        if np.iscomplexobj(x):
            sides = 'twosided'
            warnings.warn('Input data is complex, switching to '
                          'return_onesided=False')
        else:
            sides = 'onesided'
    else:
        sides = 'twosided'

    if sides == 'twosided':
        freqs_func = chain(partial(fft.fftfreq, d=1/fs), partial(fft.fftshift, axes=-1))
        fft_func = chain(_fft_helper, partial(fft.fftshift, axes=-1), inspect_kwargs=True)
        ifft_func = chain(partial(fft.ifftshift, axes=-1), fft.ifft, inspect_kwargs=True)
    else:
        # sides == 'onesided'
        freqs_func = partial(fft.rfftfreq, d=1/fs)
        fft_func = _fft_helper
        ifft_func = fft.irfft

    freqs = freqs_func(nfft)

    # Perform the windowed FFTs. Need to pass kwargs so that FunctionChain can pass on only those
    # that are allowed for each function
    result = fft_func(x, win=win, detrend_func=detrend_func, normalize_func=normalize_func,
                      nperseg=nperseg, noverlap=noverlap, nfft=nfft, sides=sides, workers=workers)

    # Do custom stuff with the Fourier transformed data
    result, freqs = fourier_procfn(result, freqs, **settings)

    # Absolute value square and scaling to get the PSD
    result = scale * math.abs2(result)

    if sides == 'onesided':
        if nfft % 2:
            result[..., 1:] *= 2
        else:
            # Last point is unpaired Nyquist freq point, don't double
            result[..., 1:-1] *= 2

    # Inverse fft for processed time series data (not averaged over Welch segments)
    if not all(fp is fourier_space.Id for fp in fourier_procfn.functions):
        yf, _ = fourier_procfn(
            # Basically just fft.fft or fft.rfft
            fft_func(
                x, win=1, detrend_func=Id, normalize_func=Id, nperseg=x.shape[-1], noverlap=0,
                nfft=x.shape[-1], sides=sides, workers=workers
            )[..., 0, :],
            freqs_func(x.shape[-1]),
            **settings
        )
        y = ifft_func(yf, overwrite_x=True, workers=workers)
        ifft = np.moveaxis(y, -1, axis)
    else:
        ifft = np.moveaxis(x, -1, axis)

    result = result.astype(outdtype)

    # Output is going to have new last axis for time/window index, so a
    # negative axis index shifts down one
    if axis < 0:
        axis -= 1

    # Roll frequency axis back to axis where the data came from
    result = np.moveaxis(result, -1, axis)

    # Average over windows.
    if len(result.shape) >= 2 and result.size > 0:
        if result.shape[-1] > 1:
            if average == 'median':
                # np.median must be passed real arrays for the desired result
                bias = _median_bias(result.shape[-1])
                if np.iscomplexobj(result):
                    result = (np.median(np.real(result), axis=-1)
                              + 1j * np.median(np.imag(result), axis=-1))
                else:
                    result = np.median(result, axis=-1)
                result /= bias
            elif average == 'mean':
                result = result.mean(axis=-1)
            else:
                raise ValueError('average must be "median" or "mean", got %s'
                                 % (average,))
        else:
            result = np.reshape(result, result.shape[:-1])

    return result, freqs, ifft


def _fft_helper(x, win, detrend_func, normalize_func, nperseg, noverlap, nfft, sides, workers):
    """
    Calculate windowed FFT, for internal use by
    `scipy.signal._spectral_helper`.

    This is a helper function that does the main FFT calculation for
    `_spectral helper`. All input validation is performed there, and the
    data axis is assumed to be the last axis of x. It is not designed to
    be called externally. The windows are not averaged over; the result
    from each window is returned.

    Returns
    -------
    result : ndarray
        Array of FFT data

    Notes
    -----
    Adapted from matplotlib.mlab
    Then adapted from scipy.signal

    .. versionadded:: 0.16.0
    """
    # Created sliding window view of array
    if nperseg == 1 and noverlap == 0:
        result = x[..., np.newaxis]
    else:
        # https://stackoverflow.com/a/5568169
        step = nperseg - noverlap
        result = np.lib.stride_tricks.sliding_window_view(
            x, window_shape=nperseg, axis=-1, writeable=True
        )
        result = result[..., 0::step, :]

    # Detrend and normalize each data segment individually
    result = normalize_func(detrend_func(result))

    # Apply window by multiplication. No inplace op here since result might have uncastable type
    result = win*result

    # Perform the fft. Acts on last axis by default. Zero-pads automatically
    if sides == 'twosided':
        func = fft.fft
    else:
        result = result.real
        func = fft.rfft

    # Can overwrite because a new array is created above
    return func(result, n=nfft, workers=workers, overwrite_x=True)
