# type: ignore
import copy
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Literal

import cql2

from sentineltoolbox.filesystem_utils import get_universal_path
from sentineltoolbox.resources.data import DATAFILE_METADATA

global_param = [
    "processor_name",
    # 'version',
    # 'min_disk_space',
    # 'max_time'
]


def to_dpr_type(legacy_type):
    dpr_type = DATAFILE_METADATA.to_dpr_ptype(legacy_type)
    if isinstance(dpr_type, list):
        if not len(dpr_type):
            if legacy_type.endswith("_G"):
                return to_dpr_type(legacy_type[:-1] + "_")
            else:
                return None
        else:
            return dpr_type
    else:
        return dpr_type


def build_property(name, property_dict):
    default_name = "{local_variables.%s}" % name
    return {"op": "=", "args": [{"property": name}, property_dict.get(name, default_name)]}


def _build_op_offset(op, variable, interval, offset):
    return {
        "op": op,
        "args": [
            {"property": variable},
            {"interval": [interval[0], interval[1]]},
            {"start_offset": offset[0]},
            {"end_offset": offset[1]},
        ],
    }


DEFAULT_CQL2_PROPERTIES = dict(
    Ta="global_variables.start_datetime",
    Tb="global_variables.stop_datetime",
    dTa="local_variables.dTa",
    dTb="local_variables.dTb",
    product_type="global_variables.product_type",
)


def build_prop_def(prop_names, prop_dict):
    """
    prop_names: ["name1", "name2"]
    prop_dict: {"name1": "tasktable.path1", ...}

    -> "name1='{tasktable.path1}' AND name2='{tasktable.path2}'"
    """
    cql_defs_txt = {}
    for ident, path in prop_dict.items():
        cql_defs_txt[ident] = "%s='{%s}'" % (ident, path)

    lst = [cql_defs_txt[ident] for ident in prop_names]
    return " AND ".join(lst)


def extract_properties(d, parent=None, replace=None):
    if replace is None:
        replace = {}
    if isinstance(d, dict):
        if "property" in d:
            name = d["property"]
            if name in replace and parent:
                if isinstance(parent, list):
                    for i, v in enumerate(parent):
                        if v == {"property": name}:
                            parent[i] = "{" + replace[name] + "}"
                elif isinstance(parent, dict):
                    for k, v in parent.items():
                        if v == {"property": name}:
                            parent[k] = "{" + replace[name] + "}"

            yield name
        else:
            for k, v in d.items():
                yield from extract_properties(v, parent=d, replace=replace)
    elif isinstance(d, list):
        for v in d:
            yield from extract_properties(v, parent=d, replace=replace)


def cql_txt_to_json(
    cql_query,
    property_mode: Literal["property", "inline_def", "replace"] = "property",
    property_dict=None,
    **kwargs,
):
    """
    property_mode:
        - property: only write property:
            text command: "name"
            json: {'property': 'name'}
        - inline_def: write select query and property:
            text command: name='{tasktable.path}' AND filter_command(name)
            json:
            {'op': 'and', 'args': [
              {'op': '=', 'args': [{'property': 'name'}, '{tasktable.path}']},
              {'op': 'filter_command', 'args': [{'property': 'name'}]}
            ]}
        - replaced:  replace by path
            text command: "'{tasktable.path}'"

    :param cql_query:
    :param property_mode:
    :return:
    """
    # fix properties if necessary
    lst = []
    parsed_query = cql2.parse_text(cql_query).to_json()
    if property_mode == "inline_def":
        properties = list(extract_properties(parsed_query))
        for prop_name in properties:
            if prop_name in property_dict:
                lst.append(prop_name)
        if lst:
            cql_query = build_prop_def(lst, property_dict) + " AND " + cql_query
            parsed_query = cql2.parse_text(cql_query).to_json()
    elif property_mode == "replace":
        parsed_query = cql2.parse_text(cql_query).to_json()
        list(extract_properties(parsed_query, replace=property_dict))

    return parsed_query


SORT_START = [{"field": "start_datetime", "direction": "desc"}]
SORT_STOP = [{"field": "stop_datetime", "direction": "desc"}]
SORT_OVERLAP = [{"field": "overlap", "direction": "desc"}]

MODE_VAL_INTERSECT: dict[str, Any] = {
    "command": "T_INTERSECTS(INTERVAL(start_datetime, end_datetime), INTERVAL(Ta-dTa, Tb+dTb))",
    "sort": SORT_START,
}

# ValIntersect + sort=start_datetime + limit=1,
MODE_LATEST_VAL_INTERSECT = copy.copy(MODE_VAL_INTERSECT)
MODE_LATEST_VAL_INTERSECT["limit"] = 1

MODE_VAL_COVER = {
    "command": "T_CONTAINS(INTERVAL(start_datetime, end_datetime), INTERVAL(Ta-dTa, Tb+dTb))",
    "sort": SORT_START,
}
MODE_LATEST_VAL_COVER = copy.copy(MODE_VAL_INTERSECT)
MODE_LATEST_VAL_COVER["limit"] = 1

