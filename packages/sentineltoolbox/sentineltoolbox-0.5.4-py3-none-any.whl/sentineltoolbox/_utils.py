import re
from copy import copy
from pathlib import Path, PurePosixPath
from typing import Any

from sentineltoolbox.typedefs import (
    T_Attributes,
    T_ContainerWithAttributes,
    is_attributes,
    is_container_with_attributes,
)


def to_posix_str(path: PurePosixPath | Path | str) -> str:
    if isinstance(path, (PurePosixPath, Path)):
        pathstr = path.as_posix()
    else:
        pathstr = PurePosixPath(path).as_posix()
    if ":\\" in pathstr:
        parts = pathstr.split(":\\")
        drive = parts[0]
        relpath = ":\\".join(parts[1:])
        posix_str = drive + ":\\" + relpath.replace("\\", "/")
    else:
        posix_str = pathstr.replace("\\", "/")
    return posix_str


def split_protocol(url: str) -> tuple[set[str], PurePosixPath]:
    """
    Split a URL into its protocol(s) and path component.

    This function takes a URL string and splits it into a set of protocols
    and the corresponding file path in POSIX format. It supports multiple protocols
    (separated by `::`) and assumes the "file" protocol if no protocol is explicitly provided.

    Parameters
    ----------
    url : str
        The input URL or file path to be split into protocol(s) and a path.

    Returns
    -------
    tuple[set[str], PurePosixPath]
        A tuple containing:
        - A set of protocols (e.g., {"file"}, {"s3"}, {"zip", "s3"}).
        - A `PurePosixPath` object representing the file path in POSIX format.

    Example
    -------
    >>> protocols, path = split_protocol("s3::zip://my-bucket/my-folder/myfile.zip")
    >>> path
    PurePosixPath('my-bucket/my-folder/myfile.zip')
    >>> protocols # doctest: +SKIP
    {'s3', 'zip'}

    Notes
    -----
    - If no protocol is specified (i.e., the URL does not contain "://"), it defaults to the "file" protocol.
    - Supports multiple protocols chained together using "::" (e.g., "s3::zip://").
    """
    url_str = str(url)
    # Check if the URL contains a protocol (indicated by "://").
    if "://" in url_str:
        parts = url_str.split("://")
        protocol = parts[0]
        path = parts[1]
        # If no protocol is explicitly specified, default to "file".
        if not protocol:
            protocol = "file"
    else:
        # If there is no "://", assume the entire string is a local path.
        protocol = "file"
        path = url_str
    return set(protocol.split("::")), PurePosixPath(path)


def build_url(protocols: set[str], relurl: PurePosixPath) -> str:
    # build valid_protocol list
    # remove conflicts like zip::file
    # force order like zip::s3
    protocols = copy(protocols)
    valid_protocols = []
    for p in ["zip", "s3"]:
        if p in protocols:
            valid_protocols.append(p)
            protocols.remove(p)
    valid_protocols += list(protocols)
    protocol = "::".join(valid_protocols)
    if str(relurl) == ".":
        return f"{protocol}://"
    else:
        return f"{protocol}://{to_posix_str(relurl)}"


def fix_url(url: str) -> str:
    """
    Fix url to get always same protocols and protocol order.

    >>> fix_url("test.txt")
    'file://test.txt'
    >>> fix_url("/d/test.txt")
    'file:///d/test.txt'
    >>> fix_url("D:\\test.txt")
    'file://D:\\test.txt'
    >>> fix_url("s3://test")
    's3://test'
    >>> fix_url("s3://")
    's3://'
    >>> fix_url("://test")
    'file://test'
    >>> fix_url("://")
    'file://'
    >>> fix_url("zip::s3://")
    'zip::s3://'
    >>> fix_url("s3::zip://")
    'zip::s3://'
    >>> fix_url("s3://test.zip")
    'zip::s3://test.zip'


    :param url:
    :return:
    """
    protocols, relurl = split_protocol(url)
    # add protocols based on extensions
    if Path(str(url)).suffix == ".zip":
        protocols.add("zip")

    return build_url(protocols, relurl)


def _is_s3_url(url: str) -> bool:
    protocols, path = split_protocol(url)
    return "s3" in protocols


def string_to_slice(s: str) -> slice:
    """
    Convert a string in the format "start:stop:step" to a Python slice object.

    :param s: String representing the slice.
    :return: Corresponding Python slice object.
    """
    # Split the string by colon to get start, stop, and step parts
    parts: list[str | Any] = s.split(":")
    parts = [int(part) for part in parts]

    # If the string contains fewer than three parts, append None for missing values
    while len(parts) < 3:
        parts.append(None)

    # Convert the parts to integers or None
    start = int(parts[0]) if parts[0] else None
    stop = int(parts[1]) if parts[1] else None
    step = int(parts[2]) if parts[2] else None

    if start is None and stop is None and step is None:
        raise ValueError(s)

    # Create and return the slice object
    return slice(start, stop, step)


def patch(instance: Any, manager_class: Any, **kwargs: Any) -> None:
    manager = manager_class(instance, **kwargs)

    for attr_name in dir(manager):
        if attr_name.startswith("_"):
            continue
        attr = getattr(manager, attr_name)
        if callable(attr):
            try:  # if method existed before, save it to _method
                setattr(instance, "_" + attr_name, getattr(instance, attr_name))
            except AttributeError:
                pass
            setattr(instance, attr_name, attr)


def _get_attr_dict(data: T_ContainerWithAttributes | T_Attributes) -> T_Attributes:
    if is_container_with_attributes(data):
        return data.attrs  # type: ignore
    elif is_attributes(data):
        return data  # type: ignore
    else:
        raise ValueError(f"type {type(data)} is not supported")


def to_snake_case(string: str) -> str:
    """


    Convert a camelCase or PascalCase string to snake_case.

    Args:
        string (str): The input string in camelCase or PascalCase.

    Returns:
        str: The converted string in snake_case.

    """
    # Step 1: Insert an underscore before any uppercase letter
    # that is preceded by a lowercase letter or number
    pattern = re.compile(r"(?<!^)(?=[A-Z][a-z])")
    string = pattern.sub("_", string)

    # Step 2: Insert an underscore before any sequence of uppercase letters
    # that is followed by a lowercase letter
    pattern = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
    string = pattern.sub("_", string)

    # Step 3: Convert to lowercase
    return string.lower()
