import sys
import logging
from numbers import Integral, Number
from typing import Iterator, List, Optional, Tuple, Sequence, Union

import numpy
import h5py
import hdf5plugin  # noqa F401
from numpy.typing import ArrayLike
from silx.io import h5py_utils
from silx.utils import retry as retrymod
from silx.io.utils import get_data as silx_get_data

from .blissdata import iter_bliss_scan_data_from_memory  # noqa F401
from .blissdata import iter_bliss_scan_data_from_memory_slice  # noqa F401
from .blissdata import last_lima_image  # noqa F401
from .blissdata import dynamic_hdf5

from .contextiterator import contextiterator
from . import hdf5
from . import nexus
from . import url


logger = logging.getLogger(__name__)


def get_data(
    data: Union[str, ArrayLike, Number], **options
) -> Union[numpy.ndarray, Number]:
    if isinstance(data, str):
        data_url = url.as_dataurl(data)
        filename, h5path, idx = url.h5dataset_url_parse(data_url)
        if filename.endswith(".h5") or filename.endswith(".nx"):
            return _get_hdf5_data(filename, h5path, idx=idx, **options)
        if not data_url.scheme():
            if sys.platform == "win32":
                data_url = f"fabio:///{data}"
            else:
                data_url = f"fabio://{data}"
        return silx_get_data(data_url)
    elif isinstance(data, (Sequence, Number, numpy.ndarray)):
        return data
    else:
        raise TypeError(type(data))


def get_image(*args, **kwargs) -> numpy.ndarray:
    data = get_data(*args, **kwargs)
    return numpy.atleast_2d(numpy.squeeze(data))


@h5py_utils.retry()
def _get_hdf5_data(filename: str, h5path: str, idx=None, **options) -> numpy.ndarray:
    with hdf5.h5context(filename, h5path, **options) as dset:
        if _is_bliss_file(dset):
            if "end_time" not in nexus.get_nxentry(dset):
                raise retrymod.RetryError
        if idx is None:
            idx = tuple()
        return dset[idx]


@contextiterator
def iter_bliss_scan_data(
    filename: str,
    scan_nr: Integral,
    lima_names: Optional[List[str]] = None,
    counter_names: Optional[List[str]] = None,
    subscan: Optional[Integral] = None,
    **options,
) -> Iterator[dict]:
    """Iterate over the data from one Bliss scan. The counters are assumed to have
    many data values as scan points.

    :param str filename: the Bliss dataset filename
    :param Integral filename: the scan number in the dataset
    :param list lima_names: names of lima detectors
    :param list counter_names: names of non-lima detectors (you need to provide at least one)
    :param Integral subscan: subscan number (for example "10.2" has `scan_nr=10` and `subscan=2`)
    :param Number retry_timeout: timeout when it cannot access the data for `retry_timeout` seconds
    :param Number retry_period: interval in seconds between data access retries
    :yields dict: data
    """
    if not subscan:
        subscan = 1
    if counter_names is None:
        counter_names = list()
    with dynamic_hdf5.File(filename, lima_names=lima_names, **options) as root:
        scan = root[f"{scan_nr}.{subscan}"]
        # assert _is_bliss_file(scan), "Not a Bliss dataset file"
        measurement = scan["measurement"]
        instrument = scan["instrument"]
        datasets = {name: measurement[name] for name in counter_names}
        for name in lima_names:
            datasets[name] = instrument[f"{name}/data"]
        names = list(datasets.keys())
        for values in zip(*datasets.values()):
            yield dict(zip(names, values))


@contextiterator
def iter_bliss_data(
    filename: str,
    scan_nr: Integral,
    lima_names: List[str],
    counter_names: List[str],
    subscan: Optional[Integral] = None,
    start_index: Optional[Integral] = None,
    **options,
) -> Iterator[Tuple[int, dict]]:
    """Iterate over the data from one Bliss scan. The counters are assumed to have
    many data values as scan points.

    :param str filename: the Bliss dataset filename
    :param Integral filename: the scan number in the dataset
    :param list lima_names: names of lima detectors
    :param list counter_names: names of non-lima detectors (you need to provide at least one)
    :param Integral subscan: subscan number (for example "10.2" has `scan_nr=10` and `subscan=2`)
    :param Number retry_timeout: timeout when it cannot access the data for `retry_timeout` seconds
    :param Number retry_period: interval in seconds between data access retries
    :param Integral start_index: start iterating from this scan point index
    :yields tuple: scan index, data
    """
    if start_index is None:
        start_index = 0
    for index, data in enumerate(
        iter_bliss_scan_data(
            filename,
            scan_nr,
            lima_names=lima_names,
            counter_names=counter_names,
            subscan=subscan,
            **options,
        )
    ):
        if index >= start_index:
            yield index, data


def _is_bliss_file(h5item: Union[h5py.Dataset, h5py.Group]) -> bool:
    return (
        h5item.file.attrs.get("creator", "").lower() in _BLISS_PUBLISHERS
        or h5item.file.attrs.get("publisher", "").lower() in _BLISS_PUBLISHERS
    )


_BLISS_PUBLISHERS = ("bliss", "blissdata")
