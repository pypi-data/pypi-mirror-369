import gc
import logging
from pathlib import Path
from typing import Any, Optional

import zarr
from xarray import DataTree

from sentineltoolbox.api import open_datatree
from sentineltoolbox.models.upath import PathFsspec

logger = logging.getLogger("xarray_eop")


def product_converter(
    sample_path: str | Path | PathFsspec,
    output_path: str | Path,
    zip: Optional[bool] = False,
    metadata: dict[Any, Any] = None,
    **kwargs,
) -> DataTree:
    """Convert Sentinel-3 SAFE product to the EOP zarr structure.
    See the `Product Structure and Format Definition
    <https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/PSFDjan2024.html>`__

    Parameters
    ----------
    sample_path
        input Sentinel-3 SAFE product path
    output_path
        output Zarr product path
    zip, optional
        output the zipped product in addition (zero compression), by default True

    Returns
    -------
        Converted Zarr product
    """
    if metadata is None:
        metadata = {}

    output_path = Path(output_path)
    prod = open_datatree(sample_path, **kwargs)
    prod.attrs.update(metadata)
    prod.to_zarr(store=output_path, consolidated=True)
    gc.collect()
    # zarr.consolidate_metadata(output_path)

    # Check to open with datatree and zip
    # print("Checking product")
    # decode_times = True
    # if typ_eop in ["S03SYNVGK", "S03SYNVG1", "S03SYNV10"]:
    #     decode_times = False
    # dt: DataTree = open_datatree(output_path, decode_times=decode_times)
    if zip:
        logger.info("Zipping product")
        with zarr.ZipStore(str(output_path) + ".zip") as store:
            prod.to_zarr(store)

    return prod
