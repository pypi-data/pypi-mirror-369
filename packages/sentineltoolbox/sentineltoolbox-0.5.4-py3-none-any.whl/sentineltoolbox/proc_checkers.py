from typing import Any, MutableMapping

from sentineltoolbox.datatree_utils import DataTreeHandler
from sentineltoolbox.exceptions import (
    InputPlatformError,
    LoadingDataError,
    MissingAdfError,
)
from sentineltoolbox.models.filename_generator import extract_semantic
from sentineltoolbox.readers.open_metadata import load_metadata


def _to_canonical_type(ptype: str, is_adf: bool = False) -> str:
    """
    Converts a given ptype into a canonical ptype based on certain rules.

    This function uses the `to_dpr_ptype` function from the `DATAFILE_METADATA`
    to first attempt to map the given `ptype` to a canonical version. If no
    canonical version is found and the `is_adf` flag is True, it prepends
    "SXX_ADF_" to the semantic component of the `ptype`. Otherwise, it only
    extracts the semantic component of the `ptype`.

    Example where product:type is recognized and so constellation is known (S02, S03, ...)

    >>> _to_canonical_type("OLCEFR")
    'S03OLCEFR'
    >>> _to_canonical_type("OLINS", is_adf=True)
    'S03_ADF_OLINS'

    Example where product:type is not recognized. Constellation cannot be determined and is replaced by "SXX"
    >>> _to_canonical_type("ABCDEF")
    'SXXABCDEF'
    >>> _to_canonical_type("ABCDE", is_adf=True)
    'SXX_ADF_ABCDE'

    :param ptype: The ptype string that needs to be converted into its canonical form.
    :type ptype: str
    :param is_adf: Specifies whether the `ptype` is related to an ADF. Defaults to False.
    :type is_adf: bool
    :return: The canonical ptype derived from the input `ptype`.
    :rtype: str
    """
    from sentineltoolbox.resources.data import DATAFILE_METADATA

    canonical_ptype = DATAFILE_METADATA.to_dpr_ptype(ptype)
    if not canonical_ptype:
        if is_adf:
            canonical_ptype = "SXX_ADF_" + extract_semantic(ptype)
        else:
            canonical_ptype = "SXX" + extract_semantic(ptype)
    elif isinstance(canonical_ptype, list):
        canonical_ptype = canonical_ptype[0]
    return canonical_ptype


def check_processor_inputs(inputs: MutableMapping[str, Any], adfs: MutableMapping[str, Any], **kwargs: Any) -> None:
    """
    Check the validity and coherence of processor inputs and associated data files.

    This function verifies the coherence of the provided products and associated
    data files (ADFs) by ensuring consistency in the registered platform across
    all inputs. When a platform has already been determined, it checks whether
    additional inputs conform to the expected platform.

    The process also supports optional autofix behavior to correct found discrepancies, where applicable.

    :param inputs: A mapping containing products to check for platform coherence.
    :param adfs: A mapping of associated data files (ADFs) to validate.
    :param kwargs: Optional arguments including:
        - `autofix` (bool, default=False): apply autofix for products
        - `autofix_adfs` (bool, default=True): apply autofix for adfs.
            See DataTreeHandler.fix(), AttribHandler.fix()
        - `required_adfs` (List[str]): List of required ADFs for validation.
            See DataTreeHandler.fix(), AttribHandler.fix()
    """
    # extract platform from inputs and check coherence
    platform = None
    for alias, product in inputs.items():
        hdl = DataTreeHandler(product)
        if kwargs.get("autofix", False):
            hdl.fix()
        pl = hdl.get_stac_property("platform", default=None)
        # store first platform found
        if platform is None and pl:
            platform = pl
        # if a platform is already registered, compare current platform to it
        elif platform and pl and pl != platform:
            raise InputPlatformError(f"Multiple platforms found: {pl}, {platform}")

    # check adfs and check platform coherence with inputs
    check_adfs(adfs, required=kwargs.get("required_adfs", []), required_platform=platform)


