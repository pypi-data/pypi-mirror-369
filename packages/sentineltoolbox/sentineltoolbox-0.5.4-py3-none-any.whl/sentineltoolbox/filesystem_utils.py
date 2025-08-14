import datetime
import json
import logging
import mimetypes
import os
import shutil
import stat
import sys
import tarfile
import zipfile
from copy import copy
from importlib.resources.abc import Traversable
from json import JSONDecodeError
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, List

import fsspec
import s3fs

from sentineltoolbox._utils import build_url, fix_url, split_protocol
from sentineltoolbox.configuration import get_config
from sentineltoolbox.exceptions import MultipleResultsError
from sentineltoolbox.models.credentials import S3BucketCredentials
from sentineltoolbox.models.upath import PathFsspec
from sentineltoolbox.typedefs import (
    Credentials,
    PathOrPattern,
    fix_datetime,
    is_any_path,
    is_eopf_adf,
    is_json,
)

logger = logging.getLogger("sentineltoolbox")

MIMETYPES_ZIP = [("application/x-zip-compressed", None), ("application/zip", None)]
MIMETYPES_TAR = [("application/x-tar", "gzip"), ("application/x-tar", "bzip2")]
MIMETYPES_COMPRESSED = MIMETYPES_ZIP + MIMETYPES_TAR


def detect_sentineltoolbox_engine(url: str) -> str | None:
    """
    Infers the appropriate engine to use for loading a dataset based ...
      - on the file extension
      - and/or specific patterns in the URL

    This function examines the file extension and content of the provided URL to determine the most suitable
    engine for processing the dataset. If no suitable engine is identified, it returns `None`.

    For engine compatible with xarray, please use fix_kwargs_xarray_engine.

    Parameters:
        url (str): The URL or file path of the dataset to analyze.

    Returns:
        Optional[str]: The inferred engine as a string, or `None` if no engine could be determined.

    Supported Engines:
        - `"zarr"`: For `.zarr` file extensions.
        - `"sentinel-3"`: For `.SEN3` file extensions.
        - `"sentinel-2"`: For `.SAFE` file extensions containing `"MSI"` in the URL.
        - `"h5netcdf"`: For `.nc` file extensions.
        - `"json"`: For JSON files determined by the `is_json` function.
        - `None`: When no matching criteria are found.

    >>> detect_sentineltoolbox_engine("S2A_MSIL1A.SAFE")
    'sentinel-2'
    """
    ext = PurePosixPath(url).suffixes
    if ".zarr" in ext:
        engine = "zarr"
    elif ".SEN3" in ext:
        engine = "sentinel-3"
    elif ".SAFE" in ext and "MSI" in url:
        engine = "sentinel-2"
    elif ".nc" in ext:
        engine = "h5netcdf"
    elif is_json(url):
        engine = "json"
    else:
        engine = None
    return engine


def fix_kwargs_xarray_engine(url: str, kwargs: Any) -> None:
    """
    Determines and sets the appropriate engine for reading an xarray dataset based on the file extension in the URL.

    Main goal is to force to use h5netcdf engine for netcdf files.

    This function modifies the `kwargs` dictionary in-place. If the `engine` key in `kwargs` is not set,
    it attempts to infer the correct engine from the file extension of the provided URL. Supported file
    extensions include `.zarr` for the Zarr format and `.nc` for NetCDF files.

    Parameters:
        url (str): The URL or file path of the dataset to be loaded.
        kwargs (Any): A dictionary-like object containing parameters for loading the dataset.
                      If the `engine` key is unset, it will be updated with the appropriate value.

    Modifications:
        - If the file extension in the URL is `.zarr`, sets `kwargs["engine"]` to `"zarr"`.
        - If the file extension in the URL is `.nc`, sets `kwargs["engine"]` to `"h5netcdf"`.
        - If no matching file extension is found, sets `kwargs["engine"]` to `None`.

    Example:
        kwargs = {}
        fix_kwargs_xarray_engine("dataset.zarr", kwargs)
        print(kwargs)  # Output: {"engine": "zarr"}
    """
    if kwargs.get("engine") is None:
        ext = PurePosixPath(url).suffixes
        if ".zarr" in ext:
            engine = "zarr"
        elif ".nc" in ext:
            engine = "h5netcdf"
        else:
            engine = None

        kwargs["engine"] = engine


