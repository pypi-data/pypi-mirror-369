__all__ = [
    "AUXILIARY_TREE",
    "FIELDS_DESCRIPTION",
    "DATAFILE_METADATA",
    "PRODUCT_PATTERNS",
    "PRODUCT_TREE",
    "PROPERTIES_METADATA",
    "TERMS_METADATA",
    "product_summaries",
    "term_summaries",
    "XML_NAMESPACES",
    "XML_NAMESPACES_WITH_DUPLICATES",
    "fields_headers",
    "NAMESPACES",
]

import copy
from typing import Any, Iterable, Self

from sentineltoolbox.exceptions import DataSemanticConversionError
from sentineltoolbox.readers.resources import ReloadableDict, load_resource_file


class ResourceDb(ReloadableDict):
    def map(self, field: str) -> dict[str, Any]:
        map = {}
        for name, metadata in self.items():
            value = metadata.get(field)
            if value is not None:
                map[name] = metadata.get(field)
        return map

    def get_metadata(self, name: str, field: str | None = None, default: Any = None) -> Any:
        if field is None:
            return self.get(name, {})
        else:
            return self.get(name, {}).get(field, default)

    def summary(
        self,
        names: Iterable[str],
        fields: Iterable[str] = ("name", "description"),
    ) -> list[list[str]]:
        lst: list[list[str]] = []
        for name in names:
            item = []
            for field in fields:
                if field == "name":
                    item.append(name)
                else:
                    item.append(self.get_metadata(name, field, ""))
            lst.append(item)
        return lst


class ProductMetadataResource(ResourceDb):
    def __init__(self, data: ReloadableDict | None = None, **kwargs: Any):
        self.dpr_full_name: dict[str, str] = {}
        conf_kwargs = {}
        for k in ("configuration",):
            if k in kwargs:
                conf_kwargs[k] = kwargs[k]

        self.documentation = load_resource_file("metadata/product_documentation.toml", fmt=".toml", **conf_kwargs)
        self.legacy_to_dpr = load_resource_file("metadata/mapping_legacy_dpr.json", **conf_kwargs)
        self.dpr_to_legacy: dict[str, list[str]] = {}
        self.from_split_legacy: list[str] = []
        self.from_merged_legacy: list[str] = []
        super().__init__(data, **kwargs)
        self._field_mapping = {"level": "processing:level", "name": "product:type"}

    def reload(self, **kwargs: Any) -> Self:
        super().reload(**kwargs)
        if kwargs.get("recursive", True):
            if isinstance(self.legacy_to_dpr, ReloadableDict):
                self.legacy_to_dpr.reload()
            if isinstance(self.documentation, ReloadableDict):
                self.documentation.reload()
        self.dpr_full_name.clear()
        self.dpr_to_legacy.clear()

        for dpr_name, metadata in self.items():
            metadata["product:type"] = dpr_name
            if "ADF" in dpr_name:
                self.dpr_full_name[dpr_name] = dpr_name  # S03_ADF_OLINS -> S03_ADF_OLINS
                self.dpr_full_name[dpr_name[4:]] = dpr_name  # ADF_OLINS -> S03_ADF_OLINS
                self.dpr_full_name[dpr_name.split("_")[-1]] = dpr_name  # OLINS -> S03_ADF_OLINS
            else:
                self.dpr_full_name[dpr_name[3:]] = dpr_name  # OLCEFR -> S03OLCEFR
            self.dpr_full_name[dpr_name] = dpr_name  # S03OLCEFR -> S03OLCEFR

        for dpr_name, documentation in self.documentation.items():
            dpr_name = self.dpr_full_name.get(dpr_name, dpr_name)
            self.setdefault(dpr_name, {})["documentation"] = documentation

        self.from_split_legacy = []

        for legacy, dpr_outputs in self.legacy_to_dpr.items():
            if isinstance(dpr_outputs, str):
                dpr_outputs = [dpr_outputs]
            for dpr_name in dpr_outputs:
                if len(dpr_outputs) > 1:
                    self.from_split_legacy.append(dpr_name)
                self.dpr_to_legacy.setdefault(dpr_name, []).append(legacy)

        self.from_merged_legacy = []
        for dpr_name, legacies in self.dpr_to_legacy.items():
            if len(legacies) > 1:
                self.from_merged_legacy.append(dpr_name)

        return self

    def map(self, field: str) -> dict[str, Any]:
        map = {}
        for dpr_name, metadata in self.items():
            map[dpr_name] = metadata.get(field)
        return map

    def get_metadata(self, name: str, field: str | None = None, default: Any = None) -> Any:
        if field is None:
            return self.get(self.dpr_full_name.get(name, name), {})
        elif field == "legacy":
            return self.to_legacy_ptypes(name)
        else:
            field = self._field_mapping.get(field, field)
            return self.get(self.dpr_full_name.get(name, name), {}).get(field, default)

    def to_dpr_ptype(self, product_type: str, default: list[str] | str | None = None) -> str | list[str]:
        return self.legacy_to_dpr.get(product_type, self.dpr_full_name.get(product_type, default))

    def to_dpr_ptypes(self, product_type: str) -> list[str]:
        new_ptypes = self.legacy_to_dpr.get(product_type, self.dpr_full_name.get(product_type, []))
        if isinstance(new_ptypes, str):
            return [new_ptypes]
        elif isinstance(new_ptypes, list):
            return new_ptypes
        else:
            raise DataSemanticConversionError(
                f"Invalid value for legacy {product_type!r}.\n"
                f"Please specify correct semantic with semantic='XXXXX' Or fix db (wrong value: {new_ptypes!r})",
            )

    def to_legacy_ptype(self, product_type: str) -> list[str] | str:
        default = [product_type] if product_type in self.legacy_to_dpr else []
        result = self.dpr_to_legacy.get(self.dpr_full_name.get(product_type, product_type), default)
        if len(result) == 1:
            return result[0]
        else:
            return result

    def to_legacy_ptypes(self, product_type: str) -> list[str] | str:
        default = [product_type] if product_type in self.legacy_to_dpr else []
        return self.dpr_to_legacy.get(self.dpr_full_name.get(product_type, product_type), default)


