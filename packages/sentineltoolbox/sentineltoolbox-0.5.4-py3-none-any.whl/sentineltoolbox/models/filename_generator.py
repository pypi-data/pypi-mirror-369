import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path, PurePosixPath
from string import ascii_letters
from typing import Any, Callable, Hashable, MutableMapping

from sentineltoolbox.exceptions import (
    DataSemanticConversionError,
    MultipleDataSemanticConversionError,
)
from sentineltoolbox.models.dpr_product_name import SentinelProductNameDefinition
from sentineltoolbox.typedefs import (
    DATE_FORMAT,
    FileNameGenerator,
    L_DataFileNamePattern,
    T_DateTime,
    T_TimeDelta,
    fix_datetime,
    fix_timedelta,
)

from .s2_legacy_pdi_filename import PDILogicalFilename
from .s2_legacy_product_name import S2MSIL1CProductURI

__all__ = ["detect_filename_pattern", "FileNameGenerator"]


logger = logging.getLogger("sentineltoolbox")

"""

# OL = OLCI
# SL = SLSTR
# SR = SRAL
# DO = DORIS
# MW = MWR
# GN = GNSS
# SY = Instruments Synergy
# TM = telemetry data (e.g. HKTM, navigation, attitude, time)
# AX = for multi instrument auxiliary data


Generating Centres for the Instrument data products:
LN1 = Land OLCI Processing and Archiving Centre
LN2 = Land SLSTR and SYN Processing and Archiving Centre
LN3 = Land Surface Topography Mission Processing and Archiving Centre
MAR = Marine Processing and Archiving Centre
SVL = Svalbard Satellite Core Ground Station
Generating Centres for the Auxiliary data file:
The list is not exhaustive
ECW = ECMWF
EUM = EUMETSAT
SVL = Svalbard Satellite Core Ground Station
MPC = ESA’s Mission Performance Coordinating Centre
POD = Offline POD Service
CNE = CNES SALP service
MSL = Mullard Space Science Laboratory
"""

S1_BEAM_IDENTIFIERS = [
    "S1",
    "S2",
    "S3",
    "S4",
    "S5",
    "S6",
    "IW",
    "EW",
    "WV",
    "EN",
    "N1",
    "N2",
    "N3",
    "N4",
    "N5",
    "N6",
    "Z1",
    "Z2",
    "Z3",
    "Z4",
    "Z5",
    "Z6",
    "ZI",
    "ZE",
    "ZW",
    "GP",
]

S1_PRODUCT_TYPE = ["RAW", "SLC", "GRD", "OCN", "ETA"]

S1_RESOLUTION_CLASS = ["F", "H", "M", "_"]  # Full resolution  # High resolution  # Medium resolution  # Not applicable

S1_PROCESSING_LEVEL = ["0", "1", "2", "A"]  # Level-0  # Level-1  # Level-2  # ETAD product

S1_PRODUCT_CLASS = ["S", "A", "N", "C", "X"]  # SAR Standard  # Annotation  # Noise  # Calibration  # ETAD product

S1_POLARISATION = [
    "SH",  # Single HH
    "SV",  # Single VV
    "DH",  # Dual HH/HV
    "DV",  # Dual VV/VH
    "HH",  # Partial Dual, HH Only
    "HV",  # Partial Dual, HV Only
    "VV",  # Partial Dual, VV Only
    "VH",  # Partial Dual, VH Only
]

RE_PATTERNS = dict(
    s1_BB=r"(?:%s)" % "|".join(S1_BEAM_IDENTIFIERS),
    s1_TTT=r"(?:%s)" % "|".join(S1_PRODUCT_TYPE),
    s1_M=r"(?:%s|_)" % "|".join(S1_RESOLUTION_CLASS),
    s1_L=r"(?:%s|_)" % "|".join(S1_PROCESSING_LEVEL),
    s1_C=r"(?:%s|_)" % "|".join(S1_PRODUCT_CLASS),
    s1_P=r"(?:%s|__)" % "|".join(S1_POLARISATION),
    ext_L=r"(?:\.SAFE|\.SEN3)",  # .SAFE
    ext=r"(?:\.zarr\.zip|\.zarr|\.json\.zip|\.json)",  # .zarr.zip
    mission2=r"S[0-9]{2}",  # S03
    mission1=r"S[0-9]{1}",  # S3
    mission=r"S[0-9]{1,2}",  # S3, S03
    platform=r"[A-Z_]",  # A, _
    level=r"(?:0|1|2)",  # 1
    level_L=r"(?:0|1|2|_)",  # 1
    level_S2=r"L[1-2][A-C]",  # L1C
    sensor=r"[A-Z]{3}",  # OLC, MSI, SLS
    sensor_S3L=r"(?:OL|SL|SR|DO|MW|GN|SY|TM)",  # OL
    sensor_S3ADFL=r"(?:OL|SL|SR|DO|MW|GN|SY|TM|AX)",  # OL
    sensor_S2L=r"(?:)",  # ??
    prod_S3L=r"[A-Z0-9_]{6}",  # EFR___, CR0___, LFR_BW,
    adf_S3L=r"[A-Z0-9_]{4}AX",  # CLUTAX, CLM_AX
    adf_semantic=r"[A-Z]{5}",  # OLINS
    prod=r"[A-Z0-9_]{3}",  # EFR, CR0, L0_
    date=r"[0-9]{8}T[0-9]{6,8}",  # 20160216T000000,
    duration=r"[0-9]{4}",  # 0180, 9999 if duration is longer
    cycle=r"[0-9]{3}",
    orbit=r"[0-9]{3}",
    consolidation=r"(?:X|T|S|_)",
    eopf_hash=r"[0-9A-Fa-f]{3}",
    processing_center=r"[A-Z0-9]{3}",
    timeliness=r"[A-Z]{2}",
    baseline=r"[0-9_]{3}",
    frame_along_track=r"[0-9_]{4}",  # ____, 1980, 0000,
    area=r"[A-Z]{6}_{11}",  # EUROPE__________
)
#
RE_ADF: re.Pattern[str] = re.compile("S[0-9]{1}[A-Z_]_ADF_[0-9A-Z]{5}")
RE_PRODUCT: re.Pattern[str] = re.compile("S[0-9]{1}[A-Z_]{3}[A-Z0-9_]{3}")

