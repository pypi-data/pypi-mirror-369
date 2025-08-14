import json
import sys
from io import TextIOWrapper
from typing import Any, Hashable, TextIO

import click
import numpy as np
from deepdiff import DeepDiff
from xarray import DataArray, DataTree

from sentineltoolbox.converters import convert_to_dict
from sentineltoolbox.readers.open_datatree import open_datatree
from sentineltoolbox.readers.open_metadata import load_metadata
from sentineltoolbox.writers.json import DataTreeJSONEncoder


class NotFound:
    pass


def convert_mapping_to_datatree(mapping: Any, **kwargs: Any) -> DataTree:
    """
     Mapping:
     {
         "short_name": "oa01_radiance",
         "target_path": "/measurements/image/oa01_radiance",
         "source_path": "Oa01_radiance.nc:Oa01_radiance",
         "accessor_id": "netcdf",
         "transform": {
             "dimensions": ["rows", "columns"],
             "attributes": {
                 "coordinates": "latitude longitude",
                 "long_name": "TOA radiance for OLCI acquisition band 01",
                 "dimensions": "rows columns",
                 "units": "mW.m-2.sr-1.nm-1",
                 "dtype": "<u2",
             },
             "rechunk": {"rows": 1024, "columns": 1024},
         },
     }


    xdataarray.attrs:

    {
        "_ARRAY_DIMENSIONS": ["rows", "columns"],
        "coordinates": "time_stamp latitude longitude",
        "short_name": "oa01_radiance",
        "standard_name": "toa_upwelling_spectral_radiance",
        "units": "mW.m-2.sr-1.nm-1",
        "valid_max": 893.550000693649,
        "valid_min": 0.0,
        "_io_config": {
            "scale_factor": 0.013634907081723213,
            "add_offset": 0.0,
            "valid_min": 0,
            "valid_max": 65534,
            "fill_value": 65535,
            "dtype": dtype("uint16"),
        },
        "description": "TOA radiance for OLCI acquisition band oa01",
    }


    xdataarray.encoding

    {"_FillValue": 65535, "scale_factor": 0.013634907081723213, "add_offset": 0.0, "dtype": dtype("uint16")}

    """
    xdt = DataTree()
    stac_discovery = mapping.get("stac_discovery", {})
    for k, v in stac_discovery.items():
        xdt.attrs[k] = v
    xdt.attrs = {}

    data_mapping = mapping.get("data_mapping", [])
    for data in data_mapping:
        target = data.get("target_path")
        if target is None:
            continue
        if target.startswith("coords:"):
            pass
        elif target.startswith("attrs:"):
            pass
        else:
            transform = data.get("transform", {})
            map_dims = transform.get("dimensions", [])
            map_attrs = transform.get("attributes", {})
            shape = [1 for _ in map_dims]

            var = DataArray(np.empty(shape, dtype=map_attrs.get("dtype")), dims=map_dims)
            var.attrs.setdefault("_io_config", {})["dtype"] = var.dtype
            ms = transform.get("mask_and_scale", {})
            for field in ("fill_value", "scale_factor", "add_offset"):
                if field == "fill_value":
                    target_field = "_FillValue"
                else:
                    target_field = field
                value = ms.get(field, NotFound)
                if value is NotFound:
                    pass
                else:
                    var.encoding[target_field] = value
                    var.attrs.setdefault("_io_config", {})[field] = value

            for field in ("valid_min", "valid_max"):
                value = ms.get(field, NotFound)
                if value is NotFound:
                    pass
                else:
                    var.attrs.setdefault("_io_config", {})[field] = value

            for k, v in map_attrs.items():
                if k in ("dimensions",):
                    continue
                var.attrs[k] = v

            xdt[target] = var

    # print(data_mapping)
    return xdt


def convert_datatree_to_str(prod: DataTree) -> str:
    json_str = json.dumps(
        convert_to_dict(prod, output_format="nested-datatree"),
        indent="  ",
        sort_keys=True,
        cls=DataTreeJSONEncoder,
    )
    return json_str


def convert_dict_to_metadata_structure(attrs: dict[Hashable, Any], path: str = "/", **kwargs: Any) -> str:
    """

    :param attrs:
    :param path:
    :param kwargs:
    :return:
    """
    output_str = ""
    for k in sorted(attrs):  # type: ignore
        if isinstance(k, str):
            output_str += f"{path}{k}\n"
            v = attrs[k]
            if isinstance(v, dict):
                output_str += convert_dict_to_metadata_structure(v, path=path + k + "/")
            elif isinstance(v, list):
                if k == "history":
                    continue

                for i, child in enumerate(v):
                    if isinstance(child, dict):
                        output_str += convert_dict_to_metadata_structure(child, path=path + k + "/" + str(i) + "/")
        else:
            continue
    return output_str


def convert_datatree_to_metadata_structure(prod: DataTree, path: str = "/", **kwargs: Any) -> str:
    return convert_dict_to_metadata_structure(prod.attrs)


