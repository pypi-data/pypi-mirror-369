import copy
import json
from pathlib import Path
from typing import Any

import defusedxml.ElementTree as ET
from eopf import EOProduct
from l0.common.eopf_converters.l0_accessors import (
    PACKET_FIELD_LIST,
    PACKET_FIELDS,
    PRODUCT_TYPES_AN_EN,
    PRODUCT_TYPES_EW_IW_WV,
    PRODUCT_TYPES_SM,
    PacketField,
    product_type_dpr_to_legacy,
    product_type_legacy_to_dpr,
)

from sentineltoolbox._utils import to_snake_case
from sentineltoolbox.readers.resources import get_resource_path
from sentineltoolbox.resources.data import DATAFILE_METADATA, XML_NAMESPACES
from sentineltoolbox.writers.json import DataTreeJSONEncoder

STRIPMAP_LEGACY_TYPES = ["S1_RAW_", "S2_RAW_", "S3_RAW_", "S4_RAW_", "S5_RAW_", "S6_RAW_"]
SMi_Ni = PRODUCT_TYPES_SM + PRODUCT_TYPES_AN_EN
SMi_Ni_EW_IW_WV = SMi_Ni + PRODUCT_TYPES_EW_IW_WV
PRODUCT_TYPES_SAR = SMi_Ni_EW_IW_WV + ["S01RFCANC"]
ISP_DIMENSIONS = ["packet_number", "packet_length"]

PACKET_DESCRIPTION = {
    "packetSequenceCount": "packet sequence count",
    "packetDataLength": "packet data length",
    "coarseTime": "coarse time",
    "fineTime": "fine time",
    "dataWordIndex": "data word index",
    "dataWord": "data word",
    "spacePacketCount": "source packet count",
    "priCount": "pulse repetition interval count",
    "BAQMode": "block adaptive quantization mode",
    "BAQBlockLength": "block adaptive quantization length",
    "rangeDecimation": "range decimation",
    "RXGain": "receive gain",
    "TXRampRate": "transmit ramp rate",
    "TXPulseStartFrequency": "transmit pulse start frequency",
    "TXPulseLength": "transmit pulse length",
    "rank": "rank",
    "PRI": "pulse repetition interval",
    "SWST": "sampling window start time",
    "SWL": "sampling window length",
    "numberOfQuads": "number of quads",
    "userData": "user data packet",
    "annot.sensingTimeDays": "sensing time days elapsed since 01-01-2000",
    "annot.sensingTimeMillisecs": "sensing time milliseconds elapsed since the beginning of day",
    "annot.sensingTimeMicrosecs": "sensing time microseconds",
    "annot.downlinkTimeDays": "downlink time days elapsed since 20000101",
    "annot.downlinkTimeMillisecs": "sensing time milliseconds elapsed since the beginning of day",
    "annot.downlinkTimeMicrosecs": "downlink time microseconds",
    "annot.frames": "number of transfer frames containing the current packet vh",
    "annot.missingFrames": "number of missing transfer frames for the current packet vh",
    "annot.CRCFlag": "crc error flag indicating detection of crc error in packet vh",
    "annot.VCIDPresentFlag": "flag set to 1 if vcid field contains vcid, 0 otherwise (vh)",
    "annot.VCID": "virtual channel identifier for which the vh packet was multiplexed onto",
    "annot.channel": "vh channel information: 01 (binary) = C1, 10 (binary) = C2",
    "dataTakeID": "size in bytes of the hv packet pointed by the current index "
    "(valid for all the packets in the block if var_size_flag = 0, "
    "valid only for the first packet if var_size_flag = 1 and its value is > 0)",
    "mpduPacketZone": "transfer frames",
}

EXCLUDED_FLAG = "<NOTUSED>"

PACKET_LEGACY_TO_DPR = {
    "S01RFCANC": {
        "packetVersionNumber": "packet_version",
        "packetType": "packet_type",
        "secondaryHeaderFlag": "header_flag",
        "PID": "application_process_identifier",
        "PCAT": "packet_category",
        "sequenceFlag": "sequence_flag",
        "packetSequenceCount": "packet_sequence_count",
        "packetDataLength": "packet_data_length",
        "coarseTime": "coarse_time",
        "fineTime": "fine_time",
        "syncMarker": "synchronisation_marker",
        "dataTakeID": "datatake_id",
        "ECCNumber": "ecc_number",
        "firstSpareBit": EXCLUDED_FLAG,
        "testMode": "test_mode",
        "RXChannelID": "rx_channel_id",  # recieve_channel_id ?
        "instrumentConfigurationID": "instrument_configuration_id",
        "dataWordIndex": EXCLUDED_FLAG,
        "dataWord": EXCLUDED_FLAG,
        "spacePacketCount": "space_packet_count",
        "priCount": "mode_pri_count",
        "firstSpare3Bit": EXCLUDED_FLAG,
        "BAQMode": "baq_mode",
        "BAQBlockLength": "baq_block_length",
        "spareByte": EXCLUDED_FLAG,
        "rangeDecimation": "range_decimation",
        "RXGain": "rx_gain",
        "TXRampRate": "tx_pulse_ramp_rate",
        "TXPulseStartFrequency": "tx_pulse_start_frequency",
        "TXPulseLength": "tx_pulse_length",
        "secondSpare3Bit": EXCLUDED_FLAG,
        "rank": "rank",
        "PRI": "pulse_repetition_interval",
        "SWST": "sampling_window_start_time",
        "SWL": "sampling_window_length",
        "ssbFlag": "sas_ssb_data_field",
        "polarisation": "polarisation",
        "temperatureCompensation": "temperature_compensation",
        "firstSpare2Bit": EXCLUDED_FLAG,
        "elevationBeamAddress": "elevation_beam_address",
        "secondSpare2Bit": EXCLUDED_FLAG,
        "beamAddress": "azimuth_beam_address",
        "calMode": "calibration_mode",
        "secondSpareBit": EXCLUDED_FLAG,
        "TXPulseNumber": "tx_pulse_number",
        "signalType": "signal_type",
        "thirdSpare3Bit": EXCLUDED_FLAG,
        "swap": "swap_flag",
        "swathNumber": "swath_number",
        "numberOfQuads": "radar_sample_count_service",
        "fillerOctet": EXCLUDED_FLAG,
        "userData": EXCLUDED_FLAG,
        "annot.sensingTimeDays": "sensing_time_days",
        "annot.sensingTimeMillisecs": "sensing_time_millisecs",
        "annot.sensingTimeMicrosecs": "sensing_time_microsecs",
        "annot.downlinkTimeDays": "downlink_time_days",
        "annot.downlinkTimeMillisecs": "downlink_time_millisecs",
        "annot.downlinkTimeMicrosecs": "downlink_time_microsecs",
        "annot.packetLength": "packet_length",
        "annot.frames": "frames",
        "annot.missingFrames": "missing_frames",
        "annot.CRCFlag": "crc_flag",
        "annot.VCIDPresentFlag": "vcid_present_flag",
        "annot.VCIDSpare": "vcid_spare",
        "annot.VCID": "vcid",
        "annot.channel": "channel",
        "annot.channelSpare": "channel_spare",
        "annot.spare": "spare",
    },
    "S01GPSRAW": {
        # primaryHeaderType
        "packetVersionNumber": "packet_version",
        "packetType": "packet_type",
        "DFHFlag": "header_flag",
        "PID": EXCLUDED_FLAG,
        "PCAT": "packet_category",
        "sequenceFlag": "sequence_flag",
        "packetSequenceCount": "packet_sequence_count",
        "packetDataLength": "packet_data_length",
        # dataFieldHeaderType
        "PUSVersion": EXCLUDED_FLAG,
        "serviceType": EXCLUDED_FLAG,
        "serviceSubtype": EXCLUDED_FLAG,
        "destinationIdentifier": EXCLUDED_FLAG,
        "spareByte": EXCLUDED_FLAG,
        "coarseTime": "coarse_time",
        "fineTime": "fine_time",
        "spare": EXCLUDED_FLAG,
        # measurementDataHeaderType
        "structureIdentifier": "record",
        "filler": EXCLUDED_FLAG,
        "frontEndTemperature": EXCLUDED_FLAG,
        "RSAIdentifier": EXCLUDED_FLAG,
        "receiverMode": EXCLUDED_FLAG,
        "numberOfRecords": EXCLUDED_FLAG,
        "ispType.measurementData": EXCLUDED_FLAG,
    },
    "S01HKMRAW": {
        # primaryHeaderType
        "transferFrameVersionNumber": "transfer_frame_version_number",
        "spacecraftId": "spacecraft_id",
        "virtualChannelId": "virtual_channel_id",
        "virtualChannelFrameCount": "virtual_channel_frame_count",
        "replayFlag": "replay_flag",
        "reservedSpareFlag": "reserved_spare_flags",
        "frameHeaderErrorControl": "frame_header_error_control",
        # tpType
        "mpduHeader": "m_pdu_headers",
        "mpduPacketZone": EXCLUDED_FLAG,
    },
    "S01AISRAW": {
        # primaryHeaderType
        "packetVersionNumber": "packet_version",
        "packetType": "packet_type",
        "secondaryHeaderFlag": "header_flag",
        "PID": EXCLUDED_FLAG,
        "PCAT": "packet_category",
        "sequenceFlag": "sequence_flag",
        "packetSequenceCount": "packet_sequence_count",
        "packetDataLength": "packet_data_length",
        # timeStampType
        "secondSpare3Bit": "second_spare",
        "coarseTime": "coarse_time",
        "fineTime": "fine_time",
        # ispType
        "userData": EXCLUDED_FLAG,
    },
}

