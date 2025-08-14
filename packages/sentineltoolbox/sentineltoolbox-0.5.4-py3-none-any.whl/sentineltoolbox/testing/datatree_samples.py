import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr
import zarr
from xarray import DataArray, DataTree

from sentineltoolbox.attributes import AttributeHandler
from sentineltoolbox.proc_checkers import _to_canonical_type
from sentineltoolbox.testing.dataset_samples import (
    check_adf_simple_g1_v1,
    check_adf_simple_v,
)

DATE_FORMAT = r"%Y%m%dT%H%M%S"


def fix_path(path: Path | None, **kwargs: Any) -> Path | None:
    if path is None:
        return None
    path = Path(path).absolute()
    if path.exists():
        force = kwargs.get("force", False)
        ask = kwargs.get("ask", False)
        if force and path.suffix not in [".zarr", ".zip"]:
            print("CANNOT FORCE OVERWRITE on path without .zarr or .zip extenstion")
            force = False
        if ask:
            force = input(f"  -> replace {path} ? [n]") == "y"
        if force:
            if path.is_dir():
                shutil.rmtree(str(path))
            elif path.is_file():
                path.unlink()
            else:
                raise NotImplementedError
            print(f"REMOVE {path}")
            return path
        else:
            print(f"KEEP existing path {path}")
            return None
    else:
        return path


def _save_on_disk(dt: DataTree, **kwargs: Any) -> None:
    zarr_path = fix_path(kwargs.get("url"), **kwargs)
    zip_path = fix_path(kwargs.get("url_zip"), **kwargs)

    if zarr_path:
        print(f"CREATE {zarr_path!r}")
        dt.attrs["filename"] = zarr_path.name
        dt.to_zarr(zarr_path)

    if zip_path:
        with zarr.ZipStore(zip_path) as store:
            print(f"CREATE {zip_path!r}")
            dt.attrs["filename"] = zip_path.name
            dt.to_zarr(store)


def check_datatree_sample(dt: DataTree) -> None:
    assert "other_metadata" in dt.attrs  # nosec
    assert "measurements" in dt  # nosec
    assert "coarse" in dt["measurements"]  # nosec
    assert "fine" in dt["measurements"]  # nosec
    assert "var1" in dt["measurements/coarse"].variables  # nosec
    var1 = dt["measurements/coarse/var1"]
    assert var1.shape == (2, 3)  # nosec


def check_datatree_adf_simple(dt: DataTree) -> None:
    assert isinstance(dt, DataTree)
    check_adf_simple_v(dt["v"])
    check_adf_simple_g1_v1(dt["g1/v1"])


def check_datatree_adf_xarray(dt: DataTree) -> None:
    assert dt["v"].item(0) == 0
    assert dt["v"].item(1) == 0
    assert "band" in dt.coords
    assert "detector" in dt["g1"].coords
    assert dt["g1/v1"].attrs["long_name"] == "V1 long_name"
    assert dt["scalars/s1"].dtype == np.float64


def create_datatree_sample(**kwargs: Any) -> DataTree:
    data = xr.DataArray(
        np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
        dims=("x", "y"),
        coords={"x": [10, 20], "y": [10, 20, 30]},
    )

    ds_coarse = xr.Dataset({"var1": data})
    ds_fine: xr.Dataset = ds_coarse.interp(coords={"x": [10, 15, 20], "y": [10, 15, 20, 25, 30]})
    ds_root = xr.Dataset(attrs={"other_metadata": {}})

    dt = DataTree.from_dict({"measurements/coarse": ds_coarse, "measurements/fine": ds_fine, "/": ds_root})

    # register shortnames
    dt["measurements/fine/var1"].attrs["eov_attrs"] = {"dimensions": [], "short_name": "fine_v1"}
    dt["measurements/coarse/var1"].attrs["eov_attrs"] = {"dimensions": [], "short_name": "coarse_v1"}

    _save_on_disk(dt, **kwargs)

    return dt


def create_datatree_sample_diff(**kwargs: Any) -> DataTree:
    """
    datatree sample slightly different. Use to test datatree compare function
    """
    data = xr.DataArray(
        np.array([[1.0, 2.0, 3.0], [1.0, 5.0, 6.0]]),
        dims=("x", "z"),
        coords={"x": [10, 20], "z": [10, 20, 30]},
    )

    ds_coarse = xr.Dataset({"var1": data, "newvar": True})
    ds_fine: xr.Dataset = ds_coarse.interp(coords={"x": [10, 15, 20], "z": [10, 15, 20, 25, 30]})
    ds_root = xr.Dataset(attrs={"other_metadata": {}})

    dt = DataTree.from_dict({"measurements/coarse": ds_coarse, "measurements/fine": ds_fine, "/": ds_root})

    _save_on_disk(dt, **kwargs)

    return dt


