import csv
import gc
import json
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path, PurePosixPath
from typing import Any

import netCDF4 as nc
import numpy as np
import pandas
import rioxarray  # noqa: F401
import xarray
from dask.array import Array
from xarray import DataArray, DataTree
from xarray.backends.zarr import DIMENSION_KEY

import sentineltoolbox.api as stb
from sentineltoolbox.api import open_datatree
from sentineltoolbox.conversion.utils import generate_datatree_from_legacy_adf
from sentineltoolbox.filesystem_utils import get_universal_path
from sentineltoolbox.models.upath import PathFsspec
from sentineltoolbox.resources.data import DATAFILE_METADATA
from sentineltoolbox.writers.zarr import write_zarr

# flake8: noqa: E501


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(
            obj,
            (
                np.integer,
                np.uint8,
                np.uint16,
                np.uint32,
                np.uint64,
                np.int8,
                np.int16,
                np.int32,
                np.int64,
            ),
        ):
            return int(obj)
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class GenericAuxiliaryConverter:
    baseline_collection = 0

    def __init__(
        self,
        input_paths: list[Path | PathFsspec],
        input_files: list | None = None,
    ) -> None:
        if input_files is None:
            input_files = []
        adf_name = [int(ip.name[-8:-5]) for ip in input_paths]
        if adf_name:
            self.baseline_collection = max(adf_name)
        self.coordinates_variables: list = []

        self.attrs = OrderedDict()

        self.name_mapping: dict = {}  # full path -> out var name
        self.path_mapping: dict = {}  # old full path -> new full path

        self.input_paths = input_paths
        self.input_files = input_files

        # TODO: self.metadata_factory = create_mapping_factory(DATAFILE_METADATA_PATH)

    def iter_variables(self, obj):
        for ds in obj.subtree:
            for k, v in ds.variables.items():
                if ds.path != "/":
                    yield ds.path + "/" + k, v
                else:
                    yield k, v

    def iter_groups(self, obj):
        if isinstance(obj, DataTree):
            yield from obj.subtree
        else:
            yield obj

    def is_custom_variable(self, variable: xarray.Variable, varpath: str):
        """
        Implement this method to define which variable must be managed manually.
        If variable must be managed manually, this method must return True else False.
        By default, always return False
        """
        return False

    def manage_custom_variable(self, out_product, variable: xarray.Variable, varpath: str):
        pass

    def out_varname(self, dt: DataTree, path: str):
        varname = PurePosixPath(path).name
        return self.name_mapping.get(varname, varname.lower())

    def out_varpath(self, dt: DataTree, path: str):
        var_name = self.out_varname(dt, path)
        parts = path.split("/")
        parts[-1] = var_name
        default_path = "/".join(parts).lower()
        variable = dt[path]

        is_coordinate = len(variable.dims) == 1 and variable.path[1:] == variable.dims[0]
        if var_name in self.coordinates_variables or is_coordinate:
            var_path = f"/coordinates{default_path}"
        else:
            var_path = f"/maps{default_path}"

        return self.path_mapping.get(variable.path, var_path)


class AuxiliaryConverterJSON(GenericAuxiliaryConverter):
    def out_varpath(self, dt: DataTree, path: str):
        var_name = self.out_varname(dt, path)
        parts = path.split("/")
        parts[-1] = var_name
        default_path = "/".join(parts).lower()
        if path.startswith("//"):
            path = path[2:]
        variable = dt[path]

        is_coordinate = len(variable.dims) == 1 and path[1:] == variable.dims[0]
        if var_name in self.coordinates_variables or is_coordinate:
            var_path = f"/coordinates{default_path}"
        else:
            var_path = default_path

        return self.path_mapping.get(path, var_path.lower())

    def generate(self):
        json_data = {}
        self.update(json_data, self.input_paths)
        return json_data

    def _dict_tree(self, root: dict, path: str) -> dict:
        dic = root
        for part in path.split("/")[:-1]:
            if not part:
                continue
            if part not in dic:
                dic[part] = {}
            dic = dic[part]
        return dic

    def manage_generic_variable(self, out_product: dict, dt: DataTree, path: str):
        var_name = self.out_varname(dt, path)
        var_path = self.out_varpath(dt, path)
        variable = dt[path]

        if var_name != DIMENSION_KEY and var_name != "coordinates":
            # EXTRACT SCALARS
            if len(variable.dims) == 0:
                # out.attrs[var_name] = {k: v for k, v in variable.attrs.items() if k != "_io_config"}
                dic = out_product
                dtype = variable.data.dtype
                value = variable.data.item()
                dic = self._dict_tree(dic, var_path)
                dic[var_name] = {k: v for k, v in variable.attrs.items() if k != "_io_config"}
                dic[var_name]["value"] = value
                dic[var_name]["type"] = str(dtype)
                io = variable.attrs.get("_io_config", {})
                dic[var_name].update({k: str(v) for k, v in io.items()})
            # COPY VARIABLES
            else:
                group = self._dict_tree(out_product, var_path)
                variable_json = group.setdefault(var_name, {})
                if isinstance(variable.data, Array):
                    lst = variable.data.compute().tolist()
                else:
                    lst = variable.data.tolist()
                variable_json["value"] = lst
                variable_json["type"] = f"array[{variable.data.dtype}]"
                variable_json.update(
                    {k: v for k, v in variable.attrs.items() if k != "_io_config"},
                )
                io = variable.attrs.get("_io_config", {})
                variable_json.update({k: str(v) for k, v in io.items()})
                # out_product.add_variable(out_path, variable)

    def update(self, out_product, input_paths):
        for input_path in input_paths:
            # for nc_file in input_path.glob("*.nc"):
            for nc_file in [i for i in input_path.iterdir() if i.suffix in [".nc", ".nc4"]]:
                if self.input_files and not nc_file.name in self.input_files:
                    continue
                legacy = open_datatree(nc_file)
                for varpath, variable in self.iter_variables(legacy):
                    if self.is_custom_variable(legacy, varpath):
                        self.manage_custom_variable(out_product, legacy, varpath)
                    else:
                        self.manage_generic_variable(out_product, legacy, varpath)

        out_product.update(self.attrs)


