"""
Convert a S2 MSI SAFE Tile to Zarr.

Can also be used to only open a SAFE, represent it in-memory with a DataTree, and optionally persisting it to Zarr.

One-way conversion SAFE -> Zarr. The other way around is not supported.

Metadata might be lost during the conversion process. Example: DataStrip metadata is excluded by default.
"""

__all__ = ["open_s2msi_tile_safe_product"]

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Literal, Self, Sequence, get_args

import click
import numpy as np
import rioxarray
import xarray as xr
from bs4 import BeautifulSoup
from lxml import etree
from lxml.etree import XPathEvalError
from xarray import DataTree

try:
    from eopf.formatting.geometry_formatters import ToBbox, ToGeoJson
    from eopf.formatting.xml_formatters import ToListStr
except (ImportError, TypeError):
    from sentineltoolbox.local_eopf.formatters import ToBbox, ToGeoJson, ToListStr
from sentineltoolbox.models.filename_generator import ProductFileNameGenerator
from sentineltoolbox.models.s2_legacy_product_name import S2MSIL1CProductURI

DEFAULT_CHUNKS = {}

to_geojson = ToGeoJson()._format
to_bbox = ToBbox()._format
to_list_str = ToListStr()._format


S2L1CProductMetadata = dict[str, Any]

L2A_NATIVE_RESOLUTION = 20  # in meters

ProductLevelType = Literal["L1C", "L2A"]

# Standalone Conversion - Taken from s2msi - START - 20240916
ResolutionType = Literal[10, 20, 60]
BandNameType = Literal[
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
]
BandNameToResolutionMapping: dict[BandNameType, ResolutionType] = {
    "b01": 60,
    "b02": 10,
    "b03": 10,
    "b04": 10,
    "b05": 20,
    "b06": 20,
    "b07": 20,
    "b08": 10,
    "b8a": 20,
    "b09": 60,
    "b10": 60,
    "b11": 20,
    "b12": 20,
}
BAND_NAMES = tuple(get_args(BandNameType))


def bitpack_raster_with_bands(raster: xr.DataArray, *, nbits: Literal[8, 16, 32, 64] = 8) -> xr.DataArray:
    """
    Bitpack a 3-D boolean array to a 2-D uint8 array

    See also notebook:
    https://gitlab-dpr.acrist-services.com/S2/msi/s2msi/-/blob/edhah/finalize_radiometric_correction/notebooks/drafts
    /convert_safe2zarr_L1AB_v6.ipynb?ref_type=heads

    Parameters
    ----------
    raster
        3-D boolean array

    Returns
    -------
        2-D uint8 array

    Raises
    ------
    NotImplementedError
        If more than 8 bands are present
    """
    n_bands = raster["band"].size
    if n_bands > nbits:
        raise NotImplementedError(f"Cannot pack more than {nbits=} bands in a byte (uint8).")
    bitpacked_raster = sum(
        (raster.isel(band=band_index, drop=True) * (1 << band_index)) for band_index in range(n_bands)
    ).astype(  # type: ignore
        dtype=f"uint{nbits}",
        copy=False,
    )
    return bitpacked_raster


@dataclass(kw_only=True, frozen=True)
class S02MSITileZarrPathRenderer:
    """
    Helper to build resolution-dependant paths for S2MSI L1C and L2A Products.

    Exposes absolute paths as properties, allowing discovery in live Python sessions
    and improved type-checking, and adds flexibility as it de-hardcodes any path
    from the source code, if consistently used.

    Attributes
    -------
    resolution
        Resolution, optional
        If provided, append the resolution path part to any resolution-dependant paths
        If not provided, only provide the prefix of resolution-dependant paths
        The type is not enforced. It is expected to be any valid resolution accepted
        by a L1C or L2A product (10, 20, 60)

    Raises
    ------
    ValueError
        When trying to render the resolution group part path if resolution was not provided.
    """

    resolution: int | None = None

    @property
    def geometry(self) -> PurePosixPath:
        return PurePosixPath("/conditions/geometry")

    @property
    def mean_sun_angles(self) -> PurePosixPath:
        return self.geometry / "mean_sun_angles"

    @property
    def mean_viewing_incidence_angles(self) -> PurePosixPath:
        return self.geometry / "mean_viewing_incidence_angles"

    @property
    def sun_angles(self) -> PurePosixPath:
        return self.geometry / "sun_angles"

    @property
    def viewing_incidence_angles(self) -> PurePosixPath:
        return self.geometry / "viewing_incidence_angles"

    @property
    def detector_footprint(self) -> PurePosixPath:
        path = PurePosixPath("/conditions/mask/detector_footprint/")
        return path if self.resolution is None else (path / self.resolution_group)

    @property
    def l1c_classification(self) -> PurePosixPath:
        # Mask S2
        path = PurePosixPath("/conditions/mask/l1c_classification/")
        return path if self.resolution is None else (path / self.resolution_group)

    @property
    def l1c_cloud_mask(self) -> PurePosixPath:
        return self.l1c_classification / "b00"

    @property
    def l2a_classification(self) -> PurePosixPath:
        # Scene Classification
        path = PurePosixPath("/conditions/mask/l2a_classification/")
        return path if self.resolution is None else (path / self.resolution_group)

    @property
    def scl(self) -> PurePosixPath:
        return self.scene_classification

    @property
    def scene_classification(self) -> PurePosixPath:
        return self.l2a_classification / "scl"

    @property
    def dem(self) -> PurePosixPath:
        return self.l2a_classification / "dem"

    @property
    def slp(self) -> PurePosixPath:
        return self.l2a_classification / "slp"

    @property
    def asp(self) -> PurePosixPath:
        return self.l2a_classification / "asp"

    @property
    def sdw(self) -> PurePosixPath:
        return self.l2a_classification / "sdw"

    @property
    def lcm(self) -> PurePosixPath:
        return self.esacci_lcm

    @property
    def esacci_lcm(self) -> PurePosixPath:
        return self.l2a_classification / "lcm"

    @property
    def wbi(self) -> PurePosixPath:
        return self.esacci_wbi

    @property
    def esacci_wbi(self) -> PurePosixPath:
        return self.l2a_classification / "wbi"

    @property
    def snc(self) -> PurePosixPath:
        return self.esacci_snc

    @property
    def esacci_snc(self) -> PurePosixPath:
        return self.l2a_classification / "snc"

    @property
    def meteorology(self) -> PurePosixPath:
        return PurePosixPath("/conditions/meteorology")

    @property
    def meteo_cams(self) -> PurePosixPath:
        return self.meteorology / "cams"

    @property
    def meteo_ecmwf(self) -> PurePosixPath:
        return self.meteorology / "ecmwf"

    @property
    def reflectance(self) -> PurePosixPath:
        path = PurePosixPath("/measurements/reflectance/")
        return path if self.resolution is None else (path / self.resolution_group)

    @property
    def quality_mask(self) -> PurePosixPath:
        path = PurePosixPath("/quality/mask/")
        return path if self.resolution is None else (path / self.resolution_group)

    @property
    def atmosphere(self) -> PurePosixPath:
        path = PurePosixPath("/quality/atmosphere/")
        return path if self.resolution is None else (path / self.resolution_group)

    @property
    def aot(self) -> PurePosixPath:
        return self.atmospherical_optical_thickness

    @property
    def atmospherical_optical_thickness(self) -> PurePosixPath:
        return self.atmosphere / "aot"

    @property
    def wvp(self) -> PurePosixPath:
        return self.water_vapour

    @property
    def water_vapour(self) -> PurePosixPath:
        return self.atmosphere / "wvp"

    @property
    def vim(self) -> PurePosixPath:
        # WARNING: This is VIM with a M and not VIS, which is different! Beware when reading the logic.
        return self.visibility_cams

    @property
    def visibility_cams(self) -> PurePosixPath:
        return self.atmosphere / "vim"

    @property
    def probability(self) -> PurePosixPath:
        path = PurePosixPath("/quality/probability/")
        return path if self.resolution is None else (path / self.resolution_group)

    @property
    def cld(self) -> PurePosixPath:
        return self.cloud_confidence_mask

    @property
    def cloud_confidence_mask(self) -> PurePosixPath:
        return self.probability / "cld"

    @property
    def snw(self) -> PurePosixPath:
        return self.snow_confidence_mask

    @property
    def snow_confidence_mask(self) -> PurePosixPath:
        return self.probability / "snw"

    @property
    def resolution_group(self) -> PurePosixPath:
        if self.resolution is None:
            raise ValueError("Cannot render a resolution-dependant tile zarr path.")
        return PurePosixPath(f"r{self.resolution}m")

    @property
    def tci_l1c(self) -> PurePosixPath:
        if self.resolution is None:
            raise ValueError("Cannot render a resolution-dependant tile zarr path.")
        return PurePosixPath(f"/quality/l1c_quicklook/r{self.resolution}m/tci")

    @property
    def tci_l2a(self) -> PurePosixPath:
        if self.resolution is None:
            raise ValueError("Cannot render a resolution-dependant tile zarr path.")
        return PurePosixPath(f"/quality/l2a_quicklook/r{self.resolution}m/tci")

    @staticmethod
    def extract_resolution_from_path(path: PurePosixPath) -> ResolutionType:
        """
        Extract resolution from path

        Parameters
        ----------
        path
            Path to extract the resolution from, eg

        Returns
        -------
            Resolution extracted from the input path
        """
        if "r60m" in path.parts:
            return 60
        if "r20m" in path.parts:
            return 20
        if "r10m" in path.parts:
            return 10
        raise ValueError(f"No resolution could be extracted from the given {path=}")

    @staticmethod
    def determine_lowest_resolution_in_a_list_of_paths(paths: Sequence[PurePosixPath]) -> int:
        """
        Determine the lowest resolution in a list of paths.

        Careful with wording: lowest resolution has actually the highest associated integer value.

        Parameters
        ----------
        paths
            Sequence of PurePosixPaths. All of them are expected to contain a resolution group in their parts.

        Returns
        -------
            The lowest resolution (maximum value of resolution)
        """
        lowest_resolution = max(S02MSITileZarrPathRenderer.extract_resolution_from_path(path) for path in paths)
        return lowest_resolution


def repr_datatree(
    xdt: DataTree,
    *,
    tabsize: int = 4,
    offset: int = 1,
    with_full_path: bool = False,
    with_group_variables: bool = False,
    rich: bool = False,
    rich_plot: bool = False,
    rich_txt_dataset: bool = True,
    opened: bool = False,
) -> str:
    """
    Represent a DataTree

    Parameters
    ----------
    xdt
        DataTree to represent
    tabsize, optional
        If ``rich`` is OFF, amount of tabs in the text representation, by default 4
    offset, optional
        If ``rich`` is OFF, initial amount of tabs, by default 1
    with_full_path, optional
        Whether to repr the full path or the stem of a Node., by default False
    with_group_variables, optional
        Whether to repr groups only, or groups with their variables, by default False
    rich, optional
        Use rich HTML representation, by default False
    rich_plot, optional
        If ``rich`` is ON, call the default xarray's ``plot`` on the node being currently represented, by default False
    rich_txt_dataset, optional
        If ``rich`` is ON, whether to display text-version or HTML-version of the node being repred, by default True
    opened, optional
        If ``rich`` is ON, whether to initially display opened or closed detail sections, by default False

    Returns
    -------
        String representation
    """
    try:
        from IPython.display import HTML, Markdown
    except ImportError:
        print("Please install IPython to get rich display")
        return repr_datatree_text(xdt)

    lines = []

    for node in sorted(xdt.subtree, key=lambda n: n.path):
        path = PurePosixPath(node.path)
        tabs = len(path.parts)
        path_str = f"{(node.name or '') if not with_full_path else path}"
        group_title = f"{path_str} <small> (<code>{path}</code>) </small>"
        if len(node.data_vars) == 0:
            if rich:
                lines.append(Markdown(f"{'#' * tabs} {group_title}"))
            else:
                lines.append(f'{" " * ((tabs - offset) * tabsize)}{group_title}')

            if node.attrs:
                lines.append(
                    Markdown(
                        wrap_in_details(
                            f"```json\n{json.dumps(node.attrs, indent=4)}\n```",
                            summary=f"Attributes <small> (`{path}`) </small>",
                            opened=opened,
                        ),
                    ),
                )

        if with_group_variables:
            for varname in node.ds.data_vars:
                varname_str = f"{path / varname if with_full_path else varname}"
                if rich:
                    if rich_plot:
                        lines.append(Markdown(varname_str))
                        lines.append(node.ds.data_vars[varname].plot())
                else:
                    lines.append(f'{" " * (tabs * tabsize)}{varname_str}')
        elif rich:
            if len(node.data_vars) > 0:
                if rich_txt_dataset:
                    lines.append(
                        HTML(wrap_in_details(node.to_dataset()._repr_html_(), summary=group_title, opened=opened)),
                    )
                    # lines.append(node.ds)
                else:
                    code = f"```python\n{str(node.ds)}\n```"
                    lines.append(Markdown(wrap_in_details(code, summary=group_title, opened=opened)))
    if rich:
        return lines
    else:
        return "\n".join(lines)


