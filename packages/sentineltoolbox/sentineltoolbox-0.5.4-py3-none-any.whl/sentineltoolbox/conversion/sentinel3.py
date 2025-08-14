import json
import logging
import numbers
from collections import Counter
from itertools import count
from pathlib import Path
from typing import Any, Literal, Tuple

import numpy as np
import s3fs
import xarray as xr
from xarray import DataTree

from sentineltoolbox.conversion.utils import (
    ACRONYMS,
    HOMOGENIZE_NAME,
    MAPPINGS,
    SIMPL_MAPPING_PATH,
    STANDARD_NAME,
    convert_mapping,
    use_custom_mapping,
)
from sentineltoolbox.filesystem_utils import get_universal_path
from sentineltoolbox.models.upath import PathFsspec
from sentineltoolbox.typedefs import DEFAULT_COMPRESSOR, T_Json, T_JsonValue

EOP_TREE_STRUC = [
    "measurements",
    "conditions",
    "quality",
]

logger = logging.getLogger("sentineltoolbox.conversion")


ENGINE_NETCDF = "h5netcdf"


def _check_duplicate_set(items):
    hash_bucket = set()
    for item in items:
        if item in hash_bucket:
            print(item)
            return True
        hash_bucket.add(item)
    return False


def _modify_duplicate_elements(input_list: tuple[Any, ...]) -> list[str]:
    c = Counter(input_list)

    iters = {k: count(1) for k, v in c.items() if v > 1}
    output_list = [x + str(next(iters[x])) if x in iters else x for x in input_list]
    return output_list


def _fix_dataset(
    filename_or_obj,
    ds: dict[str, xr.Dataset],
    key: str,
    chunk_sizes: dict[str, int] | None = None,
    decode_times: bool = True,
    open_non_chunked: bool = True,
    **kwargs: Any,
) -> bool:
    if open_non_chunked:
        # TODO: cette ligne pose pb car elle est incompatible avec fs.open
        # il faut donc utiliser une solution alternative, comme stb.open_dataset
        ds[key] = xr.open_dataset(
            filename_or_obj,
            decode_times=decode_times,
            engine=ENGINE_NETCDF,
            **kwargs,
        )

    fixed = False
    for v in ds[key]:
        array = ds[key][v]
        if len(set(array.dims)) < len(array.dims):
            new_dims = _modify_duplicate_elements(array.dims)
            new_array = xr.DataArray(array.data, coords=array.coords, dims=new_dims)
            ds[key][v] = new_array
            if open_non_chunked:
                ds[key] = ds[key].chunk(chunk_sizes)
            fixed = True
    return fixed


def _homogeneize_dataset(ds: xr.Dataset) -> xr.Dataset:

    # Replace var, coord or dimension names following a defined static list
    var_and_dim_names = list(ds.variables)
    var_and_dim_names.extend(list(ds.dims))
    change_names = {k: v for k, v in HOMOGENIZE_NAME.items() if k in var_and_dim_names}
    if change_names:
        try:
            ds = ds.rename(change_names)
        except ValueError:
            pass

    # ATTRIBUTES modification
    # Lower case for attrs.
    def _to_lower(x):
        return " ".join(a if a in ACRONYMS else a.lower() for a in x.split())

    attrs_list = ["long_name", "flag_meanings"]
    for var in ds.data_vars:
        for attr in attrs_list:
            name = ds[var].attrs.get(attr, None)
            if name:
                ds[var].attrs[attr] = _to_lower(name)

    # Check sandard_name
    attrs_list = ["standard_name"]
    for var in ds.data_vars:
        for attr in attrs_list:
            name = ds[var].attrs.get(attr, None)
            if name in STANDARD_NAME:
                ds[var].attrs[attr] = STANDARD_NAME[name]

    # Remove ancillary_variables
    attrs_list = ["ancillary_variables", "bandwidth", "wavelength", "flag_descriptions"]
    for var in ds.data_vars:
        for attr in attrs_list:
            ds[var].attrs.pop(attr, None)

    # Drop scalar variables
    ds = ds.squeeze(drop=True)

    return ds


