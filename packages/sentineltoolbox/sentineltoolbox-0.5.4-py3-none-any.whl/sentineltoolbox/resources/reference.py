__all__ = ["AUXILIARY_TREE", "PRODUCT_TREE", "PRODUCT", "AUXILIARY", "TASKTABLE"]

from sentineltoolbox.models.lazydatadir import DataFilter, LazyDataDir
from sentineltoolbox.models.sentineldatadir import SentinelDocDataFilter
from sentineltoolbox.models.tasktable import TaskTableDataFilter
from sentineltoolbox.readers.resources import load_resource_file
from sentineltoolbox.resources.data import AUXILIARY_TREE, PRODUCT_TREE


def load_reference_products(group: str = "PRODUCT", data_filter: DataFilter | None = None) -> LazyDataDir:
    from sentineltoolbox.filesystem_utils import get_universal_path

    if data_filter is None:
        data_filter = SentinelDocDataFilter()

    autodoc = load_resource_file("autodoc.json")
    paths = []
    for path in autodoc.get("paths", {}).get(group, []):
        secret_alias = autodoc.get("secrets_aliases", {}).get(path)
        if secret_alias:
            paths.append(get_universal_path(path, secret_alias=secret_alias))
        else:
            paths.append(get_universal_path(path))
    return LazyDataDir(paths, data_filter=data_filter)


PRODUCT = load_reference_products()
AUXILIARY = load_reference_products("AUXILIARY")
TASKTABLE = load_reference_products("TASKTABLE", data_filter=TaskTableDataFilter())
