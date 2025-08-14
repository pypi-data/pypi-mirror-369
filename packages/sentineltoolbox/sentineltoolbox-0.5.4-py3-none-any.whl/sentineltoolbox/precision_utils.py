# Copyright 2023 ESA
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

"""
Precision utilities for fixing floating-point precision issues in datatrees.

This module provides functions to detect and correct floating-point precision
errors that can occur when converting between single and double precision formats,
particularly in scale_factor and add_offset attributes.
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np
from xarray.core.datatree import DataTree


def print_precision_report(issues: List[Dict[str, Any]]) -> None:
    """
    Print a formatted report of precision issues.

    Parameters
    ----------
    issues : List[Dict[str, Any]]
        List of precision issues from detect_precision_issues
    """
    if not issues:
        print("No precision issues detected.")
        return

    print(f"Found {len(issues)} precision issues:")
    print("-" * 80)

    for i, issue in enumerate(issues, 1):
        print(f"{i}. Variable: {issue['variable']}")
        print(f"   Attribute: {issue['attribute']}")
        print(f"   Expected: {issue['expected']}")
        print(f"   Found: {issue['found']}")
        print(f"   Difference: {issue['difference']:.2e}")
        print()


def detect_precision_issues(
    datatree: DataTree,
    tolerance: float = 1e-10,
    attributes_to_check: List[str] | None = None,
    method: str = "relative_error",
) -> List[Dict[str, Any]]:
    """
    Detect floating-point precision issues using mathematical methods.

    Parameters
    ----------
    datatree : DataTree
        The datatree to check
    tolerance : float, optional
        Tolerance for relative error comparison (default: 1e-10)
    attributes_to_check : List[str], optional
        List of attribute names to check (default: common precision-related attributes)
    method : str, optional
        Detection method to use: "relative_error", "significant_digits", "binary_representation",
        or "combined" (default: "relative_error")

    Returns
    -------
    List[Dict[str, Any]]
        List of detected precision issues
    """
    if attributes_to_check is None:
        attributes_to_check = ["scale_factor", "add_offset", "fill_value", "_FillValue"]

    issues = []

    def check_value(value: Union[int, float], variable_path: str, attribute_name: str) -> None:
        """Check if a value has precision issues using mathematical methods."""
        if not isinstance(value, (int, float)):
            return

        # Handle NaN and infinity
        if not np.isfinite(value):
            return

        if method == "relative_error":
            clean_value = _find_clean_representation(value)
            if clean_value is not None:
                # Avoid division by zero
                if clean_value == 0:
                    # If clean_value is 0, check if the original value is very close to 0
                    if abs(value) < tolerance and value != clean_value:
                        issues.append(
                            {
                                "variable": variable_path,
                                "attribute": attribute_name,
                                "expected": clean_value,
                                "found": value,
                                "difference": abs(value - clean_value),
                                "relative_error": abs(value) if value != 0 else 0.0,
                                "method": "relative_error",
                            },
                        )
                else:
                    relative_error = abs(value - clean_value) / abs(clean_value)
                    if relative_error < tolerance and value != clean_value:
                        issues.append(
                            {
                                "variable": variable_path,
                                "attribute": attribute_name,
                                "expected": clean_value,
                                "found": value,
                                "difference": abs(value - clean_value),
                                "relative_error": relative_error,
                                "method": "relative_error",
                            },
                        )

        elif method == "significant_digits":
            if _has_excessive_precision(value):
                clean_value = _round_to_significant_digits(value)
                issues.append(
                    {
                        "variable": variable_path,
                        "attribute": attribute_name,
                        "expected": clean_value,
                        "found": value,
                        "difference": abs(value - clean_value),
                        "method": "significant_digits",
                    },
                )

        elif method == "binary_representation":
            clean_value = _find_clean_binary_representation(value)
            if clean_value is not None and value != clean_value:
                issues.append(
                    {
                        "variable": variable_path,
                        "attribute": attribute_name,
                        "expected": clean_value,
                        "found": value,
                        "difference": abs(value - clean_value),
                        "method": "binary_representation",
                    },
                )

        elif method == "combined":
            # Try multiple methods
            clean_value = _find_clean_representation(value)
            if clean_value is not None:
                # Avoid division by zero
                if clean_value == 0:
                    # If clean_value is 0, check if the original value is very close to 0
                    if abs(value) < tolerance and value != clean_value:
                        issues.append(
                            {
                                "variable": variable_path,
                                "attribute": attribute_name,
                                "expected": clean_value,
                                "found": value,
                                "difference": abs(value - clean_value),
                                "relative_error": abs(value) if value != 0 else 0.0,
                                "method": "combined_relative_error",
                            },
                        )
                else:
                    relative_error = abs(value - clean_value) / abs(clean_value)
                    if relative_error < tolerance and value != clean_value:
                        issues.append(
                            {
                                "variable": variable_path,
                                "attribute": attribute_name,
                                "expected": clean_value,
                                "found": value,
                                "difference": abs(value - clean_value),
                                "relative_error": relative_error,
                                "method": "combined_relative_error",
                            },
                        )
            elif _has_excessive_precision(value):
                clean_value = _round_to_significant_digits(value)
                issues.append(
                    {
                        "variable": variable_path,
                        "attribute": attribute_name,
                        "expected": clean_value,
                        "found": value,
                        "difference": abs(value - clean_value),
                        "method": "combined_significant_digits",
                    },
                )

    # Iterate through all variables in the datatree
    for child in datatree.subtree:
        for var_name in child.variables:
            var = child[var_name]
            variable_path = f"{child.path}/{var_name}" if hasattr(child, "path") else var_name

            # Check attributes
            if hasattr(var, "attrs") and var.attrs:
                for attr_name in attributes_to_check:
                    if attr_name in var.attrs:
                        check_value(var.attrs[attr_name], variable_path, f"attrs.{attr_name}")

            # Check encoding
            if hasattr(var, "encoding") and var.encoding:
                for attr_name in attributes_to_check:
                    if attr_name in var.encoding:
                        check_value(var.encoding[attr_name], variable_path, f"encoding.{attr_name}")

    return issues


def _find_clean_representation(value: float, max_relative_error: float = 1e-6) -> float | None:
    """
    Find a "clean" representation of a floating-point value.

    This function looks for simple, clean representations that the value
    might have been intended to be, such as:
    - Integers: 0, 1, 2, -32768, etc.
    - Simple fractions: 0.5, 0.25, 0.125, etc.
    - Powers of 10: 0.1, 0.01, 0.001, etc.
    - Common scientific values: 0.002, 1e-6, etc.

    Parameters
    ----------
    value : float
        The value to find a clean representation for
    max_relative_error : float, optional
        Maximum relative error to consider a match (default: 1e-8)

    Returns
    -------
    Optional[float]
        The clean representation if found, None otherwise
    """
    # Handle NaN and infinity
    if not np.isfinite(value):
        return None

    if value == 0:
        return 0.0

    # Check for integers
    if abs(value - round(value)) < max_relative_error * abs(value):
        return float(round(value))

    # Check for simple fractions (1/2, 1/4, 1/8, etc.)
    for denom in [2, 4, 8, 16, 32, 64, 128, 256]:
        fraction = 1.0 / denom
        if abs(value - fraction) < max_relative_error * abs(fraction):
            return fraction

    # Check for powers of 10
    log10_val = np.log10(abs(value))
    if abs(log10_val - round(log10_val)) < 0.01:  # Close to a power of 10
        power = round(log10_val)
        clean_val = 10.0**power
        if abs(value - clean_val) < max_relative_error * abs(clean_val):
            return clean_val if value >= 0 else -clean_val

    # Check for common scientific values
    common_values = [
        0.002,
        0.5,
        290.0,
        1e-6,
        2e-5,
        5e-5,
        1e-3,
        1e-4,
        1e-5,
        0.1,
        0.01,
        0.001,
        0.0001,
        0.00001,
        1.0,
        10.0,
        100.0,
        1000.0,
        -32768,
        -2147483648,
        -9223372036854775808,
    ]

    for common_val in common_values:
        # Avoid division by zero when common_val is 0
        if common_val == 0:
            if abs(value) < max_relative_error:
                return common_val
        else:
            if abs(value - common_val) < max_relative_error * abs(common_val):
                return common_val

    # Check for values that are very close to simple decimal representations
    # This catches cases like 0.0020000000949949026 -> 0.002
    str_val = f"{value:.15g}"
    if "e" in str_val.lower():
        # Handle scientific notation
        base, exp = str_val.lower().split("e")
        base_clean = _find_clean_decimal(base)
        if base_clean is not None:
            clean_val = base_clean * (10 ** int(exp))
            # Avoid division by zero when clean_val is 0
            if clean_val == 0:
                if abs(value) < max_relative_error:
                    return clean_val
            else:
                if abs(value - clean_val) < max_relative_error * abs(clean_val):
                    return clean_val
    else:
        # Handle decimal notation
        clean_val = _find_clean_decimal(str_val)
        if clean_val is not None:
            # Avoid division by zero when clean_val is 0
            if clean_val == 0:
                if abs(value) < max_relative_error:
                    return clean_val
            else:
                if abs(value - clean_val) < max_relative_error * abs(clean_val):
                    return clean_val

    return None


def _find_clean_decimal(decimal_str: str) -> Optional[float]:
    """
    Find a clean decimal representation by removing trailing noise.

    Parameters
    ----------
    decimal_str : str
        String representation of a decimal number

    Returns
    -------
    Optional[float]
        Clean decimal value if found, None otherwise
    """
    if "." not in decimal_str:
        return None

    # Remove trailing zeros after decimal point
    clean_str = decimal_str.rstrip("0")
    if clean_str.endswith("."):
        clean_str = clean_str[:-1]

    # Check if the cleaned string represents a simple fraction
    try:
        clean_val = float(clean_str)
        return clean_val
    except ValueError:
        return None


def _has_excessive_precision(value: float, max_significant_digits: int = 6) -> bool:
    """
    Check if a value has excessive precision (too many significant digits).

    Parameters
    ----------
    value : float
        The value to check
    max_significant_digits : int, optional
        Maximum number of significant digits to consider reasonable (default: 6)

    Returns
    -------
    bool
        True if the value has excessive precision
    """
    # Handle NaN and infinity
    if not np.isfinite(value):
        return False

    if value == 0:
        return False

    # Count significant digits
    str_val = f"{abs(value):.15g}"
    if "e" in str_val.lower():
        # Handle scientific notation
        base, exp = str_val.lower().split("e")
        significant_digits = len(base.replace(".", ""))
    else:
        # Handle decimal notation
        significant_digits = len(str_val.replace(".", ""))

    return significant_digits > max_significant_digits


def _round_to_significant_digits(value: float, significant_digits: int = 6) -> float:
    """
    Round a value to a reasonable number of significant digits.

    Parameters
    ----------
    value : float
        The value to round
    significant_digits : int, optional
        Number of significant digits to round to (default: 6)

    Returns
    -------
    float
        Rounded value
    """
    # Handle NaN and infinity
    if not np.isfinite(value):
        return value  # Return NaN/inf as is

    if value == 0:
        return 0.0

    try:
        # Use numpy's around function with appropriate precision
        return float(
            np.format_float_positional(
                value,
                precision=significant_digits - 1,
                unique=False,
                fractional=False,
                trim="k",
            ),
        )
    except (ValueError, TypeError):
        # Fallback for problematic values
        return value


def _find_clean_binary_representation(value: float) -> Optional[float]:
    """
    Find a clean binary representation by analyzing the binary structure.

    This method looks for values that are very close to "clean" binary
    representations (values that can be exactly represented in floating-point).

    Parameters
    ----------
    value : float
        The value to analyze

    Returns
    -------
    Optional[float]
        Clean binary representation if found, None otherwise
    """
    # Handle NaN and infinity
    if not np.isfinite(value):
        return None

    if value == 0:
        return 0.0

    # Convert to binary and back to see if there's precision loss
    import struct

    binary = struct.pack("d", value)
    reconstructed = struct.unpack("d", binary)[0]

    # If the value is very close to its binary reconstruction, it might be a clean value
    if abs(value - reconstructed) < 1e-15:
        return reconstructed

    # Try common binary-friendly values
    binary_friendly = [
        0.0,
        1.0,
        0.5,
        0.25,
        0.125,
        0.0625,
        0.03125,
        0.015625,
        0.002,
        0.001,
        0.0001,
        0.00001,
        290.0,
        -32768.0,
        -2147483648.0,
    ]

    for friendly_val in binary_friendly:
        if abs(value - friendly_val) < 1e-10:
            return friendly_val

    return None


def fix_floating_point_precision(
    datatree: DataTree,
    tolerance: float = 1e-10,
    attributes_to_fix: List[str] | None = None,
    method: str = "relative_error",
    inplace: bool = False,
) -> DataTree:
    """
    Fix floating-point precision issues using mathematical approaches.

    Parameters
    ----------
    datatree : DataTree
        The datatree to fix precision issues in
    tolerance : float, optional
        Tolerance for detecting precision errors (default: 1e-10)
    attributes_to_fix : List[str], optional
        List of attribute names to fix. If None, defaults to
        ['scale_factor', 'add_offset', '_FillValue']
    method : str, optional
        Method to use for detection and fixing (see detect_precision_issues)
    inplace : bool, optional
        If True, modify the datatree in place. If False, return a copy (default: False)

    Returns
    -------
    DataTree
        The datatree with corrected precision values
    """
    if attributes_to_fix is None:
        attributes_to_fix = ["scale_factor", "add_offset", "_FillValue"]

    def fix_value(value: Union[int, float], tolerance: float) -> Union[int, float]:
        """Fix a single value using mathematical methods."""
        if not isinstance(value, (int, float)):
            return value

        # Handle NaN and infinity
        if not np.isfinite(value):
            return value  # Return NaN/inf as is

        if method == "relative_error":
            clean_value = _find_clean_representation(value)
            if clean_value is not None:
                if clean_value == 0:
                    if abs(value) < tolerance:
                        return clean_value
                else:
                    relative_error = abs(value - clean_value) / abs(clean_value)
                    if relative_error < tolerance:
                        return clean_value

        elif method == "significant_digits":
            if _has_excessive_precision(value):
                return _round_to_significant_digits(value)

        elif method == "binary_representation":
            clean_value = _find_clean_binary_representation(value)
            if clean_value is not None:
                return clean_value

        elif method == "combined":
            # Try multiple methods
            clean_value = _find_clean_representation(value)
            if clean_value is not None and abs(value - clean_value) < tolerance:
                return clean_value

            if _has_excessive_precision(value):
                return _round_to_significant_digits(value)

        return value

    def fix_attrs(attrs: Dict[str, Any], tolerance: float) -> Dict[str, Any]:
        """Fix attributes in a dictionary."""
        if not isinstance(attrs, dict):
            return attrs

        fixed_attrs = {}
        for key, value in attrs.items():
            if key in attributes_to_fix:
                fixed_attrs[key] = fix_value(value, tolerance)
            else:
                fixed_attrs[key] = value
        return fixed_attrs

    # Create a copy if not modifying in place
    if not inplace:
        fixed_dt = datatree.copy()
    else:
        fixed_dt = datatree

    # Iterate through all variables in the datatree
    for child in fixed_dt.subtree:
        for var_name in child.variables:
            var = child[var_name]

            # Fix attributes
            if hasattr(var, "attrs") and var.attrs:
                var.attrs = fix_attrs(var.attrs, tolerance)

            # Fix encoding if it exists
            if hasattr(var, "encoding") and var.encoding:
                for attr_name in attributes_to_fix:
                    if attr_name in var.encoding:
                        var.encoding[attr_name] = fix_value(var.encoding[attr_name], tolerance)

    return fixed_dt


def fix_and_validate(
    datatree: DataTree,
    tolerance: float = 1e-10,
    method: str = "combined",
    inplace: bool = False,
    verbose: bool = True,
) -> DataTree:
    """
    Convenience function to detect, fix, and validate precision issues using mathematical methods.

    Parameters
    ----------
    datatree : DataTree
        The datatree to process
    tolerance : float, optional
        Tolerance for detecting precision errors (default: 1e-10)
    method : str, optional
        Method to use for detection and fixing (default: "combined")
    inplace : bool, optional
        If True, modify the datatree in place (default: False)
    verbose : bool, optional
        If True, print detailed information about the process (default: True)

    Returns
    -------
    DataTree
        The datatree with corrected precision values
    """
    if verbose:
        print(f"Detecting precision issues using {method} method...")

    issues = detect_precision_issues(datatree, tolerance, method=method)

    if verbose:
        print_precision_report(issues)

    if not issues:
        if verbose:
            print("No issues to fix.")
        return datatree

    if verbose:
        print("Fixing precision issues...")

    fixed_dt = fix_floating_point_precision(datatree, tolerance, method=method, inplace=inplace)

    if verbose:
        remaining_issues = detect_precision_issues(fixed_dt, tolerance, method=method)
        print("Validation results:")
        print(f"  Original issues: {len(issues)}")
        print(f"  Issues fixed: {len(issues) - len(remaining_issues)}")
        print(f"  Remaining issues: {len(remaining_issues)}")
        print(f"  Fix successful: {len(remaining_issues) == 0}")

    return fixed_dt