# samples
# S3A_OL_0_EFR____20221101T162118_20221101T162318_20221101T180111_0119_091_311______PS1_O_NR_002.SEN3
# S3A_OL_0_CR0____20220511T202328_20220511T202413_20220511T213302_0045_085_142______PS1_O_NR_002.SEN3
# S3B_SL_2_LFR_BW_20230602T101215_20230602T101515_20230603T123759_0180_080_122_1980_PS2_O_NT_004.SEN3

RE_PRODUCT_S3_LEGACY = r"_".join(
    [
        RE_PATTERNS["mission1"] + RE_PATTERNS["platform"],
        RE_PATTERNS["sensor_S3L"],
        RE_PATTERNS["level"],
        RE_PATTERNS["prod_S3L"],
        RE_PATTERNS["date"],
        RE_PATTERNS["date"],
        RE_PATTERNS["date"],
        RE_PATTERNS["duration"],
        RE_PATTERNS["cycle"],
        RE_PATTERNS["orbit"],
        RE_PATTERNS["frame_along_track"],
        RE_PATTERNS["processing_center"],
        RE_PATTERNS["platform"],
        RE_PATTERNS["timeliness"],
        RE_PATTERNS["baseline"],
    ],
)

# samples
# S3A_SY_2_V10____20231221T000000_20231231T235959_20240102T232539_EUROPE____________PS1_O_NT_002.SEN3
# S3A_SY_2_VG1____20191227T124111_20191227T124411_20230403T132606_GLOBAL____________PS1_D_NR_002.SEN3
RE_PRODUCT_S3_LEGACY_COMPOSITE = r"_".join(
    [
        RE_PATTERNS["mission1"] + RE_PATTERNS["platform"],
        RE_PATTERNS["sensor_S3L"],
        RE_PATTERNS["level"],
        RE_PATTERNS["prod_S3L"],
        RE_PATTERNS["date"],
        RE_PATTERNS["date"],
        RE_PATTERNS["date"],
        RE_PATTERNS["area"],
        RE_PATTERNS["processing_center"],
        RE_PATTERNS["platform"],
        RE_PATTERNS["timeliness"],
        RE_PATTERNS["baseline"],
    ],
)

# sample: S3__AX___CLM_AX_20000101T000000_20991231T235959_20151214T120000___________________MPC_O_AL_001.SEN3
# sample: S3A_OL_1_CLUTAX_20160425T095210_20991231T235959_20160525T120000___________________MPC_O_AL_003.SEN3
RE_ADF_S3_LEGACY = r"_".join(
    [
        RE_PATTERNS["mission1"] + RE_PATTERNS["platform"],  # S3_
        RE_PATTERNS["sensor_S3ADFL"],  # OL, AX
        RE_PATTERNS["level_L"],  #
        RE_PATTERNS["adf_S3L"],
        RE_PATTERNS["date"],
        RE_PATTERNS["date"],
        RE_PATTERNS["date"],
        r"_________________",
        RE_PATTERNS["processing_center"],
        RE_PATTERNS["platform"],
        RE_PATTERNS["timeliness"],
        RE_PATTERNS["baseline"],
    ],
)

# S1A_IW_RAW__0SDH_20240410T075338_20240410T075451_053368_0678E5_F66E.SAFE
# S1A_GP_RAW__0____20240410T031915_20240410T083701_053366________6A58.SAFE
RE_PRODUCT_S1_LEGACY = r"_".join(
    [
        RE_PATTERNS["mission1"] + RE_PATTERNS["platform"],  # S1A
        RE_PATTERNS["s1_BB"],  # IW
        RE_PATTERNS["s1_TTT"],  # RAW
        RE_PATTERNS["s1_M"] + RE_PATTERNS["s1_L"] + RE_PATTERNS["s1_C"] + RE_PATTERNS["s1_P"],  # _0SDH
        RE_PATTERNS["date"],  # 20240410T075338
        RE_PATTERNS["date"],  # 20240410T075451
        r".*",  # 053368_0678E5_F66E
    ],
)

