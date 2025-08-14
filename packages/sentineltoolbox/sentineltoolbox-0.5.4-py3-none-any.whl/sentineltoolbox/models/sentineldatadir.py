from logging import getLogger
from typing import Any

from xarray import DataTree

import sentineltoolbox.api as stb
from sentineltoolbox.datatree_utils import DataTreeHandler
from sentineltoolbox.hotfix import load_hotfix
from sentineltoolbox.models.filename_generator import filename_generator
from sentineltoolbox.models.lazydatadir import DataFilter
from sentineltoolbox.readers.open_datatree import open_datatree
from sentineltoolbox.readers.open_metadata import load_metadata
from sentineltoolbox.typedefs import T_DataPath

LOGGER = getLogger("sentineltoolbox")


def is_json(path: T_DataPath) -> bool:
    suffixes: str = "".join(path.suffixes)
    return path.is_file() and suffixes in {".json", ".json.zip"}


def is_sentinel_data(path: T_DataPath) -> bool:
    suffixes: str = "".join(path.suffixes)
    return (path.is_dir() and suffixes.lower() in {".zarr", ".zarr.light"}) or (
        path.is_file() and str(path).endswith(".zarr.zip")
    )


class SentinelDataFilter(DataFilter):
    """
    Filter that consider as data ...
      - folders with .zarr suffix
      - json files
      - .json.zip and .zarr.zip files

    Key is the file name, extension included
    """

    def is_group_path(self, path: T_DataPath) -> bool:
        return path.is_dir() and not is_sentinel_data(path)

    def is_data_path(self, path: T_DataPath) -> bool:
        return is_json(path) or is_sentinel_data(path)

    def open_data(self, path: T_DataPath) -> DataTree:
        return open_datatree(path)

    def to_html(self, data: Any) -> str:
        if isinstance(data, DataTree):
            return "DataTree"
        else:
            try:
                return data._repr_html_()
            except AttributeError:
                return str(data)


class SentinelReferenceDataFilter(SentinelDataFilter):
    """
    SentinelReferenceDataFilter: SentinelDataFilter that keeps only one file by product type.
    This file is referenced by short key "PRODUCT_TYPE"
    """

    def data_keys(self, path: T_DataPath) -> list[str]:
        try:
            fgen, fdata = filename_generator(path.name.replace(".zip", ""))
        except NotImplementedError:
            return [path.name]
        else:
            keys = []
            if fdata["fmt"].startswith("adf"):
                keys.append(f"{fgen.mission}_ADF_{fgen.semantic}")
            else:
                keys.append(fgen.mission + fgen.semantic)
            return keys

    def open_data(self, path: T_DataPath) -> DataTree:
        return stb.open_datatree(path)


class SentinelDocDataFilter(SentinelReferenceDataFilter):
    """
    SentinelDocDataFilter: SentinelDataFilter that keeps only one file by product type and load product metadata as
    quick as possible. Drawbacks: arrays are replaced with empty arrays
    """

    def open_data(self, path: T_DataPath) -> DataTree:
        xdt = load_metadata(path).container()
        hotfix_list = load_hotfix()
        hdl = DataTreeHandler(xdt, hotfix_list=hotfix_list)
        hdl.fix()
        return xdt

    def to_html(self, data: Any) -> str:
        if isinstance(data, DataTree):
            return "DataTree (metadata only)"
        else:
            try:
                return data._repr_html_()
            except AttributeError:
                return str(data)