def convert_adf_json(adf_type: str, input_path: Path) -> dict[Any, Any]:

    if adf_type == "SY2PP":
        input_files = ["OL_2_PCP_AX.nc", "SY_2_PCP_AX.nc"]
    else:
        input_files = None

    converter = AuxiliaryConverterJSON([input_path], input_files=input_files)
    data = converter.generate()

    title = DATAFILE_METADATA.get_metadata(adf_type, "description", adf_type)
    attrs = stb.AttributeHandler(data)
    attrs.set_attr("product:type", adf_type)
    attrs.set_attr("title", title)

    return data


def str_to_python_type(s):
    if not s:
        return None
    s = s.strip().lower()
    if s == "false":
        return False, "bool"
    if s == "true":
        return True, "bool"
    if s in ("null", "none"):
        return None

    try:
        v = int(s)
        return (v, str(np.dtype(type(v))))
    except ValueError:
        try:
            v = float(s)
            return (v, str(np.dtype(type(v))))
        except ValueError:
            if "," in s:
                v_list = [i.strip() for i in s.split(",")]
            else:
                v_list = [i.strip() for i in s.split()]
                if len(v_list) <= 1:
                    return v_list[0]
            v = []
            for l in v_list:
                t = str_to_python_type(l)
                if t is None:
                    return None
                else:
                    v.append(t[0])
            return (v, str(np.dtype(type(v[0]))))


class ADJ:
    def __init__(self, path):
        self._read(path)

    def _read(self, ascii_file):
        with ascii_file.open() as file:
            self.header = file.readline()
            self.nchan = int(file.readline().split("=")[1])
            self.ptype = int(file.readline().split("=")[1])
            self.ncoef = int(file.readline().split("=")[1])
            self.nsec = int(file.readline().split("=")[1])
            self.int_id = [int(d) for d in file.readline().split() if d.isdigit()]
            self.path_length = [float(d) for d in file.readline().split()]
            self.coefs = np.zeros((self.nsec, self.nchan, self.ncoef))
            for ns in range(self.nsec):
                for nc in range(self.nchan):
                    self.coefs[ns, nc, :] = [float(d) for d in file.readline().split()]

    def to_json(self) -> dict[str, Any]:
        adf = {
            "title": "AVHRR/SLSTR Adjustment Parameters Data file",
            "baseline collection": "001",
            "nchan": {
                "type": "int16",
                "value": self.nchan,
                "description": "Number of SLSTR channels",
            },
            "ncoef": {
                "type": "int16",
                "value": self.ncoef,
                "description": "Number of coefficients",
            },
            "nsec": {
                "type": "int16",
                "value": self.nsec,
                "description": "Number of path lengths",
            },
            "path_length": {
                "type": "array[float64]",
                "value": self.path_length,
                "description": "Considered path lengths",
            },
            "coeffs": {
                "type": "array[float64]",
                "value": self.coefs.tolist(),
                "description": "Coefficients enabling the adjustment between AVHRR and SLSTR radiometric content",
            },
        }
        return adf


def convert_sl_and_syn_adf_json(adf_type: str, input_path: Path) -> dict[Any, Any]:
    json_data = {}
    # TODO: support PathFsspec correctly (with open to be compatible with bucket)

    if adf_type in (
        "SL1PP",  # legacy: SL_1_PCP_AX
        "SL2PP",  # legacy: SL_2_PCP_AX
        "SY1PP",  # legacy: SY_1_PCP_AX
        "VGSPP",  # legacy: SY_2_PCPSAX
    ):
        tag_modifications = {"land_branch_switches": "switches"}

        for xml_file in input_path.glob("*.xml"):
            if xml_file.name == "xfdumanifest.xml":
                continue
            with xml_file.open() as xml_file_fp:
                tree = ET.parse(xml_file_fp)
                root = tree.getroot()
                for child in root:
                    tag = child.tag.lower()
                    tag = tag_modifications.get(tag, tag)
                    json_data[tag] = {}
                    for param in child:
                        p = {k.lower(): v for k, v in param.attrib.items() if k != "name"}
                        name = param.attrib["name"].lower()
                        json_data[tag][name] = p
                        # Correct type
                        raw_value = param.attrib["value"].strip()
                        if raw_value:
                            result = str_to_python_type(raw_value)
                            if result is not None:
                                json_data[tag][name]["value"] = result[0]
                                json_data[tag][name]["type"] = result[1]
                        else:
                            t = param.attrib.get("type")
                            if t == "INTEGER":
                                json_data[tag][name]["value"] = None
                                json_data[tag][name]["type"] = "int64"
                            if t == "DOUBLE":
                                json_data[tag][name]["value"] = None
                                json_data[tag][name]["type"] = "float64"

    elif adf_type == "SLADJ":
        # legacy: SL_1_ADJ_AX
        for ascii_file in input_path.glob("*.inf"):
            adf = ADJ(ascii_file)
            json_data.update(adf.to_json())
    else:
        raise NotImplementedError(f"No 'convert to json' converter for {adf_type}")
    return json_data


