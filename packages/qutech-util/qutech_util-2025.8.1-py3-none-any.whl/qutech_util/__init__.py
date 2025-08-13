"""This is the new name of the qutil module which is just an alias to qutil for backwards compatibility reasons."""
import sys

import lazy_loader

import qutil

__version__ = qutil.__version__
__all__ = qutil.__all__

for module_name in qutil.__all__:
    globals()[module_name] = lazy_loader.load(f'qutil.{module_name}')

sys.modules[__name__] = qutil

del qutil

del lazy_loader
del sys
