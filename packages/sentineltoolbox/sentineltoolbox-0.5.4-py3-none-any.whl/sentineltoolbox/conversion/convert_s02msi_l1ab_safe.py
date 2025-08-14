import json
import logging
import re
import warnings
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any, Literal, Mapping, Optional, Self, Type, TypeVar
from xml.etree import ElementTree as ET

import dask.array as da
import geopandas as gpd
import numpy as np
import numpy.typing as npt
import rasterio
import rioxarray as rxr
import xarray as xr
from dacite import Config, from_dict
from shapely.geometry import LineString, Polygon
from xarray import DataTree

from sentineltoolbox.attributes import AttributeHandler
from sentineltoolbox.conversion.s2msi_l1ab_typedefs import (
    ACT_DIMENSIONS_L1A,
    ACT_DIMENSIONS_L1B,
    ALT_CHUNK_SIZES,
    BAND_NAMES,
    DETECTOR_IDS,
    ALTChunkSizeType,
    BandNameType,
    DetectorIdType,
    SensorGeometryVariableNameType,
)

DEFAULT_CHUNKS = {}
T = TypeVar("T")


def get_logger_name(suffix: str | None = None) -> str:
    return __name__ if suffix is None else f"{__name__}#{suffix}"


def instanciate_dataclass_from_dict(data_class: Type[T], data: Mapping[str, Any]) -> T:
    """
    Instanciate a dataclass from a mapping, potentially nested.

    The return type is parameterized from the dataclass' class.

    Parameters
    ----------
    data_class
        Dataclass' class to convert the data to
    data
        Data to inject into the dataclass instance.

    Returns
    -------
        The dataclass instance.
    """
    # Note: Paths are automatically instanciated from their string representation
    instance = from_dict(
        data_class=data_class,
        data=data,
        config=Config(cast=[Path, PurePosixPath]),
    )
    return instance


TIME_FORMAT = "S%Y%m%dT%H%M%S"

ProductLevelType = Literal["L1A", "L1B"]
ProductTypeType = Literal["EOProduct", "DataTree"]
OrbitDirectionType = Literal["descending", "ascending"]


@dataclass(kw_only=True, frozen=True)
class S02MSIL1ABProductConversionParameters:
    """
    The S02MSI L1AB Product Conversion Parameters

    Attributes
    ----------
    detector_ids
        Detector IDs to process
    band_names
        Band Names to process
    """

    detector_ids: tuple[DetectorIdType, ...] = DETECTOR_IDS
    band_names: tuple[BandNameType, ...] = BAND_NAMES

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """
        Class factory method to instanciate from any dict.

        Parameters
        ----------
        data
            Input Data

        Returns
        -------
            The dataclass
        """
        result = instanciate_dataclass_from_dict(cls, data)
        return result


