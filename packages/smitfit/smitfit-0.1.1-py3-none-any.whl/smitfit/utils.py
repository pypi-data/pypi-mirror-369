from __future__ import annotations

from functools import reduce
from typing import Any, OrderedDict, Union

import numpy as np


# todo this should accept iterable of arrays
# then Root can also use it
def flat_concat(data: dict[str, np.ndarray]) -> np.ndarray:
    return np.concatenate([arr.flatten() for arr in data.values()])


def clean_types(d: Any) -> Any:
    """cleans up nested dict/list/tuple/other `d` for exporting as yaml

    Converts library specific types to python native types, including numpy dtypes,
    OrderedDict, numpy arrays

    # https://stackoverflow.com/questions/59605943/python-convert-types-in-deeply-nested-dictionary-or-array

    """
    if isinstance(d, np.floating):
        return float(d)

    if isinstance(d, np.integer):
        return int(d)

    if isinstance(d, np.ndarray):
        return d.tolist()

    if isinstance(d, list):
        return [clean_types(item) for item in d]

    if isinstance(d, tuple):
        return tuple(clean_types(item) for item in d)

    if isinstance(d, OrderedDict):
        return clean_types(dict(d))

    if isinstance(d, dict):
        return {k: clean_types(v) for k, v in d.items()}

    else:
        return d


def format_indexer(indexer: tuple[slice, int, None, Ellipsis]) -> str:
    """Format a tuple of slice objects into a string that can be used to index a numpy array.

    More or less the inverse of `numpy.index_exp`.


    Args:
        indexer: Tuple of indexing objects.

    """

    return f"[{', '.join(_format_indexer(sl) for sl in indexer)}]"


def _format_indexer(indexer: Union[slice, int, None, Ellipsis]) -> str:
    if isinstance(indexer, int):
        return str(indexer)
    elif isinstance(indexer, slice):
        # adapted from
        # https://stackoverflow.com/questions/24662999/how-do-i-convert-a-slice-object-to-a-string-that-can-go-in-brackets
        sl_start = "" if indexer.start is None else str(indexer.start)
        sl_stop = "" if indexer.stop is None else str(indexer.stop)
        if indexer.step is None:
            sl_str = "%s:%s" % (sl_start, sl_stop)
        else:
            sl_str = "%s:%s:%s" % (sl_start, sl_stop, indexer.step)
        return sl_str
    elif isinstance(indexer, type(None)):
        return "None"
    elif isinstance(indexer, type(Ellipsis)):
        return "..."
    else:
        raise TypeError(f"Unexpected type: {type(indexer)}")


# https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties/31174427#31174427
def rsetattr(obj: Any, attr: str, val: Any) -> Any:
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


# https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties/31174427#31174427
def rgetattr(obj: Any, attr: str, *default):
    try:
        return reduce(getattr, attr.split("."), obj)
    except AttributeError as e:
        if default:
            return default[0]
        else:
            raise e
