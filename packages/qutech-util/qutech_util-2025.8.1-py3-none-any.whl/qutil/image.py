from __future__ import annotations

import os
import pathlib
from typing import Literal, Optional, Union

import numpy as np
import tifffile
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

from qutil import io

try:
    from numpy.typing import NDArray
except ImportError:
    NDArray = np.ndarray

_pathT = Union[str, os.PathLike]


def convert_tiff(file: _pathT, fps: float, format: str = '.mp4', threads: int | None = None,
                 out: _pathT | None = None, logger: Literal['bar'] | None = None):
    """Converts a multipage .tif file to `format` and writes it to disk.

    Parameters
    ----------
    file : str | os.PathLike
        The .tif file to be converted.
    fps : float
        The framerate of the video.
    format : str
        The output format.
    threads : int, optional
        The number of CPU threads to use for the conversion (see
        :meth:`ImageSequenceClip.write_videofile`) and (possible)
        decompression (see :meth:`tifffile.TiffFile.asarray`)
    out : str | os.PathLike, optional
        A custom filename to write to. Otherwise, the original filename
        with a different suffix is used.
    logger : 'bar' | Proglog logger, optional
        See :meth:`ImageSequenceClip.write_videofile`.

    Examples
    --------
    `fps.txt` holds filenames and corresponding fps values::

        import pandas as pd
        import tempfile
        path = pathlib.Path('//janeway/User AG Bluhm/Common/GaAs',
                            'Hangleiter/characterization/vibrations/videos')
        out = pathlib.Path(tempfile.tempdir, 'foobar')
        tbl = pd.read_table(path / 'fps.txt',
                            dtype={'file': str, 'fps': float},
                            delim_whitespace=True)
        for _, series in tbl.iterrows():
            convert_tiff(path / series.file, series.fps, out=out, logger='bar',
                         threads=os.cpu_count())

    """
    in_name = pathlib.Path(file).with_suffix('.tif')
    out_name = io.query_overwrite((out or in_name).with_suffix(format))

    data = tifffile.imread(str(in_name), maxworkers=threads)
    # Grayscale tiffs returned without color channel in last axis,
    # but ImageSequenceClip implicitly expects it, so expand to 4
    # dims and broadcast the last axis to 3 (rgb).
    data = data.reshape(data.shape + (1,)*(4 - data.ndim))
    data = np.broadcast_to(data, data.shape[:3] + (3,))
    clip = ImageSequenceClip(list(data), fps=fps)

    clip.write_videofile(str(out_name), fps, audio=False, threads=threads,
                         logger=logger)
