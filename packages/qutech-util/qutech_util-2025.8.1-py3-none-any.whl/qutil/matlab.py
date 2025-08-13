"""This module contains utility functions that help interacting with matlab and matlab files"""
import array
import dataclasses
import datetime
import itertools
import json
import os
import pathlib
import re
import warnings
from collections.abc import Sequence
from typing import Any, List, Literal, Optional, Tuple, Union

import hdf5storage
import numpy as np
import pandas as pd
import xarray as xr

import qutil.caching

SM_DATE_FORMAT = '%Y_%m_%d_%H_%M_%S'
SM_DATE_REGEX = re.compile(r'(\d\d\d\d(?:_\d\d){5})')

try:
    import matlab.engine

    try:
        # legacy version shipped with old MATLAB installations
        from matlab import mlarray
    except ImportError:
        # pypi version
        mlarray = None

except (ImportError, OSError):
    warnings.warn("Matlab engine  interface not installed. "
                  "Some functionality requires using MATLAB directly.\n"
                  "If you are using the newest MATLAB you can install it directly from pypi via "
                  "'python -m pip install matlabengine'.\n"
                  r"For older MATLAB versions, navigate to "
                  r"'C:\Program Files\MATLAB\$YOUR_VERSION$\extern\engines\python' and execute "
                  r"'python setup.py install'.",
                  category=ImportWarning)
    matlab = None
    mlarray = None

__all_ = ['load_special_measure_scan', 'cached_load_mat_file', 'special_measure_to_dataframe',
          'load_special_measure_with_matlab_engine', 'mlarray_to_numpy']


if mlarray is not None:
    DTYPE_TO_MLARRAY = {
        np.dtype('float64'): mlarray.double
    }
elif matlab is not None and mlarray is None:  # matlab.mlarray deprecated for versions > 2021a
    DTYPE_TO_MLARRAY = {
        np.dtype('float64'): matlab.double
    }

def mlarray_to_numpy(d) -> np.ndarray:
    """Converts a mlarray (matlab engine array) into a readable numpy array in an efficient manner if possible.

    Calling np.asarray(your_matlab_array) is very slow because mlarray does not implement the buffer protocol.
    This function utilizes the internal private representation if possible
    """
    try:
        data = d._data
        strides = d._strides
        shape = d._size
        item_size = data.itemsize

        return np.lib.stride_tricks.as_strided(
            data,
            shape=shape, strides=[s * item_size for s in strides], writeable=False
        )

    except AttributeError:
        # slow fallback
        return np.asarray(d)


def numpy_to_mlarray(a: np.ndarray):
    mf_type = DTYPE_TO_MLARRAY[a.dtype]
    try:
        d = mf_type(size=a.shape)
        d._data = array.array(d._data.typecode, a.tobytes(order='F'))
        return d
    except AttributeError:
        # fallback
        return mf_type(initializer=a.tolist())


class ModuleEngineWrapper:
    """The purpose of this class is to be a default argument for engine requiring functions different from None.
     This is the least stupid default interface I came up with (Simon)."""
    ENGINE = None

    @classmethod
    def get_engine(cls):
        if cls.ENGINE is None:
            cls.ENGINE = matlab.engine.connect_matlab()
        return cls.ENGINE

    @staticmethod
    def to_engine(obj) -> 'matlab.engine.MatlabEngine':
        if isinstance(obj, str):
            return matlab.engine.connect_matlab(name=obj)
        elif obj is None:
            print('Connecting to (and maybe starting) MATLAB')
            return matlab.engine.connect_matlab()
        elif isinstance(obj, matlab.engine.MatlabEngine):
            return obj
        else:
            return obj.get_engine()


def read_table(engine, table_path: str) -> pd.DataFrame:
    """Read a table from the given path in the engine namespace and return it
    as a pd.DataFrame."""
    row_names = engine.eval(f'{table_path}.Properties.RowNames')
    col_names = engine.eval(f'{table_path}.Properties.VariableNames')
    values = engine.eval(f'{table_path}.Variables')
    return pd.DataFrame(np.array(values),
                            columns=col_names, index=row_names)


def _has_trafofn(engine, scan_path: str) -> bool:
    return engine.eval(f"isfield({scan_path}.loops, 'trafofn') && "
                       f"any(arrayfun(@(loop) ~isempty(loop.trafofn), {scan_path}.loops))")


def _get_config_channel_values(engine, loaded_path: Optional[str]) -> pd.Series:
    if loaded_path:
        configch = engine.eval(f'{loaded_path}.configch')
        configvals = engine.eval(f'{loaded_path}.configvals')
    else:
        configch = engine.workspace['configch']
        configvals = engine.workspace['configvals']
    return pd.Series(np.array(configvals).ravel(), index=configch)



def _mat_string_to_str(mstring) -> str:
    if isinstance(mstring, str):
        return mstring
    elif isinstance(mstring, list):
        return '\n'.join(str(line) for line in mstring)
    else:
        return str(mstring) if len(mstring) else ''