@dataclass(frozen=False, kw_only=True)
class S02MSIL1ABProductConversion:
    """
    S02 MSI L1AB safe product convertor

    Attributes
    ------
    safe_product_path
        The path of the SAFE product.
    product_level
        The level of the SAFE product.
    output_product_type
        The type of the output product (EOProduct | DataTree)
    orbit_direction
        The orbit direction
    """

    safe_product_path: Path
    product_level: ProductLevelType
    output_product_type: ProductTypeType = "DataTree"
    orbit_direction: OrbitDirectionType = "descending"

    def initialize_logger(self, class_name: str) -> None:
        """Initialize the Logger of the Processing Unit.

        Parameters
        ----------
        class_name
            Class name to identify the logger.
            The intended value to pass from the implementing class is ``self.__class__.__name__``.
        """

        logger = logging.getLogger("sentineltoolbox")
        logger.info(f"Starting of the {class_name}")
        self.logger = logger

    def initialize_params(self, kwargs: dict[str, Any]) -> None:
        """
        Initialize the Class's parameters.

        Parameters
        ----------
        kwargs
            Kwargs passed down to the ``convert_s2msi_l1_safe_product`` method of the Class
        """

        params = S02MSIL1ABProductConversionParameters.from_dict(kwargs)
        self.logger.info(f"{params=}")
        self.params = params

    def create_empty_product(
        self,
    ) -> DataTree:
        """
        Initiate an empty EOProduct or xarray DataTree.

        Returns
        -------
        new_product
            An empty EOProduct or DataTree.
        """
        # initiate the output xarray DataTree
        return DataTree()

    def convert_s2msi_l1_safe_product(self, **kwargs: Any) -> DataTree:
        """
        This function is responsible for orchestrating the conversion of an S2MSI L1 SAFE product to Zarr.

        Returns
        -------
        output_product
            The converted-to-Zarr S2MSI L1 SAFE product.
        """
        if "detector_ids" not in kwargs:
            kwargs["detector_ids"] = (
                "d01",
                "d02",
                "d03",
                "d04",
                "d05",
                "d06",
                "d07",
                "d08",
                "d09",
                "d10",
                "d11",
                "d12",
            )
        if "band_names" not in kwargs:
            kwargs["band_names"] = (
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
            )

        # Initialize the EOPF logger
        self.initialize_logger(self.__class__.__name__)

        # Initialize the class parameters access
        self.initialize_params(kwargs)

        # Create an empty product to host the safe data
        output_product = self.create_empty_product()

        self.logger.info("Output Zarr Product initiated.")
        self.logger.info(f"Starting the conversion of the input {self.product_level} SAFE product to Zarr.")

        # dictionary of Polygon objects for all detectors
        detectors_polygons_dict: dict[DetectorIdType, Polygon] = {}

        # Iterate over detectors
        for detector_id in self.params.detector_ids:

            # Construct the detector swath footprint
            detector_polygon = self.handle_detector_swath_footprint_construction(output_product, detector_id)

            # Append to the polygon to the global dictionary
            detectors_polygons_dict[detector_id] = detector_polygon

            # Iterate over bands
            for band_name in self.params.band_names:
                self.logger.info(f"Converting {detector_id}/{band_name} SAFE data.")

                # Check the level of the product
                if self.product_level == "L1A":
                    # Set the chunk size
                    chunk_size = s2msi_l1a_chunk_size(band_name)

                elif self.product_level == "L1B":
                    # Set the chunk size
                    chunk_size = s2msi_l1b_chunk_size(band_name)

                # Extract the image data paths of the band in question
                img_data_paths = sorted(
                    self.safe_product_path.glob(f"GRANULE/S2*{detector_id.upper()}*/IMG_DATA/*{band_name.upper()}.jp2"),
                )
                # Group the image data of the band in question by scene time
                grouped_img_data_paths_dict = group_img_data_names(img_data_paths, TIME_FORMAT, self.orbit_direction)
                # Identify missing scenes within the image data of the band in question
                grouped_img_data_paths_dict = identify_missing_scenes(grouped_img_data_paths_dict, TIME_FORMAT)
                # Build the full swath image data of the band in question
                full_image_data_arr = concatenate_all_the_imgs_jp2s(
                    grouped_img_data_paths_dict,
                    chunk_size,
                    self.orbit_direction,
                    default_chunks=kwargs.get("default_chunks", DEFAULT_CHUNKS),
                )

                # Extract the quality masks data paths of the band in question
                msk_data_paths = sorted(
                    self.safe_product_path.glob(f"GRANULE/S2*{detector_id.upper()}*/QI_DATA/*{band_name.upper()}*.jp2"),
                )
                # Group the quality masks data of the band in question by scene time
                grouped_msk_data_paths_dict = group_img_data_names(msk_data_paths, TIME_FORMAT, self.orbit_direction)
                # Identify missing scenes within the quality masks data of the band in question
                grouped_msk_data_paths_dict = identify_missing_scenes(grouped_msk_data_paths_dict, TIME_FORMAT)
                # Build the full swath quality masks data of the band in question
                full_qualit_masks_data_arr = concatenate_all_the_qualit_msks_jp2s(
                    grouped_msk_data_paths_dict,
                    chunk_size,
                    self.orbit_direction,
                )

                # Build measurements along satellite track coordinate of the band in question image data
                alt_coords_array = np.arange(0, full_image_data_arr.shape[0], 1)
                # Put the coordinates into an xarray DataArray to have label dimensions that match the data
                band_alt_coordinates: xr.DataArray = xr.DataArray(data=alt_coords_array, dims=("alt",))

                # Build measurements across satellite track coordinate of the band in question image data
                act_coords_array = np.arange(0, full_image_data_arr.shape[1], 1)
                # Put the coordinates into an xarray DataArray to have label dimensions that match the data
                band_act_coordinates: xr.DataArray = xr.DataArray(data=act_coords_array, dims=("act",))

                # Put the concatenated data into DataArrays (needed to build the zarr) and ensure desired chunking
                band_img_data: xr.DataArray = xr.DataArray(
                    full_image_data_arr,
                    dims=("alt", "act"),
                ).chunk(chunk_size)
                band_quality_msk_data: xr.DataArray = xr.DataArray(
                    full_qualit_masks_data_arr,
                    dims=("alt", "act"),
                ).chunk(chunk_size)

                # Populate the output product with the band image and quality mask data
                self.populate_product(
                    output_product,
                    detector_id,
                    band_name,
                    band_img_data,
                    band_quality_msk_data,
                    band_alt_coordinates,
                    band_act_coordinates,
                )

        # Create a GeoDataFrame of the detectors polygons
        detectors_gdf = gpd.GeoDataFrame(geometry=list(detectors_polygons_dict.values()))

        # Clean-up polygons from overlaps or intersections not accounted for by shared borders
        detectors_gdf["geometry"] = detectors_gdf.buffer(
            0,
        )  # This .buffer(0) method is a common trick to clean up slight inaccuracies or topology errors in geometries.

        # Merge polygons into a single footprint of the DS
        DS_footprint = detectors_gdf.unary_union

        # Optionally, create a GeoDataFrame for the merged footprint
        DS_footprint_gdf = gpd.GeoDataFrame(geometry=[DS_footprint], crs="EPSG:4326")  # Assuming WGS84 Lat/Lon
        # tolerance: the parameter that decides the degree of simplification
        # higher values will result in more simplification, but may also distort the shape more
        tolerance = 0.01  # Adjust this value based on your specific needs
        DS_footprint_gdf["geometry"] = DS_footprint_gdf.geometry.simplify(tolerance, preserve_topology=True)
        # Get the need parameters
        product_bbox = list(DS_footprint_gdf.geometry.iloc[0].bounds)
        product_geometry = json.loads(DS_footprint_gdf.to_json(indent=4))["features"][0]["geometry"]
        self.logger.info("The global footprint of the product is generated.")

        stac_attrs = {
            "bbox": product_bbox,
            "geometry": product_geometry,
            "properties": {},
            "stac_extensions": [],
            "stac_version": "1.0.0",
            "type": "Feature",
        }

        # Extract the geometric refinement parameters from the datastrip metadata
        self.logger.info(f"Starting the extraction of the {self.product_level} SAFE product datastrip metadata.")
        datastrip_metadata_xml_file_path = sorted(self.safe_product_path.glob("DATASTRIP/S2*/S2*.xml"))
        product_metadata = build_product_metadata(datastrip_metadata_xml_file_path[0], self.product_level)
        self.logger.info(f"The {self.product_level} SAFE product datastrip metadata extracted.")

        # populate the product attributes
        output_product.attrs["stac_discovery"] = stac_attrs
        self.logger.info("The generated global footprint of the product added to the product attributes' STAC entry.")

        output_product.attrs["other_metadata"] = product_metadata

        attrs = AttributeHandler(output_product)
        attrs.set_attr("product:type", f"S02MSI{self.product_level}")
        attrs.set_attr("processing:level", self.product_level)

        self.logger.info(
            f"The {self.product_level} SAFE product datastrip metadata added to the output zarr product "
            "attributes' other metadata entry.",
        )

        return output_product

    def handle_detector_swath_footprint_construction(
        self,
        new_product: DataTree,
        detector_id: DetectorIdType,
    ) -> Polygon:
        """
        This function is in charge of building the footprint of an S2MSI detector swath, appending the coordinates of
        the swath sides to the S2MSI product whose detector's swath footprint is build, and storing the swath footprint
        into a Shapely's Polygon object to be used in constructing the global footprint of the product.

        Parameters
        ----------
        new_product
            The S2MSI product whose detector's swath footprint to be build.
        detector_id
            The ID of the detector in question.

        Returns
        -------
        detector_swath_footprint_polygon
            A Shapely's Polygon object containing the built detector swath footprint.
        """

        # Extract the image data paths of the band in question
        granule_metadata_paths = sorted(
            self.safe_product_path.glob(f"GRANULE/S2*{detector_id.upper()}*/S2*{detector_id.upper()}*.xml"),
        )
        # Group the image data of the band in question by scene time
        grouped_granule_metadata_paths_dict = group_img_data_names(
            granule_metadata_paths,
            TIME_FORMAT,
            self.orbit_direction,
        )
        # Identify missing scenes within the image data of the band in question
        grouped_granule_metadata_paths_dict = identify_missing_scenes(grouped_granule_metadata_paths_dict, TIME_FORMAT)

        # Set the number of points to be computed within a granule footprint (that of 60m resolution bands is selected)
        npts_alt: int = int(ALT_CHUNK_SIZES["b01"])  # b01: 60m resolution band
        npts_act: int = 2  # two point representing the left and right sides of the granule footprint

        # Build the detector attribute that contains the footprint info
        # detector_group_attrs = build_detector_footprint(grouped_granule_metadata_paths_dict)
        detector_swath_footprint = build_detector_swath_footprint(
            grouped_granule_metadata_paths_dict,
            npts_alt,
            npts_act,
            self.orbit_direction,
            self.product_level,
        )
        self.logger.info(f"The footprint of {detector_id} swath sides is generated.")

        # Store the footprint variables (longitude & latitude) of the current detector in the condition group of
        # the product
        # -------------------------------------------------------------------------------------------------------
        # Get the along satellite track chunk size for a 60m resolution band (to be used as along satellite track
        # chunk size for the footprint variables since their resolution is that of 60m band)
        alt_60m_chunk_size: ALTChunkSizeType = ALT_CHUNK_SIZES["b01"]

        # Build the footprint variables (longitude & latitude) data by combining and chunking the detector swath two
        # sides
        detector_footprint_longitudes = da.from_array(
            detector_swath_footprint["alt_lons"],
            chunks=(alt_60m_chunk_size, 2),
        )
        detector_footprint_latitudes = da.from_array(
            detector_swath_footprint["alt_lats"],
            chunks=(alt_60m_chunk_size, 2),
        )

        # Get the Zarr path of the footprint longitude variable
        vname_detector_footprint_longitudes = render_sensor_geometry_condition_footprint_zarr_path(
            detector_id,
            "lon",
        )
        # Put the built footprint longitude variable into an xarray DataArray to add the labeled dimension and make
        # the variable compatible with the product
        detector_footprint_longitudes_xda = xr.DataArray(data=detector_footprint_longitudes, dims=("alt", "side"))

        # Get the Zarr path of the footprint latitude variable
        vname_detector_footprint_latitudes = render_sensor_geometry_condition_footprint_zarr_path(
            detector_id,
            "lat",
        )
        # Put the built footprint latitude variable into an xarray DataArray to add the labeled dimension and make
        # the variable compatible with the product
        detector_footprint_latitudes_xda = xr.DataArray(data=detector_footprint_latitudes, dims=("alt", "side"))

        # Append the footprint longitude variable to the product
        new_product[vname_detector_footprint_longitudes] = detector_footprint_longitudes_xda  # type: ignore
        new_product[vname_detector_footprint_longitudes].attrs = {  # type: ignore
            "long_name": "The longitudes of the detector swath sides (left, right) footprint",
            "short_name": "lon",
            "dimensions": "alt side",
        }

        # Append the footprint latitude variable to the product
        new_product[vname_detector_footprint_latitudes] = detector_footprint_latitudes_xda  # type: ignore
        new_product[vname_detector_footprint_latitudes].attrs = {  # type: ignore
            "long_name": "The latitudes of the detector swath sides (left, right) footprint",
            "short_name": "lat",
            "dimensions": "alt side",
        }

        self.logger.info(f"The footprint of {detector_id} swath sides added to the output Product.")

        # Needed to build the product footprint
        lat_left = detector_swath_footprint["alt_lats"][:, 0]  # Latitude values for the left side
        lon_left = detector_swath_footprint["alt_lons"][:, 0]  # Longitude values for the left side
        lat_right = detector_swath_footprint["alt_lats"][:, 1]  # Latitude values for the right side
        lon_right = detector_swath_footprint["alt_lons"][:, 1]  # Longitude values for the right side

        # Combine arrays to form the polygon's coordinates
        # Assuming clockwise order: top-left, top-right, bottom-right, bottom-left
        polygon_coords = list(
            zip(
                np.concatenate([lon_left[::-1], lon_right]),
                np.concatenate([lat_left[::-1], lat_right]),
            ),
        )

        # Create a Shapely Polygon
        detector_swath_footprint_polygon = Polygon(polygon_coords)

        return detector_swath_footprint_polygon

    def populate_product(
        self,
        product: DataTree,
        detector_id: DetectorIdType,
        band_name: BandNameType,
        band_img_data: xr.DataArray,
        band_quality_msk_data: xr.DataArray,
        band_alt_coordinates: xr.DataArray,
        band_act_coordinates: xr.DataArray,
    ) -> DataTree:
        """
        This function populates an EOProduct or an xarray DataTree with data (image & quality mask) related to a
        specific S2 MSI detector and band.

        Parameters
        ----------
        product
            An EOProduct or a DataTree to be populated.
        detector_id
            The ID of the detector whose group will host the to-be added data.
        band_name
            The name of the band whose group will host the to-be added data.
        band_img_data
            The band image data.
        band_quality_msk_data
            The band quality mask data.
        band_alt_coordinates
            The index coordinates of the band image and quality mask data along the satellite track.
        band_act_coordinates
            The index coordinates of the band image and quality mask data across the satellite track.

        Returns
        -------
        product
            The EOProduct or DataTree populated with the input detector and band data.
        """
        product = self.populate_datatree(
            product,
            detector_id,
            band_name,
            band_img_data,
            band_quality_msk_data,
            band_alt_coordinates,
            band_act_coordinates,
        )

        return product

    def populate_datatree(
        self,
        datatree: DataTree,
        detector_id: DetectorIdType,
        band_name: BandNameType,
        band_img_data: xr.DataArray,
        band_quality_msk_data: xr.DataArray,
        alt_coordinate: xr.DataArray,
        act_coordinate: xr.DataArray,
    ) -> DataTree:
        """
        This function populates an xarray DataTree with data (image & quality mask) related to a specific S2 MSI
        detector and band.

        Parameters
        ----------
        datatree
            An xarray datatree to be populated.
        detector_id
            The ID of the detector whose group will host the to-be added data.
        band_name
            The name of the band whose group will host the to-be added data.
        band_img_data
            The band image data.
        band_quality_msk_data
            The band quality mask data.
        alt_coordinate
            The index coordinates of the band image and quality mask data along the satellite track.
        act_coordinate
            The index coordinates of the band image and quality mask data across the satellite track.

        Returns
        -------
        datatree
            The xarray datatree populated with the input band data.
        """

        # Populate the measurements group
        datatree = self.populate_datatree_measurements(
            datatree,
            detector_id,
            band_name,
            band_img_data,
            alt_coordinate,
            act_coordinate,
        )

        # Populate the quality group
        datatree = self.populate_datatree_quality(
            datatree,
            detector_id,
            band_name,
            band_quality_msk_data,
            alt_coordinate,
            act_coordinate,
        )

        return datatree

    def populate_datatree_measurements(
        self,
        datatree: DataTree,
        detector_id: DetectorIdType,
        band_name: BandNameType,
        band_img_data: xr.DataArray,
        alt_coordinate: xr.DataArray,
        act_coordinate: xr.DataArray,
    ) -> DataTree:
        """
        This function populates an xarray DataTree with image data related to a specific S2 MSI detector and band.

        Parameters
        ----------
        datatree
            An xarray datatree to be populated.
        detector_id
            The ID of the detector whose group will host the to-be added data.
        band_name
            The name of the band whose group will host the to-be added data.
        band_img_data
            The band image data.
        alt_coordinate
            The index coordinates of the band image and quality mask data along the satellite track.
        act_coordinate
            The index coordinates of the band image and quality mask data across the satellite track.

        Returns
        -------
        datatree
            The xarray datatree populated with the input band data.
        """

        # Define the measurements path where the data of the detector and the band in question will be stored
        vname_rad = render_sensor_geometry_measurement_zarr_path(detector_id, band_name, "img")
        # Append the image data of the detector and the band in question to the DataTree
        datatree[vname_rad] = band_img_data
        datatree[vname_rad].attrs = band_img_data.attrs

        # Define the measurements path where the along satellite track coordinates of the detector and the band in
        # question will be stored
        vname_alt_measurements = render_sensor_geometry_measurement_zarr_path(detector_id, band_name, "alt")
        # Append the the along satellite track coordinates of the detector and the band in question to the DataTree
        datatree[vname_alt_measurements] = alt_coordinate
        datatree[vname_alt_measurements].attrs = {
            "long_name": "Along Satellite Track coordinates",
            "short_name": "alt",
            "dimensions": "alt",
        }

        # Define the measurements path where the across satellite track coordinates of the detector and the band in
        # question will be stored
        vname_act_measurements = render_sensor_geometry_measurement_zarr_path(detector_id, band_name, "act")
        # Append the the across satellite track coordinates of the detector and the band in question to the DataTree
        datatree[vname_act_measurements] = act_coordinate
        datatree[vname_act_measurements].attrs = {
            "long_name": "Across Satellite Track coordinates",
            "short_name": "act",
            "dimensions": "act",
        }

        return datatree

    def populate_datatree_quality(
        self,
        datatree: DataTree,
        detector_id: DetectorIdType,
        band_name: BandNameType,
        band_quality_msk_data: xr.DataArray,
        alt_coordinate: xr.DataArray,
        act_coordinate: xr.DataArray,
    ) -> DataTree:
        """
        This function populates an xarray DataTree with quality mask data related to a specific S2 MSI detector and
        band.

        Parameters
        ----------
        datatree
            An xarray datatree to be populated.
        detector_id
            The ID of the detector whose group will host the to-be added data.
        band_name
            The name of the band whose group will host the to-be added data.
        band_quality_msk_data
            The band quality mask data.
        alt_coordinate
            The index coordinates of the band image and quality mask data along the satellite track.
        act_coordinate
            The index coordinates of the band image and quality mask data across the satellite track.

        Returns
        -------
        datatree
            The xarray datatree populated with the input band data.
        """

        # Define the quality path where the mask of the detector and the band in question will be stored
        vname_msk_quality = render_sensor_geometry_quality_zarr_path(detector_id, band_name, "mask")
        # Append the quality mask of the detector and the band in question to the DataTree
        datatree[vname_msk_quality] = band_quality_msk_data
        datatree[vname_msk_quality].attrs = band_quality_msk_data.attrs

        # Define the quality path where the along satellite track coordinates of the detector and the band in
        # question will be stored
        vname_alt_quality = render_sensor_geometry_quality_zarr_path(detector_id, band_name, "alt")
        # Append the the along satellite track coordinates of the detector and the band in question to the DataTree
        datatree[vname_alt_quality] = alt_coordinate
        datatree[vname_alt_quality].attrs = {
            "long_name": "Along Satellite Track coordinates",
            "short_name": "alt",
            "dimensions": "alt",
        }

        # Define the quality path where the across satellite track coordinates of the detector and the band in
        # question will be stored
        vname_act_quality = render_sensor_geometry_quality_zarr_path(detector_id, band_name, "act")
        # Append the the across satellite track coordinates of the detector and the band in question to the DataTree
        datatree[vname_act_quality] = act_coordinate
        datatree[vname_act_quality].attrs = {
            "long_name": "Across Satellite Track coordinates",
            "short_name": "act",
            "dimensions": "act",
        }

        return datatree


