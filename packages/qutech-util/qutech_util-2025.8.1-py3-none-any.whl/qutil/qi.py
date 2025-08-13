"""This module contains utilities pertaining to quantum information"""
from typing import Callable

import numpy as np
from scipy.spatial import transform as st

from . import linalg
from .linalg import paulis

__all__ = ['paulis', 'hadamard', 'cnot', 'cphase', 'crot', 'swap']


def crot(phi: float) -> np.ndarray:
    """conditional rotation by phi"""
    gate = np.array(
        [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 1, 0],
         [0, 0, 0, np.exp(1j*phi)]]
    )
    return gate


hadamard = np.array(
    [[1, 1],
     [1, -1]]
)/np.sqrt(2)

cnot = np.array(
    [[1, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 0, 1],
     [0, 0, 1, 0]]
)

cphase = np.array(
    [[1, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 1, 0],
     [0, 0, 0, -1]]
)

swap = np.array(
    [[1, 0, 0, 0],
     [0, 0, 1, 0],
     [0, 1, 0, 0],
     [0, 0, 0, 1]]
)


def pauli_basis(n: int):
    """n-qubit normalized Pauli basis.

    Parameters
    ----------
    n: int
        Number of qubits.

    Returns
    -------
    sigma: ndarray, shape (d**2, d, d)
        n-qubit Pauli basis.

    """
    normalization = np.sqrt(2**n)
    combinations = np.indices((4,)*n).reshape(n, 4**n)
    sigma = linalg.tensor(*np.array(paulis)[combinations], rank=2)
    sigma /= normalization
    return sigma


def ggm_basis(d: int):
    """Hermitian orthonormal basis for d-dimensional Hilbert space.

    Parameters
    ----------
    d: int
        Dimension of Hilbert space.

    Returns
    -------
    Lambda: ndarray, shape (d**2, d, d)
        The basis (see [Bert08]_).

    References
    ----------
    .. [Bert08]
        Bertlmann, R. A., & Krammer, P. (2008). Bloch vectors for
        qudits. Journal of Physics A: Mathematical and Theoretical,
        41(23). https://doi.org/10.1088/1751-8113/41/23/235303
    """
    n_sym = int(d*(d - 1)/2)
    sym_rng = np.arange(1, n_sym + 1)
    diag_rng = np.arange(1, d)

    # Indices for offdiagonal elements
    j = np.repeat(np.arange(d - 1), np.arange(d - 1, 0, -1))
    k = np.arange(1, n_sym+1) - (j*(2*d - j - 3)/2).astype(int)
    j_offdiag = tuple(j)
    k_offdiag = tuple(k)
    # Indices for diagonal elements
    j_diag = tuple(i for m in range(d) for i in range(m))
    l_diag = tuple(i for i in range(1, d))

    inv_sqrt2 = 1/np.sqrt(2)
    Lambda = np.zeros((d**2, d, d), dtype=complex)
    Lambda[0] = np.eye(d)/np.sqrt(d)
    # First n matrices are symmetric
    Lambda[sym_rng, j_offdiag, k_offdiag] = inv_sqrt2
    Lambda[sym_rng, k_offdiag, j_offdiag] = inv_sqrt2
    # Second n matrices are antisymmetric
    Lambda[sym_rng+n_sym, j_offdiag, k_offdiag] = -1j*inv_sqrt2
    Lambda[sym_rng+n_sym, k_offdiag, j_offdiag] = 1j*inv_sqrt2
    # Remaining matrices have entries on the diagonal only
    Lambda[np.repeat(diag_rng, diag_rng)+2*n_sym, j_diag, j_diag] = 1
    Lambda[diag_rng + 2*n_sym, l_diag, l_diag] = -diag_rng
    # Normalize
    Lambda[2*n_sym + 1:, range(d), range(d)] /= np.tile(
        np.sqrt(diag_rng*(diag_rng + 1))[:, None], (1, d)
    )

    return Lambda


