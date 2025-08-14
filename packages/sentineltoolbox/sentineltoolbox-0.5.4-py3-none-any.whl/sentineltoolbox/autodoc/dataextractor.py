import logging
import warnings
from collections import OrderedDict
from html import escape
from operator import getitem
from pathlib import Path
from typing import Any, Generator, Hashable, Iterable

import jinja2
from xarray import DataTree

from sentineltoolbox.attributes import AttributeHandler
from sentineltoolbox.autodoc.ellipsis import Ellipsis
from sentineltoolbox.readers.resources import load_resource_file
from sentineltoolbox.resources.data import (
    DATAFILE_METADATA,
    PROPERTIES_METADATA,
    ResourceDb,
)
from sentineltoolbox.stacutils import STAC_PROPERTIES
from sentineltoolbox.typedefs import DataTreeNode

LOGGER = logging.getLogger()
AUTODOC_CONF = load_resource_file("autodoc.json")


def extract_description_from_attrs(attrs: dict[Hashable, Any]) -> str:
    desc_keys = ["description", "long_name", "documentation"]
    for key in desc_keys:
        if key in attrs:
            desc = attrs[key]
            if isinstance(desc, dict):
                return extract_description_from_attrs(desc)
            else:
                return desc
    return ""


def is_flag_variable(obj: DataTreeNode) -> bool:
    """
    Test if variable is a mask/flag

    :param obj: variable to test
    :return: true if variable corresponds to a flag
    """
    return "flag_masks" in obj.attrs or "flag_values" in obj.attrs


def sort_groups(obj: Any) -> Any:
    group_order = AUTODOC_CONF.get("group_order", {})

    try:
        path = obj.path
    except AttributeError:
        path = str(obj)

    order = group_order.get("default", 100)
    if path == "/":
        order = 0
    for key, value in group_order.items():
        if path.startswith(key):
            order = group_order[key]
    orderstr = "%03d" % order
    return orderstr + path