def render_sensor_geometry_eovariable_name(
    detector_id: DetectorIdType,
    band_name: BandNameType,
    variable_name: SensorGeometryVariableNameType,
) -> str:
    """
    Render an EOvariable name for a Sensor Geometry product.

    Parameters
    ----------
    detector_id
        Detector ID.
    band_name
        Band Name.
    variable_name
        Variable Name.

    Returns
    -------
        The zarr name of the given variable.
    """

    return f"{detector_id}-{band_name}-{variable_name}"


def render_sensor_geometry_measurement_zarr_path(
    detector_id: DetectorIdType,
    band_name: BandNameType,
    variable_name: SensorGeometryVariableNameType,
) -> str:
    """
    Render a Zarr measurement path for a Sensor Geometry product.

    Parameters
    ----------
    detector_id
        Detector ID.
    band_name
        Band Name.
    variable_name
        Variable Name.

    Returns
    -------
        The zarr path of the given variable.
    """

    return f"/measurements/{detector_id}/{band_name}/{variable_name}"


def render_sensor_geometry_quality_zarr_path(
    detector_id: DetectorIdType,
    band_name: BandNameType,
    variable_name: SensorGeometryVariableNameType,
) -> str:
    """
    Render a Zarr quality path for a Sensor Geometry product.

    Parameters
    ----------
    detector_id
        Detector ID.
    band_name
        Band Name.
    variable_name
        Variable Name.

    Returns
    -------
        The zarr path of the given variable.
    """

    return f"quality/{detector_id}/{band_name}/{variable_name}"