DATAFILE_METADATA = ProductMetadataResource(data=None, relpath="metadata/datafiles.json")


FIELDS_DESCRIPTION = load_resource_file("metadata/fields_description.json")

PRODUCT_PATTERNS = load_resource_file("product_patterns.json")

# Note: The `load_resource_file` function can load user-defined data from the local user directory.
# Therefore, if patterns are extended by the user, prioritize user-defined patterns over the default generic ones.
PRODUCT_PATTERNS["S03OLCLFR"] = PRODUCT_PATTERNS.get("S03OLCLFR", PRODUCT_PATTERNS["S3OLCI"])
PRODUCT_PATTERNS["S03OLCLRR"] = PRODUCT_PATTERNS.get("S03OLCLRR", PRODUCT_PATTERNS["S3OLCI"])
PRODUCT_PATTERNS["S03OLCEFR"] = PRODUCT_PATTERNS.get("S03OLCEFR", PRODUCT_PATTERNS["S3OLCI"])
PRODUCT_PATTERNS["S03OLCERR"] = PRODUCT_PATTERNS.get("S03OLCERR", PRODUCT_PATTERNS["S3OLCI"])

PRODUCT_PATTERNS["S03SLSRBT"] = PRODUCT_PATTERNS.get("S03SLSRBT", PRODUCT_PATTERNS["SLSTR_RBT"])


PROPERTIES_METADATA = ResourceDb(relpath="metadata/properties.json")
TERMS_METADATA = ResourceDb(relpath="metadata/terms.json")

NAMESPACES = load_resource_file("namespaces.json")
XML_NAMESPACES = NAMESPACES.get("xml_namespaces", {})
XML_NAMESPACES_WITH_DUPLICATES = copy.copy(XML_NAMESPACES)
for alias, real_name in NAMESPACES.get("xml_aliases", {}).items():
    if real_name in XML_NAMESPACES:
        XML_NAMESPACES_WITH_DUPLICATES[alias] = XML_NAMESPACES[real_name]


class ProductTree(dict):  # type: ignore
    def __init__(self, metadata: ProductMetadataResource, tree_type: str = "product") -> None:
        super().__init__()
        self.s2: list[str] = []
        self.s3: list[str] = []
        self.all: list[str] = []
        self.s3_l0: list[str] = []

        self.metadata = metadata
        self.tree_type = tree_type
        self.reload(reload_metadata=False)

    def reload(self, **kwargs: Any) -> Self:
        if kwargs.get("recursive", True):
            self.metadata.reload()
        self.s2 = []
        self.s3 = []
        self.all = []
        self.s3_l0 = []
        for dpr_name, data in self.metadata.items():
            if data.get("adf_or_product") != self.tree_type:
                continue
            level = data.get("processing:level", "unknown")
            instrument = data.get("instrument", "X")
            mission = data.get("mission", "sentinel")
            self.all.append(dpr_name)
            if mission == "sentinel-2":
                self.s2.append(dpr_name)
            if mission == "sentinel-3":
                self.s3.append(dpr_name)
                if level == "L0":
                    self.s3_l0.append(dpr_name)
            if level == "L0" and mission == "sentinel":
                self.s3_l0.append(dpr_name)

            self.setdefault(mission, {}).setdefault(instrument, {}).setdefault(level, []).append(dpr_name)
            self.setdefault(mission, {}).setdefault(instrument, {}).setdefault("ALL", []).append(dpr_name)

        self.s2.sort()
        self.s3.sort()
        self.all.sort()
        self.s3_l0.sort()
        return self


AUXILIARY_TREE = ProductTree(DATAFILE_METADATA, tree_type="ADF")
PRODUCT_TREE = ProductTree(DATAFILE_METADATA)


def fields_headers(fields: Iterable[str]) -> list[Any]:
    return [FIELDS_DESCRIPTION.get(item, item) for item in fields]


def product_summaries(
    dpr_names: Iterable[str],
    fields: Iterable[str] = ("name", "description"),
) -> list[list[str]]:
    """
    >>> product_summaries(["OLCEFR", "OLCERR"]) # doctest: +ELLIPSIS
    [['OLCEFR', 'Full Resolution ...'], ['OLCERR', 'Reduced Resolution ...']]
    """
    return DATAFILE_METADATA.summary(dpr_names, fields)


def term_summaries(
    names: Iterable[str],
    fields: Iterable[str] = ("name", "description"),
) -> list[list[str]]:
    return TERMS_METADATA.summary(names, fields)