def convert_adf_safe(adf_type: str, input_path: PathFsspec) -> DataTree:
    """
    Convert SAFE legacy ADF (Auxiliary Data File) to a DataTree structure based on the ADF type.
    To convert to json dict, see :obj:`convert_adf_json`

    This function processes different types of ADF files and generates a corresponding
    DataTree structure.

    The `adf_type` parameter specifies the conversion method to be applied. This means that the same input can be
    converted into different DataTree structures depending on the specified `adf_type`. This feature allows for
    splitting a legacy product into multiple DataTrees.

    The function also sets metadata attributes for the resulting DataTree.

    Parameters
    ----------
    adf_type : str
        The type of ADF file to process.
    input_path : PathFsspec
        The path to the input ADF file or directory.

    Returns
    -------
    DataTree
        A DataTree structure containing the processed ADF data.

    Raises
    ------
    NotImplementedError
        If the provided ADF type is not supported.

    """
    xdt: DataTree = DataTree(name="root_adf")

    if adf_type in {"SLIRE"}:
        # See todo_{adf_type}.txt
        raise NotImplementedError(f"No converter for {input_path.name!r}. {adf_type!r} is not supported")

    elif adf_type == "OLLUT":
        # legacy: OL_1_CLUTAX
        for ncgroup in ["bright_reflectance", "sun_glint_risk"]:
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                ncgroup=ncgroup,
                dt=xdt,
            )

    elif adf_type == "OLINS":
        # legacy: OL_1_INS_AX
        nc_ds = nc.Dataset(input_path / "OL_1_INS_AX.nc")
        ncgroups = nc_ds.groups.keys()
        for ncgroup in ncgroups:
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                ncgroup=ncgroup,
                dt=xdt,
            )
        xdt.attrs.update({attr: nc_ds.getncattr(attr) for attr in nc_ds.ncattrs()})

    elif adf_type == "OLCAL":
        # legacy: OL_1_CAL_AX
        nc_ds = nc.Dataset(input_path / "OL_1_CAL_AX.nc")
        ncgroups = nc_ds.groups.keys()
        for ncgroup in ncgroups:
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                ncgroup=ncgroup,
                dt=xdt,
            )
        xdt.attrs.update({attr: nc_ds.getncattr(attr) for attr in nc_ds.ncattrs()})

    elif adf_type == "OLPRG":
        # legacy: OL_1_PRG_AX
        nc_ds = nc.Dataset(input_path / "OL_1_PRG_AX.nc")
        ncgroups = nc_ds.groups.keys()
        for ncgroup in ncgroups:
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                ncgroup=ncgroup,
                dt=xdt,
            )
        xdt.attrs.update({attr: nc_ds.getncattr(attr) for attr in nc_ds.ncattrs()})

    elif adf_type == "OLPPP":
        # legacy: OL_2_PPP_AX
        xdt = generate_datatree_from_legacy_adf(
            input_path,
            safe_file=["OL_2_PPP_AX.nc"],
            dt=xdt,
        )
        for ncgroup in ["classification_1", "gas_correction", "classification_2"]:
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                ncgroup=ncgroup,
                dt=xdt,
            )

    elif adf_type == "OLACP":
        # legacy: OL_2_ACP_AX
        for ncgroup in [
            "glint_whitecaps",
            "bright_waters_NIR",
            "standard_AC",
            "alternate_AC",
        ]:
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                ncgroup=ncgroup,
                dt=xdt,
            )

    elif adf_type == "OLOCP":
        # legacy: OL_2_OCP_AX
        xdt = generate_datatree_from_legacy_adf(
            input_path,
            dt=xdt,
        )
        for ncgroup in [
            "rhow_norm_nn",
        ]:
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                ncgroup=ncgroup,
                dt=xdt,
            )

    elif adf_type in (
        "OLWVP",  # legacy: OL_2_WVP_AX
        "OLCLP",  # legacy: OL_2_CLP_AX
        "OLVGP",  # legacy: OL_2_VGP_AX
        "SLCLO",  # legacy: SL_1_CLO_AX
        "SLGEO",  # legacy: SL_1_GEO_AX
        "IMSCD",  # legacy: SL_2_IMSCAX
        "SLVIC",  # legacy: SL_1_VIC_AX
    ):
        xdt = generate_datatree_from_legacy_adf(
            input_path,
            group="",
        )
        if adf_type == "SLGEO":
            xdt.scans_cone_angle.attrs["long_name"] = "Cone angle for each scan (nadir first, then oblique)"

    elif adf_type == "SLANC":
        # legacy: SL_1_ANC_AX
        for nc_file_path in input_path.glob("*.nc"):
            ds = open_datatree(nc_file_path)
            for group in ds.groups:
                xdt = generate_datatree_from_legacy_adf(
                    input_path,
                    ncgroup=group,
                    dt=xdt,
                )

    elif adf_type == "SLLCC":
        # legacy: SL_1_LCC_AX
        xdt = generate_datatree_from_legacy_adf(input_path, dt=xdt)

    elif adf_type == "SLGEC":
        xdt = convert_SL_1_GEC_AX_to_SLGEC(input_path, xdt)

    elif adf_type == "SLCDP":
        xdt = convert_SL_1_CDP_AX_to_SLCDP(input_path, xdt)

    elif adf_type == "SLCLP":
        xdt = convert_SL_1_CLP_AX_to_SLCLP(input_path, xdt)

    elif adf_type == "SLBDF":
        # legacy: SL_2_LSTBAX
        xdt = convert_SL_2_LSTBAX_to_SLBDF(input_path, xdt)

    elif adf_type == "LSTCD":
        # legacy: SL_2_LSTCAX
        xdt = generate_datatree_from_legacy_adf(
            input_path,
            title="lst coefficient data file",
            group="",
            var_to_attr={
                "skip_biomes": ["long_name", "flag_meanings"],
            },  # "time_bounds": []}
            dt=xdt,
        )

    elif adf_type == "LSTED":
        # legacy: SL_2_LSTEAX
        xdt = generate_datatree_from_legacy_adf(
            input_path,
            group="",
            coordinates_variable={  # variable : (dimention,coordinate)
                "u_ran_emis": ("n_biome", "biome"),
            },
            dt=xdt,
        )
        xdt.attrs["latitude resolution"] = 1
        xdt.attrs["longitude resolution"] = 1

    elif adf_type == "FRPAC":
        # legacy: S3A_SL_2_FRPTAX
        # Note: S3A_SL_2_FRPTAX is also used with S3A_SL_2_PCPFAX to generate FRPPP
        xdt = _convert_SL_2_FRPTAX_to_FRPAC(input_path, xdt)

    elif adf_type == "FRPCM":
        # legacy: SL_2_CFM_AX
        _convert_SL_2_CFM_to_FRPCM(input_path, xdt)

    elif adf_type in (
        "SDRRT",  # legacy: SY_2_RAD_AX
        "VGTRT",  # legacy: SY_2_RADPAX
        "VGSRT",  # legacy: SY_2_RADSAX
        "SYCLP",  # legacy: SY_2_PCP_AX
        "SYSRF",  # legacy: SY_2_SPCPAX
        "AODRT",  # legacy: SY_2_ART_AX
        "AODOR",  # legacy: SY_2_OSR_AX
        "AODLR",  # legacy: SY_2_LSR_AX
        "AODAC",  # legacy: SY_2_ACLMAX
    ):
        xdt = generate_datatree_from_legacy_adf(
            input_path,
            group="",
        )

    elif adf_type == "SYGCP":

        xdt = generate_datatree_from_legacy_adf(
            input_path,
            ncgroup="OGPP_L1c_Tie_Points_Database",
        )

    elif adf_type == "SYPPP":
        # legacy: SY_2_PCP_AX
        xdt = generate_datatree_from_legacy_adf(
            input_path,
            safe_file=["OL_2_PPP_AX.nc"],
            dt=xdt,
        )
        for ncgroup in ["classification_1", "classification_2"]:
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                safe_file=["OL_2_PPP_AX.nc"],
                ncgroup=ncgroup,
                dt=xdt,
            )

    elif adf_type == "SYCDI":
        # legacy: S3__SY_1_CDIBAX
        # for tif_file in sorted(input_path.glob("*.tif")):
        xdt = _convert_SY_1_CDIBAX_to_SYCDI(input_path, xdt)

    elif adf_type == "SYAOD":
        # legacy: SY_2_AODCAX
        data: list[xarray.Dataset] = []
        if "s3" in input_path.protocols:
            # Force local path because rasterio do not support opened files. bucket url not tested
            local_upath = get_universal_path(input_path, cache=True)
        else:
            local_upath = input_path
        for envi_file in sorted(local_upath.glob("*.img")):
            rds = rioxarray.open_rasterio(envi_file.path)
            # print(rds)
            data.append(
                rds.sel(band=1).drop_vars("band").rename("aod550"),
            )  # .rename({"band_data":"aod550"}))

        da = xarray.concat(data, pandas.Index(range(12), name="month"))
        global_attr = dict(
            {
                "resolution": "0.125x0.125 degrees",
                "number_of_grid_points_in_longitude": 2280,
                "number_of_grid_points_in_latitude": 1440,
                "first_longitude_value": -180.0,
                "last_longitude_value": 180.0,
                "grid_step_in_longitude": 0.125,
                "first_latitude_value": 90.0,
                "last_latitude_value": -90.0,
                "grid_step_in_latitude": 0.125,
            },
        )
        for gattr in global_attr:
            val = global_attr.get(gattr)
            if isinstance(val, str):
                da.attrs[gattr] = val.lower()
            else:
                da.attrs[gattr] = val
        if isinstance(da, DataArray):
            da = da.to_dataset()
        xdt = DataTree(dataset=da)
    else:
        raise NotImplementedError(f"{input_path.name}: ADF type {adf_type} is not supported")

    title = DATAFILE_METADATA.get_metadata(adf_type, "description", adf_type)
    attrs = stb.AttributeHandler(xdt)
    attrs.set_attr("product:type", adf_type)
    attrs.set_attr("title", title)
    attrs.set_attr("processing:version", input_path.name[-8:-5])
    return xdt