def unitary_to_rotation(U: np.ndarray) -> st.Rotation:
    """Convert a unitary operator to a scipy Rotation instance."""
    PTM = channel_to_liouville(apply_channel_unitary, pauli_basis(1), U)
    return st.Rotation.from_matrix(PTM[1:, 1:])


def apply_channel_unitary(rho, U):
    """Apply a unitary quantum channel to an input state rho."""
    return U @ rho @ U.conj().swapaxes(-2, -1)


def apply_channel_kraus(rho, K):
    """Apply the Kraus representation of a channel to the operator rho.

    Parameters
    ----------
    rho: ndarray, shape (d, d)
        The density operator going through the channel.
    K: ndarray, shape (..., n, d, d)
        The n Kraus operators of the channel.

    Returns
    -------
    rhop: ndarray, shape (d, d)
        The output density operator of the channel.

    """
    return (K @ rho @ K.conj().swapaxes(-2, -1)).sum(axis=-3)


def apply_channel_chi(rho, chi):
    """Apply the Chi matrix representation of a channel to the operator rho.

    Parameters
    ----------
    rho: ndarray, shape (d, d)
        The density operator going through the channel.
    chi: ndarray, shape (d**2, d**2)
        The chi matrix of the channel.

    Returns
    -------
    rhop: ndarray, shape (d, d)
        The output density operator of the channel.

    """
    n = int(np.log2(rho.shape[0]))
    sigma = pauli_basis(n)
    rhop = np.einsum('jk,jab,bc,kcd', chi, sigma, rho, sigma)
    return rhop


def apply_channel_liouville(rho, U, basis):
    """Apply the Liouville representation of a channel U to the operator rho.

    Parameters
    ----------
    rho: ndarray, shape (d, d)
        The density operator going through the channel.
    U: ndarray, shape (d**2, d**2)
        The Liouville representation of the channel.
    basis: ndarray, shape (d**2, d, d)
        The operator basis defining the Liouville representation.

    Returns
    -------
    rhop: ndarray, shape (d, d)
        The output density operator of the channel.

    """
    rhoket = np.tensordot(rho, basis, axes=[(-2, -1), (-1, -2)])
    rhoketp = U @ rhoket
    rhop = np.tensordot(rhoketp, basis, axes=[-1, 0])
    return rhop


def kraus_to_chi(K):
    """Convert from Kraus to chi matrix representation.

    Parameters
    ----------
    K: ndarray, shape (..., d, d)
        The Kraus operators.

    Returns
    -------
    chi: ndarray, shape (d**2, d**2)
        The chi (process) matrix.

    """
    n = int(np.log2(K.shape[-1]))
    sigma = pauli_basis(n)
    a_ij = np.einsum('iab,jba', K, sigma)
    chi = (a_ij.conj().T @ a_ij).T
    return chi


def convert_chi_liouville(chi_or_liouville, basis):
    """Convert from chi to Liouville representation and back.

    Parameters
    ----------
    chi_or_liouville: ndarray, shape (d**2, d**2)
        The chi (process) matrix.
    basis: ndarray, shape (d**2, d, d)
        The operator basis defining the Liouville / chi representations.

    Returns
    -------
    U: ndarray, shape (d**2, d**2)
        The converted channel.

    """
    traces = np.einsum('iab,jbc,kcd,lda', *[basis]*4)
    U = np.einsum('kl,ikjl', chi_or_liouville, traces)
    return U


def kraus_to_liouville(K, basis):
    """Convert from Kraus to Liouville representation.

    Parameters
    ----------
    K: ndarray, shape (..., d, d)
        The Kraus operators.
    basis: ndarray, shape (d**2, d, d)
        The operator basis defining the Liouville representation.

    Returns
    -------
    U: ndarray, shape (d**2, d**2)
        The Liouville representation.

    """
    U = np.einsum('iab,kbc,jcd,kad', basis, K, basis, K.conj())
    return U


