"""This module contains signal processing functions that work on data in
frequency space.
For consistency, functions in this module should have the data to be
processed as first and the frequencies at which the data is sampled as
their second argument, while always returning a tuple of (possibly
processed) frequencies and processed data, i.e.::

    def fun(data, f, *args, **kwargs) -> processed_data, processed_f:
        ...

Examples
--------
Compare the frequency response of a simple RC bandpass filter to the
Butterworth filter:

>>> import matplotlib.pyplot as plt
>>> cycler = plt.rcParams['axes.prop_cycle']
>>> f_min, f_max = 1e-1, 1e1
>>> f = np.logspace(-2, 2, 1001)
>>> args = (f, f_min, f_max)
>>> fig, ax = plt.subplots()
>>> for order, color in zip(range(1, 6), cycler):
...     _ = ax.loglog(f, abs(RC_transfer_function(*args, order)),
...                   **color, ls='--', label=f'RC {order}')
...     _ = ax.loglog(f, abs(butter_transfer_function(*args, order)),
...                   **color, ls='-', label=f'Butter {order}')
>>> _ = ax.axvline(f_min, color='k')
>>> _ = ax.axvline(f_max, color='k')
>>> _ = ax.legend(ncols=2)
>>> _ = ax.grid(True)
>>> _ = ax.set_xlabel('$f$ (Hz)')
>>> _ = ax.set_ylabel('$|H(f)|$')
>>> _ = ax.set_ylim(1e-2)

Note that for ``order=1``, the filters coincide:

>>> np.allclose(RC_transfer_function(f, f_min=f_min, f_max=f_max, order=1)[0],
...             butter_transfer_function(f, f_min=f_min, f_max=f_max, order=1)[0])
True

"""
import inspect
from typing import Literal, Optional, Tuple, TypeVar

import numpy as np
from scipy import integrate

from qutil import math
from qutil.caching import cache
from qutil.functools import wraps
from qutil.misc import deprecate_kwargs
from qutil.signal_processing._common import _parse_filter_edges
from qutil.typecheck import check_literals

try:
    import numba
except ImportError:
    numba = None

_S = TypeVar('_S')
_T = TypeVar('_T')


@cache
def _butterworth_coefficient(k: int, n: int) -> float:
    if k == 0:
        return 1
    if k > n // 2:
        # Make use of symmetry for extermely performance critical part
        return _butterworth_coefficient(n - k, n)
    return (_butterworth_coefficient(k - 1, n)
            * np.cos(np.pi / (2 * n) * (k - 1))
            / np.sin(np.pi / (2 * n) * k))


def _butterworth_polynomial(s: np.ndarray, n: int) -> np.ndarray:
    return sum(_butterworth_coefficient(k, n) * s ** k for k in range(n + 1))


def _standardize(function):
    """Adds variadic kwargs and f arg and return param."""
    try:
        parameters = inspect.signature(function).parameters
        assert 'f' not in parameters, \
            'Only use this decorator for functions without parameter named f'
        assert not any(p.kind is inspect.Parameter.VAR_KEYWORD for p in parameters.values()), \
            'Only use this decorator for functions without variadic keyword arguments.'
    except ValueError:
        # ufunc, https://numpy.org/doc/stable/reference/ufuncs.html#ufuncs-kwargs
        parameters = {'out', 'where', 'axes', 'axis', 'keepdims', 'casting', 'order', 'dtype',
                      'subok', 'signature', 'extobj'}

    @wraps(function)
    def wrapper(x, f, *args, **kwargs):
        # Filter kwargs that function actually accepts
        kwargs = {k: v for k, v in kwargs.items() if k in parameters}
        return function(x, *args, **kwargs), f

    return wrapper


def convention_compliant(func):
    """Wrap a function that does not take frequency as second argument
    and returns it to comply with the convention in this module."""

    @wraps(func)
    def wrapper(x, f, *args, **kwargs) -> tuple[np.ndarray, np.ndarray]:
        return func(x, *args, **kwargs), f

    return wrapper


def Id(x: _S, f: _T, *_, **__) -> tuple[_S, _T]:
    """The identity mapping."""
    return x, f


