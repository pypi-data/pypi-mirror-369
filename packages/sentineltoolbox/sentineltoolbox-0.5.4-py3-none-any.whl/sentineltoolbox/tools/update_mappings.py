"""
To clarify:

Old CS mapping:
geo_coordinates.nc:latitude -> coord:latitude

New ACRI mapping
geo_coordinates.nc:latitude -> /quality/latitude

DataTree
S03OLCEFR.quality.oa01_radiance_unc.coordinates
'latitude longitude'


"""

import copy
import json
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Hashable, Literal, TypeAlias

import numpy
import numpy as np
import xarray
from eopf.store.mapping_factory import EOPFMappingFactory
from eopf.store.mapping_manager import EOPFMappingManager
from numpy._typing import DTypeLike
from xarray import DataArray, DataTree

import sentineltoolbox.api as stb
from sentineltoolbox.autodoc.ellipsis import Ellipsis
from sentineltoolbox.datatree_utils import DataTreeHandler, get_array
from sentineltoolbox.models.upath import PathFsspec
from sentineltoolbox.readers.resources import get_resource_path, load_resource_file
from sentineltoolbox.resources.reference import PRODUCT
from sentineltoolbox.tools.stb_dump_product import (
    convert_datatree_to_structure_str,
    convert_mapping_to_datatree,
)
from sentineltoolbox.writers.json import DataTreeJSONEncoder

L_UpdateMappingMode_ScaleFactor: TypeAlias = Literal["remove", "update", "ignore"]
L_UpdateMappingMode_FillValue: TypeAlias = Literal["update", "ignore"]
L_UpdateMappingMode_Dtype: TypeAlias = Literal[
    "update-from-array",
    "update-from-metadata",
    "update-from-safe",
    "ignore",
]
L_UpdateMappingMode_DebugLevel: TypeAlias = Literal["debug", "standard"]

########################################################################################################################
# MAPPING CONFIGURATION
########################################################################################################################

DEFAULT_FILL_VALUE = {
    "int64": -9223372036854775808,
    "int32": -2147483648,
    "int16": -32768,
    "int8": -128,
    "uint64": 18446744073709551615,
    "uint32": 4294967295,
    "uint16": 65535,
    "uint8": 255,
}

DEFAULT_CHUNK_SIZES = {
    "rows_an": 1200,
    "columns_an": 1500,
    "fires_an": 600,
    "rows_bn": 1200,
    "columns_bn": 1500,
    "fires_bn": 600,
    "rows_in": 600,
    "columns_in": 750,
    "fires_in": 600,
    "rows_fn": 600,
    "columns_fn": 750,
    "fires_fn": 600,
    "rows_tn": 1024,
    "t_series": 1024,
    "columns_tp": 1024,
    "p_atmos": 1024,
    "orphan_pixels_in": 1024,
    "orphan_pixels_fn": 1024,
    "rows_tp": 1024,
    "columns_tn": 1024,
}

REMAP = stb.load_resource_file("mappings/remap.json", module="sentineltoolbox.conversion.conf")
REMAP["S03OLCEFR"] = REMAP["S3_OL_1_mapping.json"]
REMAP["S03OLCERR"] = REMAP["S3OLCERR_mapping.json"]
# https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/552
REMAP["S03SLSRBT"] = REMAP["S3_SL_1_RBT_mapping.json"]
REMAP["S03SLSLST"] = REMAP["S3_SL_2_LST_mapping.json"]

# remap "S03SLSFRP" has been removed because no more used since stb MR !83
REMAP["S03SYNL2_"] = REMAP["S3_SY_2_SYN_mapping.json"]
REMAP["S03SYNAOD"] = REMAP["S3SYNAOD_mapping.json"]
REMAP["S03OLCLFR"] = REMAP["S3_OL_2_mapping.json"]
REMAP["S03OLCLRR"] = REMAP["S3_OL_2_mapping.json"]

DPR_COORD_NAMESPACES = {
    "OLCI": {
        "geo_coordinates.nc:columns": "coords:image:columns",
        "geo_coordinates.nc:latitude": "coords:image:latitude",
        "geo_coordinates.nc:longitude": "coords:image:longitude",
        "geo_coordinates.nc:rows": "coords:image:rows",
        "geo_coordinates.nc:altitude": "coords:image:altitude",
        "instrument_data.nc:bands": "coords:image:bands",
        # "instrument_data.nc:detector_index": "/conditions/image/detector_index",
        "instrument_data.nc:detectors": "coords:detectors",
        "instrument_data.nc:frame_offset": "/conditions/image/frame_offset",
        # "removed_pixels.nc:detector_index": "coords:orphans:detector_index",
        # "removed_pixels.nc:frame_offset": "coords:orphans:frame_offset",
        "removed_pixels.nc:latitude": "coords:orphans:latitude",
        "removed_pixels.nc:longitude": "coords:orphans:longitude",
        "removed_pixels.nc:altitude": "coords:orphans:altitude",
        "removed_pixels.nc:removed_pixels": "coords:orphans:removed_pixels",
        "tie_geo_coordinates.nc:latitude": "coords:tie_point:latitude",
        "tie_geo_coordinates.nc:longitude": "coords:tie_point:longitude",
        "tie_geo_coordinates.nc:tie_columns": "coords:tie_point:tp_columns",
        "tie_geo_coordinates.nc:tie_rows": "coords:tie_point:tp_rows",
        "tie_meteo.nc:tie_pressure_levels": "coords:tie_point:pressure_level",
        "tie_meteo.nc:wind_vectors": "coords:tie_point:wind_vector",
        "time_coordinates.nc:time_stamp": "coords:image:time_stamp",
    },
    "SLSTR": {
        "met_tx.nc:t_series": "coords:tie_point:t_series",
        "met_tx.nc:p_atmos": "coords:tie_point:p_atmos",
        "geodetic_tx.nc:latitude_tx": "coords:tie_point:latitude",
        "geodetic_tx.nc:longitude_tx": "coords:tie_point:longitude",
        "cartesian_tx.nc:rows": "coords:tie_point:rows",
        "cartesian_tx.nc:columns": "coords:tie_point:columns",
        "cartesian_tx.nc:x_tx": "coords:tie_point:x",
        "cartesian_tx.nc:y_tx": "coords:tie_point:y",
        "cartesian_in.nc:rows": "coords:in:rows",
        "cartesian_in.nc:columns": "coords:in:columns",
        "cartesian_io.nc:rows": "coords:io:rows",
        "cartesian_io.nc:columns": "coords:io:columns",
        "cartesian_an.nc:rows": "coords:an:rows",
        "cartesian_an.nc:columns": "coords:an:columns",
        "cartesian_ao.nc:rows": "coords:ao:rows",
        "cartesian_ao.nc:columns": "coords:ao:columns",
        "cartesian_bn.nc:rows": "coords:bn:rows",
        "cartesian_bn.nc:columns": "coords:bn:columns",
        "cartesian_bo.nc:rows": "coords:bo:rows",
        "cartesian_bo.nc:columns": "coords:bo:columns",
        "cartesian_fn.nc:rows": "coords:fn:rows",
        "cartesian_fn.nc:columns": "coords:fn:columns",
        "cartesian_fo.nc:rows": "coords:fo:rows",
        "cartesian_fo.nc:columns": "coords:fo:columns",
        # conditions/geometry_to/(solar|sat)_(zenith|azimut|path)_to
        "geometry_to.nc:rows": "coords:to:rows",
        "geometry_to.nc:columns": "coords:to:columns",
        # conditions/geometry_to/(solar|sat)_(zenith|azimut|path)_tn
        "geometry_tn.nc:rows": "coords:tn:rows",
        "geometry_tn.nc:columns": "coords:tn:columns",
        # orphans
        "cartesian_an.nc:orphan_pixels": "coords:an:orphan_pixels",
        "cartesian_ao.nc:orphan_pixels": "coords:ao:orphan_pixels",
        "cartesian_bn.nc:orphan_pixels": "coords:bn:orphan_pixels",
        "cartesian_bo.nc:orphan_pixels": "coords:bo:orphan_pixels",
        "cartesian_in.nc:orphan_pixels": "coords:in:orphan_pixels",
        "cartesian_io.nc:orphan_pixels": "coords:io:orphan_pixels",
        "cartesian_fn.nc:orphan_pixels": "coords:fn:orphan_pixels",
        "cartesian_fo.nc:orphan_pixels": "coords:fo:orphan_pixels",
        "S1_quality_an.nc:detectors": "coords:an:detectors",
        "S1_quality_ao.nc:detectors": "coords:ao:detectors",
        "S4_quality_bn.nc:detectors": "coords:bn:detectors",
        "S4_quality_bo.nc:detectors": "coords:bo:detectors",
        "S7_quality_in.nc:detectors": "coords:in:detectors",
        "S7_quality_io.nc:detectors": "coords:io:detectors",
        "F1_quality_fn.nc:detectors": "coords:fn:detectors",
        "F1_quality_fo.nc:detectors": "coords:fo:detectors",
        "viscal.nc:visible_detectors": "coords:visible_detectors",
        "viscal.nc:swir_detectors": "coords:swir_detectors",
        "viscal.nc:integrators": "coords:integrators",
        "S1_quality_an.nc:uncertainties": "coords:an:uncertainties_s1",
        "S2_quality_an.nc:uncertainties": "coords:an:uncertainties_s2",
        "S3_quality_an.nc:uncertainties": "coords:an:uncertainties_s3",
        "S4_quality_an.nc:uncertainties": "coords:an:uncertainties_s4",
        "S5_quality_an.nc:uncertainties": "coords:an:uncertainties_s5",
        "S6_quality_an.nc:uncertainties": "coords:an:uncertainties_s6",
        "S7_quality_in.nc:uncertainties": "coords:in:uncertainties_s7",
        "S8_quality_in.nc:uncertainties": "coords:in:uncertainties_s8",
        "S9_quality_in.nc:uncertainties": "coords:in:uncertainties_s9",
        "F1_quality_fn.nc:uncertainties": "coords:fn:uncertainties_f1",
        "F2_quality_in.nc:uncertainties": "coords:in:uncertainties_f2",
        "cartesian_an.nc:x_an": "coords:an:x",
        "cartesian_an.nc:y_an": "coords:an:y",
        "geodetic_an.nc:latitude_an": "coords:an:latitude",
        "geodetic_an.nc:longitude_an": "coords:an:longitude",
        # "geodetic_an.nc:elevation_an": "coords:an:elevation",
        "cartesian_bn.nc:x_bn": "coords:bn:x",
        "cartesian_bn.nc:y_bn": "coords:bn:y",
        "geodetic_bn.nc:latitude_bn": "coords:bn:latitude",
        "geodetic_bn.nc:longitude_bn": "coords:bn:longitude",
        # "geodetic_bn.nc:elevation_bn": "coords:bn:elevation",
        "cartesian_in.nc:x_in": "coords:in:x",
        "cartesian_in.nc:y_in": "coords:in:y",
        "geodetic_in.nc:latitude_in": "coords:in:latitude",
        "geodetic_in.nc:longitude_in": "coords:in:longitude",
        # "geodetic_in.nc:elevation_in": "coords:in:elevation",
        "cartesian_fn.nc:x_fn": "coords:fn:x",
        "cartesian_fn.nc:y_fn": "coords:fn:y",
        "geodetic_fn.nc:latitude_fn": "coords:fn:latitude",
        "geodetic_fn.nc:longitude_fn": "coords:fn:longitude",
        # "geodetic_fn.nc:elevation_fn": "coords:fn:elevation",
        "cartesian_ao.nc:x_ao": "coords:ao:x",
        "cartesian_ao.nc:y_ao": "coords:ao:y",
        "geodetic_ao.nc:latitude_ao": "coords:ao:latitude",
        "geodetic_ao.nc:longitude_ao": "coords:ao:longitude",
        # "geodetic_ao.nc:elevation_ao": "coords:ao:elevation",
        "cartesian_bo.nc:x_bo": "coords:bo:x",
        "cartesian_bo.nc:y_bo": "coords:bo:y",
        "geodetic_bo.nc:latitude_bo": "coords:bo:latitude",
        "geodetic_bo.nc:longitude_bo": "coords:bo:longitude",
        # "geodetic_bo.nc:elevation_bo": "coords:bo:elevation",
        "cartesian_io.nc:x_io": "coords:io:x",
        "cartesian_io.nc:y_io": "coords:io:y",
        "geodetic_io.nc:latitude_io": "coords:io:latitude",
        "geodetic_io.nc:longitude_io": "coords:io:longitude",
        # "geodetic_io.nc:elevation_io": "coords:io:elevation",
        "cartesian_fo.nc:x_fo": "coords:fo:x",
        "cartesian_fo.nc:y_fo": "coords:fo:y",
        "geodetic_fo.nc:latitude_fo": "coords:fo:latitude",
        "geodetic_fo.nc:longitude_fo": "coords:fo:longitude",
        # "geodetic_fo.nc:elevation_fo": "coords:fo:elevation",
        # "time_an.nc:time_stamp_a": "coords:an:time_stamp",
        # "time_bn.nc:time_stamp_b": "coords:bn:time_stamp",
        # "time_in.nc:time_stamp_i": "coords:in:time_stamp",
        # "cartesian_an.nc:x_orphan_an": "coords:an_orphan:x",
        # "cartesian_an.nc:y_orphan_an": "coords:an_orphan:y",
        # "geodetic_an.nc:elevation_orphan_an": "coords:an_orphan:elevation",
        # "geodetic_an.nc:latitude_orphan_an": "coords:an_orphan:latitude",
        # "geodetic_an.nc:longitude_orphan_an": "coords:an_orphan:longitude",
        # "cartesian_bn.nc:x_orphan_bn": "coords:bn_orphan:x",
        # "cartesian_bn.nc:y_orphan_bn": "coords:bn_orphan:y",
        # "geodetic_bn.nc:elevation_orphan_bn": "coords:bn_orphan:elevation",
        # "geodetic_bn.nc:latitude_orphan_bn": "coords:bn_orphan:latitude",
        # "geodetic_bn.nc:longitude_orphan_bn": "coords:bn_orphan:longitude",
        # "cartesian_fn.nc:x_orphan_fn": "coords:fn_orphan:x",
        # "cartesian_fn.nc:y_orphan_fn": "coords:fn_orphan:y",
        # "geodetic_fn.nc:elevation_orphan_fn": "coords:fn_orphan:elevation",
        # "geodetic_fn.nc:latitude_orphan_fn": "coords:fn_orphan:latitude",
        # "geodetic_fn.nc:longitude_orphan_fn": "coords:fn_orphan:longitude",
        # "cartesian_in.nc:x_orphan_in": "coords:in_orphan:x",
        # "cartesian_in.nc:y_orphan_in": "coords:in_orphan:y",
        # "geodetic_in.nc:elevation_orphan_in": "coords:in_orphan:elevation",
        # "geodetic_in.nc:latitude_orphan_in": "coords:in_orphan:latitude",
        # "geodetic_in.nc:longitude_orphan_in": "coords:in_orphan:longitude",
        # "cartesian_ao.nc:x_orphan_ao": "coords:ao_orphan:x",
        # "cartesian_ao.nc:y_orphan_ao": "coords:ao_orphan:y",
        # "geodetic_ao.nc:elevation_orphan_ao": "coords:ao_orphan:elevation",
        # "geodetic_ao.nc:latitude_orphan_ao": "coords:ao_orphan:latitude",
        # "geodetic_ao.nc:longitude_orphan_ao": "coords:ao_orphan:longitude",
        # "cartesian_bo.nc:x_orphan_bo": "coords:bo_orphan:x",
        # "cartesian_bo.nc:y_orphan_bo": "coords:bo_orphan:y",
        # "geodetic_bo.nc:elevation_orphan_bo": "coords:bo_orphan:elevation",
        # "geodetic_bo.nc:latitude_orphan_bo": "coords:bo_orphan:latitude",
        # "geodetic_bo.nc:longitude_orphan_bo": "coords:bo_orphan:longitude",
        # "cartesian_io.nc:x_orphan_io": "coords:io_orphan:x",
        # "cartesian_io.nc:y_orphan_io": "coords:io_orphan:y",
        # "geodetic_io.nc:elevation_orphan_io": "coords:io_orphan:elevation",
        # "geodetic_io.nc:latitude_orphan_io": "coords:io_orphan:latitude",
        # "geodetic_io.nc:longitude_orphan_io": "coords:io_orphan:longitude",
        # "cartesian_fo.nc:x_orphan_fo": "coords:fo_orphan:x",
        # "cartesian_fo.nc:y_orphan_fo": "coords:fo_orphan:y",
        # "geodetic_fo.nc:elevation_orphan_fo": "coords:fo_orphan:elevation",
        # "geodetic_fo.nc:latitude_orphan_fo": "coords:fo_orphan:latitude",
        # "geodetic_fo.nc:longitude_orphan_fo": "coords:fo_orphan:longitude",
    },
}
# "geo_coordinates.nc:columns": "coords:image:columns",
DPR_COORD_NAMESPACES["S03OLCEFR"] = copy.copy(DPR_COORD_NAMESPACES["OLCI"])
DPR_COORD_NAMESPACES["S03OLCLFR"] = copy.copy(DPR_COORD_NAMESPACES["OLCI"])
DPR_COORD_NAMESPACES["S03OLCERR"] = copy.copy(DPR_COORD_NAMESPACES["OLCI"])
DPR_COORD_NAMESPACES["S03OLCLRR"] = copy.copy(DPR_COORD_NAMESPACES["OLCI"])
DPR_COORD_NAMESPACES["S03SLSRBT"] = copy.copy(DPR_COORD_NAMESPACES["SLSTR"])
DPR_COORD_NAMESPACES["S03SLSLST"] = copy.copy(DPR_COORD_NAMESPACES["SLSTR"])
DPR_COORD_NAMESPACES["S03SLSFRP"] = copy.copy(DPR_COORD_NAMESPACES["SLSTR"])

