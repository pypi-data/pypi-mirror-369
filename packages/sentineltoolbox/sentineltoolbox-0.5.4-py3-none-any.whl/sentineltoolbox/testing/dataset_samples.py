from typing import Any

import numpy as np
from xarray import Dataset


def check_adf_simple_v(v: Any) -> None:
    assert v.dtype == bool
    assert v.item() is False
    assert v.attrs["description"] == "v attribute"
    assert list(v.attrs.keys()) == ["description"]


def check_adf_simple_g1_v1(v: Any) -> None:
    assert v.attrs["description"] == "g1/v1 attribute"
    assert v.item() == 10


def check_dataset_adf_simple(ds: Dataset) -> None:
    assert isinstance(ds, Dataset)
    check_adf_simple_v(ds["v"])
    check_adf_simple_g1_v1(ds["g1/v1"])


def check_dataset_adf_xarray(ds: Dataset) -> None:
    assert isinstance(ds, Dataset)
    assert ds["v"].item(0) == 0
    assert ds["v"].item(1) == 0
    assert "band" in ds.coords
    assert "detector" in ds.coords
    assert ds["g1/v1"].attrs["long_name"] == "V1 long_name"
    assert ds["scalars/s1"].dtype == np.float64
