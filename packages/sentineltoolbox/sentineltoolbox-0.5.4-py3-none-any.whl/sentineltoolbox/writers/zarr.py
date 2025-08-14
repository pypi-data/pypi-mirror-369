from typing import Any

from xarray import DataTree


def write_zarr(xdt: DataTree, path: Any, **kwargs: Any) -> None:
    xdt.to_zarr(str(path))
