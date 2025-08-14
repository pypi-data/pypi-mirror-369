"""
3. EOPF product types and file naming rules

This section defines EOPF product types and the EOPF file name convention.

Product types distinguish between data product items of different structure in the sense of having different variables.
Example: There are variables for radiances of 21 bands in a Sentinel-3 OLCI Level-1 product, while there are variables
for 13 reflectance bands of different resolutions in a Sentinel-2 MSI Level-1 product. These are two different types.
Within a product type, the product items of the type share having the same variables and the same attributes.
The definition of their structures is the subject of sections 5 and 7. The product items of a type usually have
different measurement data values and attribute values but represented in the same structure.
Sentinel product types are defined in subsection 3.1.

Product (file) names of EOPF products are formatted as a logical identifier made up of different fields.
The identifier shall be unique in the sense that two different product items shall have different names.
Most of the fields are common for different product types to harmonise Sentinel file names and make them
easy to recognise. The logical identifier helps to find out which product is identified, but it is not intended to
replace the function of a catalogue to find products with certain features. Discovery metadata, useful for catalogues,
are defined in section 7. Sentinel product names are defined in subsection 3.2.

The paragraph above as well as later docstrings are taken from: (2024-07-04)
https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/PSFD/3-product-types-naming-rules.html
"""

from dataclasses import dataclass
from typing import Self


@dataclass(kw_only=True, frozen=True)
class SentinelProductTypeDefinition:
    """
    3.1 EOPF Sentinel Product Type Definition

    Sentinel product type identifiers are build using a schema

    MMMSSSCCC  (mission, sensor, code)

    with

    Attributes
    ----------

    mission
        MMM two characters for the mission, S01, S02, S03, etc

    sensor
        SSS three characters for sensor and - where necessary - sensor mode

    code
        CCC three characters for a processing code

    Notes
    -----
    Example:

    S01SEWSLC

    with

    S01 mission Sentinel-1

    SEW sensor S(AR), mode EW

    SLC processing code

    Legacy Sentinel product type names had a different length and had been padded by underscores.
    For the new names, this has been changed in favour of shorter type names because in most cases
    a small part of the legacy name is sufficient to identify the type. A shorter name, e.g. SLC,
    has been used when talking about a type anyway. This is now reflected in the shorter type names,
    with the decision to start with an S to distinguish Sentinel products from products of other missions,
    to include the mode where helpful, and to use a common length for harmonisation.

    This common length has consequences for a very few types that get abbreviated (GRM for GRD M) to fit
    into the three characters, in particular for GRD and SRAL products. The platform (A, B, …) is not
    considered part of the type as the data structure of different platforms is identical.

    Platform is part of the file name defined in subsection 3.2, though.
    """

    mission: str
    sensor: str
    code: str

    @classmethod
    def from_string(cls, string: str) -> Self:
        return cls(
            mission=string[0:3],
            sensor=string[3:6],
            code=string[6:9],
        )

    def __str__(self) -> str:
        return f"{self.mission}{self.sensor}{self.code}"


