"""
No public API here.
Use root package to import public function and classes
"""

__all__: list[str] = []

import copy
import logging
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr
import zarr
from xarray import DataTree, Variable
from xarray.conventions import decode_cf_variable

from sentineltoolbox.attributes import AttributeHandler
from sentineltoolbox.converters import convert_to_datatree
from sentineltoolbox.filesystem_utils import (
    _get_fsspec_filesystem_from_url_and_credentials,
    get_url_and_credentials,
)
from sentineltoolbox.readers import _utils
from sentineltoolbox.readers._utils import (
    decode_storage_attributes,
    fix_kwargs_for_lazy_loading,
    is_eopf_adf_loaded,
)
from sentineltoolbox.typedefs import (
    Credentials,
    PathMatchingCriteria,
    PathOrPattern,
    is_json,
)


def convert_zarrgroup_to_light_datatree(
    zgroup: zarr.Group,
    name: str = "product",
) -> DataTree:
    """
    Warning: arrays are not loaded but replaced with empty arrays!
    """

    class FillDataTree:

        def __init__(
            self,
            dt: DataTree,
            zdata: zarr.Group,
            light: bool = True,
        ) -> None:
            """_summary_

            Parameters
            ----------
            dt
                _description_
            zdata
                _description_
            light, optional
                extract only metadata, ignore arrays, by default True
            """
            self.zdata = zdata
            self.dt = dt
            self.light = light

        def __call__(self, path: str) -> None:
            # TODO: replace manual cf conversion with xarray
            # See https://github.com/pydata/xarray/blob/main/xarray/backends/zarr.py#L625
            zgr = self.zdata[path]
            dt = self.dt
            name = Path(path).name
            zattrs = zgr.attrs.asdict()
            attrs = copy.copy(zattrs)
            dims = zattrs.get("_ARRAY_DIMENSIONS")
            if isinstance(zgr, zarr.core.Array):
                if "scale_factor" in zattrs:
                    dtype = np.dtype(type(zattrs["scale_factor"]))
                else:
                    dtype = zgr.dtype
                dtype = zgr.dtype
                try:
                    shape = [1 for n in zgr.shape]
                    attrs["_FillValue"] = zgr.fill_value
                    if self.light:
                        data = np.empty(shape, dtype)
                        array = xr.DataArray(dims=dims, data=data, attrs=attrs)
                    else:
                        data = zgr
                        array = xr.DataArray(dims=dims, data=data, attrs=attrs)

                    variable = Variable(array.dims, data=array, attrs=attrs)
                except ValueError as e:
                    raise e
                else:

                    # Decode array if required
                    variable = decode_cf_variable(name, variable, decode_times=False)
                    dt[path] = variable
                    variable.attrs.update(zattrs)

                    # Fill io dict (encoded information)
                    encoding_data = {"fill_value": zgr.fill_value, "storage_type": zgr.dtype}
                    # attrs["fill_value"] = np.iinfo(variable.dtype).min
                    attrs = decode_storage_attributes(variable, encoding=encoding_data, path=path)
                    dt[path].attrs.update(attrs)

            else:
                dt[path] = DataTree(name=name)
                dt[path].attrs = attrs

    dt: DataTree = DataTree(name=name)
    dt.attrs = zgroup.attrs.asdict()
    filler = FillDataTree(dt, zgroup)
    zgroup.visit(filler)

    for gr in dt.subtree:
        coordinates = set()
        for p_var in gr.variables:
            try:
                coords = gr[p_var].coordinates.split(" ")
            except AttributeError:
                pass
            else:
                coordinates.update(set(coords))
        if coordinates:
            gr.attrs["_coordinates"] = coordinates

    return dt


def load_metadata(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> AttributeHandler:
    if isinstance(path_or_pattern, DataTree):
        return AttributeHandler(path_or_pattern)
    elif is_eopf_adf_loaded(path_or_pattern) and isinstance(path_or_pattern.data_ptr, DataTree):
        return AttributeHandler(path_or_pattern.data_ptr)
    url, upath, credentials = get_url_and_credentials(
        path_or_pattern,
        credentials=credentials,
        match_criteria=match_criteria,
        **kwargs,
    )
    fix_kwargs_for_lazy_loading(kwargs)
    logger = kwargs.get("logger", logging.getLogger("sentineltoolbox"))

    if is_json(url):
        xdt = convert_to_datatree(_utils.load_json(upath))
    else:
        if credentials is not None:
            zarr_kwargs = credentials.to_kwargs(url=url, target="zarr.open_consolidated")
        else:
            zarr_kwargs = dict(store=url)

        logger.info(f"open {url}")

        kwargs["credentials"] = credentials
        fs, url = _get_fsspec_filesystem_from_url_and_credentials(url=url, **kwargs)
        if not fs.exists(url):
            raise FileNotFoundError(url)

        data = zarr.open_consolidated(**zarr_kwargs)
        xdt = convert_zarrgroup_to_light_datatree(data)

    xdt.reader_info = {"name": upath.name, "url": upath.url}
    return AttributeHandler(xdt)