def render_sensor_geometry_condition_footprint_zarr_path(
    detector_id: DetectorIdType,
    variable_name: SensorGeometryVariableNameType,
) -> str:
    """
    Render a Zarr conditions' footprint path for a Sensor Geometry product.

    Parameters
    ----------
    detector_id
        Detector ID.
    variable_name
        Variable Name.

    Returns
    -------
        The zarr path of the given variable.
    """

    return f"conditions/{detector_id}/footprint/{variable_name}"


def get_sensor_geometry_dimensions() -> tuple[SensorGeometryVariableNameType, SensorGeometryVariableNameType]:
    """
    Render dimensions for a Sensor Geometry product.

    Returns
    -------
        A tuple of the dimensions' names.
    """

    return ("alt", "act")


def s2msi_l1a_chunk_size(band_name: BandNameType) -> tuple[int, int]:
    """
    Return a legacy S2MSI L1A granule (chunk) size for a given band.

    Parameters
    ----------
    band_name
        The name of the band in question.

    Returns
    -------
        A tuple of the legacy S2MSI L1A granule (chunk) size for the given band.
    """

    # Get the along satellite track dimension of the L1A granule (chunk) for the given band
    alt_chunk_size: int = int(ALT_CHUNK_SIZES[band_name])

    # Get the across satellite track dimension of the L1A granule (chunk) for the given band
    act_chunk_size: int = int(ACT_DIMENSIONS_L1A[band_name])

    return (alt_chunk_size, act_chunk_size)


def s2msi_l1b_chunk_size(band_name: BandNameType) -> tuple[int, int]:
    """
    Return a legacy S2MSI L1B granule (chunk) size for a given band.

    Parameters
    ----------
    band_name
        The name of the band in question.

    Returns
    -------
        A tuple of the legacy S2MSI L1B granule (chunk) size for the given band.
    """

    # Get the along satellite track dimension of the L1B granule (chunk) for the given band
    alt_chunk_size: int = int(ALT_CHUNK_SIZES[band_name])

    # Get the across satellite track dimension of the L1B granule (chunk) for the given band
    act_chunk_size: int = int(ACT_DIMENSIONS_L1B[band_name])

    return (alt_chunk_size, act_chunk_size)


# Revised function to extract the correct time info using regular expressions
def extract_time_info_with_regex(img_data_name: str) -> Optional[str]:
    """
    This function extracts the scene time from the name of the image data file.

    Parameters
    ----------
    img_data_name
        The name of the image data file.

    Returns
    -------
    the extracted scene time.
    """

    # Using regular expression to find the pattern '_SyyyymmddThhmmss_'
    match = re.search(r"_S\d{8}T\d{6}_", img_data_name)
    return match.group(0)[1:-1] if match else None


# Function to convert time info to datetime object
def time_info_to_datetime(time_info: str, time_format: str) -> datetime:
    """
    This function converts the extracted scene time for the file name to datetime format.

    Parameters
    ----------
    time_info
        The extracted scene time string.
    time_format
        the format of the scene time present in the path of the image data.

    Returns
    -------
    datetime
        The extracted scene time in datetime format.
    """

    return datetime.strptime(time_info, time_format)


# Function to check if a time is within one second of any group's time
def is_within_one_second(time: datetime, scene_times: list[datetime]) -> bool:
    """
    This function checks if the current scene time is within the offset of the existing (identified already) scene
    times.

    Parameters
    ----------
    time
        The current scene to be checked.
    scene_times
        The list containing existing (identified already) scene times.

    Returns
    -------
    A boolean indicating if the current scene time is within the offset  of the existing (identified already) scene
    times.
    """

    dt = timedelta(seconds=1)
    return any((scene_time - dt <= time <= scene_time + dt) for scene_time in scene_times)


