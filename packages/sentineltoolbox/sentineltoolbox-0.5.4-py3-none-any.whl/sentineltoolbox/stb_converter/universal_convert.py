import gc
import hashlib
import json
import logging
from copy import copy
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, Generator

from xarray import DataTree

from sentineltoolbox._utils import split_protocol
from sentineltoolbox.conversion.convert import product_converter
from sentineltoolbox.conversion.converter_s03_adf_legacy import (
    CONVERT_ADFS,
    CONVERT_AND_MERGE_ADFS,
    NumpyEncoder,
    convert_adf,
)
from sentineltoolbox.exceptions import (
    DataSemanticConversionError,
    MultipleDataSemanticConversionError,
)
from sentineltoolbox.filesystem_utils import (
    autofix_cache_and_compression_args,
    get_universal_path,
    is_local_copy_or_uncompression_required,
)
from sentineltoolbox.models.filename_generator import (
    convert_semantics,
    filename_generator,
)
from sentineltoolbox.models.upath import PathFsspec
from sentineltoolbox.resources.data import DATAFILE_METADATA
from sentineltoolbox.typedefs import fix_datetime
from sentineltoolbox.writers.zarr import write_zarr

logger = logging.getLogger("stb_convert_products")
custom_converters = {}
custom_converters.update(CONVERT_ADFS)
LEGACY_FILES_PATTERNS = [
    "*.SEN3",
    "*.SAFE",
    "*.SEN3.zip",
    "*.SAFE.zip",
    # "*.SEN3.tgz", "*.SAFE.tgz"
]


def convert_product_with_eopf_mapping(input_path: PathFsspec, output_path: str) -> None:
    from eopf import EOSafeStore, EOZarrStore, OpeningMode

    p = PurePosixPath(output_path)
    zarr_store = EOZarrStore(url=p.parent.as_posix()).open(mode=OpeningMode.CREATE_OVERWRITE)
    store = EOSafeStore(input_path.url, storage_options=input_path.fs.storage_options).open()
    eoproduct = store.load()
    zarr_store[p.name] = eoproduct


def iter_legacy_products(
    inputs: list[str | Path],
    input_dir: PathFsspec | None = None,
    **kwargs: Any,
) -> Generator[PathFsspec, None, None]:
    recursive = kwargs.get("recursive", False)
    if inputs:
        for path in inputs:
            upath = get_universal_path(path, autofix_args=True)
            if upath.exists():
                yield upath
            else:
                logger.critical(f"{upath.url} doesn't exist")
    elif input_dir is not None:
        if recursive:
            for pattern in LEGACY_FILES_PATTERNS:
                for inp in input_dir.rglob(pattern):
                    yield inp
        else:
            for pattern in LEGACY_FILES_PATTERNS:
                for inp in input_dir.glob(pattern):
                    yield inp
    else:
        pass


# def _pretty_relpath(upath_input_product: PathFsspec, rel_input_path: str) -> str:
#    relpath = rel_input_path + "/" if rel_input_path else ""
#    return f"{relpath}{upath_input_product.name}"


def pretty_path(upath: PathFsspec, refpath: Path | str | None = None) -> str:
    url = upath.original_url
    if url.startswith("file://"):
        protocols, p = split_protocol(url)
        if refpath is None:
            refpath = Path(".").absolute()
        else:
            refpath = Path(refpath)
        try:
            relpath = p.relative_to(refpath).as_posix()
        except ValueError:
            relpath = p.as_posix()
        relpath = str(relpath)
    else:
        relpath = url
    if upath.url != url:
        return f"{relpath} (local uncompressed copy used)"
    else:
        return relpath