# packet defined here are added as "other_metadata" attribute.
INCLUDE_DPR_METADATA = {
    "S01GPSRAW": ["packet_type"],
    "S01RFCANC": [
        "application_process_identifier",
        "ecc_number",
        "synchronisation_marker",
        "instrument_configuration_id",
        "packet_category",
        "packet_type",
        "packet_version",
        "sequence_flag",
        "header_flag",
        "test_mode",
    ],
    "S01AISRAW": ["packet_type"],
    "S01HKMRAW": ["packet_type"],
    "S01SIWRAW": [
        "application_process_identifier",
        "ecc_number",
        "synchronisation_marker",
        "instrument_configuration_id",
        "packet_category",
        "packet_type",
        "packet_version",
        "sequence_flag",
        "header_flag",
        "test_mode",
        "rx_channel_id",
    ],
}

INCLUDE_DPR_METADATA["S01SEWRAW"] = INCLUDE_DPR_METADATA["S01SIWRAW"]
INCLUDE_DPR_METADATA["S01SWVRAW"] = INCLUDE_DPR_METADATA["S01SIWRAW"]


DPR_METADATA_ALIAS = {}
DPR_METADATA_ALIAS["ecc_number"] = "event_control_code"
DPR_METADATA_ALIAS["rx_channel_id"] = "receive_channel_id"

ALL_ANC_CONDITIONS = []
for packet_id, dpr_name in PACKET_LEGACY_TO_DPR["S01RFCANC"].items():
    if dpr_name == EXCLUDED_FLAG or "." in packet_id:
        continue
    ALL_ANC_CONDITIONS.append(dpr_name)

# Duplicate data for all similar product types


for dpr_type in PRODUCT_TYPES_SM:
    INCLUDE_DPR_METADATA[dpr_type] = copy.copy(INCLUDE_DPR_METADATA["S01RFCANC"])
for dpr_type in PRODUCT_TYPES_AN_EN:
    INCLUDE_DPR_METADATA[dpr_type] = copy.copy(INCLUDE_DPR_METADATA["S01RFCANC"])


for dpr_type in PRODUCT_TYPES_SM:
    PACKET_LEGACY_TO_DPR[dpr_type] = copy.copy(PACKET_LEGACY_TO_DPR["S01RFCANC"])
for dpr_type in PRODUCT_TYPES_AN_EN:
    PACKET_LEGACY_TO_DPR[dpr_type] = copy.copy(PACKET_LEGACY_TO_DPR["S01RFCANC"])
for dpr_type in PRODUCT_TYPES_EW_IW_WV:
    PACKET_LEGACY_TO_DPR[dpr_type] = copy.copy(PACKET_LEGACY_TO_DPR["S01RFCANC"])


# Not used for the moment
POLARIZATIONS_SIMPLE_DESC = {
    "SH": "Single HH polarisation",
    "SV": "Single VV polarisation",
    "HH": "HH polarisation for dual polarisation acquisition",
    "VV": "VV polarisation for dual-pol",
    "HV": "HV polarisation for dual-pol",
    "VH": "VH polarisation for dual-pol",
}

# Not used for the moment
POLARIZATIONS_DOUBLE_DESC = {
    "DH": "dual pol, polarisation combinations HH and HV",
    "DV": "dual pol, combinations VV and VH",
}

# Not used for the moment
PRODUCT_CLASS_DESC = {"S": "standard", "C": "calibration", "N": "noise", "A": "annotation"}

# Not used for the moment
INSTRUMENT_MODE_DESC = {
    "SM": "Stripmap",
    "EW": "Extra Wide Swath",
    "IW": "Interferometric Wide Swath",
    "WV": "Wave",
    "RF": "RF Characterisation Mode",
    "EN": "Elevation Notch",
    "AN": "Azimuth Notch",
    "ZS": "Noise Characterisation SM",
    "ZE": "Noise Characterisation EWS",
    "ZI": "Noise Characterisation IWS",
    "ZW": "Noise Characterisation Wave",
    "AI": "AIS",
    "GP": "GPSR/GNSS",
    "HK": "HKTM",
}
POLARIZATIONS = [pol.lower() for pol in sorted(POLARIZATIONS_SIMPLE_DESC)]