def convert_variable_details_to_str(data: DataArray, **kwargs: Any) -> str:

    attrs = sorted(data.attrs.keys())
    for ignore in ("_ARRAY_DIMENSIONS", "_io_config"):
        if ignore in attrs:
            attrs.remove(ignore)
    attrs_data = ", ".join(attrs)
    details = ""
    if attrs_data:
        details += f"\n  - attrs: {attrs_data}"

    if kwargs.get("add_io_details", False):
        io = data.attrs.get("_io_config", {})
        values = [f"{k}={v}" for k, v in sorted(io.items())]
        io_data = ", ".join(values)

        if io_data:
            details += f"\n  - data: {io_data}"

    if kwargs.get("add_encoding_details", False):
        values = [f"{k}={v}" for k, v in sorted(data.encoding.items())]
        encoding_data = ", ".join(values)
        if encoding_data:
            details += f"\n  - encoding: {encoding_data}"
    try:
        details += f"\n  - coordinates: {', '.join([str(coord) for coord in data.coords])}"
    except AttributeError:
        pass

    try:
        details += f"\n  - dimensions: {data.dims}"
    except AttributeError:
        pass
    return details


def convert_datatree_to_structure_str(prod: DataTree, **kwargs: Any) -> str:
    output_str = ""
    add_details = kwargs.get("details", False)
    add_dtype = kwargs.get("dtype", False)
    paths = []
    for group in prod.subtree:
        paths.append(group.path)
    paths.sort()

    # output_str += f"VARIABLES\n"
    for group_path in paths:
        group = prod[group_path]
        output_str += f"[group] {group_path}\n"
        root_path = group_path if group_path == "/" else group_path + "/"
        for var_path, var in sorted(group.data_vars.items()):
            details = convert_variable_details_to_str(var)
            details_str = " " + details if add_details else ""
            dtype_str = f", {var.dtype}" if add_dtype else ""
            output_str += f"  [var] {root_path + var_path}, {var.shape}{dtype_str}{details_str}\n"
        for coord_path, coord in sorted(group.coords.items()):
            details = convert_variable_details_to_str(coord)
            details_str = " " + details if add_details else ""
            dtype_str = f", {coord.dtype}" if add_dtype else ""
            output_str += f"  [coord] {root_path + coord_path}, {coord.shape}{dtype_str}{details_str}\n"

    return output_str


def convert_datatree_to_metadata_json(prod: DataTree) -> str:
    json_str = json.dumps(prod.attrs, indent="  ", sort_keys=True, cls=DataTreeJSONEncoder)
    return json_str


@click.command()
@click.argument(
    "input",
    type=str,
    nargs=1,
)
@click.argument("output", type=str, nargs=1, default="")
@click.option("--full-metadata", "dump_mode", flag_value="full-metadata", help="dump metadata only as json")
@click.option("--metadata", "dump_mode", flag_value="metadata-only", help="dump metadata structure only as json")
@click.option(
    "--structure-only",
    "dump_mode",
    flag_value="structure-only",
    default=True,
    help="dump structure only as text",
)
@click.option(
    "--structure-and-details",
    "dump_mode",
    flag_value="structure-and-details",
    help="dump structure with attrs and data summaries",
)
@click.option("--full", "dump_mode", flag_value="full-datatree", help="dump full datatree")
@click.option(
    "--compare",
    "compare",
    type=str,
    default="",
    help="compare with this product and display diff instead of dump",
)
def cli_dump_product(input: str, output: str | None, dump_mode: str, compare: str) -> None:
    path = input
    prod = open_path_as_datatree(path)

    if output:
        fp: TextIO | TextIOWrapper = open(output, "w")
    else:
        fp = sys.stdout

    if compare:
        prod2 = open_path_as_datatree(compare)
        dd = DeepDiff(convert_datatree_to_structure_str(prod), convert_datatree_to_structure_str(prod2))
        print(dd)
    else:
        if dump_mode == "full-metadata":
            fp.write(convert_datatree_to_metadata_json(prod))
        elif dump_mode == "metadata-only":
            fp.write(convert_datatree_to_metadata_structure(prod))
        elif dump_mode == "structure-only":
            fp.write(convert_datatree_to_structure_str(prod))
        elif dump_mode == "structure-and-details":
            fp.write(convert_datatree_to_structure_str(prod, details=True))
        elif dump_mode == "full-datatree":
            fp.write(convert_datatree_to_str(prod))
        else:
            raise NotImplementedError(f"dump_mode {dump_mode!r} is not supported")

    if output:
        fp.close()


def open_path_as_datatree(path: str) -> DataTree:
    if path.endswith(".json"):
        with open(path) as input_fp:
            json_data = json.load(input_fp)
            ptype = json_data.get("recognition", {}).get("product_type")
            if ptype:
                prod = convert_mapping_to_datatree(json_data)
            else:
                prod = open_datatree(path)
    else:
        try:
            prod = load_metadata(path).container()
        except KeyError:
            prod = open_datatree(path)
    return prod