def fix_credentials(url: str, **kwargs: Any) -> Credentials | None:
    protocols, path = split_protocol(url)
    credentials = kwargs.get("credentials")
    if "s3" in protocols:
        if credentials is None:
            conf = get_config(**kwargs)
            secret_alias = conf.get_secret_alias(url)
            if secret_alias:
                kwargs["secret_alias"] = secret_alias
            credentials = S3BucketCredentials.from_env(**kwargs)
    else:
        credentials = None
    return credentials


def get_directory_mtime(
    fs: fsspec.spec.AbstractFileSystem,
    path: str,
    preferred: str = ".zmetadata",
) -> datetime.datetime:
    file_path = None
    for child_path in fs.ls(path):
        child_name = PurePosixPath(child_path).name
        if fs.isfile(child_path):
            file_path = child_path
            if child_name == preferred:
                break
    if file_path is None:
        return datetime.datetime.now()
    else:
        return fs.modified(file_path)


def secure_extract_tar(
    tar_path_or_fileobj: str | Path | PurePosixPath | BinaryIO,
    output_dir: str | Path | PurePosixPath,
    max_members: int = 5000,
    max_total_size: int = 10_000_000_000,  # 10 GB
) -> None:
    """
    Safely extract a tar archive to a given directory, with security checks.

    Uses filter="data" to prevent path traversal and extraction of special files.

    Note: name of this function use adjective "secure" instead of "safe" to avoid confusion with sentinel "safe" format
    (*.SAFE, *.SEN3)

    Args:
        tar_path_or_fileobj: Path to the tar archive or open file object
        output_dir: Directory to extract files into.
        max_members: Maximum number of files allowed in the archive.
        max_total_size: Maximum total uncompressed size allowed (in bytes).

    Raises:
        Exception: If the archive is suspicious (too many files, too large).
    """
    if isinstance(tar_path_or_fileobj, (Path, PurePosixPath, str)):
        with tarfile.open(tar_path_or_fileobj, "r") as tar:
            # "r" and "r:*" are equivalent.
            # It means that tarfile guess compression used (gzip, bz2, lzma) and use the right decompressor
            secure_extract_tar_obj(tar, output_dir, max_members, max_total_size)
    else:
        with tarfile.open(fileobj=tar_path_or_fileobj) as tar:
            secure_extract_tar_obj(tar, output_dir, max_members, max_total_size)


def secure_extract_tar_obj(
    fileobj: tarfile.TarFile,
    output_dir: str | Path | PurePosixPath,
    max_members: int,
    max_total_size: int,
) -> None:

    total_size = 0
    members = fileobj.getmembers()

    if len(members) > max_members:
        raise Exception(f"Archive has too many files ({len(members)} > {max_members})")

    for member in members:
        if member.isfile():
            if member.size < 0:
                raise Exception("File with negative size detected")
            total_size += member.size
            if total_size > max_total_size:
                raise Exception(f"Archive is too large ({total_size} bytes > {max_total_size} bytes)")

    # filter="data" disables path traversal and special file extraction
    # available only since 3.12
    # See https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractall
    if sys.version_info >= (3, 12):
        fileobj.extractall(path=output_dir, filter="data")
    else:
        fileobj.extractall(path=output_dir)  # nosec B202


def can_trust_zip_path(base_path: str, target_path: str, follow_symlinks: bool = True) -> bool:
    """
    Check if the target path is within the base path.

    Args:
        base_path (str): The base directory where files should be extracted.
        target_path (str): The target path to validate.
        follow_symlinks (bool): Whether to resolve symbolic links. Defaults to True.

    Returns:
        bool: True if the target path is within the base path, False otherwise.
    """
    if follow_symlinks:
        base_path = os.path.realpath(base_path)
        target_path = os.path.realpath(target_path)
    else:
        base_path = os.path.abspath(base_path)
        target_path = os.path.abspath(target_path)

    return os.path.commonprefix([base_path, target_path]) == base_path


