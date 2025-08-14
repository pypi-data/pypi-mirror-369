from dataclasses import dataclass

PRODUCT_URI_PARTS_LEN = 7
MISSION_ID_LEN = len("MMM")
PRODUCT_LEVEL_LEN = len("MSIXXX")
DATATAKE_SENSING_START_TIME_STR_LEN = len("YYYYMMDDTHHMMSS")
PROCESSING_BASELINE_NUMBER_LEN = len("Nxxyy")
RELATIVE_ORBIT_NUMBER_LEN = len("ROOO")
TILE_ID_LEN = len("Txxxxx")
PRODUCT_DISCRIMINATOR_TIME_STR_LEN = DATATAKE_SENSING_START_TIME_STR_LEN


@dataclass(frozen=True, kw_only=True)
class S2MSIL1CProductURI:
    """
    Parsed Product URI (Compact Naming Convention)

    The original string is contained in the ``original`` attribute.


    See `Compact Naming Convention
    <https://sentiwiki.copernicus.eu/web/s2-products#S2Products-NamingConventionS2-Products-Naming-Conventiontrue>`_

    Example
    -------
    ..  code-block::

        S2A_MSIL1C_20230422T085551_N0509_R007_T34QFL_20230422T110127.SAFE
        [ ] [    ] [             ] [   ] [  ] [    ] [             ]
        ^   ^      ^               ^     ^    ^      ^
        |   |      |               |     |    |      |
        |   |      |               |     |    |       product_discriminator_time_str
        |   |      |               |     |     tile_id
        |   |      |               |      relative_orbit_number
        |   |      |                processing_baseline_number
        |   |       datatake_sensing_start_time_str
        |    product_level
         mission_id
    """

    original: str
    mission_id: str
    product_level: str
    datatake_sensing_start_time_str: str
    processing_baseline_number: str  # eg N0204
    relative_orbit_number: str  # (R001 - R143)
    tile_id: str
    product_discriminator_time_str: str
    extension: str = "SAFE"

    def __str__(self) -> str:
        return (
            "_".join(
                (
                    self.mission_id,
                    self.product_level,
                    self.datatake_sensing_start_time_str,
                    self.processing_baseline_number,
                    self.relative_orbit_number,
                    self.tile_id,
                    self.product_discriminator_time_str,
                ),
            )
            + "."
            + self.extension
        )

    @classmethod
    def from_string(cls, product_uri_string: str) -> "S2MSIL1CProductURI":
        splitted = product_uri_string.split(".")[0].split("_")
        if len(splitted) != PRODUCT_URI_PARTS_LEN:
            raise ValueError(
                f"Given Product URI {product_uri_string!r} is incomplete. Expected 7 parts, but only"
                f" {len(splitted)} are present.",
            )

        mission_id = splitted[0]

        product_uri = cls(
            original=product_uri_string,
            mission_id=mission_id,
            product_level=splitted[1],
            datatake_sensing_start_time_str=splitted[2],
            processing_baseline_number=splitted[3],
            relative_orbit_number=splitted[4],
            tile_id=splitted[5],
            product_discriminator_time_str=splitted[6],
        )

        return product_uri