DPR_COORD_NAMESPACES["S03SLSFRP"].update(
    {
        "FRP_in.nc:fires": "coords:in:fires",
        "FRP_in.nc:columns": "coords:in:columns",
        "FRP_in.nc:rows": "coords:in:rows",
        "FRP_in.nc:latitude": "coords:in:latitude",
        "FRP_in.nc:longitude": "coords:in:longitude",
        "FRP_an.nc:fires": "coords:an:fires",
        "FRP_an.nc:columns": "coords:an:columns",
        "FRP_an.nc:rows": "coords:an:rows",
        "FRP_an.nc:latitude": "coords:an:latitude",
        "FRP_an.nc:longitude": "coords:an:longitude",
        "FRP_bn.nc:fires": "coords:bn:fires",
        "FRP_bn.nc:columns": "coords:bn:columns",
        "FRP_bn.nc:rows": "coords:bn:rows",
        "FRP_bn.nc:latitude": "coords:bn:latitude",
        "FRP_bn.nc:longitude": "coords:bn:longitude",
    },
)

for legacy, dpr in DPR_COORD_NAMESPACES["S03SLSFRP"].items():
    legacy_filename, legacy_coord_name = legacy.split(":")
    if legacy_filename in (
        "cartesian_in.nc",
        "cartesian_bn.nc",
        "cartesian_fn.nc",
        "geodetic_in.nc",
        "geodetic_bn.nc",
        "geodetic_fn.nc",
    ):
        _, ns, dpr_coord_name = dpr.split(":")
        DPR_COORD_NAMESPACES["S03SLSFRP"][legacy] = f"coords:aux_{ns}:{dpr_coord_name}"

DPR_COORD_NAMESPACES["S03SLSLST"].update(
    {
        "cartesian_in.nc:x_orphan_in": "coords:in_orphan:x",
        "cartesian_in.nc:y_orphan_in": "coords:in_orphan:y",
        "geodetic_in.nc:latitude_orphan_in": "coords:in_orphan:latitude",
        "geodetic_in.nc:longitude_orphan_in": "coords:in_orphan:longitude",
    },
)

SUPPORTED_MAPPINGS = DPR_COORD_NAMESPACES.keys()


