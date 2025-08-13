"""
Tools for easier interoparability with QCoDeS and qtt
"""
from collections.abc import Mapping
from typing import Callable

import numpy as np
import pandas as pd

from .functools import scaled

try:
    from qcodes_loop.data.data_array import DataArray
    from qcodes_loop.data.data_set import DataSet, new_data
except ImportError:
    # legacy qcodes version
    from qcodes.data.data_array import DataArray
    from qcodes.data.data_set import DataSet, new_data

DEFAULT_TO_MV_TRAFO = {
    'V': scaled(1e3),
    'uV': scaled(1e-3),
    'µV': scaled(1e-3)
}


def dataframe_to_legacy_dataset(df: pd.DataFrame, unitlookup: Mapping[str, str]) -> DataSet:
    """Create a DataSet from given DataFrame. Set arrays are constructed from
    the index which needs to be a MultiIndex. metadata is copied from df.attrs.
    default_parameter_name is the forst column.

    Parameters
    ----------
    df : pd.DataFrame
        pandas DataFrame with df.index being a pandas.MultiIndex.
    unitlookup : TYPE
        Units of columns and index levels are looked up here.
        All must be present.

    Returns
    -------
    data : DataSet
        default_parameter_name.

    """
    data = new_data()
    data.metadata.update(df.attrs)

    assert isinstance(df.index, pd.MultiIndex)

    das = []
    for lvl, lvldata in enumerate(df.index.levels):
        levname = df.index.names[lvl]
        levdata = df.index.get_level_values(lvl).values.reshape(df.index.levshape)
        levidx = (slice(None, None),) * (lvl + 1) + (0,) * (len(df.index.levshape) - (lvl + 1))
        levdata = levdata[levidx]

        da = DataArray(name=lvldata.name,
                  unit=unitlookup[lvldata.name],
                  array_id=lvldata.name,
                  shape=levdata.shape,
                  is_setpoint=True,
                  preset_data=levdata)
        das.append(da)
        data.add_array(da)

    for colname, colser in df.items():
        col_data = colser.values.reshape(df.index.levshape)

        da = DataArray(name=colname,
          unit=unitlookup[colname],
          array_id=colname,
          shape=col_data.shape,
          is_setpoint=False,
          set_arrays=das,
          preset_data=col_data)
        data.add_array(da)
    data.metadata['default_parameter_name'] = df.columns[0]
    return data


def to_mv_dataset(data: DataSet,
                  to_mv_trafo: Mapping[str, Callable[[np.ndarray], np.ndarray]] = None) -> DataSet:
    """
    Convert all voltage units to mV using the transformations given in
    to_mv_trafo. Some qtt function expect x and y axis to be mV.

    Parameters
    ----------
    data : DataSet
        DESCRIPTION.
    to_mv_trafo : Mapping[str, Callable[[np.ndarray], np.ndarray]], optional
        mapping of units to trafo functions. The default is None which gets
        replaced with DEFAULT_TO_MV_TRAFO.

    Returns
    -------
    DataSet
        Dataset with all voltage like units beeing millivolt.

    """
    if to_mv_trafo is None:
        to_mv_trafo = DEFAULT_TO_MV_TRAFO

    if all(array.unit not in to_mv_trafo for array in data.arrays.values()):
        return data

    new_dataset = new_data()
    new_dataset.metadata.update(data.metadata)

    for array in data.arrays.values():
        if array.is_setpoint:
            if array.set_arrays:
                # a setpoint array must be its own inner loop
                pass

            new_dataset.add_array(DataArray(
                name=array.name,
                array_id=array.name,
                shape=array.shape,
                label=array.label,
                full_name=array.full_name,
                is_setpoint=True,
                unit='mV',
                preset_data=to_mv_trafo.get(array.unit, lambda x: x)(array.ndarray)
                ))

    for array in data.arrays.values():
        if not array.is_setpoint:
            set_arrays = tuple(new_dataset.arrays[set_array.name]
                               for set_array in array.set_arrays)

            new_dataset.add_array(DataArray(
                name=array.name,
                array_id=array.name,
                shape=array.shape,
                label=array.label,
                full_name=array.full_name,
                is_setpoint=False,
                set_arrays=set_arrays,
                unit='mV',
                preset_data=to_mv_trafo.get(array.unit, lambda x: x)(array.ndarray)
                ))

    return new_dataset