@dataclasses.dataclass
class PlottedData:
    """Representation of the actually plotted object in a matlab figure. Currently image, text and line are supported.
    """

    plot_type: Literal['image', 'text', 'line']

    x_data: Optional[np.ndarray] = dataclasses.field(default=None)
    y_data: Optional[np.ndarray] = dataclasses.field(default=None)
    c_data: Optional[np.ndarray] = dataclasses.field(default=None)

    line_style: Optional[str] = dataclasses.field(default=None)
    text: Optional[Sequence[str]] = dataclasses.field(default=None)

    @classmethod
    def load_from_path(cls, engine, path: str):
        plot_type = engine.eval(f"{path}.Type", nargout=1).lower()

        kwargs = {}
        if engine.eval(f"isfield({path}, 'CData')"):
            kwargs['c_data'] = mlarray_to_numpy(engine.eval(f"{path}.CData", nargout=1)).astype(float)
        if engine.eval(f"isfield({path}, 'XData')"):
            kwargs['x_data'] = mlarray_to_numpy(engine.eval(f"{path}.CData", nargout=1)).astype(float)
        if engine.eval(f"isfield({path}, 'YData')"):
            kwargs['y_data'] = mlarray_to_numpy(engine.eval(f"{path}.CData", nargout=1)).astype(float)

        if engine.eval(f"isfield({path}, 'String')"):
            kwargs['text'] = _mat_string_to_str(engine.eval(f"{path}.String", nargout=1))

        if engine.eval(f"isfield({path}, 'LineStyle')"):
            kwargs['line_style'] = engine.eval(f"{path}.LineStyle", nargout=1)

        if plot_type not in typing.get_args(cls.plot_type):
            warnings.warn(f"Don't know what {plot_type} is.")
        return cls(plot_type, **kwargs)


@dataclasses.dataclass
class AxesData:
    """Data of an axes object in a matlab plot."""
    title: str
    subtitle: str
    xlim: tuple[float, float]
    ylim: tuple[float, float]
    xlabel: str
    ylabel: str
    xscale: str
    yscale: str

    content: list[PlottedData]

    @classmethod
    def load_from_path(cls, engine, path: str):
        title = _mat_string_to_str(engine.eval(f"{path}.Title.String", nargout=1))
        if engine.eval(f"{path}.Subtitle.String", nargout=1):
            subtitle = _mat_string_to_str(engine.eval(f"{path}.Subtitle.String", nargout=1))
        else:
            subtitle = None
        xlim = tuple(mlarray_to_numpy(engine.eval(f"{path}.XLim", nargout=1)).astype(float).reshape(-1))
        ylim = tuple(mlarray_to_numpy(engine.eval(f"{path}.YLim", nargout=1)).astype(float).reshape(-1))
        xlabel = _mat_string_to_str(engine.eval(f"{path}.XLabel.String", nargout=1))
        ylabel = _mat_string_to_str(engine.eval(f"{path}.YLabel.String", nargout=1))
        xscale = _mat_string_to_str(engine.eval(f"{path}.XScale", nargout=1))
        yscale = _mat_string_to_str(engine.eval(f"{path}.YScale", nargout=1))

        n_children = int(engine.eval(f"length({path}).Children)", nargout=1))
        content = []
        for j in range(n_children):
            child_path = f"{path}.Children({j + 1})"
            child_data = PlottedData.load_from_path(engine, child_path)
            content.append(child_data)

        return cls(title=title, subtitle=subtitle,
                   xlim=xlim, ylim=ylim, xlabel=xlabel, ylabel=ylabel,
                   xscale=xscale, yscale=yscale, content=content)


@dataclasses.dataclass
class FigureData:
    """Data of a matlab figure."""
    name: str
    axes_data: Optional[list[AxesData]]
    user_data: Optional[Any]

    @classmethod
    def load_from_file(cls, file_name: str, engine = ModuleEngineWrapper,
                       fig_path: str = 'loaded_figure',
                       load_axes_data: bool = True,
                       user_data_loader = 'json',
                       user_data_blacklist: Sequence[str] = ()):
        engine = ModuleEngineWrapper.to_engine(engine)


        engine.eval(f"{fig_path} = openfig('{file_name}', 'invisible');", nargout=0)
        name = _mat_string_to_str(f"{fig_path}.Name")
        axes_data = None
        if load_axes_data:
            axes_data = []
            n_axes = n_plots = int(engine.eval(f"length({fig_path}.Children)", nargout=1))
            for ax_idx in range(n_axes):
                ax_data = AxesData.load_from_path(engine, f"{fig_path}.Children({ax_idx + 1})")
                axes_data.append(ax_data)

        user_data = None
        if not user_data_loader:
            pass
        if user_data_loader == 'json':
            user_data = {}
            user_data_fields = list(str(s) for s in engine.eval(f"fieldnames({fig_path}.UserData)'"))
            for fieldname in user_data_fields:
                if fieldname in user_data_blacklist:
                    continue
                try:
                    json_encoded = engine.eval(f'jsonencode({fig_path}.UserData.{fieldname})', nargout=1)
                except Exception as err:
                    warnings.warn(f"Ignoring field '{fieldname}': '{err}'", RuntimeWarning)
                else:
                    value = json.loads(json_encoded)
                    user_data[fieldname] = value
        return cls(name, axes_data=axes_data, user_data=user_data)