@deprecate_kwargs(deriv_order='order')
def derivative(x, f, order: int = 0, overwrite_x: bool = False,
               **_) -> tuple[np.ndarray, np.ndarray]:
    r"""Compute the (anti-)derivative.

    The sign convention is according to the following defintion of the
    Fourier transform:

    .. math::
        \hat{f}(\omega) &= \int_{-\infty}^\infty\mathrm{d}t
            e^{-i\omega t} f(t) \\
        f(t) &= \int_{-\infty}^\infty\frac{\mathrm{d}\omega}{2\pi}
            e^{i\omega t} \hat{f}(\omega)

    .. note::
        For negative ``order`` (antiderivatives), the zero-frequency
        component is set to zero (due to zero-division).

    Parameters
    ----------
    x : array_like
        Target data.
    f : array_like
        Frequencies corresponding to the last axis of `x`.
    order : int
        The order of the derivative. If negative, the antiderivative is
        computed (indefinite integral). Default: 0.
    overwrite_x : bool, default False
        Overwrite the input data array.

    Examples
    --------
    Compare finite-differences to the Fourier space derivative:

    >>> dt = .1; n = 51
    >>> t = np.arange(n * dt, step=dt)
    >>> xt = np.sin(5 * t)
    >>> f = np.fft.rfftfreq(n, dt)
    >>> xf = np.fft.rfft(xt)

    Compute the derivatives:

    >>> import matplotlib.pyplot as plt
    >>> xfd, f = derivative(xf, f, order=1)
    >>> xtd = np.gradient(xt, t)
    >>> plt.plot(t, 5 * np.cos(5 * t), label='Analytical')  # doctest: +SKIP
    >>> plt.plot(t, xtd, label='Finite differences')  # doctest: +SKIP
    >>> plt.plot(t, np.fft.irfft(xfd, n=n), label='FFT')  # doctest: +SKIP
    >>> plt.legend(); plt.xlabel('$t$'); plt.ylabel('$dx/dt$')  # doctest: +SKIP

    Integrals:

    >>> from scipy import integrate
    >>> xfii, f = derivative(xf, f, order=-2)
    >>> xti = integrate.cumulative_simpson(xt, x=t, initial=0)
    >>> xtii = integrate.cumulative_simpson(xti, x=t, initial=0)
    >>> plt.plot(t, -xt / 25, label='Analytical')  # doctest: +SKIP
    >>> # cheating a bit here because indefinite integration is tricky
    >>> plt.plot(t, xtii - np.linspace(0, 1, n), label='Finite differences')  # doctest: +SKIP
    >>> plt.plot(t, np.fft.irfft(xfii, n=n), label='FFT')  # doctest: +SKIP
    >>> plt.legend(); plt.xlabel('$t$'); plt.ylabel(r'$\iint x dt$')  # doctest: +SKIP

    Note that the backtransform method naturally only works well for
    periodic data.

    """
    f = np.asanyarray(f)
    x = np.asanyarray(x)
    x = np.array(x, copy=not overwrite_x, dtype=np.result_type(x.dtype, 1j))
    with np.errstate(invalid='ignore', divide='ignore'):
        x *= (2j*np.pi*f)**order
    if order < 0:
        x[..., (f == 0).nonzero()] = 0
    return x, f


