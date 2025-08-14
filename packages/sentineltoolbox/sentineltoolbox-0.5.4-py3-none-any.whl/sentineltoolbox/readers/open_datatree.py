"""
No public API here.
Use root package to import public function and classes
"""

__all__: list[str] = []

import logging
from pathlib import Path
from typing import Any, Generator, Hashable, Union

import xarray as xr
import zarr
import zarr.errors
from xarray import DataTree
from xarray.core.treenode import NodePath
from zarr import Group

from sentineltoolbox.attributes import AttributeHandler, recursive_update
from sentineltoolbox.conversion.eopf_extraction import extract_metatadata_with_eopf
from sentineltoolbox.converters import convert_dict_to_datatree
from sentineltoolbox.filesystem_utils import (
    fix_kwargs_xarray_engine,
    get_url_and_credentials,
)
from sentineltoolbox.models.filename_generator import (
    detect_filename_pattern,
    filename_generator,
)
from sentineltoolbox.models.upath import PathFsspec
from sentineltoolbox.readers import _utils
from sentineltoolbox.readers._utils import (
    _cleaned_kwargs,
    fix_kwargs_for_lazy_loading,
    is_eopf_adf_loaded,
)
from sentineltoolbox.typedefs import (
    DEFAULT_COMPRESSOR,
    Credentials,
    L_DataFileNamePattern,
    PathMatchingCriteria,
    PathOrPattern,
    is_json,
)

logger = logging.getLogger("sentineltoolbox")


def _iter_zarr_groups(root: Group, parent: NodePath = NodePath("/")) -> Generator[str, None, None]:
    for path, group in root.groups():
        gpath = parent / path
        yield str(gpath)
        yield from _iter_zarr_groups(group, parent=gpath)


def open_eop_datatree(
    filename_or_obj: Union[str, Path],
    **kwargs: Any,
) -> DataTree:
    """Open and decode a EOPF-like Zarr product

    Parameters
    ----------
    filename_or_obj: str, Path
        Path to directory in file system or name of zip file.
        It supports passing URLs directly to fsspec and having it create the "mapping" instance automatically.
        This means, that for all of the backend storage implementations supported by fsspec, you can skip importing and
        configuring the storage explicitly.

    kwargs: dict

    Returns
    -------
        DataTree
    """

    if "chunks" not in kwargs:
        kwargs["chunks"] = {}

    paths: list[str] = []
    if "groups" in kwargs:
        groups = kwargs.pop("groups")
        if isinstance(groups, (list, tuple)):
            paths.extend(groups)
        elif groups is None:
            pass
        else:
            logger.warning(
                f"open_datatree(..., {groups=!r}): groups is not supported, please use list of str. "
                "groups has been ignored.",
            )
            groups = None
    else:
        groups = None

    if "group" in kwargs:
        paths.append(kwargs.pop("group"))

    if not paths and groups is None:
        # user hasn't specified paths explicitly, fill paths with all children.
        # if user has specified groups=[], do what is expected: load only root
        if "backend_kwargs" in kwargs:
            storage_options = kwargs["backend_kwargs"]
            zds = zarr.open_group(filename_or_obj, mode="r", **storage_options)
        else:
            zds = zarr.open_group(filename_or_obj, mode="r")

        for path in _iter_zarr_groups(zds):
            paths.append(path)

    tree_root = DataTree.from_dict({"/": xr.open_dataset(filename_or_obj, **kwargs)})

    for path in paths:
        try:
            subgroup_ds = xr.open_dataset(filename_or_obj, group=path, **kwargs)
        except zarr.errors.PathNotFoundError:
            subgroup_ds = xr.Dataset()

        # TODO refactor to use __setitem__ once creation of new nodes by assigning Dataset works again
        node_name = NodePath(path).name
        new_node: DataTree = DataTree(name=node_name, dataset=subgroup_ds)
        tree_root._set_item(
            path,
            new_node,
            allow_overwrite=False,
            new_nodes_along_path=True,
        )
    return tree_root