def load_data_from_matlab_figure(file_name: os.PathLike,
                                 engine=ModuleEngineWrapper,
                                 with_scan=True):
    """
    Loads data saved in matlab figures

    Args:
        file_name: fig file to load
        engine:
            None, str -> passed to matlab.engine.connect_matlab()
            () -> Use module instance
            MatlabEngine -> used directly

    Returns:
        fig_data
        user_data

    """
    engine = ModuleEngineWrapper.to_engine(engine)

    engine.eval(f"fig = openfig('{file_name}', 'invisible');", nargout=0)
    engine.eval(f"plot = fig.Children;", nargout=0)
    n_plots = int(engine.eval("length(plot)", nargout=1))

    fig_data = []

    for i in range(n_plots):
        n_children = int(engine.eval(f"length(plot({i+1}).Children)", nargout=1))
        if n_children > 0:
            title = engine.eval(f"plot({i+1}).Title.String", nargout=1)
            if isinstance(title, list):
                title = [str(e) for e in title if len(e)]
            else:
                title = str(title) if len(title) else ''

            plot_data = {
                'title': title,
                'subtitle': engine.eval(f"plot({i+1}).Subtitle.String", nargout=1),
                'XLim': mlarray_to_numpy(engine.eval(f"plot({i+1}).XLim", nargout=1)).astype(float).reshape(-1),
                'YLim': mlarray_to_numpy(engine.eval(f"plot({i+1}).YLim", nargout=1)).astype(float).reshape(-1),
                'XLabel': str(engine.eval(f"plot({i+1}).XLabel.String", nargout=1)),
                'YLabel': str(engine.eval(f"plot({i+1}).YLabel.String", nargout=1)),
                'XScale': str(engine.eval(f"plot({i+1}).XScale")),
                'YScale': str(engine.eval(f"plot({i+1}).YScale")),
            }
            """
            other properties to potentially use:

            XTick
            YTick
            XAxis
            YAxis
            """

            plot_data['content'] = []
            for j in range(n_children):
                child = {
                    'type': engine.eval(f"plot({i+1}).Children({j+1}).Type", nargout=1).lower()
                }

                if child['type'] == 'image':
                    child['CData'] = mlarray_to_numpy(engine.eval(f"plot({i+1}).Children({j+1}).CData", nargout=1)).astype(float)
                    child['XData'] = mlarray_to_numpy(engine.eval(f"plot({i+1}).Children({j+1}).XData", nargout=1)).astype(float)
                    child['YData'] = mlarray_to_numpy(engine.eval(f"plot({i+1}).Children({j+1}).YData", nargout=1)).astype(float)
                elif child['type'] == 'text':
                    child['text'] = engine.eval(f"plot({i+1}).Children({j+1}).String", nargout=1)
                    child['text'] = [str(e) for e in child['text'] if len(e)]
                elif child['type'] == 'line':
                    child['XData'] = mlarray_to_numpy(engine.eval(f"plot({i+1}).Children({j+1}).XData", nargout=1)).astype(float)
                    child['YData'] = mlarray_to_numpy(engine.eval(f"plot({i+1}).Children({j+1}).YData", nargout=1)).astype(float)
                    child['LineStyle'] = engine.eval(f"plot({i+1}).Children({j+1}).LineStyle", nargout=1)
                else:
                    warnings.warn(f"Don't know what {child['type']} is. Thus nothing extracted.")

                plot_data['content'].append(child)
            fig_data.append(plot_data)

    fig_data = list(reversed(fig_data))

    engine.eval(f"ud = fig.UserData;", nargout=0)
    if engine.eval("isfield(ud, 'scan')") and not with_scan:
        engine.eval(f"ud = rmfield(ud, 'scan');", nargout=0)
    engine.eval(f"ud = jsonencode(ud);", nargout=0)
    user_data = json.loads(engine.workspace['ud'])

    return fig_data, user_data