MODE_CLOSEST_STOP_VALIDITY = {
    "command": "T_CLOSEST(stop_datetime, (Ta-dTa+Tb+dTb)/2)",
    "sort": SORT_START,
}
MODE_CLOSEST_START_VALIDITY = {
    "command": "T_CLOSEST(start_datetime, (Ta-dTa+Tb+dTb)/2)",
    "sort": SORT_START,
}

MODE_LATEST_VALIDITY_CLOSEST = {
    "command": "T_CLOSEST(start_datetime, (Ta-dTa+Tb+dTb)/2)",
    "sort": SORT_START,
    "limit": 1,
}

MODE_LATEST_START_VALIDITY = {"sort": SORT_START, "limit": 1}
MODE_LATEST_STOP_VALIDITY = {"sort": SORT_STOP, "limit": 1}

MODE_BEST_CENTERED_COVER = {
    "command": "T_BEST_CENTERED_COVERED(INTERVAL(start_datetime,  stop_datetime), (Ta-dTa+Tb+dTb)/2)",
    "sort": SORT_START,
}

MODE_LARGEST_OVERLAP = {
    "command": "T_INTERSECTS(INTERVAL(start_datetime, end_datetime), INTERVAL(Ta-dTa, Tb+dTb))",
    "sort": SORT_OVERLAP,
}

MODE_LARGEST_OVERLAP85 = {
    "command": "T_OVERLAP_85(INTERVAL(start_datetime, end_datetime), INTERVAL(Ta-dTa, Tb+dTb))",
    "sort": SORT_OVERLAP,
}

MODE_LATEST_VALIDITY = {
    "sort": SORT_START,
    "limit": 1,
}


map_retrieval = {
    "ValIntersect": MODE_VAL_INTERSECT,
    "LatestValIntersect": MODE_LATEST_VAL_INTERSECT,
    "ValCover": MODE_VAL_COVER,
    "LatestValCover": MODE_LATEST_VAL_COVER,
    "ClosestStopValidity": MODE_CLOSEST_STOP_VALIDITY,
    "ClosestStartValidity": MODE_CLOSEST_START_VALIDITY,
    "ValIntersectWithoutDuplicates": MODE_VAL_INTERSECT,
    "LatestValidityClosest": MODE_LATEST_VALIDITY_CLOSEST,
    "LatestStartValidity": MODE_LATEST_START_VALIDITY,
    "LatestStopValidity": MODE_LATEST_STOP_VALIDITY,
    "BestCenteredCover": MODE_BEST_CENTERED_COVER,
    "LatestValCoverClosest": MODE_LATEST_VAL_COVER,  # TODO: confirm this one
    "LargestOverlap": MODE_LARGEST_OVERLAP,
    "LargestOverlap85": MODE_LARGEST_OVERLAP85,
    "LatestValidity": MODE_LATEST_VALIDITY,
}


def convert_alternative(element, **kwargs) -> tuple[dict[str, Any], str | None]:
    json = {
        "order": None,
        "stac_query": {"filter-lang": "cql2-json"},
        "local_variables": {},
        "validation_rules": {"minimum_products": 1, "duplication": False},
    }
    mode = None
    dpr_type = None
    for attr in element:
        tag = attr.tag
        if tag == "File_Type":
            dpr_type = to_dpr_type(attr.text)
            if isinstance(dpr_type, list):
                dpr_type = "TODO_" + "_".join(dpr_type)
            elif dpr_type is None:
                dpr_type = "TODO_" + attr.text
            json["local_variables"]["product_type"] = dpr_type
        elif tag == "Order":
            json["order"] = attr.text
        elif tag == "T0":
            json["local_variables"]["dTa"] = attr.text
        elif tag == "T1":
            json["local_variables"]["dTb"] = attr.text
        elif tag == "Retrieval_Mode":
            mode = attr.text.strip()

    filter_data = {}
    sort_data = None
    limit_data = None

    if mode in map_retrieval:
        mode_data = map_retrieval[mode]
        sort_data = mode_data.get("sort")
        limit_data = mode_data.get("limit")
        command = mode_data.get("command")

        if command:
            filter_data = {
                "op": "and",
                "args": [
                    build_property("product_type", property_dict=kwargs.get("property_dict", {})),
                    cql_txt_to_json(command, **kwargs),
                ],
            }
    else:
        print(f"mode {mode!r} is not supported")

    for k, v in {"filter": filter_data, "sort_by": sort_data, "limit": limit_data}.items():
        if v:
            json["stac_query"][k] = v
    return json, dpr_type