#  "latitude_an": "latitude",
COORD_MAPPINGS = {
    "OLCI": {
        "tp_rows": "rows",
        "tp_columns": "columns",
        "tp_latitude": "latitude",
        "tp_longitude": "longitude",
        "orphan_latitude": "latitude",
        "orphan_longitude": "longitude",
        "orphan_frame_offset": "frame_offset",
        "orphan_detector_index": "detector_index",
    },
    "SLSTR": {
        "fires_in": "fires",
        "fires_bn": "fires",
        "fires_an": "fires",
        "rows_tp": "rows",
        "columns_tp": "columns",
        "rows_in": "rows",
        "columns_in": "columns",
        "rows_io": "rows",
        "columns_io": "columns",
        "rows_an": "rows",
        "columns_an": "columns",
        "rows_ao": "rows",
        "columns_ao": "columns",
        "rows_bn": "rows",
        "columns_bn": "columns",
        "rows_bo": "rows",
        "columns_bo": "columns",
        "rows_fn": "rows",
        "columns_fn": "columns",
        "rows_fo": "rows",
        "columns_fo": "columns",
        "rows_to": "rows",
        "columns_to": "columns",
        "rows_tn": "rows",
        "columns_tn": "columns",
        "orphan_pixels_an": "orphan_pixels",
        "orphan_pixels_ao": "orphan_pixels",
        "orphan_pixels_bn": "orphan_pixels",
        "orphan_pixels_bo": "orphan_pixels",
        "orphan_pixels_in": "orphan_pixels",
        "orphan_pixels_io": "orphan_pixels",
        "orphan_pixels_fn": "orphan_pixels",
        "orphan_pixels_fo": "orphan_pixels",
        "detectors_an": "detectors",
        "detectors_ao": "detectors",
        "detectors_bn": "detectors",
        "detectors_bo": "detectors",
        "detectors_in": "detectors",
        "detectors_io": "detectors",
        "detectors_fn": "detectors",
        "detectors_fo": "detectors",
        "x_an": "x",
        "y_an": "y",
        "latitude_an": "latitude",
        "longitude_an": "longitude",
        "elevation_an": "elevation",
        "x_bn": "x",
        "y_bn": "y",
        "latitude_bn": "latitude",
        "longitude_bn": "longitude",
        "elevation_bn": "elevation",
        "x_in": "x",
        "y_in": "y",
        "latitude_in": "latitude",
        "longitude_in": "longitude",
        "elevation_in": "elevation",
        "x_fn": "x",
        "y_fn": "y",
        "latitude_fn": "latitude",
        "longitude_fn": "longitude",
        "elevation_fn": "elevation",
        "x_ao": "x",
        "y_ao": "y",
        "latitude_ao": "latitude",
        "longitude_ao": "longitude",
        "elevation_ao": "elevation",
        "x_bo": "x",
        "y_bo": "y",
        "latitude_bo": "latitude",
        "longitude_bo": "longitude",
        "elevation_bo": "elevation",
        "x_io": "x",
        "y_io": "y",
        "latitude_io": "latitude",
        "longitude_io": "longitude",
        "elevation_io": "elevation",
        "x_fo": "x",
        "y_fo": "y",
        "latitude_fo": "latitude",
        "longitude_fo": "longitude",
        "elevation_fo": "elevation",
        "x_tp": "x",
        "y_tp": "y",
        "latitude_tp": "latitude",
        "longitude_tp": "longitude",
        "time_stamp_a": "time_stamp",
        "time_stamp_b": "time_stamp",
        "time_stamp_i": "time_stamp",
        "x_orphan_an": "x",
        "y_orphan_an": "y",
        "elevation_orphan_an": "elevation",
        "latitude_orphan_an": "latitude",
        "longitude_orphan_an": "longitude",
        "x_orphan_bn": "x",
        "y_orphan_bn": "y",
        "elevation_orphan_bn": "elevation",
        "latitude_orphan_bn": "latitude",
        "longitude_orphan_bn": "longitude",
        "x_orphan_fn": "x",
        "y_orphan_fn": "y",
        "elevation_orphan_fn": "elevation",
        "latitude_orphan_fn": "latitude",
        "longitude_orphan_fn": "longitude",
        "x_orphan_in": "x",
        "y_orphan_in": "y",
        "elevation_orphan_in": "elevation",
        "latitude_orphan_in": "latitude",
        "longitude_orphan_in": "longitude",
        "x_orphan_ao": "x",
        "y_orphan_ao": "y",
        "elevation_orphan_ao": "elevation",
        "latitude_orphan_ao": "latitude",
        "longitude_orphan_ao": "longitude",
        "x_orphan_bo": "x",
        "y_orphan_bo": "y",
        "elevation_orphan_bo": "elevation",
        "latitude_orphan_bo": "latitude",
        "longitude_orphan_bo": "longitude",
        "x_orphan_io": "x",
        "y_orphan_io": "y",
        "elevation_orphan_io": "elevation",
        "latitude_orphan_io": "latitude",
        "longitude_orphan_io": "longitude",
        "x_orphan_fo": "x",
        "y_orphan_fo": "y",
        "elevation_orphan_fo": "elevation",
        "latitude_orphan_fo": "latitude",
        "longitude_orphan_fo": "longitude",
    },
}
COORD_MAPPINGS["S03OLCEFR"] = COORD_MAPPINGS["OLCI"]
COORD_MAPPINGS["S03OLCLFR"] = COORD_MAPPINGS["OLCI"]
COORD_MAPPINGS["S03OLCERR"] = COORD_MAPPINGS["OLCI"]
COORD_MAPPINGS["S03OLCLRR"] = COORD_MAPPINGS["OLCI"]
COORD_MAPPINGS["S03SLSRBT"] = COORD_MAPPINGS["SLSTR"]
COORD_MAPPINGS["S03SLSLST"] = COORD_MAPPINGS["SLSTR"]
COORD_MAPPINGS["S03SLSFRP"] = COORD_MAPPINGS["SLSTR"]

DIMS_MAPPINGS = {
    "S03SLSLST": {
        "rows_tn": "rows_tp",
        "columns_tn": "columns_tp",
    },
    "S03SLSRBT": {
        "rows_tn": "rows_tp",
        "columns_tn": "columns_tp",
    },
    "S03SLSFRP": {
        "rows_tn": "rows_tp",
        "columns_tn": "columns_tp",
    },
}

# "geodetic_tx.nc:latitude_tx"
# -> "coords:tie_point:latitude" ("rows_tp", "columns_tp")
# -> meteo : latitude_tp /conditions/geometry


COORD_LUT = {
    "OLCI": {
        "/conditions/image/longitude": "image",
        "/conditions/image/latitude": "image",
        "/conditions/image/altitude": "image",
        "/measurements/longitude": "image",
        "/measurements/latitude": "image",
        "/measurements/altitude": "image",
        "/quality/orphans/longitude": "orphans",
        "/quality/orphans/latitude": "orphans",
        "/quality/orphans/altitude": "orphans",
        "/conditions/meteorology/pressure_level": "tie_point",
        "/conditions/meteorology/tp_rows": "tie_point",
        "/conditions/meteorology/tp_columns": "tie_point",
    },
    "SLSTR": {
        "/measurements/orphan/elevation": "in_orphan",
        "/measurements/orphan/x": "in_orphan",
        "/measurements/orphan/y": "in_orphan",
        "/measurements/orphan/latitude": "in_orphan",
        "/measurements/orphan/longitude": "in_orphan",
        "/measurements/anadir/latitude": "an",
        "/measurements/bnadir/latitude": "bn",
        "/measurements/inadir/latitude": "in",
        "/measurements/anadir/longitude": "an",
        "/measurements/bnadir/longitude": "bn",
        "/measurements/inadir/longitude": "in",
        "/measurements/anadir/columns": "an",
        "/measurements/bnadir/columns": "bn",
        "/measurements/inadir/columns": "in",
        "/measurements/anadir/rows": "an",
        "/measurements/bnadir/rows": "bn",
        "/measurements/inadir/rows": "in",
        "/conditions/auxiliary/anadir/latitude": "aux_an",
        "/conditions/auxiliary/bnadir/latitude": "aux_bn",
        "/conditions/auxiliary/inadir/latitude": "aux_in",
        "/conditions/auxiliary/anadir/longitude": "aux_an",
        "/conditions/auxiliary/bnadir/longitude": "aux_bn",
        "/conditions/auxiliary/inadir/longitude": "aux_in",
        "/conditions/auxiliary/anadir/columns": "aux_an",
        "/conditions/auxiliary/bnadir/columns": "aux_bn",
        "/conditions/auxiliary/inadir/columns": "aux_in",
        "/conditions/auxiliary/anadir/rows": "aux_an",
        "/conditions/auxiliary/bnadir/rows": "aux_bn",
        "/conditions/auxiliary/inadir/rows": "aux_in",
        "/conditions/auxiliary/anadir/elevation": "aux_an",
        "/conditions/auxiliary/bnadir/elevation": "aux_bn",
        "/conditions/auxiliary/inadir/elevation": "aux_in",
        "/conditions/auxiliary/anadir/x": "aux_an",
        "/conditions/auxiliary/bnadir/x": "aux_bn",
        "/conditions/auxiliary/inadir/x": "aux_in",
        "/conditions/auxiliary/anadir/y": "aux_an",
        "/conditions/auxiliary/bnadir/y": "aux_bn",
        "/conditions/auxiliary/inadir/y": "aux_in",
        "/measurements/elevation": "in_orphan",
        "/measurements/x": "in",
        "/measurements/y": "in",
        "/measurements/latitude": "in",
        "/measurements/longitude": "in",
        "/conditions/geometry/x": "tie_point",
        "/conditions/geometry/y": "tie_point",
        "/conditions/geometry_to/rows": "to",
        "/conditions/geometry_to/columns": "to",
        "/conditions/geometry/latitude": "tie_point",
        "/conditions/meteorology/latitude": "tie_point",
        "/conditions/meteorology/longitude": "tie_point",
        "/conditions/meteorology/t_series": "tie_point",
        "/conditions/meteorology/p_atmos": "tie_point",
    },
}
COORD_LUT["S03OLCEFR"] = COORD_LUT["OLCI"]
COORD_LUT["S03OLCLFR"] = COORD_LUT["OLCI"]
COORD_LUT["S03OLCERR"] = COORD_LUT["OLCI"]
COORD_LUT["S03OLCLRR"] = COORD_LUT["OLCI"]
COORD_LUT["S03SLSRBT"] = COORD_LUT["SLSTR"]
COORD_LUT["S03SLSLST"] = COORD_LUT["SLSTR"]
COORD_LUT["S03SLSFRP"] = COORD_LUT["SLSTR"]

FORCE_TARGET_DTYPE = {
    "OLCI": {
        "/conditions/image/detector_index": "u2",
        "/conditions/orphans/detector_index": "u2",
        "/conditions/image/frame_offset": "i1",
        # "coords:tie_point:pressure_level": "u1",  # CS demand, see !822
        # "coords:tie_point:wind_vector": "u1",  # CS demand, see !822
        # "/coordinates/orphans/removed_pixels": "u1",  # CS demand, see !822
    },
    "SLSTR": {
        # "/conditions/time/nadir_first_scan_i": "int32",
        # "/conditions/time/nadir_last_scan_i": "int32",
        # "/conditions/time/nadir_maximal_ts_i": "int32",
        # "/conditions/time/nadir_minimal_ts_i": "int32",
        # "/conditions/time/oblique_first_scan_i": "int32",
        # "/conditions/time/oblique_last_scan_i": "int32",
        # "/conditions/time/oblique_maximal_ts_i": "int32",
        # "/conditions/time/oblique_minimal_ts_i": "int32",
        "/conditions/processing/inadir/pixel": "int32",
        "/conditions/processing/inadir/scan": "int32",
        "/conditions/processing/inadir/orphan/pixel": "int32",
        "/conditions/processing/inadir/orphan/scan": "int32",
        "/conditions/time_in/nadir_first_scan_i": "int32",
        "/conditions/time_in/nadir_last_scan_i": "int32",
        "/conditions/time_in/oblique_first_scan_i": "int32",
        "/conditions/time_in/oblique_last_scan_i": "int32",
        "/conditions/processing/anadir/pixel": "int32",
        "/conditions/processing/anadir/orphan/pixel": "int32",
        "/conditions/processing/anadir/scan": "int32",
        "/conditions/processing/anadir/orphan/scan": "int32",
        "/conditions/processing/aoblique/pixel": "int32",
        "/conditions/processing/aoblique/orphan/pixel": "int32",
        "/conditions/processing/aoblique/scan": "int32",
        "/conditions/processing/aoblique/orphan/scan": "int32",
        "/conditions/processing/bnadir/pixel": "int32",
        "/conditions/processing/bnadir/orphan/pixel": "int32",
        "/conditions/processing/bnadir/scan": "int32",
        "/conditions/processing/bnadir/orphan/scan": "int32",
        "/conditions/processing/boblique/pixel": "int32",
        "/conditions/processing/boblique/orphan/pixel": "int32",
        "/conditions/processing/boblique/scan": "int32",
        "/conditions/processing/boblique/orphan/scan": "int32",
        "/conditions/processing/fnadir/pixel": "int32",
        "/conditions/processing/fnadir/orphan/pixel": "int32",
        "/conditions/processing/fnadir/scan": "int32",
        "/conditions/processing/fnadir/orphan/scan": "int32",
        "/conditions/processing/foblique/pixel": "int32",
        "/conditions/processing/foblique/orphan/pixel": "int32",
        "/conditions/processing/foblique/scan": "int32",
        "/conditions/processing/foblique/orphan/scan": "int32",
        "/conditions/processing/ioblique/pixel": "int32",
        "/conditions/processing/ioblique/orphan/pixel": "int32",
        "/conditions/processing/ioblique/scan": "int32",
        "/conditions/processing/ioblique/orphan/scan": "int32",
        "/conditions/time_an/nadir_first_scan_a": "int32",
        "/conditions/time_an/nadir_last_scan_a": "int32",
        "/conditions/time_an/oblique_first_scan_a": "int32",
        "/conditions/time_an/oblique_last_scan_a": "int32",
        "/conditions/time_bn/nadir_first_scan_b": "int32",
        "/conditions/time_bn/nadir_last_scan_b": "int32",
        "/conditions/time_bn/oblique_first_scan_b": "int32",
        "/conditions/time_bn/oblique_last_scan_b": "int32",
        "/measurements/bnadir/used_channel": "uint8",
        "/measurements/anadir/used_channel": "uint8",
        "/measurements/inadir/used_channel": "uint8",
        "/measurements/bnadir/s5_confirm": "uint8",
        "/measurements/anadir/s5_confirm": "uint8",
        "/measurements/inadir/s5_confirm": "uint8",
        "/measurements/bnadir/day_night": "int8",
        "/measurements/anadir/day_night": "int8",
        "/measurements/inadir/day_night": "int8",
    },
}
FORCE_TARGET_DTYPE["S03OLCEFR"] = FORCE_TARGET_DTYPE["OLCI"]
FORCE_TARGET_DTYPE["S03OLCLFR"] = FORCE_TARGET_DTYPE["OLCI"]
FORCE_TARGET_DTYPE["S03OLCERR"] = FORCE_TARGET_DTYPE["OLCI"]
FORCE_TARGET_DTYPE["S03OLCLRR"] = FORCE_TARGET_DTYPE["OLCI"]
FORCE_TARGET_DTYPE["S03SLSRBT"] = FORCE_TARGET_DTYPE["SLSTR"]
FORCE_TARGET_DTYPE["S03SLSLST"] = FORCE_TARGET_DTYPE["SLSTR"]
FORCE_TARGET_DTYPE["S03SLSFRP"] = FORCE_TARGET_DTYPE["SLSTR"]

