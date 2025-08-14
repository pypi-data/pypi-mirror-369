import base64
import gc
import json
import logging
import os
import tempfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from sentineltoolbox._utils import split_protocol
from sentineltoolbox.readers._utils import load_toml

logger = logging.getLogger("sentineltoolbox")


class Configuration:
    _current: "Configuration | None" = None

    def __init__(self, **kwargs: Any) -> None:
        self._map_secret_alias_path: dict[str, list[str]] = {}
        self.config_path = kwargs.get("path", Path.home() / ".eopf/sentineltoolbox.toml")
        self._data: dict[Any, Any] = {}
        self._temporary_directories: dict[str, TemporaryDirectory[str]] = {}
        self.resources: dict[tuple[str, str], Any] = {}
        self.reload()

    def clear(self) -> None:
        self._map_secret_alias_path.clear()

    def reload(self) -> None:
        self.clear()
        if self.config_path.exists():
            self._data.update(load_toml(self.config_path))

        env_file = os.environ.get("SENTINELTOOLBOX_JSON_BASE64")
        if env_file:
            json_str = base64.b64decode(env_file).decode("utf-8")
            conf = json.loads(json_str)
            self._data.update(conf)

        for resource in self.resources.values():
            resource.reload()

        self.map_secret_aliases(self._data.get("secretsmap", {}))

    @classmethod
    def instance(cls, *, new: bool = False, **kwargs: Any) -> "Configuration":
        """

        :param new: if True, each call generate new instance, else, return default instance
        :param kwargs:
        :return:
        """
        if cls._current is None or new:
            cls._current = Configuration(**kwargs)
        return cls._current

    @property
    def data(self) -> dict[Any, Any]:
        return self._data

    def map_secret_aliases(self, map: dict[str, str]) -> None:
        if not isinstance(map, dict):
            raise ValueError(f"dict expected, got {map!r}")
        valid_paths: list[str] = []
        for alias, paths in map.items():
            if not isinstance(alias, str):
                logger.warning(f"Invalid alias. expect str, got {alias!r}")
                continue
            if isinstance(paths, str):
                valid_paths = [paths]
            elif isinstance(paths, (list, tuple)):
                # as expected, nothing to do
                valid_paths = paths
            else:
                logger.warning(f"Invalid data for {alias!r}: expect str or list, got {paths!r}")

            current_paths = self._map_secret_alias_path.get(alias, [])
            final_paths = []
            for path in valid_paths:
                if path in current_paths:
                    logger.warning(f"path {path!r} already registered for alias {alias!r}")
                elif isinstance(path, str) and path.startswith("s3://"):
                    final_paths.append(path)
                else:
                    logger.warning(f"Invalid data for {alias!r}: expect str starting with s3://, got {path!r}")

            if final_paths:
                self._map_secret_alias_path.setdefault(alias, []).extend(final_paths)
            else:
                logger.warning(f"Invalid data {valid_paths!r}: alias {alias!r} not updated")

    def get_secret_alias(self, path: str) -> str | None:
        protocols, relurl = split_protocol(path)
        strurl = f"s3://{relurl}"
        for secret_alias, secret_paths in self._map_secret_alias_path.items():
            for secret_path in secret_paths:
                if strurl.startswith(secret_path):
                    return secret_alias
        return None

    @property
    def secret_aliases(self) -> dict[str, list[str]]:
        return {k: v for k, v in self._map_secret_alias_path.items()}

    def get_temporary_directory(self, identifier: str = "") -> TemporaryDirectory[str]:
        if identifier and identifier in self._temporary_directories:
            tmpdir = self._temporary_directories[identifier]
            if Path(tmpdir.name).exists():
                return tmpdir

        tmpdir = tempfile.TemporaryDirectory(prefix="sentineltoolbox_")
        if not identifier:
            identifier = Path(tmpdir.name).name
        self._temporary_directories[identifier] = tmpdir
        return tmpdir

    def clean_temporary_directories(self) -> None:
        removed = []
        for identifier, tmpdir in self._temporary_directories.items():
            logger.info(f"clean tmp dir {tmpdir.name} used for {identifier!r}")
            try:
                tmpdir.cleanup()
            except PermissionError:
                pass
            else:
                removed.append(identifier)

        for identifier in removed:
            del self._temporary_directories[identifier]

    def __del__(self) -> None:
        gc.collect()
        self.clean_temporary_directories()


def get_config(**kwargs: Any) -> Configuration:
    return kwargs.get("configuration", Configuration.instance(**kwargs))
