# all function are loaded in api module instead of in sentineltoolbox/__init__.py
# to avoid to load all dependencies each time.
# For example, pip loads sentineltoolbox to extract __version__ information.
# In this case, we don't want to load all sub packages and associated dependencies

# PLEASE NEVER NEVER IMPORT FEATURE THAT DEPENDS ON EOPF HERE. Such features must be in EOPF
# PLEASE NEVER FROM eopf_dep HERE

"""
ALL FUNCTIONS AND CLASSES OF "sentineltoolbox.api" FOLLOW THESE CONSTRAINTS:
  - signature is stable, API won't break in the future*
  - function is illustrated by a tutorial
  - global feature provided by these functions/classes must be listed in overview and release note
  - unittest must cover at least 70% of code
  - mypy must pass

If an API break is absolutely necessary:
  - minor version is increased and old API with deprecation warning is maintained if possible
  - a migration guide is written
Deprecated API will be removed in later release, generally in major release.
"""

from sentineltoolbox import raw_loaders

from .attributes import AttributeHandler, append_log, get_logs
from .configuration import get_config
from .converters import convert_to_datatree, convert_to_dict
from .datatree_utils import DataTreeHandler, get_array, get_datatree, patch_datatree
from .env import init_jupyter_env
from .filesystem_utils import (
    get_fsspec_filesystem,
    get_universal_path,
    get_url_and_credentials,
)
from .flags import create_flag_array, get_flag, update_flag
from .models.credentials import S3BucketCredentials, map_secret_aliases
from .models.filename_generator import (
    AdfFileNameGenerator,
    ProductFileNameGenerator,
    detect_filename_pattern,
    filename_generator,
)
from .proc_checkers import check_adfs, check_processor_inputs
from .readers.open_dataset import load_dataset, open_dataset
from .readers.open_datatree import load_datatree, open_datatree
from .readers.open_metadata import load_metadata
from .readers.open_standard_files import load_json, load_toml, load_yaml, open_json
from .readers.resources import get_resource_path, get_resource_paths, load_resource_file
from .typedefs import Adf

__all__: list[str] = [
    "Adf",
    "AdfFileNameGenerator",
    "AttributeHandler",
    "DataTreeHandler",
    "ProductFileNameGenerator",
    "S3BucketCredentials",
    "append_log",
    "check_adfs",
    "check_processor_inputs",
    "convert_to_datatree",
    "convert_to_dict",
    "create_flag_array",
    "detect_filename_pattern",
    "filename_generator",
    "get_array",
    "get_config",
    "get_datatree",
    "get_flag",
    "get_fsspec_filesystem",
    "get_logs",
    "get_resource_path",
    "get_resource_paths",
    "get_universal_path",
    "get_url_and_credentials",
    "init_jupyter_env",
    "load_dataset",
    "load_datatree",
    "load_json",
    "load_metadata",
    "load_resource_file",
    "load_toml",
    "load_yaml",
    "map_secret_aliases",
    "open_dataset",
    "open_datatree",
    "open_json",
    "patch_datatree",
    "raw_loaders",
    "update_flag",
]
