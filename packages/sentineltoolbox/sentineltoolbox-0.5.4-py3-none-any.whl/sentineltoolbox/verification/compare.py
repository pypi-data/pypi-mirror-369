# Copyright 2024 ACRI-ST
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import warnings
from contextlib import contextmanager
from typing import Any, Generator

import dask.array as da
import numpy as np
import pandas as pd
import xarray as xr
from sklearn.metrics import confusion_matrix
from xarray import DataTree
from xarray.core.datatree_mapping import map_over_datasets

from sentineltoolbox.filesystem_utils import get_fsspec_filesystem
from sentineltoolbox.readers.datatree_subset import filter_datatree

try:
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay
except ImportError:
    PLOT_AVAILABLE = False
else:
    PLOT_AVAILABLE = True

logger = logging.getLogger("sentineltoolbox.verification")


@contextmanager
def suppress_numpy_warnings() -> Generator[None, None, None]:
    """Context manager to temporarily suppress specific numpy warnings.

    This suppresses warnings for:
    - All-NaN slice encountered
    - Invalid value encountered in divide
    - Mean of empty slice
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(action="ignore", message="All-NaN slice encountered")
        warnings.filterwarnings(action="ignore", message="invalid value encountered in divide")
        warnings.filterwarnings(action="ignore", message="Mean of empty slice")
        warnings.filterwarnings(action="ignore", message="divide by zero encountered in divide")
        yield


def map_over_subtree(func):  # type: ignore

    def wrapper_map_over_subtree(*args, **kwargs):  # type: ignore
        return map_over_datasets(func, *args, **kwargs)

    return wrapper_map_over_subtree


# Formatted string when test fails
def _get_failed_formatted_string_vars(
    name: str,
    values: list[Any],
    threshold_nb_outliers: float,
    threshold_coverage: float,
) -> str:
    with suppress_numpy_warnings():
        relative = values[11]
        threshold = np.unique(values[12])

        # Base stats depending on relative/absolute mode
        if relative:
            base_stats = (
                f"{name}: "
                f"min={values[0]*100:8.4f}% "
                f"max={values[1]*100:8.4f}% "
                f"mean={values[2]*100:8.4f}% "
                f"stdev={values[3]*100:8.4f}% "
                f"median={values[4]*100:8.4f}% "
                f"mse={values[5]:9.6f} "
                f"psnr={20 * np.log10(values[6]/values[5]):9.6f}dB -- "
                f"eps={threshold*100}%"
            )
        else:
            base_stats = (
                f"{name}: "
                f"min={values[0]:9.6f} "
                f"max={values[1]:9.6f} "
                f"mean={values[2]:9.6f} "
                f"stdev={values[3]:9.6f} "
                f"median={values[4]:9.6f} "
                f"mse={values[5]:9.6f} "
                f"psnr={20 * np.log10(values[6]/values[5]):9.6f}dB -- "
                f"eps={threshold}"
            )

        # Add outliers and coverage stats
        return (
            f"{base_stats} "
            f"outliers={values[7]} (={values[7]/values[8]*100:.3f}% allowed={threshold_nb_outliers*100}%) "
            f"coverage={values[10]/values[9]*100:+.3f}% (allowed={threshold_coverage*100}%)"
        )


def _get_failed_formatted_string_flags(
    name: str,
    ds: xr.Dataset,
    bit: int,
    threshold_nb_outliers: float,
) -> str:
    with suppress_numpy_warnings():
        return (
            f"{name} ({ds.bit_position.data[bit]})({ds.bit_meaning.data[bit]}): "
            f"equal_pix={ds.equal_percentage.data[bit]:8.4f}% "
            f"diff_pix={ds.different_percentage.data[bit]:8.4f}% -- "
            f"outliers={ds.different_count.data[bit]} "
            f"(={ds.different_count.data[bit]/ds.total_bits.data[bit]*100:.3f}% allowed={threshold_nb_outliers*100}%)"
        )


def _get_passed_formatted_string_flags(name: str, ds: xr.Dataset, bit: int) -> str:
    return f"{name} ({ds.bit_position.data[bit]})({ds.bit_meaning.data[bit]})"


# Function to get leaf paths
def get_leaf_paths(paths: list[str]) -> list[str]:
    """Given a list of tree paths, returns leave paths

    Parameters
    ----------
    paths
        list of tree structure path

    Returns
    -------
        leaf paths
    """
    leaf_paths = []
    for i in range(len(paths)):
        if i == len(paths) - 1 or not paths[i + 1].startswith(paths[i] + "/"):
            leaf_paths.append(paths[i])
    return leaf_paths


def sort_datatree(tree: DataTree) -> DataTree:
    """Alphabetically sort DataTree nodes by tree name

    Parameters
    ----------
    tree
        input `DataTree`

    Returns
    -------
        Sorted `DataTree`
    """
    paths = tree.groups
    sorted_paths = sorted(paths)

    if tuple(sorted_paths) == paths:
        logger.debug(f"No need to sort {tree.name}")
        return tree
    else:
        logger.debug(f"Sorting {tree.name}")
        sorted_tree: DataTree = DataTree(tree.to_dataset(), name=tree.name)
        for p in sorted_paths[1:]:
            sorted_tree[p] = tree[p]
        return sorted_tree


def encode_time_dataset(ds: xr.Dataset) -> xr.Dataset:
    for name, var in ds.data_vars.items():
        if var.dtype == np.dtype("timedelta64[ns]") or var.dtype == np.dtype(
            "datetime64[ns]",
        ):
            ds[name] = var.astype(int)
    return ds


def encode_time_datatree(dt: DataTree) -> DataTree:
    for tree in dt.subtree:
        for name, var in tree.data_vars.items():
            if var.dtype == np.dtype("timedelta64[ns]") or var.dtype == np.dtype(
                "datetime64[ns]",
            ):
                tree[name] = var.astype(int)
        for name, coord in tree.coords.items():
            if coord.dtype == np.dtype("timedelta64[ns]") or coord.dtype == np.dtype(
                "datetime64[ns]",
            ):
                tree[name] = coord.astype(int)
                # tree[name].drop_duplicates(name)
    return dt


@map_over_subtree
def encode_time(ds: xr.Dataset) -> xr.Dataset:
    # Create a mutable copy of the dataset to avoid DatasetView mutation error
    ds_mutable = ds.copy()
    for name, var in ds_mutable.data_vars.items():
        if var.dtype == np.dtype("timedelta64[ns]") or var.dtype == np.dtype(
            "datetime64[ns]",
        ):
            ds_mutable[name] = var.astype(int)
    return ds_mutable


@map_over_subtree
def drop_duplicates(ds: xr.Dataset) -> xr.Dataset:
    """Drop duplicate values

    Parameters
    ----------
    ds
        input `xarray.Dataset` or `DataTree`

    Returns
    -------
        `xarray.Dataset` or `DataTree`
    """
    return ds.drop_duplicates(dim=...)


@map_over_subtree
def count_outliers(err: xr.Dataset, threshold: float | xr.Dataset) -> xr.Dataset:
    """For all variables of a `xarray.Dataset/DataTree`, count the number of outliers, exceeding the
    threshold value

    Parameters
    ----------
    err
        input `xarray.Dataset` or `DataTree`
    threshold
        Threshold value, either a float to use the same threshold for all variables,
        or a Dataset with matching structure to use different thresholds per variable

    Returns
    -------
        reduced count `xarray.Dataset` or `DataTree`
    """
    return err.where(abs(err) > threshold, np.nan).count(keep_attrs=True)


@map_over_subtree
def drop_coordinates(ds: xr.Dataset) -> xr.Dataset:
    """Remove all coordinates of a `DataTree

    Parameters
    ----------
    ds
        input `xarray.Dataset` or `DataTree`

    Returns
    -------
        `xarray.Dataset` or `DataTree`
    """
    return ds.drop_vars(ds.coords)


def compute_array_median(array: xr.DataArray) -> xr.DataArray:
    """Compute the median of a DataArray.
    It excludes NaN and it accounts for dask.array in which case the array
    needs to be explicitely flatten first

    Parameters
    ----------
    array
        input xr.DataArray

    Returns
    -------
        reduced DataArray with median
    """
    if isinstance(array.data, da.core.Array):
        return da.nanmedian(da.ravel(array), axis=0)
    else:
        return array.median(skipna=True)


@map_over_subtree
def compute_median(ds: xr.Dataset) -> xr.Dataset:
    """Compute the median of a DataTree, excluding NaN

    Parameters
    ----------
    ds
        input xr.Dataset

    Returns
    -------
        reduced Dataset with median
    """

    median_dict = {var: compute_array_median(ds[var]) for var in ds}
    return xr.Dataset(median_dict)


def _compute_reduced_datatree(tree: DataTree, results: dict[str, Any] | None = None) -> dict[str, Any]:
    if not results:
        results = {}

    for tree in tree.subtree:
        for name, var in tree.variables.items():
            key = "/".join([tree.path, str(name)])
            if key in results:
                results[key].append(var.compute().data)
            else:
                results[key] = [var.compute().data]
            # results[name]=[var.compute().data]

    return results


def _get_coverage(tree: DataTree, results: dict[str, Any] | None = None) -> dict[str, Any]:
    if not results:
        results = {}

    for tree in tree.subtree:
        for name, var in tree.variables.items():
            key = "/".join([tree.path, str(name)])
            nb_valid = var.count().values
            nb_total = var.size
            if key in results:
                results[key].append(nb_valid)
                results[key].append(nb_total)
            else:
                results[key] = [nb_valid, nb_total]

    return results


@map_over_subtree
def apply_where_condition(ds: xr.Dataset, condition: xr.Dataset) -> xr.Dataset:
    """Apply a where condition to mask values in a Dataset based on a condition Dataset

    Parameters
    ----------
    ds
        input Dataset to apply the condition to
    condition
        Dataset containing the boolean condition mask to apply

    Returns
    -------
        Dataset with values masked according to the condition
    """
    return ds.where(condition)


@map_over_subtree
def compute_relative_mode(ds: xr.Dataset, relative: bool, absolute: bool) -> xr.Dataset:
    """Compute relative comparison boolean mode for each variable.

    Parameters
    ----------
    ds : xr.Dataset
        Input dataset
    relative : bool
        If True, force relative mode for all variables
    absolute : bool
        If True, force absolute mode for all variables

    Returns
    -------
    xr.Dataset
        New dataset with scalar boolean values indicating relative mode for each variable
    """
    result = ds.copy()
    for name, var in result.variables.items():
        # Determine the mode value based on flags
        if relative:
            value = True  # Force relative mode
        elif absolute:
            value = False  # Force absolute mode
        else:
            # Default: relative except for packed variables
            scale_factor = var.encoding.get("scale_factor", None)
            value = scale_factor is None

        # Create scalar with preserved attributes and encoding
        scalar = xr.DataArray(value)
        scalar.attrs.update(var.attrs)
        scalar.encoding.update(var.encoding)
        result[name] = scalar

    return result


@map_over_subtree
def compute_threshold(ds: xr.Dataset, relative_mode: xr.Dataset, threshold: float) -> xr.Dataset:
    """Compute threshold values for each variable based on their mode.

    Parameters
    ----------
    ds : xr.Dataset
        Input dataset
    relative_mode : xr.Dataset
        Boolean dataset indicating which variables use relative mode
    threshold : float
        Base threshold value

    Returns
    -------
    xr.Dataset
        New dataset with scalar threshold values for each variable
    """
    result = ds.copy()
    for name, var in result.variables.items():
        # Determine threshold value based on mode and encoding
        if relative_mode[name]:
            value = threshold  # Use base threshold for relative mode
        else:
            # For absolute mode, check if variable is packed
            scale_factor = var.encoding.get("scale_factor", None)
            if scale_factor is not None:
                value = scale_factor * 1.5  # Special threshold for packed variables
            else:
                value = threshold  # Use base threshold

        # Create DataArray with same shape as input
        scalar = xr.full_like(var, value, dtype=np.float64)
        if relative_mode[name]:
            zero_ref = ds[name] == 0
            try:
                res = np.float64(np.finfo(var.dtype).resolution)
            except ValueError:
                res = np.float64(0.0)
            scalar = xr.where(zero_ref, res, value)
        scalar.attrs.update(var.attrs)
        scalar.encoding.update(var.encoding)
        result[name] = scalar

    return result


@map_over_subtree
def compute_error(diff: xr.Dataset, ref_ds: xr.Dataset, relative_mode: xr.Dataset) -> xr.Dataset:
    """Compute error based on absolute difference, reference dataset and relative mode.

    Parameters
    ----------
    diff : xr.Dataset
        Absolute difference dataset
    ref_ds : xr.Dataset
        Reference dataset
    relative_mode : xr.Dataset
        Dataset with scalar boolean values indicating relative mode for each variable

    Returns
    -------
    xr.Dataset
        New dataset containing computed errors
    """
    result = diff.copy()
    for name, diff_var in diff.variables.items():
        if relative_mode[name].item():  # Access scalar boolean value
            if name not in ref_ds:  # Ignore variables missing in reference dataset
                continue
            # Mask where reference is zero
            ref_nonzero = ref_ds[name] != 0
            result[name] = xr.where(ref_nonzero, diff_var / ref_ds[name], diff_var)
        # For absolute mode, the input difference is already the error
    return result


def variables_statistics(
    dt: DataTree,
    dt_ref: DataTree,
    relative: bool,
    absolute: bool,
    threshold: float,
) -> tuple[dict[str, Any], DataTree]:
    """Compute statistics on all the variables of a `DataTree`
    Note that this function triggers the `dask.array.compute()`

    Parameters
    ----------
    dt
        input datatree
    dt_ref
        reference datatree
    relative
        Compute relative error (default for non-packed variables)
    absolute
        Compute absolute error (default for packed variables)
    threshold
        Maximum allowed threshold defining the PASSED/FAILED result.
        In relative mode, this is a float between 0 and 1 (e.g. 0.01 for 1%).
        In absolute mode, packed variables use an hardcoded threshold of 1.5 * scale_factor.

    Returns
    -------
        A dictionary with keys the name of the variable (including its tree path) and the list a computed statistics
    """
    with suppress_numpy_warnings():
        with xr.set_options(keep_attrs=True):
            # Filter out coordinates and flags variables.
            # Coordinates are not accounted for after reduction operation as min,max...
            # so remove the coordinates from input datatrees.
            dt_filtered = drop_coordinates(filter_datatree(dt.copy(), [], type="flags"))
            dt_ref_filtered = drop_coordinates(filter_datatree(dt_ref.copy(), [], type="flags"))
            # Convert datetime to int if needed
            dt_filtered = encode_time(dt_filtered)
            dt_ref_filtered = encode_time(dt_ref_filtered)
            # Compute comparison modes and thresholds
            relative_dt = compute_relative_mode(dt_filtered, relative, absolute)
            threshold_dt = compute_threshold(dt_filtered, relative_dt, threshold)
            # Compute difference and error
            diff = dt_filtered - dt_ref_filtered  # type: ignore
            err = compute_error(diff, dt_ref_filtered, relative_dt)

        min_dt = err.min(skipna=True)
        max_dt = err.max(skipna=True)
        mean_dt = err.mean(skipna=True)
        std_dt = err.std(skipna=True)
        med_dt = compute_median(err)
        count = count_outliers(err, threshold_dt)
        # Add new metrics mse and psnr
        mse = (diff * diff).mean(skipna=True)  # type: ignore
        sq_max_value = ((diff + dt_ref_filtered).max(skipna=True) - (diff + dt_ref_filtered).min(skipna=True)) ** 2
        # Add valid data coverage differences
        coverage_diff = dt_filtered.count() - dt_ref_filtered.count()

        results = _compute_reduced_datatree(min_dt)
        results = _compute_reduced_datatree(max_dt, results)
        results = _compute_reduced_datatree(mean_dt, results)
        results = _compute_reduced_datatree(std_dt, results)
        results = _compute_reduced_datatree(med_dt, results)
        results = _compute_reduced_datatree(mse, results)
        results = _compute_reduced_datatree(sq_max_value, results)
        results = _compute_reduced_datatree(count, results)
        results = _get_coverage(drop_coordinates(err), results)
        results = _compute_reduced_datatree(coverage_diff, results)
        results = _compute_reduced_datatree(relative_dt, results)
        results = _compute_reduced_datatree(threshold_dt, results)

        return results, err


def bitwise_statistics_over_dataarray(array: xr.DataArray) -> xr.Dataset:
    """Compute bitwise statistics over a dataarray

    Parameters
    ----------
    array
        input dataarray. It is assumed to represent the difference between 2 bitwise flag values for instance
        flag1 ^ flag2

    Returns
    -------
        returns a `xarray.dataset` indexed by the bit range with the following variables
        "bit_position",
        "bit_meaning",
        "total_bits":,
        "equal_count",
        "different_count",
        "equal_percentage",
        "different_percentage"
    """
    flag_meanings = array.attrs["flag_meanings"]
    mask = array.attrs.get("flag_masks", None)
    if mask is None:
        mask = array.attrs.get("flag_values")
    try:
        flag_masks = list(mask)
    except Exception as e:
        raise e
    key: list[str] = []
    if isinstance(flag_meanings, str):
        key = flag_meanings.split(" ")
    else:
        key = flag_meanings

    bit_stats: list[dict[str, Any]] = []

    for bit_mask in flag_masks:
        # get bit position aka log2(bit_mask)
        bit_pos = 0
        m = bit_mask
        while m > 1:
            m >>= 1
            bit_pos += 1
        # for bit_pos in range(num_bits):
        # bit_mask = 1 << bit_pos
        diff = (array & bit_mask) >> bit_pos
        equal_bits = diff == 0

        try:
            idx = flag_masks.index(bit_mask)
            # idx = np.where(flag_masks == bit_mask)
        except ValueError:
            print(
                f"Encounter problem while retrieving the bit position for value {bit_mask}",
            )

        flag_name = key[idx]

        with suppress_numpy_warnings():
            total_bits = equal_bits.size
            equal_count = equal_bits.sum().compute().data
            diff_count = total_bits - equal_count

            bit_stats.append(
                {
                    "bit_position": bit_pos,
                    "bit_meaning": flag_name,
                    "total_bits": total_bits,
                    "equal_count": equal_count,
                    "different_count": diff_count,
                    "equal_percentage": equal_count / total_bits * 100,
                    "different_percentage": diff_count / total_bits * 100,
                },
            )

    return xr.Dataset.from_dataframe(pd.DataFrame(bit_stats))


def bitwise_statistics(dt: DataTree) -> dict[str, xr.Dataset]:
    """Compute bitwise statistics on all the variables of a `DataTree`.
    The variables should represent flags/masks variables as defined by the CF conventions, aka including
    "flags_meanings" and "flags_values" as attributes
    Note that this function triggers the `dask.array.compute()`

    Parameters
    ----------
    dt
        input `DataTree

    Returns
    -------
        dictionary of `xarray.Dataset` with keys being the variable name.
        The `xarray.Dataset` is indexed by the bit range and contains the following variables
        "bit_position",
        "bit_meaning",
        "total_bits":,
        "equal_count",
        "different_count",
        "equal_percentage",
        "different_percentage"
    """
    # TODO test if dt only contains flags variables
    # call to filter_flags for instance

    res: dict[str, xr.Dataset] = {}
    for tree in dt.subtree:
        # if tree.is_leaf:
        if tree.ds:
            for var in tree.data_vars:
                try:
                    res[var] = bitwise_statistics_over_dataarray(tree.data_vars[var])
                except Exception as e:
                    print(f"Warning cannot compute bitwise statistics for variable {var}: {e}")

    return res


def compute_confusion_matrix_for_dataarray(
    reference: xr.DataArray,
    predicted: xr.DataArray,
    normalize: Any | None = None,
    title: str | None = None,
    show: bool = False,
) -> float:
    """Display the confusion matrix for an array of exclusive flags

    Parameters
    ----------
    reference : xr.DataArray
        _description_
    predicted : xr.DataArray
        _description_
    normalize : Any | None, optional
        _description_, by default None
    title : str | None, optional
        _description_, by default None
    """
    if show and not PLOT_AVAILABLE:
        logger.warning("Please install sentineltoolbox extra-dependencies [dev] to display matrices.")
        logger.warning("Display matrix feature disabled")
        show = False
    true_1d = reference.values.ravel()
    pred_1d = predicted.values.ravel()

    unique_class_indices = list(set(np.unique(true_1d)) | set(np.unique(pred_1d)))
    labels = predicted.attrs["flag_meanings"]
    display_labels = [labels[i] for i in unique_class_indices]
    matrix = confusion_matrix(true_1d, pred_1d, normalize=normalize)
    if show:
        disp = ConfusionMatrixDisplay(confusion_matrix=matrix, display_labels=display_labels)
        disp.plot()
        plt.show()
    matrix_abs = confusion_matrix(true_1d, pred_1d)
    if show:
        disp = ConfusionMatrixDisplay(confusion_matrix=matrix_abs, display_labels=display_labels)
        disp.plot()
        plt.show()

    score = np.sum(np.diagonal(matrix_abs) * np.diagonal(matrix) * 100) / np.trace(matrix_abs)

    return score


def product_exists(input_path: str, secret: str | None = None) -> bool:
    """Check if input product exists wheter it is on filesystem or object-storage"""
    kwargs = {}
    if secret:
        kwargs["secret_alias"] = secret
    fs, url = get_fsspec_filesystem(input_path, **kwargs)
    return fs.exists(url)


def parse_cmp_vars(reference: str, new: str, cmp_vars: str) -> list[tuple[str, str]]:
    """Parse command-line option cmp-vars"""
    list_prods: list[tuple[str, str]] = []

    for vars in cmp_vars.split(","):
        var = vars.split(":")
        if len(var) != 2:
            raise ValueError(f"{cmp_vars} is not a valid --cmp-var option syntax")
        list_prods.append(
            (var[0], var[1]),
        )

    return list_prods