def repr_datatree_text(
    xdt: DataTree,
    *,
    tabsize: int = 4,
    offset: int = 1,
    with_full_path: bool = False,
    with_group_variables: bool = False,
) -> str:
    """
    Represent a DataTree as text

    Parameters
    ----------
    xdt
        DataTree to represent
    tabsize, optional
        If ``rich`` is OFF, amount of tabs in the text representation, by default 4
    offset, optional
        If ``rich`` is OFF, initial amount of tabs, by default 1
    with_full_path, optional
        Whether to repr the full path or the stem of a Node., by default False
    with_group_variables, optional
        Whether to repr groups only, or groups with their variables, by default False

    Returns
    -------
        DataTree text representation
    """
    lines = []
    for node in xdt.subtree:
        path = PurePosixPath(node.path)
        tabs = len(path.parts)
        lines.append(f'{" " * ((tabs - offset) * tabsize)}{(path.stem) if not with_full_path else path}')
        if with_group_variables:
            for varname in node.ds.data_vars:
                lines.append(f'{" " * (tabs * tabsize)}{path / varname if with_full_path else varname}')
    return "\n".join(lines)


def wrap_in_details(contents: str, *, summary: str | None = None, opened: bool = True) -> str:
    """
    Wrap a string in details

    Parameters
    ----------
    contents
        Input string to wrap
    summary, optional
        Summary in the tag of same name in the detail section, by default None
    opened, optional
        If ``rich`` is ON, whether to initially display opened or closed detail sections, by default False

    Returns
    -------
        HTML-string wrapped with a detail section
    """
    summary_tag = "" if summary is None else f"\n<summary> {summary} </summary>"
    details_prefix = f"<details {'open' if opened else ''}>{summary_tag}\n\n"
    details_suffix = "\n\n</summary>"

    return f"{details_prefix}{contents}{details_suffix}"


# Standalone Conversion - Taken from s2msi - END


@dataclass(frozen=True, kw_only=True)
class S02MSITileProduct:
    """
    S02 MSI Tile Product

    The role of this class is:

    - First to open a SAFE directory into a DataTree
    - Then to write this DataTree to Zarr.

    Attributes
    ------
    xdt
        The DataTree representing the SAFE product.
    """

    xdt: DataTree

    @classmethod
    def from_safe_path(cls, input_safe_path: Path, **kwargs: Any) -> Self:
        """
        Instanciate from a SAFE Path.

        Parameters
        ----------
        input_safe_path
            Input SAFE Path.
            The legacy SAFE filename must contain 'MSIL1C' or 'MSIL2A'.

        Returns
        -------
            An own instance, with ``xdt`` containing a DataTree representing the SAFE.
        """
        product_level = S2MSIL1CProductURI.from_string(input_safe_path.stem).product_level[3:]
        return cls(xdt=open_s2msi_tile_safe_product(input_safe_path, product_level=product_level, **kwargs))

    def to_zarr(self, output_zarr_path: Path, **kwargs: Any) -> None:
        """
        Write the DataTree representation of the SAFE to a Zarr store.

        Parameters
        ----------
        output_zarr_path
            Output ZARR Path
            See also ``convert_legacy_to_dpr_filename`` to construct a correct name.
        kwargs
            Any additional keyword arguments to pass to ``to_zarr``
        """
        print(f"Persist to specified output path {output_zarr_path=}")
        self.xdt.to_zarr(output_zarr_path, **kwargs)  # 20s without chunking, 60s with

        print("Re-open zarr with datatree to ensure re-readability")
        zarr_xdt = xr.open_datatree(output_zarr_path, engine="zarr")

        print("Output product structure:")
        print(repr_datatree_text(zarr_xdt))

        zarr_xdt.close()

        return None

    @staticmethod
    def convert_legacy_to_dpr_filename(legacy_filename: str | Path) -> str:
        """
        Converts a legacy SAFE filename to the DPR filename

        Parameters
        ----------
        legacy_filename
            Legacy Filename, eg ``S2A_MSIL1C_20240625T103631_N0510_R008_T31UGQ_20240625T142035.SAFE``
            Can be a string or a Path, in all case, will be converted to Path and the stem
            will be extracted from it. Path('x').stem will roundtrip 'x'.

        Returns
        -------
            The new DPR filename, eg ``S02MSIL1C_20240625T142035_0000_A008_T000.zarr``
        """
        return ProductFileNameGenerator.from_string(Path(legacy_filename).stem, duration=0).to_string()

    def text(self, **kwargs: Any) -> str:
        """
        Text

        Returns
        -------
            Lite-weight string representation of a datatree.
        """
        return repr_datatree_text(self.xdt, **kwargs)

    def get_display_cells(self, **kwargs: Any):
        """
        Display Cells

        Returns
        -------
            Returns a list of display cells on which IPython's `display` can be called.
        """
        return repr_datatree(self.xdt, rich=True, **kwargs)


@dataclass(frozen=True, kw_only=True)
class GridInfo:
    """
    Grid Info. Used to construct the Sun and Viewing Angles grid.

    Attributes
    ----------
    ulx
        Upper Left Corner x-coord
    uly
        Upper Left Corner y-coord
    sign_step_x
        Sign of step for x (+ = increasing or - = decreasing axis)
    sign_step_y
        Sign of step for y (+ = increasing or - = decreasing axis)
    """

    ulx: int
    uly: int
    sign_step_x: int
    sign_step_y: int


@dataclass(frozen=True, kw_only=True)
class AccessorXML:
    """
    Accessor in multiple XML files.

    Attributes
    ----------
    namespaces
        Dict of XML namespaces
    roots
        All XML candidates documents to try to use an xpath on.
    """

    namespaces: dict[str, dict[str, str]]
    roots: Any  # XML Node loaded from etree

    def findone(self, path) -> Any:
        """
        Find one element. Errors if not found.

        Parameters
        ----------
        path
            xpath to find

        Returns
        -------
            First found element for xpath
        """
        allfound = self.findall(path)
        return allfound[0].text

    def findoptional(self, path) -> Any:
        """
        Optionally find one element

        Parameters
        ----------
        path
            xpath to find

        Returns
        -------
            First found element for xpath, else string 'N/A'
        """
        allfound = self.findall(path)
        if allfound is None or len(allfound) == 0:
            return "N/A"
        else:
            return allfound[0].text

    def findoneattr(self, path) -> Any:
        """
        Find one attribute. Errors if not found.

        Parameters
        ----------
        path
            xpath to find

        Returns
        -------
            First found attribute for xpath
        """
        return self.findall(path)[0]

    def findalltext(self, path):
        """
        Find all elements, get their text values.

        Parameters
        ----------
        path
            xpath to find

        Returns
        -------
            List of text of all found elements.
        """
        return [el.text for el in self.findall(path)]

    def findall(self, path):
        """
        Find all elements

        Parameters
        ----------
        path
            xpath to find

        Returns
        -------
            List of all found element.s
        """
        for root, namespace_name in self.roots:
            try:
                result = root.xpath(path, namespaces=self.namespaces[namespace_name])
            except XPathEvalError:
                continue

            if len(result) > 0:
                return result
        return None


def open_s2msi_tile_safe_product(
    safe_path: Path,
    *,
    product_level: ProductLevelType | None,
    with_datastrip_metadata: bool = False,
    do_merge_meteo_data: bool = False,
    **kwargs: Any,
) -> DataTree:
    """
    Open a Sentinel-2 L1C product from a SAFE archive as a DataTree.

    Supports L1C and L2A.

    Links:

    - https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-1-sar/data-formats/safe-specification

    Parameters
    ----------
    safe_path
        Path to a S2MSI SAFE folder, L1C or L2A
    product_level
        Product level: L1C and L2A are supported, if None, guess from the SAFE path.
    with_datastrip_metadata, optional
        Read datastrip metadata (warning: slow operation), by default False
    do_merge_meteo_data, optional
        Merge ECMWF and CAMS meteo data together, by default False


    Returns
    -------
        A DataTree being the representation of the SAFE.

    Raises
    ------
    NotImplementedError
        In case the product level is unsupported or cannot be determined automatically
    """
    safe_path = Path(safe_path)

    if product_level is None:
        product_level = guess_product_level(safe_path)

    # Metadata
    attrs_from_xml = convert_xml_metadata(safe_path, product_level=product_level)

    # Raster Data
    xdt = read_product_raster_data(
        safe_path,
        product_level=product_level,
        eo_band_metadata=attrs_from_xml["stac_discovery"]["properties"]["eo:bands"],
        default_chunks=kwargs.get("default_chunks", DEFAULT_CHUNKS),
    )
    xdt.name = safe_path.stem
    xdt.attrs.update(attrs_from_xml)

    # Geometry Data (Solar and Viewing ANgles)
    granule_metadata = read_product_granule_metadata((safe_path))
    xdt[str(S02MSITileZarrPathRenderer().geometry)] = DataTree(
        granule_metadata[
            ["sun_angles", "viewing_incidence_angles", "mean_sun_angles", "mean_viewing_incidence_angles"]
        ],
    )

    # Meteorology Data
    aux_ecmwft = load_meteo_data(safe_path, "AUX_ECMWFT")
    try:
        aux_camsfo = load_meteo_data(safe_path, "AUX_CAMSFO")
    except ValueError:
        # Fallback mechanism: if no CAMSFO found, use CAMSRE
        aux_camsfo = load_meteo_data(safe_path, "AUX_CAMSRE")

    if do_merge_meteo_data:
        xdt[str(S02MSITileZarrPathRenderer().meteorology)] = DataTree(xr.merge([aux_ecmwft, aux_camsfo]))
    else:
        # European Centre for Medium-Range Weather Forecasts (ECMWF)
        xdt[str(S02MSITileZarrPathRenderer().meteo_ecmwf)] = DataTree(aux_ecmwft)
        # Copernicus Atmosphere Monitoring Service (CAMS)
        xdt[str(S02MSITileZarrPathRenderer().meteo_cams)] = DataTree(aux_camsfo)

    # Datastrip Metadata (optional)
    if with_datastrip_metadata:
        # /!/ Slow
        datastrip_metadata = read_product_datastrip_metadata(Path(safe_path))
        xdt["conditions/metadata/datastrip"] = DataTree(xr.Dataset(datastrip_metadata))

    # Post-raster data additions
    # Sample product level proj stac extension data from a band
    # Note: extensions are in properties
    b05_20m_path = str(S02MSITileZarrPathRenderer(resolution=20).reflectance / "b05")
    xdt.attrs["stac_discovery"]["properties"]["proj:epsg"] = xdt[b05_20m_path].attrs["proj:epsg"]
    xdt.attrs["stac_discovery"]["properties"]["proj:bbox"] = xdt[b05_20m_path].attrs["proj:bbox"]

    return xdt


def guess_product_level(safe_path: Path) -> Literal["L1C", "L2A"]:
    """
    Guess the product level from a SAFE path.

    Returns
    -------
        The product level

    Raises
    ------
    ValueError
        If the product level could not be guessed
    """
    if "MSIL1C" in safe_path.stem:
        product_level = "L1C"
    elif "MSIL2A" in safe_path.stem:
        product_level = "L2A"
    else:
        raise ValueError(
            "Cannot guess product level from SAFE path (neither L1C nor L2A). "
            "Try to provide an argument for the 'product_level parameter",
        )

    return product_level


def read_product_granule_metadata(safe_path: Path, *, band_dim_name: str = "band") -> xr.Dataset:
    """
    Extract metadata from MTD_TL.xml.

    The resulting dataset have the following shape:
    - A variable named `sun_angles` with 3 dimensions: (angle, y, x)
    - A variable named `viewing_incidence_angles` with 5 dimensions: (band, detector, angle, y, x)

    Example
    -------
    .. code-block::

        <xarray.Dataset>
        Dimensions:                   (angle: 2, y: 23, x: 23, band: 13, detector: 7)
        Coordinates:
        * angle                     (angle) <U7 'zenith' 'azimuth'
        * y                         (y) int32 1300000 1305000 ... 1405000 1410000
        * x                         (x) int32 399960 404960 409960 ... 504960 509960
        * band                      (band) int32 0 1 2 3 4 5 6 7 8 9 10 11 12
        * detector                  (detector) int32 2 3 4 5 6 7 8
        Data variables:
            sun_angles                (angle, y, x) float64 80.86 80.82 ... 77.51 77.27
            viewing_incidence_angles  (band, detector, angle, y, x) float64 9.597 ......

    Args:
        safe_path (Path): Path to the Sentinel-2 SAFE archive

    Returns:
       ``xr.Dataset``
    """
    # See https://sentinel.esa.int/documents/247904/685211/sentinel-2-products-specification-document
    soup = load_granule_metadata(safe_path)

    if soup is None:
        raise ValueError

    angles_xds = extract_angles(soup, band_dim_name)
    enriched_metadata_xds = enrich_metadata(soup)

    # Replace band integer ids by band str names
    granule_metadata_xds = xr.merge([angles_xds, enriched_metadata_xds], combine_attrs="no_conflicts").assign_coords(
        {"band": list(BAND_NAMES)},
    )

    return granule_metadata_xds