def convert_tasktable_to_json(xml, **kwargs):
    if isinstance(xml, ET.ElementTree):
        root = xml.getroot()
    elif isinstance(xml, ET.Element):
        root = xml
    elif isinstance(xml, str):
        if xml.lstrip().startswith("<?xml"):
            root = ET.fromstring(xml)
        else:
            upath = get_universal_path(xml, **kwargs)
            with upath.open() as fp:
                root = ET.fromstring(fp.read())

    property_dict = {}
    property_dict.update(copy.copy(DEFAULT_CQL2_PROPERTIES))
    user_property_dict = kwargs.get("property_dict")
    if isinstance(user_property_dict, dict):
        property_dict.update(user_property_dict)
    kwargs["property_dict"] = property_dict

    new_tt = {}
    new_tt["version"] = kwargs.get("version", "TODO_version")
    new_tt["baseline_collection"] = kwargs.get("baseline_collection", "TODO_baseline_collection")
    # Global parameters
    for child in root:
        tag = child.tag.lower()
        if tag in global_param:
            new_tt[child.tag.lower()] = child.text

    adf_input_list = []
    product_input_list = []
    product_output_list = []

    for t in root.find("List_of_Pools/Pool/List_of_Tasks/Task"):
        if t.tag == "List_of_Inputs":
            for xml_input in t.findall("Input"):
                alternatives = []
                adf_or_product = None
                input_json = {"name": "TODO"}

                for child in xml_input:
                    if child.tag == "List_of_Alternatives":
                        for xml_product_or_adf in child.findall("Alternative"):
                            json_data, product_type = convert_alternative(xml_product_or_adf, **kwargs)
                            adf_or_product = DATAFILE_METADATA.get_metadata(product_type, "adf_or_product")
                            alternatives.append(json_data)
                    elif child.tag == "Mode":
                        input_json["mode"] = child.text.strip().lower()
                    elif child.tag == "Mandatory":
                        mandatory = child.text.strip().lower()
                        if mandatory in ("y", "yes", "true"):
                            input_json["mandatory"] = True
                        else:
                            input_json["mandatory"] = False
                input_json["alternatives"] = alternatives
                if adf_or_product == "product":
                    product_input_list.append(input_json)
                elif adf_or_product == "ADF":
                    adf_input_list.append(input_json)
            new_tt["input_products"] = product_input_list
            new_tt["input_adfs"] = adf_input_list
        elif t.tag == "List_of_Outputs":
            for xml_output in t.findall("Output"):
                safe_type = xml_output.find("Type")
                if safe_type is not None:
                    dpr_type = to_dpr_type(safe_type.text)
                    if dpr_type is None:
                        dpr_type = safe_type.text
                        print(
                            f"Warning : the old product_type {dpr_type} is used, "
                            f"Please updated it to the correct DPR Product Type",
                        )
                    product_output_list.append(
                        {
                            "name": dpr_type[3:].lower(),
                            "product_type": dpr_type,
                        },
                    )
            new_tt["output_products"] = product_output_list

    return new_tt


def convert_tt(tasktable: str, version: str = "", baseline_collection: str = "") -> str:
    # namespaces = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    tree = ET.parse(tasktable)
    new_tt = convert_tasktable_to_json(tree.getroot(), version, baseline_collection)

    json_str = json.dumps(new_tt, indent=4)

    return json_str


def generate_sentinel3_tasktables(tt_table_path="/opt/DATA/Tasktables"):
    tt_conf = Path(tt_table_path)

    ipfs = {
        # "OL1": ("06.17", "OL__L1_.003.03.01"),
        # "OL1_RAC": ("06.15", "OL__L1_.003.03.01"),
        # "OL1_SPC": ("06.12", "OL__L1_.003.03.01"),
        # "OL2_FR": ("06.18", "OL__L2L.002.11.02"),
        # "SL1": ("06.21", "SL__L1_.004.06.00"),
        # "SL2": ("06.22", "SL__LST.004.07.02"),
        # "SL2_FRP": ("01.09", "FRP_NTC.004.08.02"),
        # "SY2": ("06.26", "SYN_L2_.002.18.01"),
        # "SY2_AOD": ("01.09", "AOD_NTC.002.08.01"),
        # "SY2_VGS": ("06.13", "SYN_L2V.002.09.01"),
        "L0_DO_DOP": ("06.15", ""),
        "L0_DO_NAV": ("06.15", ""),
        "L0_GN_GNS": ("06.15", ""),
        "L0_MW_MWR": ("06.15", ""),
        "L0_OL_CR_": ("06.15", ""),
        "L0_OL_EFR": ("06.15", ""),
        "L0_SL_SLT": ("06.15", ""),
        "L0_SR_CAL": ("06.15", ""),
        "L0_SR_SRA": ("06.15", ""),
        "L0_TM_HKM": ("06.15", ""),
        "L0_TM_HKM2": ("06.15", ""),
        "L0_TM_NAT": ("06.15", ""),
    }
    for ipf, version in ipfs.items():
        print(f"* Convert {ipf} TaskTable")
        json_str = convert_tt(
            str(tt_conf / "xml" / f"TaskTable_S3A_{ipf}.xml"),
            version=version[0],
            baseline_collection=version[1],
        )
        new_tt_file = tt_conf / "json" / f"TaskTable_{ipf}.json"
        with open(str(new_tt_file), mode="w") as f:
            f.write(json_str)


if __name__ == "__main__":
    pass
    # generate_sentinel3_tasktables()