SAFE_TO_DPR_PTYPE = product_type_legacy_to_dpr
# /S1A_IW_RAW__0SDH_20220406T130116_20220406T130148_042653_0516C6_6FA3.SAFE


CHUNK_SIZES = {}

CHUNK_SIZES["default"] = {"packet_number": 10000, "packet_length": 10000}
for dpr_type in PRODUCT_TYPES_SAR + ["S01GPSRAW", "S01HKMRAW", "S01AISRAW"]:
    CHUNK_SIZES[dpr_type] = CHUNK_SIZES["default"]

"""

"source_path": "@#find{'product_url': '<URL>','pattern': '.*.dat'}#@"

"""


def to_dpr_name(packet_field_name, packet_fields=None):
    if packet_fields is None:
        packet_fields = {}
    return packet_fields.get(packet_field_name, to_snake_case(packet_field_name))


def generate_long_name(packet_field_name, signal_type=None, packet_fields=None, **kwargs):
    dpr_name = to_dpr_name(packet_field_name, packet_fields)
    auto_name = " ".join(dpr_name.split("_"))
    root = PACKET_DESCRIPTION.get(packet_field_name, auto_name)
    return root


def generate_short_name(dpr_name, signal_type=None, **kwargs):
    return dpr_name


def load_safe_with_eopf(safe_path, metadata_only=False):
    product_path = AnyPath.cast(safe_path)
    safe_store = EOSafeStore(
        product_path,
        mask_and_scale=True,
    )  # legacy store to access a file on the given URL
    eop = safe_store.load(name="NEWMAPPING", metadata_only=metadata_only)  # create and return the EOProduct
    return eop


block_types = {
    "bool": "bool",
    "scalar_bool": "s_bool",
    "uint8": "uint8",
    "scalar_uint8": "s_uint8",
    "uint16": "uint16",
    "scalar_uint16": "s_uint16",
    "uint32": "uint32",
    "scalar_uint32": "s_uint32",
    "uint64": "uint64",
    "scalar_uint64": "s_uint64",
    "double": "double",
    "var_bytearray": "var_bytearray",
    "bytearray": "bytearray",
}

block_stac_extensions = [
    "Text(https://stac-extensions.github.io/eopf/v1.0.0/schema.json)",
    "Text(https://stac-extensions.github.io/product/v0.1.0/schema.json)",
    "Text(https://stac-extensions.github.io/eo/v1.1.0/schema.json)",
    "Text(https://stac-extensions.github.io/sat/v1.0.0/schema.json)",
    "Text(https://stac-extensions.github.io/view/v1.0.0/schema.json)",
    "Text(https://stac-extensions.github.io/scientific/v1.0.0/schema.json)",
    "Text(https://stac-extensions.github.io/processing/v1.2.0/schema.json)",
]


def build_stac_properties(product_type: str, **kwargs: Any) -> dict[str, Any]:
    DEFAULT_STAC_VALUES = {
        "timeliness_category": "NRT",
        "timeliness": "PT3H",
        "instrument": DATAFILE_METADATA.get_metadata(product_type, "instrument", "sar"),
    }
    dic = {}
    for prop_id, prop_value in DEFAULT_STAC_VALUES.items():
        dic[prop_id] = kwargs.get(prop_id, prop_value)

    stac_properties = {
        "datetime": "Text(null)",
        "start_datetime": "corrected_Date_ISO8601(metadataSection/metadataObject[@ID='acquisitionPeriod']/metadataWrap/xmlData/s0:acquisitionPeriod/s0:startTime)",  # noqa: E501
        "end_datetime": "corrected_Date_ISO8601(metadataSection/metadataObject[@ID='acquisitionPeriod']/metadataWrap/xmlData/s0:acquisitionPeriod/s0:stopTime)",  # noqa: E501
        "created": "corrected_Date_ISO8601(metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/s0:processing/@stop)",  # noqa: E501
        "sat:platform_international_designator": "metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/s0:platform/s0:nssdcIdentifier",  # noqa: E501
        "sat:anx_datetime": "metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/s0:orbitReference/s0:extension/s1:orbitProperties/s1:ascendingNodeTime",  # noqa: E501
        "sat:relative_orbit": "to_int(metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/s0:orbitReference/s0:relativeOrbitNumber[@type='stop'])",  # noqa: E501
        "sat:absolute_orbit": "to_int(metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/s0:orbitReference/s0:orbitNumber[@type='stop'])",  # noqa: E501
        "sat:orbit_state": "to_sat_orbit_state(metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/s0:orbitReference/s0:extension/s1:orbitProperties/s1:pass)",  # noqa: E501
        "processing:expression": "Text(systematic)",
        "processing:level": "Text(L0)",
        "processing:facility": "metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/s0:processing/s0:facility/@name",  # noqa: E501
        "processing:software": "to_processing_software(metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/s0:processing/s0:resource[2])",  # noqa: E501
        "platform": "to_str_lower(concat(metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/s0:platform/s0:familyName, metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/s0:platform/s0:number))",  # noqa: E501
        "instrument": "Text(%(instrument)s)" % dic,
        "constellation": "Text(sentinel-%s)" % product_type[2],
        "product:timeliness_category": "Text(%(timeliness_category)s)" % dic,
        "product:timeliness": "Text(%(timeliness)s)" % dic,
        "eopf:instrument_mode": "metadataSection/metadataObject[@ID='platform']/metadataWrap/xmlData/s0:platform/s0:instrument/s0:extension/s1sar:instrumentMode/s1sar:mode",  # noqa: E501
        "product:type": f"Text({product_type})",
        "providers": [
            {
                "name": "to_providers(metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/s0:processing/s0:facility/@site)",  # noqa: E501
                "roles": ["Text(processor)"],
            },
            {
                "name": "to_providers(metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/s0:processing/s0:facility/@organisation)",  # noqa: E501
                "roles": ["Text(producer)"],
            },
        ],
    }

    packet_fields = PACKET_FIELDS.get(product_type, {})
    if "dataTakeID" in packet_fields:
        packet = packet_fields["dataTakeID"]
        stac_properties["eopf:datatake_id"] = to_memmap_slice(
            product_type,
            packet,
            pattern="s1.*-??-.*(?<!annot)(?<!index)\\.dat",
        )

    return stac_properties


block_namespaces = XML_NAMESPACES


def to_memmap_slice(dpr_type: str, packet: PacketField, pattern: str) -> str:
    if packet.dpr_type == "var_bytearray":
        raise ValueError
    elif packet.dpr_type == "bool":
        return f"to_bool({pattern}:({packet.start},{packet.stop}):scalar_{packet.dpr_type})"
    else:
        return f"{pattern}:({packet.start},{packet.stop}):scalar_{packet.dpr_type}"


