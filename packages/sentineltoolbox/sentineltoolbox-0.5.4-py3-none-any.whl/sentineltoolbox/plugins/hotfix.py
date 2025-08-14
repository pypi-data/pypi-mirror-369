from typing import Any, Hashable

from packaging.version import Version
from xarray import DataTree

from sentineltoolbox import __version__
from sentineltoolbox.attributes import AttributeHandler
from sentineltoolbox.hotfix import (
    ConverterDateTime,
    HotfixAttrs,
    HotfixDataTree,
    HotfixPath,
    HotfixPathInput,
    HotfixValue,
    HotfixValueInput,
    HotfixWrapper,
    to_int,
    to_lower,
)
from sentineltoolbox.metadata_utils import guess_product_type
from sentineltoolbox.models.filename_generator import filename_generator
from sentineltoolbox.resources.data import DATAFILE_METADATA
from sentineltoolbox.typedefs import (
    AttrsVisitor,
    Converter,
    DataTreeVisitor,
    MetadataType_L,
    T_Attributes,
)

STAC_PRODUT_TYPE = "product:type"
STAC_TIMELINE = "product:timeline"

#################################################
# WRAPPERS
#################################################
# A wrapper simplifies the user's experience by automatically converting raw data into
# high-level Python types on the fly. For example, a date string is returned as a datetime object.
# It also performs the reverse conversion: if the user sets a datetime object, it is converted
# back to a string to support serialization.

# category / relative path -> Wrapper
WRAPPERS_GENERIC_FUNCTIONS: dict[MetadataType_L, dict[str, Converter]] = {
    "stac_properties": {
        "created": ConverterDateTime(),
        "end_datetime": ConverterDateTime(),
        "start_datetime": ConverterDateTime(),
    },
    "stac_discovery": {},
    "metadata": {},
    "root": {},
}

#################################################
# PATHS FIXES & SHORT NAMES
#################################################
# A "path fix" automatically replaces outdated or incorrect paths with valid ones.
# This is useful for all metadata where the name has changed.

# wrong path -> valid_category, valid_path
HOTFIX_PATHS_GENERIC: HotfixPathInput = {
    # {"name": ("category", None)}  if short name is equal to attribute path relative to category.
    #  This is equivalent to {"name": ("category", "name")}
    # {"short name": ("category", "relative path name")}  if short name is different
    # Ex: {"b0_id": ("stac_properties", "bands/0/name")}
    # {"/absolute/wrong/path": ("category", "relative/path")}
    # Ex: {"other_metadata/start_time": ("stac_properties", None)}
    # short names
    "bands": ("stac_properties", None),
    "created": ("stac_properties", None),
    "datatake_id": ("stac_properties", None),
    "datetime": ("stac_properties", None),
    "end_datetime": ("stac_properties", None),
    "eo:bands": ("stac_properties", "bands"),
    "eopf": ("stac_properties", None),
    "eopf:datastrip_id": ("stac_properties", None),
    "eopf:instrument_mode": ("stac_properties", None),
    "eopf:timeline": ("stac_properties", STAC_TIMELINE),
    "eopf:type": ("stac_properties", STAC_PRODUT_TYPE),
    "gsd": ("stac_properties", None),
    "instrument": ("stac_properties", None),
    "constellation": ("stac_properties", None),
    "mission": ("stac_properties", None),
    "platform": ("stac_properties", None),
    "processing:level": ("stac_properties", None),
    "processing:version": ("stac_properties", None),
    STAC_TIMELINE: ("stac_properties", None),
    STAC_PRODUT_TYPE: ("stac_properties", None),
    "providers": ("stac_properties", None),
    "start_datetime": ("stac_properties", None),
    "updated": ("stac_properties", None),
    # wrong paths
    "stac_discovery/properties/eo:bands": ("stac_properties", "bands"),
    "stac_discovery/properties/eopf:type": ("stac_properties", STAC_PRODUT_TYPE),
    "stac_discovery/properties/eopf:timeline": ("stac_properties", STAC_TIMELINE),
}


#################################################
# VALUE FIXES
#################################################
# Function used to fix definitely value

