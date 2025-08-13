"""Color and colormap definitions and tools.

The RWTH corporate design things might be replaced by
https://git.rwth-aachen.de/philipp.leibner/rwthcolors. At the moment
though, importing that package automatically sets the matplotlib style
which is too invasive.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import matplotlib as mpl
import numpy as np
from cycler import cycler

from ..misc import filter_warnings

_color_names = ['blue', 'magenta', 'green', 'orange', 'teal', 'maygreen',
                'red', 'purple', 'violet', 'bordeaux', 'petrol', 'yellow',
                'black']

# Lightness 100
_color_tuples_100 = [
    (0 / 255, 84 / 255, 159 / 255),  # blue
    (227 / 255, 0 / 255, 102 / 255),  # magenta
    (87 / 255, 171 / 255, 39 / 255),  # green
    (246 / 255, 168 / 255, 0 / 255),  # orange
    (0 / 255, 152 / 255, 161 / 255),  # teal
    (189 / 255, 205 / 255, 0 / 255),  # maygreen
    (204 / 255, 7 / 255, 30 / 255),  # red
    (97 / 255, 33 / 255, 88 / 255),  # purple
    (122 / 255, 111 / 255, 172 / 255),  # violet
    (161 / 255, 16 / 255, 53 / 255),  # bordeaux
    (0 / 255, 97 / 255, 101 / 255),  # petrol
    (255 / 255, 237 / 255, 0 / 255),  # yellow
    (0 / 255, 0 / 255, 0 / 255),  # black
]

# Lightness 75
_color_tuples_75 = [
    (64 / 255, 127 / 255, 183 / 255),  # blue
    (233 / 255, 96 / 255, 136 / 255),  # magenta
    (141 / 255, 192 / 255, 96 / 255),  # green
    (250 / 255, 190 / 255, 80 / 255),  # orange
    (0 / 255, 177 / 255, 183 / 255),  # teal
    (208 / 255, 217 / 255, 92 / 255),  # maygreen
    (216 / 255, 92 / 255, 65 / 255),  # red
    (131 / 255, 78 / 255, 117 / 255),  # purple
    (155 / 255, 145 / 255, 193 / 255),  # violet
    (182 / 255, 82 / 255, 86 / 255),  # bordeaux
    (45 / 255, 127 / 255, 131 / 255),  # petrol
    (255 / 255, 240 / 255, 85 / 255),  # yellow
    (100 / 255, 101 / 255, 103 / 255),  # black
]

# Lightness 50
_color_tuples_50 = [
    (142 / 255, 186 / 255, 229 / 255),  # blue
    (241 / 255, 158 / 255, 177 / 255),  # magenta
    (184 / 255, 214 / 255, 152 / 255),  # green
    (253 / 255, 212 / 255, 143 / 255),  # orange
    (137 / 255, 204 / 255, 207 / 255),  # teal
    (224 / 255, 230 / 255, 154 / 255),  # maygreen
    (230 / 255, 150 / 255, 121 / 255),  # red
    (168 / 255, 133 / 255, 158 / 255),  # purple
    (188 / 255, 181 / 255, 215 / 255),  # violet
    (205 / 255, 139 / 255, 135 / 255),  # bordeaux
    (125 / 255, 164 / 255, 167 / 255),  # petrol
    (255 / 255, 245 / 255, 155 / 255),  # yellow
    (156 / 255, 158 / 255, 159 / 255),  # black
]

# Lightness 25
_color_tuples_25 = [
    (199 / 255, 221 / 255, 242 / 255),  # blue
    (249 / 255, 210 / 255, 218 / 255),  # magenta
    (221 / 255, 235 / 255, 206 / 255),  # green
    (254 / 255, 234 / 255, 201 / 255),  # orange
    (202 / 255, 231 / 255, 231 / 255),  # teal
    (240 / 255, 243 / 255, 208 / 255),  # maygreen
    (243 / 255, 205 / 255, 187 / 255),  # red
    (210 / 255, 192 / 255, 205 / 255),  # purple
    (222 / 255, 218 / 255, 235 / 255),  # violet
    (229 / 255, 197 / 255, 192 / 255),  # bordeaux
    (191 / 255, 208 / 255, 209 / 255),  # petrol
    (255 / 255, 250 / 255, 209 / 255),  # yellow
    (207 / 255, 209 / 255, 210 / 255),  # black
]

# Lightness 10
_color_tuples_10 = [
    (232 / 255, 241 / 255, 250 / 255),  # blue
    (253 / 255, 238 / 255, 240 / 255),  # magenta
    (242 / 255, 247 / 255, 236 / 255),  # green
    (255 / 255, 247 / 255, 234 / 255),  # orange
    (235 / 255, 246 / 255, 246 / 255),  # teal
    (249 / 255, 250 / 255, 237 / 255),  # maygreen
    (250 / 255, 235 / 255, 227 / 255),  # red
    (237 / 255, 229 / 255, 234 / 255),  # purple
    (242 / 255, 240 / 255, 247 / 255),  # violet
    (245 / 255, 232 / 255, 229 / 255),  # bordeaux
    (230 / 255, 236 / 255, 236 / 255),  # petrol
    (255 / 255, 253 / 255, 238 / 255),  # yellow
    (236 / 255, 237 / 255, 237 / 255),  # black
]

RWTH_COLORS_100 = RWTH_COLORS = dict(zip(_color_names, _color_tuples_100))
RWTH_COLORS_75 = dict(zip(_color_names, _color_tuples_75))
RWTH_COLORS_50 = dict(zip(_color_names, _color_tuples_50))
RWTH_COLORS_25 = dict(zip(_color_names, _color_tuples_25))
RWTH_COLORS_10 = dict(zip(_color_names, _color_tuples_10))


def get_rwth_color_cycle(intensity: Literal[10, 25, 50, 75, 100], alpha: float = 1,
                         exclude: Sequence[str] = None):
    """Get the default RWTH color cycle with an alpha channel.

    Parameters
    ----------
    intensity :
        The color intensity. One of 10, 25, 50, 75, 100.
    alpha : float
        The alpha (transparency) value for the color cycle.
    exclude : sequence of str
        Exclude these colors. See RWTH_COLORS for all available keys.
        Yellow is a good choice to exclude.

    Example
    -------
    >>> import matplotlib.pyplot as plt
    >>> cycle_100 = get_rwth_color_cycle(100)
    >>> cycle_50 = get_rwth_color_cycle(50)
    >>> x = np.linspace(0, 2*np.pi, 51)
    >>> fig, ax = plt.subplots()
    >>> for i, (v100, v50) in enumerate(zip(cycle_100, cycle_50)):  # doctest: +SKIP
    ...     ax.plot(x, np.sin(x) + i / len(cycle_100), lw=2, **v100)
    ...     ax.plot(x, -np.sin(x) + i / len(cycle_50), lw=2, **v50)

    See Also
    --------
    https://matplotlib.org/stable/tutorials/intermediate/color_cycle.html

    https://matplotlib.org/cycler/
    """
    if intensity not in {10, 25, 50, 75, 100}:
        raise ValueError("Intensity should be one of {10, 25, 50, 75, 100}")
    if alpha < 0 or alpha > 1:
        raise ValueError('alpha should be in the range [0, 1].')

    exclude = exclude or []
    return cycler(
        color=[tup + (alpha,) for name, tup in globals().get(f'RWTH_COLORS_{intensity}').items()
               if name not in exclude]
    )


def make_sequential_colormap(
        color: str | tuple[float, ...], name: str | None = None,
        endpoint: Literal['black', 'white', 'blackwhite'] = 'white'
) -> mpl.colors.ListedColormap:
    """Generate a sequential colormap for *color*.

    Converts the color to the CAM02-UCS color space and interpolates
    the lightness linearly from completely dark or to completely light.

    Parameters
    ----------
    color :
        Either a rgb color tuple or a key of :attr:`RWTH_COLORS` or
        :attr:`~matplotlib:matplotlib.colors.cnames`.
    name :
        A name for the colormap. Default is automatic.
    endpoint :
        The endpoint of the colormap. If 'blackwhite', the colormap
        interpolates from black to *color* to white.
        Does not always seem to work.

    Returns
    -------
    cmap :
        The :class:`matplotlib:~matplotlib.colors.ListedColormap`.

    Examples
    --------
    Show the lightness of all colormaps generated from the base RWTH
    colors. Code partially adapted from
    https://matplotlib.org/stable/users/explain/colors/colormaps.html.


    >>> import matplotlib.pyplot as plt
    >>> from colorspacious import cspace_convert

    >>> def plot(cmaps):
    ...     locs = []
    ...     names = []
    ...     x = np.linspace(0.0, 1.0, 100)
    ...     fig, ax = plt.subplots()
    ...     for i, cmap in enumerate(cmaps):
    ...         rgb = cmap(x)[np.newaxis, :, :3]
    ...         lab = cspace_convert(rgb, "sRGB1", "CAM02-UCS")
    ...         names.append(cmap.name)
    ...         locs.append(i * 1.6)
    ...         ax.scatter(x + locs[-1], lab[0, :, 0], c=x, cmap=cmap,
    ...                    s=300, linewidths=0.0)
    ...         ax.set_ylim(0, 100)
    ...         ax.set_ylabel('$L^*$')
    ...         ax.set_xlabel('Sequential RWTH base colormaps')
    ...         # Set up labels for colormaps
    ...         ax.xaxis.set_ticks_position('top')
    ...         ticker = mpl.ticker.FixedLocator(locs)
    ...         ax.xaxis.set_major_locator(ticker)
    ...         formatter = mpl.ticker.FixedFormatter(names)
    ...         ax.xaxis.set_major_formatter(formatter)
    ...         ax.xaxis.set_tick_params(rotation=50)

    Colormaps going to the light end of the spectrum:

    >>> plot([make_sequential_colormap(c, endpoint='white') for c in RWTH_COLORS])

    Colormaps going to the dark end of the spectrum:

    >>> with np.errstate(divide='ignore'):
    ...     plot([make_sequential_colormap(c, endpoint='black') for c in RWTH_COLORS
    ...           if c != 'black'])

    Colormaps going from black to white:

    >>> with np.errstate(divide='ignore'):
    ...     plot([make_sequential_colormap(c, endpoint='blackwhite') for c in RWTH_COLORS
    ...           if c != 'black'])

    """
    colors_rgb, color_names = _make_color_gradient([color], name, endpoint)
    if name is None:
        name = color_names[0]
    return mpl.colors.ListedColormap(colors_rgb[0], name)


def make_diverging_colormap(
        colors: tuple[str | tuple[float, ...], str | tuple[float, ...]], name: str | None = None,
        endpoint: Literal['black', 'white', 'blackwhite'] = 'white'
) -> mpl.colors.ListedColormap:
    """Generate a diverging colormap from ``colors[0]`` to ``colors[1]``.

    Converts the colors to the CAM02-UCS color space and interpolates
    the lightness linearly from completely dark or to completely light.

    """
    colors_rgb, color_names = _make_color_gradient(colors, name, endpoint)
    if name is None:
        name = '_'.join(color_names)
    return mpl.colors.ListedColormap(np.concatenate([colors_rgb[0], colors_rgb[1][::-1]]), name)


def _make_color_gradient(colors: tuple[str | tuple[float, ...], ...], name: str | None = None,
                         endpoint: Literal['black', 'white', 'blackwhite'] = 'white'):
    try:
        from colorspacious import cspace_convert
    except ImportError:
        raise ImportError('This function requires the colorspacious package.')

    def normalize(c, start=None, stop=None):
        v0, v1 = c[[0, -1]]
        if start is None:
            start = v0
        if stop is None:
            stop = v1
        return (c - start) * (stop - start) / (v1 - v0) + start

    colors_rgb = []
    color_names = []
    for i, color in enumerate(colors):
        if isinstance(color, str):
            if color in RWTH_COLORS:
                color_rgb = RWTH_COLORS[color]
                color_names.append(f'rwth_{color}s')
            elif color in mpl.colors.cnames:
                color_rgb = mpl.colors.cnames[color]
                color_names.append(f'{color}s')
            else:
                raise ValueError("Not an RWTH color or a valid matplotlib color name.")
        else:
            color_rgb = color
            color_names.append('')

        # three-tuple of "J" (for lightness), "C" (for chroma), and "h" (for hue)
        # https://colorspacious.readthedocs.io/en/latest/tutorial.html#perceptual-transformations
        color_jch = cspace_convert(color_rgb, 'sRGB1', 'CAM02-UCS')
        L_mid = color_jch[0]
        N = 256 // len(colors)
        if endpoint == 'blackwhite':
            Ls = (np.linspace(0, L_mid, round(L_mid / 100 * N) + 1, endpoint=False),
                  np.linspace(L_mid, 100, round((1 - L_mid / 100) * N)))
            cs = (
                normalize(
                    cspace_convert([(L, *color_jch[1:]) for L in Ls[0]], 'CAM02-UCS', 'sRGB1'),
                    start=0, stop=None
                ),
                normalize(
                    cspace_convert([(L, *color_jch[1:]) for L in Ls[1]], 'CAM02-UCS', 'sRGB1'),
                    start=None, stop=1
                ),
            )
            colors_rgb.append(np.concatenate(cs))
            continue
        elif endpoint == 'black':
            Ls = np.linspace(L_mid, 0, N)
        elif endpoint == 'white':
            Ls = np.linspace(L_mid, 100, N)
        else:
            raise ValueError("endpoint should be 'white', 'black', or 'blackwhite'")

        colors_rgb.append(normalize(
            cspace_convert([(L, *color_jch[1:]) for L in Ls], 'CAM02-UCS', 'sRGB1'),
            start=None, stop=int(endpoint == 'white')
        ))

    return np.clip(colors_rgb, 0, 1), color_names


RWTH_COLOR_CYCLE_10 = get_rwth_color_cycle(10)
RWTH_COLOR_CYCLE_25 = get_rwth_color_cycle(25)
RWTH_COLOR_CYCLE_50 = get_rwth_color_cycle(50)
RWTH_COLOR_CYCLE_75 = get_rwth_color_cycle(75)
RWTH_COLOR_CYCLE_100 = get_rwth_color_cycle(100)
RWTH_COLOR_CYCLE = RWTH_COLOR_CYCLE_100

with filter_warnings(action='ignore', category=UserWarning):
    # autoreload might trigger a UserWarning about the sequence being already defined
    mpl.color_sequences.register('rwth10', RWTH_COLOR_CYCLE_10.by_key()['color'])
    mpl.color_sequences.register('rwth25', RWTH_COLOR_CYCLE_25.by_key()['color'])
    mpl.color_sequences.register('rwth50', RWTH_COLOR_CYCLE_50.by_key()['color'])
    mpl.color_sequences.register('rwth75', RWTH_COLOR_CYCLE_75.by_key()['color'])
    mpl.color_sequences.register('rwth100', RWTH_COLOR_CYCLE_100.by_key()['color'])
    mpl.color_sequences.register('rwth', RWTH_COLOR_CYCLE.by_key()['color'])

    mpl.colormaps.register(mpl.colors.ListedColormap(mpl.color_sequences['rwth10'], 'rwth10'),
                           force=True)
    mpl.colormaps.register(mpl.colors.ListedColormap(mpl.color_sequences['rwth25'], 'rwth25'),
                           force=True)
    mpl.colormaps.register(mpl.colors.ListedColormap(mpl.color_sequences['rwth50'], 'rwth50'),
                           force=True)
    mpl.colormaps.register(mpl.colors.ListedColormap(mpl.color_sequences['rwth75'], 'rwth75'),
                           force=True)
    mpl.colormaps.register(mpl.colors.ListedColormap(mpl.color_sequences['rwth100'], 'rwth100'),
                           force=True)
    mpl.colormaps.register(mpl.colors.ListedColormap(mpl.color_sequences['rwth'], 'rwth'),
                           force=True)
