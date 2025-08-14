import logging
from typing import Any, Protocol

import dask.array as da
import numpy as np
import numpy.typing as npt
from xarray import DataTree

from sentineltoolbox.exceptions import (
    DatatreeSchemaAttributeError,
    DatatreeSchemaAttrsError,
    DatatreeSchemaDataError,
    DatatreeSchemaDimError,
    DatatreeSchemaDtypeError,
    DatatreeSchemaKeyError,
)

DICT_DATA: dict[str, Any] = {"numpy.ndarray": np.ndarray, "dask.array.core.Array": da.Array}


class ValidatorFunction(Protocol):
    def __call__(self, expected: Any, actual: Any, path_with_new_node: Any) -> Any: ...


def validate_array_type(
    expected: str,
    actual: npt.NDArray[Any] | da.Array,
    path_with_new_node: str,
    dict_data: dict[str, Any] = DICT_DATA,
    **kwargs: Any,
) -> None:
    """
    Validate the data type of a value against a given type.

    The validation of data attribute is only a validation for type, not value.

    Parameters
    ----------
    expected :
        The expected data type, as a string.
    actual :
        The value to validate.
    key :
        The key of the value in the schema, used for error messages.
    dict_data :
        A dictionary mapping data type strings to the corresponding types.
        Default is DICT_DATA.
    kwargs:
        logger: Optional
            A logger to print the verifications.

    Raises
    ------
    DatatreeSchemaDataError
        If the data type of the obtained value does not match the type of the expected value.
    """
    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))
    if not isinstance(actual, dict_data[expected]):
        raise DatatreeSchemaDataError(f"Expected {expected}, obtained {type(actual)} for {path_with_new_node}.")
    logger.info(f"Check array type OK: node {path_with_new_node}. Obtained {dict_data[expected]} successfully.")


def _is_hashable(value: Any) -> bool:
    """Check if a variable is hashable (supports equality)."""
    try:
        hash(value)
        return True
    except TypeError:
        return False


def validate_attrs(
    expected: dict[str, Any],
    actual: Any,
    path_with_new_node: str,
    **kwargs: Any,
) -> None:
    """
    Validate the data type of a value against a given type.

    Parameters
    ----------
    expected :
        The expected data type, as a string.
    actual :
        The value to validate.
    path_with_new_node :
        The key of the value in the schema, used for error messages.
    dict_data :
        A dictionary mapping data type strings to the corresponding types.
        Default is DICT_DATA.
    kwargs:
        logger: Optional
            A logger to print the verifications.

    Raises
    ------
    DatatreeSchemaAttrsError
        If the data in the attrs section is not correct.
    """
    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))
    for expected_key, expected_value in expected.items():

        if isinstance(expected_value, dict):
            if isinstance(actual, dict):
                try:
                    new_actual = actual[expected_key]
                except KeyError:
                    raise DatatreeSchemaAttrsError(f"Expected {expected_key} in {path_with_new_node} but didn't find.")
                validate_attrs(expected_value, new_actual, path_with_new_node + "/" + expected_key, **kwargs)
            else:
                raise DatatreeSchemaAttrsError(
                    f"Expected {path_with_new_node} to be of type dict, obtained {type(actual)}.",
                )

        elif expected_value == "":
            # Empty string means no check are performed: key can be present or absent.
            # This exception is necessary since "" is hashable, but should not be
            # included in comparisons
            continue

        elif expected_value == "required":
            # When "required" is specified in the scheme, we only check key exists.
            try:
                actual[expected_key]
                logger.debug(f"Check {path_with_new_node} OK: {expected_key} found as expected.")
                continue
            except KeyError:
                raise DatatreeSchemaAttrsError(
                    f"Expected attrs {expected_key} in {path_with_new_node}, but dit not find it.",
                )

        elif _is_hashable(expected_value):
            # We can check for equality.
            try:
                actual_value = actual[expected_key]
            except KeyError:
                raise DatatreeSchemaAttrsError(
                    f"Expected attrs {expected_key} of value {expected_value} "
                    f"in {path_with_new_node}, but dit not find it.",
                )

            if expected_value == actual_value:
                logger.debug(
                    f"Check {path_with_new_node} OK: {expected_key} found equal to {expected_value} as expected.",
                )
                continue
            else:
                raise DatatreeSchemaAttrsError(
                    f"Expected attrs {expected_value}, obtained {actual[expected_key]} "
                    f"for {expected_key} in {path_with_new_node}.",
                )
        else:
            logger.info(
                f"{expected_key} specified in the scheme at node {path_with_new_node} but not "
                "required or hashable: no check on values performed.",
            )
            continue


def validate_dimension(expected: tuple[str], actual: tuple[str] | list[str], path_with_new_node: str) -> None:
    """
    Validate the dimensions of a value against a given set of dimensions.

    Parameters
    ----------
    expected :
        The expected dimensions, as a tuple of strings.
    actual :
        The dimensions of the value to validate, as a tuple of strings.
    path_with_new_node :
        The key of the value in the schema, used for error messages.

    Raises
    ------
    DatatreeSchemaDimError
        If the dimensions of the obtained value do not match the expected dimensions.
    """

    if isinstance(expected, dict):
        expected = expected.keys()
    if isinstance(actual, dict):
        actual = actual.keys()

    if isinstance(expected, str):
        expected = (expected,)
    if isinstance(actual, str):
        actual = (actual,)

    if tuple(expected) != tuple(actual):
        raise DatatreeSchemaDimError(f"Expected {expected}, obtained {actual} for {path_with_new_node}.")


