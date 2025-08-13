"""This module contains utility functions for linear algebra manipulations."""
import operator
import string
import sys
import warnings
from collections.abc import Sequence
from functools import reduce
from itertools import zip_longest
from typing import List, NamedTuple, Tuple, Union

import numpy as np
from numpy import linalg, ndarray
from scipy.linalg import polar

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

from .math import abs2, cexp, max_abs_diff, max_rel_diff, remove_float_errors

try:
    cexp = deprecated('Use math.cexp instead')(cexp)
except AttributeError:
    _cexp = cexp

    def cexp(*args, **kwargs):
        warnings.warn('Use math.cexp instead', DeprecationWarning)
        return _cexp(*args, **kwargs)
try:
    abs2 = deprecated('Use math.abs2 instead')(abs2)
except AttributeError:
    _abs2 = abs2

    def abs2(*args, **kwargs):
        warnings.warn('Use math.abs2 instead', DeprecationWarning)
        return _abs2(*args, **kwargs)
remove_float_errors = deprecated('Use math.remove_float_errors instead')(remove_float_errors)
max_abs_diff = deprecated('Use math.max_abs_diff instead')(max_abs_diff)
max_rel_diff = deprecated('Use math.max_rel_diff instead')(max_rel_diff)

__all__ = ['check_phase_eq', 'density', 'dot_HS', 'mdot', 'pauli_expm', 'ptrace', 'sparsity',
           'tensor', 'paulis']


class PauliMatrices(NamedTuple):
    """Collection of pauli matrices that can be addressed by 'name' or by index.

    Examples
    --------
    >>> from qutil.linalg import paulis
    >>> paulis.sigma_z
    array([[ 1,  0],
           [ 0, -1]])
    >>> import numpy as np
    >>> np.testing.assert_equal(paulis.sigma_0 @ paulis.sigma_x, paulis.sigma_x)
    >>> np.testing.assert_equal(paulis.sigma_x @ paulis.sigma_x, paulis.sigma_0)
    >>> np.testing.assert_equal(paulis.sigma_x @ paulis.sigma_y, 1j * paulis.sigma_z)
    >>> np.testing.assert_equal(paulis.sigma_y.transpose().conjugate(), paulis.sigma_y)
    """
    sigma_0: np.ndarray = np.array([[1, 0], [0, 1]])
    sigma_x: np.ndarray = np.array([[0, 1], [1, 0]])
    sigma_y: np.ndarray = np.array([[0, -1j], [1j, 0]])
    sigma_z: np.ndarray = np.array([[1, 0], [0, -1]])


paulis = PauliMatrices()


def closest_unitary(Q: ndarray, subspace: Sequence[int] = None) -> ndarray:
    """Compute the closest unitary to ``Q[np.ix_(*subspace)]`` on a given
    subspace using left polar decomposition."""
    if subspace is None:
        subspace = (range(Q.shape[-2]), range(Q.shape[-1]))

    idx = np.ix_(*subspace)
    V = Q.copy()
    if Q.ndim == 2:
        V[idx], _ = polar(Q[idx], side='left')
    else:
        for i, q in enumerate(Q):
            V[i][idx], _ = polar(q[idx], side='left')

    return V