# category / relative path -> fix functions
HOTFIX_VALUES_GENERIC: HotfixValueInput = {
    "stac_properties": {
        "platform": to_lower,
        "mission": lambda value, **kwargs: "copernicus",
        "constellation": to_lower,
        "instrument": to_lower,
        "sat:relative_orbit": to_int,
        "datetime": lambda value, **kwargs: None,
    },
    "stac_discovery": {},
    "metadata": {},
    "root": {},
}


def fix_04x(attrs: T_Attributes, product_type: str = "") -> bool:
    """
    Apply some hotfix only if we are using sentineltoolbox >= 0.4.0.
    Reason is that sentinel processors are linked to older STAC specs and we don't want to break validation with
    STAC fixes. So keep old values, even if wrong.

    For most recent package using sentineltoolbox >= 0.4.0, we want up-to-date attributes so all fixes are applied

    :return:
    """
    return Version(__version__) > Version("0.4.0")


class FixSentinelDataTree(DataTreeVisitor):

    def visit_attrs(
        self,
        root: DataTree,
        path: str,
        obj: dict[Hashable, Any],
        node: Any = None,
    ) -> None | dict[Hashable, Any]:
        if "long_name" in obj:
            obj["description"] = obj.pop("long_name")
        attrs = AttributeHandler(obj)

        if path == "/":
            ptype = guess_product_type(root)
            metadata = DATAFILE_METADATA.get_metadata(ptype)
            if metadata:

                for attr_name in (STAC_PRODUT_TYPE, "processing:level", "mission", "instrument"):
                    value = metadata.get(attr_name)
                    if value:
                        if attr_name == "mission":
                            attr_name = "constellation"
                        attrs.set_attr(attr_name, value)

            # extract information from filename if not already set in metadata
            if hasattr(root, "reader_info"):
                name = root.reader_info.get("name")
                if name:
                    try:
                        fgen, fdata = filename_generator(name)
                    except NotImplementedError:
                        pass
                    else:
                        metadata = attrs.get_stac_property(default={})
                        for k, v in fgen.stac().get("stac_discovery", {}).get("properties", {}).items():
                            if k not in metadata:
                                attrs.set_stac_property(k, v)
            return obj
        return None


class FixSentinelRootAttrs(AttrsVisitor):

    def visit_node(self, root: T_Attributes, path: str, obj: T_Attributes) -> None:
        if path == "/":
            ptype = guess_product_type(root)
            if DATAFILE_METADATA.get_metadata(ptype).get("adf_or_product") == "product":
                # Add eopf_category if not exists
                other = obj.setdefault("other_metadata", {})
                other["eopf_category"] = other.get("eopf_category", "eoproduct")

            mission = obj.get("stac_discovery", {}).get("properties", {}).get("mission")
            is_sentinel = isinstance(mission, str) and mission.lower().startswith("sentinel")
            if mission is None:
                constellation = obj.get("stac_discovery", {}).get("properties", {}).get("constellation")
                is_sentinel |= isinstance(constellation, str) and constellation.lower().startswith("sentinel")
                if is_sentinel:
                    obj.setdefault("stac_discovery", {}).setdefault("properties", {})["mission"] = "copernicus"
            elif is_sentinel:
                obj.setdefault("stac_discovery", {}).setdefault("properties", {})["mission"] = "copernicus"


HOTFIX = [
    HotfixValue(
        HOTFIX_VALUES_GENERIC,
        priority=10,
        name="Generic Metadata Fix",
        description="Fix platform, instrument, ...",
    ),
    HotfixPath(HOTFIX_PATHS_GENERIC, priority=10, name="Generic Path Fix", description="Fix eopf:type, ..."),
    HotfixWrapper(
        WRAPPERS_GENERIC_FUNCTIONS,
        priority=10,
        name="Generic Wrappers",
        description="wrap dates<->datetime.",
    ),
    HotfixDataTree(
        FixSentinelDataTree(),
        priority=15,
        name="Fix sentinel datatree",
        description="Add product:type, level, ...",
    ),
    HotfixAttrs(
        FixSentinelRootAttrs(),
        priority=5,
        name="Fix sentinel metadata",
        description="Add mission=copernicus, ...",
        is_applicable_func=fix_04x,
    ),
]
