from typing import Literal, TypeAlias, get_args

from xarray import DataTree

ProcessingUnitProducts: TypeAlias = dict[str, DataTree]  # 2.3.0

DetectorIdType = Literal[
    "d01",
    "d02",
    "d03",
    "d04",
    "d05",
    "d06",
    "d07",
    "d08",
    "d09",
    "d10",
    "d11",
    "d12",
]

BandNameType = Literal[
    "b01",
    "b02",
    "b03",
    "b04",
    "b05",
    "b06",
    "b07",
    "b08",
    "b8a",
    "b09",
    "b10",
    "b11",
    "b12",
]

SensorGeometryVariableNameType = Literal["act", "alt", "img", "msk", "lat", "lon", "mask"]

ResolutionType = Literal[10, 20, 60]

BandNameToResolutionMapping: dict[BandNameType, ResolutionType] = {
    "b01": 60,
    "b02": 10,
    "b03": 10,
    "b04": 10,
    "b05": 20,
    "b06": 20,
    "b07": 20,
    "b08": 10,
    "b8a": 20,
    "b09": 60,
    "b10": 60,
    "b11": 20,
    "b12": 20,
}

# Define the band across satellite track per detector dimension type for L1A products
ACTDimensionsL1AType = Literal[1296, 2592]
# The bands across satellite track per detector dimension for L1A products
ACT_DIMENSIONS_L1A: dict[BandNameType, ACTDimensionsL1AType] = {
    "b01": 1296,
    "b02": 2592,
    "b03": 2592,
    "b04": 2592,
    "b05": 1296,
    "b06": 1296,
    "b07": 1296,
    "b08": 2592,
    "b8a": 1296,
    "b09": 1296,
    "b10": 1296,
    "b11": 1296,
    "b12": 1296,
}
# Define the band across satellite track per detector dimension type for L1B products
ACTDimensionsL1BType = Literal[425, 1276, 2552]
# The bands across satellite track per detector dimension for L1B products
ACT_DIMENSIONS_L1B: dict[BandNameType, ACTDimensionsL1BType] = {
    "b01": 425,
    "b02": 2552,
    "b03": 2552,
    "b04": 2552,
    "b05": 1276,
    "b06": 1276,
    "b07": 1276,
    "b08": 2552,
    "b8a": 1276,
    "b09": 425,
    "b10": 425,
    "b11": 1276,
    "b12": 1276,
}

# Define the along satellite track chuck size type (the size is that of a legacy Granule: one scene ~ 3.6 sec)
ALTChunkSizeType = Literal[384, 1152, 2304]
# The bands along satellite track chunk sizes
ALT_CHUNK_SIZES: dict[BandNameType, ALTChunkSizeType] = {
    "b01": 384,
    "b02": 2304,
    "b03": 2304,
    "b04": 2304,
    "b05": 1152,
    "b06": 1152,
    "b07": 1152,
    "b08": 2304,
    "b8a": 1152,
    "b09": 384,
    "b10": 384,
    "b11": 1152,
    "b12": 1152,
}

DETECTOR_IDS = tuple(get_args(DetectorIdType))
BAND_NAMES = tuple(get_args(BandNameType))
SENSOR_GEOMETRY_VARIABLE_NAMES = tuple(get_args(SensorGeometryVariableNameType))

RESOLUTIONS = tuple(get_args(ResolutionType))

band_name_to_band_id = {band_name: BAND_NAMES.index(band_name) for band_name in BAND_NAMES}

# Define TDI acceptable types
TdiType = Literal["no_tdi", "applied", "line_a", "line_b"]

# Define DEM acceptable types
DEMType = Literal["GETAS", "DEM90", "DEM30"]

# Define SAD acceptable IDs
SadIdType = Literal[
    "s09123",
    "s11105",
    "s11106",
    "s11107",
    "s11108",
    "s11109",
    "s11110",
    "s11111",
    "s11112",
    "s11113",
    "s11114",
    "s11115",
    "s11116",
    "s11117",
    "s11118",
    "s11119",
    "s11120",
    "s11121",
    "s11122",
    "s11123",
    "s11124",
    "s11125",
    "s11126",
    "s37105",
    "s38105",
    "s39105",
    "s48218",
    "s48223",
    "s48224",
    "s48225",
    "s48226",
    "s48227",
]


LevelOfDetailType = Literal["prod", "dependency", "debug", "notset"]
LevelOfDetailPriorityConfig: dict[LevelOfDetailType, int] = {
    "notset": 0,  # should theoretically act as a dry run
    "debug": 10,  # only for debug purposes
    "dependency": 30,  # intermediate products required by other processing units
    "prod": 50,
}


def get_active_level_of_details(level_of_detail: LevelOfDetailType) -> dict[LevelOfDetailType, bool]:
    """Get a dict mapping a level of detail to its activation or not.

    Parameters
    ----------
    level_of_detail
        Desired minimal level of detail (inclusive)

    Returns
    -------
        Dict of level of detail to activated (True) or disabled (False)
    """

    return _get_active_level_of_details(level_of_detail, LevelOfDetailPriorityConfig)


def _get_active_level_of_details(
    level_of_detail: LevelOfDetailType,
    lod_priority_config: dict[LevelOfDetailType, int],
) -> dict[LevelOfDetailType, bool]:
    """Get a dict mapping a level of detail to its activation or not.

    Parameters
    ----------
    level_of_detail
        Desired minimal level of detail (inclusive)
    lod_priority_config
        Dict of level of detail name to priority

    Returns
    -------
        Dict of level of detail to activated (True) or disabled (False)
    """

    return {k: v >= lod_priority_config[level_of_detail] for k, v in lod_priority_config.items()}