def build_block_other_metadata(dpr_type, **kwargs: Any) -> dict[str, Any]:
    args: dict[str, Any] = {}
    args["eopf_category"] = kwargs.get("eopf_category", "eocontainer")

    other_metadata = {
        "eopf_category": "Text(%(eopf_category)s)" % args,
        # TODO: add product_sensing_consolidation, receive_channel_id
        "consolidation": "metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:productConsolidation",  # noqa: E501
        "product_sensing_consolidation": "is_optional(metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:productSensingConsolidation)",  # noqa: E501
        "history": "to_processing_history(metadataSection/metadataObject[@ID='processing']/metadataWrap/xmlData/s0:processing)",  # noqa: E501
        "cycle_number": "to_int(metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/s0:orbitReference/s0:cycleNumber)",  # noqa: E501
        "phase_identifier": "to_int(metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/s0:orbitReference/s0:phaseIdentifier)",  # noqa: E501
        "start_datetime_anx": "metadataSection/metadataObject[@ID='acquisitionPeriod']/metadataWrap/xmlData/s0:acquisitionPeriod/s0:extension/s1:timeANX/s1:startTimeANX",  # noqa: E501
        "stop_datetime_anx": "metadataSection/metadataObject[@ID='acquisitionPeriod']/metadataWrap/xmlData/s0:acquisitionPeriod/s0:extension/s1:timeANX/s1:stopTimeANX",  # noqa: E501
    }

    for packet in PACKET_FIELD_LIST[dpr_type]:
        dpr_name = to_dpr_name(packet.name, PACKET_LEGACY_TO_DPR[dpr_type])
        if dpr_name in INCLUDE_DPR_METADATA.get(dpr_type, []) and packet.dpr_type != "var_bytearray":
            other_metadata_name = DPR_METADATA_ALIAS.get(dpr_name, dpr_name)
            other_metadata[other_metadata_name] = to_memmap_slice(
                dpr_type,
                packet,
                pattern="s1.*-??-.*(?<!annot)(?<!index)\\.dat",
            )

    return other_metadata


block_attr_stac_discovery = {
    "target_path": "attrs:/:stac_discovery",
    "source_path": "manifest.safe",
    "accessor_id": "xmlmetadata",
    "accessor_config": {
        "mapping": "@#copy{'map':'<SELF[stac_discovery]>'}#@",
        "namespaces": "@#copy{'map':'<SELF[namespaces]>'}#@",
        "path_template": "@#copy{'map':'<SELF[manifest_template_path]>'}#@",
    },
}
block_attr_other_metadata = {
    "target_path": "attrs:/:other_metadata",
    "source_path": "manifest.safe",
    "accessor_id": "xmlmetadata",
    "accessor_config": {
        "mapping": "@#copy{'map':'<SELF[other_metadata]>'}#@",
        "namespaces": "@#copy{'map':'<SELF[namespaces]>'}#@",
        "path_template": "@#copy{'map':'<SELF[manifest_template_path]>'}#@",
    },
}

block_other_metadata_from_memmap = {
    "target_path": "attrs:/:other_metadata",
    "source_path": "",
    "accessor_id": "MemMapToAttrAccessor",
    "accessor_config": {
        "mapping": "@#copy{'map':'<SELF[other_metadata]>'}#@",
        "types_mapping": "@#copy{'map':'<SELF[l0_mapping/types]>'}#@",
        "primary_header_length_bytes": 6,
        "ancillary_header_length_bytes": 0,
        "packet_length_start_position_bytes": 4,
        "packet_length_stop_position_bytes": 6,
    },
}


def build_block_unroll_l0_attr(**kwargs: Any):
    category = kwargs.get("category", "stac_discovery")
    dic = dict(
        pattern=kwargs.get("pattern", "s1.*-??-.*(?<!annot)(?<!index)\\.dat"),
        category=category,
        product_path=kwargs.get("product_path", "{{product_name}}"),
        eopf_category=kwargs.get("eopf_category", "eoproduct"),
    )

    unroll_line = (
        "@#find_unroll_l0{'product_url': '<URL>', 'pattern': '%s', 'json_data_in':'<VALUE>'}#@" % dic["pattern"]
    )
    mapping_block = {
        "target_path": "attrs:%(product_path)s:%(category)s" % dic,
        "source_path": "manifest.safe",
        "accessor_id": "xmlmetadata",
        "accessor_config": {
            "namespaces": "@#copy{'map':'<SELF[namespaces]>'}#@",
            "path_template": "@#copy{'map':'<SELF[manifest_template_path]>'}#@",
        },
    }

    if category == "other_metadata":
        mapping_block["accessor_config"]["mapping"] = {"eopf_category": "Text(%(eopf_category)s)" % dic}
    else:
        mapping_block["accessor_config"]["mapping"] = {}

    return {unroll_line: mapping_block}


def build_block_variable(**kwargs):
    """
    to create a block for "unroll" formatter, define both
      - key = "<local_path>"
      - source_path = "{{product_path}}"

    :param kwargs:
    :return:
    """
    key = kwargs["key"]
    dpr_tgt = kwargs["target_path"]
    accessor_id = kwargs.get("accessor_id", "L0Accessor")
    short_name = kwargs.get("short_name", dpr_tgt.split("/")[-1])
    long_name = (kwargs.get("long_name", dpr_tgt.split("/")[-1]),)
    attrs = {"long_name": long_name}
    attrs.update(kwargs.get("attrs", {}))
    source_path = kwargs.get("source_path", key)
    dimensions = kwargs.get("dimensions")

    block_variable = {
        "short_name": short_name,
        "source_path": source_path,
        "target_path": dpr_tgt,
        "accessor_id": accessor_id,
        "accessor_config": kwargs.get("accessor_config", {}),
        "transform": {"attributes": attrs, "rechunk": "@#copy{'map':'<SELF[chunk_sizes]>'}#@"},
    }
    if key != source_path:
        block_variable["local_path"] = key

    if dimensions:
        block_variable["transform"]["dimensions"] = dimensions

    coord_namespace = kwargs.get("coords_namespace")
    if coord_namespace:
        block_variable["coords_namespace"] = coord_namespace

    return block_variable


def build_block_unroll_l0_variable(**kwargs):
    dic = dict(pattern=kwargs.get("pattern", "s1.*-??-.*(?<!annot)(?<!index)\\.dat"))
    kwargs["source_path"] = kwargs.get("product_path", "{{product_path}}")
    unroll_line = "@#find_unroll_l0{'product_url': '<URL>', 'pattern': '%(pattern)s', 'json_data_in':'<VALUE>'}#@" % dic
    return {unroll_line: build_block_variable(**kwargs)}


def build_data_list(safe_path: Path) -> dict[str, dict[str, Any]]:
    manifest = ET.parse(safe_path / "manifest.safe")
    root = manifest.getroot()
    metadata = {}
    objects = {}
    for metadata_object in root.find("metadataSection"):
        for ref in metadata_object.findall("metadataReference"):
            ident = metadata_object.attrib.get("ID")
            metadata[ident] = ref.attrib.get("href")
    for data_object in root.find("dataObjectSection"):
        for byte_stream in data_object:
            stream: dict[str, Any] = {}
            stream["size"] = byte_stream.attrib.get("size")
            stream["path"] = byte_stream.find("fileLocation").attrib.get("href")
            stream["schema"] = metadata[data_object.attrib["repID"]]
            stream["id"] = data_object.attrib.get("ID")
            objects[stream["path"]] = stream

    return objects


