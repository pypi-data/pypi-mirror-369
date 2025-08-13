"""This module contains some useful plotting functions.

Moreoever, there are custom stylefiles defined in the ``stylelib``
subdir. You can employ these globally by calling::

    plt.style.use('qutil.plotting.<stylename>')

or within a context::

    with plt.style.context('qutil.plotting.<stylename>'):
        ...

Note that this requires ``matplotlib>=3.7.0``. If you don't want to
upgrade, you can also copy the style files to
``matplotlib.get_configdir()/stylelib``.

Examples
--------
Note that this syntax requires ``matplotlib>=3.7.0``.

Plot data using a style adjusted to APS journals:

>>> import matplotlib.pyplot as plt
>>> with plt.style.context('qutil.plotting.publication_aps_tex'):
...    plt.plot([1, 2], [3, 4], label='presentation style')
...    plt.legend()
...    plt.show(block=False)
[...

Plot data using all available custom styles:

>>> import pathlib, qutil
>>> module_path = pathlib.Path(qutil.__file__).parent
>>> for file in (module_path / 'plotting').glob('*.mplstyle'):
...     file = file.relative_to(module_path)
...     style = '.'.join(('qutil',) + file.parent.parts + (file.stem,))
...     with plt.style.context(style):
...         plt.plot([1, 2], [3, 4])
...         plt.title(file.stem)
...         plt.show(block=False)
[...

The official RWTH corporate design colors are exported as matplotlib
color cycles and also registered as colormaps and color sequences.
Because of the lazy loading mechanism, the :mod:`qutil.plotting.colors`
module needs to be explicitly imported.

>>> import qutil.plotting.colors
>>> rwth_cycler = qutil.plotting.colors.RWTH_COLOR_CYCLE
>>> rwth_cmap = plt.colormaps['rwth']
>>> rwth_sequence = plt.color_sequences['rwth']
>>> fig, ax = plt.subplots()
>>> for i, style in enumerate(rwth_cycler):  # doctest: +SKIP
...     ax.plot([i-0.1], [0.9], 'o', **style)
...     ax.plot([i+0.0], [1.0], 's', color=rwth_cmap.colors[i])
...     ax.plot([i+0.1], [1.1], 'v', color=rwth_sequence[i])
...

Versions with varying degrees of intensity also exist, e.g.,
``'rwth25'`` for colormaps or sequences and
:const:`.colors.RWTH_COLOR_CYCLE_25`.

The same as above can also be achieved with a style sheet:

>>> from random import random
>>> for intensity in (10, 25, 50, 75, 100):  # doctest: +SKIP
...     with plt.style.context(f'qutil.plotting.rwth_colors{intensity}'):
...         plt.figure()
...         plt.title(f'Intensity {intensity}')
...         for i in range(12):
...             plt.scatter(random(), random())

"""

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)

del lazy