def _fix_dataset_attr(attr: Any, path="") -> T_JsonValue | T_Json:
    if isinstance(attr, dict):
        for attr_name, attr_value in attr.items():
            attr[attr_name] = _fix_dataset_attr(attr_value, path=path + "/" + attr_name)
        return attr
    elif isinstance(attr, list):
        for i, value in enumerate(attr):
            attr[i] = _fix_dataset_attr(value, path=path + f"/{i}")
        return attr
    elif isinstance(attr, np.ndarray):
        return attr.tolist()
    elif isinstance(attr, (int, float, bool, str)):
        return attr
    elif isinstance(attr, numbers.Integral):
        return int(attr)
    elif isinstance(attr, numbers.Real):
        return float(attr)
    elif attr is None:
        return attr
    else:
        print(f"{path} Unsupported attribute type {type(attr)}")
        return attr


def _fix_dataset_attrs(ds: xr.Dataset) -> None:
    # Iterating over global attributes
    for attr_name, attr_value in ds.attrs.items():
        ds.attrs[attr_name] = _fix_dataset_attr(attr_value, path="ROOT:")

    # Iterating over each data variable and its attributes
    for var_name, variable in ds.data_vars.items():
        for attr_name, attr_value in variable.attrs.items():
            variable.attrs[attr_name] = _fix_dataset_attr(attr_value, path=f"{var_name}:{attr_name}")

    # Iterating over each coordinate and its attributes
    for coord_name, coord in ds.coords.items():
        for attr_name, attr_value in coord.attrs.items():
            coord.attrs[attr_name] = _fix_dataset_attr(attr_value, path=f"{coord_name}:{attr_name}")


def read_and_fix_netcdf(safe_ds, filename_or_obj, name, chunk_sizes, decode_times, compute=True, **kwargs):
    try:
        # In xarray >2024, warning is added when opening a dataset in case of duplicate dimensions
        # (for instance a correlation matrix)
        # ValueError is raised when trying to chunk in such a case
        # The issue is fixed from xarray.2024.07.0
        safe_ds[name] = xr.open_dataset(
            filename_or_obj,
            chunks=chunk_sizes,
            decode_times=decode_times,
            engine=ENGINE_NETCDF,
            **kwargs,
        )
    except ValueError as e:
        fixed = _fix_dataset(
            filename_or_obj,
            safe_ds,
            name,
            chunk_sizes=chunk_sizes,
            decode_times=decode_times,
            **kwargs,
        )
        if not fixed:
            print(e)
            raise ValueError
    # For xarray >= 2024.07.0 duplicated dimensions is fixed and do not return ValueError anymore
    # Yet, it modified anyway to avoid duplicated dimensions as good practice
    _fix_dataset(filename_or_obj, safe_ds, name, open_non_chunked=False)

    for ds_id, ds in safe_ds.items():
        if compute:
            safe_ds[ds_id] = ds.compute()
        _fix_dataset_attrs(safe_ds[ds_id])


def _create_dataset_from_ncfiles(
    input_list: list[PathFsspec],
    chunk_sizes: dict[str, int] | None,
    decode_times: bool = True,
    **kwargs: Any,
) -> dict[str, xr.Dataset]:

    safe_ds = {}
    for f in input_list:
        # ignore non nc files, for example "quicklook.png"
        if not f.name.endswith(".nc"):
            continue
        if f.name in ["tg.nc", "met_tx.nc"]:
            decode_times = False
        if "file" in f.fs.protocol or "local" in f.fs.protocol:
            read_and_fix_netcdf(safe_ds, f.path, f.name, chunk_sizes, decode_times, compute=False, **kwargs)
        else:
            with f.open("rb") as filename_or_obj:
                read_and_fix_netcdf(safe_ds, filename_or_obj, f.name, chunk_sizes, decode_times, compute=True, **kwargs)

    return safe_ds


