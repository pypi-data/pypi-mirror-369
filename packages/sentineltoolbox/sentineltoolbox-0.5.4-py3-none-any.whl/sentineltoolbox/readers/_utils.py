import copy
import json
import logging
from typing import Any, BinaryIO, Callable, Hashable, Literal, TextIO

import numpy as np
import tomli
import yaml

from sentineltoolbox.typedefs import is_eopf_adf

logger = logging.getLogger("sentineltoolbox")


L_SUPPORTED_FORMATS = Literal[".json", ".toml", ".txt", None]

stb_open_parameters = (
    "secret_alias",
    "logger",
    "credentials",
    "configuration",
    "filesystem",
    "cache",
    "uncompress",
    "local_copy_dir",
    "autofix_args",
    "load",
)


def _load_data(path: Any, load_fp_func: Callable[[TextIO], Any]) -> Any:
    if hasattr(path, "open"):
        with path.open("r", encoding="utf-8") as data_fp:
            return load_fp_func(data_fp)
    else:
        with open(str(path), "r", encoding="utf-8") as data_fp:
            return load_fp_func(data_fp)


def _load_data_bytes(path: Any, load_fp_func: Callable[[BinaryIO], Any]) -> Any:
    if hasattr(path, "open"):
        with path.open("rb") as data_fp:
            return load_fp_func(data_fp)
    else:
        with open(str(path), "rb") as data_fp:
            return load_fp_func(data_fp)


def load_toml_fp(fp: BinaryIO) -> dict[str, Any]:
    """
    Load data from a TOML file.

    Provides functionality to read and parse the content of a TOML file
    from a BinaryIO stream and return it as a Python dictionary.

    :param fp: File-like object opened in binary mode, containing the TOML content.
    :return: Parsed TOML data as a dictionary.
    """
    with fp:
        return tomli.load(fp)


def load_yaml_fp(fp: TextIO) -> dict[str, Any]:
    """
    Loads a YAML file from a given file pointer and returns its parsed content.

    :param fp: A file pointer to the YAML file.
    :return: The parsed content of the YAML file as a dictionary.
    """
    with fp:
        dic = yaml.safe_load(fp)
        if dic is None:
            dic = {}
        return dic


def load_json_fp(fp: TextIO) -> dict[str, Any]:
    """
    Loads a JSON file from a given file pointer and returns its parsed content.

    :param fp: A file pointer to the JSON file.
    :return: The parsed content of the JSON file as a dictionary.
    """
    with fp:
        return json.load(fp)


def load_toml(path: Any) -> dict[str, Any]:
    """
    Loads a TOML file from the given file path and returns its content as a dictionary.

    :param path: Path to the TOML file to be loaded.
    :return: Parsed TOML data as a dictionary.
    """
    return _load_data_bytes(path, load_toml_fp)


def load_yaml(path: Any) -> dict[str, Any]:
    """
    Load a YAML file from the given path and parse its content into a dictionary.

    This function reads and parses a YAML file provided through the specified
    file path, converting it into a Python dictionary.

    :param path: The path to the YAML file.
    :return: A dictionary containing parsed YAML data.
    """
    return _load_data(path, load_yaml_fp)


def load_json(path: Any) -> dict[str, Any]:
    """
    Loads and parses a JSON file from the specified path. This function use builtin module json.

    :param path: Path to the JSON file to load.
    :return: Parsed JSON content as a dictionary.
    """
    return _load_data(path, load_json_fp)


def is_eopf_adf_loaded(path_or_pattern: Any) -> bool:
    """
    Determines if an EOPF ADF is loaded.

    Checks whether the specified :obj:`~sentineltoolbox.module.EOPF` ADF file is
    loaded and contains a valid data pointer.

    :param path_or_pattern: Path or pattern referencing the :obj:`~sentineltoolbox.module.EOPF` ADF to check.
    :return: True if the specified ADF is loaded and has a data pointer; otherwise, False.
    """
    return is_eopf_adf(path_or_pattern) and path_or_pattern.data_ptr is not None


