from sentineltoolbox.converters import convert_to_datatree

SAMPLE_JSON_ADF = {
    "param_root": {
        "long_name": "Root Parameter (int)",
        "value": 0,
        "type": "uint16",
        "valid_min": "0",
        "valid_max": "9",
    },
    "group": {
        "param_group": {
            "long_name": "Group Parameter (array)",
            "value": [0, 1, 2],
            "type": "array[uint16]",
            "valid_min": "0",
            "valid_max": "9",
        },
        "subgroup": {
            "param_subgroup": {
                "long_name": "Sub-Group Parameter",
                "value": "str value",
                "type": "str",
            },
        },
    },
    "title": "Sample Group",
    "baseline collection": "001",
    "metainformation": {"some_meta": "sample metadata"},
    "eopf:type": "SAMPLE_JSON",
}

SAMPLE_ADF = convert_to_datatree(SAMPLE_JSON_ADF)
