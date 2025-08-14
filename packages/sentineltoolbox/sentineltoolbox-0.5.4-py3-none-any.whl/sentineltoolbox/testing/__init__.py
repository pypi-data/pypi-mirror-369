from pathlib import Path

from sentineltoolbox.configuration import Configuration

UT_DATA = Path("tests/ut/data/")
UT_DATA_BUCKET = "s3://buc-acaw-dpr/testdata/sentineltoolbox/tests/ut/data/"
IT_DATA = Path("tests/it/data/")
IT_DATA_BUCKET = "s3://buc-acaw-dpr/testdata/sentineltoolbox/tests/it/data/"
SAFE_DATA = IT_DATA / "SAFE"
SAFE_DATA_BUCKET = IT_DATA_BUCKET + "SAFE/"


PROD_S3_SAFE = (
    SAFE_DATA
    / "S3/Prod/S3A_SY_2_AOD____20191227T124211_20191227T124311_20230616T170045_0060_053_109______PS1_D_NR_002.SEN3"
)
ADF_SAFE_ZARR = (
    SAFE_DATA
    / "S3/ADF/S3A_OL_1_CLUTAX_20160425T095210_20991231T235959_20160525T120000___________________MPC_O_AL_003.SEN3"
)  # -> S03A_ADF_OLLUT_20160425T095210_20991231T235959_20241009T172430.zarr

ADF_SAFE_JSON = (
    SAFE_DATA
    / "S3/ADF/S3A_OL_1_EO__AX_20160425T103700_20991231T235959_20230613T120000___________________MPC_O_AL_015.SEN3"
)  # -> S03A_ADF_OLEOP_20160425T103700_20991231T235959_20241009T172430.json
# NO LOCAL S2 FOR THE MOMENT BECAUSE SIZE IS TOO IMPORTANT


PROD_S3_SAFE_BUCKET = (
    SAFE_DATA_BUCKET
    + "S3/Prod/S3A_SY_2_AOD____20191227T124211_20191227T124311_20230616T170045_0060_053_109______PS1_D_NR_002.SEN3"
)
PROD_S2L1A_SAFE_BUCKET = SAFE_DATA_BUCKET + "S2/Prod/S2A_MSIL1A_20000101T000000_N0001_R001_T00XXX_20000101T000000.SAFE"
PROD_S2L1C_SAFE_BUCKET = (
    "s3://s2-input/Validation/Dataset/36TUL/S2MSI1C/S2A_MSIL1C_20180820T083601_N0500_R064_T36TUL_20230629T063559.SAFE"
)
ADF_SAFE_ZARR_BUCKET = (
    SAFE_DATA_BUCKET
    + "S3/ADF/S3A_OL_1_CLUTAX_20160425T095210_20991231T235959_20160525T120000___________________MPC_O_AL_003.SEN3"
)  # -> S03A_ADF_OLLUT_20160425T095210_20991231T235959_20241009T172430.zarr

ADF_SAFE_JSON_BUCKET = (
    SAFE_DATA_BUCKET
    + "S3/ADF/S3A_OL_1_EO__AX_20160425T103700_20991231T235959_20230613T120000___________________MPC_O_AL_015.SEN3"
)  # -> S03A_ADF_OLEOP_20160425T103700_20991231T235959_20241009T172430.json


def home_path_empty() -> Path:
    """
    mocked return function to replace Path.home
    always return valid but empty directory
    """
    return Path("tests/ut/data/empty")


def home_path_sample() -> Path:
    """
    mocked return function to replace Path.home
    always return valid but empty directory
    """
    return Path("tests/ut/data/home")


def configuration_sample() -> Configuration:
    conf = Configuration(path=home_path_sample() / ".eopf/sentineltoolbox.toml")
    conf.data["resources"]["sentineltoolbox.resources"] = [home_path_sample() / "resources"]
    return conf