def _cleaned_kwargs(kwargs: Any) -> dict[str, Any]:
    cleaned = {}
    for kwarg in kwargs:
        if kwarg not in stb_open_parameters:
            cleaned[kwarg] = kwargs[kwarg]
    return cleaned


def fix_kwargs_for_lazy_loading(kwargs: Any) -> None:
    """
    Fixes the `kwargs` dictionary to ensure compatibility with lazy loading operations.
    This is specifically used in scenarios requiring data chunking for efficient
    processing during lazy loading. If the `chunks` key is not provided, it initializes
    it with an empty dictionary. Additionally, it enforces that a `None` value for
    `chunks` is not acceptable, raising a `ValueError` in such cases.

    :param kwargs: Dictionary of keyword arguments to be modified.
    :raises ValueError: Raised if the `chunks` parameter is explicitly set to
        `None`, since lazy loading cannot function without chunking.
    """
    if "chunks" not in kwargs:
        kwargs["chunks"] = {}
    else:
        if kwargs["chunks"] is None:
            raise ValueError(
                "open_datatree(chunks=None) is not allowed. Use load_datatree instead to avoid lazy loading data",
            )


def decode_storage_attributes(variable: Any, encoding: dict[str, Any] | None = None, path: str = "") -> dict[Any, Any]:
    """
    Decodes storage-related attributes of a variable, applying transformations and validations.

    This function extracts and adjusts various metadata attributes like `valid_min`, `valid_max`, `scale_factor`,
    and `add_offset` from the input variable or its encoding. It ensures compliance with ADF standards by
    computing decoded attributes and preparing them for further processing.

    :param variable: Input variable containing metadata attributes.
    :param encoding: Optional dictionary with specific encoding details.
    :param path: Path string used for debugging and error messages.
    :return: Dictionary of decoded and computed attributes.
    """
    if encoding is None:
        try:
            encoding = variable.encoding
        except AttributeError:
            encoding = {}
    io = {}
    attrs = {}
    fill_value = encoding.get("_FillValue", encoding.get("fill_value", -1))
    storage_type = encoding.get("dtype", encoding.get("storage_type", np.int32))
    defaults = dict(scale_factor=1.0, add_offset=0.0)
    zattrs = copy.copy(variable.attrs)

    for field in {
        "valid_min",
        "valid_max",
        "scale_factor",
        "add_offset",
    }:
        if field in zattrs:
            io[field] = zattrs[field]
        elif field in encoding:
            io[field] = encoding[field]
        elif field in defaults:
            io[field] = defaults[field]

    if fill_value is not None:
        io["fill_value"] = fill_value
    io["dtype"] = storage_type
    # Compute decode information
    scale_factor = io.get("scale_factor", 1.0)
    add_offset = io.get("add_offset", 0.0)
    mini = io.get("valid_min")
    maxi = io.get("valid_max")
    try:
        valid_max = (add_offset + maxi * scale_factor) if maxi is not None else None
    except TypeError:
        raise TypeError(
            f"{path}: TypeError during operation {add_offset=} + {maxi=} * {scale_factor=}",
        )
    try:
        valid_min = (add_offset + mini * scale_factor) if mini is not None else None
    except TypeError:
        raise TypeError(
            f"{path}: TypeError during operation {add_offset=} + {mini=} * {scale_factor=}",
        )
    decoded: dict[Hashable, Any] = {}
    decoded["valid_min"] = valid_min
    decoded["valid_max"] = valid_max

    # decoded["fill_value"] = np.iinfo(np.int32).min
    for field in {"valid_min", "valid_max"}:
        if decoded[field] is not None:
            attrs[field] = decoded[field]
    if io:
        attrs["_io_config"] = io

    # attrs["dtype"] = variable.dtype
    return attrs