def _parse_orthogonal_qupulse_scan(scan_path: str, engine: 'matlab.engine.MatlabEngine') -> tuple[list, list, list, dict]:
    """This function does not really reflect a robust or correct way to extract the information, but it just works most
    of the time."""
    awg_program = json.loads(engine.eval(f"jsonencode({scan_path}.data.awg_program)"))

    # scan_name = awg_program["pulse_template"]["main"]
    pulse_is_named = True

    # maybe one could take the information which pulse template to use from awg_program["pulse_template"]["main"].
    scan_name = engine.eval(f'{scan_path}.data.conf_seq_args.pulse_template', nargout=1)
    if engine.isempty(scan_name):
        # if scan.data.conf_seq_args.pulse_template is empty, one will use something else:
        if 'main' in awg_program["pulse_template"]:
            scan_name = awg_program["pulse_template"]["main"]

    # ok, then the scan does not have a name and we hope that awg_program["parameters_and_dicts"]
    # still contains the necessary information
    if len(scan_name) == 0:
        scan_name = ""
        pulse_is_named = False

    # there are multiple dicts given for the pulse parameters.
    # The later ones overwrite the settings of the prior ones. This is done in the next lines of code.
    scan_params = {}
    for d in awg_program["parameters_and_dicts"]:
        if pulse_is_named and scan_name in d:
            scan_params = {**scan_params, **d[scan_name]}
        else:
            scan_params = {**scan_params, **d}
        
    # the hacky way is now to look for start_x, ..., stop_y within the scan_params
    keywords_of_interest = ['start', 'stop', 'N']
    found_kws = {}
    for kw in keywords_of_interest:
        for sp in scan_params.keys():
            if kw in sp:
                # the keyword of interest is in the selected scan_param
                se = sp.replace(scan_name, "").replace(kw, "").split("_")
                axis_name = "_".join([x for x in se if (x != "")])

                # save that to the dict
                found_kws.setdefault(kw, {})
                found_kws[kw].setdefault(axis_name, [])
                found_kws[kw][axis_name].append(sp)

    prefix_priority = [scan_name, ""]
    selected_kws = {}
    for kw, v in found_kws.items():
        selected_kws[kw] = {}
        for ax, a in v.items():
            a_sorted = [*a]
            a_sorted.sort(key=len)
            for pp in prefix_priority:
                for e in a_sorted:
                    if pp in e:
                        # now the interesting keywords are found, the corresponding values is to be obtained
                        # selected_kws[kw][pf] = v2[pp][-1] # set the keyword
                        selected_kws[kw][ax] = scan_params[e] # set the value
                        break
                if ax in selected_kws[kw]:
                    break
            else:
                warnings.warn(f"The parameter for the keyword {kw} and the axis {ax} has not been found to match with prefix_priority. Will use the shortest one instead.")
                selected_kws[kw][ax] = scan_params[a_sorted[0]]

    # checking if every axis has all the necessary entries
    all_axes = {}
    for k, v in selected_kws.items():
        for kk in v.keys():
            all_axes.setdefault(kk, 0)
            all_axes[kk] += 1
    _v = -1
    for v in all_axes.values():
        if _v == -1:
            _v = v
        elif _v != v:
            warnings.warn(f"incomplete information about scan axes.")

    # TODO need to throw out the entries that do not contain all of the keywords_of_interest values
    # TODO this might need to use user specific parameters.

    # filling the output arrays (could also be more dynamic)
    qupulse_rngs = np.full((len(list(all_axes.keys())), 2), np.nan).astype(float)
    qupulse_npoints_list = np.full(len(list(all_axes.keys())), np.nan).astype(int)
    qupulse_setchans = list(all_axes.keys())
    for i, c in enumerate(qupulse_setchans):
        qupulse_rngs[i][0] = selected_kws['start'][c]
        qupulse_rngs[i][1] = selected_kws['stop'][c]
        qupulse_npoints_list[i] = selected_kws['N'][c]

    return list(qupulse_rngs), list(qupulse_npoints_list), list(qupulse_setchans), dict(
        channel_mapping=awg_program['channel_mapping'],
        global_transformation=awg_program['global_transformation']
    )


