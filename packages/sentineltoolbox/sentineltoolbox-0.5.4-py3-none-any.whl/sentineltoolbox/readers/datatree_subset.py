from typing import Literal

import xarray as xr
from xarray import DataTree
from xarray.core.datatree_mapping import map_over_datasets


def map_over_subtree(func):  # type: ignore

    def wrapper_map_over_subtree(*args, **kwargs):  # type: ignore
        return map_over_datasets(func, *args, **kwargs)

    return wrapper_map_over_subtree


@map_over_subtree
def filter_flags(ds: xr.Dataset) -> xr.Dataset:
    """Filter only flags variable while preserving the whole structure
    Following the CF convention, flag variables are filtered based on the presence of "flag_masks" attribute

    Parameters
    ----------
    ds
        input xarray.Dataset or DataTree

    Returns
    -------
        xarray.Dataset or DataTree
    """
    return xr.merge(
        [
            ds.filter_by_attrs(flag_masks=lambda v: v is not None),
            ds.filter_by_attrs(flag_values=lambda v: v is not None),
        ],
    )


def filter_datatree(
    dt: DataTree,
    vars_grps: list[str],
    type: Literal["variables", "groups", "flags"],
) -> DataTree:
    """Filter datatree by selecting a list of given variables or groups

    Parameters
    ----------
    dt
        input DataTree
    vars_grps
        List of variable or group paths
    type
        Defines if the list is made of variables or groups ("variables" or "groups")

    Returns
    -------
        Filtered DataTree

    Raises
    ------
    ValueError
        if incorrect type is provided
    """
    if type == "variables":
        dt = dt.filter(
            lambda node: any(
                "/".join([node.path, var]) in vars_grps for var in node.variables  # type: ignore[list-item]
            ),
        )
        for tree in dt.subtree:
            variables = list(tree.data_vars)
            drop_variables = [v for v in variables if "/".join([tree.path, v]) not in vars_grps]
            if drop_variables:
                tree.ds = tree.ds.drop_vars(drop_variables)
    elif type == "groups":
        # We use startswith to keep also all descendants groups.
        # Append "/" to node.path in filter to allow vars_grps ending with "/".
        dt = dt.filter(lambda node: any((node.path + "/").startswith(grp_path) for grp_path in vars_grps))
    elif type == "flags":
        for tree in dt.subtree:
            variables = list(tree.data_vars)
            drop_variables = [v for v in variables if "flag_masks" in tree[v].attrs or "flag_values" in tree[v].attrs]
            if drop_variables:
                tree.ds = tree.ds.drop_vars(drop_variables)
    else:
        raise ValueError("type as incorrect value: ", type)

    return dt
