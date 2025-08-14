import copy
from pathlib import PurePosixPath
from typing import Any, Mapping, MutableMapping, Tuple, TypeAlias

import numpy as np
from dask.array.core import Array
from xarray import DataArray, Dataset, DataTree

from sentineltoolbox.datatree_utils import DataTreeHandler
from sentineltoolbox.typedefs import (
    KEYID_GROUP_ATTRIBUTES,
    L_ToDictDataOptions,
    is_eoproduct,
)

try:
    from eopf import EOProduct
except (ImportError, TypeError):
    EOProduct: TypeAlias = Any  # type: ignore


VALID_CONVERTER_FORMATS = ["nested-datatree", None]


def _dataset_path(dataset: Dataset, key: str) -> str:
    if dataset.name:
        return f"{dataset.name}/{key}"
    else:
        return key


def fix_json_xarray(dic: dict[str, Any]) -> dict[str, Any]:
    """

    :param dic:
    :return:
    """
    dic = copy.copy(dic)
    # group
    if ("attrs" in dic or "data_vars" in dic) and "data" not in dic:
        for field in ("attrs", "data_vars", "coords", "dims"):
            dic[field] = dic.get(field, {})
        for path, variable in dic["data_vars"].items():
            dic["data_vars"][path] = fix_json_xarray(variable)
    # variable
    elif "data" in dic:
        dic["dims"] = dic.get("dims", ())
    else:
        raise TypeError(dic)

    return dic


def fix_datatype(dt: DataTree, dtype_mapping: dict[Any, Any] | None = None) -> None:
    if dtype_mapping is None:
        dtype_mapping = {"int32": np.int64}
    for ds in dt.subtree:
        for var_name, data_array in ds.data_vars.items():
            stype = str(data_array.dtype)
            try:
                ds[var_name] = data_array.astype(dtype_mapping[stype])
            except KeyError:
                pass


def _fix_dtype_and_value_formatting(dtype: Any, value: Any) -> Tuple[Any, Any]:
    """Function to fix problems encountered when converting type and value, for example
    with Sentinel 3 SLSTR L1 ADF SL1PP"""
    if dtype in ("STRING", "string"):
        dtype = str

    elif dtype in ("DOUBLE", "double"):
        dtype = np.float64
        if value == "":  # ex: value == ""
            value = np.empty(0)

    elif dtype in ("INTEGER", "integer"):
        if isinstance(value, str) and " " in value:  # ex: value == "0 0 0 0 0 0 0 0"
            value = [int(v) for v in list(value) if v != " "]

        elif value == "":  # ex: value == ""
            value = np.empty(0)

        dtype = np.int64
    elif isinstance(dtype, str) and "array" in dtype:
        dtype = dtype.replace("array", "").lstrip("[").rstrip("]")
    return dtype, value


def convert_json_to_datatree(json_dict: dict[Any, Any], path: str = "/") -> DataTree:
    datasets: MutableMapping[str, Dataset | DataTree | None] = {}
    variables = {}
    attrs = {}
    for k, v in json_dict.items():
        if isinstance(v, dict):
            if "value" in v and "type" in v:
                value = v.pop("value")
                dtype = v.pop("type")
                dtype, value = _fix_dtype_and_value_formatting(dtype, value)
                if value is None:
                    a = None
                else:
                    a = np.array(value, dtype=dtype)
                if isinstance(value, list) and a is not None:
                    dims = [f"{k}_{i}" for i, _ in enumerate(a.shape)]
                else:
                    dims = None
                variables[k] = DataArray(a, attrs=v, dims=dims)
            elif k == "attrs" and isinstance(v, dict):
                attrs.update(v)
            elif k in ("stac_discovery", "metadata", "properties"):
                attrs[k] = v
            else:
                datasets[k] = convert_json_to_datatree(v, path + k + "/")
        else:
            attrs[k] = v
    if variables:
        datasets["/"] = Dataset(data_vars=variables, attrs=attrs)

    dt = DataTree.from_dict(datasets)
    dt.attrs.update(attrs)
    return dt