def is_special_file(file_path: str) -> bool:
    """
    Check if the file is a symbolic link or a special file type (block, char, FIFO, socket).

    Args:
        file_path (str): The path of the file to check.

    Returns:
        bool: True if the file is a special type, False otherwise.
    """
    try:
        # Get the file's mode to check for block/char devices, FIFO, or socket
        mode = os.stat(file_path).st_mode
        if stat.S_ISBLK(mode) or stat.S_ISCHR(mode) or stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode):
            return True
    except OSError:
        pass

    return False


def list_zip_allowed_members(zip_ref: zipfile.ZipFile, extract_to: str) -> List[str]:
    """
    Filter and return a list of members with safe paths from the zip archive.

    Args:
        zip_ref (zipfile.ZipFile): A reference to the open zip file.
        extract_to (str): The base directory where files should be extracted.

    Returns:
        List[str]: A list of safe members to extract.
    """
    allowed_members: List[str] = []

    for member in zip_ref.namelist():
        member_path = os.path.join(extract_to, member)
        if can_trust_zip_path(extract_to, member_path):
            if not is_special_file(member_path):
                allowed_members.append(member)

    return allowed_members


def _get_fsspec_filesystem_from_url_and_credentials(
    url: str,
    credentials: Credentials | None = None,
    **kwargs: Any,
) -> Any:
    protocols, relurl = split_protocol(url)
    if "filesystem" in kwargs and kwargs["filesystem"] is not None:
        return kwargs["filesystem"], relurl
    else:
        if credentials and "s3" in protocols:
            fsspec_options = credentials.to_kwargs(target=fsspec.filesystem)
        else:
            fsspec_options = {"protocol": "::".join(protocols)}
            fsspec_options["protocol"] = fsspec_options["protocol"].replace("zip::file", "file")
            fsspec_options["protocol"] = fsspec_options["protocol"].replace("file::zip", "file")
        return fsspec.filesystem(**fsspec_options), relurl


def get_fsspec_filesystem(
    path_or_pattern: PathOrPattern,
    **kwargs: Any,
) -> tuple[Any, PurePosixPath]:
    """
    Function to instantiate fsspec.filesystem from url.
    Return path relative to filesystem. Can be absolute or not depending on fs.
    This function clean url and extract credentials (if necessary) for you.

    >>> fs, root = get_fsspec_filesystem("tests")
    >>> fs, root = get_fsspec_filesystem("s3://s3-input/Products/", secret_alias="s3-input") # doctest: +SKIP
    >>> fs.ls(root) # doctest: +SKIP

    See `fsspec documentation <https://filesystem-spec.readthedocs.io/en/latest/usage.html>`_

    :param path_or_pattern: path to use to build filesystem
    :param kwargs: see generic input parameters in :obj:`sentineltoolbox.typedefs` module
    :return: fsspec.AbstractFileSystem, path relative to filesystem
    """
    fs = kwargs.get("filesystem")
    if fs is None:
        _, upath, _ = get_url_and_credentials(path_or_pattern, **kwargs)
        return upath.fs, PurePosixPath(upath.path)
    else:
        _, relurl = split_protocol(path_or_pattern)
        return fs, relurl


def get_universal_path(
    path_or_pattern: PathOrPattern,
    **kwargs: Any,
) -> PathFsspec:
    """
    Return a universal Path: a path following pathlib.Path api but supporting all kind of path (local, s3 bucket, ...)
    thanks to fsspec. fsspec/universal_pathlib is the candidate for this but is not enough mature for the moment
    (for example, protocol chaining is not supported, see https://github.com/fsspec/universal_pathlib/issues/28)
    So we define ...
      - protocol DataPath: a subset of pathlib.Path
      - PathFsspec: an implementation of DataPath based on fsspec, used until UPath doesn't work with chaining
      - upath.UPath: will be used as soon as possible

    In all cases, return type will be PathFsspec

    :param path_or_pattern:

    :param kwargs:
    :return:
    """
    url, upath, _ = get_url_and_credentials(path_or_pattern, **kwargs)
    return upath


