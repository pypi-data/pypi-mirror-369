from pathlib import Path
from typing import Any

from sentineltoolbox.filesystem_utils import get_universal_path
from sentineltoolbox.models.upath import PathFsspec


def convert_path_to_eopf_store_inputs(
    path: str | Path | PathFsspec,
    **kwargs: Any,
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    eopf_args: list[Any] = []
    eopf_kwargs: dict[str, Any] = {}
    if isinstance(path, PathFsspec):
        eopf_args.append(path.url)
        eopf_kwargs["storage_options"] = path.fs.storage_options
    elif isinstance(path, (str, Path)):
        upath = get_universal_path(path, **kwargs)
        eopf_args.append(upath.url)
        eopf_kwargs["storage_options"] = upath.fs.storage_options
    else:
        raise NotImplementedError

    return tuple(eopf_args), eopf_kwargs