def group_img_data_names(
    img_data_paths: list[Path],
    time_format: str,
    orbit_direction: OrbitDirectionType,
) -> dict[str, list[Path]]:
    """
    This function groups the paths the image data of the band in question by scene time through which
    missing detectors can be identified. It extracts the scene times from the file names and handles the possible
    offset (due to the framing and the rounding) of the scene time in the names.

    Parameters
    ----------
    img_data_paths
        The list containing paths of the image data of the band in question.
    time_format
        the format of the scene time present in the path of the image data.
    orbit_direction:
        The orbit direction.

    Returns
    -------
    grouped_img_data_paths_dict
        The dictionary containing the paths of the image data of the band in question grouped by scene time.
    """

    grouped_img_data_paths_time_range: dict[str, list[Path]] = defaultdict(list)
    scene_times: list[datetime] = []

    # Iterate over the image data paths
    for img_data_path in img_data_paths:
        # Get the scene time from the image data file name
        time_info = extract_time_info_with_regex(img_data_path.name)
        # Grouping img_data_names with +/- one second range
        if not time_info:
            continue

        file_time = time_info_to_datetime(time_info, time_format)
        # Check if this time is within one second of any group's time
        if is_within_one_second(file_time, scene_times):
            # Add to the existing group
            for scene_time in scene_times:
                if is_within_one_second(file_time, [scene_time]):
                    grouped_img_data_paths_time_range[scene_time.strftime(time_format)].append(img_data_path)
                    break
        else:
            # Create a new group
            scene_times.append(file_time)
            grouped_img_data_paths_time_range[time_info].append(img_data_path)

    # Displaying the result with time range grouping
    grouped_img_data_paths_dict = dict(
        grouped_img_data_paths_time_range,
    )  # Converting to regular dict for easier display

    # Check the orbit direction
    if orbit_direction == "descending":
        # Sorting dictionary by keys (scene time increasing)
        grouped_img_data_paths_dict = dict(sorted(grouped_img_data_paths_dict.items(), reverse=False))

    elif orbit_direction == "ascending":
        # Sorting dictionary by keys (scene time decreasing)
        grouped_img_data_paths_dict = dict(sorted(grouped_img_data_paths_dict.items(), reverse=True))

    return grouped_img_data_paths_dict


def identify_missing_scenes(
    grouped_img_data_paths_dict: dict[str, list[Path]],
    time_format: str,
) -> dict[str, list[Path]]:
    """
    This function identifies missing scenes and updates the input dictionary with such scenes if exist.

    Note: updates in-place.

    Parameters
    ----------
    grouped_img_data_paths_dict
        The dictionary containing the paths of the image data of the band in question grouped by scene time.
    time_format
        the format of the scene time present in the path of the image data.

    Returns
    -------
    grouped_img_data_paths_dict
        The updated dictionary containing the paths of the image data of the band in question grouped by scene time.
    """

    scene_times = list(grouped_img_data_paths_dict.keys())
    # Iterate over scene times
    for i in range(len(scene_times) - 1):
        # Convert to datetime
        current_time = time_info_to_datetime(scene_times[i], time_format)
        next_time = time_info_to_datetime(scene_times[i + 1], time_format)
        # Ensure the duration between two consecutive scene is within the expected scene duration
        duration = abs((next_time - current_time).total_seconds())
        # Identify missing scenes
        if duration > 4:
            missing_scene_time = current_time + timedelta(seconds=3)
            grouped_img_data_paths_dict[missing_scene_time.strftime(time_format)] = []

    return grouped_img_data_paths_dict


def open_image_data(img_data_path: Path, chunks: Any = True) -> xr.DataArray:
    """
    This function opens the JP2000 image of the band in question as dask array.

    Parameters
    ----------
    img_data_path
        The path of the image data of the band in question.

    Returns
    -------
    img_data_raster
        The dask array raster of the band in question opened granule image data.
    """

    # since the cog store is non product specific, many variable do not have a geo-reference
    # hence we filter out NotGeoreferencedWarning warnings
    warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

    # Open the raster
    img_data_raster = rxr.open_rasterio(
        img_data_path,
        chunks=chunks,
    )

    return img_data_raster  # type: ignore


# Populating the initiated full image
def concatenate_all_the_imgs_jp2s(
    grouped_img_data_paths_dict: dict[str, list[Path]],
    chunk_size: tuple[int, int],
    orbit_direction: OrbitDirectionType,
    default_chunks: Any = True,
) -> xr.DataArray:
    """
    This function builds the full swath image data of the band in question by concatenating the dask arrays of its
    individual granules. It handles missing detectors and scenes by concatenating a zeros dask array where the missing
    data exist.

    Parameters
    ----------
    grouped_img_data_paths_dict
        The dictionary containing the paths of the image data of the band in question grouped by scene time.
    chunk_size
        The chunk size (i.e., a granule size).
    orbit_direction:
        The orbit direction.

    Returns
    -------
    full_concat
        The full swath image data dask array of the band in question.
    """

    # Build the zeros dask array to be placed where missing data exist
    zeros = da.zeros(chunk_size, dtype="float32")

    # Define the list hosting the scenes data
    time_rasters: list[xr.DataArray] = []
    # Iterate over scene time and the corresponding data paths
    for _, img_data_path in grouped_img_data_paths_dict.items():
        # Handle missing scenes
        if len(img_data_path) <= 0:
            # Append the zeros dask array to the detector list
            time_rasters.append(zeros)
        else:
            # Load the data of existing detectors as a dask array
            img_data = open_image_data(img_data_path[0], chunks=default_chunks)
            # Drop the irrelevant dimension
            img_data = img_data.isel(band=0, drop=True)

            # Check the orbit direction
            if orbit_direction == "descending":
                img_data = img_data.data

            elif orbit_direction == "ascending":
                # Rotate the data so the first line is at the bottom
                img_data = img_data.data[::-1]

            # Populate the scene list with the concatenating scene full image
            time_rasters.append(img_data)

    # Build the full swath image by concatenating the scene list populated with dask arrays of the concatenating scene
    # full images
    full_concat = da.concatenate(time_rasters, axis=0)  # time/y/alt

    return full_concat


# Populating the initiated full image
def concatenate_all_the_qualit_msks_jp2s(
    grouped_img_data_paths_dict: dict[str, list[Path]],
    chunk_size: tuple[int, int],
    orbit_direction: OrbitDirectionType,
) -> xr.DataArray:
    """
    This function builds the full swath quality masks data of the band in question by concatenating the dask arrays of
    its individual granules. It handles missing detectors and scenes by concatenating a zeros dask array where the
    missing data exist.

    Parameters
    ----------
    grouped_img_data_paths_dict
        The dictionary containing the paths of the image data of the band in question grouped by scene time.
    chunk_size
        The chunk size (i.e., a granule size).
    orbit_direction:
        The orbit direction.

    Returns
    -------
    full_concat
        The full swath quality mask data dask array of the band in question.
    """

    # Build the zeros dask array to be placed where missing data exist
    zeros = da.zeros(chunk_size, dtype="uint16")

    # Define the list hosting the scenes data
    time_rasters: list[xr.DataArray] = []
    # Iterate over scene time and the corresponding data paths
    for _, mask_data_path in grouped_img_data_paths_dict.items():
        # Handle missing scenes
        if len(mask_data_path) <= 0:
            # Append the zeros dask array to the detector list
            time_rasters.append(zeros)
        else:
            # Load the data of existing detectors as a dask array
            masks_data = open_image_data(mask_data_path[0])
            # Encode each mask into the encoded_masks array
            for i in range(masks_data.shape[0]):
                # get the data of a single mask and ensure correct datatype
                mask_data = masks_data[i].astype(np.uint16)

                # Check the orbit direction
                if orbit_direction == "descending":
                    mask_data = mask_data.data

                elif orbit_direction == "ascending":
                    # Rotate the data so the first line is at the bottom
                    mask_data = mask_data.data[::-1]

                # Merge the masks into bitpack mask
                zeros |= mask_data << i

            # Populate the detector list with the dask arrays
            time_rasters.append(zeros)

    # Build the full swath image by concatenating the scene list populated with dask arrays of the concatenating scene
    # full images
    full_concat = da.concatenate(time_rasters, axis=0)  # time/y/alt

    return full_concat