def convert_datatree_to_dataset(dt: DataTree) -> Dataset:
    flat_ds = Dataset(attrs=dt.attrs)
    for ds in dt.subtree:
        if ds.name and ds.attrs:
            flat_ds.attrs.setdefault(KEYID_GROUP_ATTRIBUTES, {})[ds.name] = ds.attrs
        for k, v in ds.variables.items():
            flat_ds[_dataset_path(ds, k)] = v
        for k, c in ds.coords.items():
            flat_ds[_dataset_path(ds, k)] = c
    return flat_ds


def convert_dataset_to_datatree(dataset: Dataset) -> DataTree:
    datatree: DataTree = DataTree()
    attribs = copy.copy(dataset.attrs)
    if KEYID_GROUP_ATTRIBUTES in attribs:
        group_attribs = attribs.pop(KEYID_GROUP_ATTRIBUTES)
    else:
        group_attribs = {}
    datatree.attrs.update(attribs)
    for path, variable in dataset.items():
        pathstr = str(path)
        if isinstance(variable, (DataArray, Array, np.ndarray)):
            datatree[pathstr] = variable
        else:
            try:
                datatree[pathstr]
            except KeyError:
                datatree[pathstr] = DataTree(name=PurePosixPath(pathstr).name)
            datatree[pathstr].attrs.update(variable.attrs)
    for path, attrs in group_attribs.items():
        pathstr = str(path)
        # DO NOT USE path in datatree. Doesn't behave as expected
        # DO NOT USE
        #   group = DataTree(...)
        #   datatree[path] = group
        #   use(group) # 'group' and 'datatree[path]' are differents
        if isinstance(attrs, str):
            # consider it is a global attribute, not a group
            datatree.attrs[pathstr] = attrs
        else:
            try:
                datatree[pathstr]
            except KeyError:
                datatree[pathstr] = DataTree(name=PurePosixPath(pathstr).name)
            datatree[pathstr].attrs.update(attrs)

    return datatree


def convert_eoproduct20_to_datatree(eoproduct: EOProduct) -> DataTree:
    dt: DataTree = DataTree(name=eoproduct.name)
    dt.attrs.update(eoproduct.attrs)  # type: ignore
    for obj in eoproduct.walk():
        if isinstance(obj.data, DataArray):  # type: ignore
            dt[str(obj.path)] = obj.data  # type: ignore
        else:
            dt[str(obj.path)] = DataTree(name=obj.name)
        dt[str(obj.path)].attrs.update(obj.attrs)  # type: ignore
    hdl = DataTreeHandler(dt)
    hdl.set_short_names(eoproduct.short_names)
    return dt


def convert_dict_to_datatree(data: dict[Any, Any]) -> DataTree:
    if "data_vars" in data:
        json = fix_json_xarray(data)
        ds = Dataset.from_dict(json)
        xdt = convert_dataset_to_datatree(ds)
    else:
        xdt = convert_json_to_datatree(data)
    fix_datatype(xdt)
    return xdt


def convert_to_dict(data: Any, **kwargs: Any) -> dict[Any, Any]:
    output_format = kwargs.get("output_format")
    if output_format not in VALID_CONVERTER_FORMATS:
        raise NotImplementedError(f"{output_format=!r} is not recognized")
    input_format = kwargs.get("output_format")
    if input_format not in VALID_CONVERTER_FORMATS:
        raise NotImplementedError(f"{input_format=!r} is not recognized")

    if isinstance(data, dict):
        return data
    elif isinstance(data, DataTree) and output_format == "nested-datatree":
        return convert_datatree_to_nested_dict(data, **kwargs)
    else:
        raise NotImplementedError(f"Cannot convert {type(data)} to dict")


