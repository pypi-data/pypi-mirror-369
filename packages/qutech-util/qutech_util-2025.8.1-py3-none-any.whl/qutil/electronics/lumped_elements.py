"""Exposes fastz under a nicer name."""
import importlib

import fastz
import numpy as np

_REEXPORTED_CLASSES = [
    'R',
    'C',
    'L',
    'Z',
    'SeriesZ',
    'ParallelZ',
    'LumpedElement',
]

# we do this instead of 'from tikz import ...' to
#  1. avoid duplication with __all__
#  2. make this code work with a mocked fastz
for cls in _REEXPORTED_CLASSES:
    locals()[cls] = getattr(fastz, cls)


__all__ = [
    'fastz',
    'Rv',
] + _REEXPORTED_CLASSES


class Rv(R):
    """Virtual AC input resistance of a TIA."""

    @property
    def prefix(self):
        return 'Rv'

    def __call__(self, ff, **lumpedparam):
        return np.asarray(ff) * self._lookup_value(**lumpedparam)


del cls
del importlib