REMOVE_VARIABLES = {
    "S03OLCLFR": [
        # "/conditions/image/altitude",
        "coords:detectors",
        "coords:tie_point:tp_columns",
        "coords:tie_point:tp_rows",
        "coords:tp_columns",
        "coords:tp_rows",
        "coords:columns",
        "coords:rows",
        "coords:image:columns",
        "coords:image:rows",
    ],
    "S03OLCEFR": [
        "coords:orphans:frame_offset",
        "coords:orphans:detector_index",
        "coords:tie_point:tp_columns",
        "coords:tie_point:tp_rows",
        "coords:tp_columns",
        "coords:tp_rows",
        "coords:columns",
        "coords:rows",
        "coords:image:columns",
        "coords:image:rows",
    ],
    "S03SLSRBT": [
        # "/conditions/meteorology/east_west_stress_tp",
        # "/conditions/meteorology/latent_heat_tp",
        # "/conditions/meteorology/north_south_stress_tp",
        # "/conditions/meteorology/sensible_heat_tp",
        # "/conditions/meteorology/solar_radiation_tp",
        # "/conditions/meteorology/specific_humidity_tp",
        # "/conditions/meteorology/temperature_profile_tp",
        # "/conditions/meteorology/thermal_radiation_tp",
        # "/conditions/meteorology/u_wind_tp",
        # "/conditions/meteorology/v_wind_tp",
    ],
    "S03SLSLST": [
        # "coords:t_series",
        # "/conditions/meteorology/cloud_fraction_tp",
        # "/conditions/meteorology/dew_point_tp",
        # "/conditions/meteorology/east_west_stress_tp",
        # "/conditions/meteorology/latent_heat_tp",
        # "/conditions/meteorology/north_south_stress_tp",
        # "/conditions/meteorology/sea_ice_fraction_tp",
        # "/conditions/meteorology/sea_surface_temperature_tp",
        # "/conditions/meteorology/sensible_heat_tp",
        # "/conditions/meteorology/skin_temperature_tp",
        # "/conditions/meteorology/snow_albedo_tp",
        # "/conditions/meteorology/snow_depth_tp",
        # "/conditions/meteorology/soil_wetness_tp",
        # "/conditions/meteorology/solar_radiation_tp",
        # "/conditions/meteorology/specific_humidity_tp",
        # "/conditions/meteorology/surface_pressure_tp",
        # "/conditions/meteorology/temperature_profile_tp",
        # "/conditions/meteorology/temperature_tp",
        # "/conditions/meteorology/thermal_radiation_tp",
        # "/conditions/meteorology/total_column_ozone_tp",
        # "/conditions/meteorology/total_column_water_vapour_tp",
        # "/conditions/meteorology/u_wind_tp",
        # "/conditions/meteorology/v_wind_tp",
    ],
    "S03SLSFRP": [
        "coords:an:fires",
        "coords:bn:fires",
        "coords:in:fires",
        "coords:an:columns",
        "coords:bn:columns",
        "coords:in:columns",
        "coords:tie_point:columns",
        "coords:aux_an:columns",
        "coords:aux_bn:columns",
        "coords:aux_in:columns",
        "coords:aux_fn:columns",
        "coords:an:rows",
        "coords:bn:rows",
        "coords:in:rows",
        "coords:tie_point:rows",
        "coords:aux_an:rows",
        "coords:aux_bn:rows",
        "coords:aux_in:rows",
        "coords:aux_fn:rows",
        # "coords:tie_point:x",
        # "coords:aux_an:x",
        # "coords:aux_bn:x",
        # "coords:aux_in:x",
        # "coords:aux_fn:x",
        # "coords:tie_point:y",
        # "coords:aux_an:y",
        # "coords:aux_bn:y",
        # "coords:aux_in:y",
        # "coords:aux_fn:y",
        "coords:in_orphan:x",
        "coords:in_orphan:y",
        "coords:in_orphan:longitude",
        "coords:in_orphan:latitude",
        "coords:in_orphan:elevation",
        "coords:fn_orphan:x",
        "coords:fn_orphan:y",
        "coords:fn_orphan:longitude",
        "coords:fn_orphan:latitude",
        "coords:fn_orphan:elevation",
    ],
}

REMOVE_VARIABLES["S03OLCLRR"] = REMOVE_VARIABLES["S03OLCLFR"]
REMOVE_VARIABLES["S03OLCERR"] = REMOVE_VARIABLES["S03OLCEFR"]


FORCE_ATTRS = {
    "OLCI": {
        "coords:tie_point:wind_vector": {"long_name": "dimensions of horizontal wind vector"},  # CS demand, see !822
        "coords:wind_vector": {"long_name": "dimensions of horizontal wind vector"},  # CS demand, see !822
        "coords:orphans:altitude": {
            "long_name": "altitude above reference ellipsoid for removed pixels",  # CS demand, see !822
        },
    },
    "SLSTR": {},
}
# "geo_coordinates.nc:columns": "coords:image:columns",
FORCE_ATTRS["S03OLCEFR"] = copy.copy(FORCE_ATTRS["OLCI"])
FORCE_ATTRS["S03OLCLFR"] = copy.copy(FORCE_ATTRS["OLCI"])
FORCE_ATTRS["S03OLCERR"] = copy.copy(FORCE_ATTRS["OLCI"])
FORCE_ATTRS["S03OLCLRR"] = copy.copy(FORCE_ATTRS["OLCI"])
FORCE_ATTRS["S03SLSRBT"] = copy.copy(FORCE_ATTRS["SLSTR"])
FORCE_ATTRS["S03SLSLST"] = copy.copy(FORCE_ATTRS["SLSTR"])
FORCE_ATTRS["S03SLSFRP"] = copy.copy(FORCE_ATTRS["SLSTR"])

T_CoordId: TypeAlias = tuple[str, tuple[int, ...], str]


def load_map_legacy_to_dpr(ptype: str) -> dict[str, str]:
    """
    Load legacy_to_dpr_product_map if exists else build one using "update_legacy_to_dpr"
    and save it in the right directory.

    legacy_to_dpr_product_map is a dict "legacy path" -> "dpr path":
    {
      "Oa01_radiance.nc:Oa01_radiance": "/measurements/oa01_radiance"
    }

    :param ptype: dpr product type. Ex 'S03OLCEFR'
    :return: dict legacy_to_dpr_product_map
    """
    try:
        return load_resource_file(f"mappings/{ptype}.json", module="sentineltoolbox.conversion")
    except FileNotFoundError:
        print("[SENTINELTOOLBOX] Build new map legacy -> dpr")
        print(f"[SENTINELTOOLBOX] saved to sentineltoolbox/conversion/mappings/{ptype}.json")
        return update_legacy_to_dpr(ptype)


SIMPLIFIED_MAPPINGS: dict[str, Any] = {}
SIMPLIFIED_MAPPINGS["S03OLCEFR"] = load_resource_file(
    "simplified_mappings/S3_OL_1_mapping.json",
    module="sentineltoolbox.conversion.conf",
)
SIMPLIFIED_MAPPINGS["S03OLCERR"] = load_resource_file(
    "simplified_mappings/S3OLCERR_mapping.json",
    module="sentineltoolbox.conversion.conf",
)
SIMPLIFIED_MAPPINGS["S03OLCLFR"] = load_resource_file(
    "simplified_mappings/S3_OL_2_mapping.json",
    module="sentineltoolbox.conversion.conf",
)
SIMPLIFIED_MAPPINGS["S03SLSRBT"] = load_resource_file(
    "simplified_mappings/ref/S3_SL_1_RBT_mapping.json",
    module="sentineltoolbox.conversion.conf",
)
SIMPLIFIED_MAPPINGS["S03SLSLST"] = load_resource_file(
    "simplified_mappings/ref/S3_SL_2_LST_mapping.json",
    module="sentineltoolbox.conversion.conf",
)

SIMPLIFIED_MAPPINGS["S03SLSFRP"] = load_resource_file(
    "simplified_mappings/S3SLSFRP_mapping.json",
    module="sentineltoolbox.conversion.conf",
)

########################################################################################################################
# CONVENIENCE FUNCTIONS TO EXTRACT MAPPING DATA OR UPDATE MAPPING CONFIGURATION
########################################################################################################################


def f() -> None:
    mappings = EOPFMappingManager()
    mapping, _ = mappings.parse_mapping(product_type="S03OLCEFR", processing_version="TODO")
    # JSON(mapping)

    prod = convert_mapping_to_datatree(mapping)
    # PRODUCT.map()

    print(convert_datatree_to_structure_str(prod, details=True))

    S03OLCEFR = PRODUCT["S03OLCEFR"]
    S03OLCEFR.measurements.oa01_radiance