def build_data_filenames(safe_name: str, generic_name: bool = True) -> list[str]:
    p = safe_name.lower().split("_")
    prefix = "-".join([p[0], p[1], p[2], p[4][1]])
    if generic_name:
        data_id = ".*"
    else:
        data_id = "-".join([p[5], p[6], p[7], p[8]])
    for suffix in [".dat", "-annot.dat"]:
        for polarization in POLARIZATIONS:
            data_name = f"{prefix}-{polarization}-{data_id}{suffix}"
            yield data_name


def initialize_l0_sar_mapping(dpr_type):
    data_mapping = [block_attr_stac_discovery, block_attr_other_metadata, block_other_metadata_from_memmap]
    mapping = {
        "recognition": {
            "filename_pattern": "TODO",
            "product_type": f"{dpr_type}",
            "processing_version": "2025",
        },
        "chunk_sizes": CHUNK_SIZES.get(dpr_type, {}),
        "l0_mapping": {"types": block_types, "annotation_mapping": block_types},
        "stac_discovery": {
            "type": "Text(Feature)",
            "stac_version": "Text(1.1.0)",
            "stac_extensions": block_stac_extensions,
            "id": "metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:productClassDescription",  # noqa: E501
            "geometry": "to_geoJson(metadataSection/metadataObject[@ID='measurementFrameSet']/metadataWrap/xmlData/s0:frameSet/s0:frame/s0:footPrint/gml:coordinates)",  # noqa: E501
            "bbox": "to_bbox(metadataSection/metadataObject[@ID='measurementFrameSet']/metadataWrap/xmlData/s0:frameSet/s0:frame/s0:footPrint/gml:coordinates)",  # noqa: E501
            "properties": {},
            "links": [{"rel": "Text(self)", "href": "Text(./.zattrs.json)", "type": "Text(application/json)"}],
            "assets": {},
        },
        "other_metadata": build_block_other_metadata(dpr_type),
        "manifest_template_path": {
            "template_folder": "$EOPF_ROOT/product/store/templates",
            "template_name": "S01_L0_manifest.xml",
        },
        "namespaces": block_namespaces,
        "data_mapping": data_mapping,
    }
    return mapping


def update_mapping_other_metadata(mapping, dpr_type):
    """
    # Update "other_metadata"
    """

    if dpr_type in PRODUCT_TYPES_SAR:
        mapping["other_metadata"].update(
            {
                "cal_isp_present": "metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:calISPPresent",  # noqa: E501
                "noise_isp_present": "metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:noiseISPPresent",  # noqa: E501
                "circulation_flag": "to_int(metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:circulationFlag)",  # noqa: E501
                "slice_product_flag": "metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:sliceProductFlag",  # noqa: E501
                "echo_compression_type": "is_optional(metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:echoCompressionType)",  # noqa: E501
                "noise_compression_type": "metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:noiseCompressionType",  # noqa: E501
                "cal_compression_type": "metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:calCompressionType",  # noqa: E501
                "transmitter_receiver_polarisation": "metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:transmitterReceiverPolarisation",  # noqa: E501
                "cycle_number": "to_int(metadataSection/metadataObject[@ID='measurementOrbitReference']/metadataWrap/xmlData/s0:orbitReference/s0:cycleNumber)",  # noqa: E501
                "packet_count": "to_int(metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:numOfElements)",  # noqa: E501
                "missing_packets": "to_int(metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:numOfMissingElements)",  # noqa: E501
                "corrupted_packets": "to_int(metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:numOfCorruptedElements)",  # noqa: E501
                "byte_order": "metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:byteOrder",  # noqa: E501
                "average_bit_rate": "to_int(metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:averageBitRate)",  # noqa: E501
                "packet_store_id": "to_int(metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:packetStoreID)",  # noqa: E501
            },
        )

    if dpr_type in ("S01SIWRAW", "S01EWRAW", "S01WVRAW"):
        # do not use to_int for packet_count, missing_packets, corrupted packets because here it is a coma separated
        # list and to_int do not support it.
        mapping["other_metadata"].update(
            {
                "ids": "metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:dataObjectID",  # noqa: E501
                "packet_count": "metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:numOfElements",  # noqa: E501
                "missing_packets": "metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:numOfMissingElements",  # noqa: E501
                "corrupted_packets": "metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:numOfCorruptedElements",  # noqa: E501
            },
        )

    elif dpr_type == "S01GPSRAW":
        mapping["other_metadata"]["quality"] = {
            "ids": "metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:dataObjectID",  # noqa: E501
            "packet_count": "to_int(metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:numOfElements)",  # noqa: E501
            "missing_packets": "to_int(metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:numOfMissingElements)",  # noqa: E501
            "corrupted_packets": "to_int(metadataSection/metadataObject[@ID='measurementQualityInformation']/metadataWrap/xmlData/s0:qualityInformation/s0:extension/s1:qualityProperties/s1:numOfCorruptedElements)",  # noqa: E501
        }


def update_mapping_header(mapping, dpr_type, safe_type):
    """
    # Update mapping header
    """
    if dpr_type == "S01RFCANC":
        recognition_pattern = f"S1[A-D]_RF_RAW__0S.*SAFE|{dpr_type}.*"
    elif dpr_type in PRODUCT_TYPES_SM:
        sm_id = safe_type[1]
        recognition_pattern = f"S1[A-D]_S{sm_id}_RAW__0S.*SAFE|{dpr_type}.*"
    elif dpr_type == "S01GPSRAW":
        recognition_pattern = f"S1[A-D]_GP_RAW__0____.*SAFE|{dpr_type}.*"
        mapping["other_metadata"]["eopf_category"] = "Text(eoproduct)"
    elif dpr_type == "S01AISRAW":
        recognition_pattern = f"S1[A-D]_AI_RAW__0____.*SAFE|{dpr_type}.*"
        mapping["other_metadata"]["eopf_category"] = "Text(eoproduct)"
    elif dpr_type == "S01HKMRAW":
        recognition_pattern = f"S1[A-D]_HK_RAW__0____.*SAFE|{dpr_type}.*"
        mapping["other_metadata"]["eopf_category"] = "Text(eoproduct)"
    elif dpr_type in ("S01SEWRAW", "S01SIWRAW", "S01SWVRAW", "S01ENRAW_"):
        code = safe_type[:2]
        recognition_pattern = f"S1[A-D]_{code}_RAW__0S.*SAFE|{dpr_type}.*"
    elif dpr_type.startswith("S01N"):
        sm_id = safe_type[1]
        recognition_pattern = f"S1[A-D]_N{sm_id}_RAW__0S.*SAFE|{dpr_type}.*"
    else:
        recognition_pattern = "TODO"
    mapping["recognition"]["filename_pattern"] = recognition_pattern
    if dpr_type in PRODUCT_TYPES_SM or dpr_type in PRODUCT_TYPES_AN_EN:
        mapping["finalize_function"] = {
            "module": "l0.common.eopf_converters.S01L0",
            "class": "ExtractNoiseFromEcho",
        }

    elif dpr_type in PRODUCT_TYPES_EW_IW_WV:
        mapping["finalize_function"] = {
            "module": "l0.common.eopf_converters.S01L0",
            "class": "SplitByBurstAndSwath",
        }
    elif dpr_type == "S01GPSRAW":
        mapping["finalize_function"] = {
            "module": "l0.common.eopf_converters.S01L0",
            "class": "GPSRawFinalization",
        }