def chi_to_choi(superoperator: np.ndarray, basis: np.ndarray):
    r"""Transform from Chi matrix to Choi matrix representation.

    Parameters
    ----------
    superoperator: array_like, shape (..., d**2, d**2)
        The superoperator to be transformed.
    basis: ndarray, shape (d**2, d, d)
        The basis defining the representation.

    Returns
    -------
    transformed: ndarray, shape (..., d**2, d**2)
        The transformed superoperator.

    Notes
    -----
    The transformation is given by

    .. math::

        \mathrm{choi}(\chi) = \mathcal{C}^T\chi\mathcal{C}

    with :math:`\mathcal{C}` the basis reshaped as a :math:`d^2\times
    d^2` matrix.
    """
    C = basis.reshape(superoperator.shape)
    choi = C.T @ superoperator @ C
    return choi


def choi_to_kraus(choi: np.ndarray):
    r"""Compute Kraus operators for a given Choi matrix.

    Parameters
    ----------
    choi: ndarray, shape (..., d**2, d**2)
        The choi matrix representation of a completely positive quantum
        map.

    Returns
    -------
    kraus: ndarray, shape (..., d**2, d, d)
        The Kraus operators of the quantum channel (completely positive
        map) represented by choi.

    Notes
    -----
    The Kraus (operator-sum) representation of a quantum channel
    :math:`\mathcal{S}` is given by

    .. math::

        \mathcal{S}(\bullet) = \sum_i A_i\bullet A_i^\dagger.

    The Kraus operators are obtained from the eigendecomposition of the
    Choi operator through the isomorphism

    .. math::

        A_i\simeq\sqrt{\lambda_i} v_i

    where :math:`\lambda_i, v_i` are the eigenvalues and -vectors of
    the Choi operator, respectively.
    """
    d2 = choi.shape[-1]
    d = int(np.sqrt(d2))
    outshape = choi.shape[:-1] + (d, d)

    eigvals, eigvecs = np.linalg.eigh(choi)
    kraus = np.sqrt(eigvals)[..., None, None] * eigvecs.T.reshape(outshape, order='F')
    return kraus


def choi_to_generalized_kraus(choi: np.ndarray):
    r"""Compute generalized Kraus operators for a given Choi matrix.

    Parameters
    ----------
    choi: ndarray, shape (..., d**2, d**2)
        The choi matrix representation of a (not necessarily completely
        positive) quantum map.

    Returns
    -------
    kraus_left, kraus_right: ndarray, shapes (d**2, d, d)
        The left and right generalized Kraus operators.

    Notes
    -----
    The map represented by the choi matrix
    :math:`\mathrm{choi}(\mathcal{S})` is decomposed into left and right
    generalized Kraus operators as

    .. math::

        \mathrm{choi}(\mathcal{S}) = \sum_i A_i\bullet B_i^\dagger,

    by decomposing :math:`\mathrm{choi}(\mathcal{S}) = U\Sigma
    V^\dagger` using singular value decomposition. Then there exists an
    ismorophism between left and right generalized Kraus operators and
    the SVD:

    .. math::

        A_i &\simeq \sqrt{\Sigma_i} U_i \\
        B_i &\simeq \sqrt{\Sigma_i} V_i.
    """
    d2 = choi.shape[-1]
    d = int(np.sqrt(d2))
    outshape = choi.shape[:-1] + (d, d)

    U, S, Vh = np.linalg.svd(choi, hermitian=True)

    sqrt_S = np.sqrt(S)
    kraus_left = sqrt_S[..., None, None] * U.T.reshape(outshape, order='F')
    kraus_right = sqrt_S[..., None, None] * Vh.conj().reshape(outshape, order='F')

    return kraus_left, kraus_right