# sample: S2A_MSIL1C_20231001T094031_N0509_R036_T33RUJ_20231002T065101.SAFE"
# or S2A_MSIL1A_20231019T120714_N0509_R082.SAFE/
RE_PRODUCT_S2_LEGACY = r"_".join(
    [
        RE_PATTERNS["mission1"] + RE_PATTERNS["platform"],
        r"MSI" + RE_PATTERNS["level_S2"],
        RE_PATTERNS["date"],
        r".*",
    ],
)

# sample: OLCEFR_20230506T015316_0180_B117_T931.zarr
# sample: SRACL0_20180504T091252_0014_A378_T129.zarr
# sample: GPSRAW_20240410T031915_19066_A097_T461.zarr
RE_PRODUCT_EOPF_COMMON = "_".join(
    [
        RE_PATTERNS["sensor"] + RE_PATTERNS["prod"],
        RE_PATTERNS["date"],
        RE_PATTERNS["duration"],
        RE_PATTERNS["platform"] + RE_PATTERNS["orbit"],
        RE_PATTERNS["consolidation"] + RE_PATTERNS["eopf_hash"],
    ],
)

# sample: S3OLCEFR_20230506T015316_0180_B117_T931.zarr
RE_PRODUCT_EOPF_LEGACY = RE_PATTERNS["mission1"] + RE_PRODUCT_EOPF_COMMON

# sample: S03OLCEFR_20230506T015316_0180_B117_T931.zarr
RE_PRODUCT_EOPF = RE_PATTERNS["mission2"] + RE_PRODUCT_EOPF_COMMON

# sample: S03OLCEFR_test
RE_PRODUCT_PERMISSIVE = (RE_PATTERNS["mission"] + RE_PATTERNS["sensor"] + RE_PATTERNS["prod"]) + r"\.*"

# sample: ADF_OLEOP_20160216T000000_20991231T235959_20231030T154253
RE_ADF_EOPF_COMMON: str = "_".join(
    [
        RE_PATTERNS["platform"],
        "ADF",
        RE_PATTERNS["adf_semantic"],
        RE_PATTERNS["date"],
        RE_PATTERNS["date"],
        RE_PATTERNS["date"],
    ],
)

# sample: S3A_ADF_OLEOP_20160216T000000_20991231T235959_20231030T154253.zarr
RE_ADF_EOPF_LEGACY = RE_PATTERNS["mission1"] + RE_ADF_EOPF_COMMON

# sample: S03A_ADF_OLEOP_20160216T000000_20991231T235959_20231030T154253.zarr
RE_ADF_EOPF = RE_PATTERNS["mission2"] + RE_ADF_EOPF_COMMON

# sample: ADF_OLINS_test
RE_ADF_PERMISSIVE = "(?:%s_){0,1}ADF_[A-Z0-9]{5}.*" % (RE_PATTERNS["mission"] + RE_PATTERNS["platform"])

CO_PATTERNS = {key: re.compile(pattern) for key, pattern in RE_PATTERNS.items()}


def is_s2_legacy_adf(filename: str) -> bool:
    try:
        PDILogicalFilename.from_string(Path(filename).stem)
    except ValueError:
        return False
    else:
        return True


PATTERNS: dict[L_DataFileNamePattern, str | Callable[..., bool]] = {
    "product/s3-legacy": RE_PRODUCT_S3_LEGACY,
    "product/s3-legacy-composite": RE_PRODUCT_S3_LEGACY_COMPOSITE,
    "product/s1-legacy": RE_PRODUCT_S1_LEGACY,
    "product/s2-legacy": RE_PRODUCT_S2_LEGACY,
    "product/eopf": RE_PRODUCT_EOPF,
    "product/eopf-legacy": RE_PRODUCT_EOPF_LEGACY,
    "adf/s3-legacy": RE_ADF_S3_LEGACY,
    "adf/s2-legacy": is_s2_legacy_adf,
    "adf/eopf": RE_ADF_EOPF,
    "adf/eopf-legacy": RE_ADF_EOPF_LEGACY,
    "product/permissive": RE_PRODUCT_PERMISSIVE,
    "adf/permissive": RE_ADF_PERMISSIVE,
}

PATTERN_ORDER: list[L_DataFileNamePattern] = [
    "product/s3-legacy",
    "product/s3-legacy-composite",
    "product/s2-legacy",
    "product/s1-legacy",
    "product/eopf",
    "product/eopf-legacy",
    "adf/s3-legacy",
    "adf/eopf",
    "adf/eopf-legacy",
    # Put permissive patterns at the end to catch it only if all valid patterns has failed
    "adf/s2-legacy",
    "product/permissive",
    "adf/permissive",
]

DETECTION_FUNCTIONS: dict[str, Callable[..., bool]] = {}


def match_pattern(filename: str, pattern: str) -> bool:
    co = re.compile(pattern)
    if co.match(filename):
        return True
    else:
        return False


for fmt, pattern_or_func in PATTERNS.items():
    if isinstance(pattern_or_func, str):
        pattern: str = pattern_or_func

        DETECTION_FUNCTIONS[fmt] = partial(match_pattern, pattern=pattern)
    else:
        func = pattern_or_func
        DETECTION_FUNCTIONS[fmt] = func


def detect_filename_pattern(filename: str) -> L_DataFileNamePattern:
    filename = Path(filename).name
    for fmt in PATTERN_ORDER:
        match = DETECTION_FUNCTIONS[fmt]
        if match(filename):
            return fmt
    return "unknown/unknown"