def sort_by_coords(xdt: DataTree) -> dict[T_CoordId, list[str]]:
    """
    Organizes the variables of the DataTree by their coordinates.

    Example of returned value:
     {
        ("latitude", (4088, 77), "float64"): ["/conditions/geometry/oaa", "/conditions/geometry/oza", ...]
    }

    :param xdt: A data structure of type DataTree
    :return: A dictionary where keys are coordinate identifiers
             (name, shape, data type) and values are lists of variable paths
    """
    d: dict[T_CoordId, list[str]] = {}
    for gr in xdt.subtree:
        for coord_name, coord in gr.coords.items():
            k: T_CoordId = (str(coord_name), coord.shape, coord.dtype.name)
            d.setdefault(k, []).append(gr.path)

        for var_path, var in gr.data_vars.items():

            for coord_name, coord in var.coords.items():
                k = (str(coord_name), coord.shape, coord.dtype.name)
                d.setdefault(k, []).append(gr.path + "/" + var_path)
    return d


def display_by_coords(xdt: DataTree, ellipsis: Ellipsis | None = None) -> None:
    """
    Displays the variables of the DataTree grouped by coordinates.

    Example of output:

    altitude (4088, 4865), float32
      - /conditions/image/detector_index
      - /conditions/image/frame_offset
      - /conditions/image/frame_offsetdpr

    :param xdt: A data structure of type DataTree
    :param ellipsis: An optional object allowing truncation of displayed paths
    """
    d = sort_by_coords(xdt)
    for cdata in sorted(d):  # type: ignore
        lst = d[cdata]
        coord_name = cdata[0]
        print(coord_name, ", ".join([str(i) for i in cdata[1:]]))
        if ellipsis is None:
            for real_path in lst:
                print("  -", real_path)
        else:
            for real_path, ellipsed_path in ellipsis.prune(lst):
                print("  -", ellipsed_path)


def display_coord_def_dict(xdt: DataTree, ellipsis: Ellipsis | None = None) -> dict[T_CoordId, str]:
    """
    Generates content of dictionary "coordinate ID" -> "coordinate namespace"
    Comments are added to show real example of variables associated to coordinates.

    Example of output:

    #/conditions/image/detector_index, /conditions/image/frame_offset
    ('altitude', (4088, 4865), 'float32'): "coords:XXXX:altitude",
    #/conditions/geometry/oaa, /conditions/geometry/oza, /conditions/geometry/saa,
    #/conditions/geometry/sza # noqa: E501
    ('latitude', (4088, 77), 'float64'): "coords:XXXX:latitude",

    Use it to update COORDS_DEF dictionnary. Do not forget to replace XXXX

    :param xdt: A data structure of type DataTree
    :param ellipsis: An optional object allowing truncation of displayed paths. See autodoc tutorials
    :return: A dictionary associating each coordinate identifier with a description string
    """
    d = sort_by_coords(xdt)
    ns: dict[T_CoordId, str] = {}
    for k in sorted(d):  # type: ignore
        lst = d[k]
        if ellipsis:
            pruned_lst = ellipsis.prune(lst)
            samples = ", ".join([ell for real, ell in pruned_lst])
        else:
            samples = ", ".join(lst)

        samples = "\n# ".join(textwrap.wrap(samples, 75))
        code = f'# {samples}\n{k}: "coords:XXXX:{k[0]}", '
        print(code)
        ns[k] = f"coords:XXXX:{k[0]}"
    return ns


def associate_safe_src_to_namespace(
    mapping: dict[Hashable, Any],
    safe_path: PathFsspec | Path | str | None = None,
) -> dict[str, str]:
    """
    Example of output

    {'geo_coordinates.nc:rows': 'coords:rows',
    'geo_coordinates.nc:columns': 'coords:columns',
    'tie_geo_coordinates.nc:tie_rows': 'coords:tp_rows',
    'tie_geo_coordinates.nc:tie_columns': 'coords:tp_columns'
    }

    Use this output to update COORDS_NAMESPACES dict

    :param mapping:
    :return:
    """
    d = {}
    ds = {}
    for data in mapping["data_mapping"]:
        tgt = data["target_path"]
        src = data["source_path"]
        if tgt.startswith("coords:"):
            if safe_path:
                safe_path = stb.get_universal_path(safe_path)
                safe_coord = src
                safe_coord_filename, safe_coord_name = safe_coord.split(":")
                if safe_coord_filename not in ds:
                    ds[safe_coord_filename] = stb.open_datatree(safe_path / safe_coord_filename)
            d[src] = tgt
    return d


def associate_safe_src_to_namespace_from_ncfiles(safe_path: str) -> dict[str, str]:
    """
    This function iterates over all NetCDF files in the specified SAFE directory,
    extracts dimension names, and creates a mapping to namespace strings. The
    namespace strings are constructed using the file name and dimension name.

    Parameters:
    safe_path (str): The path to the SAFE directory containing NetCDF files.

    Returns:
    dict[str, str]: A dictionary where keys are in the format "filename:dimension_name"
                    and values are namespace strings in the format "coords:namespace:dimension_name".
    """
    safe = stb.get_universal_path(safe_path)
    nc_data = {}
    ns = {}

    # Iterate over all NetCDF files in the SAFE directory
    for nc_file in safe.rglob("*.nc"):
        path = nc_file.name

        # If the file is not already in the nc_data dictionary, open it and store it (cache)
        if path not in nc_data:
            nc_data[path] = stb.open_datatree(nc_file, decode_cf=False, decode_times=False)

        data = nc_data[path]

        # Iterate over all dimensions in the NetCDF data
        for dim_name in data.dims:
            # dim = getattr(data, str(dim_name))
            ns_name = path.split(".")[0]
            ns[f"{path}:{dim_name}"] = f"coords:{ns_name}:{dim_name}"

    return ns


def _extract_coord() -> None:
    """
    if "/" in dpr_tgt:
        ns = ":".join(dpr_tgt.split("/"))
        print(f"{dpr_tgt!r}:'coords{ns}'")

    """


def extract_mapping_vars(mapping: dict[Hashable, Any]) -> dict[str, str]:
    """

    Example of output
    {
        "/conditions/geometry/altitude": "",
        "/conditions/geometry/oaa": "",
        ...
        "coords:bands": "",
        "coords:bands2": "",
    }

    :param mapping:
    :return:
    """
    d = {}
    for i, map_var in enumerate(mapping.get("data_mapping", [])):
        # src = map_var.get("source_path", "")
        dest = map_var.get("target_path", "")
        d[dest] = ""
    return d


def display_mapping_vars(mapping: dict[Hashable, Any]) -> None:
    """
    Like extract_mapping_vars but print sorted json instead of returning dict

    Example of output
    {
        "/conditions/geometry/altitude": "",
        "/conditions/geometry/oaa": "",
        ...
        "coords:bands": "",
        "coords:bands2": "",
    }

    :param mapping:
    :return:
    """
    d = extract_mapping_vars(mapping)
    print(json.dumps(d, sort_keys=True, indent=2))


########################################################################################################################
# Function to update mapping from ref products
########################################################################################################################


def load_ref_product(ptype: str, cache_dir: Path | str = "~/DATA/Products/") -> DataTree:
    """
    Load a reference product from an S3 bucket with optional local caching.

    Args:
        ptype (str): The product type identifier.
        cache_dir (Optional[Path]): The local directory to cache the product. Defaults to "~/DATA/Products/".

    Returns:
        Any: The opened datatree.
    """
    cache_dir = Path(cache_dir).expanduser().absolute()
    if ptype.startswith("S03"):
        return stb.open_datatree(f"s3://s3-input/Products/{ptype}*.zarr", cache=True, local_copy_dir=cache_dir)
    elif ptype.startswith("S02"):
        return stb.open_datatree(f"s3://s2-input/Products/{ptype}*.zarr", cache=True, local_copy_dir=cache_dir)
    else:
        raise NotImplementedError(ptype)


def load_ref_metadata(ptype: str) -> DataTreeHandler:
    """
    Load reference metadata for a given product type.

    Args:
        ptype (str): The product type identifier.

    Returns:
        DataTreeHandler: DataTreeHandler of a DataTree containing all metadata and fake data
    """
    return PRODUCT[ptype]


def load_mapping(ptype: str) -> dict[str, Any]:
    """
    Load the mapping for a given product type.

    Args:
        ptype (str): The product type identifier, for example "S03OLCEFR"

    Returns:
        dict[str, Any]: The EOPF mapping for this product type.
    """
    processing_versions = {"S03SLSLST": "004", "S03SLSFRP": "001"}
    processing_version = processing_versions.get(ptype, "TODO")
    mapping_path = get_resource_path("legacy_mapping", module="eopf.store").as_posix()
    mf = EOPFMappingFactory(mapping_path=mapping_path)
    mappings = EOPFMappingManager(mf)
    mapping, _ = mappings.parse_mapping(product_type=ptype, processing_version=processing_version)
    if mapping is None:
        raise FileNotFoundError(f"No mapping found for {ptype!r}")
    else:
        return mapping


def build_map_legacy_to_dpr(ptype: str, ref: DataTree | None = None) -> dict[str, str]:
    """
    Build a mapping legacy safe data -> DPR path

    To build this dict, code use 'simplified mapping' and 'remap' data from sentineltoolbox conversion.

    See ...
     - 'simplified mapping': 'sentineltoolbox/conversion/conf/simplified_mappings'
     - 'remap.json': sentineltoolbox/conversion/conf/mappings/remap.json

    For example:
    {
       'geo_coordinates.nc:latitude': '/quality/latitude'
    }

    Args:
        ptype (str): The product type identifier.

    Returns:
        Dict[str, str]: A dictionary mapping legacy paths to DPR paths.
    """
    simp = SIMPLIFIED_MAPPINGS.get(ptype, {})
    remap = REMAP.get(ptype, {})
    simplified_data_mapping = simp.get("data_mapping", {})
    old_eopf_data_mapping = load_mapping(ptype).get("data_mapping", {})

    map_legacy_to_dpr = {}
    for gr_path, legacy_files in simplified_data_mapping.items():
        for legacy_file, variables in legacy_files.items():
            for legacy_name, dpr_name in variables:
                # if "cartesian_an.nc:x_orphan_an"
                src_path = f"{legacy_file}:{legacy_name}"
                target_path = f"{gr_path}/{dpr_name}"

                for d in remap:
                    r = re.search(d, target_path)
                    if r:
                        if r.re.pattern == target_path:
                            target_path = remap[target_path]
                        else:
                            v = target_path.split("/")[-1]
                            target_path = remap[d]
                            l = target_path.split("/")[:-1]  # noqa: E741
                            l.append(v)
                            target_path = "/".join(l)

                if target_path in remap:
                    new_path = remap[target_path]
                    target_path = new_path

                target_path = target_path.replace("meteo/", "meteorology/")
                map_legacy_to_dpr[src_path] = target_path

    for data in old_eopf_data_mapping:
        src_path = data.get("source_path")
        target_path = data.get("target_path")
        if target_path in remap:
            # print(f"{src_path}: {map_legacy_to_dpr.get(src_path, '?')} -> {target_path}")
            map_legacy_to_dpr[src_path] = target_path
        elif src_path not in map_legacy_to_dpr and target_path.split(":")[0] not in ("coords", "attrs"):
            # ignore data in legacy mapping but no more in stb mappings
            pass
        else:
            # do not update because current value is considered more reliable
            pass

    for src_path, target_path in map_legacy_to_dpr.items():
        map_legacy_to_dpr[src_path] = target_path.replace("meteo/", "meteorology/")

    # apply second time remap because some remap information applies on previous dpr map
    for src_path, target_path in map_legacy_to_dpr.items():
        map_legacy_to_dpr[src_path] = remap.get(target_path, target_path)

    # compare with ref
    if ref:
        paths = []
        for subtree in ref.subtree:
            for varname, variable in subtree.data_vars.items():
                varpath = Path(subtree.path, varname).as_posix()
                paths.append(varpath)

        variables = set(paths)
        mapping = set(map_legacy_to_dpr.values())
        print("Variables found in reference product but not in mapping:\n - ", end="")
        print("\n - ".join(variables.difference(mapping)))
    return map_legacy_to_dpr