def load_meteo_data(safe_path: Path, filename: str) -> xr.Dataset:
    """
    Load meteorology information present in a SAFE archive.

    Parameters
    ----------
    safe_path
        Path to S2 MSI L1C SAFE archive
    filename
        Filename to load (AUX_CAMSFO or AUX_ECMWFT)

    Returns
    -------
        Dataset of meteorological data.
    """
    # Assumes that the glob will return only one subfolder
    glob = f"GRANULE/*/AUX_DATA/{filename}"
    path = glob_unique_result(safe_path, glob)
    xds = xr.load_dataset(path, engine="cfgrib", backend_kwargs=dict(indexpath="", errors="ignore"))

    # Cleanup created idx (should not be needed if the ifx file is not persisted in the first place.)
    glob_idx = f"GRANULE/*/AUX_DATA/{filename}*.idx"
    paths_idx = list(safe_path.glob(glob_idx))
    for path_idx in paths_idx:
        path_idx.unlink()

    return xds


def convert_xml_metadata(safe_path: Path, *, product_level: Literal["L1C", "L2A"]) -> dict[str, Any]:
    """
    Convert XML Metadata

    Parameters
    ----------
    safe_path
        Path to a S2MSI SAFE folder, L1C or L2a
    product_level
        Product level: L1C and L2A are supported, if None, guess from the SAFE path.

    Returns
    -------
        A nested dictionary of metadata, that can be added to a DataTree's attributes.

    Raises
    ------
    ValueError
        If the requested product level is not L1C nor L2A.
    """
    if product_level == "L1C":
        product_metadata_xml_path = safe_path / "MTD_MSIL1C.xml"
    elif product_level == "L2A":
        product_metadata_xml_path = safe_path / "MTD_MSIL2A.xml"
    else:
        raise ValueError("Incorrect product level")

    granule_metadata_xml_path = sorted(safe_path.glob("GRANULE/*/MTD_TL.xml"))[0]
    datastrip_metadata_xml_path = sorted(safe_path.glob("DATASTRIP/*/MTD_DS.xml"))[0]
    manifest_safe_xml_path = safe_path / "manifest.safe"

    roots = [
        (etree.parse(product_metadata_xml_path), "product_namespaces"),
        (etree.parse(granule_metadata_xml_path), "tile_namespaces"),
        (etree.parse(datastrip_metadata_xml_path), "datastrip_namespaces"),
        (etree.parse(manifest_safe_xml_path), "manifest_namespaces"),
    ]
    xml_accessor = AccessorXML(roots=roots, namespaces=get_xml_namespaces(product_level=product_level, roots=roots))

    # <Handle locally generated L2A>
    # Many metadata missing for L2A generated locally
    # See 'T2A' vs 'UP2A' -> first is used but only second is convertable UP user product)
    partial_l2a_flag: bool = False
    try:
        xml_accessor.findone("n1:Quality_Indicators_Info/Snow_Coverage_Assessment")
    except TypeError:
        partial_l2a_flag = True
    try:
        xml_accessor.findone("n1:Quality_Indicators_Info/Image_Content_QI/CLOUDY_PIXEL_OVER_LAND_PERCENTAGE")
    except TypeError:
        partial_l2a_flag = True
    # </Handle locally generated L2A>

    stac_discovery = render_stac_discovery(xml_accessor, product_level=product_level, partial_l2a_flag=partial_l2a_flag)
    other_metadata = render_other_metadata(xml_accessor, product_level=product_level, partial_l2a_flag=partial_l2a_flag)
    attrs = {
        "stac_discovery": stac_discovery,
        "other_metadata": other_metadata,
    }
    return attrs


def get_xml_namespaces(*, product_level: str, roots: Any) -> dict[str, dict[str, str]]:
    """
    Get XML namespaces

    Parameters
    ----------
    product_level
        Product level: L1C and L2A are supported, if None, guess from the SAFE path, by default "L1C"

    Returns
    -------
        Dictionary of XML namespaces.

    Raises
    ------
    ValueError
        If the requested product level is not L1C nor L2A.
    """
    version = 14
    if product_level == "L1C":
        level_name = "1C"
    elif product_level == "L2A":
        level_name = "2A"
    else:
        raise ValueError

    schemas = {}
    schema_root = f"https://psd-{version}.sentinel2.eo.esa.int/PSD"
    default_schemas = {
        "product_namespaces": f"{schema_root}/User_Product_Level-{level_name}.xsd",
        "tile_namespaces": f"{schema_root}/S2_PDI_Level-{level_name}_Tile_Metadata.xsd",
        "datastrip_namespaces": f"{schema_root}/S2_PDI_Level-{level_name}_Datastrip_Metadata.xsd",
    }
    for xml, name in roots:
        locations = xml.getroot().attrib.get("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation")
        if locations:
            locations_lst = locations.split()
            for location in locations_lst:
                if location.startswith("https://"):
                    schemas[name] = location
        elif name in default_schemas:
            schemas[name] = default_schemas[name]
        else:
            schemas[name] = None

    namespaces = {
        "product_namespaces": {
            "xfdu": "urn:ccsds:schema:xfdu:1",
            "gml": "http://www.opengis.net/gml",
            "safe": "http://www.esa.int/safe/sentinel/1.1",
            "sentinel-safe": "http://www.esa.int/safe/sentinel/1.1",
            "n1": schemas["product_namespaces"],
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        },
        "tile_namespaces": {
            "n1": schemas["tile_namespaces"],
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        },
        "datastrip_namespaces": {
            "xfdu": "urn:ccsds:schema:xfdu:1",
            "gml": "http://www.opengis.net/gml",
            "safe": "http://www.esa.int/safe/sentinel/1.1",
            "sentinel-safe": "http://www.esa.int/safe/sentinel/1.1",
            "n1": schemas["datastrip_namespaces"],
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        },
        "manifest_namespaces": {
            "safe": "http://www.esa.int/safe/sentinel/1.1",
            "gml": "http://www.opengis.net/gml",
        },
    }
    return namespaces


def read_product_raster_data(
    safe_path: Path,
    *,
    product_level: str,
    eo_band_metadata: dict[str, str | float],
    perform_bitpacking: bool = True,
    default_chunks=True,
) -> DataTree:
    """
    Read Product Raster Data

    .. note::

        The Band 10 is not excluded from L2A product if found.
        If the band is here, convert it. If it is not, then it is excluded by construction.
        The conversion tool only consumes data and tries to make as little decisions as possible.

    Parameters
    ----------
    safe_path
        Path to a S2MSI SAFE folder, L1C or L2A
    product_level
        Product level: L1C and L2A are supported, if None, guess from the SAFE path, by default "L1C"
    eo_band_metadata
        EO Band Metadata. Used to enrich reflectances attributes (their long names)
    perform_bitpacking, optional
        Perform Bitpacking of QI_DATA MSK_QUALIT and QI_DATA MSK_CLASSI masks, by default True
        The multi-band 2-D boolean masks will be compressed into single-band 1-D byte masks.

    Returns
    -------
        A DataTree containing the product's raster data information

    Raises
    ------
    NotImplementedError
        If a band name is not supported, when iterating over the found ``.jp2`` files.
    """
    root_xdt = DataTree()

    band_name_to_wavelength = {v["name"]: v["center_wavelength"] for v in eo_band_metadata}

    # IMG_DATA
    empty_resolutions = {f"r{k}m": DataTree() for k in list(BandNameToResolutionMapping.values())}
    xdt = DataTree.from_dict(empty_resolutions)
    if product_level == "L1C":
        # Image Data
        for band_file_path in sorted(safe_path.glob("GRANULE/*/IMG_DATA/*.jp2")):
            band_name = extract_band_name_from_band_file_path(band_file_path)
            if band_name in BAND_NAMES:
                raster = open_raster(band_file_path, remove_encoding=False, default_chunks=default_chunks)
                raster = raster.isel(band=0, drop=True)
                long_name = (
                    "TOA reflectance from MSI acquisition at spectral band "
                    f"{band_name} {band_name_to_wavelength[band_name]} nm"
                )
                raster.attrs.update(create_attrs_dict_for_reflectance(long_name))
                xdt[f"r{get_band_name_to_resolution_mapping(band_name)}m"][band_name] = raster
            elif band_name == "tci":
                long_name = "TCI: True Color Image"
                raster = open_raster(
                    band_file_path,
                    remove_encoding=True,
                    band_name=band_name,
                    default_chunks=default_chunks,
                ).astype(np.uint8)
                raster.attrs.update(dict(long_name=long_name))
                root_xdt[
                    str(S02MSITileZarrPathRenderer(resolution=get_band_name_to_resolution_mapping(band_name)).tci_l1c)
                ] = raster
            else:
                message = f"Band name not supported ({band_name}) ({product_level=})"
                print(message)
                raise NotImplementedError(message)

        root_xdt[str(S02MSITileZarrPathRenderer().reflectance)] = xdt  # For L1C
    elif product_level == "L2A":
        # Image Data
        for band_file_path in sorted(safe_path.glob("GRANULE/*/IMG_DATA/*/*.jp2")):
            parts = band_file_path.stem.split("_")
            resolution = int(parts[-1][:-1])
            band_name = extract_band_name_from_band_file_path(band_file_path)

            if band_name in BAND_NAMES:
                print("Do band", band_name, resolution, "(reflectance)")
                raster = open_raster(
                    band_file_path,
                    remove_encoding=False,
                    band_name=band_name,
                    resolution=resolution,
                    default_chunks=default_chunks,
                )
                raster = raster.isel(band=0, drop=True)
                long_name = (
                    "BOA reflectance from MSI acquisition at spectral band "
                    f"{band_name} {band_name_to_wavelength[band_name]} nm"
                )
                raster.attrs.update(create_attrs_dict_for_reflectance(long_name))
                xdt[f"r{resolution}m"][band_name] = raster
            else:
                print("Do band", band_name, resolution, "(other)")
                pr = S02MSITileZarrPathRenderer(resolution=resolution)
                if band_name == "aot":
                    raster = open_raster(
                        band_file_path,
                        remove_encoding=True,
                        band_name=band_name,
                        resolution=resolution,
                        default_chunks=default_chunks,
                    ).isel(band=0, drop=True)
                    root_xdt[str(pr.atmosphere / band_name)] = raster
                elif band_name == "wvp":
                    raster = open_raster(
                        band_file_path,
                        remove_encoding=True,
                        band_name=band_name,
                        resolution=resolution,
                        default_chunks=default_chunks,
                    ).isel(band=0, drop=True)
                    root_xdt[str(pr.atmosphere / band_name)] = raster
                elif band_name == "scl":
                    raster = open_raster(
                        band_file_path,
                        remove_encoding=True,
                        band_name=band_name,
                        resolution=resolution,
                        default_chunks=default_chunks,
                    ).isel(band=0, drop=True)
                    root_xdt[str(pr.l2a_classification / band_name)] = raster
                elif band_name == "tci":
                    raster = open_raster(
                        band_file_path,
                        remove_encoding=True,
                        band_name=band_name,
                        resolution=resolution,
                        default_chunks=default_chunks,
                    ).astype(np.uint8)
                    root_xdt[str(pr.tci_l2a)] = raster
                elif band_name == "vim":
                    long_name = "VIM: Visibility array computed from CAMS auxiliary data."
                    raster = open_raster(
                        band_file_path,
                        remove_encoding=True,
                        band_name=band_name,
                        resolution=resolution,
                        default_chunks=default_chunks,
                    ).isel(band=0, drop=True)
                    raster.attrs.update(dict(long_name=long_name))
                    root_xdt[str(pr.vim)] = raster
                elif band_name in ("lcm", "wbi", "snc"):
                    code_to_long_name = {
                        "lcm": "LCM: ESA CCI Map: Land Cover Classification",
                        "wbi": "WBI: ESA CCI Map: Water Bodies",
                        "snc": "SNC: ESA CCI Map: Snow Climatology",
                    }
                    code_to_path = {
                        "lcm": str(pr.lcm),
                        "wbi": str(pr.wbi),
                        "snc": str(pr.snc),
                    }
                    long_name = code_to_long_name[band_name]
                    raster = (
                        open_raster(
                            band_file_path,
                            remove_encoding=True,
                            band_name=band_name,
                            resolution=resolution,
                            default_chunks=default_chunks,
                        )
                        .isel(band=0, drop=True)
                        .astype(np.uint8)
                    )
                    raster.attrs.update(dict(long_name=long_name))
                    root_xdt[code_to_path[band_name]] = raster
                else:
                    message = f"Band name not supported ({band_name}) ({product_level=})"
                    print(message)
                    raise NotImplementedError(message)

        root_xdt["measurements/reflectance"] = xdt  # For L2A

    # QI_DATA/MSK_CLASSI
    xdt = DataTree.from_dict({"r60m": DataTree()})
    for band_file_path in sorted(safe_path.glob("GRANULE/*/QI_DATA/MSK_CLASSI*")):
        band_name = extract_band_name_from_band_file_path(band_file_path)
        raster = open_raster(band_file_path, remove_encoding=True, default_chunks=default_chunks)

        available_masks: tuple[str, ...] = ("OPAQUE", "CIRRUS", "SNOW_ICE")

        # raster = raster.assign_coords({"mask_sub_type": xr.DataArray(list(available_masks), dims="band")})

        if perform_bitpacking:
            # Assuming the bands 1 2 3 ... 8 are represented when bit packed as 1 2 4 ... 128
            raster_bitpacked = bitpack_raster_with_bands(raster)
            raster_bitpacked.attrs.update(raster.attrs)  # Preserve original attributes like proj:transform
            xdt["r60m"][band_name] = raster_bitpacked
        else:
            xdt["r60m"][band_name] = raster

        xdt["r60m"][band_name].attrs.update(
            {
                "long_name": "cloud classification mask provided in the final reference frame (ground geometry)",
                "dtype": "<u1",
                "flag_meanings": list(available_masks),
                "flag_masks": [1, 2, 4, 8, 16, 32, 64, 128][: len(list(available_masks))],
            },
        )

    # Contains the L1C Mask S2 classification mask ; both in L1C and L2A product
    root_xdt["conditions/mask/l1c_classification"] = xdt
    xdt = DataTree.from_dict(empty_resolutions)
    for band_file_path in sorted(safe_path.glob("GRANULE/*/QI_DATA/MSK_QUALIT*")):
        band_name = extract_band_name_from_band_file_path(band_file_path)
        raster = open_raster(band_file_path, remove_encoding=True, default_chunks=default_chunks)

        available_masks: tuple[str, ...] = (
            "ANC_LOST",
            "ANC_DEG",
            "MSI_LOST",
            "MSI_DEG",
            "QT_DEFECTIVE_PIXELS",
            "QT_NODATA_PIXELS",
            "QT_PARTIALLY_CORRECTED_PIXELS",
            "QT_SATURATED_PIXELS_L1A",
        )

        # raster = raster.assign_coords({"mask_sub_type": xr.DataArray(list(available_masks), dims="band")})

        resolution_group = f"r{BandNameToResolutionMapping[band_name]}m"

        if perform_bitpacking:
            # Assuming the bands 1 2 3 ... 8 are represented when bit packed as 1 2 4 ... 128
            raster_bitpacked = bitpack_raster_with_bands(raster)
            raster_bitpacked.attrs.update(raster.attrs)  # Preserve original attributes like proj:transform
            xdt[resolution_group][band_name] = raster_bitpacked
        else:
            xdt[resolution_group][band_name] = raster

        xdt[resolution_group][band_name].attrs.update(
            {
                "long_name": "quality mask provided in the final reference frame (ground geometry)",
                "dtype": "<u1",
                "flag_meanings": list(available_masks),
                "flag_masks": [1, 2, 4, 8, 16, 32, 64, 128][: len(list(available_masks))],
            },
        )

    root_xdt["quality/mask"] = xdt

    # QI_DATA/MSK_DETFOO
    xdt = DataTree.from_dict(empty_resolutions)
    for band_file_path in sorted(safe_path.glob("GRANULE/*/QI_DATA/MSK_DETFOO*")):
        band_name = extract_band_name_from_band_file_path(band_file_path)
        raster = open_raster(band_file_path, remove_encoding=True, default_chunks=default_chunks)
        raster = raster.isel(band=0, drop=True)

        raster.attrs.update(
            {
                "long_name": (
                    "detector footprint mask provided in the final reference frame (ground geometry). "
                    "0 = no detector, 1-12 = detector 1-12"
                ),
                "dtype": "<u1",
            },
        )

        xdt[f"r{BandNameToResolutionMapping[band_name]}m"][band_name] = raster

    root_xdt[str(S02MSITileZarrPathRenderer().detector_footprint)] = xdt

    if product_level == "L2A":
        # Keep the 20m resolution
        resolution = L2A_NATIVE_RESOLUTION

        msk_cldprb_band_path = sorted(safe_path.glob(f"GRANULE/*/QI_DATA/MSK_CLDPRB*{resolution}*"))[0]
        band_name = "cld"
        raster = open_raster(
            msk_cldprb_band_path,
            remove_encoding=True,
            band_name=band_name,
            default_chunks=default_chunks,
        ).isel(band=0)
        root_xdt[f"/quality/probability/r{resolution}m/{band_name}"] = raster

        msk_snwprb_band_path = sorted(safe_path.glob(f"GRANULE/*/QI_DATA/MSK_SNWPRB*{resolution}*"))[0]
        band_name = "snw"
        raster = open_raster(
            msk_snwprb_band_path,
            remove_encoding=True,
            band_name=band_name,
            default_chunks=default_chunks,
        ).isel(band=0)
        root_xdt[f"/quality/probability/r{resolution}m/{band_name}"] = raster

    return root_xdt


