from typing import Optional, Tuple

import numpy as np


def _parse_filter_edges(f_min: float, f_max: float,
                        fs: Optional[float] = None, N: Optional[int] = None,
                        f: Optional[np.ndarray] = None) -> tuple[np.ndarray, Optional[str]]:
    if f is not None:
        if np.unique(np.around(np.diff(f), 10)).size == 1:
            # linspaced array
            if fs is None:
                fs = 2*np.max(f)
            if N is None:
                N = f.size

            lb = fs/N
            ub = fs/2
        else:
            # irregular spacing, just look at extremal frequencies
            lb = np.min(f)
            ub = np.max(f)
            fs = 2*ub
    elif fs is not None and N is not None:
        lb = fs/N
        ub = fs/2
    else:
        raise ValueError('Need either f or fs and N not None')

    if f_min <= lb < f_max <= ub:
        btype = 'lowpass'
        cutoff = f_max
    elif lb <= f_min < ub <= f_max:
        btype = 'highpass'
        cutoff = f_min
    elif lb <= f_min < f_max <= ub:
        btype = 'bandpass'
        cutoff = [f_min, f_max]
    elif lb <= f_max < f_min <= ub:
        btype = 'bandstop'
        cutoff = [f_min, f_max]
    elif lb >= f_min < f_max >= ub:
        return np.array([]), None
    else:
        raise ValueError('Require 0 ≤ f_min, f_max ≤ ∞')

    cutoff = np.atleast_1d(cutoff)
    assert ((0 < cutoff) & (cutoff <= (fs or 2) / 2)).all()

    return cutoff, btype
