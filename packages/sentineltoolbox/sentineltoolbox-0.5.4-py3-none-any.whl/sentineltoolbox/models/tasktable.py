from typing import Any

from sentineltoolbox.models.lazydatadir import DataFilter
from sentineltoolbox.readers.open_standard_files import open_json
from sentineltoolbox.typedefs import T_DataPath


class TaskTable(dict[str, Any]):
    @property
    def inputs(self) -> list[Any]:
        return self.get("list_of_inputs", self.get("data", {}).get("list_of_inputs", []))


class TaskTableDataFilter(DataFilter):
    """
    LazyDataDir that keep only one product by product_type
    Thanks to this simplification, data key == product_type.
    For example, key "OL1_RAC" refers to product like "TaskTable_OL1_RAC.json"
    """

    def is_data_path(self, path: T_DataPath) -> bool:
        return path.is_file() and path.suffix.lower() in [".json"]

    def data_keys(self, path: T_DataPath) -> list[str]:
        return [path.stem.replace("TaskTable_", "")]

    def open_data(self, path: T_DataPath) -> TaskTable:
        # JSON format
        return TaskTable(open_json(path))