def create_attrs_dict_for_reflectance(long_name: str) -> dict[str, Any]:
    """
    Create the attributes dictionary for reflectance bands.

    It defines important encoding information such as the fill value, scale factor and add offset.

    Used by :py:func:`read_product_raster_data`

    Parameters
    ----------
    long_name
        Long name of the reflectance band

    Returns
    -------
        Attributes dictionary to be attached to the band.
    """

    # In a MTD_MSIL2A.xml file: BOA (bottom of atmosphre)
    #   <QUANTIFICATION_VALUES_LIST>
    #     <BOA_QUANTIFICATION_VALUE unit="none">10000</BOA_QUANTIFICATION_VALUE>
    #     <AOT_QUANTIFICATION_VALUE unit="none">1000.0</AOT_QUANTIFICATION_VALUE>
    #     <WVP_QUANTIFICATION_VALUE unit="cm">1000.0</WVP_QUANTIFICATION_VALUE>
    #   </QUANTIFICATION_VALUES_LIST>
    #   <BOA_ADD_OFFSET_VALUES_LIST>
    #     <BOA_ADD_OFFSET band_id="0">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="1">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="2">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="3">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="4">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="5">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="6">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="7">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="8">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="9">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="10">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="11">-1000</BOA_ADD_OFFSET>
    #     <BOA_ADD_OFFSET band_id="12">-1000</BOA_ADD_OFFSET>
    #   </BOA_ADD_OFFSET_VALUES_LIST>
    return {
        "long_name": long_name,
        "dtype": "<u2",
        "units": "digital_counts",
        "fill_value": 0,
        "_FillValue": 0,
        "scale_factor": 0.0001,
        "add_offset": -0.1,  # -1000/10000 = -0.1
        "valid_min": 1,
        "valid_max": 65535,
    }


def open_raster(
    band_file_path: Path,
    *,
    remove_encoding: bool = False,
    convert_spatial_ref_to_stac_proj: bool = True,
    band_name: str | None = None,
    resolution: ResolutionType | None = None,
    default_chunks: Any = True,
) -> xr.DataArray:
    """
    Open Raster

    Parameters
    ----------
    band_file_path
        Band File Path
    remove_encoding, optional
        Whether to remove the encoding, by default False
    convert_spatial_ref_to_stac_proj, optional
        Convert the ``spatial_ref`` attributes automatically set by :py:mod:`rasterio`
        to STAC attributes and set them on the band's DataArray's attributes, by default True
    band_name, optional
        Band Name, by default None
        When None, the band name is extracted from the band file path.
        When explicitly set, the provided value is used as a band name.
    resolution, optional
        Resolution, by default None
        When None, the resolution is guessed according to the band name.
        When explicitly set, the provided value is used.

    Returns
    -------
        An :py:class:`xr.DataArray` representation of a Sentinel-2 SAFE band.

    Raises
    ------
    TypeError
        _description_
    """
    band_name = band_name or extract_band_name_from_band_file_path(band_file_path)
    if resolution is None:
        if band_name == "b00":
            resolution = 60  # cloud mask
        elif band_name in ("aot", "wvp", "scl", "cld", "snw"):
            resolution = L2A_NATIVE_RESOLUTION
        else:
            # print(f"{band_name=} <- {band_file_path=}")
            resolution = get_band_name_to_resolution_mapping(band_name)
    # Note: chunking significantly slows down datatree writing
    raster = rioxarray.open_rasterio(band_file_path, chunks=default_chunks)
    raster = raster.chunk(get_chunk_size(resolution))

    if not isinstance(raster, xr.DataArray):
        raise TypeError

    # Ensure coordinates are integer.
    raster["x"] = raster["x"].astype(int)
    raster["y"] = raster["y"].astype(int)

    if remove_encoding:
        # If these attributes coming from rioxarray are kept, dtype will become float when reopening the persisted zarr.
        # Use remove_encoding when loading integer rasters to avoid unwanted float conversion when persisted.
        del raster.attrs["scale_factor"]
        del raster.attrs["add_offset"]

    if convert_spatial_ref_to_stac_proj:
        # See https://github.com/stac-extensions/projection/blob/v1.0.0/README.md
        # this will be set on whole Product level, as the UTM tile is the dominant data-format
        # metadata can use lat and lon, but the reflectances in themselves are a UTM tile.
        # see example https://github.com/stac-extensions/projection/blob/v1.0.0/examples/item.json

        # to_epsg removes the EPSG:prefix, redundant with proj:epsg.
        raster.attrs["proj:epsg"] = int((raster.rio.crs).to_epsg())  # Eg 'EPSG:32632' -> 32632

        xmin, ymin, xmax, ymax = raster.rio.bounds()  # (399960.0, 4990200.0, 509760.0, 5100000.0)
        raster.attrs["proj:bbox"] = [xmin, ymin, xmax, ymax]
        # Is resolution specific. Do not set on product level.
        # Example: From raster.spatial_ref.GeoTransform == '399960.0 60.0 0.0 5100000.0 0.0 -60.0'
        # to [399960.0, 60.0, 0.0, 5100000.0, 0.0, -60.0, 0, 0, 1]
        raster.attrs["proj:transform"] = list(
            raster.rio.transform(),
        )

        # Is resolution specific. Do not set on product level.
        raster.attrs["proj:shape"] = [raster["y"].size, raster["x"].size]

        # Is resolution specific. Do not set on product level.
        # /!/ is the crs_wkt from raster rio the wkt2 format?
        raster.attrs["proj:wkt2"] = raster.spatial_ref.attrs["crs_wkt"]

        # Finally, remove the spatial_ref from the final product now that relevant information
        # has been passed tothe proj: attributes.
        del raster["spatial_ref"]
    return raster