def classify_polygon_sides(polygon: Polygon) -> dict[str, LineString]:
    """
    Classify the sides of a four-sided polygon into 'top', 'bottom', 'left', and 'right'.

    This function assumes that the polygon is four-sided and that the sides can be distinguished based on their
    latitude and longitude coordinates. It does not account for cases where the polygon's sides may be aligned or of
    equal length.

    Parameters
    ----------
    polygon
        A shapely Polygon object representing a four-sided polygon.

    Returns
    -------
    sides
        A dictionary with keys 'top', 'bottom', 'left', 'right', each mapping to a LineString object representing the
        respective side of the polygon.
    """

    # Extract the coordinates of the polygon's exterior ring, excluding the duplicated start/end coordinate.
    coords = list(polygon.exterior.coords)[:-1]

    # Initialize the dictionary to store the classified sides.
    sides = {"top": None, "bottom": None, "left": None, "right": None}

    # Sort the coordinates by latitude (y-coordinate) primarily, and then by longitude (x-coordinate).
    # This will order the points from bottom to top, left to right.
    coords_sorted = sorted(coords, key=lambda x: (x[1], x[0]))

    # The first two points in the sorted list will form the bottom side (smallest latitude),
    # and the last two points will form the top side (largest latitude).
    bottom = LineString([coords_sorted[0], coords_sorted[1]])
    top = LineString([coords_sorted[2], coords_sorted[3]])

    # Sort the coordinates by longitude (x-coordinate) primarily, and then by latitude (y-coordinate).
    # This will order the points from left to right, bottom to top.
    coords_sorted = sorted(coords, key=lambda x: (x[0], x[1]))

    # The first two points in the sorted list will form the left side (smallest longitude),
    # and the last two points will form the right side (largest longitude).
    left = LineString([coords_sorted[0], coords_sorted[1]])
    right = LineString([coords_sorted[2], coords_sorted[3]])

    # Assign the identified LineString objects to their corresponding sides in the dictionary.
    sides["top"] = top
    sides["bottom"] = bottom
    sides["left"] = left
    sides["right"] = right

    # Return the dictionary containing the classified sides of the polygon.
    return sides


def footprint_variables_building(
    granule_metadata_xml_file_path: Path,
    npts_alt: int,
    npts_act: int,
    level: ProductLevelType,
) -> dict[str, npt.NDArray[Any]]:
    """
    Extracts various geometric and positional information from a given granule metadata XML file path and store it in
    geopandas dataframe.

    Parameters
    ----------
    granule_metadata_xml_file_path
        A Path object pointing to the XML file containing the metadata.
    npts_alt
        The number of points requested for the footprint along satellite track variables (lon, lat).
    npts_act
        The number of points requested for the footprint across satellite track variables (lon, lat).
    level
        The level of the product to be processed (L1A or L1B).

    Returns
    -------
    footprint_vars
        A dictionary with keys 'top_lons', 'top_lats, 'bottom_lons', 'bottom_lats', 'left_lons', 'left_lons',
        'right_lons', 'right_lats' each mapping to a numpy array representing the coordinates of respective side of
        the footprint polygon.
    """

    # Load and parse the XML file
    tree = ET.parse(granule_metadata_xml_file_path)
    root = tree.getroot()

    # Define namespace for finding elements
    # if level == "L1A":
    #     namespaces = {"n1": "https://psd-14.sentinel2.eo.esa.int/PSD/S2_PDI_Level-1A_Granule_Metadata.xsd"}
    # elif level == "L1B":
    #     namespaces = {"n1": "https://psd-14.sentinel2.eo.esa.int/PSD/S2_PDI_Level-1B_Granule_Metadata.xsd"}

    namespaces = extract_namespaces(root)

    # Extract the "EXT_POS_LIST" string
    ext_pos_list_element = root.find(
        ".//n1:Geometric_Info//Granule_Footprint//Footprint//EXT_POS_LIST",
        namespaces=namespaces,
    )
    ext_pos_list = ext_pos_list_element.text.strip().split() if ext_pos_list_element is not None else []  # type: ignore

    # Build  a polygon with positions from EXT_POS_LIST
    polygon = Polygon(
        [
            [
                float(ext_pos_list[3 * i + 1]),
                float(ext_pos_list[3 * i]),
                float(ext_pos_list[3 * i + 2]),
            ]
            for i in range(4)
        ],
    )

    # Get classified polygon sides
    polygon_sides = classify_polygon_sides(polygon)

    # Calculate the total length of the side and the distances for each point
    top_total_length = polygon_sides["top"].length
    top_distances = [top_total_length * (i / (npts_act - 1)) for i in range(npts_act)]
    # Interpolate points along the side
    top_points = [polygon_sides["top"].interpolate(distance) for distance in top_distances]
    # Extract the coordinates of the points
    top_coords = [point.coords[0] for point in top_points]
    # Using list comprehension to extract the longitudes and latitudes of each top side
    # top_lons = np.asarray(sorted([coord[0] for coord in top_coords]))
    top_lons = np.asarray([coord[0] for coord in top_coords])
    # top_lats = np.asarray(sorted([coord[1] for coord in top_coords]))
    top_lats = np.asarray([coord[1] for coord in top_coords])

    # Calculate the total length of the side and the distances for each point
    bottom_total_length = polygon_sides["bottom"].length
    bottom_distances = [bottom_total_length * (i / (npts_act - 1)) for i in range(npts_act)]
    # Interpolate points along the side
    bottom_points = [polygon_sides["bottom"].interpolate(distance) for distance in bottom_distances]
    # Extract the coordinates of the points
    bottom_coords = [point.coords[0] for point in bottom_points]
    # Using list comprehension to extract the longitudes and latitudes of each bottom side
    # bottom_lons = np.asarray(sorted([coord[0] for coord in bottom_coords]))
    bottom_lons = np.asarray([coord[0] for coord in bottom_coords])
    # bottom_lats = np.asarray(sorted([coord[1] for coord in bottom_coords]))
    bottom_lats = np.asarray([coord[1] for coord in bottom_coords])

    # Calculate the total length of the side and the distances for each point
    left_total_length = polygon_sides["left"].length
    left_distances = [left_total_length * (i / (npts_alt - 1)) for i in range(npts_alt)]
    # Interpolate points along the side
    left_points = [polygon_sides["left"].interpolate(distance) for distance in left_distances]
    # Extract the coordinates of the points
    left_coords = [point.coords[0] for point in left_points]
    # Using list comprehension to extract the longitudes and latitudes of each left side
    # left_lons = np.asarray(sorted([coord[0] for coord in left_coords]))
    left_lons = np.asarray([coord[0] for coord in left_coords])
    # left_lats = np.asarray(sorted([coord[1] for coord in left_coords]))
    left_lats = np.asarray([coord[1] for coord in left_coords])

    # Calculate the total length of the side and the distances for each point
    right_total_length = polygon_sides["right"].length
    right_distances = [right_total_length * (i / (npts_alt - 1)) for i in range(npts_alt)]
    # Interpolate points along the side
    right_points = [polygon_sides["right"].interpolate(distance) for distance in right_distances]
    # Extract the coordinates of the points
    right_coords = [point.coords[0] for point in right_points]
    # Using list comprehension to extract the longitudes and latitudes of each right side
    # right_lons = np.asarray(sorted([coord[0] for coord in right_coords]))
    right_lons = np.asarray([coord[0] for coord in right_coords])
    # right_lats = np.asarray(sorted([coord[1] for coord in right_coords]))
    right_lats = np.asarray([coord[1] for coord in right_coords])

    # Integrating the footprint variables information into the output dictionary
    footprint_vars = {
        "top_lons": top_lons,
        "top_lats": top_lats,
        "bottom_lons": bottom_lons,
        "bottom_lats": bottom_lats,
        "left_lons": left_lons,
        "left_lats": left_lats,
        "right_lons": right_lons,
        "right_lats": right_lats,
    }

    return footprint_vars