@dataclass(kw_only=True, frozen=True)
class SentinelProductNameDefinition:
    """
    3.2 EOPF Sentinel Product Name Definition

    Sentinel product (file) names are build using a schema:

    MMMSSSCCC_YYYYMMDDTHHMMSS_UUUU_PRRR_XVVV[_Z*]

    (type, time, duration, platform and relorbit, aux level and quasi-unique identification, type-specific part)

    with

    Attributes
    ----------
    product_type
        MMMSSSCCC 9 characters product type

    acquisition_start_time
        YYYYMMDDTHHMMSS acquisition start time (time of first instrumental measurement without milli and microseconds)
        in ISO 8601 format

    acquisition_duration
        UUUU acquisition duration in seconds, 0000..9999

    platform
        P platform, A, B, …

    relative_orbit_number
        RRR relative orbit number or pass/track number for MWR&SRAL, 000..999

    auxiliary_data_consolidation_level
        X auxiliary data consolidation level, T (forecasT) or S (analysiS),
        (S and T are used instead of A and F to distinguish them from the hexadecimal number
        and from the platform identifier); note that this field is based on the product:timeline metadata.

            - product:timeline = NRT <==> X = T
            - product:timeline = STC <==> X = _
            - product:timeline = NTC <==> X = S

        For product types where the auxiliary data quality level is not applicable, X is '_'.

    quasi_unique_hexadecimal_number
        VVV quasi-unique hexadecimal number (0..9,A..F), like a CRC checksum
        (to avoid overwriting files in case of reprocessing action)

    type_specific_name_extension
        Z* type-specific name extension, e.g. :

            - 5 characters ZZZZZ data take hexadecimal identifier for Sentinel-1
            - 2 characters ZZ polarisation for Sentinel-1, DV (dual polarisation VV-VH), DH (dual polarisation HH-HV),
            SH (single polarisation HH), SV (single polarisation VV), HH (if HH component is extracted),
            VV (if VV component is extracted), separated by _ from datatake ID
            - 5 characters ZZZZZ MGRS granule identifier or 3 characters ZZZ UTM zone identifier for Sentinel-2
            - 3 digits ZZZ processing baseline for SRAL and MSI products

    Notes
    -----
    These extensions are rather free and are not yet defined for the nomminal production.

    Example:

    S01SEWOCN_20210926T090903_0064_B175_S28C_5464A_SV

    with

    S01SEWOCN type name

    20210926T090903 acquisition start time in UTC

    0064 duration of 64 seconds

    B platform Sentinel-1 B, 175 relative orbit 175

    S analysis level of consolidated auxiliary data, 28C quasi-unique number

    5464A datatake identifier (possible extension field for Sentinel-1)

    SV polarisation (possible extension field for Sentinel-1)

    Legacy file names had more fields. Start and stop times have been replaced by the shorter start and duration.
    Processing time has been dropped in favour of a shorter quasi-unique number.
    Cycle and frame (where applicable) has been dropped. Product generation centre has been dropped.
    A catalogue and STAC metadata inspection can be used to find this information.

    File names are build from the product name by adding an extension:

            <product_name>.zarr : a directory in zarr format

            <product_name>.nc : a single-file NetCDF

            <product_name>.cog : a directory with COG TIFF files

            <product_name>.safe : a directory in SAFE format

            <product_name>.zarr.zip : a ZIP file containing a zarr directory

            <product_name>.cog.zip : a ZIP file containing a COG directory

    Details of these formats are defined in section 4.

    Examples of product names:

            S01SEWOCN_20210926T090903_0064_B175_S28C_5464A_SV

            S01SEWGRM_20210926T090903_0064_B175_S4A9_5464B_DH

            S02MSIL1C_20190313T123122_0028_A015_T7F0_35VPH

            S03AHRL1A_20230121T070448_3029_B075_T1EC_004

            S03OLCEFR_20220119T092920_0180_B061_S34C

            S03SLSRBT_20220512T023357_0180_A085_S852

    Examples of EOPF products are available on https://eopf-public.s3.sbg.perf.cloud.ovh.net/index.html
    """

    product_type: SentinelProductTypeDefinition
    acquisition_start_time: str
    acquisition_duration: str
    platform: str
    relative_orbit_number: str
    auxiliary_data_consolidation_level: str
    quasi_unique_hexadecimal_number: str
    type_specific_name_extension: str | None

    @classmethod
    def from_string(cls, string: str) -> Self:
        return cls(
            product_type=SentinelProductTypeDefinition.from_string(string[0:9]),
            acquisition_start_time=string[10:25],
            acquisition_duration=string[26:30],
            platform=string[31:32],
            relative_orbit_number=string[32:35],
            auxiliary_data_consolidation_level=string[36:37],
            quasi_unique_hexadecimal_number=string[37:40],
            type_specific_name_extension=string[41:] if len(string) > 41 else None,
        )

    def __str__(self) -> str:
        prefix = (
            f"{self.product_type}"
            "_"
            f"{self.acquisition_start_time}"
            "_"
            f"{self.acquisition_duration}"
            "_"
            f"{self.platform}"
            f"{self.relative_orbit_number}"
            "_"
            f"{self.auxiliary_data_consolidation_level}"
            f"{self.quasi_unique_hexadecimal_number}"
        )
        if self.type_specific_name_extension is None:
            return prefix
        return prefix + f"_{self.type_specific_name_extension}"
