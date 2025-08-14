from sentineltoolbox.models.eopf_payload import convert_payload_dict_to_dataclass

SAMPLE_JSON_PAYLOAD = {
    "I/O": {
        "adfs": [
            {
                "id": "L2ASC",
                "path": "./resources/examples/adf/ADF_L2ASC.json",
                "store_params": {},
            },
            {
                "id": "L2AGS",
                "path": "./resources/examples/adf/GlobalSnowMap.zarr.tar.xz",
                "store_params": {},
            },
        ],
        "input_products": [
            {
                "id": "l1c_input",
                "path": ".../S2A_MSIL1C_20231215T103431_N0510_R108_T32TLQ_20231215T124106.zarr",
                "store_params": {"mode": "r"},
                "store_type": "zarr",
            },
        ],
        "output_products": [
            {
                "id": "l2a_output",
                "path": "outputs_main.zarr",
                "store_params": {"mode": "w"},
                "store_type": "zarr",
                "type": "filename",
            },
        ],
    },
    "breakpoints": None,
    "config": None,
    "dask_context": {
        "client_config": {"timeout": "320s"},
        "cluster_config": {
            "memory_limit": "4GiB",
            "n_workers": 4,
            "threads_per_worker": 4,
        },
        "cluster_type": "local",
        "performance_report_file": "performance_report_file.html",
    },
    "general_configuration": None,
    "logging": ["logging_config.json"],
    "workflow": [
        {
            "active": True,
            "adfs": {},
            "inputs": {"in": "l1c_input"},
            "module": "s2msi.l2a_prototype.computing.scene_classification.l2a_sc_0b_resampling",
            "name": "ResamplingSCProcessingUnit_instance",
            "outputs": {},
            "parameters": {
                "impl_params": {
                    "band_names": [
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
                    ],
                    "feature_flags": {},
                    "level_of_detail": "dependency",
                    "target_resolution_in_m": 60,
                },
            },
            "processing_unit": "ResamplingSCProcessingUnit",
            "step": None,
        },
        {
            "active": True,
            "adfs": {"adf_l2asc": "L2ASC"},
            "inputs": {"in": "ResamplingSCProcessingUnit_instance.out"},
            "module": "s2msi.l2a_prototype.computing.scene_classification.l2a_sc_0a_exclude_pixels",
            "name": "ExcludePixelsProcessingUnit_instance",
            "outputs": {},
            "parameters": {
                "impl_params": {
                    "feature_flags": {},
                    "level_of_detail": "dependency",
                    "target_resolution_in_m": 60,
                },
            },
            "processing_unit": "ExcludePixelsProcessingUnit",
            "step": None,
        },
        {
            "active": True,
            "adfs": {"adf_l2asc": "L2ASC"},
            "inputs": {"in": "ExcludePixelsProcessingUnit_instance.out"},
            "module": "s2msi.l2a_prototype.computing.scene_classification.l2a_sc_01_cloud_snow_detection",
            "name": "CloudSnowDetectionProcessingUnit_instance",
            "outputs": {},
            "parameters": {
                "impl_params": {
                    "feature_flags": {
                        "with_spatial_filtering": False,
                        "with_step_b02_b11": False,
                        "with_step_b04": True,
                        "with_step_b08_b03": False,
                        "with_step_b08_b11": False,
                        "with_step_ndsi": True,
                        "with_step_ndvi": False,
                    },
                    "level_of_detail": "dependency",
                    "target_resolution_in_m": 60,
                },
            },
            "processing_unit": "CloudSnowDetectionProcessingUnit",
            "step": None,
        },
        {
            "active": True,
            "adfs": {"adf_l2ags": "L2AGS", "adf_l2asc": "L2ASC"},
            "inputs": {"in": "CloudSnowDetectionProcessingUnit_instance.out"},
            "module": "s2msi.l2a_prototype.computing.scene_classification.l2a_sc_01_snow_detection_loop",
            "name": "SnowDetectionLoopProcessingUnit_instance",
            "outputs": {"out": "l2a_output"},
            "parameters": {
                "impl_params": {
                    "default_enter_the_snow_loop": True,
                    "feature_flags": {
                        "snow_filter_1b_ratio_b05_on_b8a_enabled": True,
                        "usage_of_esa_cci_maps_enabled": False,
                        "usage_of_global_snow_map_enabled": True,
                    },
                    "level_of_detail": "dependency",
                    "target_resolution_in_m": 60,
                },
            },
            "processing_unit": "SnowDetectionLoopProcessingUnit",
            "step": None,
        },
    ],
}

SAMPLE_PAYLOAD = convert_payload_dict_to_dataclass(SAMPLE_JSON_PAYLOAD)
