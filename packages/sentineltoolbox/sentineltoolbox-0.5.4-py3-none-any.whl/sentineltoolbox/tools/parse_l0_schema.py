import pprint

from l0.common.eopf_converters.l0_accessors import PacketField

from sentineltoolbox.readers.resources import load_resource_file
from sentineltoolbox.resources.data import NAMESPACES
from sentineltoolbox.tools.update_mappings_l0 import (
    EXCLUDED_FLAG,
    to_dpr_name,
)

L0_YAML_SCHEMA_FILENAMES = {
    "S01RFCANC": "schema_s1_sar.yaml",
    "S01GPSRAW": "schema_s1_gps.yaml",
    "S01HKMRAW": "schema_cadus.yaml",
    "S01AISRAW": "schema_s1_ais.yaml",
}


def extract_dpr_names_from_yaml_schema(schema):
    fields = {}
    for header_name, header in schema.items():
        fields.update(header)
    position_to_name = {}
    for dpr_name, data in fields.items():
        start = data.get("bit_offset")
        length = data.get("bit_length")
        if start is not None and length:
            stop = start + length
            position_to_name[(start, stop)] = dpr_name
    return position_to_name


def build_legacy_to_dpr_name_from_yaml_schema(packets, schema, **kwargs):
    mapping = {}
    position_to_name = extract_dpr_names_from_yaml_schema(schema)
    for packet in packets:
        position = (packet.start, packet.stop)
        dpr_name = position_to_name.get(position, EXCLUDED_FLAG)
        mapping[packet.name] = dpr_name
    return mapping


def update_complex_types(complex_type, root_name, simpletypedefs, typedefs, aliases):
    ns = NAMESPACES
    typename = complex_type.attrib["name"]
    if root_name:
        typename = root_name + "." + typename
    sequence = complex_type.find("xs:sequence", namespaces=ns)
    if sequence is None:
        dtype = complex_type.attrib.get("type")
        if dtype:
            typedefs[typename] = {"type": dtype}
        else:
            print("ERROR", typename, complex_type.attrib)
    else:
        for child in sequence:
            child_type = child.attrib.get("type")
            child_name = child.attrib["name"]
            if child_type in simpletypedefs:
                typedefs[f"{typename}.{child_name}"] = simpletypedefs[child_type]
            else:
                update_complex_types(child, typename, simpletypedefs, typedefs, aliases)
            typedefs.setdefault(typename, []).append(f"{typename}.{child_name}")


def build_typedefs(root):
    ns = NAMESPACES
    typedefs = {}
    simpletypedefs = {"xs:unsignedByte": {"size": 8}, "xs:unsignedShort": {"size": 16}}
    aliases = {}

    for e in root.findall("xs:simpleType", namespaces=ns):
        typedef = {}
        typename = e.attrib["name"]
        block = e.find("xs:annotation/xs:appinfo/sdf:block", namespaces=ns)
        if block is None:
            continue

        length = block.find("sdf:length", namespaces=ns)
        if length is not None:
            value = length.text
            unit = length.attrib.get("unit")
            if unit == "bit":
                typedef["size"] = int(value)
            elif unit is None:
                typedef["size"] = 8 * int(value)
            else:
                print(f"ERROR: {unit=} not supported for {typename!r}")
        else:
            print(f"ERROR: {typename!r} not supported")
        typedefs[typename] = typedef
        simpletypedefs[typename] = typedef

    for e in root.findall("xs:complexType", namespaces=ns):
        update_complex_types(e, None, simpletypedefs, typedefs, aliases)

    return dict(simpletypes=simpletypedefs, alltypes=typedefs, aliases=aliases)


