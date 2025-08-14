import logging
from copy import deepcopy
from typing import Any, Iterable

import dask.array as da
import numpy as np
import xarray as xr
from xarray import DataTree

from sentineltoolbox.api import convert_to_datatree


def _get_shape_from_dim_name(
    _dims: Iterable[Any],
    default_size: int,
    dict_dim_size: dict[str, int] = {"my_variable": 1},
) -> tuple[int, ...]:
    """Associate dimension with shapes using user configuration or default values."""
    _shape = []
    for _dim in list(_dims):
        if _dim in dict_dim_size:
            _shape.append(dict_dim_size[_dim])
        else:
            _shape.append(default_size)
    return tuple(_shape)


def _get_attrs_dtype_array_type_from_attrs_section(dict_: dict[Any, Any]) -> tuple[dict[Any, Any], str, str]:
    """Extract attrs, dtyoe and _array_type fril attrs section in dict_"""
    if "attrs" in dict_:
        attrs_ = dict_["attrs"]
        dtype = attrs_.get("dtype", "float64")
        _array_type = attrs_.get("_array_type", "numpy.ndarray")
    else:
        attrs_ = {}
        dtype = "float64"
        _array_type = "numpy.ndarray"
    return attrs_, dtype, _array_type


def _dims_to_list(_dims: Any) -> list[Any]:
    """Return dimensions as a list"""
    if isinstance(_dims, str):
        return [_dims]
    else:
        return _dims


DICT_FUNC_ARRAY = {
    "numpy.ndarray": lambda size: np.random.choice(range(9999), size=size, replace=False),
    "dask.array.core.Array": lambda size: da.random.randint(low=-1000, high=5000, size=size),
}


def _get_sample_product_from_schema(
    schema: dict[str, Any],
    default_shape: int,
    dimension_shape: dict[str, int] = {"my_dim": 1},
    array_generators: dict[str, Any] = DICT_FUNC_ARRAY,
) -> dict[str, Any] | xr.Dataset | xr.DataArray:
    """Recursive function to create a sample product (with random/pseudo random values) out of
    a scheme describing the product."""

    dt_schema = deepcopy(schema)

    _, dtype, _array_type = _get_attrs_dtype_array_type_from_attrs_section(dt_schema)

    default_func = array_generators[_array_type]

    is_an_xarray_dataset = "data_vars" in dt_schema
    is_an_xarray_dataarray = "dims" in dt_schema

    if is_an_xarray_dataset:

        node = "coords"

        try:
            dt_schema[node]
            has_coords = True
        except KeyError:
            has_coords = False

        if has_coords:
            for coord_name in dt_schema[node]:

                _, dtype, _array_type = _get_attrs_dtype_array_type_from_attrs_section(dt_schema[node][coord_name])

                coord = dt_schema[node][coord_name]

                try:
                    _dims = coord["dims"]
                except KeyError:
                    raise KeyError(
                        f"Expected dims to be specified in the schema for coordinate {coord_name} at node {node}.",
                    )

                _dims = _dims_to_list(_dims)

                shape = _get_shape_from_dim_name(_dims, default_shape, dimension_shape)
                dt_schema[node][coord_name] = (_dims, np.arange(shape[0]))

        node = "data_vars"

        try:
            dt_schema[node]
        except KeyError:
            raise KeyError(
                "node is called coords but is not associated with a data_vars node. This behavior is prohibited: "
                "coords and data_vars are special names for xarray Datasets.",
            )

        for variable_name in dt_schema[node]:

            _, dtype, _array_type = _get_attrs_dtype_array_type_from_attrs_section(dt_schema[node][variable_name])

            variable = dt_schema[node][variable_name]

            try:
                _dims = variable["dims"]
            except KeyError:
                raise KeyError(
                    f"Expected dims to be specified in the schema for variable {variable_name} at node {node}.",
                )

            _dims = _dims_to_list(_dims)

            shape = _get_shape_from_dim_name(_dims, default_shape, dimension_shape)
            dt_schema[node][variable_name] = (_dims, default_func(shape).astype(np.dtype(dtype)))

        if has_coords:
            # xarray Dataset __init__ has no "dims" keyword
            try:
                del dt_schema["dims"]
            except KeyError:
                pass
            return xr.Dataset(
                **dt_schema,
            )

        # I don't use from dict since from_dict expects a coords keyword, which can be absent in simple __init__
        return xr.Dataset(dt_schema["data_vars"])

    elif is_an_xarray_dataarray:

        # Convert dims to a list, in the case dims is a single str (ex: a dataset with one dimension only)
        _dims = dt_schema["dims"]
        if isinstance(_dims, str):
            _dims = [_dims]

        # Associate dimension with shapes using user configuration or default values.
        shape = _get_shape_from_dim_name(_dims, default_shape, dimension_shape)
        dt_schema["data"] = default_func(shape).astype(np.dtype(dtype))

        return xr.DataArray.from_dict(dt_schema)

    elif isinstance(dt_schema, dict):

        for node, expected in dt_schema.items():
            # Recursive call
            dt_schema[node] = _get_sample_product_from_schema(
                expected,
                default_shape,
                dimension_shape,
                array_generators,
            )

    elif dt_schema == "":
        pass

    return dt_schema