def two_digit_mission(mission: str) -> str:
    if len(mission) == 3:
        return mission
    elif len(mission) == 2:
        try:
            mission_num = int(mission[1:2])
        except ValueError:
            # For example S_ -> S00
            return "%s00" % mission[0]
        else:
            mission_name = mission[0]
            return "%s%02d" % (mission_name, mission_num)
    else:
        raise ValueError(f"mission {mission!r} is not valid")


def timeliness_to_consolidation(timeliness: str) -> str:
    if timeliness == "NT":
        consolidation = "S"
    elif timeliness == "NR":
        consolidation = "T"
    else:
        consolidation = "_"
    return consolidation


def convert_semantic(fmt: str, old_semantic: str, **kwargs: Any) -> str:
    semantics = convert_semantics(fmt, old_semantic, **kwargs)
    semantic = kwargs.get("semantic")
    if semantic is not None:
        return semantic
    elif len(semantics) > 1:
        raise MultipleDataSemanticConversionError(
            f"Multiple values for legacy {old_semantic!r}: {semantics!r}.\n"
            "Please specify the right one with semantic='XXXXX'",
        )
    elif len(semantics) == 1:
        return semantics[0]
    else:
        raise DataSemanticConversionError(old_semantic)


def convert_semantics(fmt: str, old_semantic: str, **kwargs: Any) -> list[str]:
    legacy_fmts: list[L_DataFileNamePattern] = [
        "adf/s2-legacy",
        "adf/s3-legacy",
        "product/s1-legacy",
        "product/s2-legacy",
        "product/s3-legacy",
        "product/s3-legacy-composite",
    ]
    semantic_mapping = kwargs.get("semantic_mapping", {})
    if "semantic" in kwargs:
        return kwargs["semantic"]
    elif old_semantic in semantic_mapping:
        return [semantic_mapping[old_semantic]]
    elif fmt in legacy_fmts:
        from sentineltoolbox.resources.data import DATAFILE_METADATA

        new_ptypes = DATAFILE_METADATA.to_dpr_ptypes(old_semantic)

        if new_ptypes:
            new_semantics = [ptype[-5:] if "ADF" in ptype else ptype[-6:] for ptype in new_ptypes]
            return new_semantics
        else:
            raise DataSemanticConversionError(
                f"Cannot convert legacy semantic {old_semantic!r} to DPR 'semantic'.\n"
                f"Please specify semantic='XXXXX' or update sentineltoolbox database",
            )
    else:
        return [old_semantic]


