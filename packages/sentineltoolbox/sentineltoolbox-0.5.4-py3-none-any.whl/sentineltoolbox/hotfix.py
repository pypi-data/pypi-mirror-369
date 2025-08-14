__all__ = [
    "HotfixValue",
    "HotfixDataTree",
    "Hotfix",
    "load_hotfix",
    "HotfixManager",
    "HotfixPath",
    "HotfixWrapper",
]

import datetime
import logging
from importlib.metadata import entry_points
from pathlib import PurePosixPath
from typing import Any, Literal, MutableMapping, TypeAlias

from sentineltoolbox.typedefs import (
    AttrsVisitor,
    Converter,
    DataTreeVisitor,
    IsApplicableFunction,
    MetadataType_L,
    T_Attributes,
    fix_datetime,
)

"""
Some useful links:
https://eoframework.esa.int/display/CDSE/Copernicus+Data+Space+Ecosystem+%28CDSE%29+STAC+catalogue
"""

logger = logging.getLogger("sentineltoolbox")


def to_lower(value: Any, **kwargs: Any) -> str:
    new_value = value.lower()
    return new_value


def to_int(value: Any, **kwargs: Any) -> int | str:
    try:
        new_value: str | int = int(value)
    except ValueError:
        new_value = value
    return new_value


class ConverterDateTime(Converter):
    json_type: type = str
    py_type: type = datetime.datetime

    def to_json(self, value: Any, **kwargs: Any) -> Any:
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        else:
            return str(value)

    def from_json(self, value: Any, **kwargs: Any) -> Any:
        return fix_datetime(value)


HotfixType_L: TypeAlias = Literal["wrapper", "path", "value", "datatree", "alias", "attrs"]
HotfixPathInput: TypeAlias = dict[str, tuple[MetadataType_L, str | None]]
HotfixValueInput: TypeAlias = dict[MetadataType_L | str, dict[str, Any]]
HotfixWrapperInput: TypeAlias = dict[MetadataType_L, dict[str, Converter]]
HotfixDataTreeInput: TypeAlias = DataTreeVisitor
HotfixAttrsInput: TypeAlias = AttrsVisitor


class Hotfix:

    def __init__(
        self,
        data: Any,
        hotfix_type: HotfixType_L,
        is_applicable_func: IsApplicableFunction | None = None,
        **kwargs: Any,
    ):
        self.data = data
        self.hotfix_type = hotfix_type
        self.priority = kwargs.get("priority", 0)
        self.name = kwargs.get("name", f"{self.hotfix_type} hotfix")
        self.description = kwargs.get("description", "")
        if is_applicable_func is None:
            self._is_applicable = lambda attrs, product_type: True
        else:
            self._is_applicable = is_applicable_func

    def is_applicable(self, attrs: T_Attributes, product_type: str = "") -> bool:
        return self._is_applicable(attrs, product_type)


class HotfixPath(Hotfix):
    def __init__(
        self,
        data: HotfixPathInput,
        is_applicable_func: IsApplicableFunction | None = None,
        **kwargs: Any,
    ):
        """
        :param data:  example: {"stac_discovery/properties/eo:bands": ("stac_properties", "bands")},
        """
        final_data = {}
        for wrong_or_short, correct_data in data.items():
            cat, path = correct_data
            if path is None:
                path = PurePosixPath(wrong_or_short).name
            final_data[wrong_or_short] = (cat, path)
        super().__init__(data=final_data, hotfix_type="path", is_applicable_func=is_applicable_func, **kwargs)


class HotfixValue(Hotfix):
    def __init__(
        self,
        data: HotfixValueInput,
        is_applicable_func: IsApplicableFunction | None = None,
        **kwargs: Any,
    ):
        """
        :param data:  example: {
            "stac_properties": {
                "platform": lambda value, **kwargs: str(value).lower()
                },
            "/measurements/oa01_radiance": {
                "long_name":  lambda value, **kwargs: str(value).capitalize()
                }
            }
        }
        """
        super().__init__(data=data, hotfix_type="value", is_applicable_func=is_applicable_func, **kwargs)


class HotfixWrapper(Hotfix):
    def __init__(
        self,
        data: HotfixWrapperInput,
        is_applicable_func: IsApplicableFunction | None = None,
        **kwargs: Any,
    ):
        """
        :param data: {"stac_properties": {"created": ConverterDateTime()}}
        """
        super().__init__(data=data, hotfix_type="wrapper", is_applicable_func=is_applicable_func, **kwargs)


class HotfixDataTree(Hotfix):
    def __init__(
        self,
        data: HotfixDataTreeInput,
        is_applicable_func: IsApplicableFunction | None = None,
        **kwargs: Any,
    ):
        """
        :param data: {"stac_properties": {"created": ConverterDateTime()}}
        """
        super().__init__(data=data, hotfix_type="datatree", is_applicable_func=is_applicable_func, **kwargs)


class HotfixAttrs(Hotfix):
    def __init__(
        self,
        data: HotfixAttrsInput,
        is_applicable_func: IsApplicableFunction | None = None,
        **kwargs: Any,
    ):
        """
        :param data: {"stac_properties": {"created": ConverterDateTime()}}
        """
        super().__init__(data=data, hotfix_type="attrs", is_applicable_func=is_applicable_func, **kwargs)


class HotfixManager:
    def __init__(self, hotfix_list: list[Hotfix]):
        self.hotfix_list = list(sorted(hotfix_list, key=lambda hotfix: hotfix.priority, reverse=True))
        self.hotfix: MutableMapping[HotfixType_L, list[Hotfix]] = {}
        for hotfix in hotfix_list:
            self.hotfix.setdefault(hotfix.hotfix_type, []).append(hotfix)

    def _fixes(self, htype: HotfixType_L, attrs: T_Attributes | None = None, product_type: str = "") -> list[Hotfix]:
        valid_fixes = []
        if attrs is None:
            attrs = {}
        for hotfix in sorted(self.hotfix.get(htype, []), key=lambda hotfix: hotfix.priority, reverse=True):
            if hotfix.is_applicable(attrs, product_type):
                valid_fixes.append(hotfix)
        return valid_fixes

    def path(self, attrs: T_Attributes | None = None, product_type: str = "") -> list[Hotfix]:
        return self._fixes("path", attrs, product_type)

    def value(self, attrs: T_Attributes | None = None, product_type: str = "") -> list[Hotfix]:
        return self._fixes("value", attrs, product_type)

    def wrapper(self, attrs: T_Attributes | None = None, product_type: str = "") -> list[Hotfix]:
        return self._fixes("wrapper", attrs, product_type)

    def datatree(self, attrs: T_Attributes | None = None, product_type: str = "") -> list[Hotfix]:
        return self._fixes("datatree", attrs, product_type)

    def get_alias(
        self,
        path: str,
        attrs: T_Attributes | None = None,
        product_type: str = "",
        **kwargs: Any,
    ) -> tuple[MetadataType_L | None, str]:
        for hotfix in self.path(attrs, product_type):
            # search in prop lookuptable / short names
            if path in hotfix.data:
                return hotfix.data[path]
        return None, path


def load_hotfix() -> list[Hotfix]:
    lst = []
    for ep in entry_points(group="sentineltoolbox.hotfix"):
        logger.info(f"load plugin {ep.value}")
        data = ep.load()
        if isinstance(data, Hotfix):
            lst.append(data)
        elif isinstance(data, (list, tuple)):
            lst.extend(data)
    return lst