def build_coord_data(
    ptype: str,
    dpr_coord_namespace: dict[str, str] | None = None,
    map_legacy_to_dpr: dict[str, str] | None = None,
) -> list[tuple[str, str, str | None]]:
    """
    Build coordinate data for a given product type.
    coordinate data is a list of tuple (dpr_path, safe_path, mapping_coord_ns)
    for example:
    ('/measurements/anadir/latitude', 'geodetic_an.nc:latitude_an', 'an')
    if ns is not found or root => ns = None.

    Args:
        ptype (str): The product type identifier.
        safe_product_path (Path|None): The path to the SAFE product. Defaults to None.
    """
    if map_legacy_to_dpr is None:
        map_legacy_to_dpr = load_map_legacy_to_dpr(ptype)

    # dict type of {"cartesian_an.nc:x_orphan_an": "coords:an_orphan:x"}
    if dpr_coord_namespace is None:
        dpr_coord_namespace = DPR_COORD_NAMESPACES.get(ptype, {})

    coord_data = []
    for safe_path, dpr_path in map_legacy_to_dpr.items():
        if safe_path in dpr_coord_namespace:
            tgt = dpr_coord_namespace[safe_path]
            parts = tgt.split(":")
            if len(parts) == 3:
                ns = parts[1]
            else:
                ns = None
            coord_data.append((dpr_path, safe_path, ns))
        else:
            pass
    return coord_data


def increment_var_name(name: str) -> str:
    # Use a regular expression to find the number at the end of the variable name
    match = re.match(r"(.*?)(\d*)$", name)
    if match:
        prefix = match.group(1)
        number = match.group(2)
        if number:
            # If a number is present, increment it
            new_number = str(int(number) + 1)
        else:
            # Otherwise, add '2'
            new_number = "2"
        return prefix + new_number
    else:
        # If no match is found, return the original name with '2'
        return name + "2"


def prefer_new_type(old_type: str, new_type: str) -> bool:
    return True