def _resolve_pattern(
    pattern: str | Path | Traversable,
    **kwargs: Any,
) -> tuple[str, PathFsspec, Credentials | None]:
    """
    Resolve a file pattern into a specific file or path, across various file systems or protocols.

    This function accepts a file path or pattern (which can include wildcards) and attempts to resolve
    it to a single file or path. It supports various protocols (e.g., local filesystem, cloud storage, zip files)
    and uses optional credentials for authentication in cases where a remote file system is involved (e.g., S3, GCS).
    If multiple files match the pattern, the function selects the one with the most recent creation or modification
    date by default.

    Parameters
    ----------
    pattern:
        The file pattern to resolve. This can be a string representing the path or a `Path` object. The pattern may
        contain wildcards or partial file names.

    see :obj:`sentineltoolbox.typedefs` for details on
        - path_or_pattern
        - match_criteria


    Returns
    -------
    tuple[str, PathFsspec]
        A tuple containing:
        - The fully-resolved URL of the selected file.
        - A `PathFsspec` object representing the resolved file

    Raises
    ------
    ValueError
        If the pattern cannot be resolved to any file or if an invalid pattern is provided.
    MultipleResultsError
        If multiple files match the pattern and cannot be disambiguated based on the given criteria.

    Example
    -------
    >>> _resolve_pattern("s3://my-bucket/data/*.csv", credentials=my_creds) # doctest: +SKIP
    ("s3://my-bucket/data/file_2023.csv", PathFsspec(...))

    Notes
    -----
    - The function supports various protocols via `fsspec`, including local files ("file://"), cloud storage (S3, GCS),
      and zip files ("zip://").
    - When the pattern resolves to multiple files, it selects the one with the latest creation or modification date by
      default.
    - For ADF (Arc Data Files), the creation date is extracted directly from the filename.
    """
    credentials = fix_credentials(str(pattern), **kwargs)
    match_criteria = kwargs.get("match_criteria", "last_creation_date")
    protocols, relurl = split_protocol(str(pattern))

    # If the protocol involves the local file system, resolve the relative URL to an absolute path.
    # ex ../../sample.zarr -> /home/user/sample.zarr
    if "file" in protocols:
        relurl = PurePosixPath(Path(relurl.as_posix()).resolve().as_posix())

    # If a specific file system is passed in via kwargs, use it. Otherwise, resolve protocols.
    if "filesystem" in kwargs:
        fs: fsspec.spec.AbstractFileSystem = kwargs["filesystem"]
    else:
        resolve_protocols = copy(protocols)
        if "zip" in protocols:
            # Here we want to list all files/directory matching pattern, so we want to list all files sibling
            # current file. Remove zip because we want to manipulate parent dir, not file itself.
            resolve_protocols.remove("zip")

        if credentials is not None:
            # WARNING: use skip_instance_cache=True to create new instance
            # This is forced because data is not well refreshed. For example fs.ls returns old list
            fs = fsspec.filesystem(**credentials.to_kwargs(target=fsspec.filesystem), skip_instance_cache=True)
        else:
            fs = fsspec.filesystem("::".join(resolve_protocols))

    paths = fs.expand_path(str(relurl))

    if not paths:
        raise ValueError(f"Invalid pattern {pattern!r}")
    elif len(paths) == 1:
        url = fix_url("::".join(protocols) + "://" + str(paths[0]).replace(":/", ":\\"))
        protocols, relurl = split_protocol(url)
        upath = PathFsspec(relurl, fs=fs)
        return url, upath, credentials
    elif len(paths) > 1:
        from sentineltoolbox.models.filename_generator import detect_filename_pattern

        dates = {}
        for path in paths:
            ftype = detect_filename_pattern(path)
            if ftype.startswith("adf") and match_criteria == "last_creation_date":
                creation_date = fix_datetime(PurePosixPath(path).name.split(".")[0].split("_")[-1])
            else:
                try:
                    creation_date = fs.modified(path)
                except IsADirectoryError:
                    creation_date = get_directory_mtime(fs, path)
            dates[path] = creation_date

        last, last_date = None, datetime.datetime(1, 1, 1, 1, tzinfo=datetime.timezone.utc)
        for path, creation_date in dates.items():
            if creation_date > last_date:
                last = path
                last_date = creation_date
            elif creation_date == last_date:
                raise MultipleResultsError(
                    f"cannot select file from pattern {pattern}.\n"  # nosec B608
                    f"files {last} and {path} have same creation date",  # nosec B608
                )
        if last:
            url = fix_url("::".join(protocols) + "://" + str(last))
            protocols, relurl = split_protocol(url)
            upath = PathFsspec(relurl, fs=fs)
            logger.info(f"Select {url!r} for pattern {pattern!r}")
            return url, upath, credentials
        else:
            raise ValueError(f"cannot select file from pattern {pattern}")  # nosec B608
    else:
        raise ValueError(f"Cannot expand pattern {pattern!r}: result: {paths}")  # nosec B608