def _extract_data_from_product_filename(filename: str, **kwargs: Any) -> dict[str, Any]:
    """return a dictionnary containing data extracted from filename.

    Parameters
    ----------
    filename
        filename to parse

    Returns
    -------
        dictionnary with keys compatible with DataFileName constructor
    """
    data: dict[str, Any] = {}
    platform = "_"
    strict = kwargs.get("strict", True)
    start: datetime = fix_datetime(0)
    orbit_number = 0
    consolidation = "_"
    filename = PurePosixPath(filename).stem
    fmt = detect_filename_pattern(filename)
    data["input_data"] = dict(filename=filename, kwargs=kwargs, fmt=fmt)
    suffix: str | None = ""

    if fmt.startswith("product/eopf"):
        # sample: S03OLCEFR_20230506T015316_0180_A117_T931.zarr
        if fmt == "product/eopf-legacy":
            # Pad with a 0 to get a 3-letter mission id (eg 'S02').
            fixed_filename = f"{filename[:1]}0{filename[1:]}"
        else:
            # Keep existing 3-letter mission id.
            fixed_filename = filename

        parsed_name = SentinelProductNameDefinition.from_string(fixed_filename)
        mission = two_digit_mission(parsed_name.product_type.mission)
        sensor = parsed_name.product_type.sensor  # eg MSI
        code = parsed_name.product_type.code  # eg L1C
        semantic = sensor + code  # eg MSIL1C
        start = fix_datetime(parsed_name.acquisition_start_time)
        duration = fix_timedelta(int(parsed_name.acquisition_duration))
        platform = parsed_name.platform
        orbit_number = int(parsed_name.relative_orbit_number)
        consolidation = parsed_name.auxiliary_data_consolidation_level
        suffix = parsed_name.type_specific_name_extension
        if suffix:
            suffix = "_" + suffix
        else:
            suffix = ""
    elif fmt == "product/s1-legacy":
        # sample: S1A_IW_RAW__0SDH_20240410T075338_20240410T075451_053368_0678E5_F66E.SAFE
        mission = two_digit_mission(filename[0:2])  # S1A
        old_semantic = filename[4:14]  # IW_RAW__0S
        semantic = convert_semantic(fmt, old_semantic, **kwargs)
        start = fix_datetime(filename[17:32])
        end = fix_datetime(filename[33:48])
        duration = end - start
        platform = filename[2]
        suffix = filename[49:]
    elif fmt == "product/s2-legacy":
        # sample: S2A_MSIL1C_20230422T085551_N0509_R007_T34QFL_20230422T110127
        try:
            s2prod = S2MSIL1CProductURI.from_string(filename)
        except ValueError as e:
            logger.debug(f"s2-legacy filename {filename} seems not valid: {e}")
            s2prod = S2MSIL1CProductURI.from_string(filename[:37] + "_TXXXXX_20010101T000000.SAFE")
        mission = two_digit_mission(s2prod.mission_id[0:2])
        platform = s2prod.mission_id[-1]
        semantic = s2prod.product_level  # eg MSIL1C
        data["input_data"]["semantic"] = semantic
        data["input_data"]["creation_date"] = s2prod.product_discriminator_time_str
        start = fix_datetime(s2prod.product_discriminator_time_str)
        duration = fix_timedelta(kwargs.get("duration", 0))
        orbit_number = int(s2prod.relative_orbit_number[1:])
        consolidation = kwargs.get("consolidation", "T")

    elif fmt == "product/s3-legacy":
        # sample: S3A_OL_0_EFR____20221101T162118_20221101T162318_20221101T180111_0119_091_311_1234_PS1_O_NR_002.SEN3
        mission = two_digit_mission(filename[0:2])
        platform = filename[2]
        old_semantic = filename[4:15]
        data["input_data"]["semantic"] = old_semantic
        semantic = convert_semantic(fmt, old_semantic, **kwargs)[-6:]  # eg MSIL1C
        start = fix_datetime(filename[16:31])
        duration = fix_timedelta(int(filename[64:68]))
        data["input_data"]["creation_date"] = filename[48:63]
        orbit_number = int(filename[73:76])
        consolidation = timeliness_to_consolidation(filename[88:90])
    elif fmt == "product/s3-legacy-composite":
        # sample: S3A_SY_2_V10____20231221T000000_20231231T235959_20240102T232539_EUROPE____________PS1_O_NT_002.SEN3
        mission = two_digit_mission(filename[0:2])
        platform = filename[2]
        old_semantic = filename[4:15]
        data["input_data"]["semantic"] = old_semantic
        semantic = convert_semantic(fmt, old_semantic, **kwargs)[-6:]  # eg MSIL1C
        start = fix_datetime(filename[16:31])
        duration = fix_timedelta(0)
        orbit_number = 0
        consolidation = timeliness_to_consolidation(filename[88:90])
    elif fmt == "product/permissive":
        # sample: S03OLCEFR_test
        # S2MSIL2A_20231002T054641_N0509_R048_T43TFL_623.zarr
        if strict:
            msg = f"""{filename!r} is not recognized as a valid format.
Common issues: format doesn't match valid pattern. For example: MMMSSSCCC_YYYYMMDDTHHMMSS_UUUU_PRRR_XVVV[_Z*]
pass: strict=False to still extract partial data from this name"""
            raise NotImplementedError(msg)

        logger.info(
            "Try to extract information from product with incorrect name. "
            "Result may be hazardous. Please double check result",
        )
        pattern_found = CO_PATTERNS["mission"].search(filename.split("_")[0])
        if pattern_found:
            mission = pattern_found.group()
            i = len(mission)
            semantic = filename[i : i + 6]  # noqa: E203
            filename = filename[i + 6 :]  # noqa: E203
        else:
            mission = "S__"
            semantic = "XXXXXX"

        pattern_found = CO_PATTERNS["date"].search(filename)
        if pattern_found:
            start = fix_datetime(pattern_found.group())
            filename = filename[pattern_found.end() + 1 :]  # noqa: E203
        else:
            start = datetime.now()

        pattern_found = CO_PATTERNS["duration"].search(filename)
        if pattern_found:
            duration = fix_timedelta(int(pattern_found.group()))
            filename = filename[pattern_found.end() + 1 :]  # noqa: E203
        else:
            duration = fix_timedelta(0)

        pattern_found = CO_PATTERNS["orbit"].search(filename)
        if pattern_found:
            orbit_number = int(pattern_found.group())

    else:
        msg = f"""{filename!r} is not recognized as a valid format.
Common issues:
  - format doesn't match valid pattern. For example: MMMSSSCCC_YYYYMMDDTHHMMSS_UUUU_PRRR_XVVV[_Z*]"""
        raise NotImplementedError(msg)

    data.update(
        dict(
            mission=mission,
            platform=platform,
            semantic=semantic,
            start=start,
            duration=duration,
            orbit_number=orbit_number,
            consolidation=consolidation,
            suffix=suffix,
        ),
    )
    return data