def update_mapping(
    ptype: str,
    safe_file_path: Path | str | None = None,
    cache_dir: str | Path = "~/DATA/Products",
    **kwargs: Any,
) -> None:
    """
    Updates the mapping for a given product type by processing coordinate
    transformations, variable mappings, and attribute adjustments.

    The function loads an existing mapping, updates coordinate references,
    and adjusts variable attributes such as scale factors, fill values,
    and data types based on a reference datatree.

    :param ptype: The product type identifier (e.g., "S03OLCEFR" or "S02MSIL1C") used to
                  determine the correct reference product and mapping
    :param cache_dir: The local directory where cached product data is stored.
                      Defaults to "~/DATA/Products".

    The function performs the following operations:
    1. Determines the reference product path based on `ptype`.
    2. Attempts to load the product data as a `DataTree`
    3. Retrieves coordinate namespaces and excluded variables for the given `ptype`.
    4. Loads the current mapping
    5. Applies remapping rules, ensuring coordinates and variable paths are correctly
       assigned.
    6. Adjusts transformation attributes such as `scale_factor`, `fill_value`, and
       `dtype` based on configuration options (`scale_factor_mode`, `dtype_mode`, etc.).
    7. Generates an updated mapping and saves it as a new JSON file "mappingname_new.json"

    Configuration Options:

    * scale_factor_mode: Defines how scale_factor and add_offset attributes are handled.
      - "remove": Removes these attributes from all variables.
      - "update": Removes add_offset if 0 and scale_factor if 1 else update with reference product values
      - "ignore": Leaves scale_factor and add_offset unchanged.
    * fill_value_mode: Determines how _FillValue is handled.
      - "update": Updates the fill_value if defined in reference metadata.
      - "ignore": Leaves the fill_value unchanged.
    * dtype_mode: Controls how the dtype of variables is determined.
      - "update-from-array": Uses the actual data type from the loaded reference product.
      - "update-from-metadata": Uses the data type from the reference metadata.
      - "ignore": Leaves dtype unchanged.
    * generation_mode: Defines whether debug metadata is included in mapping
      - "standard": Produces a clean mapping without debug info.
      - "debug": Adds debug metadata in "other_metadata/debug":
        - generator: mapping generation timestamp

    For information, comparison between mapping and equivalent final variable

     Mapping:
     {
         "short_name": "oa01_radiance",
         "transform": {
             "dimensions": ["rows", "columns"],
             "attributes": {
                 "coordinates": "latitude longitude",
                 "dimensions": "rows columns",
                 "dtype": "<u2",
             }
             "mask_and_scale": {
                    "valid_min": -180000000,
                    "fill_value": -2147483648,
                    "valid_max": 180000000,
                    "scale_factor": 1e-06
                },
         },
     }


    xdataarray.attrs:

    {
        "_ARRAY_DIMENSIONS": ["rows", "columns"],
        "coordinates": "time_stamp latitude longitude",
        "short_name": "oa01_radiance",
        "standard_name": "toa_upwelling_spectral_radiance",
        "units": "mW.m-2.sr-1.nm-1",
        "valid_max": 893.550000693649,
        "valid_min": 0.0,
        "_io_config": {
            "scale_factor": 0.013634907081723213,
            "add_offset": 0.0,
            "valid_min": 0,
            "valid_max": 65534,
            "fill_value": 65535,
            "dtype": dtype("uint16"),
        },
        "description": "TOA radiance for OLCI acquisition band oa01",
    }


    xdataarray.encoding

    {"_FillValue": 65535, "scale_factor": 0.013634907081723213, "add_offset": 0.0, "dtype": dtype("uint16")}
    """
    if ptype not in SUPPORTED_MAPPINGS:
        print(f"DO NOT UPDATE MAPPING BECAUSE THIS CODE DO NOT SUPPORT TYPE {ptype!r}")
        return

    mapping_path_dir = get_resource_path("mapping", module="eopf.store")

    # extract update modes
    scale_factor_mode: L_UpdateMappingMode_ScaleFactor = kwargs.get("scale_factor_mode", "update")
    fill_value_mode: L_UpdateMappingMode_FillValue = kwargs.get("fill_value_mode", "update")
    dtype_mode: L_UpdateMappingMode_Dtype = kwargs.get("dtype_mode", "update-from-array")
    generation_mode: Literal["standard", "debug"] = kwargs.get("generation_mode", "debug")

    if dtype_mode == "update-from-safe" and not safe_file_path:
        print("Cannot update dtype from safe type. safe_path is not specified. Ignore dtype change")
        dtype_mode = "ignore"

    # Open reference products
    cache_dir = Path(cache_dir).expanduser()
    if ptype.startswith("S03"):
        ref_prod_path = f"s3://s3-input/Products/{ptype}*.zarr"
    elif ptype.startswith("S02"):
        ref_prod_path = f"s3://s2-input/Products/{ptype}*.zarr"
    else:
        ref_prod_path = "XXXXX"

    try:
        print("Load", ref_prod_path)
        full_prod = stb.open_datatree(ref_prod_path, cache=True, local_copy_dir=cache_dir)
        # full_prod_raw = stb.open_datatree(ref_prod_path, cache=True, local_copy_dir=cache_dir, decode_cf=False)
    except FileNotFoundError:
        full_prod = None
        # full_prod_raw = None

    # get "dpr targets", "ignore list" and official "mapping" for this ptype
    dpr_coord_namespace = DPR_COORD_NAMESPACES.get(ptype, {})
    remove_var_list = REMOVE_VARIABLES.get(ptype, [])
    coord_mapping = COORD_MAPPINGS.get(ptype, {})
    dims_mapping = DIMS_MAPPINGS.get(ptype, {})
    coord_lut = COORD_LUT.get(ptype, {})
    force_target_dtype = FORCE_TARGET_DTYPE.get(ptype, {})
    force_attrs = FORCE_ATTRS.get(ptype, {})

    short_names = {}

    try:
        missing_data = load_resource_file(f"mappings/{ptype}_missing_data.json", module="sentineltoolbox.conversion")
    except FileNotFoundError:
        missing_data = {}

    try:
        ref_product: DataTree | None = PRODUCT[ptype]
    except KeyError:
        ref_product = None

    # Generate equivalence map "legacy path" -> "reference product path" using simplified mappings.
    map_legacy_to_dpr = load_map_legacy_to_dpr(ptype)
    map_dpr_to_legacy = {v: k for k, v in map_legacy_to_dpr.items()}

    # map_legacy_to_dpr_path = mapping_path_dir / "definition" / f"{ptype}_path_map.json"
    # map_legacy_to_dpr_path.parent.mkdir(exist_ok=True, parents=True)
    # with open(map_legacy_to_dpr_path, "w") as json_fp:
    #    json.dump(map_legacy_to_dpr, json_fp, indent=4, cls=DataTreeJSONEncoder, sort_keys=True)

    # load raw mapping where chunks and variables are not "unrolled"
    raw_mapping = load_resource_file(
        f"{ptype}.json",
        module=kwargs.get("input_mapping_module", "eopf.store.legacy_mapping"),
    )

    RTOL = 1e-8
    ATOL = 1e-8
    original_data_mapping = raw_mapping.get("data_mapping", [])

    new_data_mapping = []
    new_data_paths = []

    coord_data = build_coord_data(ptype, dpr_coord_namespace=dpr_coord_namespace, map_legacy_to_dpr=map_legacy_to_dpr)
    dpr_path_to_ns: dict[str, str | None] = {}
    # build simple dict dpr_path -> ns. Also include parents:
    # For example {'/measurements/anadir/latitude': 'an'}
    for dpr_path, safe_path, ns in coord_data:
        dpr_path_to_ns[dpr_path] = ns

    for dpr_path, ns in coord_lut.items():
        dpr_path_to_ns[dpr_path] = ns

    done = []
    dimension_set = set()
    for original_data in original_data_mapping:
        data = copy.copy(original_data)
        # 'target_path': 'coords:rows', 'source_path': 'geo_coordinates.nc:rows'

        # extract dpr path associated to legacy path. If not found use mapping original data (map_tgt)
        src = data.get("source_path")
        map_tgt = data.get("target_path")

        # "time_coordinates.nc:time_stamp": "/conditions/time/time_stamp"
        # before it was coords:time_stamp

        dpr_tgt = map_legacy_to_dpr.get(src, map_tgt)

        if src in dpr_coord_namespace:
            dpr_tgt = dpr_coord_namespace[src]
            print(f"[variable] {src} -> {dpr_tgt}")
            if not map_tgt.startswith("coords:"):
                print(f"  [variable->coord] {src} -> {dpr_tgt}: old variable {map_tgt} is now a coordinate")
        else:
            print(f"[variable] {src} -> {dpr_tgt}")
            if map_tgt.startswith("coords:"):
                print(f"  [coord->variable] {src} -> {dpr_tgt}: old coordinate {map_tgt} is now a variable")

        if src not in map_legacy_to_dpr:
            if not dpr_tgt.startswith("attrs:") and not dpr_tgt.startswith("coords:"):
                print(f"  [REMOVE] {src} -> None: remove old variable {map_tgt}")
                continue

        ignore_var = False
        increment = False
        if dpr_tgt in done:
            # remove duplicate variables ...
            ignore_var = True

            # except for metadata / stac_discovery: keep duplicated for the moment
            for name in ("attrs:/:stac_discovery", "attrs:/:other_metadata"):
                if name in dpr_tgt:
                    increment = False
                    ignore_var = False
                    break

            # for bands, increment names
            for name in ("bands",):
                if name in dpr_tgt:
                    increment = True
                    ignore_var = False

        if ignore_var:
            continue

        if increment:
            while dpr_tgt in done:
                dpr_tgt = increment_var_name(dpr_tgt)

        done.append(dpr_tgt)
        data["target_path"] = dpr_tgt

        # FIX DTYPE
        dtype_str = data.get("transform", {}).get("attributes", {}).get("dtype")
        if isinstance(dtype_str, str) and dtype_str.startswith("<M4"):
            dtype_str = dtype_str.replace("<M4", "<M8")
            data["transform"]["attributes"]["dtype"] = dtype_str
        if force_target_dtype.get(dpr_tgt):
            dtype_str = force_target_dtype.get(dpr_tgt)
            forced_dtype = np.dtype(dtype_str).str.replace("|", "<")
            data["transform"].setdefault("attributes", {})["dtype"] = forced_dtype
            data["transform"].setdefault("mask_and_scale", {})["eopf_target_dtype"] = forced_dtype
            fill_value = DEFAULT_FILL_VALUE.get(dtype_str)
            if fill_value:
                data["transform"].setdefault("mask_and_scale", {})["fill_value"] = fill_value

            print(f"  [force_type] {src} -> {dpr_tgt}: force to dtype {forced_dtype}")

        # Force attributes
        if dpr_tgt in force_attrs:
            for attr_key, attr_value in force_attrs[dpr_tgt].items():
                data["transform"]["attributes"][attr_key] = attr_value
                print(f"  [force_attr] {src} -> {dpr_tgt}: force attr {attr_key!r} to {attr_value!r}")

        reference_variable: DataArray | None = None
        io = {}
        var_prod: DataArray | None = None
        # tries to load reference variable from zarr reference product.
        if isinstance(full_prod, DataTree) and ref_product:
            try:
                reference_variable = get_array(ref_product, dpr_tgt)
                var_prod = get_array(full_prod, dpr_tgt)
            except KeyError:
                reference_variable = None
            else:
                io = reference_variable.attrs.get("_io_config", reference_variable.attrs)

        # if not reference variable, for example for some coord or missing samples,
        # tries to load from netcdf file.
        if not reference_variable and safe_file_path and ":" in src:
            netcdf_file_name, netcdf_var_name = src.split(":")
            if netcdf_file_name.endswith(".nc"):
                netcdf_path = Path(safe_file_path) / netcdf_file_name

                netcdf_ds = xarray.open_dataset(netcdf_path)
                reference_variable = getattr(netcdf_ds, netcdf_var_name)
                var_prod = reference_variable

                netcdf_ds = xarray.open_dataset(netcdf_path, decode_cf=False)
                reference_variable_encoded = getattr(netcdf_ds, netcdf_var_name)
                io = reference_variable_encoded.attrs

        if reference_variable is not None and var_prod is not None:

            ########################################################################################################
            # UPDATE COORDINATES
            ########################################################################################################
            coordinates, use_ns = extract_ns_and_coords(coord_mapping, data, dpr_path_to_ns, dpr_tgt, var_prod)

            # if current variable is a real variable (not a coordinate), update coordinates to match ref coordinates.
            # for example coordinate "latitude_an longitude_an" -> "latitude longitude" because now namespace is
            # used to differentiate latitude_an and latitude (coords:an:latitude vs coords:latitude for example)
            if coordinates and not data["target_path"].startswith("coords:"):
                coordinates_str = " ".join([c.split(":")[-1] for c in coordinates])
                data.setdefault("transform", {}).setdefault("attributes", {})["coordinates"] = coordinates_str

            # if use_ns, specify it in mapping, else remove coords_namespace information
            if use_ns:
                data["coords_namespace"] = use_ns
                print(f"  [ns] {src} -> {dpr_tgt}: now use coord namespace {use_ns}")
            else:
                try:
                    del data["coords_namespace"]
                except KeyError:
                    pass
                else:
                    print(f"  [ns] {src} -> {dpr_tgt}: remove coord namespace")
            # extract coordinates for this variable from ref product

            ########################################################################################################
            # UPDATE DIMENSIONS
            ########################################################################################################
            map_dims = data.get("transform", {}).get("dimensions")  # .get("eopf", [])
            if isinstance(map_dims, dict):
                map_dims_eopf = map_dims.get("eopf")
                if map_dims_eopf:
                    new_dims = [dims_mapping.get(dim_name, dim_name) for dim_name in map_dims_eopf]
                    if new_dims != map_dims_eopf:
                        print(f"  [dims] {src} -> {dpr_tgt}: {map_dims_eopf} -> {new_dims}")
                        data["transform"]["dimensions"]["eopf"] = new_dims
            # {"transform": {"dimensions": {"eopf": ["rows_in", "columns_in"], "safe": ["rows", "columns"]}}}

            ########################################################################################################
            # UPDATE Attributes
            ########################################################################################################
            ref_attrs = var_prod.attrs
            map_attrs = data.get("transform", {}).get("attributes", {})
            old_short_name = data.get("short_name")
            short_name = old_short_name

            for ref_attr_name, ref_attr in ref_attrs.items():
                map_attr = map_attrs.get(ref_attr_name)
                if isinstance(ref_attr, np.ndarray):
                    ref_attr = ref_attr.tolist()
                try:
                    differ = map_attr != ref_attr
                    if differ:  # force evaluation with this line
                        pass
                except ValueError:
                    print(
                        f"  [ERROR] {src} -> {dpr_tgt}: attrs {ref_attr_name} cannot be compared. "
                        f"mapping:{type(map_attr)}, ref:{type(ref_attr)}",
                    )
                    differ = False

                if differ:
                    if ref_attr_name == "long_name" and map_attr:
                        # replace long_name only if not defined because mapping name is considered more up-to-date
                        continue
                    if ref_attr_name in ("valid_min", "valid_max"):
                        # this information is already in transform bloc, ignore it
                        continue
                    if ref_attr_name == "short_name":
                        # add short_name to the right place then continue
                        short_name = ref_attr
                        continue

                    print(f"  [attrs] {src} -> {dpr_tgt}: {ref_attr_name} updated. -> {map_attr!r} -> {ref_attr!r}")
                    map_attrs[ref_attr_name] = ref_attr

                if ref_attr_name == "flag_meanings":
                    if isinstance(ref_attr, str):
                        map_attrs[ref_attr_name] = ref_attr.lower()
                    elif isinstance(ref_attr, list):
                        map_attrs[ref_attr_name] = " ".join([str(flag).lower() for flag in ref_attr])

            if short_name:
                short_names[dpr_tgt] = short_name
                if not old_short_name:
                    data["short_name"] = short_name
                    print(f"  [shortname] {src} -> {dpr_tgt}: add new short_name {short_name}")

            ########################################################################################################
            # UPDATE TRANSFORMATIONS
            ########################################################################################################

            # SCALE FACTOR / ADD_OFFSET ----------------------------------------
            scale_factor = io.get("scale_factor")
            add_offset = io.get("add_offset")

            is_default_scale_factor = scale_factor is not None and numpy.isclose(scale_factor, 1, rtol=RTOL, atol=ATOL)
            is_default_add_offset = add_offset is not None and numpy.isclose(add_offset, 0, rtol=RTOL, atol=ATOL)

            is_scale_factor_defined = (
                data.get("transform", {}).get("mask_and_scale", {}).get("scale_factor") is not None
            )
            is_add_offset_defined = data.get("transform", {}).get("mask_and_scale", {}).get("add_offset") is not None

            if scale_factor_mode == "remove":
                # see https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/547
                # REMOVE ALL add_offset and scale_factor of all variables
                if is_default_add_offset:
                    try:
                        del data["transform"]["mask_and_scale"]["add_offset"]
                    except KeyError:
                        pass
                    continue
                if is_default_scale_factor:
                    try:
                        del data["transform"]["mask_and_scale"]["scale_factor"]
                    except KeyError:
                        pass
                    else:
                        print(f"  [mask_and_scale] {src} -> {dpr_tgt}: remove scale_factor")
                    continue
            elif scale_factor_mode == "update":
                # REMOVE add_offset==0 and scale_factor==1
                if is_scale_factor_defined:
                    data["transform"].setdefault("mask_and_scale", {})["scale_factor"] = "from_legacy_attr:scale_factor"
                    print(f"  [mask_and_scale] {src} -> {dpr_tgt}: load scale_factor from legacy")
                if is_add_offset_defined:
                    data["transform"].setdefault("mask_and_scale", {})["add_offset"] = "from_legacy_attr:add_offset"
                    print(f"  [mask_and_scale] {src} -> {dpr_tgt}: load add_offset from legacy")

            for field in (
                "valid_min",
                "valid_max",
                "fill_value",
            ):
                if field in io:
                    value = io[field]
                    # FILL VALUE ------------------------------------------
                    if field == "fill_value" and (value is numpy.nan or fill_value_mode == "ignore"):
                        continue
                    else:
                        data.setdefault("transform", {}).setdefault("mask_and_scale", {})[field] = value

            # attributes / target_dtype

            # STORAGE / TARGET DTYPE ------------------------------------------
            dtype_str = data.get("transform", {}).get("attributes", {}).get("dtype")
            try:
                storage_type = np.dtype(dtype_str)
            except TypeError:
                print(f"{data['target_path']}: type {dtype_str!r} not supported")
                storage_type = None
            if dtype_mode == "update-from-metadata":
                # use metadata value
                io_dtype = io.get("dtype")
                if io_dtype is None:
                    variable_dtype: DTypeLike | None = None
                else:
                    variable_dtype = np.dtype(io_dtype)
            elif dtype_mode == "update-from-array":
                # use ref product array dtype
                variable_dtype = var_prod.dtype
            elif dtype_mode == "update-from-safe" and safe_file_path:
                netcdf_file_name, netcdf_var_name = src.split(":")
                netcdf_path = Path(safe_file_path) / netcdf_file_name
                print(f"  [netcdf] load netcdf {netcdf_path}:{netcdf_var_name}")
                netcdf_ds = xarray.open_dataset(netcdf_path)
                variable_dtype = getattr(netcdf_ds, netcdf_var_name).dtype
                netcdf_ds = xarray.open_dataset(netcdf_path, decode_cf=False)
                storage_type = getattr(netcdf_ds, netcdf_var_name).dtype
            else:
                variable_dtype = None

            # FIX DTYPE
            if storage_type:
                storage_type_str = storage_type.str.replace("|", "<")
                if storage_type_str != dtype_str and prefer_new_type(dtype_str, storage_type_str):
                    data.setdefault("transform", {}).setdefault("attributes", {})["dtype"] = storage_type_str
                    print(f"  [dtype] {src} -> {dpr_tgt}: force to dtype={storage_type_str}")

            # FIX TARGET TYPE
            fix_target_type = False
            if variable_dtype is not None and variable_dtype != storage_type:
                fix_target_type = True
            if force_target_dtype.get(dpr_tgt):
                fix_target_type = False  # already done!

            if fix_target_type and variable_dtype is not None:
                variable_dtype_str = np.dtype(variable_dtype).str.replace("|", "<")
                data.setdefault("transform", {}).setdefault("mask_and_scale", {})[
                    "eopf_target_dtype"
                ] = variable_dtype_str
                print(f"  [mask_and_scale] {src} -> {dpr_tgt}: force to target_dtype={variable_dtype_str}")

        ########################################################################################################
        # Remove attributes
        ########################################################################################################

        for map_block in ("attributes", "mask_and_scale"):
            for attr_name in ("dimensions", "target_dtype", "_FillValue"):
                try:
                    del data["transform"][map_block][attr_name]
                except KeyError:
                    pass
                else:
                    print(f"  [attrs] {src} -> {dpr_tgt}: remove transform/{map_block}/{attr_name}")

                try:
                    del data[map_block][attr_name]
                except KeyError:
                    pass
                else:
                    print(f"  [attrs] {src} -> {dpr_tgt}: remove {map_block}/{attr_name}")

        dtype = data.get("transform", {}).get("attributes", {}).get("dtype")
        unit = data.get("transform", {}).get("attributes", {}).get("units")
        if unit:
            if dtype and dtype.startswith("<M8"):
                data["transform"]["attributes"]["data_units"] = "from_legacy_attr:units"
            else:
                data["transform"]["attributes"]["data_units"] = unit
            del data["transform"]["attributes"]["units"]

        ####
        dimension_set.update(extract_dimensions(data))

        dpr_tgt = data["target_path"]
        if dpr_tgt not in remove_var_list:
            new_data_mapping.append(data)
            new_data_paths.append(dpr_tgt)

    ########################################################################################################
    # Update chunks
    ########################################################################################################

    chunk_sizes = raw_mapping.get("chunk_sizes", {})
    for dim_name in dimension_set:
        if dim_name not in chunk_sizes:
            chunk_sizes[dim_name] = DEFAULT_CHUNK_SIZES.get(dim_name, 1024)
    raw_mapping["chunk_sizes"] = chunk_sizes

    if isinstance(full_prod, DataTree) and ref_product:
        missing_data = {}
        for gr in full_prod.subtree:
            for varname, variable in gr.data_vars.items():
                varpath = gr.path + "/" + varname
                if varpath not in new_data_paths:
                    variable_metadata = ref_product[varpath]

                    data = {
                        "target_path": varpath,
                        "source_path": map_dpr_to_legacy.get(varpath, "TODO"),
                        "accessor_id": "netcdf",
                        "transform": {
                            "dimensions": variable_metadata.attrs.get("_ARRAY_DIMENSIONS", []),
                            "mask_and_scale": variable_metadata.attrs.get("_io_config", {}),
                            "attributes": variable.attrs,
                            "rechunk": "@#copy{'map':'<SELF[chunk_sizes]>'}#@",
                        },
                        "coords_namespace": "TODO",
                    }

                    coordinates, use_ns = extract_ns_and_coords(coord_mapping, data, dpr_path_to_ns, varpath, variable)
                    if use_ns:
                        data["coords_namespace"] = use_ns
                    else:
                        del data["coords_namespace"]
                    if coordinates:
                        data["attributes"]["coordinates"] = coordinates

                    missing_data[varpath] = data

        if missing_data:
            missing_data_path = f"{ptype}_missing_data.json"
            print("[MISSING DATA] Some data found in reference product are missing in mapping")
            print(f"[MISSING DATA]You can found first draft for this data in {missing_data_path}")
            with open(missing_data_path, "w") as fp:
                json.dump(missing_data, fp, indent=2, cls=DataTreeJSONEncoder, sort_keys=True)

    raw_mapping["data_mapping"] = new_data_mapping
    raw_mapping["stac_discovery"]["properties"]["mission"] = "Text(copernicus)"
    raw_mapping["stac_discovery"]["properties"]["constellation"] = f"Text(sentinel-{ptype[2]})"
    raw_mapping["stac_discovery"]["stac_version"] = "Text(1.1.0)"

    # TODO: fix short names!
    for path, short_name in short_names.items():
        print(short_name, "->", path)

    # DEBUG INFORMATION ------------------------------------------
    if generation_mode == "debug":
        raw_mapping.setdefault("other_metadata", {}).setdefault("debug", {})[
            "generator"
        ] = f"Text(mapping '{datetime.now()}')"
        raw_mapping.setdefault("other_metadata", {})["safe_dpr_equivalence"] = map_legacy_to_dpr

    mapping_path = mapping_path_dir / f"{ptype}.json"
    with open(mapping_path, "w") as json_fp:
        json.dump(raw_mapping, json_fp, indent=4, cls=DataTreeJSONEncoder)


