import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Self, Union

import lxml.etree
from shapely.affinity import translate
from shapely.geometry import MultiPolygon, Polygon


class FormattingError(Exception):
    pass


def poly_coords_parsing(a_string: str) -> list[float]:
    """Used to parse a string with coordinates and convert it to a list of points (latitude, longitude)

    Parameters
    ----------
    a_string: str
        String (xpath output usually) with ``posList`` coordinates (separated by a white space)

    Returns
    ----------
    List[List[float]]
        List containing pairs of coordinates cast to floating point representation (latitude, longitude)
    """
    # remove comma for coordinates pairs (S1-specific)
    return [float(f) for f in a_string.strip().replace(",", " ").split(" ")]


def detect_pole_or_antemeridian(coordinates: List[List[float]]) -> bool:
    """Verify if a list of coordinates crosses a antemeridian or a pole

    Parameters
    ----------
    coordinates: List[List[float]]
        List containing pairs of coordinates (latitude, longitude)

    Returns
    ----------
    bool:
        True if coordinates cross pole/antemeridian at least once, False otherwise
    """
    import itertools

    longitude_threshold = 270
    crossing = 0
    # Flat coordinates in order to iterate only over longitudes
    flatten_coords = [longitude for longitude in itertools.chain.from_iterable(coordinates)]
    # Compare absolute difference of longitude[i+1], longitude[i] with threshold
    for current_longitude, next_longitude in zip(flatten_coords[1::2], flatten_coords[3::2]):
        longitude_difference = abs(next_longitude - current_longitude)
        if longitude_difference > longitude_threshold:
            crossing += 1

    return crossing >= 1


def split_poly(polygon: Polygon) -> MultiPolygon:
    the_planet = Polygon([[-180, 90], [180, 90], [180, -90], [-180, -90], [-180, 90]])
    shifted_planet = Polygon([[180, 90], [540, 90], [540, -90], [180, -90], [180, 90]])
    normalized_points = []
    for point in polygon.exterior.coords:
        lon = point[0]
        if lon < 0.0:
            lon += 360.0
        normalized_points.append([lon, point[1]])

    normalized_polygon = Polygon(normalized_points)

    # cut out eastern part (up to 180 deg)
    intersection_east = the_planet.intersection(normalized_polygon)

    # cut out western part - shifted by 360 deg using the shifted planet boundary
    # and shift the intersection back westwards to the -180-> 180 deg range
    intersection_west = shifted_planet.intersection(normalized_polygon)
    shifted_back = translate(intersection_west, -360.0, 0, 0)

    return MultiPolygon([intersection_east, shifted_back])


class EOAbstractFormatter(ABC):
    """Abstract formatter representation"""

    def __init__(self, inner_formatter: Optional[Self] = None) -> None:
        self._inner_formatter = inner_formatter
        self._logger = logging.getLogger("eopf.formatting")

    @property
    @abstractmethod
    def name(self) -> str:
        """Set the name of the formatter, for registering it"""
        raise NotImplementedError()

    def format(self, input: Any) -> Any:
        """Function that returns the formatted input"""
        if self._inner_formatter is not None:
            return self._format(self._inner_formatter.format(input))
        else:
            return self._format(input)

    @abstractmethod
    def _format(self, input: Any) -> Any:
        raise NotImplementedError

    def reverse_format(self, input: Any) -> Any:
        """Function that returns the reverse of the formatted input"""
        return input


class EOListValuesFormatter(EOAbstractFormatter):
    """Abstract formatter representation for a lists"""

    @abstractmethod
    def _format(self, input: List[Any]) -> Any:
        """Function that returns the formatted input"""
        raise NotImplementedError()

    def reverse_format(self, input: Any) -> Any:
        """Function that returns the reverse of the formatted input"""
        return input


class EOAbstractXMLFormatter(EOListValuesFormatter):
    """ "
    specialization for xml input formatter
    """

    @abstractmethod
    def _format(self, input: List[lxml.etree._Element]) -> Any:
        """Function that returns the formatted input"""
        raise NotImplementedError()


class ToListStr(EOAbstractXMLFormatter):
    name = "to_list_str"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> Any:
        return [element for element in xpath_input]


class ToBbox(EOAbstractFormatter):
    """Formatter for computing coordinates of a polygon bounding box"""

    # docstr-coverage: inherited
    name = "to_bbox"

    # docstr-coverage: inherited
    def _format(self, input: Any) -> List[float]:
        """Computes coordinates of a polygon bounding box

        Parameters
        ----------
        path: str
            xpath

        Returns
        ----------
        List[float]:
            Returns a list with coordinates, longitude, latitude for SW/NE points

        Raises
        ----------
        FormattingError
            When formatting can not be performed
        """
        import ast

        # when reconverting back to SAFE, the input can be directly evaluated as a list
        try:
            return list(to_stac_bbox(ast.literal_eval(input)))
        except (ValueError, SyntaxError):
            pass

        # when converting from SAFE, parse the input
        try:
            return list(to_stac_bbox(poly_coords_parsing(a_string=input)))
        except Exception as e:
            raise FormattingError(f"{e}")


class ToGeoJson(EOAbstractFormatter):
    """Formatter for converting polygon coordinates to geoJson format"""

    # docstr-coverage: inherited
    name = "to_geoJson"

    # docstr-coverage: inherited
    def _format(self, input: Any) -> Dict[str, Union[List[Any], str]]:
        """Computes polygon coordinates in geoJson format,
        from xml acquired coordinates

        Parameters
        ----------
        input: str

        Returns
        ----------
        List[List[float]]:
            Returns a list of lists(tuples) containing a pair (latitude, longitude) for each point of a polygon.

        Raises
        ----------
        FormattingError
            When formatting can not be performed
        """
        import ast

        # when reconverting back to SAFE, the input can be directly evaluated as a list
        try:
            return dict(type="Polygon", coordinates=[ast.literal_eval(input)])
        except (ValueError, SyntaxError):
            pass

        # when converting from SAFE, parse the input
        try:
            poly_coords_str = input
            poly_coords_flat = poly_coords_parsing(poly_coords_str)
            poly_coords = list(zip(poly_coords_flat[0::2], poly_coords_flat[1::2]))
            # If polygon coordinates crosses any pole or antemeridian, split the polygon in a multipolygon
            if detect_pole_or_antemeridian(poly_coords):
                return dict(type="MultiPolygon", coordinates=split_poly(poly_coords))
            # Otherwise, just return computed coordinates
            return dict(type="Polygon", coordinates=[poly_coords])
        except Exception as e:
            raise FormattingError(f"{e}")


def to_stac_bbox(gml_coordinates: list[float]) -> tuple[float, float, float, float]:
    lons = gml_coordinates[0::2]
    lats = gml_coordinates[1::2]

    # empirical! in theory due to earth curvature even the tile near the equator crosses the antimeridian
    cross_antimeridian = 180 in gml_coordinates

    if cross_antimeridian:
        stac_bbox = max(lons), min(lats), min(lons), max(lats)
    else:
        stac_bbox = min(lons), min(lats), max(lons), max(lats)

    return stac_bbox