def check_adfs(adfs: MutableMapping[str, Any], *, required: list[str] | None = None, **kwargs: Any) -> None:
    """
    Checks the presence and validity of Auxiliary Data Files (ADFs) and ensures they meet specified requirements.

    This function evaluates ADFs provided in the input dictionary against the specified required types and other
    optional checks, such as platforms. It ensures required ADFs are present, validates their metadata,
    and handles potential issues specific to the ADF structure.

    Additionally, it autofix ADFS using :obj:`~sentineltoolbox.module.AttributeHandler.fix` feature when possible.

    :param adfs: A mapping of ADF aliases to their respective metadata files. This contains the core input
                 data for validation and type inference.
    :param required: A list of required ADF types that must be present in the input dataset. Defaults
                     to an empty list if not provided. Ex: ["S03_ADF_OLINS", "S03_ADF_OLCEFR"]
    :param kwargs: Additional optional parameters for more specific validation logic. Notable options
                   include:
                     - "autofix": Whether to use autofix features during metadata evaluation (default=True),
                       linked with the :obj:`~sentineltoolbox.module.AttributeHandler.fix`.
                     - "required_platform": Specifies a required platform name to be validated against
                       the platforms found in the input ADF metadata.

    :raises MissingAdfError: Raised when a required ADF type is missing from the input data.
    :raises InputPlatformError: Raised when platform validation fails either due to a specific required
                                 platform not matching, or multiple platforms being found in the ADF data.
    """
    if not adfs:
        return

    if required is None:
        required = []

    input_types = {}
    platforms = {}
    for alias, adf in adfs.items():
        try:
            xdt = load_metadata(adf).container()
        except (LoadingDataError, FileNotFoundError):
            continue
        except (NotImplementedError, NotADirectoryError, KeyError):
            product_type = _to_canonical_type(alias, is_adf=True)
        else:
            attrs = DataTreeHandler(xdt)
            if kwargs.get("autofix", True):
                attrs.fix()
            product_type = attrs.get_stac_property("product:type", default=alias)
            platform = attrs.get_stac_property("platform", default=None)
            if platform and platform[-1] != "x":
                platforms[alias] = platform

        input_types[alias] = product_type

    ptypes = input_types.values()
    for adf_name in required:
        dpr_name = _to_canonical_type(adf_name, is_adf=True)
        if not (adf_name in ptypes or dpr_name in ptypes):
            str_inputs = "\n  - ".join([f"{k!r}: {v!r}" for k, v in input_types.items()])
            long_name = _to_canonical_type(adf_name, is_adf=True)
            raise MissingAdfError(f"ADF {long_name!r} is required but not found in inputs: \n  - {str_inputs}")

    # check platforms
    required_platform = kwargs.get("required_platform")
    if required_platform and required_platform not in platforms.values():
        raise InputPlatformError(f"required platform not found: {required_platform}")

    # Group platforms by mission and check for conflicts
    mission_platforms: dict[str, set[str]] = {}
    for platform in platforms.values():
        mission, variant = _normalize_platform(platform)
        if mission not in mission_platforms:
            mission_platforms[mission] = set()
        mission_platforms[mission].add(variant)

    mission_platforms.pop("sentinel-0", None)
    # Check for conflicts between different Sentinels missions
    if len(mission_platforms) > 1:
        raise InputPlatformError(f"Multiple satellite constellations found: {mission_platforms}")

    # Check for conflicts between specific variants
    for mission, variants in mission_platforms.items():
        specific_variants = variants - {"_"}
        if len(specific_variants) > 1:
            raise InputPlatformError(f"Multiple platforms found ({specific_variants}) for {mission}")


def _normalize_platform(platform: str) -> tuple[str, str]:
    """
    Normalize platform name and return mission and variant.

    :param platform: Platform name (e.g. 'sentinel-2a', 'sentinel-3_')
    :return: Tuple of (mission, variant) where mission is 'sentinel-2' or 'sentinel-3'
             and variant is 'a', 'b', or '_'
    """
    if not platform:
        return "", ""

    # Extract mission and variant
    parts = platform.split("-")
    if len(parts) != 2:
        return platform, ""

    mission = f"{parts[0]}-{parts[1][0]}"  # e.g. 'sentinel-2' or 'sentinel-3'
    variant = parts[1][1:] if len(parts[1]) > 1 else "_"  # 'a', 'b', or '_'

    return mission, variant