def read_product_metadata(safe_path: Path, *, band_dim_name: str = "band") -> S2L1CProductMetadata:
    """
    Read Product Metadata

    .. note

        This function is unused in the conversion process as it contains not enough metadata.

    Parameters
    ----------
    safe_path
        SAFE path
    band_dim_name, optional
        Band dimension-name, by default "band".
        rioxarray uses "band" by default when loading multi-band rasters.

    Returns
    -------
        S2 L1C Product Metadata.
    """
    # See ADF_BLINDP to remove the use of beautiful soup and use lxml instead.
    with open(safe_path / "MTD_MSIL1C.xml", encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, "xml")

    datatake_type = soup.DATATAKE_TYPE.string

    quantification_value = int(
        soup.Product_Image_Characteristics.QUANTIFICATION_VALUE.string,
    )

    radio_add_offsets = {
        el.attrs["band_id"]: int(el.string) for el in soup.Product_Image_Characteristics.find_all("RADIO_ADD_OFFSET")
    }
    granule = soup.Product_Organisation.Granule_List.Granule
    image_file_list = [c.string for c in granule.findChildren("IMAGE_FILE", recursive=False)]
    # Last 3 characters of the IMAGE_FILE field corresponds to the 3-letter band name
    raster_paths = {el[-3:]: el for el in image_file_list}

    band_info_dict = {
        el.attrs["bandId"]: {
            "resolution": int(el.RESOLUTION.string),
            "wavelength_min": dict(value=int(el.MIN.string), units=el.MIN.attrs["unit"]),
            "wavelength_max": dict(value=int(el.MAX.string), units=el.MAX.attrs["unit"]),
            "wavelength_central": dict(value=float(el.CENTRAL.string), units=el.CENTRAL.attrs["unit"]),
            "spectral_response_step": dict(value=int(el.STEP.string), units=el.STEP.attrs["unit"]),
            "spectral_response_values": (el.VALUES.string),
            "physical_band": el.attrs["physicalBand"],
            "band_id": el.attrs["bandId"],
        }
        for el in soup.find_all("Spectral_Information")
    }

    physical_gain_dict = {
        el.attrs["bandId"]: float(el.string) for el in soup.Product_Image_Characteristics.find_all("PHYSICAL_GAINS")
    }

    for band_id, band_info in band_info_dict.items():
        band_name = normalize_band_name(band_info["physical_band"])
        band_info["band_name"] = band_name
        band_info["image_file"] = raster_paths[band_name]
        band_info["radio_add_offset"] = radio_add_offsets[band_id]
        band_info["physical_gain"] = physical_gain_dict[band_id]

    bands = {band_info["band_name"]: band_info for band_info in band_info_dict.values()}
    product_uri = soup.Product_Info.PRODUCT_URI.string

    product_uri = S2MSIL1CProductURI.from_string(soup.Product_Info.PRODUCT_URI.string)

    sensing_start_time = str(soup.PRODUCT_START_TIME.string)
    sensing_stop_time = str(soup.PRODUCT_STOP_TIME.string)
    orbit_direction = str(soup.SENSING_ORBIT_DIRECTION.string)
    orbit_number = str(soup.SENSING_ORBIT_NUMBER.string)
    generation_time = str(soup.GENERATION_TIME.string)
    processing_baseline = str(soup.PROCESSING_BASELINE.string)
    candidates_gipp_filename_abca = soup.GIPP_List.findAll(
        lambda tag: tag.name == "GIPP_FILENAME" and "type" in tag.attrs and tag["type"] == "GIP_R2ABCA",
    )

    gipp_filename_abca = None
    gipp_filename_abca_version = None

    if len(candidates_gipp_filename_abca) == 1:
        gipp = candidates_gipp_filename_abca[0]
        gipp_filename_abca = gipp.string
        if "version" in gipp.attrs:
            gipp_filename_abca_version = gipp.attrs["version"]

    gri_filename_list = [str(el.string) for el in soup.GRI_List.findAll("GRI_FILENAME")]

    dictionary = dict(
        quantification_value=quantification_value,
        sensing_start_time=sensing_start_time,
        sensing_stop_time=sensing_stop_time,
        orbit_direction=orbit_direction,
        orbit_number=orbit_number,
        generation_time=generation_time,
        processing_baseline=processing_baseline,
        gipp_filename_abca=gipp_filename_abca,
        gipp_filename_abca_version=gipp_filename_abca_version,
        gri_filename_list=gri_filename_list,
        product_uri=str(product_uri),
        datatake_type=datatake_type,
        bands=bands,
    )
    return dictionary


def extract_radio_add_offset_from_metadata(
    metadata: S2L1CProductMetadata,
    band_name_set: list[str],
    band_dim_name: str = "band",
) -> xr.DataArray:
    """
    Extract the radiometric add offset from metadata

    .. note

        This function is unused in the conversion process as it contains not enough metadata.

    Parameters
    ----------
    metadata
        S2 L1C Product Metadata
    band_name_set
        Set of band names
    band_dim_name, optional
        Band dimension-name, by default "band".
        rioxarray uses "band" by default when loading multi-band rasters.

    Returns
    -------
        DataArray reprensenting the radiometric add offset.
    """
    # Regarding the radio_add_offset, use an xarray with correct bands for broadcast

    radio_add_offset_dict = {
        band_name: band.radio_add_offset for band_name, band in metadata.bands.items() if band_name in band_name_set
    }

    radio_add_offset = xr.DataArray(
        list(radio_add_offset_dict.values()),
        coords={band_dim_name: list(radio_add_offset_dict.keys())},
        dims=band_dim_name,
        name="radio_add_offset (Radiometric Offset)",
    )

    return radio_add_offset


def extract_official_calibration_coefficients_from_metadata(
    metadata: S2L1CProductMetadata,
    band_name_set: list[str],
    band_dim_name: str = "band",
):
    """
    Extract official calibration coefficients from S2 L1C Product Metadata

    .. note

        This function is unused in the conversion process as it contains not enough metadata.

    Parameters
    ----------
    metadata
        S2 L1C Product Metadata
    band_name_set
        Set of band names
    band_dim_name, optional
        Band dimension-name, by default "band".
        rioxarray uses "band" by default when loading multi-band rasters.

    Returns
    -------
        DataArray reprensenting the official calibration coefficients.
    """
    a_off_k_dict = {
        band_name: band.physical_gain for band_name, band in metadata.bands.items() if band_name in band_name_set
    }
    a_off_k = xr.DataArray(
        list(a_off_k_dict.values()),
        coords={band_dim_name: list(a_off_k_dict.keys())},
        dims=band_dim_name,
        name="a_off_k (Official Calibration Coefficients)",
    )

    return a_off_k


def load_datastrip_metadata(safe_path: Path) -> BeautifulSoup:
    """
    Load Datastrip Metadata

    .. warning

        The Datastrip metadata is large and not included in the default conversion process.

    Parameters
    ----------
    safe_path
        SAFE Path

    Returns
    -------
        BeautifulSoup object that represents the datastrip XML metadata.
    """
    glob = "DATASTRIP/*/MTD_DS.xml"
    path = glob_unique_result(safe_path, glob)
    with open(path, encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, "xml")

    return soup


def read_product_datastrip_metadata(safe_path: Path) -> dict:
    """
    Read Product Datastrip Metadata

    .. warning

        The Datastrip metadata is large and not included in the default conversion process.

    Parameters
    ----------
    safe_path
        SAFE Path

    Returns
    -------
        Dictionary
    """
    # XXX Extremely slow because the file is 130k-line long. Might consider using regexpes...
    soup = load_datastrip_metadata(safe_path)

    if soup.Image_Refining is None:
        gri_refined_product = None
    else:
        gri_refined_product = soup.Image_Refining.attrs["flag"]

    ecmwf_data_ref = soup.ECMWF_DATA_REF.string
    cams_data_ref = soup.CAMS_DATA_REF.string

    datastrip_sensing_start = soup.DATASTRIP_SENSING_START.string
    datastrip_sensing_stop = soup.DATASTRIP_SENSING_STOP.string

    return dict(
        gri_refined_product=gri_refined_product,
        ecmwf_data_ref=ecmwf_data_ref,
        cams_data_ref=cams_data_ref,
        datastrip_sensing_start=datastrip_sensing_start,
        datastrip_sensing_stop=datastrip_sensing_stop,
    )


def load_granule_metadata(safe_path: Path) -> BeautifulSoup:
    """
    Load Granule Metadata

    Parameters
    ----------
    safe_path
        SAFE Path

    Returns
    -------
        BeautifulSoup object that represents the granule XML metadata.

    """
    glob = "GRANULE/*/MTD_TL.xml"
    path = glob_unique_result(safe_path, glob)

    with open(path, encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, "xml")

    return soup


def analyze_tie_points_grid_from_xml(grid) -> Any:
    """
    Analyze Tie-Points (angles) Grid from XML.

    Parameters
    ----------
    grid
        Grid (BeautifulSoup object representing the XML)

    Returns
    -------
        A dictionary of col_step, row_step and values to construct the Tie-Points grid.
    """
    col_step = {"attrs": grid.COL_STEP.attrs, "value": int(grid.COL_STEP.string)}
    row_step = {"attrs": grid.ROW_STEP.attrs, "value": int(grid.ROW_STEP.string)}
    values_rows = grid.Values_List.findChildren("VALUES", recursive=False)
    values = [[float(value) for value in row.string.split(" ")] for row in values_rows]
    return {"col_step": col_step, "row_step": row_step, "values": values}