def load_special_measure_with_matlab_engine(file_name: os.PathLike,
                                            engine=ModuleEngineWrapper,
                                            return_disp: bool=False,
                                            return_rng_as_linspace_params: bool=False) -> Union[
    tuple[pd.DataFrame, Sequence[np.ndarray], pd.Series, Sequence[Sequence[str]]],
    tuple[pd.DataFrame, Sequence[np.ndarray], pd.Series, Sequence[Sequence[str]], dict],
]:
    """
    Load special measure scan using MATLAB. This requires that the package delivered with MATLAB is installed.

    Args:
        file_name: mat file to load
        engine:
            None, str -> passed to matlab.engine.connect_matlab()
            () -> Use module instance
            MatlabEngine -> used directly
        return_disp: Additionally return the disp field of the scan
        return_rng_as_linspace_params: Return the scan axes as linspace parameters (breaks virtual scans)

    Returns:
        scan_axes
        data
        config
        getchans
    """
    if matlab is None:
        raise RuntimeError("Requires MATLAB engine interface.")

    engine = ModuleEngineWrapper.to_engine(engine)

    def normalize_chan(chan) -> Sequence[str]:
        if isinstance(chan, str):
            return [chan]
        elif len(chan) == 0:
            # {} or []
            return []
        else:
            return chan

    # we cannot return a struct array to python so we load it into the namespace
    engine.load(os.fspath(file_name), 'scan', 'data', 'configch', 'configvals', nargout=0)

    for f in ['scan', 'data', 'configch', 'configvals']:
        if not engine.eval(f"exist('{f}', 'var')"):
            raise ValueError(f"{file_name} does not contain {f}.")

    data = engine.workspace['data']
    configch = engine.workspace['configch']
    configvals = engine.workspace['configvals']

    config = pd.Series(np.array(configvals).ravel(), index=configch)

    n_loops = int(engine.eval('numel(scan.loops)'))
    getchans = []
    for ii in range(n_loops):
        getchans.append(normalize_chan(engine.eval(f'scan.loops({ii + 1}).getchan')))

    rngs = []
    npoints_list = []
    setchans = []

    for ii in range(n_loops):
        rng = np.array(engine.eval(f'scan.loops({ii+1}).rng')).ravel()
        if engine.eval(f"isfield(scan.loops({ii + 1}), 'npoints') && ~isempty(scan.loops({ii + 1}).npoints)"):
            npoints = int(engine.eval(f'scan.loops({ii + 1}).npoints'))
        else:
            npoints = rng.size

        if not len(rng) == 0:
            # TODO rng==[] could be used as a flag to look for awg pulses. 
            rngs.append(rng)
            npoints_list.append(npoints)
            setchans.append(normalize_chan(engine.eval(f'scan.loops({ii + 1}).setchan')))

    # hacked together method for detecting qupulse pulses:
    # looking for awg program
    has_pulse_info = engine.eval("isfield(scan, 'data') && isfield(scan.data, 'awg_program')", nargout=1)
    if has_pulse_info:
        qupulse_rngs, qupulse_npoints_list, qupulse_setchans, attrs = _parse_orthogonal_qupulse_scan('scan', engine)
        rngs = qupulse_rngs + rngs
        npoints_list = qupulse_npoints_list + npoints_list
        setchans = qupulse_setchans + setchans
        config.attrs.update(attrs)

    # process trafofn
    if engine.eval("isfield(scan.loops, 'trafofn') && any(arrayfun(@(loop) ~isempty(loop.trafofn), scan.loops))"):
        try:
            n_setchans = int(engine.eval('numel(scan.loops(1).trafofn)'))
            _scan_axes = []
            for ii in range(n_setchans):
                _scan_axes.append(read_table(engine, f'scan.loops(1).trafofn({ii+1}).args{{1}}'))
            scan_axes = pd.concat(_scan_axes, axis='columns')

        except matlab.engine.MatlabExecutionError as e:
            warnings.warn(f"The used trafofns are not understood. And applying them to the extracted ranges and stuff is not implemented.")
            warnings.warn(f"matlab.engine.MatlabExecutionError: {str(e)}")

    if not return_rng_as_linspace_params:
        scan_axes_col = list({chan for chans in setchans for chan in chans})
        scan_axes_rows = [('origin', 0)]
        for l, rng in enumerate(rngs):
            scan_axes_rows.extend((f'loop_{l + 1}', jj) for jj in range(1, rng.size))
        scan_axes_rows = pd.MultiIndex.from_tuples(scan_axes_rows, names=('axis', 'n'))

        scan_axes = pd.DataFrame(index=scan_axes_rows, columns=scan_axes_col)

        for col in scan_axes.columns:
            for idx, setchan in enumerate(setchans):
                if col in setchan:
                    axis = f'loop_{idx+1}'
                    for n, x in enumerate(rngs[idx]):
                        if n == 0:
                            scan_axes.loc[('origin', 0), col] = x
                        else:
                            scan_axes.loc[(axis, n), col] = x
                    break
    else:
        scan_axes = {}
        for i, c in enumerate(setchans):
            if isinstance(c, list):
                _c = ",".join(c)
            else:
                _c = c
            scan_axes[_c] = (*rngs[i], npoints_list[i])

    if return_disp:
        disp = json.loads(engine.eval("jsonencode(scan.disp)", nargout=1))
        return scan_axes, [mlarray_to_numpy(d) for d in data], config, getchans, disp
    else:
        return scan_axes, [mlarray_to_numpy(d) for d in data], config, getchans


def special_measure_to_dataframe(loaded_scan_data: dict,
                                 squeeze_constant_setchan: bool = True) -> pd.DataFrame:
    """Try to interpret the data returned from hdf5storage.loadmat(filename)
    as a pd.DataFrame.

    Not handled/tested yet:
        - Buffered measurements
        - trafofn
        - procfn
        - any thing with MATLAB tables or other classes.
    """
    scan = loaded_scan_data['scan']
    assert scan.shape == (1, 1)
    scan = scan[0, 0]

    loops = scan['loops']
    assert len(loops.shape) == 2
    assert loops.shape[0] == 1
    loops = loops[0, :]

    n_loops = loops.size

    # fails if a loop has more than one npoints
    npoints = list(loops['npoints'].astype(np.int64))
    for idx, npoint in enumerate(npoints):
        if npoint < 0:
            warnings.warn(f"Negative npoints {npoint} in loop {idx} gets clamped to 0")
            npoints[idx] = max(npoint, 0)

    setchan = list(loops['setchan'])
    for loop_idx, chan in enumerate(setchan):
        assert len(chan.shape) == 2
        assert chan.shape[0] == 1
        setchan[loop_idx] = tuple(ch[0] for ch in chan.ravel())

    # rngs can be per channel or
    rngs = list(loops['rng'])
    for loop_idx, rng in enumerate(rngs):
        assert rng.shape == (1, 2)
        rngs[loop_idx] = tuple(rng.ravel())

    # This code needs to be adapted if it is possible to use different ranges
    # for different setchannels in the same loop. This might require
    # interpreting the trafofn
    sweeps = []
    for loop_idx in range(n_loops):
        loop_sweeps = {}

        span = np.linspace(*rngs[loop_idx], num=npoints[loop_idx])

        for ch in setchan[loop_idx]:
            loop_sweeps[ch] = span
        sweeps.append(loop_sweeps)

    labels, values = [], []
    for sweep in sweeps:
        if len(sweep) > 1:
            vals = list(sweep.values())
            if np.unique(vals, axis=0).shape[0] != 1:
                raise RuntimeError('Simultaneous sweep with different ranges not supported', vals)
            labels.append('-'.join(sweep.keys()))
            values.append(vals[0])

    idx = pd.MultiIndex.from_product(values, names=labels)

    # buffered measurements no handled?
    getchan = loops['getchan']
    for loop_idx, chan in enumerate(getchan):
        assert len(chan.shape) == 2
        assert chan.shape[0] == 1
        getchan[loop_idx] = tuple(ch[0] for ch in chan.ravel())

    measured = list(itertools.chain.from_iterable(getchan))

    # always vector cell
    data = loaded_scan_data['data']
    assert data.shape == (1, len(measured))
    data = data[0, :]

    result = pd.DataFrame(index=idx)
    assert len(measured) == len(data)
    for meas, val in zip(measured, data):
        val = val.transpose()
        result[meas] = val.flatten()
        assert result[meas].shape == idx.levshape

    if squeeze_constant_setchan:
        to_squeeze = [lvl_idx
                      for lvl_idx, lvl_dim in enumerate(idx.levshape)
                      if lvl_dim == 1]
        result = result.droplevel(to_squeeze)

    try:
        result.attrs['consts'] = loaded_scan_data['scan']['consts']
    except ValueError:
        pass

    return result