def _get_url_and_credentials_from_eopf_inputs(
    path_or_pattern: PathOrPattern,
    **kwargs: Any,
) -> tuple[str, Credentials | None]:
    credentials = kwargs.get("credentials")
    if is_eopf_adf(path_or_pattern):
        any_path = path_or_pattern.path
        if not is_any_path(any_path):
            return any_path, credentials
        # TODO: manage case where store_options is defined but empty
        if not path_or_pattern.store_params:
            if isinstance(any_path._fs, s3fs.S3FileSystem):
                storage_options = any_path._fs.storage_options
                credentials = S3BucketCredentials.from_kwargs(**storage_options)
            else:
                credentials = None
        else:
            storage_options = path_or_pattern.store_params["storage_options"]
            credentials = S3BucketCredentials.from_kwargs(**storage_options)
        kwargs["credentials"] = credentials
    else:
        any_path = path_or_pattern
        if "ADF" in str(any_path.original_url):
            logger.warning(
                "For ADF, prefer passing whole AuxiliaryDataFile/ADF object instead of AuxiliaryDataFile.path",
            )
        if isinstance(any_path._fs, s3fs.S3FileSystem):
            storage_options = any_path._fs.storage_options
            kwargs["credentials"] = S3BucketCredentials.from_kwargs(**storage_options)

    try:
        url = str(any_path.original_url)
    except AttributeError:
        url = str(any_path)
    try:
        url, upath, credentials = _resolve_pattern(url, **kwargs)
    except NotImplementedError:
        pass
    return url, credentials


def _filename_without_compression_extension(path_str_or_path: str | Path) -> str:
    filename = Path(path_str_or_path).name
    for ext in (".zip", ".tgz", ".tar.gz"):
        if filename.endswith(ext):
            return filename[: -len(ext)]
    return filename


def _copy_to_local_url(path: str | Path, local_url: Path, overwrite: bool) -> None:
    """
    Copy a file from the source path to the local URL location.

    Args:
        path (str): The source file path to copy.
        local_url (Path): The destination path where the file will be copied.
        overwrite (bool): If True, allows overwriting the file at the destination if it exists.

    Raises:
        FileExistsError: If the destination file exists and overwrite is set to False.
    """
    src_path = Path(path)
    if local_url.exists():
        if overwrite:
            if src_path.is_file():
                shutil.copy2(src_path, local_url)
            else:
                shutil.copytree(src_path, local_url, dirs_exist_ok=True)
        else:
            raise FileExistsError(f"{local_url}. Use overwrite=True to force overwrite")
    else:
        if src_path.is_file():
            shutil.copy2(src_path, local_url)
        else:
            shutil.copytree(src_path, local_url)


def _move_to_local_url(path: str | Path, local_url: Path, overwrite: bool) -> None:
    """
    Move a file from the source path to the local URL location.

    Args:
        path (str): The source file path to move.
        local_url (Path): The destination path where the file will be moved.
        overwrite (bool): If True, allows overwriting the file at the destination if it exists.

    Raises:
        FileExistsError: If the destination file exists and overwrite is set to False.
    """
    src_path = Path(path)
    if local_url.exists():
        if overwrite:
            try:
                logger.info(f"Move {src_path=} to {local_url=}")
                if local_url.is_file():
                    local_url.unlink()
                elif local_url.is_dir():
                    shutil.rmtree(local_url)
                shutil.move(src_path, local_url)
            except Exception as err:
                logger.exception(err)
        else:
            raise FileExistsError(f"{local_url}. Use overwrite=True to force overwrite")
    else:
        shutil.move(src_path, local_url)


