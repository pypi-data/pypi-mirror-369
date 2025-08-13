"""
This module contains random functions
"""
import numpy as np
from numpy import ndarray


def random_hermitian(d: int = 2, n: int = 1, std: float = 1,
                     mean: float = 0) -> ndarray:
    r"""
    Generate *n* random Hermitian matrices of dimension *d* drawn from a
    Gaussian ensemble :math:`~\mathcal{N}(\mu, \sigma^2)`.
    """
    H = np.random.randn(n, d, d)*(1 + 1j)*std/2
    H += H.conj().swapaxes(1, 2)
    return H.squeeze() + mean