@dataclasses.dataclass
class SpecialMeasureScan:
    """Baseline data of special measure scans.

    TODO: store and interpret the disp attribute

    Attributes:
        config: special measure channels and values at the time of scan start.
        data: Measured data field in mat file
        save_time: Timestamp extracted from file metadata i.e. the modification time
        meas_time: Timestamp extracted from the file name if possible
        name: File name without the extension
    """

    config: pd.Series
    data: tuple[np.ndarray, ...]
    save_time: Optional[pd.Timestamp]
    meas_time: Optional[pd.Timestamp]
    name: str

    @property
    def attrs(self):
        attrs = dict(config=self.config)
        if self.meas_time is not None:
            attrs['meas_time'] = self.meas_time
        if self.save_time is not None:
            attrs['save_time'] = self.save_time
        return attrs


@dataclasses.dataclass
class SimpleScan(SpecialMeasureScan):
    """Represents a simple special measure scan.

    Assumptions:
         - Each loop has one or more setchannels
         - No trafofn
         - Procfn results are ignored but may be included
         - All get channels are in the fast loop
    """

    # per loop one setchannel. Fast axis is setchans[-1]
    set_channels: Sequence[str]
    set_ranges: Sequence[Sequence[float]]

    # only fast loop has getchannels
    get_channels: tuple[str, ...]
    
    @property
    def main_channels(self) -> tuple[str, ...]:
        return tuple(self.set_channels)
        

    def to_xarray(self, procfn='warn') -> xr.DataArray:
        assert procfn in ('ignore', 'warn', 'error')
        assert len(self.get_channels) <= len(self.data)
        if len(self.get_channels) < len(self.data):
            if procfn == 'warn':
                warnings.warn("Scan apparently has procfn results")
            elif procfn == 'error':
                raise ValueError("Scan apparently has procfn results")
            data = self.data[:len(self.get_channels)]
        else:
            data = self.data
        shape = tuple(len(ax) for ax in self.set_ranges)
        for d in data:
            assert d.shape == shape

        # fast axis is
        coords = [('getchan', list(self.get_channels))]
        coords.extend(
            (setchan, np.asarray(values))
            for setchan, values in zip(self.set_channels, self.set_ranges)
        )

        return xr.DataArray(
            np.stack(data, axis=0),
            coords=coords,
            attrs=self.attrs,
            name=self.name
        )


@dataclasses.dataclass
class VirtualScan(SpecialMeasureScan):
    """Virtual i.e. non-orthogonal scan.

    The virtual scan is in the space of `physical_gates`. It starts at `origin` and the axes that span the scan are
    in `scan_axes`. The fastest is `scan_axes[-1]`. Currently only data that corresponds to all `get_channels` being
    measured at all points is allowed."""
    physical_gates: tuple[str, ...]
    origin: tuple[float, ...]
    scan_axes: Sequence[tuple[float, ...]]

    # only fast loop has getchannels
    get_channels: tuple[str, ...]

    @property
    def main_channels(self) -> tuple[str, ...]:
        """Return the names of the channels which have the highest magnitude in each axis."""
        return tuple(self.physical_gates[max(range(len(axis)), key=lambda idx: abs(axis[idx]))]
                     for axis in self.scan_axes)

    def to_xarray(self):
        assert len(self.get_channels) <= len(self.data)
        if len(self.get_channels) < len(self.data):
            warnings.warn("Scan apparently has procfn results")

        if len(self.scan_axes) == 1 and all(len(d.shape) > 1 and d.shape[0] == 1 for d in self.data):
            data = [d[0, ...] for d in self.data]
        else:
            data = self.data
        
        shape, = {d.shape for d in data[:len(self.get_channels)]}
        if len(shape) != len(self.scan_axes):
            raise ValueError("Malformed virtual scan data")

        coords = [('getchan', list(self.get_channels))]
        for n_points, scan_axis in zip(shape, self.scan_axes):
            max_idx = int(np.argmax(np.abs(scan_axis)))

            axis_values = self.origin[max_idx] + np.linspace(0., scan_axis[max_idx], num=n_points)

            axis_name = []
            for gate, value in zip(self.physical_gates, scan_axis):
                if np.abs(value) > 1e-15:
                    axis_name.append(f'{value}*{gate}')
            axis_name = f'Virtual {self.physical_gates[max_idx]}:' + ','.join(axis_name)

            coords.append((axis_name, axis_values))

        return xr.DataArray(
            np.stack(data, axis=0),
            coords=coords,
            attrs={**self.attrs, 'origin': self.origin},
            name=self.name
        )