def _merge_dataset(
    safe_ds: dict[str, xr.Dataset],
    data_map: dict[str, Any],
    group: str,
) -> xr.Dataset:
    if group not in data_map:
        print(f"{group} not found in data mapping")
        raise KeyError

    init = True
    ds: xr.Dataset = xr.Dataset()
    grp = group
    for file in data_map[grp]:
        # rename coordinates in safe_ds[file] if needed
        if file not in safe_ds:
            logger.warning(f"Expect file {file!r}. Please check input is correct")
            continue
        for var in data_map[grp][file]:
            if var[0] in safe_ds[file].coords.keys() and var[1] != var[0]:
                safe_ds[file] = safe_ds[file].rename({var[0]: var[1]})
        for var in data_map[grp][file]:
            try:
                array = safe_ds[file][var[0]]
            except:  # noqa: E722
                array = safe_ds[file][var[1]]
            # print(array)
            # print(array.name,array.dims)
            if not init:
                # Case where name of var is a dimension => automatically read as a coordinate
                if array.name in array.dims:
                    continue
                elif var[1] in ds.dims or var[1] in ds.coords.keys():  # noqa: F821
                    ds = ds.assign_coords({var[1]: array})  # noqa: F821
                    # print(f"{var[1]} is a coordinate")
                # elif var[1] in ["latitude", "longitude", "time_stamp", "x", "y"]:
                elif var[1] in ["latitude", "longitude", "x", "y"]:
                    ds = ds.assign_coords({var[1]: array})
                else:
                    try:
                        ds = xr.merge([ds, array.rename(var[1])])
                    except ValueError as e:
                        print(e)
                        print(f"{file}:{grp}")  # - {data_map[group][file]}")
                        print(var[0], var[1])
                        raise (e)
            else:
                if var[1] in array.coords.keys():
                    ds = array.coords.to_dataset()
                elif var[1] in ["latitude", "longitude", "time_stamp", "x", "y"]:
                    ds = xr.Dataset()
                    ds = ds.assign_coords({var[1]: array})
                else:
                    ds = array.to_dataset(name=var[1])
                init = False

    ds = _homogeneize_dataset(ds)

    return ds


def _get_s3filesystem_from_storage_options(
    storage_options: dict[str, Any] | None = None,
) -> s3fs.S3FileSystem:
    if storage_options is None:
        return s3fs.S3FileSystem(anon=True)
    else:
        try:
            endpoint_url = storage_options["s3"]["endpoint_url"]
        except KeyError:
            endpoint_url = storage_options["s3"]["client_kwargs"]["endpoint_url"]
        return s3fs.S3FileSystem(
            key=storage_options["s3"]["key"],
            secret=storage_options["s3"]["secret"],
            endpoint_url=endpoint_url,
        )


def _get_product_type(url: PathFsspec) -> str:
    return url.name[4:12]


def _get_data_mapping(
    dataset: Literal["eogroup", "netcdf"],
    url: PathFsspec,
    product_type: str,
    files: list[PathFsspec],
    ncfile_or_eogroup: str | None = None,
    simplified_mapping: bool | None = None,
) -> tuple[dict[str, Any], dict[str, Any], list[PathFsspec]]:
    data_map = {}
    chunk_sizes = {}
    if dataset == "eogroup":
        if simplified_mapping is None:
            simplified_mapping = use_custom_mapping(url)

        if simplified_mapping:
            mapfile = SIMPL_MAPPING_PATH / MAPPINGS[product_type]
            with mapfile.open() as f:
                map_safe = json.load(f)
        else:
            map_safe = convert_mapping(MAPPINGS[product_type])
        data_map = map_safe["data_mapping"]

        chunk_sizes = map_safe["chunk_sizes"]

        if ncfile_or_eogroup is None:
            selected_files = files
        else:
            selected_files = [f for f in files if f.name in data_map[ncfile_or_eogroup].keys()]
    else:
        if ncfile_or_eogroup is None:
            selected_files = [url]
        else:
            ncfile_path = url + "/" + ncfile_or_eogroup
            selected_files = [ncfile_path]

    return data_map, chunk_sizes, selected_files