def xarrayize_xml_table(grid, grid_info: GridInfo, crs: str, angle_type: str) -> xr.DataArray:
    """
    Convert a XML Table to an xarray DataArray

    .. note::

        The resulting y and x coordinates follow a Pixel-is-Area convention.
        **It means that all coordinates are offsetted by half a sign-step from the ULX, ULY.**
        See https://www.usgs.gov/media/images/differences-between-pixel-area-and-pixel-point-designations

        rioxarray does the same when opening a raster.
        See https://corteva.github.io/rioxarray/html/rioxarray.html#rioxarray-open-rasterio

        The angle grid is 23x23 with a 5km step, 110km-wide for a tile.

    Parameters
    ----------
    grid
        Grid (BeautifulSoup object representing the XML)
    grid_info
        Grid Info (dataclass with upper-left corener and step sign information)
    crs
        Coordinate Reference System
    angle_type
        Angle Type: Zenith or Azimuth

    Returns
    -------
        xarray DataArray representing the angles.
    """
    values = grid["values"]
    col_step = grid["col_step"]["value"]
    row_step = grid["row_step"]["value"]
    # See https://sentinels.copernicus.eu/ca/web/sentinel/user-guides/sentinel-2-msi/product-types/level-1c
    # > In Level-1C products, pixel coordinates refer to the upper left corner of the pixel.
    # So start with a step //2 offset to align rio.bounds() UL to MTD UL.
    # XXX Dubious step alignment. Best covering seems to be obtained when NO OFFSET is added.
    # No offset = The first point of the tie point grid coincides with the UL corner in mtd.
    signed_row_step_y = grid_info.sign_step_y * row_step
    signed_col_step_x = grid_info.sign_step_x * col_step
    pre_step_coef = 0  # or 1 (lag) (or -1 (lead))
    coords_y = grid_info.uly + (signed_row_step_y // 2 * pre_step_coef + np.arange(len(values)) * signed_row_step_y)
    coords_x = grid_info.ulx + (signed_col_step_x // 2 * pre_step_coef + np.arange(len(values[0])) * signed_col_step_x)
    xda = xr.DataArray(
        [values],
        dims=("angle", "y", "x"),
        coords={"angle": [angle_type], "y": coords_y, "x": coords_x},
    )
    xda.rio.set_crs(crs, inplace=True)
    return xda


def fill_grid_dict(
    soup: BeautifulSoup,
    grid_dict: dict,
    grid_info: GridInfo,
    crs: str,
) -> xr.DataArray:
    """
    Fill the Grid Dictionary

    Parameters
    ----------
    soup
        BeautifulSoup object representing XML
    grid_dict
        Grid Dictionary (**updated in-place**)
    grid_info
        Grid Info (dataclass with upper-left corener and step sign information)
    crs
        Coordinate Reference System

    Returns
    -------
        xarray DataArray containing the Zenith and Azimuth angles
    """
    angle_xdas = []

    grid = soup.Zenith
    analyzed_grid = analyze_tie_points_grid_from_xml(grid)
    angle_type = "zenith"
    angle_xdas.append(xarrayize_xml_table(analyzed_grid, grid_info, crs, angle_type))
    grid_dict[angle_type] = analyzed_grid

    grid = soup.Azimuth
    analyzed_grid = analyze_tie_points_grid_from_xml(grid)
    angle_type = "azimuth"
    angle_xdas.append(xarrayize_xml_table(analyzed_grid, grid_info, crs, angle_type))
    grid_dict[angle_type] = analyzed_grid

    return xr.concat(angle_xdas, dim="angle")


def validate_granule_metadata(grids):
    """
    Validate Granule Metadata.

    Verify that all angles grid coincide.

    Parameters
    ----------
    grids
        Dictionary of angle grids

    Returns
    -------
        boolean: True if PASSED, False if FAILED.
    """
    return all(
        grids["sun_angles_grid"][angle_type][step] == grid_info[angle_type][step]
        for angle_type in ("zenith", "azimuth")
        for step in ("col_step", "row_step")
        for grid_info in grids["viewing_incidence_angles_grids"]
    )


def extract_angles(soup: BeautifulSoup, band_dim_name: str) -> xr.Dataset:
    """Extract Angles

    Parameters
    ----------
    soup
        BeautifulSoup object representing XML
    band_dim_name, optional
        Band dimension-name, by default "band".
        rioxarray uses "band" by default when loading multi-band rasters.
    Returns
    -------
        xarray Dataset containing all the sun/view zenith/azimuth angles.

    Raises
    ------
    ValueError
        If the granule metadata validation failed.
    """
    input_crs = soup.HORIZONTAL_CS_CODE.string

    ulx = int(soup.ULX.string)
    uly = int(soup.ULY.string)
    sign_step_x = np.sign(int(soup.XDIM.string))
    sign_step_y = np.sign(int(soup.YDIM.string))
    grid_info = GridInfo(
        ulx=ulx,
        uly=uly,
        sign_step_x=sign_step_x,
        sign_step_y=sign_step_y,
    )

    # Sun Angles Grid
    grids = {}
    grids["sun_angles_grid"] = {}
    xda_sag = fill_grid_dict(
        soup.Tile_Angles.Sun_Angles_Grid,
        grids["sun_angles_grid"],
        grid_info,
        input_crs,
    )

    # Viewing Incidence Angles Grids
    grids["viewing_incidence_angles_grids"] = []
    via_grids = soup.Tile_Angles.findChildren(
        "Viewing_Incidence_Angles_Grids",
        recursive=False,
    )
    for via_grid in via_grids:
        grid_dict = {**via_grid.attrs}
        grids["viewing_incidence_angles_grids"].append(grid_dict)
        xda = fill_grid_dict(via_grid, grid_dict, grid_info, input_crs)

        # Note: detector ID is in [[1, 12]], similarly to MSK_DETFOO.
        detector_id = int(grid_dict["detectorId"])
        band_id = int(grid_dict["bandId"])

        xda = xda.expand_dims(dim={"detector": [detector_id]})
        xda = xda.expand_dims(dim={band_dim_name: [band_id]})
        grid_dict["dataarray"] = xda

    if not validate_granule_metadata(grids):
        raise ValueError("validate_granule_metadata failed. Please investigate the provided MTD_TL.xml")

    via_xdas = list(grid["dataarray"] for grid in grids["viewing_incidence_angles_grids"])
    xda_viag = xr.combine_by_coords(via_xdas)

    xdas = {
        "sun_angles": xda_sag,
        "viewing_incidence_angles": xda_viag,
    }

    xds = xr.Dataset(xdas)

    return xds


def enrich_metadata(soup: BeautifulSoup) -> xr.Dataset:
    """
    Enrich Metadata

    Parameters
    ----------
    soup
        BeautifulSoup object representing XML

    Returns
    -------
        xarray Dataset representing the enriched metadata.
    """

    size_xds = xr.concat(
        [
            xr.Dataset({"nrows": int(size.NROWS.string), "NCOLS".lower(): int(size.NCOLS.string)}).expand_dims(
                {"resolution": [int(size.attrs["resolution"])]},
            )
            for size in soup.findChildren("Size")
        ],
        dim="resolution",
    )

    geoposition_xds = xr.concat(
        [
            xr.Dataset(
                {k.lower(): int(geoposition.find(k).string) for k in ["ULX", "ULY", "XDIM", "YDIM"]},
            ).expand_dims({"resolution": [int(geoposition.attrs["resolution"])]})
            for geoposition in soup.findChildren("Geoposition")
        ],
        dim="resolution",
    )

    resolution_xds = xr.merge([size_xds, geoposition_xds])

    angles_names = ["ZENITH_ANGLE", "AZIMUTH_ANGLE"]

    # Mean Incidence Angles
    mean_inc_ang_xds = xr.concat(
        [
            xr.Dataset({k.lower(): float(el.find(k).string) for k in angles_names}).expand_dims(
                {"band": [int(el.attrs["bandId"])]},
            )
            for el in soup.findChildren("Mean_Viewing_Incidence_Angle")
        ],
        dim="band",
    )
    mean_inc_ang_xda = mean_inc_ang_xds.to_array(dim="angle").assign_coords(dict(angle=["zenith", "azimuth"]))
    # Same for zenith and azimuth, one dict with unit: deg
    mean_inc_ang_xda.attrs.update(soup.Mean_Viewing_Incidence_Angle.AZIMUTH_ANGLE.attrs)

    # Mean Sun Angles
    mean_sun_ang_xds = xr.Dataset({k.lower(): float(soup.Mean_Sun_Angle.find(k).string) for k in angles_names})
    mean_sun_ang_xda = mean_sun_ang_xds.to_array(dim="angle").assign_coords(dict(angle=["zenith", "azimuth"]))
    # Same for zenith and azimuth, one dict with unit: deg
    mean_sun_ang_xda.attrs.update(soup.Mean_Sun_Angle.AZIMUTH_ANGLE.attrs)

    xds = resolution_xds
    xds["mean_sun_angles"] = mean_sun_ang_xda
    xds["mean_viewing_incidence_angles"] = mean_inc_ang_xda.T  # (band, angle) order

    xds["resolution"].attrs["unit"] = "m"

    xds.update(
        {
            "tile_geocoding/" + el.name.lower(): el.string
            for el in soup.Tile_Geocoding.findChildren(recursive=False)
            if not el.findChildren()
        },
    )
    xds.update(
        {
            "image_content_qi/" + el.name.lower(): el.string
            for el in soup.Image_Content_QI.findChildren()
            if not el.findChildren()
        },
    )
    xds.update(
        {
            "general_info/" + el.name.lower(): el.string
            for el in soup.General_Info.findChildren()
            if not el.findChildren()
        },
    )

    return xds


def render_stac_discovery(accessor_xml: AccessorXML, *, product_level: str, partial_l2a_flag: bool) -> Any:
    """
    Render STAC discovery attributes

    Parameters
    ----------
    accessor_xml
        XML Accessor
    product_level
        Product Level (L1C or L2A)
    partial_l2a_flag
        Partial L2A flag: handle L2A downloaded from the web VS generated by sen2cor locally.
        Impacts some xpaths.

    Returns
    -------
        Dictionary of STAC discovery attributes.

    Raises
    ------
    NotImplementedError
        If product level is not one of L1C or L2A
    """
    findone = accessor_xml.findone
    findoneattr = accessor_xml.findoneattr

    if product_level == "L1C":
        snow_cover_tagname = "SNOW_PIXEL_PERCENTAGE"
        provider_name = "L1C Processor"
        eopf_type = "S02MSIL1C"
        processing_lineage = "IPF L1C processor"
        processing_level = "L1C"
        geometry_path = (
            "metadataSection/metadataObject[@ID='measurementFrameSet']/metadataWrap/"
            "xmlData/safe:frameSet/safe:footPrint/gml:coordinates"
        )
    elif product_level == "L2A":
        snow_cover_tagname = "SNOW_ICE_PERCENTAGE"
        provider_name = "L2A Processor"
        eopf_type = "S02MSIL2A"
        processing_lineage = "IPF L2A processor"
        processing_level = "L2A"
        geometry_path = (
            "metadataSection/metadataObject[@ID='measurementFrameSet']/metadataWrap/"
            "xmlData/safe:frameSet/safe:footPrint/gml:coordinates"
        )

    else:
        raise NotImplementedError

    if partial_l2a_flag:  # For L2A downloaded from the web\
        try:
            eo_snow_cover = float(findone(f"n1:Quality_Indicators_Info/Image_Content_QI/{snow_cover_tagname}"))
        except TypeError:
            eo_snow_cover = float(findone("n1:Quality_Indicators_Info/Image_Content_QI/SNOW_PIXEL_PERCENTAGE"))

    else:  # For L2A generated locally by sen2cor
        eo_snow_cover = float(findone("n1:Quality_Indicators_Info/Snow_Coverage_Assessment"))

    # See https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md
    dictionary = {
        "type": "Feature",
        "stac_version": "1.0.0",
        "stac_extensions": [
            "https://stac-extensions.github.io/eopf/v1.0.0/schema.json",
            "https://stac-extensions.github.io/eo/v1.1.0/schema.json",
            "https://stac-extensions.github.io/sat/v1.0.0/schema.json",
            "https://stac-extensions.github.io/view/v1.0.0/schema.json",
            "https://stac-extensions.github.io/scientific/v1.0.0/schema.json",
            "https://stac-extensions.github.io/processing/v1.1.0/schema.json",
        ],
        "id": findone("n1:General_Info/Product_Info/PRODUCT_URI"),
        # In manifest.safe
        "geometry": to_geojson(
            findone(geometry_path),
        ),
        "bbox": to_bbox(
            findone(
                "metadataSection/metadataObject[@ID='measurementFrameSet']/"
                "metadataWrap/xmlData/safe:frameSet/safe:footPrint/gml:coordinates",
            ),
        ),
        "properties": {
            # REQUIRED
            # See https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md#datetime
            # Use any acquisition date useful for searching
            "datetime": findone("n1:General_Info/Product_Info/PRODUCT_START_TIME"),
            "start_datetime": findone("n1:General_Info/Product_Info/PRODUCT_START_TIME"),
            "end_datetime": findone("n1:General_Info/Product_Info/PRODUCT_STOP_TIME"),
            "created": findone("n1:General_Info/Product_Info/GENERATION_TIME"),
            "platform": findone("n1:General_Info/Product_Info/Datatake/SPACECRAFT_NAME"),  # .lower(),
            "instrument": "msi",
            "mission": "Sentinel-2",
            "providers": [
                {"name": provider_name, "roles": ["processor"]},
                {"name": "ESA", "roles": ["producer"]},
            ],
            # Stac Extension: sat
            "sat:absolute_orbit": int(
                findone(
                    "metadataSection/metadataObject[@ID='measurementOrbitReference']/"
                    "metadataWrap/xmlData/safe:orbitReference/safe:orbitNumber",
                ),
            ),
            "sat:relative_orbit": int(findone("n1:General_Info/Product_Info/Datatake/SENSING_ORBIT_NUMBER")),
            "sat:orbit_state": findoneattr(
                "metadataSection/metadataObject[@ID='measurementOrbitReference']/"
                "metadataWrap/xmlData/safe:orbitReference/safe:orbitNumber/@groundTrackDirection",
            ),
            "sat:platform_international_designator": "2015-028A",
            # Stac Extension: sci
            "sci:doi": findone("n1:General_Info/Product_Info/PRODUCT_DOI"),
            # Stac Extension: processing
            "processing:lineage": processing_lineage,
            "processing:facility": "ESA",
            "processing:software": "Sentinel-2 IPF",
            "processing:level": processing_level,
            # Stac Extension: view
            # Commented out as angles are unclear in the SAFE Metadata.
            # "view:sun_elevation": 90 - float(findone("n1:Geometric_Info/Tile_Angles/Mean_Sun_Angle/ZENITH_ANGLE")),
            # "view:sun_azimuth": float(findone("n1:Geometric_Info/Tile_Angles/Mean_Sun_Angle/AZIMUTH_ANGLE")),
            # Stac Extension: eo
            # Same value as the following in MTD_TL.xml
            "eo:cloud_cover": float(findone("n1:Quality_Indicators_Info/Image_Content_QI/CLOUDY_PIXEL_PERCENTAGE")),
            # "eo:cloud_cover": float(findone("n1:Quality_Indicators_Info/Cloud_Coverage_Assessment")),
            # Same value as the following in MTD_TL.xml
            "eo:snow_cover": eo_snow_cover,
            "eo:bands": [
                {
                    "name": "b01",
                    "common_name": "coastal",
                    # Unit described in XML: unit="nm". XXX Must be in um according to STAC spec.
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='0']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.020,
                    # Unit in XML is the same as unit in STAC spec
                    # See Band Object https://github.com/stac-extensions/eo?tab=readme-ov-file#band-object
                    # Unit described in XML: unit="W/m²/µm" ; matches STAC spec: "W/m2/micrometers"
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='0']",
                        ),
                    ),
                },
                {
                    "name": "b02",
                    "common_name": "blue",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='1']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.065,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='1']",
                        ),
                    ),
                },
                {
                    "name": "b03",
                    "common_name": "green",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='2']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.035,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='2']",
                        ),
                    ),
                },
                {
                    "name": "b04",
                    "common_name": "red",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='3']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.030,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='3']",
                        ),
                    ),
                },
                {
                    "name": "b05",
                    "common_name": "rededge",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='4']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.015,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='4']",
                        ),
                    ),
                },
                {
                    "name": "b06",
                    "common_name": "rededge",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='5']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.015,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='5']",
                        ),
                    ),
                },
                {
                    "name": "b07",
                    "common_name": "rededge",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='6']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.020,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='6']",
                        ),
                    ),
                },
                {
                    "name": "b08",
                    "common_name": "nir",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='7']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.105,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='7']",
                        ),
                    ),
                },
                {
                    "name": "b8a",
                    "common_name": "nir08",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='8']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.020,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='8']",
                        ),
                    ),
                },
                {
                    "name": "b09",
                    "common_name": "nir09",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='9']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.020,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='9']",
                        ),
                    ),
                },
                {
                    "name": "b10",
                    "common_name": "cirrus",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='10']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.030,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='10']",
                        ),
                    ),
                },
                {
                    "name": "b11",
                    "common_name": "swir16",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='11']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.090,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='11']",
                        ),
                    ),
                },
                {
                    "name": "b12",
                    "common_name": "swir22",
                    "center_wavelength": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Spectral_Information_List/Spectral_Information[@bandId='12']/Wavelength/CENTRAL",
                        ),
                    ),
                    "full_width_half_max": 0.180,
                    "solar_illumination": float(
                        findone(
                            "n1:General_Info/Product_Image_Characteristics/"
                            "Reflectance_Conversion/Solar_Irradiance_List/SOLAR_IRRADIANCE[@bandId='12']",
                        ),
                    ),
                },
            ],
            # Stac Extension: eopf
            "eopf:resolutions": {
                "bands 02, 03, 04, 08": findone(
                    "n1:General_Info/Product_Image_Characteristics/"
                    "Spectral_Information_List/Spectral_Information[@bandId='1']/RESOLUTION",
                ),
                "bands 05, 06, 07, 8A, 11, 12": findone(
                    "n1:General_Info/Product_Image_Characteristics/"
                    "Spectral_Information_List/Spectral_Information[@bandId='4']/RESOLUTION",
                ),
                "bands 01, 09, 10": findone(
                    "n1:General_Info/Product_Image_Characteristics/"
                    "Spectral_Information_List/Spectral_Information[@bandId='0']/RESOLUTION",
                ),
            },
            "eopf:timeline": "NRT",
            "eopf:instrument_mode": findone("n1:General_Info/Product_Info/Datatake/DATATAKE_TYPE"),
            # Same value as the following in MTD_DS.xml
            # "eopf:baseline": findone("n1:General_Info/Processing_Info/PROCESSING_BASELINE"),
            "eopf:baseline": findone("n1:General_Info/Product_Info/PROCESSING_BASELINE"),
            "eopf:type": eopf_type,
            "eopf:data_take_id": findoneattr("n1:General_Info/Product_Info/Datatake/@datatakeIdentifier"),
        },
        "links": [],
        "assets": {},
    }

    if product_level == "L1C":
        dictionary["properties"].update(
            {
                "eopf:image_size": [
                    {
                        "name": band_names,
                        "start_offset": float(
                            findone(f"n1:Geometric_Info/Tile_Geocoding/Geoposition[@resolution='{resolution}']/ULY"),
                        ),
                        "track_offset": float(
                            findone(f"n1:Geometric_Info/Tile_Geocoding/Geoposition[@resolution='{resolution}']/ULX"),
                        ),
                        "rows": int(
                            findone(f"n1:Geometric_Info/Tile_Geocoding/Size[@resolution='{resolution}']/NROWS"),
                        ),
                        "columns": int(
                            findone(f"n1:Geometric_Info/Tile_Geocoding/Size[@resolution='{resolution}']/NCOLS"),
                        ),
                    }
                    for band_names, resolution in {
                        "bands 02, 03, 04, 08": 10,
                        "bands 05, 06, 07, 8A, 11, 12": 20,
                        "bands 01, 09, 10": 60,
                    }.items()
                ],
            },
        )
    elif product_level == "L2A" and (not partial_l2a_flag):
        dictionary["properties"].update(
            {
                "eopf:pixel_classification": [
                    {
                        "name": "cloud over all",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/CLOUDY_PIXEL_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "cloud over land",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/CLOUDY_PIXEL_OVER_LAND_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "degraded instrument data",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/DEGRADED_MSI_DATA_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "no-data pixel",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/NODATA_PIXEL_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "saturated or defective pixel",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/SATURATED_DEFECTIVE_PIXEL_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "dark feature or shadow",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/DARK_FEATURES_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "cloud shadow",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/CLOUD_SHADOW_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "vegetation",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/VEGETATION_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "no vegetation",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/NOT_VEGETATED_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "water",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/WATER_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "unclassified pixel",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/UNCLASSIFIED_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "cloud medium probability",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/MEDIUM_PROBA_CLOUDS_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "cloud high probability",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/HIGH_PROBA_CLOUDS_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "thin cirrus",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/THIN_CIRRUS_PERCENTAGE"),
                        ),
                    },
                    {
                        "name": "snow or ice",
                        "percent": float(
                            findone("n1:Quality_Indicators_Info/Image_Content_QI/SNOW_ICE_PERCENTAGE"),
                        ),
                    },
                ],
            },
        )

    return dictionary