def _format_dict(schema: dict[str, Any], parent_key: str = "", sep: str = "/") -> dict[str, Any]:
    """Change dictionary format from {"parent": {"child": {"grandchild": 0}}} to {"parent/child/grandchild": 0}."""

    if "data_vars" in schema:
        return {"/": schema}

    items = []
    for k, v in schema.items():
        if k == "attrs":
            continue
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            if "data_vars" in v:
                items.append((new_key, v))
            else:
                items.extend(_format_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_sample_product_from_schema(schema: dict[str, Any] | None = None, **kwargs: dict[str, Any]) -> DataTree:
    """
    Wrapper function around update_datatree_from_schema to get a sample product from a schema describing the product.
    Please see the documentation of update_datatree_from_schema for further information.
    """
    return update_datatree_from_schema(DataTree(), schema, **kwargs)


def update_datatree_from_schema(
    xdt: DataTree,
    schema: dict[str, Any] | None = None,
    **kwargs: Any,
) -> DataTree:
    """
    Update a DataTree using a schema describing the structure of the DataTree.

    Parameters
    ----------
    xdt :
        The input DataTree. Note that this is currently not used in the function,
        but it's kept for API purposes.
    schema : dict[str, Any] | None, optional
        The schema to use for updating the DataTree. If not provided, a TypeError is raised.
        This behavior might change in the future.
    **kwargs : Any
        Additional keyword arguments.
        - default_shape :
            The default shape to use for the data. Default is 2.
        - dimension_shape :
            A dictionary specifying the shape of each dimension. The default is {},
            meaning default behavior is all dimensions being assigned to a shape of default_shape.
        - array_generators :
            A dictionary of functions to use for generating arrays. Default is DICT_FUNC_ARRAY.
        - logger :
            The logger to use. Default is a logger named "logs" and created within the function.

    Returns
    -------
        The updated DataTree.

    Raises
    ------
    TypeError
        If the schema is not provided or if the type of the dummy product is neither dict nor xr.Dataset.

    Notes
    -----
    This function uses a recursive function `_get_sample_product_from_schema` to generate a sample product based on
    the schema. If the sample product is a dict, it's formatted to match the expected format for DataTree.from_dict
    and then converted to a DataTree. If the dummy product is an xr.Dataset, it's converted to a DataTree using the
    `convert_to_datatree` function.

    This function does not handle variables with unnamed dimensions.
    This function does not handle the creation of attributes yet.
    """

    default_shape = kwargs.get("default_shape", 2)
    dimension_shape = kwargs.get("dimension_shape", {})
    array_generators = kwargs.get("array_generators", DICT_FUNC_ARRAY)
    logger = kwargs.get("logger", logging.getLogger("logs"))
    logger.debug("xdt not used in the current implementation, kept for API purposes.")

    if schema is None:
        raise TypeError("Please specify a schema.")

    dummy_product = _get_sample_product_from_schema(
        schema,
        default_shape,
        dimension_shape,
        array_generators,
    )  # type: ignore
    if isinstance(dummy_product, dict):

        # Format dict to match the expected format for DataTree.from_dict (flat dictionaries)
        dummy_product = _format_dict(dummy_product)

        for key in dummy_product:
            try:
                dummy_product[key].name = key.split("/")[-1]
            except AttributeError:
                pass
        return DataTree.from_dict(dummy_product)

    elif isinstance(dummy_product, xr.Dataset):
        return convert_to_datatree(dummy_product)

    else:
        raise TypeError(
            "get_dummy_product expects a schema of type dict (for DataTree) or xarray dataset "
            "(for convert_to_datatree).",
        )
