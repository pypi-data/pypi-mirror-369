"""
This module provides type definition, interface and documentation about common arguments

Generic input arguments:

match_criteria: :obj:`sentineltoolbox.typedefs.PathMatchingCriteria`
    - ``"last_creation_date"`` the product creation date (last part of filename)
      is used to define the most recent data
    - ``"last_modified_time"`` the file/directory modified time (in sense of file system mtime)
      is used to define the most recent data

path_or_pattern: :obj:`sentineltoolbox.typedefs.PathOrPattern`
    example of path:
        - ``"s3://s2-input/Auxiliary/MSI/S2A_ADF_REOB2_xxxxxxx.json"``
        - ``"s3://s3-input/Auxiliary/OL1/S3A_ADF_OLINS_xxxxxxx.zarr"``
        - ``"/home/username/data/S3A_ADF_OLINS_xxxxxxx.zarr"``
        - ``"/d/data/S3A_ADF_OLINS_xxxxxxx.zarr"``
        - ``"D:\\data\\S3A_ADF_OLINS_xxxxxxx.zarr"`` <-- WARNING, don't forget to escape backslash
    example of patterns:
        - ``"s3://s2-input/Auxiliary/MSI/S2A_ADF_REOB2_*.json"``

    path_or_pattern also accept :obj:`eopf.computing.abstract.ADF`


All functions that accept path_or_pattern also accept this **kwargs**:
  - **secret_alias** a string defining secret_alias to use. secret aliases are defined in configuration files.
    If not set, tries to look in predefined secret_alias <-> paths mappings. See Software Configuration
  - **configuration** (FOR EXPERT ONLY): an instance of :obj:`sentineltoolbox.configuration.Configuration`
    Use default configuration if not set.
  - **credentials** (FOR EXPERT ONLY): an instance of :obj:`sentineltoolbox.typedefs.Credentials`
    If not set and required, extract credentials from environment and configuration


This module also provide convenience functions to convert Union of types to canonical type.
For example, for input paths:
  - user input can be Path, list of Path, str, list of str and Path. This is defined by type `T_Paths`
  - in code we want to manipulate only list[Path] (our canonical type) and do not write this boring code each time ...

=> this module provide a convenience function for that (:obj:`~sentineltoolbox.typedefs.fix_paths`)
return type of this function also propose the canonical type to use in your code

"""

__all__ = [
    "Adf",
    "AnyArray",
    "AnyVariable",
    "Converter",
    "Credentials",
    "DATE_FORMAT",
    "DEFAULT_COMPRESSOR",
    "DataPath",
    "DataTreeNode",
    "DataTreeVisitor",
    "EOGroup",
    "EOProduct",
    "FileNameGenerator",
    "GenericEnum",
    "KEYID_GROUP_ATTRIBUTES",
    "L_DataFileNamePattern",
    "MetadataType_L",
    "PathMatchingCriteria",
    "PathOrPattern",
    "T_Attributes",
    "T_ContainerWithAttributes",
    "T_DataPath",
    "T_DataPaths",
    "T_DateTime",
    "T_Json",
    "T_JsonValue",
    "T_Paths",
    "T_TimeDelta",
    "T_UniversalPath",
    "as_dataarray",
    "category_paths",
    "fix_datetime",
    "fix_enum",
    "fix_paths",
    "fix_timedelta",
    "is_any_path",
    "is_attributes",
    "is_container_with_attributes",
    "is_eocontainer",
    "is_eopf_adf",
    "is_eoproduct",
    "is_json",
    "is_universal_path",
]