class DataExtractor:
    """
    Extracts and processes data from a specified data structure (generally DataTree),
    This class provides utility methods for handling flag attributes, iterating over variables, and manipulating
    metadata.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.jinja_env = jinja2.Environment(autoescape=True)

    def title(self, key: str) -> str:
        return DATAFILE_METADATA.get_metadata(key, "description", key)

    def has_flag_attrs(self, obj: DataTree) -> bool:
        """
        Test if variable is a mask/flag

        :param obj: variable to test
        :return: true if variable corresponds to a flag
        """
        return "flag_masks" in obj.attrs or "flag_values" in obj.attrs

    def to_flag_dict(self, variable: DataTreeNode, varpath: str) -> OrderedDict[Hashable, Any]:
        """
        Convert variable to OrderedDict {<flag value>: meaning}

        :param variable: flag variable
        :return: flag dict
        """
        flags = OrderedDict()
        if "flag_masks" in variable.attrs:
            keys = variable.attrs["flag_masks"]
        elif "flag_values" in variable.attrs:
            keys = variable.attrs["flag_values"]
        else:
            keys = []

        meanings = variable.attrs.get("flag_meanings", "")
        # check string first because str is an Iterable but we need to split it
        if isinstance(meanings, str):
            meanings = meanings.split()
        elif isinstance(meanings, Iterable):
            pass
            # warnings.warn(f"{varpath}: flag_meanings should be a space separated list, not {type(keys)}")
        else:
            raise NotImplementedError

        descriptions = variable.attrs.get("flag_descriptions", ["" for _ in meanings])

        if isinstance(keys, int):
            warnings.warn(
                f"{varpath}: flag_masks or flag_values is not a valid list: {keys!r}, type:{type(keys)}",
            )
            keys = [keys]

        if not isinstance(keys, list):
            raise ValueError(
                f"{varpath}: flag_masks or flag_values is not a valid list: {keys!r}, type:{type(keys)}",
            )
        for i, key in enumerate(keys):
            try:
                flags[key] = dict(value=key, name=meanings[i])
            except IndexError:
                raise ValueError(
                    f"{varpath}: no flag_meaning found for flag [{i}] {key}",
                )
            else:
                if len(descriptions) == len(keys):
                    flags[key]["description"] = descriptions[i]
                    # TODO: warn user if note the case

        return flags

    def iter_variables(
        self,
        root: DataTree,
        path: str = "",
        exclude_flags: bool = False,
        ellipsis: Ellipsis | None = None,
        recursive: bool = False,
    ) -> Generator[tuple[str, DataTreeNode], None, None]:
        """
        Iterate through variables in a specified path, optionally excluding flags and recursively traversing subtrees.

        Parameters
        ----------
        root : DataTree of Any
            Root of the data tree.
        path : str, optional
            Path to iterate over, by default "".
        exclude_flags : bool, optional
            Whether to exclude flag variables, by default False.
        ellipsis : Ellipsis or None, optional
            Ellipsis object for pruning paths, by default None.
        recursive : bool, optional
            Whether to recursively traverse subtrees, by default False.

        Yields
        ------
        tuple of str, DataTreeNode
            Path and corresponding data tree node.
        """
        if recursive:
            groups = root[path].subtree
        else:
            groups = [root[path]]
        paths = []
        for obj in groups:
            path_coords = []
            path_others = []
            for varname, variable in obj.data_vars.items():
                varpath = Path(obj.path, varname).as_posix()
                if exclude_flags and is_flag_variable(variable):
                    continue
                if self.is_coordinate(root, varpath):
                    path_coords.append(varpath)
                else:
                    path_others.append(varpath)
            paths.extend(sorted(path_others))
            paths.extend(sorted(path_coords))

        if ellipsis:
            for use, path_repr in ellipsis.prune(paths):
                variable = root[use]
                yield use, variable
        else:
            for path in paths:
                yield path, root[path]

    def contains_variables(
        self,
        obj: DataTree,
        exclude_flags: bool = False,
    ) -> bool:
        """
        Determine if the object contains any variables.

        Parameters
        ----------
        obj : DataTree
            Object to check.
        exclude_flags : bool, optional
            Whether to exclude flag variables, by default False.

        Returns
        -------
        bool
            True if variables are present, False otherwise.
        """
        for path, variable in self.iter_variables(
            obj,
            exclude_flags=exclude_flags,
            recursive=True,
        ):
            if exclude_flags and is_flag_variable(variable):
                continue
            return True
        return False

    def contains_flags(self, item: DataTree) -> bool:
        try:
            next(self.iter_flags(item, recursive=False))
        except StopIteration:
            return False
        else:
            return True

    def has_flags(self, obj: DataTree, recursive: bool = True) -> bool:
        try:
            next(self.iter_flags(obj, recursive=recursive))
        except StopIteration:
            return False
        else:
            return True

    def has_attrs(self, obj: DataTree, ignore_list: Iterable[str] | None = None, recursive: bool = True) -> bool:
        if ignore_list is None:
            ignore_list = []
        if hasattr(obj, "subtree") and recursive:
            for group in obj.subtree:
                for key in group.attrs:
                    if key not in ignore_list:
                        return True
        else:
            for key in obj.attrs:
                if key not in ignore_list:
                    return True
        return False

    def iter_flags(
        self,
        root: DataTree,
        path: str = "",
        ellipsis: Ellipsis | None = None,
        recursive: bool = False,
    ) -> Generator[DataTreeNode, None, None]:
        if recursive is True:
            path_and_vars: list[tuple[str, DataTreeNode]] = []
            for group in self.ellipse_groups(root, path, ellipsis=ellipsis):
                for path, variable in self.iter_variables(
                    root,
                    group.path,
                    ellipsis=ellipsis,
                ):
                    path_and_vars.append((path, variable))
        else:
            path_and_vars = list(self.iter_variables(root, path, ellipsis=ellipsis))

        yield from sorted(
            filter(
                lambda item: "flag_meanings" in item[1].attrs,
                path_and_vars,
            ),
            key=lambda item: item[0],  # type: ignore
        )

    def flags(self, root: DataTree, path: str, ellipsis: Ellipsis | None = None) -> list[DataTreeNode]:
        return list(self.iter_flags(root, path, ellipsis=ellipsis))

    def has_data(self, obj: DataTree) -> bool:
        return self.contains_flags(obj) or self.contains_variables(obj) or self.documentation(obj) != ""

    def html_id(self, text: str) -> str:
        return text.replace("/", "_")

    def ellipse_attrs(
        self,
        dic: dict[Any, Any],
        path: str = "/",
        ellipsis: Ellipsis | None = None,
    ) -> Generator[tuple[Any, Any], Any, None]:
        if ellipsis is None:
            yield from dic.items()
        else:
            paths = [f"{path}#{key}" for key in dic]
            ellipsed_data = ellipsis.prune(paths)
            for path, path_repr in ellipsed_data:
                key_repr = path_repr.split("#")[-1]
                key = path.split("#")[-1]
                yield key_repr, dic[key]

    def ellipse_groups(
        self,
        root: DataTree,
        path: str = "",
        ellipsis: Ellipsis | None = None,
    ) -> Generator[DataTreeNode, Any, None]:
        paths = []
        obj = root[path]
        for group in obj.subtree:
            paths.append(group.path)
        paths.sort(key=sort_groups)

        if ellipsis:
            for use, path_repr in ellipsis.prune(paths):
                yield root[use]
        else:
            for path in paths:
                yield root[path]

    def has_ellipsis(
        self,
        product: DataTree,
        ellipsis: Ellipsis | None = None,
    ) -> bool:
        if ellipsis is None:
            return False
        idx = ellipsis.match(product.path)
        if idx is not None:
            return True
        for group in self.ellipse_groups(product, ellipsis=ellipsis):
            idx = ellipsis.match(group.path)
            if idx is not None:
                return True
            for var_path, variable in self.iter_variables(
                product,
                group.path,
                ellipsis=ellipsis,
            ):
                idx = ellipsis.match(var_path)
                if idx is not None:
                    return True
        return False

    def unique_sorted_list(self, lst: list[Any]) -> list[Any]:
        return list(sorted(set(lst)))

    def all_paths(self, obj: DataTree) -> list[str]:
        paths = []
        for subtree in obj.subtree:
            paths.append(subtree.path)
            for var_path, var in self.iter_variables(obj, subtree.path):
                paths.append(var_path)
        return paths

    def attributes_stac_discovery(
        self,
        obj: DataTree,
        exclude_attrs: list[str] | None = None,
    ) -> dict[Hashable, Any]:
        if exclude_attrs is None:
            exclude_attrs = []
        return {k: v for k, v in obj.attrs.get("stac_discovery", {}).items() if k not in exclude_attrs}

    def attributes_stac_extensions(self, obj: DataTree, exclude_attrs: list[str] | None = None) -> list[Any]:
        attrs = self.attributes_stac_discovery(obj)
        return attrs.get("stac_extensions", [])

    def attributes_properties(self, obj: DataTree, exclude_attrs: list[str] | None = None) -> dict[Hashable, Any]:
        if exclude_attrs is None:
            exclude_attrs = []
        return {k: v for k, v in obj.attrs.get("properties", {}).items() if k not in exclude_attrs}

    def attributes_other_metadata(
        self,
        obj: DataTree,
        exclude_attrs: list[str] | None = None,
    ) -> dict[Hashable, Any]:
        if exclude_attrs is None:
            exclude_attrs = []
        attrs = self.attributes_properties(obj, exclude_attrs)
        attrs.update(obj.attrs.get("other_metadata", {}))
        return {k: v for k, v in attrs.items() if k not in exclude_attrs}

    def attributes(self, obj: DataTree, exclude_attrs: list[str] | None = None) -> dict[Hashable, Any]:
        if exclude_attrs is None:
            exclude_attrs = []
        return {k: v for k, v in obj.attrs.items() if k not in exclude_attrs}

    def attribute_desc(self, name: str) -> str:
        return self.html(PROPERTIES_METADATA.get_metadata(name, "description", name))

    def variable_dims(self, dims: list[str], ellipsis: Ellipsis | None = None) -> list[str]:
        if ellipsis:
            coords = []
            for dim in dims:
                if ellipsis.match(dim) is not None:
                    # If a pattern is defined, use it
                    dim = ellipsis.replace(dim)
                else:
                    # Else, search if coordinates exists
                    if not dim.startswith("/coordinates/"):
                        dim = f"/coordinates/{dim}"
                    dim = ellipsis.prune([dim])[0][1]
                    dim = dim[13:]
                    dim = ellipsis.repr_name.get(dim, dim)
                coords.append(dim)
            return coords
        else:
            return dims

    def variable_storage_range(self, variable: DataTreeNode) -> str:
        """
        Extract from _io_config valid_min, valid_max to return **storage** variable range
        (as opposed to  **physical** variable range)
        :param variable:
        :return:
        """
        io = variable.attrs.get("_io_config", {})
        try:
            mini = float(io.get("valid_min"))
        except TypeError:
            mini = None
        try:
            maxi = float(io.get("valid_max"))
        except TypeError:
            maxi = None
        if mini is None or maxi is None:
            return ""
        else:
            return "[%g, %g]" % (mini, maxi)

    def variable_range(self, variable: DataTreeNode) -> str:
        """
        Extract from _io_config valid_min, valid_max, scale_factor and add_offset to compute **physical** variable range
        (as opposed to **storage** variable range)
        :param variable:
        :return:
        """
        io = variable.attrs.get("_io_config", variable.attrs)
        scale_factor = io.get("scale_factor", 1.0)
        add_offset = io.get("add_offset", 0.0)
        try:
            mini = float(io.get("valid_min"))
        except TypeError:
            mini = None
        try:
            maxi = float(io.get("valid_max"))
        except TypeError:
            maxi = None
        mini = (add_offset + mini * scale_factor) if mini is not None else None
        maxi = (add_offset + maxi * scale_factor) if maxi is not None else None
        if mini is None or maxi is None:
            return ""
        else:
            return "[%g, %g]" % (mini, maxi)

    def variable_storage_type(self, variable: DataTreeNode) -> str:
        io = variable.attrs.get("_io_config", variable.attrs)
        return io.get("dtype", variable.encoding.get("dtype", "-"))

    def variable_storage_fillvalue(self, variable: DataTreeNode) -> float | int | None:
        io = variable.attrs.get("_io_config", variable.attrs)
        return io.get("fill_value")

    def filter_variable_attributes(self, attributes: dict[Hashable, Any]) -> dict[Hashable, Any]:
        attrs: dict[Hashable, Any] = {}
        for k in ["standard_name", "units"]:
            if k in attributes:
                attrs[k] = attributes[k]
        io = attributes.get("_io_config", attributes)
        for k in ["fill_value"]:
            if k in io:
                attrs[k] = io[k]
        try:
            attrs["type"] = io["dtype"]
        except KeyError:
            pass
        return attrs

    def product_type(self, root: DataTree) -> str:
        return AttributeHandler(root).get_attr("product:type", default="")

    def is_flag(self, root: DataTree, path: str) -> bool:
        obj = root[path]
        return is_flag_variable(obj)

    def is_coordinate(self, root: DataTree, path: str) -> bool:
        parent_path = Path(path).parent.as_posix()
        try:
            parent = root[parent_path]
        except KeyError:
            coords = []
        else:
            coords = parent.attrs.get("_coordinates", [])
        var = root[path]
        return var.dims == (var.name,) or var.name in coords

    def name(self, root: DataTree, path: str, ellipsis: Ellipsis | None = None) -> str:

        if ellipsis:
            ellipsis_path = self.path(path, ellipsis)
            if ellipsis_path in ellipsis.repr_name:
                return ellipsis.repr_name[ellipsis_path]

        return Path(path).name

    def long_name(self, obj: DataTree, ellipsis: Ellipsis | None = None) -> str:
        return obj.attrs.get("long_name", "??")

    def get_mapping(self, product: Any) -> dict[Hashable, Any]:
        return product._mapping_factory.get_mapping(self.product_type(product))

    def _get_data_mapping(self, product_type: str | None) -> dict[Hashable, Any]:
        """
        if product_type in self._data_mapping:
            return self._data_mapping[product_type]
        else:
            mf = create_mapping_factory(self.mapping_dirpath)
            try:
                mapping = mf.get_mapping(product_type=product_type)
            except (MappingMissingError, MissingArgumentError):
                LOGGER.info(f"No mapping found for {product_type}")
                return {}
            else:
                self._data_mapping[product_type] = {}
                for dmap in mapping.get("data_mapping", []):
                    target = dmap.get("target_path")
                    src = dmap.get("source_path")
                    if target and src:
                        self._data_mapping[product_type][target] = dmap
                return self._data_mapping[product_type]
        """
        raise NotImplementedError

    def legacy_field(self, root: DataTree, obj: DataTree, ellipsis: Ellipsis | None = None) -> str:
        data_mapping = self._get_data_mapping(self.product_type(root))

        if obj.path in data_mapping:
            return data_mapping[obj.path].get("source_path")
        else:
            return ""

    def description(self, root: DataTree, path: str, ellipsis: Ellipsis | None = None, obj: Any = None) -> str:
        if ellipsis:
            ellipsis_path = self.path(path, ellipsis)
            if ellipsis_path in ellipsis.repr_description:
                return ellipsis.repr_description[ellipsis_path]

        if obj is None:
            obj = root[path]

        desc_keys = ["description", "long_name", "documentation"]
        try:
            data = obj.attrs
        except AttributeError:
            for key in desc_keys:
                if hasattr(obj, key):
                    return getitem(obj, key)  # type: ignore
        else:
            return extract_description_from_attrs(data)
        return ""

    def documentation(self, root: DataTree, path: str = "", ellipsis: Ellipsis | None = None) -> str:
        if ellipsis:
            ellipsis_path = self.path(path, ellipsis)
            if ellipsis_path in ellipsis.repr_documentation:
                return ellipsis.repr_documentation[path]

        return root[path].attrs.get("documentation", "")

    def path(self, path: str, ellipsis: Ellipsis | None = None) -> str:
        return ellipsis.path(path) if ellipsis else path

    def to_str(self, text: str, *args: Any, **kwargs: Any) -> str:
        if isinstance(text, list) and not text:
            return ""
        if text is None:
            return ""
        else:
            return escape(str(text))

    def html_links(self, key: str, alias: str | None = None, root: str | None = None) -> str:
        if root is None:
            # TODO: real path management
            root = "../.."
        template_kwargs = {"ROOT": root}
        if alias is None:
            alias = escape(key)
        links = PROPERTIES_METADATA.get_metadata(key, "links", [])
        if isinstance(links, str):
            links = [links]
        if links:
            template = self.jinja_env.from_string(links[0])
            href = template.render(**template_kwargs)
            html = f"""<a href="{href}">{alias}</a>"""
            for i, link in enumerate(links[1:]):
                if isinstance(link, dict):
                    link_alias: str = link.get("alias", key)
                    href = link.get("href", "")
                else:
                    link_alias = f"({i+1})"
                    href = link
                template = self.jinja_env.from_string(href)
                href = template.render(**template_kwargs)
                html += f"""<a href={href}>{escape(link_alias)}</a>"""
            return html
        else:
            return alias

    def html(self, text: str, *args: Any, name: str = "", **kwargs: Any) -> str:
        from sentineltoolbox.autodoc.rendering import render_html_json_as_list

        if isinstance(text, (list, tuple, dict)):
            return render_html_json_as_list(text, name=name)
        else:
            return self.to_str(text, *args, **kwargs)

    def product_property_documentation(self, key: str, value: str | None = None) -> str:
        data = STAC_PROPERTIES.get(key, {})
        properties = ResourceDb(relpath="metadata/properties.json")

        extracted = properties.get_metadata(key, "documentation", "")
        if isinstance(value, dict) and "units" in value:
            extracted += f'<br>unit in {value["units"]}'

        return data.get("documentation", extracted)

    def product_property(self, key: str, value: Any) -> str:
        if not isinstance(value, dict):
            value = {}
        properties = ResourceDb(relpath="metadata/properties.json")
        extracted = value.get("long_name", properties.get_metadata(key, "description", ""))
        return STAC_PROPERTIES.get(key, {}).get("description", escape(extracted))


EXTRACTOR = DataExtractor()