def convert_to_datatree(data: Any, **kwargs: Any) -> DataTree:
    """

    :param data:
    :return:
    """
    output_format = kwargs.get("output_format")
    if output_format not in VALID_CONVERTER_FORMATS:
        raise NotImplementedError(f"{output_format=!r} is not recognized")
    input_format = kwargs.get("output_format")
    if input_format not in VALID_CONVERTER_FORMATS:
        raise NotImplementedError(f"{input_format=!r} is not recognized")

    if isinstance(data, DataTree):
        return data

    original_data = data
    if isinstance(data, Dataset):
        data = convert_dataset_to_datatree(data)
    elif isinstance(data, dict):
        if input_format == "nested-datatree":
            data = convert_nested_dict_to_datatree(data)
        else:
            data = convert_dict_to_datatree(data)
    elif is_eoproduct(data):
        return convert_eoproduct20_to_datatree(data)
    else:
        data = data.__class__.__module__ + "." + data.__class__.__name__

    if isinstance(data, str):
        raise NotImplementedError(f"{type(original_data)} {data}")
    else:
        return data


def convert_datatree_to_nested_dict(
    xdt: DataTree,
    data: L_ToDictDataOptions = "list",
    encoding: bool = False,
    absolute_details: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Convert this DataTree to a dictionary following xarray naming conventions.

    The iteration over the tree is effectuated with :py:meth:`DataTree.subtree`.

    The initial creation of node dictionaries is delegated to :py:meth:`Dataset.to_dict`,
    using the immutable Dataset-like view provided by :py:attr:`DataTree.ds`.

    If this method is used with the final aim of dumping the tree to JSON, be cautious
    that while Python dictionaries are ordered, their equivalent JSON objects are not.
    Thus, the order of children nodes as well as data variables is not guaranteed
    with the JSON representation.

    The children key will be associated to the children nodes, while the data_vars
    key will be associated to data variables. The ``data_vars`` associated lists will
    be empty if the tree is hollow, ie. if only leaves carry data.

    The ``name`` attribute is an addition to the Dataset dict serialization.
    Like a Dataset contains named DataArrays, each Dataset is enriched by becoming
    a named node in the DataTree. ``children`` is to DataTree as
    ``data_vars`` is to Dataset.

    Parameters
    ----------
    data : bool or {"list", "array"}, default: "list"
        Whether to include the actual data in the dictionary. When set to
        False, returns just the schema. If set to "array", returns data as
        underlying array type. If set to "list" (or True for backwards
        compatibility), returns data in lists of Python data types. Note
        that for obtaining the "list" output efficiently, use
        ``ds.compute().to_dict(data="list")``.
    encoding : bool, default: False
        Whether to include the Dataset's encoding in the dictionary.
    absolute_details : bool, default: False
        Whether to include additional absolute details: ``path``, ``level``,
        ``depth``, `width`, ``is_root`` and ``is_leaf`` in the dictionary.
        Absolute is in the sense that such information contribute to situating
        a node in the root-tree hierarchy. These are not mandatory information
        to reconstruct the root DataTree. Disable if the nodes must remain
        agnostic of their surrounding hierarchy.

    Returns
    -------
    d : dict
        Recursive dictionary inherited key from :py:meth:`Dataset.to_dict`:
        "coords", "attrs", "dims", "data_vars" and optionally "encoding", as
        well as DataTree-specific keys: "name", "children" and optionally
        "path", "is_root", "is_leaf", "level", "depth", "width"

    See Also
    --------
    convert_dict_to_datatree
    Dataset.from_dict
    Dataset.to_dict
    """

    super_root_dict: dict[str, Any] = {"children": {}}
    for node in xdt.subtree:
        node_dict = node.ds.to_dict(data=data, encoding=encoding)
        node_dict["name"] = node.name
        if absolute_details:
            node_dict.update(
                {
                    "path": node.path,
                    "is_root": node.is_root,
                    "is_leaf": node.is_leaf,
                    "level": node.level,
                    "depth": node.depth,
                    "width": node.width,
                },
            )
        node_dict["children"] = {}
        parts = PurePosixPath(node.path).parts
        current_dict = super_root_dict
        for part in parts[:-1]:
            current_dict = current_dict["children"].get(part, {})
        current_dict["children"][parts[-1]] = node_dict
    root_dict = super_root_dict["children"]["/"]
    return root_dict


def convert_nested_dict_to_datatree(node_dict: Mapping[Any, Any]) -> DataTree:
    """Convert a dictionary into a DataTree.

    Parameters
    ----------
    d : dict-like
        Mapping representing a serialized DataTree

    Returns
    -------
    obj : DataTree

    See also
    --------
    convert_datatree_to_dict
    Dataset.to_dict
    DataArray.from_dict

    Examples
    --------
    >>> import xarray.core.datatree as dt
    >>> basic_dict = {
    ...     "coords": {
    ...         "time": {
    ...             "dims": ("time",),
    ...             "attrs": {"units": "date", "long_name": "Time of acquisition"},
    ...             "data": ["2020-12-01", "2020-12-02"],
    ...         }
    ...     },
    ...     "attrs": {
    ...         "description": "Root Hypothetical DataTree with heterogeneous data: weather and satellite"
    ...     },
    ...     "dims": {"time": 2},
    ...     "data_vars": {},
    ...     "name": "(root)",
    ...     "children": {
    ...         "weather_data": {
    ...             "coords": {
    ...                 "station": {
    ...                     "dims": ("station",),
    ...                     "attrs": {
    ...                         "units": "dl",
    ...                         "long_name": "Station of acquisition",
    ...                     },
    ...                     "data": ["a", "b", "c", "d", "e", "f"],
    ...                 }
    ...             },
    ...             "attrs": {
    ...                 "description": "Weather data node, inheriting the 'time' dimension"
    ...             },
    ...             "dims": {"station": 6, "time": 2},
    ...             "data_vars": {
    ...                 "wind_speed": {
    ...                     "dims": ("time", "station"),
    ...                     "attrs": {
    ...                         "units": "meter/sec",
    ...                         "long_name": "Wind speed",
    ...                     },
    ...                     "data": [
    ...                         [2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
    ...                         [2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
    ...                     ],
    ...                 },
    ...                 "pressure": {
    ...                     "dims": ("time", "station"),
    ...                     "attrs": {
    ...                         "units": "hectopascals",
    ...                         "long_name": "Time of acquisition",
    ...                     },
    ...                     "data": [
    ...                         [3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
    ...                         [3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
    ...                     ],
    ...                 },
    ...             },
    ...             "name": "weather_data",
    ...             "children": {
    ...                 "temperature": {
    ...                     "coords": {},
    ...                     "attrs": {
    ...                         "description": (
    ...                             "Temperature, subnode of the weather data node, inheriting the 'time' dimension "
    ...                             "from root and 'station' dimension from the Temperature group."
    ...                         )
    ...                     },
    ...                     "dims": {"time": 2, "station": 6},
    ...                     "data_vars": {
    ...                         "air_temperature": {
    ...                             "dims": ("time", "station"),
    ...                             "attrs": {
    ...                                 "units": "kelvin",
    ...                                 "long_name": "Air temperature",
    ...                             },
    ...                             "data": [
    ...                                 [3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
    ...                                 [3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
    ...                             ],
    ...                         },
    ...                         "dewpoint_temp": {
    ...                             "dims": ("time", "station"),
    ...                             "attrs": {
    ...                                 "units": "kelvin",
    ...                                 "long_name": "Dew point temperature",
    ...                             },
    ...                             "data": [
    ...                                 [4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
    ...                                 [4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
    ...                             ],
    ...                         },
    ...                     },
    ...                     "name": "temperature",
    ...                     "children": {},
    ...                 }
    ...             },
    ...         },
    ...         "satellite_image": {
    ...             "coords": {
    ...                 "x": {"dims": ("x",), "attrs": {}, "data": [10, 20, 30]},
    ...                 "y": {"dims": ("y",), "attrs": {}, "data": [90, 80, 70]},
    ...             },
    ...             "attrs": {},
    ...             "dims": {"x": 3, "y": 3, "time": 2},
    ...             "data_vars": {
    ...                 "infrared": {
    ...                     "dims": ("time", "y", "x"),
    ...                     "attrs": {},
    ...                     "data": [
    ...                         [[5.0, 5.0, 5.0], [5.0, 5.0, 5.0], [5.0, 5.0, 5.0]],
    ...                         [[5.0, 5.0, 5.0], [5.0, 5.0, 5.0], [5.0, 5.0, 5.0]],
    ...                     ],
    ...                 },
    ...                 "true_color": {
    ...                     "dims": ("time", "y", "x"),
    ...                     "attrs": {},
    ...                     "data": [
    ...                         [[6.0, 6.0, 6.0], [6.0, 6.0, 6.0], [6.0, 6.0, 6.0]],
    ...                         [[6.0, 6.0, 6.0], [6.0, 6.0, 6.0], [6.0, 6.0, 6.0]],
    ...                     ],
    ...                 },
    ...             },
    ...             "name": "satellite_image",
    ...             "children": {},
    ...         },
    ...     },
    ... }
    >>> convert_nested_dict_to_datatree(basic_dict) # doctest: +SKIP
    DataTree('(root)', parent=None)
    │   Dimensions:  (time: 2)
    │   Coordinates:
    │     * time     (time) <U10 80B '2020-12-01' '2020-12-02'
    │   Data variables:
    │       *empty*
    │   Attributes:
    │       description:  Root Hypothetical DataTree with heterogeneous data: weather...
    ├── DataTree('weather_data')
    │   │   Dimensions:     (station: 6, time: 2)
    │   │   Coordinates:
    │   │     * station     (station) <U1 24B 'a' 'b' 'c' 'd' 'e' 'f'
    │   │   Dimensions without coordinates: time
    │   │   Data variables:
    │   │       wind_speed  (time, station) float64 96B 2.0 2.0 2.0 2.0 ... 2.0 2.0 2.0 2.0
    │   │       pressure    (time, station) float64 96B 3.0 3.0 3.0 3.0 ... 3.0 3.0 3.0 3.0
    │   │   Attributes:
    │   │       description:  Weather data node, inheriting the 'time' dimension
    │   └── DataTree('temperature')
    │           Dimensions:          (time: 2, station: 6)
    │           Dimensions without coordinates: time, station
    │           Data variables:
    │               air_temperature  (time, station) float64 96B 3.0 3.0 3.0 3.0 ... 3.0 3.0 3.0
    │               dewpoint_temp    (time, station) float64 96B 4.0 4.0 4.0 4.0 ... 4.0 4.0 4.0
    │           Attributes:
    │               description:  Temperature, subnode of the weather data node, inheriting t...
    └── DataTree('satellite_image')
            Dimensions:     (x: 3, y: 3, time: 2)
            Coordinates:
              * x           (x) int64 24B 10 20 30
              * y           (y) int64 24B 90 80 70
            Dimensions without coordinates: time
            Data variables:
                infrared    (time, y, x) float64 144B 5.0 5.0 5.0 5.0 ... 5.0 5.0 5.0 5.0
                true_color  (time, y, x) float64 144B 6.0 6.0 6.0 6.0 ... 6.0 6.0 6.0 6.0
    """

    obj: DataTree = DataTree(
        name=node_dict.get("name", None),
        dataset=Dataset.from_dict(node_dict),
        children={
            child_name: convert_nested_dict_to_datatree(child_node_dict)
            for child_name, child_node_dict in node_dict.get("children", {}).items()
        },
    )
    return obj