def convert_sentinel_products(
    explicit_user_inputs: list[str | Path],
    *,
    input_dir: str | None = None,
    output_dir: str | None = None,
    dry_run: bool = False,
    force_hash: int | None = None,
    force_creation_date: datetime | str | None = None,
    user_map: dict[str, str] | None = None,
    recursive: bool = False,
    zip: bool = False,
    converter_args: dict[str, Any] | None = None,
    **kwargs: Any,
) -> None:
    """
    Converts Original Sentinel products (e.g., SEN3) to standardized output formats,

    Parameters
    ----------
    explicit_user_inputs : list of str or Path
        A list of explicit user-provided Sentinel product file paths or names to be converted.

    input_dir : str or None, optional
        Directory containing Sentinel products to be converted.
        If not specified, `explicit_user_inputs` will be used instead.
        Default is None.

    output_dir : str or None, optional
        Directory to save the converted products. Defaults to `None` (current directory).

    dry_run : bool, optional
        If `True`, only logs the conversion actions without performing any changes. Defaults to `False`.

    force_hash : int or None, optional
        Hash value to use for generating output filenames. If `None`,
        the hash is calculated automatically based on the product's
        creation date. Defaults to `None`.

    force_creation_date : datetime or None, optional
        A specific datetime to be used as the product's creation date in the output filenames.
        If `None`, the current datetime is used.
        Defaults to `None`.

    user_map : dict of str to str, optional
        A dictionary mapping legacy product types to their new format.
        If not set, guess product type thanks to sentineltoolbox internal database
        Defaults to `None` (empty dictionary).

    recursive : bool, optional
        If `True`, the `input_dir` will be searched recursively for Sentinel products. Defaults to `False`.

    zip : bool, optional
        If `True`, the output products will be compressed in a zipped format (useful for S3). Defaults to `False`.

    converter_args : dict of str to Any, optional
        Additional arguments for conversion, such as specific parameters for product types.
        Defaults to `None` (empty dictionary).

    **kwargs : Any
        Additional keyword arguments passed to utility functions for path resolution and caching.

    Returns
    -------
    None
        This function does not return a value; it performs file conversion and writes output to disk or other storage.

    Notes
    -----
    This function processes Sentinel products and ADFS in different ways:

    1. **"1 to 1" conversion**: A single input file is converted to a corresponding output file.
    2. **"n to 1" conversion**: Multiple input files are merged into a single output file, typically ADFS products.
    3. **"1 to n" conversion**: A single input file generate multiple output files
    """
    if converter_args is None:
        converter_args = {}

    # if user pass explicit inputs (for example xxx1.SEN3 xxx2.SEN3) force input_dir to None
    if explicit_user_inputs:
        input_dir = None

    # if user pass input directory (for example "LEGACY_PRODUCTS/")
    # generate universal path
    if input_dir is not None:
        upath_input_dir = get_universal_path(input_dir, autofix_args=True, **kwargs)
    else:
        upath_input_dir = None

    # if input_dir, iter on it to find all legacy products
    # if explicit inputs, convert it to universal paths
    _upath_inputs = iter_legacy_products(explicit_user_inputs, upath_input_dir, recursive=recursive)

    if dry_run:
        logger.info("Conversion PLANNED")

    if user_map is None:
        user_map = {}

    if isinstance(force_creation_date, str):
        force_creation_date = fix_datetime(force_creation_date)

    # Check and fix output dir
    if output_dir and output_dir.startswith("s3://"):
        raise NotImplementedError("Cannot convert directly to s3 bucket. Please use local output dir")

    if output_dir is None:
        output_dir_upath = get_universal_path("")
    else:
        output_dir_upath = get_universal_path(output_dir)

    # Generate a dict with all output products that will be generated.
    # key: tuple(output path, relpath).
    #   - output path: the output path (universal path) to generate
    #   - relpath: the path relative to input dir (if --input-dir is used, else "")
    # value: [list of universal_input_path]
    # it is a list because for some ADFS we need to merge multiple ADFS in one
    out_in_dict: dict[tuple[PathFsspec, str], list[PathFsspec]] = {}
    for upath_input in _upath_inputs:
        input_name = upath_input.name
        try:
            logger.debug(f"read {upath_input}")
            fgen, fgen_data = filename_generator(input_name, semantic_mapping=user_map)
            if fgen_data["fmt"].startswith("adf"):
                output_names = [fgen.to_string(creation_date=force_creation_date)]
            elif fgen_data["fmt"].startswith("product"):
                creation_date = fgen_data.get("creation_date", "01012000T000000")
                if force_hash is None:
                    hash = int(hashlib.sha256(creation_date.encode("ASCII")).hexdigest()[:3], 16)  # nosec
                else:
                    hash = force_hash
                output_names = [fgen.to_string(hash=hash)]
            else:
                raise NotImplementedError(f"Product {input_name} of type {fgen_data['fmt']} is not supported")

        except MultipleDataSemanticConversionError:
            fgen, fgen_data = filename_generator(input_name, semantic="X")
            output_names = []
            for semantic in convert_semantics(fgen_data["fmt"], fgen_data["semantic"]):
                fgen, fgen_data = filename_generator(input_name, semantic=semantic)
                output_names.append(fgen.to_string(semantic=semantic))

        except DataSemanticConversionError:
            logger.critical(
                f"Unknown DPR type for {input_name[:15]} Please specify product_type mapping "
                "with -m/--map OLD NEW. For example: -m OL_0_XYZ___ OLCXYZ",
            )
            continue

        except NotImplementedError:
            logger.critical(f"Semantic {input_name!r} is not recognized")
            continue

        # Generate path relative to input dir. Idea is to keep tree inside input_dir and avoid to have all converted
        # product in same directory
        # For example if user pass input_dir == DATA/PRODUCTS and a product DATA/PRODUCTS/OLCI/xxxx.SEN3 is found
        # rel_input_path will be "OLCI/xxxx.SEN3".
        if upath_input_dir is not None:
            rel_input_path = upath_input.url.replace(upath_input_dir.url + "/", "")
        else:
            rel_input_path = input_name

        # Keep only path to directory containing legacy product
        # "OLCI/xxxx.SEN3" -> "OLCI"
        # "xxxx.SEN3" -> ""
        relparent = "/".join(rel_input_path.split("/")[:-1])

        # Generate output path, keeping relative tree
        upath_local_output_dir = output_dir_upath / relparent
        for output_name in output_names:
            upath_output = upath_local_output_dir / output_name
            lst = out_in_dict.setdefault((upath_output, relparent), [])
            if upath_input not in lst:
                lst.append(upath_input)

        del input_name, relparent, upath_local_output_dir
    del _upath_inputs

    for upath_output_and_parent, upath_inputs in out_in_dict.items():
        upath_output, relparent = upath_output_and_parent

        # Check if path need to be downloaded or uncompress. If true, do it now and replace input path by
        # local uncompressed copy. Use it for all converters that cannot support compressed or bucket data.
        if not dry_run:
            upath_inputs = extract_and_cache_inputs_if_necessary(upath_inputs)

        if len(upath_inputs) == 1:
            # Convert "1 to 1" (CONVERT)
            upath_input = upath_inputs[0]

            _convert_1_to_1(
                upath_input,
                upath_output,
                user_map,
                converter_args,
                dry_run,
                relparent,
            )
        else:
            # Convert "n to 1" (MERGE)
            semantic = filename_generator(upath_output.name)[0].semantic
            if semantic in DATAFILE_METADATA.from_merged_legacy:
                _convert_n_to_1(upath_inputs, upath_output, user_map, dry_run)
            else:
                # Here, output file names are identical because inputs differ only on creation_date
                # or information that is no more on DPR filenames.
                # to avoid to overwrite each time the same file, creation date has been changed
                now = datetime.now()
                for i, upath_input in enumerate(upath_inputs):
                    fgen, fdata = filename_generator(upath_output.name)
                    new_upath_output = copy(upath_output)
                    newname = fgen.to_string(creation_date=(now + timedelta(seconds=i)))
                    new_upath_output.path = upath_output.path.replace(upath_output.name, newname)
                    new_upath_output.original_url = upath_output.path
                    _convert_1_to_1(
                        upath_input,
                        new_upath_output,
                        user_map,
                        converter_args,
                        dry_run,
                        relparent,
                    )