def tensor(*args, rank: int = 2,
           optimize: Union[bool, str] = False) -> ndarray:
    """
    Fast, flexible tensor product using einsum. The product is taken over the
    last *rank* axes and broadcast over the remaining axes which thus need to
    follow numpy broadcasting rules. Note that vectors are treated as rank 2
    tensors with shape (1, x) or (x, 1).

    For example, the following shapes are compatible:

     - ``rank == 2`` (e.g. matrices or vectors)::

        (a, b, c, d, d), (a, b, c, e, e) -> (a, b, c, d*e, d*e)
        (a, b, c), (a, d, e) -> (a, b*d, c*e)
        (a, b), (c, d, e) -> (c, a*d, b*e)
        (1, a), (b, 1, c) -> (b, 1, a*c)
     - ``rank == 1``::

        (a, b), (a, c) -> (a, b*c)
        (a, b, 1), (a, c) -> (a, b, c)

    Parameters
    ----------
    args : array_like
        The elements of the tensor product
    rank : int, optional (default: 2)
        The rank of the tensors. E.g., for a Kronecker product between two
        matrices ``rank == 2``. The remaining axes are broadcast over.
    optimize : bool|str, optional (default: False)
        Optimize the tensor contraction order. Passed through to
        :meth:`numpy.einsum`.

    Examples
    --------
    >>> Z = np.diag([1, -1])
    >>> np.array_equal(tensor(Z, Z), np.kron(Z, Z))
    True

    >>> A, B = np.arange(2), np.arange(2, 5)
    >>> tensor(A, B, rank=1)
    array([0, 0, 0, 2, 3, 4])

    >>> args = np.random.randn(4, 10, 3, 2)
    >>> result = tensor(*args, rank=1)
    >>> result.shape == (10, 3, 2**4)
    True
    >>> result = tensor(*args, rank=2)
    >>> result.shape == (10, 3**4, 2**4)
    True

    >>> A, B = np.random.randn(1, 3), np.random.randn(3, 4)
    >>> result = tensor(A, B)
    >>> result.shape == (1*3, 3*4)
    True

    >>> A, B = np.random.randn(3, 1, 2), np.random.randn(2, 2, 2)
    >>> try:
    ...     result = tensor(A, B, rank=2)
    ... except ValueError as err:  # cannot broadcast over axis 0
    ...     print(err)
    Incompatible shapes (3, 1, 2) and (2, 2, 2) for tensor product of rank 2.
    >>> result = tensor(A, B, rank=3)
    >>> result.shape == (3*2, 1*2, 2*2)
    True

    See Also
    --------
    :meth:`numpy.kron`
    """
    chars = string.ascii_letters
    # All the subscripts we need
    A_chars = chars[:rank]
    B_chars = chars[rank:2 * rank]
    subscripts = '...{},...{}->...{}'.format(
        A_chars, B_chars, ''.join(i + j for i, j in zip(A_chars, B_chars))
    )

    def _tensor_product_shape(shape_A: Sequence[int], shape_B: Sequence[int],
                              rank: int):
        """Get shape of the tensor product between A and B of rank rank"""
        broadcast_shape = ()
        # Loop over dimensions from last to first, filling the 'shorter' shape
        # with 1's once it is exhausted
        for dims in zip_longest(shape_A[-rank - 1::-1], shape_B[-rank - 1::-1],
                                fillvalue=1):
            if 1 in dims:
                # Broadcast 1-d of argument to dimension of other
                broadcast_shape = (max(dims),) + broadcast_shape
            elif len(set(dims)) == 1:
                # Both arguments have same dimension on axis.
                broadcast_shape = dims[:1] + broadcast_shape
            else:
                raise ValueError('Incompatible shapes ' +
                                 f'{shape_A} and {shape_B} ' +
                                 f'for tensor product of rank {rank}.')

        # Shape of the actual tensor product is product of each dimension,
        # again broadcasting if need be
        tensor_shape = tuple(
            reduce(operator.mul, dimensions) for dimensions in zip_longest(
                shape_A[:-rank - 1:-1], shape_B[:-rank - 1:-1], fillvalue=1
            )
        )[::-1]

        return broadcast_shape + tensor_shape

    def binary_tensor(A, B):
        """Compute the Kronecker product of two tensors"""
        # Add dimensions so that each arg has at least ndim == rank
        while A.ndim < rank:
            A = A[None, :]

        while B.ndim < rank:
            B = B[None, :]

        outshape = _tensor_product_shape(A.shape, B.shape, rank)
        return np.einsum(subscripts, A, B, optimize=optimize).reshape(outshape)

    # Compute the tensor products in a binary tree-like structure, calculating
    # the product of two leaves and working up. This is more memory-efficient
    # than reduce(binary_tensor, args) which computes the products
    # left-to-right.
    n = len(args)
    bit = n % 2
    while n > 1:
        args = args[:bit] + tuple(binary_tensor(*args[i:i + 2])
                                  for i in range(bit, n, 2))

        n = len(args)
        bit = n % 2

    return args[0]