def choi_to_liouville(superoperator: np.ndarray, basis: np.ndarray):
    r"""Transform from Choi matrix to Liouville representation.

    Parameters
    ----------
    superoperator: array_like, shape (..., d**2, d**2)
        The superoperator to be transformed.
    basis: Basis, shape (d**2, d, d)
        The basis defining the representation.

    Returns
    -------
    transformed: ndarray, shape (..., d**2, d**2)
        The transformed superoperator.

    Notes
    -----
    The transformation is given by

    .. math::

        \mathcal{S}_{ij} = \mathrm{tr}\left[\mathrm{choi}(\mathcal{S})
                                            (C_j^T\otimes C_i)\right]

    with :math:`C_i` a basis element.
    """
    liouville = np.empty(superoperator.shape, superoperator.dtype)
    for j in range(liouville.shape[-1]):
        liouville[..., j] = np.einsum('...ab,iba', superoperator, linalg.tensor(basis[j].T, basis))

    return liouville


def liouville_to_choi(U, basis):
    """Convert from Liouville to Choi matrix representation.

    Parameters
    ----------
    U: ndarray, shape (d**2, d**2)
        The Liouville representation.
    basis: ndarray, shape (d**2, d, d)
        The operator basis defining the Liouville representation.

    Returns
    -------
    choi: ndarray, shape (d**2, d**2)
        The Choi matrix of the channel U.

    """
    d2 = U.shape[0]

    try:
        basis_kroned = np.einsum(
            'iab,jcd->ijacbd', basis.transpose(0, 2, 1), basis
        ).reshape(d2, d2, d2, d2)
        choi = np.tensordot(U, basis_kroned, axes=[(0, 1), (1, 0)])
    except MemoryError:
        basis_kroned = np.empty((d2, d2, d2), dtype=complex)
        choi = np.empty((d2, d2), dtype=complex)
        for i in range(d2):
            basis_kroned = np.einsum(
                'ab,jcd->ijacbd', basis[i].transpose(0, 2, 1), basis,
                out=basis_kroned
            ).reshape(d2, d2, d2)
            choi[i] = np.tensordot(U, basis_kroned, axes=[(0, 1), (1, 0)])

    choi /= np.sqrt(d2)
    return choi


def channel_to_choi(U: Callable, d: int, *args, **kwargs):
    """Convert a channel U to the Choi representation.

    Parameters
    ----------
    U: Callable
        Callable that takes an operator as input and returns another operator.
    d: int
        Dimension of the Hilbert space.
    *args, **kwargs: Additional arguments passed through to U.

    Returns
    -------
    choi: ndarray, shape (d**2, d**2)
        The Choi matrix of the channel U.

    """
    eye = np.eye(d)
    choi = np.zeros((d**2, d**2), dtype=complex)
    for i in range(d):
        for j in range(d):
            ij = linalg.tensor(eye[:, i:i+1], eye[j:j+1])
            choi += linalg.tensor(ij, U(ij, *args, **kwargs))

    choi /= d
    return choi


def channel_to_liouville(U: Callable, basis: np.ndarray, *args, **kwargs):
    """Convert a channel U to the Liouville representation.

    Parameters
    ----------
    U: Callable
        Callable that takes an operator as input and returns another operator.
    basis: ndarray, shape (d**2, d, d)
        Orthonormal basis for the Hilbert space.
    *args, **kwargs: Additional arguments passed through to U.

    Returns
    -------
    choi: ndarray, shape (d**2, d**2)
        The Liouville representation matrix of the channel U.

    """
    try:
        basis_through_channel = U(basis, *args, **kwargs)
    except Exception:
        # Maybe broadcasting doesn't work with U
        try:
            first = U(basis[0], *args, **kwargs)
            basis_through_channel = np.zeros(first.shape[:-2] + basis.shape, basis.dtype)
            basis_through_channel[..., 0, :, :] = first
            for i, C in enumerate(basis[1:], start=1):
                basis_through_channel[..., i, :, :] = U(C, *args, **kwargs)
        except Exception as error:
            raise ValueError("Couldn't apply channel to basis") from error

    return np.einsum('aij,...bji->...ab', basis, basis_through_channel).real
