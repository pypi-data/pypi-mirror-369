import sys
from typing import Tuple, Union
from silx.io.url import DataUrl


def as_dataurl(url: Union[str, DataUrl]) -> DataUrl:
    if isinstance(url, str) and sys.platform == "win32":
        url = url.replace("\\", "/")
    if not isinstance(url, DataUrl):
        url = DataUrl(url)
    return url


def h5dataset_url_parse(url: Union[str, DataUrl]) -> Tuple[str, str, Tuple]:
    url = as_dataurl(url)
    filename = str(url.file_path())
    h5path = url.data_path()
    if h5path is None:
        h5path = "/"
    idx = url.data_slice()
    if idx is None:
        idx = tuple()
    return filename, h5path, idx