def render_other_metadata(accessor_xml: AccessorXML, *, product_level: str, partial_l2a_flag: bool) -> Any:
    """
    Render Other Metadata attributes

    Parameters
    ----------
    accessor_xml
        XML Accessor
    product_level
        Product Level (L1C or L2A)
    partial_l2a_flag
        Partial L2A flag: handle L2A downloaded from the web VS generated by sen2cor locally.
        Impacts some xpaths.

    Returns
    -------
        Dictionary of Other Metadata attributes.
    """
    findone = accessor_xml.findone
    findoptional = accessor_xml.findoptional
    findalltext = accessor_xml.findalltext

    band_widths = [20.0, 65.0, 35.0, 30.0, 15.0, 13.0, 19.0, 105.0, 20.0, 20.0, 30.0, 90.0, 180.0]
    # See https://github.com/radiantearth/stac-spec/blob/v1.0.0/item-spec/item-spec.md
    dictionary = {
        "UTM_zone_identification": findone("n1:General_Info/TILE_ID"),
        "mean_sensing_time": findone("n1:General_Info/SENSING_TIME"),
        "horizontal_CRS_name": findone("n1:Geometric_Info/Tile_Geocoding/HORIZONTAL_CS_NAME"),
        "horizontal_CRS_code": findone("n1:Geometric_Info/Tile_Geocoding/HORIZONTAL_CS_CODE"),
        "mean_sun_azimuth_angle_in_deg_for_all_bands_all_detectors": float(
            findone("n1:Geometric_Info/Tile_Angles/Mean_Sun_Angle/AZIMUTH_ANGLE"),
        ),
        "mean_sun_zenith_angle_in_deg_for_all_bands_all_detectors": float(
            findone("n1:Geometric_Info/Tile_Angles/Mean_Sun_Angle/ZENITH_ANGLE"),
        ),
        "L0_ephemeris_data_quality": findoptional(
            "n1:Quality_Indicators_Info/Geometric_Info/Geometric_QI/EPHEMERIS_QUALITY",
        ),
        "L0_ancillary_data_quality": findoptional(
            "n1:Quality_Indicators_Info/Geometric_Info/Geometric_QI/ANCILLARY_QUALITY",
        ),
        "absolute_location_assessment_from_AOCS": findoptional(
            "n1:Quality_Indicators_Info/Geometric_Info/Geometric_QI/Absolute_Location",
        ),
        "planimetric_stability_assessment_from_AOCS": findoptional(
            "n1:Quality_Indicators_Info/Geometric_Info/Geometric_QI/Planimetric_Stability",
        ),
        "multispectral_registration_assessment": findoptional(
            "n1:Quality_Indicators_Info/Geometric_Info/Geometric_QI/Multi_Spectral_Registration",
        ),
        (
            "reflectance_correction_factor_from_" "the_Sun-Earth_distance_variation_computed_using_the_acquisition_date"
        ): float(
            findone("n1:General_Info/Product_Image_Characteristics/" "Reflectance_Conversion/U"),
        ),
        "percentage_of_degraded_MSI_data": float(
            findone("n1:Quality_Indicators_Info/Technical_Quality_Assessment/DEGRADED_MSI_DATA_PERCENTAGE"),
        ),
        "spectral_band_of_reference": findoptional(
            "to_int(n1:General_Info/Product_Image_Characteristics/REFERENCE_BAND)",
        ),
        "band_description": {
            band_name: {
                "units": "nm",
                "central_wavelength": float(
                    findone(
                        "n1:General_Info/Product_Image_Characteristics/"
                        "Spectral_Information_List/"
                        f"Spectral_Information[@bandId='{band_id}']/Wavelength/CENTRAL",
                    ),
                ),
                "wavelength_min": float(
                    findone(
                        "n1:General_Info/Product_Image_Characteristics/"
                        "Spectral_Information_List/"
                        f"Spectral_Information[@bandId='{band_id}']/Wavelength/MIN",
                    ),
                ),
                "wavelength_max": float(
                    findone(
                        "n1:General_Info/Product_Image_Characteristics/"
                        "Spectral_Information_List/"
                        f"Spectral_Information[@bandId='{band_id}']/Wavelength/MAX",
                    ),
                ),
                "bandwidth": band_widths[band_id],
                "spectral_response_step": findone(
                    f"n1:General_Info/Product_Image_Characteristics/"
                    "Spectral_Information_List/"
                    f"Spectral_Information[@bandId='{band_id}']/Spectral_Response/STEP",
                ),
                "spectral_response_values": findone(
                    f"n1:General_Info/Product_Image_Characteristics/"
                    "Spectral_Information_List/"
                    f"Spectral_Information[@bandId='{band_id}']/Spectral_Response/VALUES",
                ),
                "physical_gain": findone(
                    f"n1:General_Info/Product_Image_Characteristics/PHYSICAL_GAINS[@bandId='{band_id}']",
                ),
                "onboard_compression_rate": findone(
                    f"n1:Image_Data_Info/Sensor_Configuration/Acquisition_Configuration/"
                    f"Spectral_Band_Info/Spectral_Band_Information[@bandId='{band_id}']/COMPRESSION_RATE",
                ),
                "onboard_integration_time": findone(
                    f"n1:Image_Data_Info/Sensor_Configuration/Acquisition_Configuration/"
                    f"Spectral_Band_Info/Spectral_Band_Information[@bandId='{band_id}']/INTEGRATION_TIME",
                ),
            }
            for band_id, band_name in enumerate(BAND_NAMES)
        },
        "meteo": {"source": "ECMWF", "type": "FORECAST"},
        "product_quality_status": findone(
            "n1:Quality_Indicators_Info/Quality_Control_Checks/Quality_Inspections/quality_check['GENERAL_QUALITY']",
        ),
        "NUC_table_ID": int(findone("n1:Image_Data_Info/Sensor_Configuration/Acquisition_Configuration/NUC_TABLE_ID")),
        "onboard_compression_flag": findone(
            "n1:Image_Data_Info/Sensor_Configuration/Acquisition_Configuration/COMPRESS_MODE",
        ),
        "onboard_equalization_flag": findoptional(
            "n1:Image_Data_Info/Sensor_Configuration/Acquisition_Configuration/EQUALIZATION_MODE",
        ),
        "SWIR_rearrangement_flag": findoptional("n1:Image_Data_Info/Radiometric_Info/SWIR_REARRANGEMENT_PROC"),
        "optical_crosstalk_correction_flag": findoptional("n1:Image_Data_Info/Radiometric_Info/CROSSTALK_OPTICAL_PROC"),
        "electronic_crosstalk_correction_flag": findoptional(
            "n1:Image_Data_Info/Radiometric_Info/CROSSTALK_ELECTRONIC_PROC",
        ),
        "geometric_refinement": {
            "spacecraft_rotation": {
                "X": {
                    "degree": findoptional(
                        "n1:Image_Data_Info/Geometric_Info/Refined_Corrections_List/"
                        "Refined_Corrections/MSI_State/Rotation/X/DEGREE",
                    ),
                    "coefficients": findoptional(
                        "n1:Image_Data_Info/Geometric_Info/Refined_Corrections_List/"
                        "Refined_Corrections/MSI_State/Rotation/X/COEFFICIENTS",
                    ),
                },
                "Y": {
                    "degree": findoptional(
                        "n1:Image_Data_Info/Geometric_Info/Refined_Corrections_List/"
                        "Refined_Corrections/MSI_State/Rotation/Y/DEGREE",
                    ),
                    "coefficients": findoptional(
                        "n1:Image_Data_Info/Geometric_Info/Refined_Corrections_List/"
                        "Refined_Corrections/MSI_State/Rotation/Y/COEFFICIENTS",
                    ),
                },
                "Z": {
                    "degree": findoptional(
                        "n1:Image_Data_Info/Geometric_Info/Refined_Corrections_List/"
                        "Refined_Corrections/MSI_State/Rotation/Z/DEGREE",
                    ),
                    "coefficients": findoptional(
                        "n1:Image_Data_Info/Geometric_Info/Refined_Corrections_List/"
                        "Refined_Corrections/MSI_State/Rotation/Z/COEFFICIENTS",
                    ),
                },
            },
            "mean_value_of_residual_displacements_at_all_tie_points_after_refinement_m": {
                "x_mean": findoptional(
                    "n1:Quality_Indicators_Info/Geometric_Info/Geometric_Refining_Quality/"
                    "Image_Refining/Correlation_Quality/Local_Residual_List/Local_Residual/X_MEAN",
                ),
                "y_mean": findoptional(
                    "n1:Quality_Indicators_Info/Geometric_Info/Geometric_Refining_Quality/"
                    "Image_Refining/Correlation_Quality/Local_Residual_List/Local_Residual/Y_MEAN",
                ),
            },
            "standard_deviation_of_residual_displacements_at_all_tie_points_after_refinement_m": {
                "x_stdv": findoptional(
                    "n1:Quality_Indicators_Info/Geometric_Info/Geometric_Refining_Quality/"
                    "Image_Refining/Correlation_Quality/Local_Residual_List/Local_Residual/X_STDV",
                ),
                "y_stdv": findoptional(
                    "n1:Quality_Indicators_Info/Geometric_Info/Geometric_Refining_Quality/"
                    "Image_Refining/Correlation_Quality/Local_Residual_List/Local_Residual/Y_STDV",
                ),
            },
        },
        "history": [
            {"type": "Raw Data", "output": "Downlinked Stream"},
            {
                "type": "Level-0 Product",
                "processor": "L0",
                "version": "???",
                "organisation": "ESA",
                "inputs": "Downlinked Stream",
                "output": "S2MSIL0__etc",
            },
            {
                "type": "Level-1A Product",
                "processor": "Sentinel-2 IPF",
                "version": "???",
                "organisation": "ESA",
                "inputs": {
                    "used DEM file name": findone("n1:Auxiliary_Data_Info/PRODUCTION_DEM_TYPE"),
                    "used GRI file list": to_list_str(findalltext("n1:Auxiliary_Data_Info/GRI_List")),
                    "used IERS file name": findone("n1:Auxiliary_Data_Info/IERS_BULLETIN_FILENAME"),
                    "used ECMWF file names": findone("n1:Auxiliary_Data_Info/ECMWF_DATA_REF"),
                    "used CAMS file names": findone("n1:Auxiliary_Data_Info/CAMS_DATA_REF"),
                    "list of used processing parameters file names": to_list_str(
                        findalltext("n1:Auxiliary_Data_Info/GIPP_List/GIPP_FILENAME"),
                    ),
                    "Level-0 Product": "S2MSIL0__etc",
                },
                "output": "S2MSIL1A_etc",
            },
            {
                "type": "Level-1B Product",
                "processor": "Sentinel-2 IPF",
                "version": "???",
                "organisation": "ESA",
                "inputs": {
                    "used DEM file name": findone("n1:Auxiliary_Data_Info/PRODUCTION_DEM_TYPE"),
                    "used GRI file list": to_list_str(findalltext("n1:Auxiliary_Data_Info/GRI_List")),
                    "used IERS file name": findone("n1:Auxiliary_Data_Info/IERS_BULLETIN_FILENAME"),
                    "used ECMWF file names": findone("n1:Auxiliary_Data_Info/ECMWF_DATA_REF"),
                    "used CAMS file names": findone("n1:Auxiliary_Data_Info/CAMS_DATA_REF"),
                    "list of used processing parameters file names": to_list_str(
                        findalltext("n1:Auxiliary_Data_Info/GIPP_List/GIPP_FILENAME"),
                    ),
                    "Level-1A Product": "S2MSIL1A_etc",
                },
                "output": "S2MSIL1B_etc",
            },
            {
                "type": "Level-1C Product",
                "processor": "Sentinel-2 IPF",
                "version": "???",
                "organisation": "ESA",
                "inputs": {
                    "used DEM file name": findone("n1:Auxiliary_Data_Info/PRODUCTION_DEM_TYPE"),
                    "used GRI file list": to_list_str(findalltext("n1:Auxiliary_Data_Info/GRI_List")),
                    "used IERS file name": findone("n1:Auxiliary_Data_Info/IERS_BULLETIN_FILENAME"),
                    "used ECMWF file names": findone("n1:Auxiliary_Data_Info/ECMWF_DATA_REF"),
                    "used CAMS file names": findone("n1:Auxiliary_Data_Info/CAMS_DATA_REF"),
                    "list of used processing parameters file names": to_list_str(
                        findalltext("n1:Auxiliary_Data_Info/GIPP_List/GIPP_FILENAME"),
                    ),
                    "Level-1B Product": "S2MSIL1B_etc",
                },
                "output": "S2MSIL1C_etc",
            },
        ],
    }

    if product_level == "L2A" and (not partial_l2a_flag):
        dictionary.update(
            {
                "declared_accuracy_of_radiative_transfer_model": float(
                    findone("n1:Quality_Indicators_Info/Image_Content_QI/RADIATIVE_TRANSFER_ACCURACY"),
                ),
                "declared_accuracy_of_water_vapour_model": float(
                    findone("n1:Quality_Indicators_Info/Image_Content_QI/WATER_VAPOUR_RETRIEVAL_ACCURACY"),
                ),
                "declared_accuracy_of_AOT_model": float(
                    findone("n1:Quality_Indicators_Info/Image_Content_QI/AOT_RETRIEVAL_ACCURACY"),
                ),
                "AOT_retrieval_model": findone("n1:Quality_Indicators_Info/Image_Content_QI/AOT_RETRIEVAL_METHOD"),
                "mean_value_of_aerosol_optical_thickness": float(
                    findone("n1:Quality_Indicators_Info/Image_Content_QI/GRANULE_MEAN_AOT"),
                ),
                "mean_value_of_total_water_vapour_content": float(
                    findone("n1:Quality_Indicators_Info/Image_Content_QI/GRANULE_MEAN_WV"),
                ),
                "ozone_source": findone("n1:Quality_Indicators_Info/Image_Content_QI/OZONE_SOURCE"),
                "ozone_value": float(findone("n1:Quality_Indicators_Info/Image_Content_QI/OZONE_VALUE")),
                (
                    "reflectance_correction_factor_from_the_Sun-Earth"
                    "_distance_variation_computed_using_the_acquisition_date"
                ): float(
                    findone("n1:General_Info/Product_Image_Characteristics/Reflectance_Conversion/U"),
                ),
            },
        )
        dictionary["history"].append(
            {
                "type": "Level-2A Product",
                "processor": "Sentinel-2 IPF",
                "version": "???",
                "organisation": "ESA",
                "inputs": {
                    "used DEM file name": findone("n1:Auxiliary_Data_Info/PRODUCTION_DEM_TYPE"),
                    "used GRI file name": findone("n1:Auxiliary_Data_Info/GRI_List/GRI_FILENAME"),
                    "used IERS file name": findone("n1:Auxiliary_Data_Info/IERS_BULLETIN_FILENAME"),
                    "used ECMWF file names": findone("n1:Auxiliary_Data_Info/ECMWF_DATA_REF"),
                    "used CAMS file names": findone("n1:Auxiliary_Data_Info/CAMS_DATA_REF"),
                    "list of used processing parameters file names": findone(
                        "n1:Auxiliary_Data_Info/GIPP_List/GIPP_FILENAME",
                    ),
                    "used snow climatology map file name": findone("n1:Auxiliary_Data_Info/SNOW_CLIMATOLOGY_MAP"),
                    "used ESA CCI water bodies map file name": findone("n1:Auxiliary_Data_Info/ESACCI_WaterBodies_Map"),
                    "used ESA CCI land cover map file name": findone("n1:Auxiliary_Data_Info/ESACCI_LandCover_Map"),
                    "used ESA CCI snow condition map folder name": findone(
                        "n1:Auxiliary_Data_Info/ESACCI_SnowCondition_Map_Dir",
                    ),
                    "used LibRadTran Look-Up Tables list": findone("n1:Auxiliary_Data_Info/LUT_List/LUT_FILENAME"),
                    "Level-1C Product": "S2MSIL1C_etc",
                },
                "output": "S2MSIL2A_etc",
            },
        )
    return dictionary