def uncompress_or_cache_data_if_required(url: str, **kwargs: Any) -> tuple[str, PathFsspec, Credentials | None, bool]:
    """
    This function checks whether a given file (from URL) needs to be uncompressed or cached locally.
    It supports compressed files like zip or tar.gz, and the input file can be located either locally or on an S3 bucket

    Args:
        url (str): The URL of the file to process.
        **kwargs: Additional options.
            - uncompress (bool): If True, uncompress the file
            - cache (bool): If True, cache the file locally.
            - local_copy_dir (str or Path): Optional directory to store the local copy. If not provided, a temporary
              directory will be used
            - overwrite (bool): if local_copy_dir is set, overwrite is False by default and you can change it to True
              to replace existing data. If local_copy_dir is not set, data are copied in a temporary dir so there is
              no risk of loss of important data. For this reason, overwrite is set to True by default.

    Returns:
        * str: The path to the local file (cached or uncompressed), or the original URL if no local copy was needed
        * True if local file, False if no change

    Raises:
        NotImplementedError: If the file's compression format or protocols are not supported.
    """
    mtype = mimetypes.guess_type(url)
    need_local_copy, need_uncompress = is_local_copy_or_uncompression_required(url, mtype=mtype, **kwargs)
    original_url = url

    if not need_local_copy:
        upath = kwargs.get("universal_path")
        if upath is None:
            fs, relurl = _get_fsspec_filesystem_from_url_and_credentials(url, **kwargs)
            upath = PathFsspec(relurl, fs=fs)
        return fix_url(str(url)), upath, kwargs.get("credentials"), need_local_copy

    conf = get_config(**kwargs)
    protocols, path = split_protocol(url)

    # We force uncompress, so path must not be open with zip: protocol
    if need_uncompress and "zip" in protocols:
        protocols.remove("zip")
        url = build_url(protocols, path)

    # If no local directory is provided, use a temporary directory
    local_copy_dir = kwargs.get("local_copy_dir")
    success = False
    reason = "Unknown error"
    is_tmp_dir = False
    if local_copy_dir is None:
        is_tmp_dir = True
        # create temporary dir at each call because netcdf doesn't release file and we cannot overwrite it
        local_copy_dir = conf.get_temporary_directory(identifier=path.name).name
        success = True
    elif isinstance(local_copy_dir, (str, Path)):
        # If a local directory is provided, ensure it's a valid directory
        local_copy_dir = Path(local_copy_dir).expanduser().resolve()
        if local_copy_dir.is_file():
            success = False
            reason = f"local_copy_dir {local_copy_dir!r} is a file"
        else:
            local_copy_dir.mkdir(parents=True, exist_ok=True)
            local_copy_dir = str(local_copy_dir)
            success = True

    # If the directory is invalid, log a warning and fall back to a temporary directory
    if not success:
        logger.warning(f"Invalid local directory {local_copy_dir!r}. {reason}. Temporary directory used.")
        local_copy_dir = conf.get_temporary_directory(str(path)).name
        is_tmp_dir = True

    overwrite = kwargs.get("overwrite", is_tmp_dir)

    # Read cache information to look if data has been cached previously.
    # TODO: support case of two times the same file with different sources
    #  for example: both s3://bucket/sample.zarr and local/dir/sample.zarr are cached in cache/sample.zarr
    #  idea1: create subfolder cache/1/sample.zarr with 1 corresponding to fs1
    #  idea2: keep folder tree
    #  idea3: combine idea2 with md5sum/mtime
    cache_mapping = {}
    cache_mapping_path = Path(local_copy_dir, "cache.json")
    if cache_mapping_path.exists():
        with open(cache_mapping_path, "r", encoding="utf-8") as cache_fp:
            try:
                cache_mapping = json.load(cache_fp)
            except JSONDecodeError as e:
                logger.exception(e)
                backup = str(cache_mapping_path) + ".backup_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                logger.warning("Current cache file is corrupted. Create a new empty cache file.")
                logger.warning(f"backup previous (corrupted) cache file {backup}")
                # warning. datetime.isoformat() is not compatible with windows as it contains ":"
                shutil.copy(str(cache_mapping_path), backup)
    cache_id = f"{url};uncompress={need_uncompress}"

    if cache_id in cache_mapping and not kwargs.get("force_reload", False):
        local_cache_url = Path(local_copy_dir, cache_mapping[cache_id]["local_url"])
        if local_cache_url.exists():
            logger.info(f"use cached data {local_cache_url}")
            # Use local file, no need of credentials
            credentials = None
            fs, relurl = _get_fsspec_filesystem_from_url_and_credentials(
                local_cache_url.as_posix(),
                credentials=credentials,
            )
            upath = PathFsspec(relurl, fs=fs, original_url=original_url)
            return fix_url(local_cache_url.as_posix()), upath, credentials, need_local_copy

    if need_uncompress:
        # Unzip / Untar in temporary directory
        conf = get_config()
        with conf.get_temporary_directory() as tmp_uncompress_dir:
            if "file" in protocols:
                if mtype in MIMETYPES_ZIP:
                    with zipfile.ZipFile(path, "r") as zip_ref:
                        # Extraction des fichiers dans le dossier temporaire
                        zip_ref.extractall(
                            tmp_uncompress_dir,
                            members=list_zip_allowed_members(zip_ref, tmp_uncompress_dir),
                        )
                elif mtype in MIMETYPES_TAR:
                    secure_extract_tar(path, tmp_uncompress_dir)
                else:
                    raise NotImplementedError(f"Cannot uncompress {'/'.join([str(part) for part in mtype])}")
            elif "s3" in protocols:
                url = build_url(protocols, path)

                kwargs["filesystem"] = None
                fs, relurl = _get_fsspec_filesystem_from_url_and_credentials(url, **kwargs)
                upath = PathFsspec(relurl, fs=fs, original_url=original_url)
                upath.compression = None
                if mtype in MIMETYPES_ZIP:
                    with upath.open(mode="rb") as src:
                        try:
                            with zipfile.ZipFile(src, "r") as zip_ref:
                                # Extraction des fichiers dans le dossier temporaire
                                zip_ref.extractall(
                                    tmp_uncompress_dir,
                                    members=list_zip_allowed_members(zip_ref, tmp_uncompress_dir),
                                )
                        except zipfile.BadZipFile:
                            raise zipfile.BadZipFile(f"File '{relurl}' is not a zip file")

                elif mtype in MIMETYPES_TAR:
                    with upath.open(mode="rb") as src:
                        secure_extract_tar(src, tmp_uncompress_dir)
                else:
                    raise NotImplementedError(f"Cannot uncompress {'/'.join([str(part) for part in mtype])}")

            else:
                raise NotImplementedError(f"Cannot uncompress file with protocols {protocols}")

            # Count number of elements uncompressed ...
            #   if only one, move this file to local_copy_dir and return url to it
            #   else move whole temporary dir to local_copy_dir and rename it to filename without compression extension
            #   this is to support zarr zipped files that contains directly elements without subfolders.
            #   In this case, we don't want that all these files pollute local_copy_dir but we want to find all of them
            #   in zarr directory with name corresponding to zipped file. For example: file.zarr.zip -> file.zarr
            tmp_uncompress_dir_path = Path(tmp_uncompress_dir)
            extracted_files = list(tmp_uncompress_dir_path.iterdir())
            fn_without_ext = _filename_without_compression_extension(Path(path))
            if len(extracted_files) == 1 and extracted_files[0].name == fn_without_ext and extracted_files[0].is_dir():
                local_url = Path(local_copy_dir, fn_without_ext)
                local_url.mkdir(parents=True, exist_ok=True)
                for children in list(extracted_files[0].iterdir()):
                    dest = local_url / children.name
                    if overwrite is True and dest.exists():
                        dest.unlink()
                    _move_to_local_url(children, dest, overwrite=overwrite)
            elif len(extracted_files) == 1:
                extracted_file = extracted_files[0]
                local_url = Path(local_copy_dir, extracted_file.name)
                _move_to_local_url(extracted_file, local_url, overwrite=overwrite)
            else:
                local_url = Path(local_copy_dir, fn_without_ext)
                _move_to_local_url(tmp_uncompress_dir_path, local_url, overwrite=overwrite)
            logger.info(f"Extract {path.name} in {local_url}")
    else:
        # Handle the case where no uncompression is needed, just copy the file locally
        # no warn if we "cache" a "local file", because it may have sense if "local file" is in fact in mounting point
        local_url = Path(local_copy_dir, Path(path).name)
        if "file" in protocols:
            _copy_to_local_url(path.as_posix(), local_url, overwrite=overwrite)
        elif "s3" in protocols:
            fs, relurl = _get_fsspec_filesystem_from_url_and_credentials(url, **kwargs)
            if fs.isdir(relurl):
                fs.get(str(relurl) + "/", local_url, recursive=True)
            else:
                fs.get(str(relurl), local_url, recursive=True)

        logger.info(f"Create a copy of {path.name} in {local_url}")
    fixed_local_url = fix_url(local_url.as_posix())

    cache_id = f"{url};uncompress={need_uncompress}"
    cache_mapping[cache_id] = {
        "local_url": local_url.name,
    }
    with open(cache_mapping_path, "w") as cache_fp:
        json.dump(cache_mapping, cache_fp, indent=2)

    # path is now local, no need of credentials
    credentials = None
    fs, relurl = _get_fsspec_filesystem_from_url_and_credentials(fixed_local_url, credentials=credentials)
    upath = PathFsspec(relurl, fs=fs, original_url=original_url)

    return fixed_local_url, upath, credentials, need_local_copy