def create_datatree_empty(**kwargs: Any) -> DataTree:
    dt: DataTree = DataTree(name="empty")
    _save_on_disk(dt, **kwargs)
    return dt


def create_datatree_empty_adf(
    adf_prefix: str,
    root_dir: str | None = None,
    creation_date: datetime | None = None,
    **kwargs: Any,
) -> DataTree:
    if creation_date is None:
        creation_date = datetime.now()
    date_str = creation_date.strftime(DATE_FORMAT)

    if root_dir is None:
        kwargs["url"] = None
        kwargs["url_zip"] = None
    else:
        kwargs["url"] = Path(root_dir, f"{adf_prefix}_{date_str}.zarr")
        kwargs["url_zip"] = Path(root_dir, f"{adf_prefix}_{date_str}.zarr.zip")

    dt: DataTree = DataTree(name="empty")
    dt.attrs = {"properties": {"created": date_str}}
    dt.attrs.update(kwargs.get("attrs", {}))
    _save_on_disk(dt, **kwargs)
    return dt


def create_datatree_for_autodoc_tests() -> DataTree:
    xdt: DataTree = DataTree(name="SAMPLE")
    xdt.attrs = {
        "stac_discovery": {
            "properties": {
                "processing:level": "L1",
                "product:type": "S03OLCERR",
            },
            "bbox": None,
            "description": "Sample EOPF EOProduct",
        },
    }

    for gr in range(2):
        xdt[f"group{gr}"] = DataTree()
        group = xdt[f"group{gr}"]
        group.attrs = {
            "documentation": f"This is the group {gr} documentation",
            "description": f"Sample group {gr}",
        }

        for var in range(2):
            group[f"group{gr}_variable{var}"] = DataArray()
            group[f"group{gr}_variable{var}"].attrs.update(
                {
                    "documentation": f"This is the variable {var} documentation",
                    "description": f"Sample Variable {var} (GR{gr})",
                },
            )

        group[f"variable{gr}xxx"] = DataArray()
        group[f"variable{gr}xxx"].attrs.update(
            {
                "documentation": f"This is the variable {gr}xxx documentation",
                "description": "Other Sample Variable xxx",
            },
        )

    xdt["other/other"] = DataTree()

    nested_gr = xdt["other/other"]
    nested_gr.attrs = {
        "complex_attribute": {"p1": 1, "p2": {"type": "list", "data": [1, 2, 3]}},
        "repetitive_attr1": 1,
        "repetitive_attr2": 2,
        "repetitive_attr3": 3,
    }
    nested_gr["nested_variable"] = DataArray()
    nested_gr["variable_with_flags"] = DataArray()
    nested_gr["variable_with_flags"].attrs.update(
        {
            "documentation": "This is a variable with associated flags",
            "description": "Flag Variable",
            "flag_values": [1, 2, 4],
            "flag_meanings": "coastline ocean tidal",
        },
    )
    return xdt


def create_empty_datatree_with_metadata(product_type: str, is_adf: bool = False, **kwargs: Any) -> DataTree:
    platform = kwargs.get("platform", "sentinel-xx")
    extension = kwargs.get("extension", ".zarr")

    if is_adf:
        # S03_ADF_XXXXX -> XXXXX
        if "ADF_" in product_type:
            semantic = product_type[-5:]
        else:
            semantic = product_type
    else:
        semantic = _to_canonical_type(product_type, is_adf=is_adf)
    pl = platform[-2:].upper()
    if is_adf:
        default_filename = f"S0{pl}_ADF_{semantic}_20160216T000000_20991231T235959_20231030T154253{extension}"
    else:
        default_filename = f"{semantic}_20230506T015316_0180_{pl}117_T688.zarr"
    filename = kwargs.get("filename", default_filename)
    method = kwargs.get("method", "metadata")
    adf = DataTree()
    adf.attrs = kwargs.get("attrs", {})
    if method == "metadata":
        attrs = AttributeHandler(adf)
        attrs.set_stac_property("product:type", product_type)
        if platform:
            attrs.set_stac_property("platform", platform)
    elif method == "filename":
        adf.reader_info = {"name": filename}
    return adf


def create_empty_product_with_metadata(product_type: str, **kwargs: Any) -> DataTree:
    return create_empty_datatree_with_metadata(product_type, is_adf=False, **kwargs)


def create_empty_adf_with_metadata(product_type: str, **kwargs: Any) -> DataTree:
    return create_empty_datatree_with_metadata(product_type, is_adf=True, **kwargs)


SAMPLE_DATATREE = create_datatree_for_autodoc_tests()