def validate_dtype(
    expected: str,
    actual: npt.DTypeLike,
    path_with_new_node: str,
    **kwargs: Any,
) -> None:
    """
    Validate the data type of a value against a given data type.

    Parameters
    ----------
    expected :
        The expected data type, as a string.
    actual :
        The data type of the value to validate.
    path_with_new_node :
        The key of the value in the schema, used for error messages.
    kwargs:
        logger: Optional
            A logger to print the verifications.

    Raises
    ------
    DatatreeSchemaDtypeError
        If the data type of the obtained value does not match the expected data type.
    """
    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))
    if np.dtype(expected) != actual:
        raise DatatreeSchemaDtypeError(f"Expected {np.dtype(expected)}, obtained {actual} for {path_with_new_node}.")
    logger.info(f"Check dtype OK: node {path_with_new_node}. Obtained {actual} successfully.")


def _validate_final_node(
    key: str,
    previous_key: str,
    expected: Any,
    actual: Any,
    **kwargs: Any,
) -> None:
    """Validate a final node in the schema against the corresponding value in the DataTree."""
    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))
    if expected == "":
        return

    if expected == "required":
        return

    dict_validation: dict[str, ValidatorFunction] = {
        "dims": validate_dimension,
    }
    func_validation = dict_validation.get(key)
    if func_validation:
        func_validation(expected, actual, previous_key + key)
        logger.info(f"Check {key} OK: {previous_key + '/' + key}. Obtained {expected} successfully.")
    else:
        logger.info(f"No check for {key} value in {previous_key + '/' + key}")


def _access_node_attribute(
    path_to_node: str,
    new_key: str,
    node: str,
    datatree: DataTree,
) -> Any:
    """Check if an attribute of a DataTree node exists."""
    try:
        return getattr(datatree, node)
    except AttributeError:
        raise DatatreeSchemaAttributeError(f"{node} in {new_key} not found in {path_to_node}.")


def _access_node_key(key: str, new_key: str, datatree: DataTree) -> Any:
    """Check if a key in the DataTree exists."""
    try:
        return datatree[new_key]
    except KeyError:
        raise DatatreeSchemaKeyError(f"{key} in {new_key} not found")


def _get_node(node: str, path_to_node: str, path_with_new_node: str, datatree: DataTree) -> Any:
    """Access the value of the datatree at the node."""

    # Attributes defines in xarray from_dict method.

    xr_attrs = {"dims", "attrs", "data", "coords", "name", "data_vars"}

    if node in xr_attrs:
        return _access_node_attribute(path_to_node, path_with_new_node, node, datatree)
    else:
        return _access_node_key(path_with_new_node, node, datatree)


def validate_datatree(
    schema: dict[str, Any],
    datatree: DataTree,
    path_to_node: str = "",
    **kwargs: Any,
) -> None:
    """
    Validate a DataTree object against a given schema.

    Parameters
    ----------
    schema :
        A nested dictionary representing the schema to validate against.
        The keys of the dictionary represent the keys in the DataTree,
        and the values represent the expected values or types for those keys.
        If a value is a dictionary, it is assumed to be a nested schema.
    datatree :
        The DataTree object to validate.
    path_to_node :
        The key of the parent node in the DataTree, used for recursive calls.
        Default is an empty string.
    kwargs:
        logger: Optional
            A logger to print the verifications.

    Raises
    ------
    DatatreeSchemaAttrsError:
        Raised when the .attrs section is not correct in the DataTree instance.

    DatatreeSchemaKeyError:
        Raised when a key (node) is missing in the DataTree instance.

    DatatreeSchemaAttributeError:
        Raised when an attribute (node) is missing in the DataTree instance.

    DatatreeSchemaDimError:
        Raised when a dimension of a variable in the DataTree instance is not as expected.

    DatatreeSchemaDataError:
        Raised when the DataTree instance does not hold the correct data type.

    DatatreeSchemaDtypeError:
        Raised when the numpy dtype of a variable in the DataTree instance is not correct.

    Notes
    -----
    The validation is performed recursively, so nested schemas are supported.
    """
    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))
    special_nodes = ["", "/", "data_vars"]
    for node, expected in schema.items():

        if (path_to_node in special_nodes) and (node not in special_nodes):
            path_with_new_node = node
        elif node in special_nodes:
            path_with_new_node = path_to_node
        else:
            path_with_new_node = path_to_node + "/" + node

        if node not in special_nodes:
            actual = _get_node(node, path_to_node, path_with_new_node, datatree)
        else:
            actual = datatree

        logger.info(f"Check exists OK: {path_with_new_node}")

        if node == "attrs":
            # attrs is a special case of dictionary
            if "dtype" in expected.keys():
                validate_dtype(expected["dtype"], datatree.dtype, path_to_node, **kwargs)
                expected.pop("dtype")
            if "_array_type" in expected.keys():
                validate_array_type(expected["_array_type"], datatree.data, path_to_node, **kwargs)
                expected.pop("_array_type")
            validate_attrs(expected, actual, path_with_new_node, **kwargs)

        elif isinstance(expected, dict):
            validate_datatree(expected, actual, path_with_new_node, **kwargs)

        else:
            _validate_final_node(node, path_to_node, expected, actual, **kwargs)
