from typing import Any

from xarray import DataTree

from sentineltoolbox.readers.open_datatree import open_datatree


def convert_safe_to_datatree(
    url: Any,
    *,
    product_type: str,
    attrs: dict[str, Any],
    name: str | None = None,
    **kwargs: Any,
) -> DataTree:
    """
    Convert a SAFE format resource into a DataTree structure.

    This function processes a given resource (e.g., Sentinel satellite data) and converts
    it into a `DataTree` structure with specified attributes and metadata.

    Parameters
    ----------
    url : Any
        The input resource to process, such as a file path, URL, or compatible object.
    product_type : str
        The type of product (e.g., "S03OLCERR") to associate with the DataTree.
    attrs : dict corresponding to global attrs (metadata)
    name : str or None, optional
        An optional name to assign to the DataTree. If None (default), no name is assigned.
    **kwargs : Any
        Additional keyword arguments passed to `open_datatree`. For example:
        - `metadata_extractors` (list of str): A list of metadata extractors to use. Possible extractors are:
          - "sentineltoolbox": metadata extracted from safe thanks to sentineltoolbox
          - "user": user inputs attributes passed by user: convert_sentinel_legacy_data(attrs={...})
          - "fix": apply sentineltoolbox fix.
            For example, platform "Sentinel-3A" is converted to lower case "sentinel-3a"
          Defaults `["sentineltoolbox", "user", "fix"]`

    Returns
    -------
    DataTree
        A structured DataTree representation of the input data.

    Notes
    -----
    - This function ensures attributes and metadata are passed correctly, with a default
      set of metadata extractors if none are provided.
    - It can process different kinds of resources as long as they are compatible with
      `open_datatree`.
    """
    kwargs["attrs"] = attrs
    kwargs["output_product_type"] = product_type
    kwargs["metadata_extractors"] = kwargs.get("metadata_extractors", ["sentineltoolbox", "user", "fix"])
    metadata_only = kwargs.get("metadata_only", False)

    if metadata_only:
        xdt = DataTree()
    else:
        xdt = open_datatree(url, **kwargs)
    if name is not None:
        xdt.name = name

    return xdt
