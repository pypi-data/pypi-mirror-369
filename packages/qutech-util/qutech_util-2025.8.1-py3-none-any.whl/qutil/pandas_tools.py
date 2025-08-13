from collections.abc import Hashable, Iterator
from typing import Any, List, Tuple, Union

import numpy as np
import pandas as pd


def consecutive_groupby(df: pd.DataFrame,
                        columns: Union[Hashable, list[Hashable]]) -> Iterator[tuple[Any, pd.DataFrame]]:
    """Iterate over the given data frame in groups where the specified columns have the same value in consecutive rows.

    Parameters
    ----------
    df
    columns

    Examples
    --------
    >>> df = pd.DataFrame([['a', 0., 42], ['a', 1., 42], ['b', 2., 42], ['b', 3., 43], ['a', 4., 43]], columns=['name', 'number', 'magic'])

    :py:`DataFrame.groupby` groups independent of the order
    >>> list(df.groupby('name')) # doctest: +NORMALIZE_WHITESPACE
    [('a',
        name  number  magic
      0    a     0.0     42
      1    a     1.0     42
      4    a     4.0     43),
     ('b',
        name  number  magic
      2    b     2.0     42
      3    b     3.0     43)]

    >>> list(consecutive_groupby(df, 'name')) # doctest: +NORMALIZE_WHITESPACE
    [('a',
        name  number  magic
      0    a     0.0     42
      1    a     1.0     42),
     ('b',
        name  number  magic
      2    b     2.0     42
      3    b     3.0     43),
     ('a',
        name  number  magic
      4    a     4.0     43)]

    >>> list(df.groupby(['name', 'magic'])) # doctest: +NORMALIZE_WHITESPACE
    [(('a', np.int64(42)),
        name  number  magic
      0    a     0.0     42
      1    a     1.0     42),
     (('a', np.int64(43)),
        name  number  magic
      4    a     4.0     43),
     (('b', np.int64(42)),
        name  number  magic
      2    b     2.0     42),
     (('b', np.int64(43)),
        name  number  magic
      3    b     3.0     43)]

    >>> list(consecutive_groupby(df, ['name', 'magic'])) # doctest: +NORMALIZE_WHITESPACE
    [(('a', 42),
        name  number  magic
      0    a     0.0     42
      1    a     1.0     42),
     (('b', 42),
        name  number  magic
      2    b     2.0     42),
     (('b', 43),
        name  number  magic
      3    b     3.0     43),
     (('a', 43),
        name  number  magic
      4    a     4.0     43)]

    Returns
    -------
    Iterator over (group_value, group_dataframe). Group value is a scalar if columns is a scalar.
    Otherwise, its a tuple.
    """
    group_vals: pd.DataFrame = df[columns]

    splits = np.not_equal(group_vals.values[1:, ...], group_vals.values[:-1, ...])
    if splits.ndim > 1:
        splits = splits.any(axis=1)
        def get_group_val(i): return tuple(group_vals.values[i])
    else:
        get_group_val = group_vals.values.__getitem__

    split_idx = np.flatnonzero(splits)
    split_idx += 1

    start_idx = 0
    for idx in split_idx:
        group_val = get_group_val(start_idx)
        yield group_val, df.iloc[start_idx:idx, :]
        start_idx = idx

    group_val = get_group_val(start_idx)
    yield group_val, df.iloc[start_idx:, :]
