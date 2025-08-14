import json
import logging
from typing import Any

import tomli
from yaml.scanner import ScannerError

from sentineltoolbox.exceptions import LoadingDataError
from sentineltoolbox.filesystem_utils import get_url_and_credentials
from sentineltoolbox.readers import _utils
from sentineltoolbox.readers._utils import is_eopf_adf_loaded
from sentineltoolbox.typedefs import Credentials, PathMatchingCriteria, PathOrPattern


def open_json(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> dict[Any, Any]:
    if is_eopf_adf_loaded(path_or_pattern) and isinstance(path_or_pattern.data_ptr, dict):
        return path_or_pattern.data_ptr

    url, upath, credentials = get_url_and_credentials(
        path_or_pattern,
        credentials=credentials,
        match_criteria=match_criteria,
        **kwargs,
    )

    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))
    logger.info(f"open {url}")

    try:
        return _utils.load_json(upath)
    except json.JSONDecodeError:
        raise LoadingDataError(url)


def load_json(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> dict[Any, Any]:
    return open_json(path_or_pattern, credentials=credentials, match_criteria=match_criteria, **kwargs)


def open_toml(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> dict[Any, Any]:
    if is_eopf_adf_loaded(path_or_pattern) and isinstance(path_or_pattern.data_ptr, dict):
        return path_or_pattern.data_ptr

    url, upath, credentials = get_url_and_credentials(
        path_or_pattern,
        credentials=credentials,
        match_criteria=match_criteria,
        **kwargs,
    )

    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))
    logger.info(f"open {url}")

    try:
        return _utils.load_toml(upath)
    except tomli.TOMLDecodeError:
        raise LoadingDataError(url)


def load_toml(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> dict[Any, Any]:
    return open_toml(path_or_pattern, credentials=credentials, match_criteria=match_criteria, **kwargs)


def open_yaml(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> dict[Any, Any]:
    if is_eopf_adf_loaded(path_or_pattern) and isinstance(path_or_pattern.data_ptr, dict):
        return path_or_pattern.data_ptr

    url, upath, credentials = get_url_and_credentials(
        path_or_pattern,
        credentials=credentials,
        match_criteria=match_criteria,
        **kwargs,
    )

    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))
    logger.info(f"open {url}")

    try:
        return _utils.load_yaml(upath)
    except (ScannerError, UnicodeDecodeError):
        raise LoadingDataError(url)


def load_yaml(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> dict[Any, Any]:
    return open_yaml(path_or_pattern, credentials=credentials, match_criteria=match_criteria, **kwargs)
