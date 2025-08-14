import time

from silx.io import h5py_utils
from silx.io.url import DataUrl

from ..data import nexus


def test_create_nexus_group(tmp_path):
    with nexus.create_nexus_group(str(tmp_path / "file.h5")) as (
        h5item,
        already_existed,
    ):
        assert not already_existed
        assert h5item.name == "/results"
    with nexus.create_nexus_group(str(tmp_path / "file.h5")) as (
        h5item,
        already_existed,
    ):
        assert already_existed
        assert h5item.name == "/results"

    with nexus.create_nexus_group(
        str(tmp_path / "file.h5::/c"), default_levels=("a", "b")
    ) as (h5item, already_existed):
        assert not already_existed
        assert h5item.name == "/c/b"
    with nexus.create_nexus_group(
        str(tmp_path / "file.h5::/c"), default_levels=("a", "b")
    ) as (h5item, already_existed):
        assert already_existed
        assert h5item.name == "/c/b"
    with nexus.create_nexus_group(str(tmp_path / "file.h5::/c/b")) as (
        h5item,
        already_existed,
    ):
        assert already_existed
        assert h5item.name == "/c/b"


def test_create_url(tmp_path):
    input_url = DataUrl(f"{tmp_path / 'file.h5'}::/1.1/measurement/integrated").path()

    created_url = nexus.create_url(input_url)
    assert created_url == nexus.as_dataurl(input_url)

    with h5py_utils.open_item(
        created_url.file_path(), created_url.data_path(), mode="a"
    ) as item:
        # Add unique id to identify the item
        item_id = f"CREATED AT {time.time()}"
        item.attrs["id"] = item_id

    created_url = nexus.create_url(input_url, overwrite=False)
    with h5py_utils.open_item(
        created_url.file_path(), created_url.data_path()
    ) as new_item:
        # It is the same item
        assert new_item.attrs["id"] == item_id

    created_url = nexus.create_url(input_url, overwrite=True)
    with h5py_utils.open_item(
        created_url.file_path(), created_url.data_path()
    ) as new_item:
        # It is a different item
        assert "id" not in new_item.attrs
