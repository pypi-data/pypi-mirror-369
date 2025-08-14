import copy
import importlib.resources
from importlib.abc import Traversable
from pathlib import Path
from typing import Any, Literal, Self

from sentineltoolbox.configuration import get_config
from sentineltoolbox.exceptions import S3BucketCredentialNotFoundError
from sentineltoolbox.filesystem_utils import get_universal_path
from sentineltoolbox.models.upath import PathFsspec
from sentineltoolbox.readers._utils import (
    load_json_fp,
    load_toml_fp,
    load_yaml_fp,
    logger,
)


class ReloadableDict(dict):  # type: ignore
    def __init__(self, data: Any = None, **kwargs: Any):
        self._loader_kwargs = kwargs
        if data is None:
            dict.__init__(self)
            kwargs = copy.copy(kwargs)
            kwargs["recursive"] = False
            self.reload(**kwargs)
        else:
            dict.__init__(self, data)

    def reload(self, **kwargs: Any) -> Self:
        self.clear()
        _kwargs = copy.copy(self._loader_kwargs)
        _kwargs.update(kwargs)
        self.update(load_resource_file(**_kwargs))
        return self


def _load_path(path: Path | PathFsspec, fmt: Literal[".json", ".toml", ".txt", None] = None, **kwargs: Any) -> Any:
    if fmt is None:
        real_fmt = path.suffix
    else:
        real_fmt = fmt

    logger.info(f"load {real_fmt!r} resource file '{path}'")

    if real_fmt == ".json":
        with path.open("r", encoding="utf-8") as f:
            return load_json_fp(f)
    elif real_fmt == ".toml":
        with path.open("rb") as f:
            return load_toml_fp(f)
    elif real_fmt == ".yaml":
        with path.open("r", encoding="utf-8") as f:
            return load_yaml_fp(f)
    else:
        with path.open() as f:
            return f.read()


def get_resource_paths(
    relpath: str | Path,
    *,
    module: str = "sentineltoolbox.resources",
    **kwargs: Any,
) -> list[PathFsspec | Path]:
    conf = kwargs.get("configuration", get_config())
    user_resources = conf.data.get("resources", {}).get(module, [])
    if isinstance(relpath, Path):
        relpath = relpath.as_posix()
    else:
        relpath = str(relpath)

    # First, read extra user paths (default: empty)
    resource_files: list[Path | PathFsspec | Traversable] = []
    for user_resource_dir in user_resources:
        try:
            upath = get_universal_path(user_resource_dir) / relpath
        except (FileNotFoundError, S3BucketCredentialNotFoundError):
            pass
        else:
            resource_files.append(upath)

    # Then, read resources in config path (default: empty)
    resource_files.append(conf.config_path.parent / "resources" / module / relpath)

    # Then read package builtin resources
    # Get path to resource.
    # Remember, in some cases path can be inside a zip or wheel and not usable directly
    traversable: Traversable = importlib.resources.files(module) / str(relpath)
    resource_files.append(traversable)

    # To get a path that can be open, we must use as_file
    # See warning above!
    paths = []

    for filepath in resource_files:
        if isinstance(filepath, (PathFsspec, Path)) and filepath.exists():
            paths.append(filepath)
        elif isinstance(filepath, Traversable):
            with importlib.resources.as_file(filepath) as real_file_path:
                if real_file_path.exists():
                    paths.append(real_file_path)
                else:
                    continue
        else:
            continue
    if paths:
        return paths
    else:
        raise FileNotFoundError(relpath)


def get_resource_path(
    relpath: str | Path,
    *,
    module: str = "sentineltoolbox.resources",
    **kwargs: Any,
) -> Path | PathFsspec:
    return get_resource_paths(relpath, module=module, **kwargs)[0]


# @lru_cache(maxsize=20)
def load_resource_file(
    relpath: str | Path,
    *,
    fmt: Literal[".json", ".toml", ".txt", None] = None,
    module: str = "sentineltoolbox.resources",
    target_type: Any = None,
    **kwargs: Any,
) -> Any:
    """
    Function to load resource files. Resource file are files provided by python packages or by user.
    You do not need to know exactly where file is, you only need to know:
      - the package providing resources. For example "sentineltoolbox.resources"
      - the relative path of file you want to load. For example: "info.json" or "metadata/product_properties"

    This function search resources in different path, following this order:
      - path defined in sentineltoolbox configuration (if defined, see "Software Configuration")
      - ~/.eopf/resources/<module>/
      - python package defined by "module" keyword

    and return the first object found

    :param relpath: path relative to resource package
    :param fmt: file format. If not specified, tries to guess
    :param module: python module path containing resources. Default sentineltoolbox.resources
    :param target_type: if specified, ensure returned type correspond to expected type. If not raise error
    :return: loaded data. Can be dict (JSON), str (text file), ...
    """
    path = get_resource_path(relpath, module=module, **kwargs)
    data = _load_path(path, fmt=fmt, **kwargs)
    if target_type and not isinstance(data, target_type):
        raise IOError(f"data {path} doesn't match expected type {target_type!r}")
    if isinstance(data, dict):
        conf = kwargs.get("configuration", get_config())
        data = ReloadableDict(data=data, relpath=relpath, fmt=fmt, module=module, target_type=target_type)
        conf.resources[(module, relpath)] = data
        return data
    else:
        return data