def extract_band_name_from_band_file_path(band_file_path: Path) -> str:
    """
    Extract Band Name from Band File Path

    Parameters
    ----------
    band_file_path
        Band File Path

    Returns
    -------
        Band Name

    Raises
    ------
    NotImplementedError
        If product level is of a length different than 3 (L1C) or 4 (L2A).
    """
    stem = band_file_path.stem
    if len(stem.split("_")) == 3:  # L1C format
        return stem[-3:].lower()
    if len(stem.split("_")) == 4:  # L2A format
        return stem[:-4][-3:].lower()
    raise NotImplementedError


def normalize_band_name(physical_band: str) -> str:
    """
    Normalize Band Name

    Parameters
    ----------
    physical_band
        2- or 3-character physical_band

    Returns
    -------
        Normalized Band Name
    """
    if len(physical_band) == 2:
        return physical_band[0] + "0" + physical_band[1]
    return physical_band


def get_chunk_size(resolution: ResolutionType) -> tuple[int, int, int]:
    """
    Get default square chunk size for Tile Zarr Products for given resolution

    Parameters
    ----------
    resolution
        Resolution

    Returns
    -------
        Chunk size for resolution
    """
    mapping: dict[ResolutionType, int] = {
        10: 1830,
        20: 915,
        60: 305,
    }
    return (1, mapping[resolution], mapping[resolution])


def glob_unique_result(search_dir: Path, glob_pattern: str) -> Path:
    """
    Find a unique result for the given glob pattern in the given search directory.

    Parameters
    ----------
    search_dir
        Base directory to glob in
    glob_pattern
        Glob pattern

    Returns
    -------
        Path if found else raise exception

    Raises
    ------
    ValueError
        If no unique result was found
    """
    paths = list(search_dir.glob(glob_pattern))
    if len(paths) != 1:
        raise ValueError(
            f"A unique path should have been found for {glob_pattern=}",
        )
    path = paths[0]
    return path


def get_band_name_to_resolution_mapping(band_name: str) -> dict[str, ResolutionType]:
    """
    For a given band name, return the corresponding resolution.

    The only reason for the existence of this utility function is because of the existence
    of the TCI (True Color Image) band, that is a RGB composite outside of the traditional
    reflectance bands.

    Parameters
    ----------
    band_name
        Band Name

    Returns
    -------
        Resolution
    """
    if band_name.lower() == "tci":
        return 10
    return BandNameToResolutionMapping[band_name]


def convert_safe_to_zarr(
    *,
    product_level: str,
    mode: str,
    input_safe_path: Path | None,
    output_zarr_path: Path | None,
) -> None:
    """
    Convert SAFE products to datatree without mappings.

    Parameters
    ----------
    product_level
        Product Level
    mode
        Mode of execution of the tool
    input_safe_path
        Input SAFE directory path
    output_zarr_path
        Output ZARR directory path

    Raises
    ------
    ValueError
        Input SAFE path is None
    FileNotFoundError
        Input SAFE path is not a directory
    ValueError
        Output ZARR path is None
    FileNotFoundError
        Output ZARR path is not a directory
    NotImplementedError
        Incorrect mode of execution
    """

    if input_safe_path is None:
        raise TypeError("No input SAFE path was given.")

    if not input_safe_path.is_dir():
        raise FileNotFoundError

    tile = S02MSITileProduct.from_safe_path(input_safe_path)

    if mode == "print":
        print(
            tile.text(
                with_full_path=True,
                with_group_variables=True,
            ),
        )
    elif mode == "persist_to_zarr":
        if output_zarr_path is None:
            raise TypeError("No output Zarr path was given.")

        print(f"Persist to specified output path {output_zarr_path=}")
        tile.xdt.to_zarr(output_zarr_path)  # 20s without chunking, 60s with

        print("Re-open zarr with datatree")
        zarr_xdt = xr.open_datatree(output_zarr_path, engine="zarr")

        print("Output product structure:")
        print(repr_datatree_text(zarr_xdt))
    else:
        raise NotImplementedError


DEFAULT_LEVEL = "L1C"
DEFAULT_MODE = "print"


@click.command()
@click.option(
    "--product_level",
    "-l",
    type=click.Choice(["L1C", "L2A"]),
    required=True,
    default=DEFAULT_LEVEL,
    help="Product level of the product to convert.",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["print", "persist_to_zarr"]),
    required=True,
    default=DEFAULT_MODE,
    help="What to do with the product once opened with datatree.",
)
@click.option(
    "--input_safe_path",
    "-i",
    type=click.Path(path_type=Path),
    required=False,
    default=None,
    help="Path to the Sentinel-2 Product's SAFE input directory",
)
@click.option(
    "--output_zarr_path",
    "-o",
    type=click.Path(path_type=Path),
    required=False,
    default=None,
    help="Path to the Sentinel-2 Product's Zarr output directory",
)
def convert_safe_to_zarr_entrypoint(
    product_level: str,
    mode: str,
    input_safe_path: Path | None,
    output_zarr_path: Path | None,
) -> None:
    """
    Convert SAFE products to datatree without mappings.
    """

    convert_safe_to_zarr(
        product_level=product_level,
        mode=mode,
        input_safe_path=input_safe_path,
        output_zarr_path=output_zarr_path,
    )


if __name__ == "__main__":
    convert_safe_to_zarr_entrypoint()  # pylint: disable=no-value-for-parameter