def extract_and_cache_inputs_if_necessary(upath_inputs: list[PathFsspec]) -> list[PathFsspec]:
    final_inputs = []
    for i, upath_input in enumerate(upath_inputs):
        url = upath_input.url
        _kwargs: Any = {}
        autofix_cache_and_compression_args(url, upath_input, _kwargs)
        need_local_copy, need_compression = is_local_copy_or_uncompression_required(url, **_kwargs)
        if need_local_copy:
            final_inputs.append(get_universal_path(upath_input.url, **_kwargs))
        else:
            final_inputs.append(upath_input)
    return final_inputs


def _convert_n_to_1(
    upath_inputs: list[PathFsspec],
    upath_output: PathFsspec,
    user_map: dict[str, str] | None,
    dry_run: bool,
) -> None:
    # Convert "n to 1"
    if dry_run:
        logger.info("[dry-run] convert and merge (sentineltoolbox)")
        for upath_input in sorted(upath_inputs, key=lambda obj: obj.path):
            logger.info(f"[dry-run]  - {pretty_path(upath_input)}")
        logger.info(f"[dry-run]   ---> {pretty_path(upath_output)}")
    else:
        logger.info("[sentineltoolbox/adf] convert and merge")
        fgen, fgen_data = filename_generator(upath_output.name, semantic_mapping=user_map)
        input_path_str = ", ".join([p.name for p in upath_inputs])
        if fgen.semantic in CONVERT_AND_MERGE_ADFS:
            convert_func = CONVERT_AND_MERGE_ADFS[fgen.semantic]
            try:
                convert_func(
                    fgen.semantic,
                    [Path(input_path.path) for input_path in upath_inputs],
                    upath_output.path,
                )
            except NotImplementedError:
                logger.critical(f"[sentineltoolbox/adf] CANNOT convert {input_path_str} to {pretty_path(upath_output)}")
            else:
                for upath_input in sorted(upath_inputs, key=lambda obj: obj.path):
                    logger.info(f"  + {pretty_path(upath_input)}")
                logger.info(f"  ===> {pretty_path(upath_output)}")

        else:
            logger.critical(f"[sentineltoolbox/adf] CANNOT convert {input_path_str} to {pretty_path(upath_output)}")