def convert_sentinel_legacy_data(
    upath: PathFsspec,
    product_type_pattern: L_DataFileNamePattern | None = None,
    **kwargs: Any,
) -> DataTree:
    """
    "product/s3-legacy",
    "product/s3-legacy-composite",
    "product/s2-legacy",  # S2A_MSIL1C_20231001T094031_N0509_R036_T33RUJ_20231002T065101
    "adf/s3-legacy",
    "adf/s2-legacy",  # S2__OPER_AUX_CAMSAN_ADG__20220330T000000_V20220330T000000_20220331T120000
    """
    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))

    url = upath.url

    credentials = kwargs.get("credentials")
    if credentials is not None:
        kwargs["backend_kwargs"] = credentials.to_kwargs(url=url, target="zarr.open_consolidated")
        kwargs["filename_or_obj"] = kwargs["backend_kwargs"].pop("store")
    else:
        kwargs["filename_or_obj"] = url

    product_type = kwargs.get("output_product_type", "")
    product_type_pattern_str = str(product_type_pattern)

    from sentineltoolbox.resources.data import PRODUCT_TREE

    is_s3_product = product_type_pattern_str.startswith("product/s3-legacy") or product_type in PRODUCT_TREE.s3
    is_s2_l1a_l1b_product = product_type_pattern_str.startswith("product/s2-legacy") or product_type in (
        "S02MSIL1A",
        "S02MSIL1B",
    )
    is_s2_l1c_l2a_product = product_type_pattern_str.startswith("product/s2-legacy") or product_type in (
        "S02MSIL1C",
        "S02MSIL2A",
    )

    if is_s3_product:
        from sentineltoolbox.conversion.sentinel3 import open_safe_datatree
        from sentineltoolbox.conversion.utils import use_custom_mapping

        simplified_mapping = use_custom_mapping(url)
        filename_or_obj = kwargs.pop("filename_or_obj")
        xdt = open_safe_datatree(filename_or_obj, simplified_mapping=simplified_mapping, universal_path=upath, **kwargs)
    elif is_s2_l1a_l1b_product or is_s2_l1c_l2a_product:
        if product_type:
            level = product_type[6:]
        else:
            fgen, data = filename_generator(upath.name)
            level = fgen.semantic[3:]
        if level in ("L1C", "L2A"):
            from sentineltoolbox.conversion.convert_s02msi_tile_safe import (
                open_s2msi_tile_safe_product,
            )

            xdt = open_s2msi_tile_safe_product(Path(upath.path), product_level=None, **kwargs)
        elif level in ("L1A", "L1B"):
            from sentineltoolbox.conversion.convert_s02msi_l1ab_safe import (
                S02MSIL1ABProductConversion,
            )

            convertor_l1a = S02MSIL1ABProductConversion(
                safe_product_path=Path(upath.path),
                product_level=level,  # type: ignore
            )  # , output_product_type = "DataTree")
            xdt = convertor_l1a.convert_s2msi_l1_safe_product(**kwargs)
        else:
            raise NotImplementedError(f"{upath.name}: {level=} is not supported")

    elif product_type_pattern == "adf/s3-legacy":
        from sentineltoolbox.conversion.converter_s03_adf_legacy import convert_adf

        converted_data = convert_adf(upath)
        if isinstance(converted_data, DataTree):
            xdt = converted_data
        else:
            xdt = convert_dict_to_datatree(converted_data)
    else:
        raise NotImplementedError(f"{upath.name}: product of type {product_type_pattern!r} is not supported")

    # Set information required for serialization
    for tree in xdt.subtree:
        for var in tree.variables:
            tree[var].encoding["compressor"] = DEFAULT_COMPRESSOR

    xdt.attrs = extract_metadata(xdt, upath, **kwargs)

    logger.info(f"open and convert {product_type_pattern} file {url!r} to datatree")
    return xdt


def extract_metadata(xdt: DataTree, upath: PathFsspec, **kwargs: Any) -> dict[Hashable, Any]:
    """
    Update attributes. Depending on strategy, attributes can come from ...
     - ["user"] user inputs attributes passed by user: convert_sentinel_legacy_data(attrs={...})
     - ["eopf"] metadata extracted from safe thanks to eopf
     - ["sentineltoolbox"] metadata extracted from safe thanks to sentineltoolbox
     - ["fix"]: apply sentineltoolbox fix
    """
    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))
    metadata_extractors = kwargs.get("metadata_extractors", ["sentineltoolbox", "eopf", "user", "fix"])

    stb_attrs = xdt.attrs
    final_attrs: dict[Hashable, Any] = {}
    for extractor in metadata_extractors:
        if extractor == "user":
            user_attrs = kwargs.get("attrs", {})
            recursive_update(final_attrs, user_attrs)
            logger.info("Update metadata with 'user' metadata")
        elif extractor == "eopf":
            eopf_attrs = extract_metatadata_with_eopf(upath)
            recursive_update(final_attrs, eopf_attrs)
            logger.info("Update metadata with safe data extracted from safe thanks to eopf mappings")
        elif extractor == "sentineltoolbox":
            recursive_update(final_attrs, stb_attrs)
            logger.info("Update metadata with safe data extracted from safe thanks to sentineltoolbox converters")
        elif extractor == "fix":
            attrs = AttributeHandler(final_attrs)
            attrs.fix()
            logger.info("Fix metadata using sentineltoolbox 'hotfix' mechanism")
        else:
            logger.warning(f"Unknown metadata extractor {extractor}")
    return final_attrs


