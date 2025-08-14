import os
from contextlib import contextmanager
from typing import Union, Iterator, Optional, Tuple

import h5py
from silx.io import h5py_utils
from .url import DataUrl
from .url import as_dataurl


def ensure_nxclass(group: h5py.Group) -> None:
    if group.attrs.get("NX_class"):
        return
    groups = [s for s in group.name.split("/") if s]
    n = len(groups)
    if n == 0:
        group.attrs["NX_class"] = "NXroot"
    elif n == 1:
        group.attrs["NX_class"] = "NXentry"
    else:
        group.attrs["NX_class"] = "NXcollection"


def select_default_plot(nxdata: h5py.Group) -> None:
    parent = nxdata.parent
    for name in nxdata.name.split("/")[::-1]:
        if not name:
            continue
        parent.attrs["default"] = name
        parent = parent.parent


def create_url(url: str, overwrite: bool = False, **open_options) -> DataUrl:
    url = as_dataurl(url)
    filename = url.file_path()
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    open_options.setdefault("mode", "a")
    with h5py_utils.open_item(filename, "/", **open_options) as parent:
        if overwrite and url.data_path() in parent:
            del parent[url.data_path()]
        h5item, _ = _create_h5group(parent, url.data_path())
        return as_dataurl(f"{filename}::{h5item.name}")


def get_nxentry(h5item: Union[h5py.Dataset, h5py.Group]):
    parts = [s for s in h5item.name.split("/") if s]
    if parts:
        return h5item.file[parts[0]]
    raise ValueError("HDF5 item must be part of an NXentry")


@contextmanager
def create_nexus_group(
    url: Union[str, DataUrl],
    retry_timeout=None,
    retry_period=None,
    default_levels: Optional[Tuple[str]] = None,
    **open_options,
) -> Iterator[Tuple[h5py.Group, bool]]:
    """
    :yields: (h5group, already_existed)
    """
    url = as_dataurl(url)
    filename = url.file_path()
    itemname = url.data_path()
    if not itemname:
        itemname = "/"
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    open_options.setdefault("mode", "a")
    with h5py_utils.open_item(
        filename,
        "/",
        retry_timeout=retry_timeout,
        retry_period=retry_period,
        **open_options,
    ) as root:
        yield _create_h5group(root, itemname, default_levels=default_levels)


def _create_h5group(
    parent, data_path: Optional[str], default_levels: Optional[Tuple[str]] = None
) -> Tuple[h5py.Group, bool]:
    """
    :yields: (h5group, already_existed)
    """
    if not data_path:
        data_path = ""
    groups = [""] + [s for s in data_path.split("/") if s]
    if default_levels:
        default_levels = [""] + list(default_levels)
    else:
        default_levels = ["", "results"]
    if len(groups) < len(default_levels):
        groups += default_levels[len(groups) :]
    data_path = "/".join(groups)
    groups[0] = "/"

    create = False
    ensure_nxclass(parent)
    for group in groups:
        if group in parent:
            parent = parent[group]
        else:
            parent = parent.create_group(group)
            create = True
        ensure_nxclass(parent)
    return parent, not create