def _convert_SL_2_CFM_to_FRPCM(input_path, xdt):
    nc_file = "Gas_Flare_List.nc"
    in_file = input_path / nc_file
    ds = nc.Dataset(in_file)
    lat = ds.variables["Latitude"][:]
    lon = ds.variables["Longitude"][:]
    gas_flare = xarray.Dataset(
        {"latitude": lat, "longitude": lon},
    )
    gas_flare.latitude.attrs["long_name"] = "Latitude"
    gas_flare.latitude.attrs["units"] = "degrees_north"
    gas_flare.latitude.attrs["valid_max"] = 90.0
    gas_flare.latitude.attrs["valid_min"] = -90.0
    gas_flare.longitude.attrs["long_name"] = "Longitude"
    gas_flare.longitude.attrs["units"] = "degrees_east"
    gas_flare.longitude.attrs["valid_max"] = 180.0
    gas_flare.longitude.attrs["valid_min"] = -180.0
    nc_file = "Volcano_list.nc"
    in_file = input_path / nc_file
    ds = nc.Dataset(in_file)
    lat = ds.variables["Latitude"][:]
    lon = ds.variables["Longitude"][:]
    volcano = xarray.Dataset({"latitude": lat, "longitude": lon})
    volcano.latitude.attrs["long_name"] = "Latitude"
    volcano.latitude.attrs["units"] = "degrees_north"
    volcano.latitude.attrs["valid_max"] = 90.0
    volcano.latitude.attrs["valid_min"] = -90.0
    volcano.longitude.attrs["long_name"] = "Longitude"
    volcano.longitude.attrs["units"] = "degrees_east"
    volcano.longitude.attrs["valid_max"] = 180.0
    volcano.longitude.attrs["valid_min"] = -180.0
    DataTree(name="gas_flare", parent=xdt, data=gas_flare)
    DataTree(name="volcano", parent=xdt, data=volcano)


