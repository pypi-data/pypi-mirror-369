from copy import copy
from functools import reduce
from json import JSONDecodeError
from pathlib import Path, PurePosixPath
from typing import Any

from sentineltoolbox.models.upath import PathFsspec
from sentineltoolbox.readers.resources import get_resource_path, load_resource_file

# https://raw.githubusercontent.com/CS-SI/eopf-stac-extension/main/json-schema/schema.json
# https://github.com/radiantearth/stac-spec/blob/master/item-spec/common-metadata.md
#

_STAC_DIRECTORY = get_resource_path("metadata/STAC")
if isinstance(_STAC_DIRECTORY, PathFsspec):
    STAC_DIRECTORY = Path(_STAC_DIRECTORY.path)
else:
    STAC_DIRECTORY = Path(str(_STAC_DIRECTORY))

STAC_URLS: dict[str, str] = load_resource_file("metadata/STAC/schemas.json", target_type=dict)


def extract_stac_data(schemas_root_path: Path, schemas_namespace: dict[str, str]) -> dict[str, Any]:
    """_summary_

    Parameters
    ----------
    schemas_root_path
        path to directory containing schemas. Must follow stac-extensions tree convention: ns/vx.y.z/schema.json

    schemas_namespace
        {"eo": "https://stac-extensions.github.io/eo/v1.1.0/schema.json"}

    Returns
    -------
        _description_
    """
    stac_local_paths = {}
    stac_definitions = {}
    stac_schemas = {}
    for ns, url in schemas_namespace.items():
        relurl = url.replace("https://stac-extensions.github.io/", "")
        # remove dots in dir names
        parts = relurl.split("/")
        parent_dir = "/".join([item.replace(".", "_") for item in parts[:-1]])
        relpath = PurePosixPath(parent_dir) / parts[-1]
        local_path = PurePosixPath(schemas_root_path) / relpath
        stac_local_paths[ns] = local_path
        try:
            schema = load_resource_file(f"metadata/STAC/{relpath}")
        except JSONDecodeError:
            pass
        else:
            stac_schemas[ns] = schema
            for name, data in schema.get("definitions", {}).get("fields", {}).get("properties", {}).items():
                if "$ref" in data:
                    def_path = data["$ref"]
                    try:
                        final_data = reduce(dict.get, def_path[2:].split("/"), schema)
                    except TypeError:
                        final_data = {}
                else:
                    final_data = data
                stac_definitions[name] = final_data
                if "title" in final_data and final_data["title"]:
                    data["description"] = final_data["title"]
    return dict(
        definitions=stac_definitions,
        paths=stac_local_paths,
        schemas=stac_schemas,
    )


STAC_DATA = extract_stac_data(
    schemas_root_path=STAC_DIRECTORY,
    schemas_namespace=STAC_URLS,
)
STAC_LOCAL_PATHS = STAC_DATA["paths"]
STAC_SCHEMAS = STAC_DATA["schemas"]
STAC_DEFINITIONS = STAC_DATA["definitions"]


STAC_PROPERTIES = copy(STAC_DEFINITIONS)
