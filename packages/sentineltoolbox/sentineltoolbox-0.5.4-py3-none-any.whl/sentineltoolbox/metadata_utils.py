from typing import Any

from sentineltoolbox._utils import _get_attr_dict
from sentineltoolbox.attributes import STAC_PRODUCT_TYPE
from sentineltoolbox.models.filename_generator import extract_ptype
from sentineltoolbox.resources.data import DATAFILE_METADATA
from sentineltoolbox.typedefs import T_Attributes, T_ContainerWithAttributes


def guess_product_type(obj: T_ContainerWithAttributes | T_Attributes, **kwargs: Any) -> str:
    """
    Attempt to determine the product type for a given object.

    This function tries to extract the product type from the provided object using these strategies in this order:
    1. [user] If a 'product_type' keyword argument is provided, it is used directly
    2. [filename] attempts to extract the product type from the filename.
        filename is available only if object was open with stb.open_datatree function
    3. [metadata] attempts to extract the product type from the metadata
        (generally in stac_discovery/properties/product:type)

    You can change order and choose strategies to use thanks to metadata_extractors kwarg.
    For example:
      - metadata_extractors=["user", "metadata"]
      - metadata_extractors=["filename"]

    Parameters
    ----------
    obj : T_ContainerWithAttributes | T_Attributes
        The object from which to guess the product type. Must support attribute access or dictionary-like access.
    **kwargs : Any
        Optional keyword arguments. If 'product_type' is provided, it will be used as the product type.

    Returns
    -------
    str
        The guessed product type. Returns an empty string if the product type cannot be determined.
    """

    extractors = kwargs.get("metadata_extractors", ["user", "filename", "metadata"])
    ptype = ""
    attrs = _get_attr_dict(obj)
    for extractor in extractors:
        if extractor == "user":
            ptype = kwargs.get("product_type", "")
        elif extractor == "filename":
            try:
                info = obj.reader_info  # type: ignore
            except AttributeError:
                info = attrs

            semantic = extract_ptype(info.get("filename", info.get("name", "")), error="ignore")
            ptype = DATAFILE_METADATA.get_metadata(semantic, STAC_PRODUCT_TYPE, semantic)

        elif extractor == "metadata":
            ptype = attrs.get("stac_discovery", {}).get("properties", {}).get(STAC_PRODUCT_TYPE, "")
        if ptype:
            return ptype

    return ptype