def update_mapping_accessor_config(mapping, dpr_type):
    """
    # Accessor config
    """
    if dpr_type in ("S01GPSRAW", "S01AISRAW"):
        accessor_config = {"product_type": dpr_type}
    elif dpr_type == "S01HKMRAW":
        accessor_config = {
            "product_type": dpr_type,
            "packet_fixed_length": 1912,
        }
    else:
        accessor_config = {
            "signalType": {"echo": 0, "noise": 1, "calibration": [9, 8, 10, 11, 12, 15]},
            "product_type": dpr_type,
        }
    mapping["l0_mapping"]["accessor_config_l0"] = accessor_config


def update_mapping_stac_properties(mapping, dpr_type):
    """
    # Update stac properties
    """
    properties_args = {}
    mapping["stac_discovery"]["properties"] = build_stac_properties(dpr_type, **properties_args)
    # add datatake_id
    if dpr_type in PRODUCT_TYPES_SAR:
        mapping["stac_discovery"]["properties"][
            "eopf:datatake_id"
        ] = "to_int(metadataSection/metadataObject[@ID='generalProductInformation']/metadataWrap/xmlData/s1sar:standAloneProductInformation/s1sar:missionDataTakeID)"  # noqa E501


def generate_data_mapping_attributes(dpr_type, builder_kwargs):
    """
    # Initialize container by associating metadata
    """
    # for GPSRAW, HKMRAW, neither subcontainer nor subproduct => nothing to add here
    data_mapping_attributes = []
    if dpr_type == "S01RFCANC" or dpr_type in PRODUCT_TYPES_EW_IW_WV:
        data_mapping_attributes += [
            build_block_unroll_l0_attr(category="stac_discovery", **builder_kwargs),
            build_block_unroll_l0_attr(category="other_metadata", **builder_kwargs),
        ]
    elif dpr_type in SMi_Ni:
        data_mapping_attributes += [
            build_block_unroll_l0_attr(
                category="stac_discovery",
                product_path="{{product_name}}",
                eopf_category="eocontainer",
                **builder_kwargs,
            ),
            build_block_unroll_l0_attr(
                category="other_metadata",
                product_path="{{product_name}}",
                eopf_category="eocontainer",
                **builder_kwargs,
            ),
            build_block_unroll_l0_attr(
                category="stac_discovery",
                product_path="{{subproduct_raw_name}}",
                **builder_kwargs,
            ),
            build_block_unroll_l0_attr(
                category="other_metadata",
                product_path="{{subproduct_raw_name}}",
                **builder_kwargs,
            ),
            build_block_unroll_l0_attr(
                category="stac_discovery",
                product_path="{{subproduct_anc_name}}",
                **builder_kwargs,
            ),
            build_block_unroll_l0_attr(
                category="other_metadata",
                product_path="{{subproduct_anc_name}}",
                **builder_kwargs,
            ),
        ]

    return data_mapping_attributes


def generate_data_mapping_sensing_time(dpr_type, main_dat_pattern, signal_types, builder_kwargs):
    """
    # add sensing_time coord
    """
    accessor_config = (
        "@#copy_and_extend{'map':'<SELF[l0_mapping/accessor_config_l0]>', 'pattern':'%(pattern)s'}#@" % builder_kwargs
    )

    data_mapping_sensing_time = []
    # sensing_time coordinate
    if dpr_type in PRODUCT_TYPES_EW_IW_WV:
        data_mapping_sensing_time.append(
            build_block_unroll_l0_variable(
                target_path="coords:{{polarization}}:sensing_time",
                key="sensing_time",
                dimensions=["packet_number"],
                short_name=generate_short_name("sensing_time", ""),
                long_name="sensing time",
                **builder_kwargs,
            ),
        )
    else:
        for signal_type in signal_types:
            data_mapping_sensing_time.append(
                build_block_unroll_l0_variable(
                    target_path="coords:{{polarization}}_%s:sensing_time" % signal_type,
                    key="sensing_time/signalType=%s" % signal_type,
                    dimensions=["packet_number"],
                    short_name=generate_short_name("sensing_time", signal_type),
                    long_name="sensing time",
                    **builder_kwargs,
                ),
            )

    if dpr_type == "S01GPSRAW":
        # build sensing_time for each sid
        data_mapping_sensing_time.append(
            build_block_unroll_l0_variable(
                target_path="coords:sid_{{product_id}}:sensing_time",
                key="sensing_time",
                dimensions=["packet_number"],
                short_name="{{product_id}}_sensing_time",
                long_name="Sensing time",
                **builder_kwargs,
            ),
        )
    if dpr_type == "S01AISRAW":
        data_mapping_sensing_time.append(
            build_block_variable(
                target_path="coords:sensing_time",
                key="sensing_time",
                source_path="@#find{'product_url': '<URL>','pattern': '%s'}#@" % main_dat_pattern,
                dimensions=["packet_number"],
                long_name="sensing_time",
                short_name="sensing_time",
                accessor_config=accessor_config,
            ),
        )
    return data_mapping_sensing_time