def rms(x, f, /, out=None, *, axis: Optional[int] = None, where=True, dtype=None, keepdims=False,
        **_) -> tuple[np.ndarray, np.ndarray]:
    """Compute the RMS (root-mean-square).

    See :class:`numpy.ufunc` and the `NumPy reference`_ for
    documentation of the arguments.

    .. _NumPy reference: https://numpy.org/doc/stable/reference/ufuncs.html

    Examples
    --------
    >>> t = np.linspace(0, 1, 1001)
    >>> x = 2*np.sqrt(2)*np.sin(2*np.pi*10*t)
    >>> xf = np.fft.fft(x)  # nb rfft would need to be scaled by factor √2
    >>> r, _ = rms(xf, ...)  # f not actually needed
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
    result /= N
    return result, f


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
        res[0] = np.sqrt(res[0]) / x.shape[0]

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


def _design_tf(lp, f, f_min, f_max):
    """Filter *f* by using the low-pass *lp* as a prototype for
    different filters.

    ``lp`` is a callable that takes the single-argument 1j*f/f_c.
    """
    cutoff, btype = _parse_filter_edges(f_min, f_max, f=f)
    # Copy f to condition it for division by zero
    f = np.array(f, dtype=np.float64, copy=True)
    f[f == 0] = np.finfo(np.float64).eps

    # https://en.wikipedia.org/wiki/Prototype_filter
    if btype is None:
        return np.ones_like(f, dtype=complex)
    elif btype == 'lowpass':
        return lp(1j / cutoff[-1] * f)
    elif btype == 'highpass':
        # iω/ω_c -> ω_c/iω
        return lp(-1j * cutoff[0] / f)
    elif btype == 'bandpass':
        # iω/ω_c -> Q(iω/ω_c + ω_c/iω)
        f_0 = np.sqrt(np.prod(cutoff))
        delta_f = np.diff(np.sort(cutoff))
        Q = f_0 / delta_f
        iff0 = 1j / f_0 * f
        return lp(Q * (iff0 + 1 / iff0))
    elif btype == 'bandstop':
        # ω_c/iω -> Q(iω/ω_c + ω_c/iω)
        f_0 = np.sqrt(np.prod(cutoff))
        delta_f = np.diff(np.sort(cutoff))
        Q = f_0 / delta_f
        return lp(1j * f * f_0 / (Q * (f_0 ** 2 - f ** 2)))


def RC_transfer_function(f, f_min: float = 0, f_max: float = np.inf, order: int = 1, **_):
    """RC-type filter transfer function.

    See :func:`RC_filter`.
    """
    def lp(iffc):
        return 1 / (1 + iffc * np.sqrt(2 ** (1 / order) - 1)) ** order

    return _design_tf(lp, f, f_min, f_max)


def butter_transfer_function(f, f_min: float = 0, f_max: float = np.inf, order: int = 1, **_):
    """Butterworth filter transfer function.

    See :func:`butter_filter`.
    """
    def lp(iffc):
        return 1 / _butterworth_polynomial(iffc, order)

    return _design_tf(lp, f, f_min, f_max)


def brickwall_transfer_function(f, f_min: float = 0, f_max: float = np.inf, **_):
    """Brickwall filter transfer function.

    See :func:`brickwall_filter`.
    """
    f = np.asanyarray(f)
    tf = np.ones_like(f, dtype=complex)
    tf[(f < f_min) | (f > f_max)] = 0
    return tf


def RC_filter(x, f, f_min: float = 0, f_max: float = np.inf, order: int = 1,
              overwrite_x: bool = False, **_) -> tuple[np.ndarray, np.ndarray]:
    r"""RC-type filter.

    .. note::
        The cutoff frequencies here are defined in terms of 3 dB
        bandwidth, meaning that for any order the transfer function
        at the cutoff frequencies takes the value :math:`1/\sqrt{2}`.

        See :ref:`examples` for how to implement a cascaded,
        :math:`n`-th order RC filter.

    Parameters
    ----------
    x : array_like
        The data to be filtered.
    f : array_like
        Frequencies corresponding to the last axis of `x`.
    f_min, f_max : float
        The cutoff frequencies for (low-, band-, high-)pass filtering.
        Given by

        .. math::
            f_\mathrm{min} &= \frac{\sqrt{2^\frac{1}{n} - 1}}
                {2\pi\tau} \\
            f_\mathrm{max} &= \frac{1}
                {2\pi\tau\sqrt{2^\frac{1}{n} - 1}}

        with :math:`\tau = RC` of either filter.
    order : int
        The order :math:`n` of the filter.
    overwrite_x : bool, default False
        Overwrite the input data array.

    Notes
    -----
    The transfer function of the general bandpass filter is given by

    .. math::
        H(f) = \left(\frac{1}{1 - i f_\mathrm{min} / f}
                     \times\frac{1}{1 + i f / f_\mathrm{max}}\right)^n.

    If ``f_min`` is 0 or ``f_max`` is inf, only a low-/high-pass filter
    is applied, respectively.

    .. _examples:

    Examples
    --------
    For consistency with e.g. :func:`butter_filter`, the cutoff
    frequency arguments of this function give the 3 dB bandwidth.
    This means that for any order, the transfer function takes on
    the absolute value of (approximately) :math:`1/\sqrt{2}` for
    ``f_min`` and ``f_max``:

    >>> order = 3
    >>> f_min, f_max = 1e-1, 1e1
    >>> f = np.geomspace(1e-2, 1e2, 101)
    >>> x = np.ones_like(f)
    >>> x_filt, f = RC_filter(x, f, f_min=f_min, f_max=f_max,
    ...                       order=order)
    >>> np.allclose(abs(x_filt[f == f_min]), 1/np.sqrt(2), atol=1e-4)
    True
    >>> np.allclose(abs(x_filt[f == f_max]), 1/np.sqrt(2), atol=1e-4)
    True

    If instead a cascaded filter is desired where each stage has the
    given cutoff frequency, you can do the following for a, say,
    third-order filter:

    >>> from qutil.functools import chain
    >>> from qutil.itertools import repeat
    >>> cascaded_RC_filter = chain(*repeat(RC_filter, order), n_args=2)
    >>> x_filt, f = cascaded_RC_filter(x, f, f_min=f_min, f_max=f_max,
    ...                                order=1)
    >>> np.allclose(abs(x_filt[f == f_min]), 1/np.sqrt(2)**order,
    ...             atol=1e-4)  # 3dB not exactly 1/sqrt(2)
    True
    >>> np.allclose(abs(x_filt[f == f_max]), 1/np.sqrt(2)**order,
    ...             atol=1e-4)
    True

    """
    x = np.array(x, dtype=complex, copy=not overwrite_x)
    f = np.asanyarray(f)
    x *= RC_transfer_function(f, f_min, f_max, order)
    return x, f


def butter_filter(x, f, f_min: float = 0, f_max: float = np.inf, order: int = 5,
                  overwrite_x: bool = False, **_) -> tuple[np.ndarray, np.ndarray]:
    r"""Butterworth filter.

    Parameters
    ----------
    x : array_like
        The data to be filtered.
    f : array_like
        Frequencies corresponding to the last axis of `x`.
    f_min, f_max : float
        The cutoff frequencies for (low-, band-, high-)pass filtering.
    order : int
        The order :math:`n` of the filter.
    overwrite_x : bool, default False
        Overwrite the input data array.

    Returns
    -------
    x : ndarray
        The filtered data.
    f : ndarray
        The input frequencies.

    Notes
    -----
    The transfer function of the Butterworth filter can be expressed in
    terms of the normalized Butterworth polynomials [1]_, [2]_

    .. math::
        B_n(s) = \sum_{k=0}^n a_k s^k

    with :math:`s = \sigma + i\omega` the Laplace transform frequency,

    .. math::
        a_k = \prod_{\mu=1}^k\frac{\cos((\mu-1)\gamma)}{\sin(\mu\gamma)}

    with :math:`\mu = \pi/2n` as

    .. math::
        H(s) = \begin{cases}
            \frac{1}{B_n(s/\omega_c)},\quad\mathrm{lowpass} \\
            \frac{(s/\omega_c)^n}{B_n(s/\omega_c)},\quad\mathrm{highpass}.
        \end{cases}

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Butterworth_filter
    .. [2] https://tttapa.github.io/Pages/Mathematics/Systems-and-Control-Theory/Analog-Filters/Butterworth-Filters.html

    """
    x = np.array(x, dtype=complex, copy=not overwrite_x)
    f = np.asanyarray(f)
    x *= butter_transfer_function(f, f_min, f_max, order)
    return x, f


def brickwall_filter(x, f, f_min: float = 0, f_max: float = np.inf,
                     overwrite_x: bool = False, **_) -> tuple[np.ndarray, np.ndarray]:
    """Apply a brick wall filter to the data.

    Parameters
    ----------
    x : array_like
        The data to be filtered.
    f : array_like
        Frequencies corresponding to the last axis of `x`.
    f_min, f_max : float
        The locations of the brick walls for (low-, band-, high-)pass
        filtering.
    overwrite_x : bool, default False
        Overwrite the input data array.
    """
    x = np.array(x, dtype=complex, copy=not overwrite_x)
    f = np.asanyarray(f)
    x *= brickwall_transfer_function(f, f_min, f_max)
    return x, f


@check_literals
def octave_band_rms(x, f, base: Literal[2, 10] = 10, fraction: int = 1,
                    return_band_edges: bool = False, **_) -> tuple[np.ndarray, np.ndarray]:
    """Compute the rms over octave fractions [1]_, [2]_.

    Parameters
    ----------
    x : ndarray, shape (..., n_freq)
        The amplitude spectral density to compute the rms from.
        (I.e., the frequency-domain data).
    f : ndarray, shape (n_freq,)
        The frequencies corresponding to the data x.
    base : 2 or 10
        The logarithm base for the octaves.
    fraction : int
        The denominator of the fraction of an octave band to use for
        the calculation.
    return_band_edges : bool
        Return the edges instead of the midband frequencies.

    Returns
    -------
    octave_band_rms : ndarray
        The rms values.
    bandedge_frequencies : ndarray
        The frequencies of the octave band edges
        (if return_band_edges is true).
    midband_frequencies : ndarray
        The midband frequencies of the octave bands.
        (if return_band_edges is false).

    References
    ----------
    .. [1] C. G. Gordon, “Generic vibration criteria for vibration-
       sensitive equipment”, in Optomechanical Engineering and
       Vibration Control, Vol. 3786 (Sept. 28, 1999), pp. 22–33.
       https://www.spiedigitallibrary.org/conference-proceedings-of-spie/3786/0000/Generic-vibration-criteria-for-vibration-sensitive-equipment/10.1117/12.363802.short
    .. [2] ANSI/ASA S1.11-2004 (R2009). Octave-Band and Fractional-
       Octave-Band Analog and Digital Filters.
       https://webstore.ansi.org/standards/asa/ansiasas1112004r2009
    """
    mask = f > 0
    f = f[mask]
    x = math.abs2(x[..., mask])
    df = f[1] - f[0]

    # Computed according to ANSI S1.11-2004
    reference_frequency = 1000
    frequency_ratio = 10**0.3 if base == 10 else 2
    # Compute the band index x from the frequencies given
    # and then calculate back the midband frequencies
    if fraction % 2:
        bmin = fraction*np.log(f.min()/reference_frequency)/np.log(frequency_ratio) + 30
        bmax = fraction*np.log(f.max()/reference_frequency)/np.log(frequency_ratio) + 30
        band_index = np.arange(np.ceil(bmin), np.ceil(bmax))
        midband_frequencies = reference_frequency*frequency_ratio**((band_index - 30)/fraction)
    else:
        bmin = (2*fraction*np.log(f.min()/reference_frequency)/np.log(frequency_ratio) + 59)/2
        bmax = (2*fraction*np.log(f.max()/reference_frequency)/np.log(frequency_ratio) + 59)/2
        band_index = np.arange(np.ceil(bmin), np.ceil(bmax))
        midband_frequencies = reference_frequency*frequency_ratio**((2*band_index - 59)/2/fraction)

    bandedge_frequencies = (midband_frequencies[:, None]
                            * frequency_ratio**(np.array([-1, 1])/2/fraction))
    bandwidths = np.diff(bandedge_frequencies)[:, 0]

    # drop bands for which the frequency resolution is too low to integrate
    mask = 2*df < bandwidths
    midband_frequencies = midband_frequencies[mask]
    bandedge_frequencies = bandedge_frequencies[mask, :]

    mean_square = np.empty(x.shape[:-1] + midband_frequencies.shape)
    for i, (f_lower, f_upper) in enumerate(bandedge_frequencies):
        mask = (f_lower <= f) & (f <= f_upper)
        mean_square[..., i] = integrate.trapezoid(x[..., mask], f[..., mask])

    if return_band_edges:
        return np.sqrt(mean_square), bandedge_frequencies
    else:
        return np.sqrt(mean_square), midband_frequencies
