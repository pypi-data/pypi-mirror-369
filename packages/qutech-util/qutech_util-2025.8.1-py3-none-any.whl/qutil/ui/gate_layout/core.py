"""
Created on Mon Apr 25 11:14:02 2022

@author: Hangleiter
"""
import logging
import pathlib
import warnings
from itertools import compress
from typing import Dict, Union

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

try:
    import ezdxf
    from ezdxf import recover
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from ezdxf.addons.drawing.properties import LayoutProperties
except ImportError:
    ezdxf = None

DEFAULT_TEXT_KWARGS = dict(backgroundcolor='black',
                           horizontalalignment='center',
                           verticalalignment='center',
                           color='white', fontsize=8)
LOG = logging.getLogger(__name__)


class GateLayout:
    def __init__(self, layout_file=None, gate_names=None, gate_mask=None,
                 background_color='#ffffff', foreground_color='tab:gray', cmap='hot', v_min=-2,
                 v_max=0, explode_factor=0.1, fignum=998, text_kwargs=None, offset=(0., 0.)):

        if ezdxf is None:
            raise RuntimeError('Could not import ezdxf which is required to read DXF files.')

        if layout_file is None:
            layout_file = (pathlib.Path(r'\\janeway\User AG Bluhm\Hangleiter\Devices\gl_005d')
                           / 'gl_005d.dxf')

        if gate_names is None:
            gate_names = ['LT', 'LP', 'LB', 'PA', 'TAB', 'PB', 'TBC', 'PC', 'TCD', 'PD', 'RB',
                          'RP', 'RT', 'SD', 'RFD', 'NCD', 'RFC', 'NBC', 'RFB', 'NAB', 'RFA', 'SA']

        if gate_mask is None:
            gate_mask = [True]*14 + [False, True, False, True, False, True, False, True]

        if len(gate_names) != len(gate_mask):
            warnings.warn("Gate name number is different from gate mask number: "
                          f"{len(gate_names)} != {len(gate_mask)}", stacklevel=2)

        self.fig = plt.figure(fignum)
        self.fig.clear()
        self.ax = self.fig.subplots()
        self.layout_file = layout_file
        self.gate_names = gate_names
        self.gate_mask = gate_mask
        self.explode_factor = explode_factor

        self.background_color = matplotlib.colors.to_hex(background_color)
        self.foreground_color = matplotlib.colors.to_hex(foreground_color)
        self.cmap = matplotlib.colormaps.get_cmap(cmap)
        self.norm = matplotlib.colors.Normalize(v_min, v_max)
        self.v_min = self.norm.vmin
        self.v_max = self.norm.vmax
        self.text_kwargs = {**DEFAULT_TEXT_KWARGS, **(text_kwargs or {})}

        self._latest_voltages = np.zeros(len(self.gate_names))
        self._offset = np.array(offset)

        self.patch_collection, self.patches, self.texts = self._setup_figure()

    def __call__(self):
        self.update()

    def __repr__(self):
        self.__call__()
        return super().__repr__()

    def update(self, voltages: Union[np.ndarray, dict[str, float]] = None, force: bool = False):
        """Update the displayed voltages.

        Parameters
        ----------
        voltages: Union[np.ndarray, Mapping[str, float]], optional
            Either an array_like with all voltages that are displayed,
            or a dict with structure {gate_name: voltage}. If None,
            voltages are obtained from :meth:`get_voltages` that can be
            overridden by subclasses.
        force: bool, optional
            Force an update by querying the instruments. Otherwise
            values are obtained from cache. Passed along to
            :meth:`get_voltages`.

        """
        # Masked gates are displayed as 0.
        if voltages is None:
            self.get_voltages(force)
        elif isinstance(voltages, dict):
            for gate, voltage in voltages.items():
                try:
                    self._latest_voltages[self.gate_names.index(gate)] = voltage
                except ValueError:
                    LOG.warning(f'Gate not found. Skipping: {gate}')
        else:
            self._latest_voltages[:] = np.broadcast_to(voltages, self._latest_voltages.shape)

        # Here we update the voltages
        self.patch_collection.set_array(self._latest_voltages)

        # Here we update the texts
        for i, (text, gate, volt) in enumerate(
                compress(zip(self.texts, self.gate_names, self._latest_voltages), self.gate_mask)
        ):
            text.set_text(f'{i}: {gate}\n{volt:.3f}')

    def get_voltages(self, force: bool = False):
        return self._latest_voltages

    def _setup_figure(self):
        vertices = get_vertices_from_dfx(self.layout_file, self.background_color,
                                         self.foreground_color)
        if len(self.gate_names) != len(vertices):
            warnings.warn(f"Found {len(vertices)} patches in file but got {len(self.gate_names)} "
                          "gate names", stacklevel=2)

        patches = []
        texts = []
        for idx, verts in enumerate(vertices):
            verts += self._offset[None, :]
            patches.append(matplotlib.patches.Polygon(verts, closed=True, zorder=0))
            texts.append(matplotlib.text.Text(*verts.mean(axis=0), 'INIT', **self.text_kwargs))

        all_coords = np.array([(patch.get_xy().mean(axis=0)) for patch in patches])

        # Order everything by angle around the center of mass
        angles = np.angle((all_coords - all_coords.mean(axis=0)).view(complex))
        texts = [text for _, text in sorted(zip(angles.flat, texts))]
        patches = [patch for _, patch in sorted(zip(angles.flat, patches))]

        # redraw everything
        self.ax.cla()

        pc = matplotlib.collections.PatchCollection(patches, norm=self.norm, cmap=self.cmap)
        pc.set_edgecolors('tab:gray')
        self.ax.add_collection(pc)

        for i, txt in enumerate(texts):
            # shift every other text by given percentage up or down to decrowd
            xpos, ypos = txt.get_position()
            txt.set_y(ypos*(1 + self.explode_factor*(-1)**(i % 2)))

            try:
                name = self.gate_names[i]
            except IndexError:
                name = f'Unknown {i}'

            txt.set_text(f'{name}: NaN')
            self.ax.add_artist(txt)
        self.ax.autoscale_view(True)
        return pc, patches, texts