def _read_common_fast_loop_getchan_fields(engine, name_for_loaded: str, shape: tuple[int, ...]):
    data = engine.eval(f'{name_for_loaded}.data')
    data = [mlarray_to_numpy(d) for d in data]
    squeeze_axis = tuple(idx for idx, dim in enumerate(shape) if dim == -1)
    if squeeze_axis:
        for idx, d in enumerate(data):
            try:
                data[idx] = np.squeeze(d, squeeze_axis)
            except ValueError:
                data[idx] = d
        shape = tuple(dim for dim in shape if dim != -1)
    elif np.product(shape) == 1:
        data = [d.reshape(shape) for d in data]
    elif len(shape) == 1:
        for idx, d in enumerate(data):
            if shape[0] in d.shape:
                data[idx] = d.reshape(shape)
        
    
    config = _get_config_channel_values(engine, name_for_loaded)
    n_loops = int(engine.eval(f'numel({name_for_loaded}.scan.loops)'))
    if n_loops == 0:
        raise ValueError("No loops defined")
    getchans = engine.eval(f'[{name_for_loaded}.scan.loops.getchan]')
    
    for d in data:
        if d.shape == ():
            raise ValueError('BUG')

    for (d, ch) in itertools.zip_longest(data, getchans, fillvalue=None):
        if d is None:
            raise TypeError("No data for getchannel. Indicates an invalid or not simple scan", ch)
        elif ch is None:
            warnings.warn("Data found that could not be accociated with a get channel. It is ignored")
        elif d.shape != shape:
            raise TypeError("data shape deviates from expected", d.shape, shape)
    return data, config, getchans


def load_simple_scan_with_matlab_engine(file_name: os.PathLike,
                                        engine=ModuleEngineWrapper,
                                        name_for_loaded: str = 'loaded') -> SimpleScan:
    """Load special measure scan using MATLAB engine. This requires that the package delivered with MATLAB is installed.

    Args:
        file_name: mat file to load
        engine:
            None, str -> passed to matlab.engine.connect_matlab()
            () -> Use module instance
            MatlabEngine -> used directly
        name_for_loaded: the given file is loaded into this variable in the matlab workspace

    Returns:
        simple_scan

    Raises:
        ValueError: if scan is not valid
        TypeError: if scan is not simple
    """
    if matlab is None:
        raise RuntimeError("Requires MATLAB engine interface.")

    engine = ModuleEngineWrapper.to_engine(engine)

    # we cannot return a struct array to python so we load it into the namespace
    engine.eval(f'{name_for_loaded} = load("{os.fspath(file_name)}");', nargout=0)
    name = pathlib.Path(file_name)

    if _has_trafofn(engine, f'{name_for_loaded}.scan'):
        raise TypeError("Cannot extract SimpleScan from scan with trafofn")
    if not engine.eval(f"isfield({name_for_loaded}, 'data')"):
        raise ValueError("No data in scan", file_name)

    scan = f'{name_for_loaded}.scan'
    n_loops = int(engine.eval(f'numel({scan}.loops)'))
    if n_loops == 0:
        raise ValueError("No loops defined")

    rngs = []
    setchans = []
    shape = []

    # we reverse here to be in the same order as data dimensions
    for ii in reversed(range(n_loops)):
        loop = f'{scan}.loops({ii+1})'
        
        setchan = _to_str_list(engine.eval(f'{loop}.setchan'))
        if not setchan:
            shape.append(-1)
            continue
            #raise TypeError(f"Loop {loop} (MATLAB index) does not have a setchan.")
        
        rng = np.array(engine.eval(f'{loop}.rng')).ravel()
        if engine.eval(f"isfield({loop}, 'npoints') && ~isempty({loop}.npoints)"):
            npoints = int(engine.eval(f'{loop}.npoints'))
            if rng.size != npoints:
                rng = np.linspace(*rng, num=npoints)


        setchans.append(','.join(setchan))
        rngs.append(rng)
        shape.append(len(rng))

    shape = tuple(shape)
    data, config, getchans = _read_common_fast_loop_getchan_fields(engine, name_for_loaded, shape)

    try:
        meas_time = _get_datetime_from_file_name(name)
    except ValueError:
        meas_time = None

    return SimpleScan(
        name=name.stem,
        data=tuple(data),
        set_ranges=rngs,
        set_channels=setchans,
        get_channels=getchans,
        config=config,
        save_time=pd.Timestamp.fromtimestamp(os.path.getmtime(file_name)),
        meas_time=meas_time
    )