def _extract_data_from_adf_filename(filename: str, **kwargs: Any) -> dict[str, Any]:
    """return a dictionnary containing data extracted from filename.

    Parameters
    ----------
    filename
        filename to parse

    Returns
    -------
        dictionnary with keys compatible with DataFileName constructor
    """
    data: dict[str, Any] = {}
    start: datetime = fix_datetime(0)
    stop: datetime = fix_datetime(0)
    filename = PurePosixPath(filename).stem
    fmt = detect_filename_pattern(filename)
    data["input_data"] = dict(filename=filename, kwargs=kwargs, fmt=fmt)

    if fmt == "adf/s2-legacy":
        # S2A_OPER_GIP_BLINDP_MPC__20150605T094736_V20150622T000000_21000101T000000_B00.SAFE
        s2adf = PDILogicalFilename.from_string(filename)
        mission = two_digit_mission(s2adf.mission_id[0:2])
        platform = s2adf.mission_id[-1]
        old_semantic = s2adf.file_class + "_" + s2adf.file_type.file_category + s2adf.file_type.semantic_descriptor
        data["input_data"]["semantic"] = old_semantic
        semantic = convert_semantic(fmt, old_semantic, **kwargs)[-5:]
        period = s2adf.instance_id.optional_suffix.applicability_time_period
        if period:
            if isinstance(period["start"], datetime):
                start = period["start"]
            if isinstance(period["stop"], datetime):
                stop = period["stop"]

    elif fmt == "adf/s3-legacy":
        # S3A_OL_1_CLUTAX_20160425T095210_20991231T235959_20160525T120000___________________MPC_O_AL_003.SEN3
        mission = two_digit_mission(filename[0:2])
        platform = filename[2]
        old_semantic = filename[4:15]
        data["input_data"]["semantic"] = old_semantic
        data["input_data"]["creation_date"] = filename[48:63]
        semantic = convert_semantic(fmt, old_semantic, **kwargs)[-5:]
        start = fix_datetime(filename[16:31])
        stop = fix_datetime(filename[32:47])
    elif fmt.startswith("adf/eopf"):
        # sample: S03A_ADF_OLINS_20241231T000102_20241231T000302_20240331T121200.zarr
        if fmt == "adf/eopf-legacy":
            i = 2
        else:
            i = 3
        mission = two_digit_mission(filename[:i])
        platform = filename[i]
        semantic = filename[i + 6 : i + 11]  # noqa: E203
        start = fix_datetime(filename[i + 12 : i + 27])  # noqa: E203
        stop = fix_datetime(filename[i + 28 : i + 43])  # noqa: E203
    elif fmt == "adf/permissive":
        re_sx = "(?:%s_)" % (RE_PATTERNS["mission1"] + RE_PATTERNS["platform"])  # S3A
        re_s0x = "(?:%s_)" % (RE_PATTERNS["mission2"] + RE_PATTERNS["platform"])  # S03A
        search_sx = re.search(re_sx, filename)
        search_s0x = re.search(re_s0x, filename)
        if search_s0x:
            search = search_s0x
        elif search_sx:
            search = search_sx
        else:
            search = None
        if search:
            mission = search.group()[:-2]
            platform = search.group()[-2:-1]
            # S03A_ADF_XXXXX_yyyy -> ADF_XXXXX_yyyy -> XXXXX
            semantic = filename[search.span()[1] :].split("_")[1]  # noqa: E203
        else:
            mission = "S__"
            platform = "_"
            if filename.startswith("ADF_"):
                semantic = filename[4:9]
            else:
                semantic = filename[:5]

        start = fix_datetime(0)
        stop = fix_datetime(0)
    else:
        raise NotImplementedError(fmt)

    data.update(
        dict(
            mission=mission,
            platform=platform,
            semantic=semantic,
            start=start,
            stop=stop,
        ),
    )
    return data


def _fixed_kwargs(**kwargs: Any) -> MutableMapping[str, Any]:
    for key, fix in [("duration", fix_timedelta), ("start", fix_datetime), ("stop", fix_datetime)]:
        if key in kwargs:
            kwargs[key] = fix(kwargs[key])
    semantic = kwargs.get("semantic", "")
    if semantic.startswith("ADF_"):
        logger.warning("Please remove 'ADF_' in semantic")
        kwargs["semantic"] = semantic[4:]
    for kwarg_name in ("strict", "semantic_mapping", "input_data"):
        if kwarg_name in kwargs:
            del kwargs[kwarg_name]
    return kwargs


@dataclass
class SentinelFileNameGenerator(FileNameGenerator):
    mission: str  # MMM. For example S03
    platform: str  # For example A, _
    semantic: str  # XXXXXX or XXXXX For example OLINS, OLCEFR
    fmt: L_DataFileNamePattern

    def __post_init__(self) -> None:
        self.mission = self.mission.upper()
        self.mission = two_digit_mission(self.mission)
        self.platform = self.platform.upper()

    def stac(self) -> MutableMapping[Hashable, Any]:
        """Generate STAC metadata from attributes"""
        from sentineltoolbox.attributes import AttributeHandler

        stac: MutableMapping[Hashable, Any] = {}
        hdl = AttributeHandler(stac)
        hdl.set_stac_property("product:type", self.semantic)
        hdl.set_stac_property("platform", f"sentinel-{self.mission[-1]}{self.platform.lower()}")
        return stac