def is_local_copy_or_uncompression_required(
    url: str,
    mtype: tuple[str | None, str | None] | None = None,
    **kwargs: Any,
) -> tuple[bool, bool]:
    if mtype is None:
        mtype = mimetypes.guess_type(url)
    # Determine if the file needs uncompressing (based on mime type or uncompress flag)
    need_uncompress = mtype in MIMETYPES_COMPRESSED
    need_uncompress = need_uncompress and kwargs.get("uncompress", False)
    # Determine if a local copy of the file is required (for uncompression or caching)
    need_local_copy = need_uncompress or kwargs.get("cache", False)
    return need_local_copy, need_uncompress


def autofix_cache_and_compression_args(url: str, upath: PathFsspec, kwargs: Any) -> None:

    cache_required_for_s3 = False
    from sentineltoolbox.models.filename_generator import detect_filename_pattern

    filename_pattern = detect_filename_pattern(url)
    if filename_pattern in ("adf/s2-legacy",):
        kwargs["uncompress"] = True
        cache_required_for_s3 = True

    engine = detect_sentineltoolbox_engine(url)
    if engine in ("sentinel-2",):
        kwargs["uncompress"] = True
    if engine == "sentinel-2":
        cache_required_for_s3 = True
    if url.endswith(".tar.gz") or url.endswith(".tgz"):
        kwargs["uncompress"] = True

    if upath is not None and "s3" in upath.fs.protocol and cache_required_for_s3:
        kwargs["cache"] = True