def generate_data_mapping_measurements(dpr_type, main_dat_pattern, signal_types, builder_kwargs, kwargs):
    """
    # add echo/noise/variables or isp
    """
    # signal_types is empty for GPSRAW, ... so nothing is done for these products. See after
    flag_isp = {
        "noise": kwargs.get("add_noise", True),
        "calibration": kwargs.get("add_calibration", True),
        "echo": kwargs.get("add_echo", True),
    }
    data_mapping_measurements = []

    if dpr_type in PRODUCT_TYPES_EW_IW_WV:
        data_mapping_measurements.append(
            build_block_unroll_l0_variable(
                target_path="{{product_name}}/measurements/isp",
                key="userData",
                coords_namespace="{{polarization}}",
                dimensions=ISP_DIMENSIONS,
                **builder_kwargs,
            ),
        )

    else:
        for signal_type, product_id in signal_types.items():
            # measurement variable
            if flag_isp.get(signal_type, True):
                if signal_type == "echo":
                    target_path = f"{product_id}/measurements/{signal_type}"
                else:
                    target_path = f"{product_id}/measurements/{signal_type}/{signal_type}"

                long_name = generate_long_name("userData", signal_type, PACKET_LEGACY_TO_DPR[dpr_type])
                data_mapping_measurements.append(
                    build_block_unroll_l0_variable(
                        target_path=target_path,
                        key=f"userData/signalType={signal_type}",
                        coords_namespace="{{polarization}}_%s" % signal_type,
                        dimensions=ISP_DIMENSIONS,
                        long_name=long_name,
                        short_name=generate_short_name("user_data", signal_type),
                        **builder_kwargs,
                    ),
                )
    if dpr_type == "S01GPSRAW":
        if flag_isp.get("isp", True):
            for src_name, dpr_name, dimensions in [
                ("measurementData", "isp", ISP_DIMENSIONS),
                ("packetSequenceCount", None, ["packet_number"]),
            ]:
                long_name = generate_long_name(src_name, None, PACKET_LEGACY_TO_DPR[dpr_type])
                if dpr_name is None:
                    dpr_name = to_dpr_name(src_name, PACKET_LEGACY_TO_DPR[dpr_type])
                data_mapping_measurements.append(
                    build_block_unroll_l0_variable(
                        target_path="measurements/sid-{{product_id}}/%s" % dpr_name,
                        key=src_name,
                        coords_namespace="sid_{{product_id}}",
                        dimensions=dimensions,
                        long_name=long_name,
                        short_name=generate_short_name(dpr_name),
                        **builder_kwargs,
                    ),
                )

    elif dpr_type == "S01HKMRAW":
        if flag_isp.get("transfer_frames", True):
            long_name = generate_long_name("mpduPacketZone", None, PACKET_LEGACY_TO_DPR[dpr_type])
            data_mapping_measurements.append(
                build_block_variable(
                    target_path="measurements/transfer_frames",
                    source_path="@#find{'product_url': '<URL>','pattern': '%s'}#@" % main_dat_pattern,
                    key="mpduPacketZone",
                    dimensions=["transfer_frame_number", "transfer_frame_length"],
                    long_name=long_name,
                    short_name=generate_short_name("transfer_frames"),
                    **builder_kwargs,
                ),
            )

    elif dpr_type == "S01AISRAW":
        if flag_isp.get("isp", True):
            long_name = generate_long_name("userData", None, PACKET_LEGACY_TO_DPR[dpr_type])
            data_mapping_measurements.append(
                build_block_variable(
                    target_path="measurements/isp",
                    source_path="@#find{'product_url': '<URL>','pattern': '%s'}#@" % main_dat_pattern,
                    key="userData",
                    dimensions=ISP_DIMENSIONS,
                    long_name=long_name,
                    short_name=generate_short_name("isp"),
                    **builder_kwargs,
                ),
            )
    return data_mapping_measurements


def generate_data_mapping_conditions(dpr_type, main_dat_pattern, builder_kwargs):
    """
    # add conditions variables
    """
    if dpr_type in PRODUCT_TYPES_SAR:
        include_list = ["packet_data_length", "radar_sample_count_service"]
    elif dpr_type == "S01HKMRAW":
        include_list = [
            "transfer_frame_version_number",
            "spacecraft_id",
            "virtual_channel_id",
            "virtual_channel_frame_count",
            "replay_flag",
            "reserved_spare_flags",
            "frame_header_error_control",
            "m_pdu_headers",
        ]
    else:
        include_list = ["packet_data_length"]

    if dpr_type == "S01RFCANC":
        conditions_paths = [
            ("noise", "{{product_name}}/conditions/noise", ALL_ANC_CONDITIONS),
            ("calibration", "{{product_name}}/conditions/calibration", ALL_ANC_CONDITIONS),
        ]
    elif dpr_type in PRODUCT_TYPES_EW_IW_WV:
        # See note for EW/IW/VW products
        conditions_paths = [
            ("*", "{{product_name}}/measurements/", ALL_ANC_CONDITIONS),
        ]
        include_list = ALL_ANC_CONDITIONS
    elif dpr_type in SMi_Ni_EW_IW_WV:
        conditions_paths = [
            ("echo", "{{subproduct_raw_name}}/conditions", include_list),
            ("noise", "{{subproduct_anc_name}}/conditions/noise", ALL_ANC_CONDITIONS),
            ("calibration", "{{subproduct_anc_name}}/conditions/calibration", ALL_ANC_CONDITIONS),
            ("echo", "{{subproduct_anc_name}}/conditions/echo", ALL_ANC_CONDITIONS),
        ]
        include_list = ALL_ANC_CONDITIONS
    elif dpr_type == "S01GPSRAW":
        conditions_paths = [("*", "conditions/sid-{{product_id}}", include_list)]
    else:
        conditions_paths = []

    data_mapping_conditions = []

    if dpr_type in PRODUCT_TYPES_EW_IW_WV:
        for packet in PACKET_FIELD_LIST[dpr_type]:
            src_name = packet.name
            dpr_name = to_dpr_name(src_name, PACKET_LEGACY_TO_DPR[dpr_type])
            if dpr_name not in include_list:
                continue
            data_mapping_conditions.append(
                build_block_unroll_l0_variable(
                    target_path="{{product_name}}/measurements/%s" % dpr_name,
                    key=src_name,
                    coords_namespace="{{polarization}}",
                    dimensions=["packet_number"],
                    long_name=generate_long_name(src_name, "", PACKET_LEGACY_TO_DPR[dpr_type]),
                    short_name=generate_short_name(dpr_name, ""),
                    **builder_kwargs,
                ),
            )

    elif dpr_type in PRODUCT_TYPES_SAR:
        for signal_type, condition_root_path, condition_include_list in conditions_paths:
            for packet in PACKET_FIELD_LIST[dpr_type]:
                src_name = packet.name
                dpr_name = to_dpr_name(src_name, PACKET_LEGACY_TO_DPR[dpr_type])
                if dpr_name not in condition_include_list:
                    continue

                target_path = f"{condition_root_path}/{dpr_name}"

                data_mapping_conditions.append(
                    build_block_unroll_l0_variable(
                        target_path=target_path,
                        key="%s/signalType=%s" % (src_name, signal_type),
                        coords_namespace="{{polarization}}_%s" % signal_type,
                        dimensions=["packet_number"],
                        long_name=generate_long_name(src_name, signal_type, PACKET_LEGACY_TO_DPR[dpr_type]),
                        short_name=generate_short_name(dpr_name, signal_type),
                        **builder_kwargs,
                    ),
                )

    # "n" dat files in legacy products
    # compute global conditions and put them in /conditions
    elif dpr_type == "S01GPSRAW":
        # add packet_data_length foreach sid
        for signal_type, condition_root_path, condition_include_list in conditions_paths:
            for packet in PACKET_FIELD_LIST[dpr_type]:
                src_name = packet.name
                dpr_name = to_dpr_name(src_name, PACKET_LEGACY_TO_DPR[dpr_type])
                if dpr_name not in condition_include_list:
                    continue

                target_path = f"{condition_root_path}/{dpr_name}"

                data_mapping_conditions.append(
                    build_block_unroll_l0_variable(
                        target_path=target_path,
                        key=src_name,
                        coords_namespace="sid_{{product_id}}",
                        dimensions=["packet_number"],
                        long_name=generate_long_name(src_name, signal_type, PACKET_LEGACY_TO_DPR[dpr_type]),
                        short_name=generate_short_name(dpr_name, signal_type),
                        **builder_kwargs,
                    ),
                )
    #  subset of conditions extracted in /conditions/
    elif dpr_type in ("S01HKMRAW", "S01AISRAW"):
        if dpr_type == "S01HKMRAW":
            dimensions = ["transfer_frame_number"]
        else:
            dimensions = ["packet_number"]
        for packet in PACKET_FIELD_LIST[dpr_type]:
            src_name = packet.name
            dpr_name = to_dpr_name(src_name, PACKET_LEGACY_TO_DPR[dpr_type])
            if dpr_name not in include_list:
                continue

            data_mapping_conditions.append(
                build_block_variable(
                    target_path=f"conditions/{dpr_name}",
                    source_path="@#find{'product_url': '<URL>','pattern': '%s'}#@" % main_dat_pattern,
                    key=src_name,
                    dimensions=dimensions,
                    long_name=generate_long_name(src_name, PACKET_LEGACY_TO_DPR[dpr_type]),
                    short_name=generate_short_name(dpr_name),
                    **builder_kwargs,
                ),
            )
    return data_mapping_conditions


