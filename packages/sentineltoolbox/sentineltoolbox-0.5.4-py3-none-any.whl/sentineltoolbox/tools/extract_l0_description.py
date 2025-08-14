import ast
import json
from typing import Any

from l0.common.eopf_converters.l0_accessors import PACKET_FIELD_LIST

from sentineltoolbox.readers.resources import get_resource_path


def extract_packet_attributes_from_mappings(dpr_type, **kwargs: Any):
    pck_id_to_pos = {}
    pck_pos_to_id = {}

    for packet in PACKET_FIELD_LIST[dpr_type]:
        packet_id = packet.name
        pos = (packet.start, packet.stop)
        pck_id_to_pos[packet_id] = pos
        pck_pos_to_id[pos] = packet_id

    long_names = {}
    dpr_names = {}
    mapping_path_dir = get_resource_path("mapping", module="eopf.store")
    for mapping_path in mapping_path_dir.glob("*EWRAW*.json"):
        print(mapping_path)
        # raw_mapping = build_mapping(safe_type, **kwargs)
        # print(f"write mapping {mapping_path}")
        with open(mapping_path, "r") as json_fp:
            mapping = json.load(json_fp)
            for data in mapping["data_mapping"]:
                k = list(data.keys())[0]
                if k.startswith("@#"):
                    data = data[k]
                    local_path = data.get("local_path")
                    target_path = data.get("target_path")

                    if local_path:
                        local_path = data.get("local_path")
                        target_path = data.get("target_path")
                        desc = data.get("transform", {}).get("attributes", {}).get("long_name")
                        try:
                            sl = slice(*ast.literal_eval(local_path))
                        except SyntaxError:
                            continue
                        pos = (sl.start, sl.stop)
                        if pos in pck_pos_to_id:
                            packet_id = pck_pos_to_id[pos]
                            long_names[packet_id] = desc
                            dpr_names[packet_id] = target_path.split("/")[-1].replace("_vh", "").replace("_hh", "")
    return dict(long_name=long_names, dpr_name=dpr_names)


if __name__ == "__main__":
    attrs = extract_packet_attributes_from_mappings("S01RFCANC")
    for attr_name, data in attrs.items():
        print("\n", attr_name)
        print(json.dumps(data, indent="", sort_keys=True))