def mdot(arr: Sequence, axis: int = 0) -> ndarray:
    """Multiple matrix products along axis"""
    return reduce(np.matmul, arr.swapaxes(0, axis))


def ptrace(arr: ndarray, dims: Sequence[int], system: int = 1) -> ndarray:
    r"""
    Partial trace of bipartite matrix.

    Parameters
    ----------
    arr : ndarray
        Matrix of bipartite system on the last two axes. There are no
        constraints on the shape of the other axes.

        .. math::

            \verb|arr|\equiv A\otimes B
    dims : Sequence of ints
        The dimensions of system A and B
    system : int
        The system to trace out, either 0 (A) or 1 (B)

    Examples
    --------
    >>> d_A, d_B = 3, 2
    >>> A = np.arange(d_A**2).reshape(1, d_A, d_A)
    >>> B = np.arange(d_B**2).reshape(1, d_B, d_B)
    >>> C = tensor(A, B)
    >>> ptrace(C, (d_A, d_B), 0)
    array([[[ 0, 12],
            [24, 36]]])
    >>> ptrace(C, (d_A, d_B), 1)
    array([[[ 0,  3,  6],
            [ 9, 12, 15],
            [18, 21, 24]]])

    """
    if system == 0:
        einsum_str = '...ijik'
    elif system == 1:
        einsum_str = '...ikjk'

    return np.einsum(einsum_str, arr.reshape(*arr.shape[:-2], *dims, *dims))


def pauli_expm(a: Sequence, nonzero_ind: list[bool]) -> ndarray:
    r"""
    Faster method of calculating a Pauli exponential

    .. math::
        \exp(-i(\vec{a}\cdot\vec{\sigma})) = I\cos|\vec{a}|
            - i(\vec{a}\cdot\vec{\sigma})\sin|\vec{a}|

    than :meth:`scipy.linalg.expm`.

    Parameters
    ----------
    a : array_like, shape (n, ...)
        Array with 0 < n <= 3 cartesian components on the first axis.
    nonzero_ind : list of three bools
        List of three Booleans indicating those cartesian components that are
        nonzero, i.e., which of the three (x, y, z) are the first axis of *a*.
        Accordingly, ``sum(nonzero_ind) == a.shape[0]``.

    Examples
    --------
    A Hadamard gate, i.e. a rotation by pi about X + Z (dividing by sqrt(2)
    normalizes the rotation axis vector):

    >>> a = np.full((2,), np.pi/2/np.sqrt(2))
    >>> pauli_expm(a, [True, False, True])  # a[0]=a[2]=pi/2/sqrt(2), a[1]=0
    array([[6.123234e-17-0.70710678j, 0.000000e+00-0.70710678j],
           [0.000000e+00-0.70710678j, 6.123234e-17+0.70710678j]])
    """
    a = np.asarray(a)
    idx = np.asarray(nonzero_ind)
    if not sum(idx) == a.shape[0]:
        raise ValueError('nonzero_ind should have the same number of True '
                         f'entries as a.shape[0] = {a.shape[0]}!')

    p0, pi = np.split(paulis, [1])
    # Twice the rotation angle
    theta = linalg.norm(a, axis=0)
    # Rotation axis
    n = a / theta
    # Replace nans originating from divide by zero
    n[np.isnan(n)] = 0
    real = np.einsum('ijk,...->jk...', p0, np.cos(theta))
    imag = np.einsum('i...,ijk,...->jk...', n, pi[idx], np.sin(theta))
    result = real - 1j * imag
    return result.transpose([2, 0, 1]) if result.ndim == 3 else result


