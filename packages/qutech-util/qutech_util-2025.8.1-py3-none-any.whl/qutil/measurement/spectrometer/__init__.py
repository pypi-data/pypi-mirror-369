import warnings

try:
    from python_spectrometer import Spectrometer as Spectrometer
    from python_spectrometer import daq as daq
    warnings.warn('The spectrometer module has moved to its own package and is now called '
                  "'python_spectrometer'. Please update your imports accordingly.",
                  DeprecationWarning)
except ImportError:
    url = 'https://git.rwth-aachen.de/qutech/python-spectrometer'
    warnings.warn(f'The spectrometer module has moved to its own package at {url}. You can "'
                  "install it from there or from pypi via 'pip install python-spectrometer'",
                  # UserWarning so that it isn't suppress by most defaults:
                  # https://docs.python.org/3/library/exceptions.html#ImportWarning
                  UserWarning)
    raise

del warnings