def open_sentinel3_dataset(
    product_urlpath: str | Path,
    ncfile_or_eogroup: str,
    *,
    drop_variables: Tuple[str] | None = None,
    storage_options: dict[str, Any] | None = None,
    simplified_mapping: bool | None = None,
    fs_copy: bool | None = None,
    **kwargs: Any,
) -> xr.Dataset:
    upath = get_universal_path(product_urlpath, **kwargs)
    product_type = _get_product_type(upath)
    files = [f for f in upath.iterdir() if f.is_file()]

    # check the ncfile or eogroup
    dataset: Literal["netcdf", "eogroup"]
    if ncfile_or_eogroup.endswith(".nc"):
        dataset = "netcdf"
    else:
        dataset = "eogroup"

    # Create the mapping to organise the new dataset
    chunk_sizes: dict[str, Any] | None
    data_map, chunk_sizes, selected_files = _get_data_mapping(
        dataset,
        upath,
        product_type,
        files,
        ncfile_or_eogroup=ncfile_or_eogroup,
        simplified_mapping=simplified_mapping,
    )

    if fs_copy is False:
        chunk_sizes = {}

    # open dataset for each selecte files
    safe_ds = _create_dataset_from_ncfiles(
        selected_files,
        chunk_sizes,
        storage_options=storage_options,
    )

    # merge the different dataset into a single one
    if dataset == "netcdf":
        return safe_ds[ncfile_or_eogroup]
    else:
        return _merge_dataset(safe_ds, data_map, ncfile_or_eogroup)


def open_safe_datatree(
    filename_or_obj: str | Path,
    simplified_mapping: bool | None = None,
    **kwargs: Any,
) -> DataTree:
    """Opens a Sentinel-3 SAFE product as a full datatree

    Parameters
    ----------
    name: str
        Name of the datatree product
    product_urlpath: str, Path
        Path in the filesystem to the product to be opened.
    simplified_mapping, optional
        Use a custom simplified mapping, by default it is set given the product type

    Returns
    -------
        DataTree
    """
    # Create the mapping to organise the new dataset
    chunk_sizes: dict[str, Any] | None

    if "universal_path" in kwargs:
        upath = kwargs.get("universal_path")
    else:
        upath = get_universal_path(filename_or_obj, **kwargs)

    product_type = _get_product_type(upath)
    files = [f for f in upath.iterdir() if f.is_file()]

    data_map, chunk_sizes, selected_files = _get_data_mapping(
        "eogroup",
        upath,
        product_type,
        files,
        simplified_mapping=simplified_mapping,
    )

    # open dataset for each selecte files
    safe_ds = _create_dataset_from_ncfiles(
        selected_files,
        chunk_sizes,
        decode_times=kwargs["decode_times"] if "decode_times" in kwargs else True,
    )

    eop_ds = {}
    for grp_path in data_map:
        eop_ds[grp_path] = _merge_dataset(safe_ds, data_map, grp_path)

    eop_ds = dict(sorted(eop_ds.items()))
    dt = DataTree.from_dict(eop_ds)

    shortnames: list = []
    for tree in dt.subtree:
        for var in tree.variables:
            tree[var].encoding["compressor"] = DEFAULT_COMPRESSOR
            # Check if coordinates do exist
            if "coordinates" in tree[var].encoding:
                coords = [c for c in tree[var].encoding["coordinates"].split(" ") if c in tree.variables]
                if coords:
                    tree[var].encoding["coordinates"] = " ".join(coords)
                else:
                    tree[var].encoding.pop("coordinates")
            # Set shortnames
            if var in shortnames:
                tmp = tree.path.split("/")[2:]
                tmp.insert(0, var)
                new_shortname = "_".join(tmp)
                if new_shortname in shortnames:
                    logger.warning(f"{new_shortname} already exists in shornames list")
                    logger.warning(f"variables {var} will not have short_name")
                    continue
                tree[var].attrs.update({"short_name": new_shortname})
                shortnames.append(new_shortname)
            else:
                tree[var].attrs.update({"short_name": var})
                shortnames.append(var)

    # Verification of unicity of shortnames
    if len(set(shortnames)) < len(shortnames):
        logger.warning("Error in shortnames: Items appear twice ...")
        # print(shortnames)
        _check_duplicate_set(shortnames)
        raise IOError("Error in shortnames: Items appear twice ...")

    return dt