def build_detector_swath_footprint(
    grouped_granule_metadata_paths_dict: dict[str, list[Path]],
    npts_alt: int,
    npts_act: int,
    orbit_direction: OrbitDirectionType,
    level: ProductLevelType,
) -> dict[str, npt.NDArray[Any]]:
    """
    Build the detector swath footprint dictionary for a given  detector.

    This function takes as input an ordered dictionary containing paths of metadata files for each
    granule that belongs to a specific detector and builds the corresponding footprint geojson dictionary.

    Parameters:
    ----------
    grouped_granule_metadata_paths_dict
        An ordered dictionary where keys are the names of detectors and values are lists of file paths pointing to
        metadata files belonging to this detector.
    npts_alt
        The number of points requested for the footprint along satellite track variables (lon, lat).
    npts_act
        The number of points requested for the footprint across satellite track variables (lon, lat).
    orbit_direction
        The direction of the orbit.
    level
        The level of the product to be processed (L1A or L1B).

    Returns:
    -------
    detector_swath_footprint
        A dictionary containing the detector swath footprint variables.
    """

    # Initialize empty lists to store results
    detector_footprint_alt_lons_list = []
    detector_footprint_alt_lats_list = []

    detector_footprint_act = []

    # Iterate over the groups of metadata files for one particular detector
    for (
        scene_time,
        granule_metadata_path,
    ) in grouped_granule_metadata_paths_dict.items():
        # Extract the footprint of the detector granules (based on scene time)
        footprint_vars = footprint_variables_building(
            granule_metadata_path[0],
            npts_alt,
            npts_act,
            level,
        )
        # Populate  the detector along satellite track footprint lists
        detector_footprint_alt_lons_list.append(
            np.column_stack((footprint_vars["left_lons"], footprint_vars["right_lons"])),
        )
        detector_footprint_alt_lats_list.append(
            np.column_stack((footprint_vars["left_lats"], footprint_vars["right_lats"])),
        )
        # Different population needed due to the desire to keep only the top and bottom side of the detector entire
        # swath
        detector_footprint_act.append(
            (
                footprint_vars["top_lats"].mean(),
                footprint_vars["top_lats"],
                footprint_vars["top_lons"],
            ),
        )
        detector_footprint_act.append(
            (
                footprint_vars["bottom_lats"].mean(),
                footprint_vars["bottom_lats"],
                footprint_vars["bottom_lons"],
            ),
        )

    # Concatenate the along satellite track footprint variables for the detector swath
    detector_footprint_alt_lons: npt.NDArray[Any] = np.vstack(detector_footprint_alt_lons_list)
    detector_footprint_alt_lats: npt.NDArray[Any] = np.vstack(detector_footprint_alt_lats_list)

    # Get the indices that would sort the first column (swath left) of the along satellite track footprint latitude
    # array
    ascending_sorted_indices = np.argsort(detector_footprint_alt_lats[:, 0])
    # Reverse the sorted indices for descending order as the satellite orbit
    descending_sorted_indices = ascending_sorted_indices[::-1]

    # Check the orbit direction
    if orbit_direction == "descending":
        # Sort the rows of both arrays using the obtained indices
        detector_footprint_alt_lons = detector_footprint_alt_lons[descending_sorted_indices]
        detector_footprint_alt_lats = detector_footprint_alt_lats[descending_sorted_indices]

    elif orbit_direction == "ascending":
        # Sort the rows of both arrays using the obtained indices
        detector_footprint_alt_lons = detector_footprint_alt_lons[ascending_sorted_indices]
        detector_footprint_alt_lats = detector_footprint_alt_lats[ascending_sorted_indices]

    # Sort the across track list to identify the top and the bottom of the detector swath
    detector_footprint_act = sorted(detector_footprint_act, key=lambda x: x[0])
    # Extract the across satellite track footprint variables for the top and bottom of the detector swath
    detector_footprint_act_lons: npt.NDArray[Any] = np.column_stack(
        (detector_footprint_act[-1][2], detector_footprint_act[0][2]),
    )
    detector_footprint_act_lats: npt.NDArray[Any] = np.column_stack(
        (detector_footprint_act[-1][1], detector_footprint_act[0][1]),
    )

    # Integrating the detector swath footprint variables information into the output dictionary
    detector_swath_footprint: dict[str, npt.NDArray[Any]] = {
        "alt_lons": detector_footprint_alt_lons,
        "alt_lats": detector_footprint_alt_lats,
        "act_lons": detector_footprint_act_lons,
        "act_lats": detector_footprint_act_lats,
    }

    return detector_swath_footprint


def extract_namespaces(xml_root: ET.Element) -> dict[str, str]:
    """
    Extracts namespaces from the XML root element.

    Parameters
    ----------
    xml_root
        The root element of the XML document.

    Returns
    -------
    namespaces
        A dictionary mapping namespace prefixes to their URI strings.
    """

    namespaces: dict[str, str] = {}
    for elem in xml_root.iter():
        # Check if the element tag contains a namespace URI.
        if "}" in elem.tag:
            uri, _ = elem.tag[1:].split("}", 1)
            # Add the namespace URI to the dictionary with a generated prefix, if not already present.
            if uri not in namespaces.values():
                namespaces[f"n{len(namespaces) + 1}"] = uri
    return namespaces