def update_elements(inp_type, elements, typedefs, aliases, start=0):
    size = typedefs[inp_type]
    if isinstance(size, list):
        for e in size:
            alias = e
            for k, v in aliases.items():
                alias = alias.replace(k, v)
            aliases[e] = alias
            start = update_elements(e, elements, typedefs, aliases, start=start)
        return start
    else:
        if "type" in size:
            alias = size["type"]
            for k, v in aliases.items():
                alias = alias.replace(k, v)
            aliases[size["type"]] = alias
            return update_elements(alias, elements, typedefs, aliases, start=start)
        else:
            size_in_bytes = size["size"]
            alias = inp_type
            for k, v in aliases.items():
                alias = alias.replace(k, v)
            aliases[inp_type] = alias
            if size_in_bytes == -1:
                elements[alias] = (alias, start, None)
                stop = -1
            else:
                stop = start + size_in_bytes
                elements[alias] = (alias, start, stop)
            return stop


def extract_packet_fields_from_l0_schema(root):
    """

    Extract packet fields from L0 xsd schemas.

    IMPORTANT: this code doesn't support full schema spec and result may contain errors, especially for non fixed
    size like userData. Please double check result and fix it manually!

    Usage

    import xml.etree.cElementTree as ET
    build_elements(ET.parse("support/L0_schema.xsd"))

    this code generate a dict like
    {'mainHeaderType.packetVersionNumber': (0, 3, 'packet_version_number'),
    'mainHeaderType.packetType': (3, 4, 'packet_type'),
    ...
    }

    :param root:
    :return:
    """
    ns = NAMESPACES
    typedefs = build_typedefs(root)
    alltypedefs = typedefs["alltypes"]
    alltypedefs["secondaryHeaderType.syncMarker"] = {"size": 32}
    alltypedefs["ispType.userData"] = {"size": -1}
    alltypedefs["ispType.sourceData"] = {"size": -1}
    alltypedefs["ispType.measurementData"] = {"size": -1}
    alltypedefs["tpType.mpduPacketZone"] = {"size": -1}

    elements = {}
    start = 0

    for e in root.findall("xs:element", namespaces=ns):
        name = e.attrib.get("name")
        dtype = e.attrib.get("type")
        aliases = {dtype: name}
        start = update_elements(dtype, elements, alltypedefs, aliases, start)

    fixed_elements = []
    fix = {
        "primaryHeaderType": "primaryHeader",
        "secondaryHeaderType": "secondaryHeader",
        "ispType.userData": "userData",
    }

    for k, v in elements.items():
        for before, after in fix.items():
            k = k.replace(before, after)
        fixed_elements.append(PacketField(*v))

    return fixed_elements


def build_legacy_to_dpr_mapping(packets, dpr_type):
    if dpr_type and dpr_type in L0_YAML_SCHEMA_FILENAMES:
        schema_name = L0_YAML_SCHEMA_FILENAMES[dpr_type]
        schema = load_resource_file(schema_name, module="l0.cadu_processing.schemas")
        print(f"generate packets mapping using {schema_name}")
        mapping = build_legacy_to_dpr_name_from_yaml_schema(packets, schema)
    else:
        mapping = {}
        for packet in packets:
            mapping[packet.name] = to_dpr_name(packet.name, {})
    return mapping


if __name__ == "__main__":
    from pathlib import Path

    import defusedxml.ElementTree as ET

    root = Path("/opt/DATA/L0_DATA/L0_supports")
    for dpr_type, group in {
        "S01RFCANC": ["S1A_RF_RAW_s1-level-0.xsd"],
        "S01GPSRAW": ["S1A_GP_RAW_s1-level-0.xsd"],
        "S01HKMRAW": ["S1A_HK_RAW_s1-level-0.xsd"],
        "S01AISRAW": ["S1A_AI_RAW_s1-level-0.xsd"],
    }.items():
        print("*" * 80)
        print(dpr_type)
        print("*" * 80)
        for xsd_path in group:
            print(xsd_path)
            xml = ET.parse((root / xsd_path).as_posix())
            lst = extract_packet_fields_from_l0_schema(xml)
            pprint.pp(lst, width=120)

            mapping = build_legacy_to_dpr_mapping(lst, dpr_type=dpr_type)
            pprint.pp(mapping, width=120)