def check_phase_eq(psi: Sequence,
                   phi: Sequence,
                   eps: float = None,
                   normalized: bool = False) -> tuple[bool, float]:
    r"""
    Checks whether psi and phi are equal up to a global phase, i.e.

    .. math::
        |\psi\rangle = e^{i\chi}|\phi\rangle \Leftrightarrow
        \langle \phi|\psi\rangle = e^{i\chi},

    and returns the phase. If the first return value is false, the second is
    meaningless in this context. psi and phi can also be operators.

    Parameters
    ----------
    psi, phi : array_like
        Vectors or operators to be compared
    eps : float
        The tolerance below which the two objects are treated as equal, i.e.,
        the function returns ``True`` if ``abs(1 - modulus) <= eps``.
    normalized : bool
        Flag indicating if *psi* and *phi* are normalized with respect to the
        Hilbert-Schmidt inner product :meth:`dot_HS`.

    Examples
    --------
    >>> import qutil.qi
    >>> psi = qutil.qi.paulis[1]
    >>> phi = qutil.qi.paulis[1]*np.exp(1j*1.2345)
    >>> eq, phase = check_phase_eq(psi, phi)
    >>> print(eq)
    True
    >>> print(phase)
    1.2345000000000603
    """
    if eps is None:
        # Tolerance the floating point eps times the # of flops for the matrix
        # multiplication, i.e. for psi and phi n x m matrices 2*n**2*m
        try:
            psi_eps = np.finfo(psi.dtype).eps
        except ValueError:
            # data type not inexact
            psi_eps = 0
        try:
            phi_eps = np.finfo(phi.dtype).eps
        except ValueError:
            # data type not inexact
            phi_eps = 0

        eps = max(psi_eps, phi_eps) * np.prod(psi.shape) * phi.shape[-1] * 2

        if not normalized:
            # normalization introduces more floating point error
            eps *= (np.prod(psi.shape) * phi.shape[-1] * 2) ** 2

    if psi.ndim - psi.shape.count(1) == 1:
        # Vector
        inner_product = (psi.T.conj() @ phi).squeeze()
        if normalized:
            norm = 1
        else:
            norm = (linalg.norm(psi) * linalg.norm(phi)).squeeze()
    elif psi.ndim == 2:
        inner_product = dot_HS(psi, phi, eps)
        # Matrix
        if normalized:
            norm = 1
        else:
            norm = np.sqrt(dot_HS(psi, psi, eps) * dot_HS(phi, phi, eps))
    else:
        raise ValueError('Invalid dimension')

    phase = np.angle(inner_product)
    modulus = abs(inner_product)

    return abs(norm - modulus) <= eps, phase


def dot_HS(U: ndarray,
           V: ndarray,
           eps: float = None) -> float:
    r"""Return the Hilbert-Schmidt inner product of U and V,

    .. math::
        \langle U, V\rangle_\mathrm{HS} := \mathrm{tr}(U^\dagger V).

    Parameters
    ----------
    U, V : ndarray
        Objects to compute the inner product of.

    Returns
    -------
    result : float, complex
        The result rounded to precision eps.

    Examples
    --------
    >>> import qutil.qi
    >>> U, V = qutil.qi.paulis[1:3]
    >>> print(dot_HS(U, V))
    0.0
    >>> print(dot_HS(U, U))
    2
    """
    if eps is None:
        # Tolerance is the dtype precision times the number of flops for the
        # matrix multiplication times two to be on the safe side
        try:
            eps = np.finfo(U.dtype).eps * np.prod(U.shape) * V.shape[-1] * 2
        except ValueError:
            # dtype is int and therefore exact
            eps = 0

    if eps == 0:
        decimals = 0
    else:
        decimals = abs(int(np.log10(eps)))

    res = np.round(np.einsum('...ij,...ij', U.conj(), V), decimals)
    return res if res.imag.any() else res.real


def sparsity(arr: ndarray, eps: float = None) -> float:
    """
    Return the sparsity of the array *arr*.

    Parameters
    ----------
    arr: array_like
        The array
    eps: float (default: dtype eps)
        Entries smaller than this value will be treated as zero

    Returns
    -------
    sparsity: float
        The sparsity of the array
    """
    eps = np.finfo(arr.dtype).eps if eps is None else eps
    return (np.abs(arr) <= eps).sum() / arr.size


def density(arr: ndarray, eps: float = None) -> float:
    """
    Return the density of the array *arr*.

    Parameters
    ----------
    arr: array_like
        The array
    eps: float (default: dtype eps)
        Entries smaller than this value will be treated as zero

    Returns
    -------
    density: float
        The density of the array
    """
    eps = np.finfo(arr.dtype).eps if eps is None else eps
    return (np.abs(arr) > eps).sum() / arr.size