def build_paths_excluding_root(
    element: ET.Element,
    current_path: str = "",
    namespaces: dict[str, str] | None = None,
) -> list[str]:
    """
    Builds XPath-like paths for elements in the XML, excluding specified root elements and including conditions based
    on attributes.

    Parameters
    ----------
    element
        The current XML element to process.
    current_path, optional
        The accumulated path of the current element's ancestors, by default "".
    namespaces, optional
        A dictionary of namespace prefixes and their URIs, by default None.

    Returns
    -------
    paths
        A list of constructed XPath-like paths.
    """

    paths = []

    # Extract namespaces from the current element if not provided.
    if namespaces is None:
        namespaces = extract_namespaces(element)

    for child in element:
        # Parse the child element's tag to extract or construct its full path.
        uri, local_part = child.tag[1:].split("}", 1) if "}" in child.tag else ("", child.tag)
        prefix = [k for k, v in namespaces.items() if v == uri]
        tag_with_prefix = f"{prefix[0]}:{local_part}" if prefix else local_part

        # Construct the child's path by appending it to the current path.
        child_path = f"{current_path}/{tag_with_prefix}" if current_path else tag_with_prefix

        # Filter and modify paths based on specific conditions and attributes.
        if (
            any(
                keyword in child_path
                for keyword in [
                    "General_Info",
                    "Image_Data_Info",
                    "Quality_Indicators_Info",
                ]
            )
            and "Granules_Information" not in child_path
        ):
            # Append attribute conditions to the path if present.
            for attrib_key in ["detectorId", "bandId", "pos"]:
                if attrib_key in child.attrib:
                    child_path += f"[@{attrib_key}='{child.attrib[attrib_key]}']"

            # Add the constructed path to the list and recursively process children.
            paths.append(child_path)
            paths.extend(build_paths_excluding_root(child, child_path, namespaces))

            # Handle 'unit' attribute specifically, constructing additional paths.
            if "unit" in child.attrib:
                child_path_value = f"{child_path}/VALUE_{child.attrib['unit']}"
                child_path_unit = f"{child_path}/UNIT_{child.attrib['unit']}"
                paths.append(child_path_value)
                paths.append(child_path_unit)

    return paths


def build_nested_dict(paths: list[str]) -> dict[Any, Any]:
    """
    Constructs a nested dictionary from a list of XPath-like paths.

    Parameters
    ----------
    paths
        A list of paths representing the structure and attributes of the XML document.

    Returns
    -------
    nested_dict
        A nested dictionary reflecting the XML structure based on the provided paths.
    """

    nested_dict: dict[Any, Any] = {}

    for path in paths:
        # Split the path into parts and initialize the current level at the root of the dictionary
        parts = path.strip("/").split("/")
        current_level = nested_dict

        # Iterate over the parts of the path
        for i, part in enumerate(parts):
            is_last_part = i == len(parts) - 1

            # Process the part to handle special cases, e.g., attributes and namespaces.
            # This involves modifying the part based on certain conditions to properly nest it within the dictionary.
            if not ("Detector_List" in part or "Band_List" in part):

                if "n1:" in part:
                    part = part[3:]

                # to  handle cases where there are detector or band lists
                if "detectorId" in part:
                    part = part.split("[@")[-1][:-2].split("=")  # type: ignore
                    part = f"{part[0][:-2]}{int(part[1][1:])}"

                elif "bandId" in part:
                    part = part.split("[@")[-1][:-2].split("=")  # type: ignore
                    if int(part[1][1:]) == 8:
                        part = f"{part[0][:-2]}{int(part[1][1:])}A"
                    elif int(part[1][1:]) < 8:
                        part = f"{part[0][:-2]}{int(part[1][1:])+1}"
                    else:
                        part = f"{part[0][:-2]}{int(part[1][1:])}"

                elif "[@pos='" in part:
                    part = part.split("[@pos='")  # type: ignore
                    part = f"{part[0]}_{part[1][:-2]}"

                elif "VALUE_" in part:
                    part = part.split("_")  # type: ignore
                    part = part[0]
                    path_alt = "/".join(path.split("/")[:-1])

                elif "UNIT_" in part:
                    part0 = part.split("_")
                    part = part0[0]
                    path_alt = part0[-1]

                part = part.lower()

                # If the part is not yet a key in the current level of the dictionary, create a new dictionary at this
                # level
                if part not in current_level:
                    if "VALUE_" in path or "UNIT_" in path:
                        current_level[part] = path_alt if is_last_part else {}
                    else:
                        current_level[part] = path if is_last_part else {}

                elif not is_last_part:
                    # If the current part is not the last one and it's a string, it means we have a shorter path
                    # previously set as a leaf node. Convert it into a dictionary.
                    if isinstance(current_level[part], str):
                        current_level[part] = {}
                    current_level = current_level[part]

    return nested_dict


def replace_tags_with_values(
    d: dict[str, dict[Any, Any] | str],
    parent: ET.Element,
    namespaces: dict[str, str],
) -> dict[str, dict[Any, Any] | str]:
    """
    Recursively replaces values in a nested dictionary that represent XML tag paths
    with the actual text content of these tags from an XML document, using specified namespaces.

    The function traverses the dictionary, and for each string value, which is expected
    to represent an XML path, it finds the corresponding XML element starting from the given
    parent element. If the element is found, the function replaces the dictionary's string
    value with the element's text content. The process is recursive for nested dictionaries.

    Parameters
    ----------
    d
        The nested dictionary where string values represent.
    parent
        The parent XML element from which to start the search for each tag.
    namespaces
        A dictionary mapping namespace prefixes to their URI strings.

    Returns
    -------
    d
        The modified the dictionary.
    """

    for key, value in d.items():
        if isinstance(value, dict):
            # Recursive call for nested dictionaries
            replace_tags_with_values(value, parent, namespaces)
        else:
            # Extracting the namespace prefix and tag name
            ns_prefix, _, tag = value.partition(":")
            if ns_prefix in namespaces:
                # Constructing the full tag with namespace for search
                ns_uri = namespaces[ns_prefix]
                full_tag = f"{{{ns_uri}}}{tag}"
            else:
                # If namespace prefix not found, use tag as is
                full_tag = tag

            # Handling the units tags
            if "/" in full_tag:
                # Finding the element with the tag, considering the namespace
                element = parent.find(".//" + full_tag, namespaces=namespaces)
                if element is not None:
                    # Replacing the dictionary value with the element text
                    d[key] = element.text  # type: ignore

    return d


def build_product_metadata(datastrip_metadata_xml_file_path: Path, level: ProductLevelType) -> dict[Any, Any]:
    """
    Extracts various product metadata information from a given datastrip metadata XML file (SAFE) path.

    Parameters
    ----------
    datastrip_metadata_xml_file_path
        A Path object pointing to the XML file containing the metadata.
    level
        The level of the product to be processed (L1A or L1B).

    Returns
    -------
    metadata_dict
        A dictionary containing the extracted metadata.
    """

    # Load and parse the XML file
    tree = ET.parse(datastrip_metadata_xml_file_path)
    root = tree.getroot()

    # Define namespace for finding elements
    if level == "L1A":
        namespaces = {"n1": "https://psd-14.sentinel2.eo.esa.int/PSD/S2_PDI_Level-1A_Datastrip_Metadata.xsd"}
    elif level == "L1B":
        namespaces = {"n1": "https://psd-14.sentinel2.eo.esa.int/PSD/S2_PDI_Level-1B_Datastrip_Metadata.xsd"}

    # Build and print all paths excluding the root
    all_paths_excluding_root = build_paths_excluding_root(root)

    # Removing duplicates from the generated list of paths
    # Using a set to remove duplicates while preserving the order
    unique_paths = list(dict.fromkeys(all_paths_excluding_root))

    # Constructing the nested dictionary
    nested_dict = build_nested_dict(unique_paths)

    # Replace the values in the nest dictionary with the actual data
    metadata_dict = replace_tags_with_values(nested_dict, root, namespaces)

    return metadata_dict