def _convert_1_to_1(
    upath_input: PathFsspec,
    upath_output: PathFsspec,
    user_map: dict[str, str],
    converter_args: Any,
    dry_run: bool,
    relparent: str,
) -> None:
    fgen, fgen_data = filename_generator(upath_output.name)
    if dry_run:
        if fgen.semantic in custom_converters:
            logger.info("[dry-run] convert (sentineltoolbox/adf)")
            logger.info(f"[dry-run]   - {pretty_path(upath_input)}")
            logger.info(f"[dry-run]   ---> {pretty_path(upath_output)}")
        else:
            logger.info("[dry-run] convert (sentineltoolbox or cpm)")
            logger.info(f"[dry-run]   - {pretty_path(upath_input)}")
            logger.info(f"[dry-run]   ---> {pretty_path(upath_output)}")
    else:
        error_msg = f"CANNOT convert {pretty_path(upath_input)} to {pretty_path(upath_output)}."
        if not upath_output.parent.exists():
            upath_output.parent.mkdir(parents=True, exist_ok=True)

        if fgen_data["fmt"].startswith("adf"):
            if fgen.semantic in custom_converters:
                _convert_and_log_adf_using_custom_formatter(
                    upath_input,
                    upath_output,
                    user_map,
                    converter_args,
                    relparent,
                )
            else:
                logger.critical(error_msg + " No ADF converter.")
        else:
            try:
                _open_datatree_kwargs: dict[str, Any] = {}
                _open_datatree_kwargs.update(converter_args.get(fgen.semantic, {}))
                _open_datatree_kwargs.update({"autofix_args": True})
                product_converter(upath_input, upath_output.path, **_open_datatree_kwargs)
            except (KeyError, NotImplementedError):
                try:
                    convert_product_with_eopf_mapping(upath_input, upath_output.path)
                except ImportError:
                    logger.critical(error_msg + " Need to install eopf > 2.4")
                except:  # noqa: E722
                    logger.critical(error_msg + " Neither sentineltoolbox nor eopf converters")
                else:
                    logger.info(f"[eopf] convert {pretty_path(upath_input)} to {pretty_path(upath_output)}")
            else:
                logger.info(
                    f"[sentineltoolbox/product] convert {pretty_path(upath_input)} to {pretty_path(upath_output)}",
                )


def _convert_and_log_adf_using_custom_formatter(
    upath_input_product: PathFsspec,
    upath_output: PathFsspec,
    user_map: dict[str, str],
    converter_args: Any,
    rel_parent_str: str = "",
) -> None:
    fgen, fgen_data = filename_generator(upath_output.path)
    rel_out = f"{rel_parent_str}/{upath_output.name}"
    try:
        # TODO: support upath, then remove uncompress=True and cache=True
        data = convert_adf(
            upath_input_product,
            adf_type=fgen.semantic,
            semantic_mapping=user_map,
            **converter_args.get(fgen.semantic, {}),
        )
        _dump_datatree(data, upath_output)
    except (ValueError, NotImplementedError) as err:
        logger.critical(
            f"[sentineltoolbox/adf] ERROR during conversion of {upath_input_product.name!r} to {rel_out}",
        )
        logger.exception(err)
    else:
        logger.info(
            f"[sentineltoolbox/adf] convert {upath_input_product.name!r} to {rel_out}",
        )


def _dump_datatree(data: dict[Any, Any] | DataTree, upath_output: PathFsspec) -> None:
    if isinstance(data, DataTree):
        write_zarr(data, upath_output)
        del data
        gc.collect()
    elif isinstance(data, dict):
        upath_output.path = upath_output.path.replace(".zarr", ".json")
        with upath_output.open("w") as json_file:
            json.dump(data, json_file, indent=2, cls=NumpyEncoder)
    else:
        raise NotImplementedError(f"Cannot dump data of type {type(data)}")
