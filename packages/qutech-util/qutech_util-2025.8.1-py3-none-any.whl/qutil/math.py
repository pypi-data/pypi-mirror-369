import numpy as np
from numpy import ndarray

try:
    import numba as nb

    numba = True
except ImportError:
    numba = False


def abs2(x, /, out=None, *, where=True, casting='same_kind', order='C', dtype=None) -> ndarray:
    r"""
    Fast absolute value squared,

    .. math::

        |\cdot|^2 = \Re(\cdot)^2 + \Im(\cdot)^2.

    Equivalent to::

        abs(x)**2.

    See :class:`numpy:numpy.ufunc` and the `NumPy reference`_ for
    documentation of the arguments.

    .. _NumPy reference: https://numpy.org/doc/stable/reference/ufuncs.html

    Examples
    --------
    >>> abs2([(1 + 1j) / np.sqrt(2)])
    array([1.])
    >>> np.abs([(1 + 1j) / np.sqrt(2)])**2
    array([1.])

    """
    x = np.asanyarray(x)
    out = np.empty(x.shape, order=order, dtype=dtype or np.float64) if out is None else out
    out = np.square(x.real, out=out, dtype=dtype, where=where, casting=casting)
    if np.iscomplexobj(x):
        tmp = np.square(x.imag, order=order, dtype=dtype, where=where, casting=casting)
        out = np.add(out, tmp, out=out, dtype=dtype, where=where, casting=casting)
    return out


def cexp(x, /, out=None, *, where=True, casting='same_kind', order='C', dtype=None) -> ndarray:
    r"""
    Fast complex exponential,

    .. math::

        \exp(i x).

    See :class:`numpy:numpy.ufunc` and the `NumPy reference`_ for
    documentation of the arguments.

    .. _NumPy reference: https://numpy.org/doc/stable/reference/ufuncs.html

    Examples
    --------
    >>> cexp([np.pi])
    array([-1.+1.2246468e-16j])
    >>> np.exp([1j * np.pi])
    array([-1.+1.2246468e-16j])

    """
    x = np.asanyarray(x)
    out = np.empty(x.shape, order=order, dtype=dtype or np.complex128) if out is None else out
    out.real = np.cos(x, out=out.real, where=where, casting=casting)
    out.imag = np.sin(x, out=out.imag, where=where, casting=casting)
    return out


if numba:
    # nb.vectorize generates ufuncs with all the kwargs, so only one argument required.
    def _abs2(x):
        result = x.real * x.real
        if np.iscomplexobj(x):
            return result + x.imag * x.imag
        return result

    def _cexp(x):
        return np.cos(x) + 1j * np.sin(x)

    _abs2.__doc__ = abs2.__doc__
    _cexp.__doc__ = cexp.__doc__
    abs2 = nb.vectorize([nb.float32(nb.float32),
                         nb.float32(nb.complex64),
                         nb.float64(nb.float64),
                         nb.float64(nb.complex128)],
                        target='parallel',
                        cache=True)(_abs2)
    cexp = nb.vectorize([nb.complex64(nb.float32),
                         nb.complex128(nb.float64)],
                        target='parallel',
                        cache=True)(_cexp)


def remove_float_errors(arr: ndarray, eps_scale: float = None):
    """
    Clean up arr by removing floating point numbers smaller than the dtype's
    precision multiplied by eps_scale. Treats real and imaginary parts
    separately.
    """
    if eps_scale is None:
        atol = np.finfo(arr.dtype).eps * arr.shape[-1]
    else:
        atol = np.finfo(arr.dtype).eps * eps_scale

    # Hack around arr.imag sometimes not being writable
    if arr.dtype == complex:
        arr = arr.real + 1j * arr.imag
        arr.real[np.abs(arr.real) <= atol] = 0
        arr.imag[np.abs(arr.imag) <= atol] = 0
    else:
        arr = arr.real
        arr.real[np.abs(arr.real) <= atol] = 0

    return arr


def max_abs_diff(a, b):
    """Maximum absolute difference"""
    return np.max(np.abs(a - b))


def max_rel_diff(a, b):
    """Maximum relative difference"""
    return np.nanmax(np.abs((a - b) / np.abs(b)))
