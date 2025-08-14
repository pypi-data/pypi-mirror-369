# mypy: disable-error-code="operator"
from typing import List, Literal, Optional

import dask.array as da
import numpy as np

from sentineltoolbox.typedefs import AnyArray, as_dataarray

MAXIMUM_NUMBER_OF_BITS_IN_NUMPY_INTS = 256  # limit set by the numpy dtypes


def create_flag_array(
    shape: tuple[int, int],
    number_of_bits: int,
    fill_value: int = 0,
    chunking: Optional[tuple[int, int]] = None,
) -> da.Array:
    """Create a standard `flag_array` array that should work with the update and read functions.

    Parameters
    ----------
    shape:
        Shape of the dask array for the `flag_array`
    number_of_bits:
        The bit length for each int in the dask array
    fill_value:
        Integer to fill the numpy array. Integer cannot be >= 2**number_of_bits.
    chunking, optional:
        Default chunking for the flag_array array.

    Returns
    -------
        flag_array array
    """
    if number_of_bits > MAXIMUM_NUMBER_OF_BITS_IN_NUMPY_INTS:
        raise NotImplementedError(
            f"the maximum int size for number_of_bits is {MAXIMUM_NUMBER_OF_BITS_IN_NUMPY_INTS}",
        )

    number_of_bits_best_dtype = np.min_scalar_type(2**number_of_bits - 1)
    if fill_value != 0:
        if fill_value > np.iinfo(number_of_bits_best_dtype).max:
            raise ValueError(
                f"The provided fill_value ({fill_value}) exceeds the maximum allowable "
                + "integer for the specified number_of_bits ({number_of_bits}). "
                + "Please choose a smaller fill_value or increase the number_of_bits to "
                + "accommodate larger values. ",
            )

        flag_array = da.full(shape, fill_value=fill_value, dtype=number_of_bits_best_dtype)
    else:
        flag_array = da.zeros(shape, dtype=number_of_bits_best_dtype)

    if chunking:
        flag_array = flag_array.rechunk(chunking)

    return flag_array


def update_flag(
    flag_array: AnyArray,
    new_flag: AnyArray,
    operation: Literal["or", "and", "xor", "replace"],
    bit_index: Optional[int] = None,
    label_list: Optional[List[str]] = None,
    label_to_update: Optional[str] = None,
) -> AnyArray:
    """given a `flag_array` array, will modify all the flags at `index` according to the values in new_flags.
    The operation performed between the `flag_array` at `index` and `new_flags` is determined by `operation`.
    It will return the `flag_array` updated. `label_list` and `label_to_update` are used when indexing by labels.

    Parameters
    ----------
    flag_array:
        Array of int (ex: dtype=np.int8 for 8 bit ints). The bits of that int will refer to a flag in `flag_array`
    new_flag
        Boolean array of with the values for the new flags. It will be updated in flag_array
    operation
        `["or","and","xor","replace"]`. defines which operation will be performed between `new_flag` and
        `quality_flag[index]`
    index, optional:
        Index of the bit depth you want to update. cannot be used alongside `label_list` and `label_to_update`
    label_list, optional
        List of labels that correspond to each bit in `flag_array` array. Used only when indexing by labels,
        cannot be used alongside `index`.
    label_to_update, optional
        Name of the label to update. it must be in label_list,Used only when indexing by labels,
        cannot be used alongside `index`.

    Returns
    -------
        flag_array array updated
    """
    qf_dtype = flag_array.dtype
    flag_array = as_dataarray(flag_array)

    if new_flag.dtype == bool or np.issubdtype(new_flag.dtype, np.floating):
        new_flag = new_flag.astype(qf_dtype)

    if bit_index is not None and label_list and label_to_update:
        raise ValueError("You cannot use integer and label indexing at the same time")
    elif not (bit_index is not None or label_list or label_to_update):
        raise ValueError("You must input an indexing method (i or label)")
    if bit_index is None and label_list and not label_to_update:
        raise ValueError("in label mode, you must input `label_to_update`")
    if bit_index is None and not label_list and label_to_update:
        raise ValueError("in label mode, you must input `label_list`")

    # for label based indexing
    i = bit_index
    if label_list and label_to_update and not i:
        i = label_list.index(label_to_update)
    new_flag *= 2**i

    if operation == "or":
        flag_array = da.bitwise_or(flag_array, new_flag)
    elif operation == "and":
        flag_array = da.bitwise_and(flag_array, new_flag)
    elif operation == "xor":
        flag_array = da.bitwise_xor(flag_array, new_flag)
    elif operation == "replace":
        reset_mask = da.full_like(flag_array, fill_value=2**i)
        flag_array = da.bitwise_and(flag_array, ~reset_mask)
        flag_array = da.bitwise_or(flag_array, new_flag)
    flag_array = flag_array.astype(qf_dtype)
    return flag_array


def get_flag(
    flag_array: AnyArray,
    bit_index: Optional[int] = None,
    label_list: Optional[List[str]] = None,
    label_to_read: Optional[str] = None,
) -> AnyArray:
    """
    Reads the flag_array array, and will return a boolean mask array of the same shape,
    corresponding to the raised and lowered flag.
    `label_list` and `label_to_update` are used when indexing by labels

    Parameters
    ----------
    flag_array:
        flag array to retrieve from.
    index, optional:
        Index of the bit depth you want to update. cannot be used alongside `label_list` and `label_to_read`
    label_list, optional
        List of labels that correspond to each bit in `flag_array` array. Used only when indexing by labels,
        cannot be used alongside `index`.
    label_to_read, optional
        Name of the label to update. it must be in label_list, used only when indexing by labels,
        cannot be used alongside `index`.

    Returns
    -------
        A boolean mask of a raised or lowered flag.


    """

    flag_array = as_dataarray(flag_array)

    if bit_index is not None and label_list and label_to_read:
        raise ValueError("You cannot use integer and label indexing at the same time")
    elif not (bit_index is not None or label_list or label_to_read):
        raise ValueError("You must input an indexing method (i or label)")
    if bit_index is None and label_list and not label_to_read:
        raise ValueError("in label mode, you must input `label_to_update`")
    if bit_index is None and not label_list and label_to_read:
        raise ValueError("in label mode, you must input `label_list`")

    i = bit_index
    # for label based indexing
    if label_list and label_to_read and not i:
        i = label_list.index(label_to_read)

    comparison_mask = da.full_like(flag_array, fill_value=2**i, dtype=flag_array.dtype)
    mask_int = da.bitwise_and(flag_array, comparison_mask)
    mask = mask_int > 0
    return mask