def get_vertices_from_dfx(file_name, background_color, foreground_color, vert_drop=0.01):
    # Safe loading procedure (requires ezdxf v0.14):
    try:
        doc, auditor = recover.readfile(file_name)
    except OSError as ioe:
        raise OSError('Not a DXF file or a generic I/O error.') from ioe
    except ezdxf.DXFStructureError as e:
        raise RuntimeError('Invalid or corrupted DXF file.') from e

    tmp_fig = plt.figure(visible=False)
    tmp_ax = tmp_fig.add_axes([0, 0, 1, 1])
    tmp_fig.set_visible(False)

    vertices = []

    # ezdxf is very object-bloated. No clue how to get to coordinates.
    # Therefore we extract vertices from drawn artists
    try:
        ctx = RenderContext(doc)
        out = MatplotlibBackend(tmp_ax)
        Frontend(ctx, out).draw_layout(
            doc.modelspace(),
            finalize=True,
            layout_properties=LayoutProperties('Ebeam',
                                               background_color,
                                               foreground_color))

        # apply trafo if necessary
        transform = tmp_ax.transData.inverted().transform
        for child in tmp_ax.get_children():
            if isinstance(child, matplotlib.patches.PathPatch):
                verts = transform(child.get_verts())
                # Drop vertices that are less than 1% apart
                # Last vertex is the first
                verts = np.vstack(
                    [verts[1:][np.linalg.norm(np.diff(verts, axis=0), axis=1) >= vert_drop],
                     verts[-1]]
                )
                vertices.append(verts)
    finally:
        plt.close(tmp_fig)
    return vertices