def _parse_tdg_trafofn(engine: 'matlab.engine.MatlabEngine', loops: str) -> pd.DataFrame:
    """

    Args:
        engine:
        loops:

    Raises:
        TypeError: no suitable trafofn

    Returns:

    """
    if not engine.eval(f"isfield({loops}, 'trafofn')"):
        raise TypeError("No trafofn defined")

    n_trafofns = mlarray_to_numpy(engine.eval(f"arrayfun(@(loop) numel(loop.trafofn), {loops})")).ravel()
    
    # we allow the lasts loop trafofn to be empty
    if n_trafofns[-1] == 0:
        n_trafofns = n_trafofns[:-1]
    
    if len(set(n_trafofns)) != 1:
        raise TypeError("The number of trafofn is not uniform accross loops", n_trafofns)
    n_setchan = int(n_trafofns[0])

    # FIXME: this does not work if `loops` is a reference i.e. a return value
    n_loops = len(n_trafofns)
    loop_tables = []
    for ii_loop in range(n_loops):
        loop_table = []
        for jj_setchan in range(n_setchan):
            args_ref = f"{loops}({ii_loop + 1}).trafofn({jj_setchan + 1}).args"
            if engine.eval(f"numel({args_ref})") != 1:
                raise TypeError("At least one trafofn has more than one argument")

            table = read_table(engine, args_ref + "{1}")
            loop_table.append(table)

        scan_axes = pd.concat(loop_table, axis='columns')
        loop_tables.append(scan_axes)
    for ii_loop in range(1, n_loops):
        if not loop_tables[0].equals(loop_tables[ii_loop]):
            raise TypeError("Tables are not uniform across loops")
    return loop_tables[0]


def load_virtual_scan_with_matlab_engine(file_name: os.PathLike,
                                         engine=ModuleEngineWrapper,
                                         name_for_loaded: str = 'loaded_virtual') -> VirtualScan:
    if matlab is None:
        raise RuntimeError("Requires MATLAB engine interface.")

    engine = ModuleEngineWrapper.to_engine(engine)

    # we cannot return a struct array to python so we load it into the namespace
    engine.eval(f'{name_for_loaded} = load("{os.fspath(file_name)}");', nargout=0)
    name = pathlib.Path(file_name)

    if not engine.eval(f"isfield({name_for_loaded}, 'data')"):
        raise ValueError("No data in scan", file_name)

    sm_scan_axes = _parse_tdg_trafofn(engine, f'{name_for_loaded}.scan.loops')
    origin = sm_scan_axes.loc['origin']
    scan_axes = list(map(tuple, sm_scan_axes.iloc[1::, :].values))[::-1]
    physical_gates = tuple(sm_scan_axes.columns)

    shape = tuple(mlarray_to_numpy(engine.eval(f"[{name_for_loaded}.scan.loops.npoints]")).ravel()[::-1].astype(int))
    data, config, getchans = _read_common_fast_loop_getchan_fields(engine, name_for_loaded, shape)

    try:
        meas_time = _get_datetime_from_file_name(name)
    except ValueError:
        meas_time = None

    return VirtualScan(
        data=tuple(data),
        config=config,
        get_channels=getchans,
        name=name.stem,
        origin=origin,
        scan_axes=scan_axes,
        physical_gates=physical_gates,
        save_time=pd.Timestamp.fromtimestamp(os.path.getmtime(file_name)),
        meas_time=meas_time,
    )


def load_special_measure_scan(file_name: os.PathLike,
                              squeeze_constant_setchan: bool = True) -> pd.DataFrame:
    """
    :param file_name: Path of the file to load
    :param squeeze_constant_setchan: If true, "set channels" that are constant are not included in the index
    :return: Data frame with a multi-index that corresponds to the "set channels" and columns that correspond to the
    "get channels".
    """
    file_name = os.fspath(file_name)

    # this is slow as the scan stuct is quite complicated and hdf5storage creates a dtype for the whole thing
    file_contents = hdf5storage.loadmat(file_name)

    return special_measure_to_dataframe(file_contents, squeeze_constant_setchan)


@qutil.caching.file_cache
def cached_load_mat_file(filename):
    return hdf5storage.loadmat(filename)


def _get_datetime_from_file_name(fname: Union[pathlib.Path, str]) -> datetime.datetime:
    # TODO: move somewhere else
    stem = getattr(fname, 'stem', fname)
    m = SM_DATE_REGEX.fullmatch(stem)
    if m:
        return datetime.datetime.strptime(m.group(1), SM_DATE_FORMAT)
    else:
        raise ValueError("Could not find datetime in file name:", fname, stem)


def _to_str_list(obj: Union[str, list[str], 'matlab.mlarray', 'matlab.double']) -> list[str]:
    """
    handles these MATLAB expressions:
        []
        {}
        'asd'
        {'asd', 'dfg'}
    """
    if not obj:
        return []
    if isinstance(obj, (list, tuple)):
        return list(map(str, obj))
    else:
        return [str(obj)]