def _convert_SY_1_CDIBAX_to_SYCDI(input_path, xdt):
    ds: list[xarray.Dataset] = []
    for j in range(8):
        var: list[xarray.Dataset] = []
        for i in range(4):
            tif_file = f"distMap_0{j}0{i}_geoTIFF.tif"
            with (input_path / tif_file).open(mode="rb") as tif_fp:
                ds_from_tif = (
                    xarray.open_dataset(
                        tif_fp,
                        chunks={"x": 4050, "y": 4050},
                    ).squeeze(drop=True),
                )

                var.append(ds_from_tif.compute())
                ds_from_tif.close()
        ds.append(xarray.concat(var, dim="y"))
    ds_concat = xarray.concat(ds, dim="x")
    ds_concat.attrs.update(
        {
            "resolution": "0.0028x0.0028 degrees",
            "number_of_tile": 32,
            "number_of_grid_points_in_longitude_per_tile": 16200,
            "number_of_grid_points_in_latitude_per_tile": 16200,
            "first_longitude_value": -180.0,
            "last_longitude_value": 180.0,
            "grid_step_in_longitude": 0.002777777777800,
            "first_latitude_value": 90.0,
            "last_latitude_value": -90.0,
            "grid_step_in_latitude": -0.002777777777800,
        },
    )
    final_ds = ds_concat.rename({"band_data": "distance_to_coast"})
    final_xdt = DataTree(final_ds)
    return final_xdt


def _convert_sl_1_dtm_to_sldtm(adf_type, input_path):
    import xarray as xr

    xdt = DataTree()

    # Same chunks as in ADF WATER produced by CS
    CHUNK_LAT: int = 649
    CHUNK_LON: int = 1297

    try:
        ds = xr.open_dataset(str(input_path) + "/distance_to.nc")
    except FileNotFoundError:
        raise FileNotFoundError(f"Expected a file distance_to.nc in {str(input_path)}.")

    ds["distance_to"] = ds["distance_to"].chunk({"lat": CHUNK_LAT, "lon": CHUNK_LON})

    xdt.ds = ds

    return xdt


def _convert_sl_1_pfp_to_slpfp(adf_type, input_path):
    import pandas as pd

    xdt = DataTree()

    CSV_FILES_SLPFP = ["ABnadir", "ABoblique", "Fnadir", "Foblique", "Inadir", "Ioblique"]
    file_with_suffix = [file + ".csv" for file in CSV_FILES_SLPFP]

    for name, file in zip(CSV_FILES_SLPFP, file_with_suffix):
        in_csv = input_path / file
        try:
            with in_csv.open(mode="r", newline=""):
                ds = pd.read_csv(str(in_csv), index_col="Pix No.").to_xarray()
        except FileNotFoundError:
            raise FileNotFoundError(f"{str(file)} expected in {str(input_path)} but not found.")

        # Store each csv file in a different node of the datatree
        xdt[name] = ds

    return xdt