def build_mapping(safe_type: str, **kwargs: Any) -> dict[str, Any]:

    dpr_type = SAFE_TO_DPR_PTYPE[safe_type]
    mapping = initialize_l0_sar_mapping(dpr_type)
    data_mapping = mapping["data_mapping"]

    # TODO: support short names
    # TODO: extract long name from old mappings and create dict dpr_target -> long name

    main_dat_pattern = "s1.*-??-.*(?<!annot)(?<!index)\\.dat"
    builder_kwargs = dict(
        pattern=main_dat_pattern,
        accessor_config="@#copy{'map':'<SELF[l0_mapping/accessor_config_l0]>'}#@",
    )

    # packet defined here are added to "conditions" group
    if dpr_type == "S01RFCANC":
        signal_types = {"noise": "{{product_name}}", "calibration": "{{product_name}}"}
    elif dpr_type in SMi_Ni_EW_IW_WV:
        signal_types = {
            "noise": "{{subproduct_anc_name}}",
            "calibration": "{{subproduct_anc_name}}",
            "echo": "{{subproduct_raw_name}}",
        }
    else:
        signal_types = {}

    # NOTE FOR EW/IW/VW PRODUCTS:
    # For EW/IW/VW we create a structure corresponding to L0 ProcessUnit input
    # then L0 Process Units will reorganize it to match final zarr structure
    # that is why all conditions are set in measurements instead of conditions for example

    update_mapping_header(mapping, dpr_type, safe_type)
    update_mapping_accessor_config(mapping, dpr_type)
    update_mapping_stac_properties(mapping, dpr_type)
    update_mapping_other_metadata(mapping, dpr_type)
    data_mapping += generate_data_mapping_attributes(dpr_type, builder_kwargs)
    data_mapping += generate_data_mapping_sensing_time(dpr_type, main_dat_pattern, signal_types, builder_kwargs)
    if kwargs.get("add_measurements", True):
        data_mapping += generate_data_mapping_measurements(
            dpr_type,
            main_dat_pattern,
            signal_types,
            builder_kwargs,
            kwargs,
        )

    if kwargs.get("add_conditions", True):
        data_mapping += generate_data_mapping_conditions(dpr_type, main_dat_pattern, builder_kwargs)

    return mapping


def update_mapping(safe_type: str, **kwargs: Any) -> None:
    """
    :param safe_type:
    :param kwargs:
    :return:
    """
    ptype = SAFE_TO_DPR_PTYPE[safe_type]

    mapping_path_dir_cpm = get_resource_path("mapping", module="eopf.store")
    mapping_path_cpm = mapping_path_dir_cpm / f"{ptype}.json"

    # mapping_path_dir_l0 = get_resource_path("mappings", module="l0.common.eopf_converters")
    # mapping_path_l0 = mapping_path_dir_l0 / f"{ptype}.json"

    raw_mapping = build_mapping(safe_type, **kwargs)
    for mapping_path in (mapping_path_cpm,):  # mapping_path_l0):
        print(f"write mapping {mapping_path}")
        with open(mapping_path, "w") as json_fp:
            json.dump(raw_mapping, json_fp, indent=4, cls=DataTreeJSONEncoder)
            json_fp.write("\n")


def extract_datatake_id(manifest_eop: EOProduct) -> str:
    # datatake_id is currently extracted from manifest.safe missionDataTakeID but it may be extracted from
    # "s1.*-??-.*(?<!annot)(?<!index)\\.dat:(128,160):scalar_uint32 (full datatake_id) and then converted to hex
    # in my tests, both values were identical
    datatake_id = manifest_eop.attrs["stac_discovery"]["properties"]["eopf:datatake_id"]
    # 327604 -> "4FFB4"
    return str(hex(datatake_id)).replace("0x", "").upper()


if __name__ == "__main__":
    from pathlib import Path

    import click
    from eopf import EOSafeStore
    from eopf.common.file_utils import AnyPath

    @click.command()
    @click.argument("product_type", type=str, default="")
    @click.option("--metadata-only", is_flag=True, help="Only generate metadata fields")
    @click.option("--no-measurements", is_flag=True, help="Skip measurement fields")
    @click.option("--no-conditions", is_flag=True, help="Skip condition fields")
    @click.option("--update-all", is_flag=True, help="Update all product type mappings")
    def main(product_type: str, metadata_only: bool, no_measurements: bool, no_conditions: bool, update_all: bool):
        """Update L0 product mappings.

        PRODUCT_TYPE: Type of product mapping to update (e.g. S01GPSRAW, IW_RAW_, etc.)
        """
        kwargs = {
            "add_measurements": not no_measurements and not metadata_only,
            "add_conditions": not no_conditions and not metadata_only,
        }
        if not product_type:
            update_all = True

        if update_all:
            # Update all mappings
            update_mapping("EN_RAW_", **kwargs)
            update_mapping("RF_RAW_", **kwargs)
            update_mapping("GP_RAW_", **kwargs)
            update_mapping("HK_RAW_", **kwargs)
            update_mapping("AI_RAW_", **kwargs)

            for i in range(1, 7):
                update_mapping(f"S{i}_RAW_", **kwargs)
            for i in range(1, 7):
                update_mapping(f"N{i}_RAW_", **kwargs)

            update_mapping("EW_RAW_", **kwargs)
            update_mapping("WV_RAW_", **kwargs)
            update_mapping("IW_RAW_", **kwargs)
        else:
            # Update single mapping
            update_mapping(product_type_dpr_to_legacy.get(product_type), **kwargs)

    main()