def open_datatree(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> DataTree:
    """
    Function to open tree data (zarr sentinel product) from bucket or local path and open it as :obj:`DataTree`

    .. note::

        Data are lazy loaded. To fully load data in memory, prefer :obj:`~sentineltoolbox.api.load_datatree`


    Optional arguments credentials, match_criteria, ... must be specified by key.

    Parameters
    ----------

    Parameters common to all open_* and load_*:
        see :obj:`sentineltoolbox.typedefs` for details on
            - path_or_pattern
            - credentials
            - match_criteria

    Parameters specific to open_datatree:
      - groups: list of path (relative to zarr root) to open. If not set, open all children.
        Note: root data and metadata are always loaded.

    """
    if isinstance(path_or_pattern, DataTree):
        return path_or_pattern
    elif is_eopf_adf_loaded(path_or_pattern) and isinstance(path_or_pattern.data_ptr, DataTree):
        return path_or_pattern.data_ptr

    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))

    # resolve url
    kwargs["autofix_args"] = True
    url, upath, credentials = get_url_and_credentials(
        path_or_pattern,
        credentials=credentials,
        match_criteria=match_criteria,
        **kwargs,
    )
    if kwargs.get("load", False) is False:
        fix_kwargs_for_lazy_loading(kwargs)

    # Tries to identify product type.
    product_type_pattern = detect_filename_pattern(upath.name)
    output_product_type = kwargs.get("output_product_type", "")
    # it is a legacy product or ADF, convert-it on the fly thanks to sentineltoolbox.conversion
    if (
        product_type_pattern
        in (
            "product/s3-legacy",
            "product/s3-legacy-composite",
            "product/s2-legacy",  # S2A_MSIL1C_20231001T094031_N0509_R036_T33RUJ_20231002T065101
            "adf/s3-legacy",
            "adf/s2-legacy",  # S2__OPER_AUX_CAMSAN_ADG__20220330T000000_V20220330T000000_20220331T120000
        )
        or output_product_type
    ):
        xdt = convert_sentinel_legacy_data(upath, product_type_pattern=product_type_pattern, **kwargs)
    # it is a JSON file, convert it to datatree
    elif is_json(url):
        logger.info(f"open and convert 'json' file {url!r} to datatree")
        xdt = convert_dict_to_datatree(_utils.load_json(upath))

    # it is a zarr file, open it normally
    else:
        if credentials is not None:
            kwargs["backend_kwargs"] = credentials.to_kwargs(url=url, target="zarr.open_consolidated")
            kwargs["filename_or_obj"] = kwargs["backend_kwargs"].pop("store")
        else:
            kwargs["filename_or_obj"] = url

        fix_kwargs_xarray_engine(url, kwargs)

        if not upath.exists():
            raise FileNotFoundError(url)
        if kwargs["engine"] == "zarr":
            logger.info(f"open and convert 'zarr' file {url!r} to datatree")
            xdt = open_eop_datatree(**_cleaned_kwargs(kwargs))
        else:
            # for local filesystem, prefer to pass path instead of url
            logger.info(f"open and convert {kwargs['engine']} file {url!r} to datatree")
            kwargs = _cleaned_kwargs(kwargs)
            if "file" in upath.fs.protocol:
                kwargs["filename_or_obj"] = upath.path
            elif credentials:
                kwargs["filename_or_obj"] = upath.open(mode="rb")
            if "backend_kwargs" in kwargs:
                del kwargs["backend_kwargs"]
            xdt = xr.open_datatree(**kwargs)
    xdt.reader_info = {"name": upath.name, "url": upath.url}
    return xdt


def load_datatree(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    fake_data: str | None = None,
    **kwargs: Any,
) -> DataTree:
    """
    Function to load tree data (zarr sentinel product) from bucket or local path and load it as :obj:`DataTree`

    .. warning::
        all data are loaded in memory. Use it only for small readers.

        To lazy load data, prefer :obj:`~sentineltoolbox.api.open_datatree`

    Optional arguments credentials, match_criteria, ... must be specified by key.

    Parameters
    ----------
    Parameters common to all open_* and load_*:
        see :obj:`sentineltoolbox.typedefs` for details on
            - path_or_pattern
            - credentials
            - match_criteria

    fake_data, optional
        if set, replace data with fake readers. Type of fake readers correspond to fake_data mode.
        Use this if you want to manipulate only metadata and attrs
    """
    kwargs["chunks"] = None
    return open_datatree(path_or_pattern, credentials=credentials, match_criteria=match_criteria, load=True, **kwargs)