def _convert_SL_2_FRPTAX_to_FRPAC(input_path, xdt):
    uh2o = []
    thickness = {"MWIR": [], "SWIR": []}
    var_a = {"MWIR": [], "SWIR": []}
    var_b = {"MWIR": [], "SWIR": []}
    var_c = {"MWIR": [], "SWIR": []}
    # Read SL_2_ATMCOR.csv
    in_csv = input_path / "SL_2_ATMCOR.csv"
    with in_csv.open(mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            row_num = list(map(lambda s: str_to_python_type(s)[0], row))
            if row_num:
                uh2o.append(row_num[0])
                thickness["MWIR"].append(row_num[1])
                var_a["MWIR"].append(row_num[2])
                var_b["MWIR"].append(row_num[3])
                var_c["MWIR"].append(row_num[4])
    # Read SL_2_ATMCOR_SWIR.csv
    in_csv = input_path / "SL_2_ATMCOR_SWIR.csv"
    with in_csv.open(mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            row_num = list(map(lambda s: str_to_python_type(s)[0], row))
            if row_num:
                # uh2o.append(row[0])
                thickness["SWIR"].append(row_num[1])
                var_a["SWIR"].append(row_num[2])
                var_b["SWIR"].append(row_num[3])
                var_c["SWIR"].append(row_num[4])
    data1 = np.stack([thickness["MWIR"], thickness["SWIR"]])
    data2 = np.stack([var_a["MWIR"], var_a["SWIR"]])
    data3 = np.stack([var_b["MWIR"], var_b["SWIR"]])
    data4 = np.stack([var_c["MWIR"], var_c["SWIR"]])
    ds = xarray.Dataset(
        data_vars=dict(
            thickness=(["band", "uh2o"], data1),
            coef_a=(["band", "uh2o"], data2),
            coef_b=(["band", "uh2o"], data3),
            coef_c=(["band", "uh2o"], data4),
        ),
        coords=dict(band=[0, 1], uh2o=uh2o),
    )
    ds.coords["band"].attrs = {"long_name": "MWIR (0) or SWIR (1)"}
    ds.coords["uh2o"].attrs = {"long_name": "water vapor", "units": ""}
    final_xdt = DataTree(
        name="maps",
        # parent=dt,
        data=ds,
    )
    return final_xdt


def convert_SL_1_GEC_AX_to_SLGEC(input_path, xdt):
    # legacy: SL_1_GEC_AX
    merged_variables = [
        "quaternions_1",
        "quaternions_2",
        "quaternions_3",
        "quaternions_4",
    ]
    merged_mapping = {
        "quaternions": (
            merged_variables,
            "n_quaternions",
            {
                "long_name": "Quaternions components. The thermo-elastic deformations are provided as quaternions covering one orbital revolution for a number of days in the year. The quaternions are derived from rotation angles from Instrument to Satellite.",
            },
        ),
    }
    # coordinates_variables = ['julian_days','on_orbit_positions_angle']
    final_xdt = generate_datatree_from_legacy_adf(
        input_path,
        merged_variables=merged_variables,
        merged_mapping=merged_mapping,
        group="",
    )  # if group=None, by default subgroup maps is created if group=="" no subgroup
    return final_xdt


def convert_SL_1_CLP_AX_to_SLCLP(input_path, xdt):
    final_xdt = generate_datatree_from_legacy_adf(
        input_path,
        group="",
    )
    # Add some attributes
    xdt.sec_satz.attrs["long_name"] = "secant of Satellite Zenith Angle"
    xdt.solz.attrs["long_name"] = "Solar Zenith Angle (reduced resolution)"
    xdt.t110.attrs["long_name"] = "textural BT 11\u03bcm channel"
    xdt.txt_110.attrs["long_name"] = "Probability density LUT for thermal texture (LSD 11\u03bcm)"
    return final_xdt


def convert_SL_2_LSTBAX_to_SLBDF(input_path, xdt):
    # Loop over the tiff files
    from eopf.accessor import EORasterIOAccessor

    for tif_file in sorted(input_path.glob("*.tif*")):
        legacy = EORasterIOAccessor(str(tif_file))
        legacy.open(mode="r")
        var = legacy["value"][0, :, :].data.compute()
        coord = legacy["coordinates"]
        x = coord.x.data.compute()
        y = coord.y.data.compute()

        xdt["maps/biome"] = xarray.Variable(
            data=var,
            attrs={"long_name": "Gridded GlobCover surface classification code"},
            dims=("x", "y"),
        )

        xdt["coordinates/x"] = xarray.Variable(
            data=-x,
            attrs={"long_name": "Longitudes", "units": "degrees_east", "valid_max": 180.0, "valid_min": -180.0},
            dims=("x",),
        )

        xdt["coordinates/y"] = xarray.Variable(
            data=-y,
            attrs={"long_name": "Latitudes", "units": "degrees_north", "valid_max": 90.0, "valid_min": -90.0},
            dims=("y",),
        )

        # Modify global attributes
        global_attr = dict(
            {
                "title": "LST Biome Data File",
                "baseline collection": f"{0:03d}",
                "resolution": "0.0089x0.0089 degrees",
                "bit meaning": [
                    "open_ocean",
                    "irrigated_cropland",
                    "rainfed_cropland",
                    "mosaic_cropland",
                    "mosaic_vegetation",
                    "broadleaved_evergreen_forest",
                    "closed_broadleaved_deciduous_forrest",
                    "open_broadleaved_deciduous_forest",
                    "closed_needleleaved_forest",
                    "open_needleleaved_forest",
                    "mixed_forest",
                    "mosaic_forest",
                    "mosaic_grassland",
                    "shrubland",
                    "grassland",
                    "sparse_vegetation",
                    "freshwater_flooded_forest",
                    "saltwater_flooded_forest",
                    "flooded_vegetation",
                    "artificial_surface",
                    "bare_area_unknown",
                    "bare_area_orthents",
                    "bare_area_sand",
                    "bare_area_calcids",
                    "bare_area_cambids",
                    "bare_area_orthels",
                    "water snow_and_ice",
                ],
                "number_of_grid_points_in_longitude": 43200,
                "number_of_grid_points_in_latitude": 21600,
                "first_longitude_value": 180.0,
                "last_longitude_value": -180.0,
                "grid_step_in_longitude": -0.008333333333333,
                "first_latitude_value": 90.0,
                "last_latitude_value": -90.0,
                "grid_step_in_latitude": -0.008333333333333,
            },
        )
        xdt.attrs.update(global_attr)

        # coordinates = {
        #    "x": -c.x,
        #    "y": -c.y,
        # }
        # print(coordinates)
        # biome = maps.biome.assign_coords(coordinates)
        # DataTree(name="maps", parent=dt_new, data=biome)

        return xdt


def convert_SL_1_CDP_AX_to_SLCDP(input_path, xdt):
    # legacy: SL_1_CDP_AX
    final_xdt = generate_datatree_from_legacy_adf(input_path, group="", dt=xdt)
    # Add some attributes
    final_xdt.c110.attrs["long_name"] = "Brigthness temperature at 11\u03bcm channel"
    final_xdt.sst.attrs["long_name"] = "sea surface salinity"
    final_xdt.sec_satz.attrs["long_name"] = "secant of Satellite Zenith Angle"
    final_xdt.solz.attrs["long_name"] = "Solar Zenith Angle (reduced resolution)"
    final_xdt.d110sst.attrs["long_name"] = "Difference between BT (11\u03bcm) and SST"
    final_xdt.d110120.attrs["long_name"] = "Difference between BT (11\u03bcm) and BT (12\u03bcm)"
    final_xdt.d037110.attrs["long_name"] = "Difference between BT (3.7\u03bcm) and BT (11\u03bcm)"
    final_xdt.t110.attrs["long_name"] = "textural BT 11\u03bcm channel"
    final_xdt.solz_1.attrs["long_name"] = "Solar Zenith Angle"
    final_xdt.sst_1.attrs["long_name"] = "sea surface salinity (reduced resolution)"
    final_xdt.c016.attrs["long_name"] = "Reflectances on 1.6\u03bcm channel in cloudy conditions"
    final_xdt.c008.attrs["long_name"] = "Reflectances on 0.87\u03bcm channel in cloudy conditions"
    final_xdt.c006.attrs["long_name"] = "Reflectances on 0.66\u03bcm channel in cloudy conditions"
    final_xdt.d006008.attrs["long_name"] = "Differences betwen R(0.66\u03bcm) and R(0.87\u03bcm)"
    final_xdt.tir_110_120.attrs["long_name"] = (
        "Spectral Probability density LUT for Thermal daytime (11\u03bcm, 12\u03bcm)"
    )
    final_xdt.txt_110.attrs["long_name"] = (
        "Probability density LUT for day- and night-time thermal texture (LSD 11\u03bcm)"
    )
    final_xdt.tir_037_110_120.attrs["long_name"] = (
        "Probability density LUT for Thermal nighttime (3.7\u03bcm, 11\u03bcm, 12\u03bcm)"
    )
    final_xdt.vis_006_008.attrs["long_name"] = (
        "Spectral Probability density LUT associated with Joint daytime reflectance in cloudy conditions"
    )
    return final_xdt


def convert_adf(
    upath_input: PathFsspec,
    adf_type: str | None = None,
    semantic_mapping: dict[Any, Any] | None = None,
    **kwargs: Any,
) -> DataTree | dict[str, Any]:
    if semantic_mapping is None:
        semantic_mapping = {}

    if adf_type is None:
        fgen, fgen_data = stb.filename_generator(upath_input.name, semantic_mapping=semantic_mapping)
        adf_type = fgen.semantic

    if adf_type in CONVERT_ADFS:
        data = CONVERT_ADFS[adf_type](
            adf_type,
            upath_input,
        )
        return data
    else:
        raise NotImplementedError(adf_type)


def convert_and_merge_adf_json(adf_type: str, input_paths: list[Path], output_path: str) -> None:
    json_data = {}
    if adf_type == "FRPPP":
        for input_path in input_paths:
            if "PCPFAX" in input_path.name:
                for xml_file in input_path.glob("*.xml"):
                    if xml_file.name == "xfdumanifest.xml":
                        continue
                    with xml_file.open(mode="r") as xml_file_fp:
                        tree = ET.parse(xml_file_fp)
                    root = tree.getroot()
                    for child in root:
                        tag = child.tag.lower()
                        json_data[tag] = {}
                        for param in child:
                            p = {k.lower(): v for k, v in param.attrib.items() if k != "name"}
                            name = param.tag.lower()
                            json_data[tag][name] = p
                            # Get value
                            if param.text:
                                result = str_to_python_type(param.text)
                                if result:
                                    json_data[tag][name]["value"] = result[0]
                                    json_data[tag][name]["type"] = result[1]

            if "FRPTAX" in input_path.name:
                for xml_file in input_path.glob("*.xml"):
                    if xml_file.name == "xfdumanifest.xml":
                        continue

                    namespaces = {"": "slstr_namespace", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
                    with xml_file.open(mode="r") as xml_file_fp:
                        tree = ET.parse(xml_file_fp)
                    root = tree.getroot()
                    step = root.find("steps", namespaces)
                    for child in step:
                        tag = child.tag.split("}")[-1].lower()
                        json_data[tag] = {}
                        for param in child:
                            p = {k.lower(): v for k, v in param.attrib.items() if k != "name"}
                            name = param.attrib["name"].lower()
                            type = param.attrib["type"]

                            json_data[tag][name] = p
                            # Correct type
                            if type == "String":
                                result = str_to_python_type(param.attrib["value"])
                                json_data[tag][name]["value"] = result[0]
                                json_data[tag][name]["type"] = result[1]
                            else:
                                result = str_to_python_type(param.attrib["value"])
                                json_data[tag][name]["value"] = result[0]
                                json_data[tag][name]["type"] = str(np.dtype(type))
    else:
        raise NotImplementedError(f"No 'convert and merge (json)' converter for {adf_type}")
    with open(output_path, "w") as outfile:
        json.dump(json_data, outfile, indent=4)


def convert_and_merge_adf(adf_type: str, input_paths: list[Path], output_path: str) -> None:
    # TODO: support s3 buckets
    xdt = DataTree(name="root_adf")
    input_path_ref = input_paths[0]
    if adf_type == "VSWCD":
        """
        legacy inputs:
        SL_1_N_S1AX, SL_1_N_S2AX, SL_1_N_S3AX, SL_1_O_S1AX, SL_1_O_S2AX, SL_1_O_S3AX, SL_1_NAS4AX, SL_1_NAS5AX,
        SL_1_NAS6AX, SL_1_NBS4AX, SL_1_NBS5AX, SL_1_NBS6AX, SL_1_OAS4AX, SL_1_OAS5AX, SL_1_OAS6AX, SL_1_OBS4AX,
        SL_1_OBS5AX, SL_1_OBS6AX
        """
        for input_path in input_paths:
            input_name = input_path.name
            group = input_name[9:13].lower()
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                coordinates_variable={  # variable : (dimention,coordinate)
                    "cal_uncertainty_uncertainty": (
                        "uncertainty_lut",
                        "cal_uncertainty_radiance",
                    ),
                    "non_linearities": ("lut", "detectors_count"),
                    "coffsets": ("channels", "voffsets"),
                },
                group=group,
                dt=xdt,
            )

    elif adf_type == "TIRCD":
        """
        legacy inputs:
        SL_1_N_S7AX, SL_1_N_S8AX, SL_1_N_S9AX, SL_1_N_F1AX, SL_1_N_F2AX, SL_1_O_S7AX, SL_1_O_S8AX, SL_1_O_S9AX,
        SL_1_O_F1AX, SL_1_O_F2AX
        """
        for input_path in input_paths:
            input_name = input_path.name
            group = input_name[9:13].lower()
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                coordinates_variable={  # variable : (dimention,coordinate)
                    "radiances": ("radiances_lut", "temperatures"),
                    "cal_uncertainty_uncertainty": (
                        "uncertainty_lut",
                        "cal_uncertainty_temperature",
                    ),
                    "non_linearities": ("non_linearities_lut", "detectors_count"),
                    "coffsets": ("offsets_lut", "voffsets"),
                },
                group=group,
                dt=xdt,
            )
    elif adf_type == "TIRND":
        """
        legacy inputs: SL_2_S7N_AX, SL_2_S7O_AX, SL_2_S8N_AX, SL_2_S8O_AX, SL_2_S9N_AX,
        SL_2_S9O_AX, SL_2_F1N_AX, SL_2_F1O_AX,
        """
        for input_path in input_paths:
            group = input_path.name[9:12].lower()
            xdt = generate_datatree_from_legacy_adf(
                input_path,
                group=group,
                dt=xdt,
            )

    elif adf_type == "SYMCH":
        # legacy inputs: OL_1_MCHDAX, SL_1_MCHDAX
        for input_path in input_paths:
            group = "root"
            if "_OL_" in input_path.name:
                group = "olci"
            elif "_SL_" in input_path.name:
                group = "slstr"

            for nc_file in input_path.glob("*.nc4"):
                dt_legacy = xarray.open_datatree(nc_file)

                ds = [dt_legacy[g].to_dataset() for g in dt_legacy.groups if g != "/"]
                band_index = [g.split("_")[-1] for g in dt_legacy.groups if g != "/"]
                ds = xarray.concat(
                    ds,
                    xarray.DataArray(band_index, name=f"{group}_band", dims="band"),
                )
                DataTree(name=group, parent=xdt, data=ds)
    elif adf_type == "FRPPA":
        # legacy: SL_2_SXPAAX, SL_2_FXPAAX
        for input_path in input_paths:
            for nc_file in input_path.glob("*.nc"):
                band = nc_file.name.split("_")[1].lower()
                view = nc_file.name.split("_")[2].lower()
                ds = xarray.open_dataset(nc_file, chunks={})
                ds = ds.rename({var: var.lower() for var in ds.variables})
                for var in ds.variables:
                    ds[var].attrs = {k.lower(): v.lower() for k, v in ds[var].attrs.items()}

                DataTree(name=band + view[0], parent=xdt, data=ds)

    else:
        raise NotImplementedError(f"No 'convert and merge' converter for {adf_type}")

    title = DATAFILE_METADATA.get_metadata(adf_type, "description", adf_type)
    attrs = stb.AttributeHandler(xdt)
    attrs.set_attr("product:type", adf_type)
    attrs.set_attr("title", title)
    attrs.set_attr("processing:version", input_path_ref.name[-8:-5])
    write_zarr(xdt, output_path)
    del xdt
    gc.collect()


CONVERT_ADFS = {
    # OL1
    "OLINS": convert_adf_safe,
    "OLLUT": convert_adf_safe,
    "OLCAL": convert_adf_safe,
    "OLPRG": convert_adf_safe,
    "OLEOP": convert_adf_json,
    "OLRAC": convert_adf_json,
    "OLSPC": convert_adf_json,
    # OL2
    "OLPPP": convert_adf_safe,
    "OLACP": convert_adf_safe,
    "OLWVP": convert_adf_safe,
    "OLOCP": convert_adf_safe,
    "OLVGP": convert_adf_safe,
    "OLCLP": convert_adf_safe,
    "OLPCP": convert_adf_json,
    # SL1
    "SLANC": convert_adf_safe,
    "SLGEC": convert_adf_safe,
    "SLGEO": convert_adf_safe,
    "SLCLO": convert_adf_safe,
    "SLCDP": convert_adf_safe,
    "SLCLP": convert_adf_safe,
    "SL1PP": convert_sl_and_syn_adf_json,
    "SLADJ": convert_sl_and_syn_adf_json,
    # SL2
    "IMSCD": convert_adf_safe,
    "SLLCC": convert_adf_safe,
    # "SLBDF": convert_adf_safe,
    "LSTCD": convert_adf_safe,
    "LSTED": convert_adf_safe,
    "SLPFP": _convert_sl_1_pfp_to_slpfp,
    "SLDTM": _convert_sl_1_dtm_to_sldtm,
    # "LSTWV": convert_adf_safe,
    "SL2PP": convert_sl_and_syn_adf_json,
    "SLVIC": convert_adf_safe,
    # SL2_FRP
    "FRPAC": convert_adf_safe,
    "FRPCM": convert_adf_safe,
    # SYN
    "SDRRT": convert_adf_safe,
    "VGTRT": convert_adf_safe,
    "VGSRT": convert_adf_safe,
    "SYCLP": convert_adf_safe,
    "SYSRF": convert_adf_safe,
    "SYGCP": convert_adf_safe,
    "SYPPP": convert_adf_safe,
    "SY1PP": convert_sl_and_syn_adf_json,  # legacy: SY_1_PCP_AX
    "VGSPP": convert_sl_and_syn_adf_json,  # legacy: SY_2_PCPSAX
    "SY2PP": convert_adf_json,
    "SYCDI": convert_adf_safe,
    # SYN AOD
    "AODRT": convert_adf_safe,
    "AODOR": convert_adf_safe,
    "AODLR": convert_adf_safe,
    "AODAC": convert_adf_safe,
    "SYAOD": convert_adf_safe,
    "AODPP": convert_adf_json,  # legacy: SY_2_PCPAAX
}


CONVERT_AND_MERGE_ADFS = {
    "TIRCD": convert_and_merge_adf,
    "TIRND": convert_and_merge_adf,
    "VSWCD": convert_and_merge_adf,
    "SYMCH": convert_and_merge_adf,
    "FRPPP": convert_and_merge_adf_json,
    "FRPPA": convert_and_merge_adf,
}

SUPPORTED_ADFS = []
for dic in (CONVERT_ADFS, CONVERT_AND_MERGE_ADFS):
    SUPPORTED_ADFS += list(dic.keys())
