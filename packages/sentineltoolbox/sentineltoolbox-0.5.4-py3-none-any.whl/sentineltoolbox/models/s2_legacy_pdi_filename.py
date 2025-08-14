"""Parse filenames

Parts of docstrings are extracted from:
"3.2 PDI Naming Convention" in "[S2-PSD] S2-PDGS-TAS-DI-PSD-V14.9.pdf"
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal, TypeGuard, get_args

from sentineltoolbox.typedefs import fix_datetime

DATE_FORMAT = r"%Y%m%dT%H%M%S"

PDI_LOGICAL_FILENAME_MIN_LEN = len("S2A_OPER_GIP_BLINDP_MPC__20150605T094736")


@dataclass
class Suffix:
    name: str
    length: int


PDI_OPTIONAL_SUFFIX_MAPPING: dict[str, Suffix] = {
    "S": Suffix(name="applicability_start", length=len("_SYYYYMMDDTHHMMSS")),
    "O": Suffix(name="orbit_period", length=len("_Offffff_llllll")),
    "V": Suffix(name="applicability_time_period", length=len("_VyyyymmddThhmmss_YYYYMMDDTHHMMSS")),
    "D": Suffix(name="detector_id", length=len("_Dxx")),
    "A": Suffix(name="absolute_orbit_number", length=len("_Affffff")),
    "R": Suffix(name="relative_orbit_number", length=len("_Rzzz")),
    "T": Suffix(name="tile_number", length=len("_Txxxxx")),
    "N": Suffix(name="processing_baseline_number", length=len("_Nxx.yy")),
    "B": Suffix(name="band_index_id", length=len("_Bxx")),
    "W": Suffix(name="completeness_id", length=len("_Wx")),
    "L": Suffix(name="degradation_id", length=len("_Ly")),
}

MissionIdLiteral = Literal["S2A", "S2B", "S2_"]  # Note: not all are listed.


def is_mission_id_type(value: str) -> TypeGuard[MissionIdLiteral]:
    """Is the given string a MissionIdType?"""

    return value in get_args(MissionIdLiteral)


@dataclass(frozen=True, kw_only=True)
class PDIOptionalSuffix:
    applicability_start: None | datetime = None
    orbit_period: None | dict[Literal["first", "last"], str] = None
    applicability_time_period: None | dict[Literal["start", "stop"], datetime | None] = None
    detector_id: None | str = None
    absolute_orbit_number: None | str = None
    relative_orbit_number: None | str = None
    tile_number: None | str = None
    processing_baseline_number: None | str = None
    band_index_id: str = ""
    # full, partial orbit
    completeness_id: None | Literal["F", "P"] = None
    # nominal, degraded data
    degradation_id: None | Literal["N", "D"] = None

    _optional_suffix_accumulator: dict[str, Any] = field(repr=False)
    _original_string: str = field(repr=False)

    @staticmethod
    def from_string(string: str) -> "PDIOptionalSuffix":
        accumulator = parse_optional_suffix_recursive(string, {})

        if "applicability_start" in accumulator:
            accumulator["applicability_start"] = fix_datetime(accumulator["applicability_start"])
        if "orbit_period" in accumulator:
            accumulator["orbit_period"] = {
                "first": accumulator["orbit_period"][:6],
                "last": accumulator["orbit_period"][7:],
            }
        if "applicability_time_period" in accumulator:
            start = fix_datetime(accumulator["applicability_time_period"][:15])
            stop = fix_datetime(accumulator["applicability_time_period"][16:])
            accumulator["applicability_time_period"] = {
                "start": start,
                "stop": stop,
            }

        data = PDIOptionalSuffix(
            _optional_suffix_accumulator=accumulator,
            _original_string=string,
            **accumulator,
        )
        return data


@dataclass(frozen=True, kw_only=True)
class PDIFileType:
    """File Type (File Category + File Semantic) of a PDI Logical File Name

    BELOW IS EXTRACTED FROM "3.2 PDI Naming Convention" in "[S2-PSD] S2-PDGS-TAS-DI-PSD-V14.9.pdf"

    File Type is a 10 characters field either uppercase letters, digits or
    underscores “_”. The File Type field is subdivided into two sub-fields as follows:
    TTTTTTTTTT = FFFFDDDDDD where:

    - FFFF is the File Category.
    - DDDDDD is the Semantic Descriptor.

    Example
    -------

    GIP_BLINDP
    FFFFDDDDDD
    TTTTTTTTTT
    """

    file_category: str
    semantic_descriptor: str

    @staticmethod
    def from_string(string: str) -> "PDIFileType":
        return PDIFileType(
            file_category=string[0:4],
            semantic_descriptor=string[4:10],
        )

    def __str__(self) -> str:
        return self.file_category + self.semantic_descriptor


@dataclass(frozen=True, kw_only=True)
class PDIInstanceId:
    """Instance ID of a PDI Logical File Name

    BELOW IS EXTRACTED FROM "3.2 PDI Naming Convention" in "[S2-PSD] S2-PDGS-TAS-DI-PSD-V14.9.pdf"

    Instance ID is used to define several sub-fields within the filename according to the nature of the
    file. For usage for the Sentinel PDGS, Instance ID is decomposed into a set of mandatory sub-
    fields in the prefix, complemented by optional ones in the trailing portion of the filename.
    The File Instance ID mandatory sub-fields are always placed on fixed positions within the filename
    for simple and unambiguous recognition. The mandatory part is subdivided into sub-fields as
    follows:

    <Instance ID mandatory prefix> = ssss_YYYYMMDDThhmmss

    where:

    - ssss is the Site Centre of the file originator
    - YYYYMMDDThhmmss is the Creation Date

    The Site Centre is a 4 characters field defined by either, uppercase letters, digits or underscore “_”.

    The Creation Date is a 15 characters field defined according composed of:

    - 8 characters, all digits, for the date: “YYYYMMDD”
    - 1 uppercase T: “T”
    - 6 characters, all digits, for the time: “hhmmss”

    Example
    -------

    S2A_OPER_GIP_BLINDP_MPC__20150605T094736_V20150622T000000_21000101T000000_B00
                        ssss_YYYYMMDDThhmmss

    """

    site_centre: str
    creation_date: datetime
    optional_suffix: PDIOptionalSuffix

    @staticmethod
    def from_string(string: str) -> "PDIInstanceId":
        site_centre = string[0:4]
        creation_date_string = string[5:20]
        optional_suffix = string[20:]

        instance_id = PDIInstanceId(
            site_centre=site_centre,
            creation_date=fix_datetime(creation_date_string),
            optional_suffix=PDIOptionalSuffix.from_string(optional_suffix),
        )
        return instance_id

    def __str__(self) -> str:
        return "_".join((self.site_centre, self.creation_date.strftime(DATE_FORMAT))) + str(self.optional_suffix)


@dataclass(frozen=True, kw_only=True)
class PDILogicalFilename:
    """Logical File Name of a PDI (Product Data Item)

    BELOW IS EXTRACTED FROM "3.2 PDI Naming Convention" in "[S2-PSD] S2-PDGS-TAS-DI-PSD-V14.9.pdf"

    3.2 PDI Naming Convention

    PDI_ID is a logical and a physical naming convention defined to identify univocally each type of
    PDI. In fact, PDI_ID or PDI_ID.tar (where the tar compression is foreseen) represents the PDI
    physical name defined case by case in the document, but PDI_ID (without extension) represents
    also the logical convention used to reference each type of PDI in the archive.

    The PDI_ID naming convention is described hereafter:

    MMM_CCCC_TTTTTTTTTT_<Instance_id> where:

    - Part MMM: Mission ID.
        - “S2A” or “S2B” “S2_” applicable to the constellation, used for satellite independent files.
    - Part CCCC: File Class
        - 4 uppercase letters can contain digits.  OPER for “Routine Operations” files.
          Note that the File Class will be set “OPER”
          for all products generated during the
          operation phase. During validation or for
          internal testing other values can be defined.
    - Part TTTTTTTTTT: File Type (File Category + File Semantic)
        - 10 uppercase letters can contain digits and underscores.
    - Part <Instance ID>: Instance Id
        - Uppercase letters, digits and underscores.

    Example
    -------

    S2A_OPER_GIP_BLINDP_MPC__20150605T094736_V20150622T000000_21000101T000000_B00
    MMM_CCCC_TTTTTTTTTT_<Instance_id>

    """

    mission_id: MissionIdLiteral
    file_class: str  # TEST or OPER
    file_type: PDIFileType
    instance_id: PDIInstanceId

    @property
    def band_id(self) -> str:
        return "B" + self.instance_id.optional_suffix.band_index_id

    @staticmethod
    def from_string(string: str) -> "PDILogicalFilename":
        if len(string) < PDI_LOGICAL_FILENAME_MIN_LEN:
            raise ValueError(
                f"Given PDI Logical Filename is incomplete. Expected {PDI_LOGICAL_FILENAME_MIN_LEN} characters, "
                f"but only {len(string)} were counted.",
            )

        mission_id_string = string[0:3]

        if not is_mission_id_type(mission_id_string):
            raise ValueError(f"Invalid value for mission id, {mission_id_string}, should be '{MissionIdLiteral}'")

        file_class_string = string[4:8]
        file_type_string = string[9:19]
        instance_id_string = string[20:]

        pdi_logical_filename = PDILogicalFilename(
            mission_id=mission_id_string,
            file_class=file_class_string,
            file_type=PDIFileType.from_string(file_type_string),
            instance_id=PDIInstanceId.from_string(instance_id_string),
        )

        return pdi_logical_filename

    def __str__(self) -> str:
        return "_".join(
            (
                self.mission_id,
                self.file_class,
                str(self.file_type),
                str(self.instance_id),
            ),
        )


def parse_optional_suffix_recursive(string: str, accumulator: dict[str, Any]) -> dict[str, Any]:
    if len(string) == 0:
        return accumulator

    prefix = string[1:2]

    if prefix in PDI_OPTIONAL_SUFFIX_MAPPING:
        optional_suffix_name = PDI_OPTIONAL_SUFFIX_MAPPING[prefix].name
        cursor = PDI_OPTIONAL_SUFFIX_MAPPING[prefix].length
        head = string[2:cursor]
        tail = string[cursor:]
        accumulator[optional_suffix_name] = head
        return parse_optional_suffix_recursive(tail, accumulator)

    raise ValueError(f"Incorrect Optional Suffix in the PDI ID for '{string}'")
