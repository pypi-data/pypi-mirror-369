import ast
import collections
import copy
import json
import logging
from typing import Any, Dict, List, Mapping, Union

import jinja2
import numpy as np
import xarray as xr
from jinja2 import Template
from xarray import DataTree

from sentineltoolbox.readers.resources import get_resource_paths

logger = logging.getLogger("sentineltoolbox")


class FakeContext:
    def __getattribute__(self, k: str) -> Any:
        return FakeContext()

    def __missing__(self, k: Any) -> Any:
        return FakeContext()

    def __iter__(self) -> Any:
        yield from [FakeContext()]

    def __str__(self) -> str:
        return "x"


def process_dict_root_attrs(d: Dict[str, Any]) -> Dict[str, Any] | None | list[Any]:
    """
    Process a dictionary by handling 'required', 'value', and 'dtype' attributes.

    Parameters
    ----------
    d : Dict[str, Any]
        The dictionary to process.

    Returns
    -------
    Dict[str, Any] | None
        Processed dictionary or None if the 'required' attribute is False.
    """
    if isinstance(d, dict):
        # Check if the dict has the required structure
        if "required" in d and "value" in d and "dtype" in d:
            # If 'required' is True, replace the dict with the 'value'
            if d["required"]:
                return d["value"]
            else:
                return None
        # If the dict does not match the specific structure, recurse into its values
        else:
            # Recurse into its values
            new_dict = {}
            for k, v in d.items():
                processed_value = process_dict_root_attrs(v)
                if processed_value is not None:
                    new_dict[k] = processed_value
            return new_dict
    elif isinstance(d, list):
        # If we encounter a list, apply the function to each element
        return [item for item in (process_dict_root_attrs(item) for item in d) if item is not None]
    else:
        # If the value is neither a dict nor a list, return it as is
        return d


def create_nd_array(shape: List[Union[str, ast.AST]], dtype: np.dtype[Any]) -> np.ndarray[Any, Any]:
    """
    Create an n-dimensional array with the specified shape and data type.

    Parameters
    ----------
    shape : list of str or ast.AST
        The shape of the array as a list of strings. Each string is evaluated to determine the dimension size.
    dtype : np.dtype
        The data type of the array.

    Returns
    -------
    np.ndarray
        The created n-dimensional array.
    """
    # Evaluate each element in the shape list to an integer
    evaluated_shape = [ast.literal_eval(dim) if isinstance(dim, str) else dim for dim in shape]

    # Convert all elements to integers if they are not already
    shape_tuple = tuple(int(dim) for dim in evaluated_shape)

    # Create an array with the specified shape
    array = np.full(shape_tuple, np.nan, dtype=dtype)
    return array


def create_tree(parent: DataTree, path: str, content: Dict[str, Any]) -> None:
    parts = path.strip("/").split("/")
    for i, part in enumerate(parts):
        # Check if the part already exists as a child
        existing_child = next((child for value, child in parent.children.items() if child.name == part), None)
        if existing_child:
            parent = existing_child
        else:
            # If this is the last part, add the data
            if i == len(parts) - 1:
                attrs = content.get("attrs", {})
                data_vars = content.get("data_vars", {})
                coords = content.get("coords", {})

                # Create datasets for coords and data_vars
                coord_data = {}
                for coord_name, coord_info in coords.items():
                    dtype = np.dtype(coord_info["attrs"]["dtype"])
                    coord_data[coord_name] = xr.DataArray(
                        data=create_nd_array(coord_info["dims"].values(), dtype),
                        dims=coord_info["dims"].keys(),
                        attrs=coord_info["attrs"],
                    )

                data_var_data = {}
                for var_name, var_info in data_vars.items():
                    dtype = np.dtype(var_info["attrs"]["dtype"])
                    data_var_data[var_name] = xr.DataArray(
                        data=create_nd_array(var_info["dims"].values(), dtype),
                        dims=var_info["dims"].keys(),
                        attrs=var_info["attrs"],
                    )

                # Combine coords and data_vars into a dataset
                dataset = xr.Dataset(data_vars=data_var_data, coords=coord_data, attrs=attrs)

                # Add the dataset to the current node

                parent[part] = DataTree(dataset=dataset)
            else:
                # Create a new child node if it doesn't exist
                parent[part] = DataTree()
                parent = parent[part]  # type: ignore