def extract_dimensions(data):
    dims = data.get("transform", {}).get("dimensions")
    if isinstance(dims, dict):
        dims = dims.get("eopf", [])
    elif isinstance(dims, (list, tuple)):
        pass
    elif isinstance(dims, str):
        dims = [dims]
    else:
        dims = []
    return dims


def extract_ns_and_coords(
    coord_mapping: dict[str, str],
    data: dict[str, Any],
    dpr_path_to_ns: dict[str, str | None],
    dpr_tgt: str | Path,
    var_prod: DataArray,
) -> tuple[list[str], str | None]:
    use_ns: Any = ""
    coordinates: list[str] = []
    # dpr_tgt "/measurements/anadir/s1_radiance"
    # dpr_tgt_parent "/measurements/anadir"
    dpr_tgt_parent = Path(dpr_tgt).parent.as_posix()
    coord_paths = set()
    coord_names = set()
    for coord_name, coord in var_prod.coords.items():
        coord_name = str(coord_name)
        coord_names.add(coord_name)
    for coord_name in data.get("transform", {}).get("attributes", {}).get("coordinates", "").split(" "):
        if coord_name:
            coord_names.add(str(coord_name))
    for coord_name in coord_names:
        # /measurements/anadir/latitude_an
        ref_coord_path_orig = f"{dpr_tgt_parent}/{coord_name}"

        # /measurements/anadir/latitude
        ref_coord_path_new = f"{dpr_tgt_parent}/{coord_mapping.get(coord_name, coord_name)}"

        coord_paths.add(ref_coord_path_orig)
        coord_paths.add(ref_coord_path_new)

    for dim_name in extract_dimensions(data):
        coord_paths.add(f"{dpr_tgt_parent}/{dim_name}")

    for coord_path in coord_paths:
        use_ns = dpr_path_to_ns.get(coord_path)
        if use_ns:
            break
    return coordinates, use_ns


def update_legacy_to_dpr(ptype: str, ref: DataTree | None = None) -> dict[str, str]:
    """
    Generate a new  legacy_to_dpr_product_map and save it in the right directory.

    legacy_to_dpr_product_map is a dict "legacy path" -> "dpr path":
    {
      "Oa01_radiance.nc:Oa01_radiance": "/measurements/oa01_radiance"
    }


    :param ptype:
    :param ref:
    :return:
    """
    # read stb converters simplified mappings and remap to generate new legacy_to_dpr_product_map
    legacy_to_dpr = build_map_legacy_to_dpr(ptype, ref)

    # build path to legacy_to_dpr_product_map json file
    legacy_to_dpr_path = get_resource_path("mappings", module="sentineltoolbox.conversion") / f"{ptype}.json"

    # write/erase legacy_to_dpr_product_map json file
    with open(legacy_to_dpr_path, "w") as fp:
        json.dump(legacy_to_dpr, fp, sort_keys=True, indent=2)
    return legacy_to_dpr


def update_derivated_mappings(ptype: str) -> None:
    if ptype in ("S03OLCLFR", "S02MSIL1C", "S02MSIL2A"):

        mapping_ref_name = f"{ptype}.json"
        mapping_path_dir = get_resource_path("mapping", module="eopf.store")
        reference_mapping_path = mapping_path_dir / mapping_ref_name

        # reference_json = load_resource_file(mapping_ref_name, module="eopf.store.mapping")
        with open(reference_mapping_path, "r") as fp:
            reference_content = fp.read()

        if ptype == "S03OLCLFR":
            derivated_mapping_path = mapping_path_dir / "S03OLCLRR.json"
            with open(derivated_mapping_path, "w") as fp:
                fp.write(reference_content.replace("LFR", "LRR"))
            print(f"Generate '{derivated_mapping_path}' mapping from '{mapping_ref_name}' mapping")

        elif ptype in ("S02MSIL1C", "S02MSIL2A"):
            derivated_mapping_path = mapping_path_dir / f"{ptype}_PSD15.json"
            reference_content = reference_content.replace(
                "https://psd-14.sentinel2.eo.esa.int/",
                "https://psd-15.sentinel2.eo.esa.int/",
            )
            reference_content = reference_content.replace("rec_S02MSIL1C_PSD14", "rec_S02MSIL1C_PSD15")
            reference_content = reference_content.replace("rec_S02MSIL2A_PSD14", "rec_S02MSIL2A_PSD15")
            reference_content = reference_content.replace(
                '"processing_version": "04.00"',
                '"processing_version": "05.00"',
            )
            with open(derivated_mapping_path, "w") as fp:
                fp.write(reference_content)

            print(f"Generate '{derivated_mapping_path}' mapping from '{mapping_ref_name}' mapping")


if __name__ == "__main__":

    # /!\ WARNING /!\
    # this script cache products in ~/DATA/Products
    # PLEASE REMOVE MANUALLY CACHED PRODUCT IF YOU UPLOAD A NEW PRODUCT TO BUCKET

    conf_scale_factor_mode: L_UpdateMappingMode_ScaleFactor = "update"
    conf_fill_value_mode: L_UpdateMappingMode_FillValue = "update"
    conf_dtype_mode: L_UpdateMappingMode_Dtype = "update-from-safe"
    conf_generation_mode: L_UpdateMappingMode_DebugLevel = "standard"

    modes = dict(
        scale_factor_mode=conf_scale_factor_mode,
        fill_value_mode=conf_fill_value_mode,
        dtype_mode=conf_dtype_mode,
        generation_mode=conf_generation_mode,
    )

    ptype = sys.argv[1]
    try:
        safe_path: str | None = sys.argv[2]
    except IndexError:
        safe_path = None

    r"""
    # /!\ WARNING /!\
    Uncomment this block ONLY IF you want to generate a new simplified mapping in
    "sentineltoolbox/conversion/mappings".
    DO NOT OVERWRITE EXISING MAPPING because it may have been manually modified by a developer.
    These mapping are used by update_mappings.py.
    See update_legacy_to_dpr

    try:
        ref = load_ref_product(ptype)
    except FileNotFoundError:
        ref = None
    update_legacy_to_dpr(ptype, ref)
    """
    # build new mapping from legacy mapping
    input_mapping_module = "eopf.store.legacy_mapping"

    # update current mapping
    input_mapping_module = "eopf.store.mapping"

    update_mapping(ptype, safe_path, input_mapping_module=input_mapping_module, **modes)
    update_derivated_mappings(ptype)