import os
from abc import abstractmethod
from collections.abc import MutableMapping as AbcMutableMapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import (
    Any,
    Callable,
    Generator,
    Hashable,
    Iterable,
    Literal,
    MutableMapping,
    Protocol,
    Self,
    Type,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

import dask.array as da
import numpy as np
import xarray
import xarray as xr
from numcodecs import Blosc
from xarray import DataArray, Dataset, DataTree

try:
    from eopf import EOGroup, EOProduct
    from eopf.product.eo_object import EOObject
except (ImportError, TypeError):
    EOProduct: TypeAlias = Any  # type: ignore
    EOGroup: TypeAlias = Any  # type: ignore
    EOObject: TypeAlias = Any  # type: ignore

GenericEnum = TypeVar("GenericEnum", bound=Enum)

# -----------------------------------------------------------------------------
# SIMPLE ALIASES
# -----------------------------------------------------------------------------

PathMatchingCriteria: TypeAlias = Literal["last_creation_date", "last_modified_time"]  # can be extended
PathOrPattern: TypeAlias = Any  # Need to support at least str, Path, cpm Adf, cpm AnyPath. Data can be zipped or not!
AnyArray: TypeAlias = xr.DataArray | da.Array | np.ndarray[Any, Any]
AnyVariable: TypeAlias = xr.Variable | xr.DataArray
DataTreeNode: TypeAlias = xr.DataArray | DataTree
XarrayData: TypeAlias = xr.DataArray | DataTree | xr.Dataset

T_DateTime: TypeAlias = datetime | str | int
T_TimeDelta: TypeAlias = timedelta | int

L_DataFileNamePattern = Literal[
    # S3A_OL_0_EFR____20221101T162118_20221101T162318_20221101T180111_0119_091_311______PS1_O_NR_002.SEN3
    "product/s3-legacy",
    "product/s3-legacy-composite",
    "product/s2-legacy",  # S2A_MSIL1C_20231001T094031_N0509_R036_T33RUJ_20231002T065101
    "product/s1-legacy",  # S1A_IW_RAW__0SDH_20240410T075338_20240410T075451_053368_0678E5_F66E.SAFE
    "product/eopf-legacy",  # S3OLCEFR_20230506T015316_0180_B117_T931.zarr
    "product/eopf",  # S03OLCEFR_20230506T015316_0180_B117_T931.zarr
    "product/permissive",  # S03OLCEFR*
    # S3__AX___CLM_AX_20000101T000000_20991231T235959_20151214T120000___________________MPC_O_AL_001.SEN3
    "adf/s3-legacy",
    "adf/s2-legacy",  # S2__OPER_AUX_CAMSAN_ADG__20220330T000000_V20220330T000000_20220331T120000
    "adf/eopf-legacy",  # S3__ADF_SLSBD_20160216T000000_20991231T235959_20231102T155016.zarr
    "adf/eopf",  # S03__ADF_SLSBD_20160216T000000_20991231T235959_20231102T155016.zarr
    "adf/permissive",  # *ADF_SLSBD*,
    "unknown/unknown",
]

"""T_Paths represents user input path or multiple paths"""
T_Paths: TypeAlias = Path | str | Iterable[Path] | Iterable[str] | Iterable[Path | str]


T_ContainerWithAttributes: TypeAlias = DataTree | Dataset | DataArray
T_Attributes: TypeAlias = MutableMapping[Hashable, Any] | MutableMapping[str, Any] | dict[str, Any]
T_JsonValue: TypeAlias = str | int | float | bool | None
T_Json: TypeAlias = dict[str, Any] | list[Any]
L_ToDictDataOptions: TypeAlias = Literal["list", "array", True, False]


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

KEYID_GROUP_ATTRIBUTES = "group_attrs"

# -----------------------------------------------------------------------------
# INTERFACES / ABSTRACT CLASSES
# -----------------------------------------------------------------------------


@dataclass
class Adf:
    name: str
    path: str
    store_params: dict[str, Any]
    data_ptr: Any


@runtime_checkable
class Credentials(Protocol):
    """
    Class storing credential information
    """

    """List of targets available for :meth:`to_kwargs`. Each derived class must define this list."""
    available_targets: list[Any] = []

    def to_kwargs(self, *, url: str | None = None, target: Any = None, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def from_env(cls) -> "Credentials":
        """
        Tries to generate credential instance from environment variables
        """
        raise NotImplementedError

    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> "Credentials":
        """
        Tries to generate credential instance from given kwargs
        """
        raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.to_kwargs() == other.to_kwargs()
        else:
            return False


class FileNameGenerator(Protocol):
    @staticmethod
    def from_string(filename: str, **kwargs: Any) -> "FileNameGenerator":
        """
        Generate a FileNameGenerator from filename string.
        If filename is a legacy filename, you must specify `semantic` to specify the new format semantic.
        """
        raise NotImplementedError

    def is_valid(self) -> bool:
        """
        return True if all required data are set, else retrun False
        """
        raise NotImplementedError

    def to_string(self, **kwargs: Any) -> str:
        """Generate a filename from data and arguments passed by user"""
        raise NotImplementedError


@runtime_checkable
@dataclass(order=True)
class DataPath(Protocol):
    """
    Interface representing Path object.
    This interface is defined to be a subset of pathlib.Path.
    So you can consider pathlib.Path will be always compatible with this interface.

    Compared to pathlib.Path, DataPath is the minimal subset required by sentineltoolbox to work.
    It may evolve depending on DataWalker requirements but will remain compatible with pathlib.Path.
    """

    path: str

    def __init__(self, path: str | Path | PurePosixPath) -> None:
        super().__init__()
        if isinstance(path, (PurePosixPath, Path)):
            pathstr = path.as_posix()
        else:
            pathstr = str(path)

        self.path = pathstr

    def __str__(self) -> str:
        """return absolute and canonical str representation of itself."""
        return str(self.path)

    @property
    def protocols(self) -> tuple[str]:
        return self._get_protocols()

    def _get_protocols(self) -> tuple[str]:
        return ("file",)

    @property
    def url(self) -> str:
        return str(self)

    @abstractmethod
    def is_file(self) -> bool:
        """
        Whether this path is a regular file (also True for symlinks pointing
        to regular files).
        """
        raise NotImplementedError

    @abstractmethod
    def is_dir(self) -> bool:
        """
        Whether this path is a directory.
        """
        raise NotImplementedError

    def exists(self) -> bool:
        """
        Whether this path is a directory.
        """
        return self.is_dir() or self.is_file()

    @property
    def name(self) -> str:
        """The final path component, if any."""
        return Path(self.path).name

    @property
    def stem(self) -> str:
        """The final path component, minus its last suffix."""
        return Path(self.path).stem

    @property
    def parent(self) -> Self:
        """The logical parent of the path."""
        raise NotImplementedError

    def stat(self, *, follow_symlinks: bool = True) -> os.stat_result:
        """
        Returns information about this path (similarly to boto3's ObjectSummary).
        For compatibility with pathlib, the returned object some similar attributes like os.stat_result.
        The result is looked up at each call to this method
        """
        raise NotImplementedError

    def open(
        self,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: Any = None,
    ) -> Any:
        raise NotImplementedError

    @property
    def suffix(self) -> str:
        """
        The final component's last suffix, if any.

        This includes the leading period. For example: '.txt'
        """
        return Path(self.path).suffix

    @property
    def suffixes(self) -> list[Any] | list[str]:
        """
        A list of the final component's suffixes, if any.

        These include the leading periods. For example: ['.tar', '.gz']
        """
        return Path(self.path).suffixes

    @abstractmethod
    def glob(self, pattern: str) -> Generator["DataPath", None, None]:
        raise NotImplementedError

    @abstractmethod
    def rglob(self, pattern: str) -> Generator["DataPath", None, None]:
        raise NotImplementedError


T_DataPath: TypeAlias = Path | DataPath
T_UniversalPath: TypeAlias = DataPath


def is_universal_path(obj: Any) -> bool:
    return isinstance(obj, DataPath)


def is_json(path: str) -> bool:
    suffixes: str = "".join(Path(path).suffixes)
    # TODO: path.is_file() and
    return suffixes in {".json", ".json.zip"}


def is_container_with_attributes(obj: Any) -> bool:
    return isinstance(obj, (DataTree, Dataset, DataArray)) or is_eoproduct(obj)


def is_attributes(obj: Any) -> bool:
    return isinstance(obj, AbcMutableMapping)


# -----------------------------------------------------------------------------
# Convenience functions to convert any type to canonical types
# -----------------------------------------------------------------------------


def fix_paths(paths: T_Paths) -> list[Path]:
    """Convenience function to convert user paths to canonical list[Path]"""
    if isinstance(paths, (str, Path)):
        path_list = [Path(paths)]
    else:
        path_list = [Path(path) for path in paths]
    return path_list


def fix_datetime(date: T_DateTime) -> datetime:
    """Convenience function to convert date to canonical :class:`datetime.datetime`

    Conversion depends on input type:
      - datetime: no change
      - int: consider it's a timestamp
      - str: consider it's a date str following ISO format YYYYMMDDTHHMMSS
    """
    if isinstance(date, datetime):
        return date
    elif isinstance(date, int):
        return datetime.fromtimestamp(date).replace(tzinfo=timezone.utc)
    else:
        dt = datetime.fromisoformat(date)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt


def fix_timedelta(delta: T_TimeDelta) -> timedelta:
    """Convenience function to convert time delta to canonical :class:`datetime.timedelta`

    Conversion depends on input type:
      - timedelta: no change
      - int: consider it a delta in seconds
    """
    if isinstance(delta, timedelta):
        return delta
    else:
        return timedelta(seconds=delta)


def fix_enum(data: Any, enum_class: Type[GenericEnum], default: GenericEnum) -> GenericEnum:
    """
    Converts input data to a member of the specified enumeration.

    Parameters:
        data (Any): The value to convert, which can be:
            - An instance of the enumeration
            - The value of a member (its name, value, or index)
        enum_class (Type[Enum]): The enumeration class to use for conversion.
        default (Enum): The default value to return if no match is found.

    Returns:
        Enum: The matching enumeration member, or the default value if no match is found.
    """
    for i, member in enumerate(enum_class):  # Iterate through all members of the enum
        if data in (member, member.value, member.name, i):  # Match by value, name, or index
            return member
    return default  # Return the default if no match is found


def as_dataarray(input: AnyArray) -> da.Array | np.ndarray[Any, Any]:
    """Conveniance function that converts xarray datatypes into dask arrays. Will return the original
    array if it is a numpy array or already a dask array.

    Parameters
    ----------
    input
        The array to be converted
    Returns
    -------
        Either a dask array or the original array
    """
    if isinstance(input, xr.DataArray):
        return input.data
    else:
        return input


MetadataType_L: TypeAlias = Literal["stac_properties", "stac_discovery", "metadata", "root"]
category_paths: dict[MetadataType_L | None, str] = {
    "stac_properties": "stac_discovery/properties/",
    "stac_discovery": "stac_discovery/",
    "metadata": "other_metadata/",
    "root": "",
    None: "",
}

# -----------------------------------------------------------------------------
# Convenience functions to identify eopf/cpm types
# -----------------------------------------------------------------------------


def is_eoproduct(obj: Any) -> bool:
    input_type = obj.__class__.__module__ + "." + obj.__class__.__name__
    return input_type == "eopf.product.eo_product.EOProduct"


def is_eocontainer(obj: Any) -> bool:
    input_type = obj.__class__.__module__ + "." + obj.__class__.__name__
    return input_type == "eopf.product.eo_product.EOContainer"


def is_eopf_adf(path_or_pattern: Any) -> bool:
    """

    :param path_or_pattern:
    :return:
    """
    adf = path_or_pattern
    # do not check full module and class name case because it doesn't match convention, it is not logical
    # so ... it may change soon (eopf.computing.abstract.ADF)
    match = hasattr(adf, "name")
    match = match and hasattr(adf, "path")
    match = match and hasattr(adf, "store_params")
    match = match and hasattr(adf, "data_ptr")
    return match


def is_any_path(path_or_pattern: Any) -> bool:
    return path_or_pattern.__class__.__name__ == "AnyPath" and hasattr(path_or_pattern, "cast")


T_DataPaths: TypeAlias = T_Paths | DataPath | Iterable[DataPath]

DATE_FORMAT = r"%Y%m%dT%H%M%S"
DEFAULT_COMPRESSOR = Blosc(
    cname="zstd",
    clevel=3,
    shuffle=Blosc.BITSHUFFLE,
)


class AttrsVisitor:
    def visit_node(self, root: T_Attributes, path: str, obj: T_Attributes) -> None:
        pass

    def is_applicable(self, xdt: DataTree) -> bool:
        return True


class DataTreeVisitor:
    def __init__(self, **kwargs: Any):
        self._kwargs = kwargs

    def visit_node(self, root: DataTree, path: str, obj: DataTree) -> None:
        pass

    def visit_dataarray(self, root: DataTree, path: str, obj: xarray.DataArray) -> None:
        pass

    def visit_attrs(
        self,
        root: DataTree,
        path: str,
        obj: dict[Hashable, Any],
        node: Any = None,
    ) -> None | dict[Hashable, Any]:
        """
        Handles visiting attributes in a DataTree structure.

        Note that by default a copy of the attributes is passed.
        If your visitor need to changes attributes values,
        you must return the updated attributes to force it.

        :param root: The root of the data tree being processed.
        :param path: The path within the tree where the operation is performed.
        :param obj: A dictionary representing the attributes to be visited or modified.
        :param node: An optional node reference associated with the data tree.
        :return: Modified attributes dictionary if applicable; otherwise, None.
        """
        pass

    def is_applicable(self, xdt: DataTree) -> bool:
        return True

    def start(self, root: DataTree) -> None:
        pass

    def end(self, root: DataTree) -> None:
        pass


class Converter:
    json_type: type
    py_type: type

    def to_json(self, value: Any, **kwargs: Any) -> Any:
        return str(value)

    def from_json(self, value: Any, **kwargs: Any) -> Any:
        return value


IsApplicableFunction: TypeAlias = Callable[[T_Attributes, str], bool]