@dataclass(kw_only=True)
class ProductFileNameGenerator(SentinelFileNameGenerator):
    """
    Sentinel Product File Name Generator
    """

    start: datetime
    duration: timedelta
    orbit_number: int
    consolidation: str

    suffix: str = ""
    fmt: L_DataFileNamePattern = "product/eopf"

    @property
    def sensor(self) -> str:
        """
        Extract the sensor information from the semantic descriptor

        Example: semantic = MSIL1C -> sensor = MSI

        Returns
        -------
            The extracted semantic descriptor
        """
        return self.semantic[:3]

    @property
    def code(self) -> str:
        """
        Extract the code information from the semantic descriptor

        Example: semantic = MSIL1C -> code = L1C

        Note: code can also be referred as "product level"

        Returns
        -------
            The extracted code
        """
        return self.semantic[3:]

    def product_type(self) -> str:
        return f"{self.mission}{self.semantic}"

    @staticmethod
    def new(
        mission: str,
        platform: str,
        semantic: str,
        start: T_DateTime,
        duration: T_TimeDelta,
        orbit_number: int | None = None,
        consolidation: str | None = None,
        suffix: str = "",
        **kwargs: Any,
    ) -> "ProductFileNameGenerator":
        """
        >>> prod_name_gen = ProductFileNameGenerator.new("s3", "a", "OLCEFR", "20241231T000000", 120, 311, "T")
        >>> prod_name_gen.to_string(hash=0x123)
        'S03OLCEFR_20241231T000000_0120_A311_T123.zarr'

        :param mission: is the owner mission
        (e.g. "S1", "S2", ... "S0" for any mission. two-digit is also allowed: "S03")
        :param platform: is the satellite id. For example, "A", "B". Use "_" if not specified
        :param semantic: is a code related to the data theme. SSSCCC <sensor><code> for example OLCEFR
        :param start: is the observation start time (str like 20170810T150000 or datetime.datetime)
        :param duration: is the duration of observation in seconds
        :param orbit_number: optional. by default None
        :param consolidation: optional. by default None
        :param suffix: optional. user suffix, by default ""
        """
        if orbit_number is None:
            orbit_number = 0
        if consolidation is None:
            consolidation = "_"
        return ProductFileNameGenerator(
            mission=mission,
            platform=platform,
            semantic=semantic,
            start=fix_datetime(start),
            duration=fix_timedelta(duration),
            orbit_number=orbit_number,
            consolidation=consolidation,
            suffix=suffix,
        )

    @staticmethod
    def from_string(filename: str, **kwargs: Any) -> "ProductFileNameGenerator":
        """
        Generate a FileNameGenerator from filename string.
        If filename is a legacy filename, you must specify `semantic` to specify the new format semantic.

        For example:

        >>> legacy_name = "S3A_OL_0_EFR____20221101T162118_20221101T162318_20221101T180111_0119_091_311______PS1_O_NR_002.SEN3" # noqa: E501
        >>> filegen = ProductFileNameGenerator.from_string(legacy_name, semantic="OLCEFR")
        >>> filegen.semantic
        'OLCEFR'

        :param filename: input filename
        :param kwargs:
        :return:
        """
        data = _extract_data_from_product_filename(filename, **kwargs)
        data.update(kwargs)
        return ProductFileNameGenerator(**_fixed_kwargs(**data))

    def is_valid(self) -> bool:
        """
        return True if all required data are set, else retrun False
        """
        valid: bool = True
        valid = valid and self.platform.lower() in ascii_letters
        valid = valid and self.duration.total_seconds() >= 0
        valid = valid and self.orbit_number > 0
        valid = valid and self.consolidation != "_"
        return valid

    def to_string(
        self,
        extension: str | None = None,
        hash: int = 0,
        creation_date: T_DateTime | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate a filename

        Parameters
        ----------
        extension, optional
            filename extension, by default ".zarr" or ".json" depending on semantic
        hash, optional
            quasi-unique hexadecimal number (0..9,A..F),
            like a CRC checksum (to avoid overwriting files in case of reprocessing action)
        creation_date, optional
            creation_date: by default, use current time

        Returns
        -------
            valid sentinel file name

        """
        if extension is None:
            from sentineltoolbox.resources.data import DATAFILE_METADATA

            extension = DATAFILE_METADATA.get_metadata(self.semantic, "ext", ".zarr")
        # S03OLCEFR_20230506T015316_0180_B117_T931.zarr
        return "_".join(
            [
                self.product_type(),
                f"{self.start.strftime(DATE_FORMAT)}",
                f"{self.duration.seconds:04}",
                f"{self.platform}{self.orbit_number:03}",
                f"{self.consolidation}{hex(hash)[2:].upper().zfill(3)}{self.suffix}{extension}",
            ],
        )

    def stac(self) -> MutableMapping[Hashable, Any]:
        """Generate STAC metadata from attributes"""
        from sentineltoolbox.attributes import AttributeHandler

        stac = super().stac()
        hdl = AttributeHandler(stac)
        if self.consolidation == "T":
            timeline = "NRT"
        elif self.consolidation == "_":
            timeline = "STC"
        elif self.consolidation == "S":
            timeline = "NTC"
        else:
            timeline = None
        hdl.set_stac_property("start_datetime", self.start.strftime(DATE_FORMAT))
        hdl.set_stac_property("end_datetime", (self.start + self.duration).strftime(DATE_FORMAT))
        hdl.set_stac_property("sat:relative_orbit", str(self.orbit_number))
        if timeline:
            hdl.set_stac_property("product:timeline", timeline)
        return stac


@dataclass(kw_only=True)
class AdfFileNameGenerator(SentinelFileNameGenerator):
    """
    Sentinel Product File Name Generator:

    EOPF ADF FILE NAME CONVENTION
    The adopted naming rule is MMMM_ADF_XXXXX_valstart_valstop_creation.ext where
      - XXXXX is a code related to the data theme (see next section)
      - MMMM is the owner mission (e.g. S01A, S02B, S03_, and S00_ for any mission)
    -valstart is the validity start time (e.g. 20170810T150000)
    -valstop is the validity stop time (e.g. 21000101T000000)
    -creation is the creation time (e.g. 20220713T103000)
    -ext is ZARR or JSON (and txt for IERSB)
    """

    start: datetime
    stop: datetime
    suffix: str = ""
    fmt: L_DataFileNamePattern = "adf/eopf"

    @staticmethod
    def new(
        mission: str,
        platform: str,
        semantic: str,
        start: T_DateTime,
        stop: T_DateTime = "20991231T235959",
        suffix: str = "",
        **kwargs: Any,
    ) -> "AdfFileNameGenerator":
        """
        >>> adf_name = AdfFileNameGenerator.new("s3", "a", "OLINS", datetime(2024, 12, 31, 0, 1, 2))
        >>> adf_name.to_string(creation_date="20240327T115758")
        'S03A_ADF_OLINS_20241231T000102_20991231T235959_20240327T115758.zarr'

        :param mission: is the owner mission (e.g. "S1", "S2", ... "S0" for any mission. two-digit is also allowed: "S03") # noqa: E501
        :param platform: is the satellite id. For example, "A", "B". Use "_" if not specified
        :param semantic: is a code related to the data theme. SSCCC <sensor><code> for example OLINS
        :param start: is the validity start time (str like 20170810T150000 or datetime.datetime)
        :param stop: is the validity stop time (str like 20170810T150000 or datetime.datetime), by default "20991231T235959" # noqa: E501
        :param suffix: optional. user suffix, by default ""
        """
        return AdfFileNameGenerator(
            mission=mission,
            platform=platform,
            semantic=semantic,
            start=fix_datetime(start),
            stop=fix_datetime(stop),
            suffix=suffix,
        )

    def product_type(self) -> str:
        return f"{self.mission}{self.platform}_ADF_{self.semantic}"

    @staticmethod
    def from_string(filename: str, **kwargs: Any) -> "AdfFileNameGenerator":
        """
        Generate a FileNameGenerator from filename string.
        If filename is a legacy filename, you must specify `semantic` to specify the new format semantic.
        """
        data = _extract_data_from_adf_filename(filename, **kwargs)
        data.update(kwargs)
        return AdfFileNameGenerator(**_fixed_kwargs(**data))

    def is_valid(self) -> bool:
        """
        return True if all required data are set, else retrun False
        """
        duration = fix_datetime(self.stop) - fix_datetime(self.start)
        valid: bool = True
        valid = valid and self.platform.lower() in ascii_letters
        valid = valid and duration.total_seconds() >= 0
        return valid

    def to_string(
        self,
        extension: str | None = None,
        hash: int = 0,
        creation_date: T_DateTime | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate a filename

        Parameters
        ----------
        extension, optional
            filename extension, by default ".zarr" or ".json" depending on ADF
        hash, optional
            quasi-unique hexadecimal number (0..9,A..F),
            like a CRC checksum (to avoid overwriting files in case of reprocessing action)
        creation_date, optional
            creation_date: by default, use current time

        Returns
        -------
            valid sentinel file name

        """
        if extension is None:
            from sentineltoolbox.resources.data import DATAFILE_METADATA

            extension = DATAFILE_METADATA.get_metadata(self.semantic, "ext", ".zarr")
        # S03A_ADF_OLEOP_20160216T000000_20991231T235959_20231030T154253.zarr
        if creation_date is None:
            creation = datetime.now()
        else:
            creation = fix_datetime(creation_date)
        return "_".join(
            [
                self.product_type(),
                f"{self.start.strftime(DATE_FORMAT)}",
                f"{self.stop.strftime(DATE_FORMAT)}",
                f"{creation.strftime(DATE_FORMAT)}{self.suffix}{extension}",
            ],
        )


def filename_generator(
    filename: str,
    **kwargs: Any,
) -> tuple[ProductFileNameGenerator | AdfFileNameGenerator, dict[str, Any]]:
    fmt = detect_filename_pattern(filename)
    if fmt.startswith("product"):
        data = _extract_data_from_product_filename(filename, **kwargs)
        return ProductFileNameGenerator.from_string(filename, **kwargs), data["input_data"]
    elif fmt.startswith("adf"):
        data = _extract_data_from_adf_filename(filename, **kwargs)
        return AdfFileNameGenerator.from_string(filename, **kwargs), data["input_data"]
    else:
        raise NotImplementedError(f"{fmt}: {filename}")


def extract_semantic(name: str, error: str = "replace") -> str:
    fmt = detect_filename_pattern(name)
    if fmt != "unknown/unknown":
        fgen, _ = filename_generator(name, strict=False)
        return fgen.semantic
    else:
        if error == "replace":
            return name
        elif error == "error":
            raise ValueError
        else:
            return ""


def extract_ptype(name: str, error: str = "replace") -> str:
    fmt = detect_filename_pattern(name)
    if fmt != "unknown/unknown":
        fgen, _ = filename_generator(name, strict=False)
        if fmt.startswith("adf"):
            return fgen.mission + "_ADF_" + fgen.semantic
        else:
            return fgen.mission + fgen.semantic
    else:
        if error == "replace":
            return name
        elif error == "error":
            raise ValueError
        else:
            return ""