def create_from_template(data_variables: Dict[str, Any]) -> DataTree:
    """
    Builds a DataTree object from a dictionary of data variables.

    Args:
        data_variables (Dict[str, Any]): Dictionary with data variables and attributes.

    Returns:
        DataTree: DataTree object containing the dataset.
    """
    # Initialize the root DataTree node
    root_attrs = data_variables["data"]["/"]["attrs"]

    root: DataTree = DataTree(name="root")
    root.attrs = root_attrs

    # Function to create DataTree nodes recursively

    # Start the recursive creation of the tree
    for path, content in data_variables["data"].items():
        if path != "/":
            create_tree(root, path, content)

    return root


def update_dict_recursively(
    original_dict: Dict[str, Any],
    dict_used_to_update: Mapping[Any, Any],
) -> Dict[str, Any]:
    """
    Recursively update a dictionary with another dictionary's values.

    Parameters
    ----------
    original_dict : dict
        The original dictionary to update.
    dict_used_to_update : dict
        The dictionary with updates.

    Returns
    -------
    dict
        The updated dictionary.
    """
    for k, v in dict_used_to_update.items():
        if isinstance(v, collections.abc.Mapping):
            original_dict[k] = update_dict_recursively(original_dict.get(k, {}), v)
        else:
            original_dict[k] = v
    return original_dict


def get_jinja_template(*, product_type: str | None = None, **kwargs: Any) -> Template:
    if product_type is None:
        raise NotImplementedError("Please specify product type")

    template_folders = []
    try:
        template_folders.extend(get_resource_paths("templates/jinja_template", module="eopf.product"))
    except (FileNotFoundError, ModuleNotFoundError):
        pass
    template_folders.extend(get_resource_paths("templates/jinja_template"))
    filename = product_type
    if not filename.endswith(".jinja"):
        filename += ".jinja"
    folder_str = ",\n  * ".join([str(p) for p in template_folders])
    logger.debug(f"Search {filename!r} template in {len(template_folders)} directories:\n  * {folder_str}")

    for template_folder in template_folders:
        template_path = template_folder / filename
        if template_path.is_file():
            logger.info(f"Found template {template_path}")
            with open(str(template_path)) as f:
                template_str = f.read()
            template = Template(template_str)
            return template
    raise FileNotFoundError(str(product_type))


def render_template_as_json(template: jinja2.Template, **kwargs: Any) -> dict[Any, Any]:
    rendered_str = template.render({"context": FakeContext()})
    context_jinja = json.loads(rendered_str).get("context", FakeContext())
    update_dict_recursively(context_jinja, kwargs.get("context", {}))
    rendered_str = template.render(context=context_jinja)
    template_json = json.loads(rendered_str)
    template_json["context"] = context_jinja
    return template_json


def fill_template_with_default_values(template: dict[Any, Any]) -> dict[Any, Any]:
    """
    Replace definition block by values
    Example:
    - {"required": True, "dtype": "int"} -> 0
    - {"required": True, "dtype": "float", value="1"} -> 1.0

    :param template:
    :return:
    """
    simple_json = copy.deepcopy(template)
    for attr_dictionary in ["stac_discovery", "other_metadata"]:
        try:
            simple_json["data"]["/"]["attrs"][attr_dictionary] = process_dict_root_attrs(
                simple_json["data"]["/"]["attrs"][attr_dictionary],
            )
        except KeyError:
            pass
    return simple_json