def get_url_and_credentials(
    path_or_pattern: PathOrPattern,
    **kwargs: Any,
) -> tuple[str, PathFsspec, Credentials | None]:
    """
    Function that cleans url and extract credentials (if necessary) for you.

    :param path_or_pattern:
    :param credentials:
    :param kwargs:
      * local_copy_dir
      * uncompress
      * cache
      * overwrite
    :return:
    """
    if isinstance(path_or_pattern, (str, Path, Traversable)):
        url = fix_url(str(path_or_pattern))
        kwargs["credentials"] = fix_credentials(url, **kwargs)
        try:
            url, upath, credentials = _resolve_pattern(path_or_pattern, **kwargs)
        except NotImplementedError:
            url = str(path_or_pattern)
            upath = get_universal_path(url, **kwargs)

        if kwargs.get("autofix_args", False):
            autofix_cache_and_compression_args(url, upath, kwargs)

        url, upath, credentials, _ = uncompress_or_cache_data_if_required(url, universal_path=upath, **kwargs)
        return url, upath, credentials

    elif is_eopf_adf(path_or_pattern) or is_any_path(path_or_pattern):
        url, credentials = _get_url_and_credentials_from_eopf_inputs(path_or_pattern, **kwargs)
        kwargs["credentials"] = credentials
        # recall get_url_and_credentials to resolve pattern
        return get_url_and_credentials(url, **kwargs)
    elif isinstance(path_or_pattern, PathFsspec):
        if path_or_pattern.options and kwargs.get("credentials") is None:
            credentials = S3BucketCredentials.from_kwargs(**path_or_pattern.options)
            kwargs["credentials"] = credentials
        return get_url_and_credentials(path_or_pattern.url, **kwargs)
    else:
        raise NotImplementedError(f"path {path_or_pattern} of type {type(path_or_pattern)} is not supported yet")
