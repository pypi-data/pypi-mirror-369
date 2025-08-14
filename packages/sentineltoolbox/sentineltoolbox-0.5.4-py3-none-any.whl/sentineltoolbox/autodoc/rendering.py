import logging
from dataclasses import dataclass
from html import escape
from pathlib import Path
from pprint import pformat
from typing import Any, Hashable, Iterable, Optional

import xarray
from jinja2 import Environment, PackageLoader
from xarray import DataTree

from sentineltoolbox.autodoc.ellipsis import Ellipsis
from sentineltoolbox.autodoc.sphinxenv import get_source_path
from sentineltoolbox.autodoc.sphinxenv import get_static_path as get_static_path
from sentineltoolbox.models.eopf_payload import EopfPayload
from sentineltoolbox.models.tasktable import TaskTable
from sentineltoolbox.resources.data import (
    DATAFILE_METADATA,
    TERMS_METADATA,
    fields_headers,
)

from ..models.lazydatadir import LazyDataDir
from ..readers.resources import load_resource_file
from .constants import DisplayMode, to_display_mode
from .dataextractor import EXTRACTOR, DataExtractor

logger = logging.getLogger("sentineltoolbox")

env_html = Environment(
    loader=PackageLoader("sentineltoolbox.resources.autodoc"),
    autoescape=True,
)


env_latex = Environment(
    loader=PackageLoader("sentineltoolbox.resources.autodoc"),
    block_start_string="<BLOCK>",
    block_end_string="</BLOCK>",
    variable_start_string="<VAR>",
    variable_end_string="</VAR>",
    autoescape=True,
)


def truncate(obj: Any, limit: int = 2, length: int = 20) -> str:
    """Returns a truncated string representation of large objects.

    Args:
        obj (Any): The object to truncate.
        limit (int): The maximum number of elements or characters to display.

    Returns:
        str: A formatted and truncated string representation of the object.
    """
    if isinstance(obj, dict):
        # Truncate the dictionary to the specified number of items
        truncated = {k: truncate(obj[k]) for k in list(obj)[:limit]}
        return pformat(truncated) + ", ...} (%d elements)" % len(obj) if len(obj) > limit else pformat(truncated)
    elif isinstance(obj, list):
        # Truncate the list to the specified number of items
        truncated = [truncate(item) for item in obj[:limit]]  # type: ignore
        return pformat(truncated + ["..."]) if len(obj) > limit else pformat(truncated)  # type: ignore
    elif isinstance(obj, str):
        # Truncate the string if it exceeds the specified length
        return obj[:length] + "..." if len(obj) > length else obj
    else:
        # For other types, simply return the string representation
        return truncate(str(obj), limit=limit, length=length)


def print_summary(obj: Any, limit: int = 2, length: int = 20) -> None:
    """Prints a truncated representation of the object.

    Args:
        obj (Any): The object to display in truncated form.
        limit (int): The maximum number of elements or characters to display.
    """
    print(truncate(obj, limit, length))


class IpythonDisplayableObject:
    def __init__(self, html: str | None = None, latex: str | None = None) -> None:
        self.html = html
        self.latex = latex

    def _repr_html_(self) -> str:
        if self.html is None:
            return ""
        else:
            return self.html

    def _repr_latex_(self) -> str:
        if self.latex is None:
            return ""
        else:
            return self.latex


def dump_eopf(obj: Any, static_path: Path | None = None) -> Path:
    from eopf.product.eo_variable import EOVariable

    if static_path is None:
        static_path = get_static_path(get_source_path())

    eopf_link = Path(static_path, "eopf", obj.product.name, obj.path[1:] + ".html")
    eopf_link.parent.mkdir(parents=True, exist_ok=True)
    if not eopf_link.exists():
        with open(eopf_link, "w", errors="ignore") as f:
            f.write(obj._repr_html_())

    if not isinstance(obj, EOVariable):
        for child in obj.values():
            dump_eopf(child)

    return Path("<STATIC_PATH_TO_REPLACE>", "eopf", obj.product.name)


def _jinja_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    kwargs["DisplayMode"] = kwargs.get("DisplayMode", DisplayMode)
    kwargs["method"] = kwargs.get("method", None)
    kwargs["mode"] = kwargs.get("mode", DisplayMode.rich)
    kwargs["extractor"] = kwargs.get("extractor", EXTRACTOR)

    return kwargs


def render_html_str_as_warning(text: str) -> str:
    return rf"<div class='warning'>{escape(text)}</div>"


def render_html_str_as_mathjax(text: str) -> str:
    """
    Return HTML bloc that will be interpreted as LaTeX instruction

    :param text: LaTeX string without '$'
    :return:
    """
    return '<span class="math notranslate nohighlight">\\(%s\\)</span>' % text


def render_html_list_as_table(obj: list[Any], **kwargs: Any) -> str:
    template = env_html.get_template("tpl_table_list.html")
    return template.render(obj=obj, kwargs=_jinja_kwargs(kwargs), **kwargs)


def list_key(item: Any, i: str = "") -> Any:
    if isinstance(item, (list, tuple)) and len(item):
        return item[0]
    else:
        return item


def list_value(item: Any) -> str:
    if isinstance(item, (list, tuple)) and len(item) > 1:
        return ", ".join([str(i) for i in item[1:]])
    else:
        return ""


def list_sep(item: Any) -> str:
    if isinstance(item, (list, tuple)) and len(item) > 1:
        return ": "
    else:
        return ""


def render_html_list_as_list(obj: list[Any], **kwargs: Any) -> str:
    template = env_html.get_template("tpl_ul_list.html")
    kwargs["key"] = list_key
    kwargs["value"] = list_value
    kwargs["sep"] = list_sep
    return template.render(obj=obj, kwargs=_jinja_kwargs(kwargs), **kwargs)


def render_html_list_as_product_summary(obj: list[str], **kwargs: Any) -> str:

    fields = kwargs.get("fields", ["name", "description"])
    kwargs["headers"] = kwargs.get("headers", fields_headers(fields))
    kwargs["identifier"] = kwargs.get("identifier", "table_" + "_".join(fields))
    lst = DATAFILE_METADATA.summary(obj, fields)
    return render_html_list_as_table(lst, **kwargs)


def render_html_list_as_term_summary(obj: list[str], **kwargs: Any) -> str:

    fields = kwargs.get("fields", ["name", "description"])
    kwargs["headers"] = kwargs.get("headers", fields_headers(fields))
    kwargs["identifier"] = kwargs.get("identifier", "table_" + "_".join(fields))
    lst = TERMS_METADATA.summary(obj, fields)
    return render_html_list_as_table(lst, **kwargs)


def render_polygon(array: Any, **kwargs: Any) -> str:
    """

    Alternative:
    from shapely.geometry import Polygon
    return Polygon(obj["coordinates"][0])._repr_svg_()

    WARNING: this code kills some jupyter kernel!
    """
    from io import StringIO

    import matplotlib.pyplot as plt

    a = array
    plt.figure(figsize=(4, 3))
    plt.axis("equal")
    plt.fill(a[:, 0], a[:, 1])

    s = StringIO()
    plt.tight_layout()
    plt.savefig(s, format="svg", bbox_inches="tight")
    plt.close()
    return s.getvalue()


def geometry(obj: Any, plot: bool = False) -> str:
    import numpy as np

    array = np.array(obj["coordinates"][0])
    if plot:
        return render_polygon(array, **obj)
    else:
        return f"{array.dtype} array of shape {array.shape}"


"""
Band Object, see https://github.com/stac-extensions/eo#band-object
"""


@dataclass(frozen=True)
class MetadataIdentifier:
    name: str
    attributes: tuple[str, ...]
    mandatory: tuple[str, ...]


STAC_DEFS = load_resource_file("metadata/STAC/stac_def.json")

FIELDS_S2_BAND = (
    "bandwidth",
    "central_wavelength",
    "onboard_compression_rate",
    "onboard_integration_time",
    "physical_gain",
    "spectral_response_step",
    "spectral_response_values",
    "units",
    "wavelength_max",
    "wavelength_min",
)


METADATA_STAC_BAND_OBJECT = MetadataIdentifier(
    "eo:bands",
    tuple(STAC_DEFS["eo:bands"].keys()),
    ("center_wavelength",),
)

METADATA_S2 = MetadataIdentifier(
    "eo:bands",
    tuple(STAC_DEFS["eo:bands"].keys()),
    ("bandwidth",),
)
FIELDS_GEOMETRY = ("coordinates", "type")
METADATA_GEOMETRY = MetadataIdentifier("geometry", FIELDS_GEOMETRY, FIELDS_GEOMETRY)

dict_tpl = {
    METADATA_STAC_BAND_OBJECT: "tpl_dict_STAC_band_object.html",
    METADATA_S2: "tpl_dict_S2_band.html",
    METADATA_GEOMETRY: geometry,
}
dict_converter = {metadata.name: metadata for metadata in dict_tpl}


def is_iterable(obj: Any) -> bool:
    return isinstance(obj, (list, tuple, type({}.items())))


def iterable_key(item: Any, i: str = "") -> Any:
    if is_iterable(item):
        # If couple, use first element as key
        if len(item) == 2:
            return item[0]
        else:
            return ""
    elif isinstance(item, dict):
        return item.get("name", i)
    else:
        return ""


def iterable_value(item: Any) -> Any:
    if is_iterable(item):
        # If couple, use second element as value
        if len(item) == 2:
            return render_html_json_as_list(item[1])
        else:
            return ", ".join([render_html_json_as_list(value) for value in item])
    elif isinstance(item, dict):
        if "name" in item:
            del item["name"]
        return render_html_json_as_list(item)
    else:
        return str(item)


def render_html_json_as_list(
    obj: dict[Hashable, Any] | list[Any],
    name: str = "",
    **kwargs: Any,
) -> str:
    kwargs["key"] = iterable_key
    kwargs["value"] = iterable_value
    kwargs["sep"] = list_sep

    if isinstance(obj, dict):
        # check if custom template is associated to this kind of dict

        for identifier, converter in dict_tpl.items():
            match = (name == "" or name == identifier.name) and frozenset(
                identifier.mandatory,
            ) <= frozenset(obj.keys())
            if match:
                if isinstance(converter, str):
                    template = env_html.get_template(converter)
                    kwargs = _jinja_kwargs(kwargs)
                    return template.render(obj=obj, kwargs=kwargs, **kwargs)
                else:
                    return converter(obj)  # type: ignore

        # No custom template, use generic render
        return render_html_json_as_list([(k, v) for k, v in obj.items()])

    elif is_iterable(obj):
        template = env_html.get_template("tpl_ul_list.html")
        kwargs = _jinja_kwargs(kwargs)
        return template.render(obj=obj, kwargs=kwargs, **kwargs)
    else:
        return str(obj)


def render_html_str_as_mermaid(text: str) -> str:
    return f"""<div class="mermaid">
    {text}
    </div>"""


def _add_ellipsis(kwargs: Any) -> Ellipsis | None:
    ellipsis_patterns = kwargs.get("ellipsis_patterns", [])
    ellipsis_variables = kwargs.get("ellipsis_variables", None)
    ellipsis = kwargs.get("ellipsis")
    if ellipsis_patterns and ellipsis is None:
        ellipsis = Ellipsis(patterns=ellipsis_patterns, variables=ellipsis_variables)
    kwargs["ellipsis"] = ellipsis
    return ellipsis


def render_html_xarray_dataset(obj: xarray.Dataset, *args: Any, **kwargs: Any) -> str:
    template = env_html.get_template("tpl_PDFS_table_xarraydataset.html")
    return template.render(obj=obj, kwargs=_jinja_kwargs(kwargs), **kwargs)


def render_html_datatree_as_table(obj: DataTree, *args: Any, **kwargs: Any) -> str:
    autodoc_conf = load_resource_file("autodoc.json")

    kwargs["method"] = kwargs.get("method", autodoc_conf.get("eoproduct_method", "compact"))
    kwargs["mode"] = kwargs.get("mode", to_display_mode(autodoc_conf.get("display_mode", "rich")))

    attributes_to_show = autodoc_conf.get("attributes_to_show", [])
    attributes_to_show.extend(kwargs.get("attributes_to_show", []))
    kwargs["attributes_to_show"] = list(sorted(set(attributes_to_show)))

    attributes_to_ignore = autodoc_conf.get("attributes_to_ignore", [])
    attributes_to_ignore.extend(kwargs.get("attributes_to_ignore", []))
    kwargs["attributes_to_ignore"] = list(sorted(set(attributes_to_ignore)))

    template = env_html.get_template("tpl_PDFS_table_datatree.html")
    _add_ellipsis(kwargs)
    return template.render(obj=obj, kwargs=_jinja_kwargs(kwargs), **kwargs)


def render_html_legacy_summary(obj: Any, *args: Any, **kwargs: Any) -> str:
    template = env_html.get_template("tpl_PDFS_legacy_information.html")
    _add_ellipsis(kwargs)
    return template.render(obj=obj, kwargs=_jinja_kwargs(kwargs), **kwargs)


def render_html_tasktable_as_table(obj: TaskTable, *args: Any, **kwargs: Any) -> str:
    template = env_html.get_template("tpl_json_tasktable.html")
    return template.render(obj=obj, json=obj, kwargs=_jinja_kwargs(kwargs), **kwargs)


def render_html_payload_as_mermaid_diag(
    obj: EopfPayload,
    *args: Any,
    **kwargs: Any,
) -> str:
    from sentineltoolbox.models.eopf_payload import render_mermaid_diagram_from_payload

    mermaid = render_mermaid_diagram_from_payload(obj, orientation="TB")
    return render_html_str_as_mermaid(mermaid)


def render_html_datafile_format_summary(dpr_name: str, *args: Any, **kwargs: Any) -> str:
    metadata = DATAFILE_METADATA.get_metadata(dpr_name)
    if not metadata:
        return f"<div class='error'>No data format information for \"{dpr_name}\"</div>"

    if metadata.get("ext", ".zarr") == ".json":
        fmt = "JSON"
    else:
        fmt = "zarr"

    html = f"""
    File format: {fmt}<br>
    """
    return html


def render_html_datatree_as_datafile_format_summary(xdt: DataTree, *args: Any, **kwargs: Any) -> str:
    ptype = EXTRACTOR.product_type(xdt)
    return render_html_datafile_format_summary(ptype, *args, **kwargs)


class GenericDataFormatter:
    """
    Class to generate rich text (HTML, LaTeX, ...) from Python object.
    You can render all type of objects. To do that, you only need to add a tuple, following one of these convention
    * (class, method, renderer)
    * (class, renderer)

    Match criteria:
    * class: a python class. If object to display is instance of this class and method match,
      call renderer function on it
    * method: str: a string describing method used to display object.
      For example, an array could be rendered as "plot" or "table".
      Method can be used to distinguish these two cases. If method is not defined

    Renderer:
    * renderer(obj: Any, *args, **kwargs)-> str: method that generate a str representation of object.
      Representation can be HTML, LaTeX, ... it depends on Generator you want to associate with
      * kwargs["mode"]: see :meth:`GenericDataFormatter.render`
    """

    def __init__(self, formatters: Iterable[Any] | None = None) -> None:
        self.extractor = DataExtractor()
        if formatters is None:
            formatters = []  # Functions used by ipython.display to render classes
        self.formatters = [formatter for formatter in formatters]

    def _notimplemented(self, *args: Any, **kwargs: Any) -> str:
        raise NotImplementedError(
            f"Generator {self.__class__.__name__} not implemented for {args} {kwargs}",
        )

    def register(self, cls: Any, function: Any, method: Any = None) -> None:
        """_summary_

        Parameters
        ----------
        cls
            class to register
        function
            function use to format instances of 'cls'
        method, optional
            to be compatible with IPython notebook, method must be None(default)
        """
        if method is None:
            self.formatters.append((cls, function))
        else:
            self.formatters.append((cls, method, function))

    def warning(self, text: str) -> str:
        return text

    def ipython_install(self, type: str = "text/html") -> None:
        try:
            from IPython.core.getipython import get_ipython
        except ImportError:
            pass
        else:
            ipython = get_ipython()
            if ipython is not None:
                ipy_formatter = ipython.display_formatter.formatters[type]
                for formatter in self.formatters:
                    if len(formatter) == 2:
                        renderer_cls, renderer_func = formatter
                        ipy_formatter.for_type(renderer_cls, renderer_func)

    def render(
        self,
        obj: Any,
        method: str | None = None,
        mode: Optional[DisplayMode] = None,
        **kwargs: Any,
    ) -> str:
        """
        :param obj:
        :param method: if different method are proposed, use this keyword to specify which one you want to use
        :param mode: select display mode.
            * Mode.text: raw text without style
            * Mode.rich: text with styles
            * Mode.dev: trext with developer and debug information (for example, class name)
            If not set, use global configuration
        :param kwargs:
        :return:
        """
        if mode is None:
            mode = DisplayMode.rich
        if isinstance(mode, str):
            mode = DisplayMode[mode]

        template_args: dict[str, Any] = {}
        template_args["method"] = method
        template_args["mode"] = mode
        template_args["DisplayMode"] = DisplayMode
        template_args["extractor"] = self.extractor

        render_args = {}
        render_args.update(kwargs)
        render_args.update(template_args)

        # EOPF Objects
        for formatter in self.formatters:
            if len(formatter) == 3:
                formatter_cls, format_method, formatter_func = formatter
            elif len(formatter) == 2:
                formatter_cls, formatter_func = formatter
                format_method = None
            else:
                raise NotImplementedError(f"{formatter}")

            method_match = method == format_method or format_method is None
            if not method_match:
                continue

            if isinstance(obj, formatter_cls):
                return formatter_func(obj, **render_args)
            else:
                continue
        else:
            return self._notimplemented(obj, **render_args)


class HtmlDocFormatter(GenericDataFormatter):
    """
    To mix LaTeX and HTML, use latex method.
    html_str = "Equation: " + EOHtmlGenerator.latex("\\sqrt(2)")
    Depending on context, it may be necessary to escape HTML codes:
    from html import escape
    escape(html_str)
    """

    def __init__(self) -> None:
        super().__init__()
        self.formatters = [
            # (class to render, render method, renderer)
            # or (class, renderer)
            (str, "datafile_format_summary", render_html_datafile_format_summary),
            (list, "table", render_html_list_as_table),
            (list, "product_summary", render_html_list_as_product_summary),
            (list, "term_summary", render_html_list_as_term_summary),
            (list, "list", render_html_list_as_list),
            # keep EOProduct before EOGroup because EOProduct is an instance of EOGroup
            (DataTree, "datafile_format_summary", render_html_datatree_as_datafile_format_summary),
            (DataTree, render_html_datatree_as_table),
            (TaskTable, render_html_tasktable_as_table),
            (EopfPayload, render_html_payload_as_mermaid_diag),
            (xarray.Dataset, render_html_xarray_dataset),
        ]


class IpythonHtmlFormatter(GenericDataFormatter):
    def __init__(self) -> None:
        super().__init__()
        self.formatters = [
            (TaskTable, render_html_tasktable_as_table),
        ]


HTML = HtmlDocFormatter()
IPYTHON_HTML = IpythonHtmlFormatter()


def render(obj: Any, method: str | None = None, **kwargs: Any) -> IpythonDisplayableObject:
    html_generator = kwargs.get("html_generator", HTML)

    ipy_obj = IpythonDisplayableObject(
        html=html_generator.render(obj, method, **kwargs),
    )
    return ipy_obj


def display(obj: Any, method: str | None = None, **kwargs: Any) -> None:
    try:
        ipy_obj = render(obj, method, **kwargs)
    except NotImplementedError:
        # TODO: use logger print(f"No render function for {type(obj)}. Use IPython.display")
        ipy_obj = obj
    try:
        from IPython.display import display as ipy_display
    except ImportError:
        logger.warning("Please install IPython to use this function")
    else:
        ipy_display(ipy_obj)


def display_product(lazydatadir: LazyDataDir, key: str, **kwargs: Any) -> None:
    try:
        product = lazydatadir[key]
    except KeyError:
        print(f"{key} not available")
    except Exception as e:
        print(f"Error {e} while loading {key}")
    else:
        # N_MEASUREMENTS = len(list(EXTRACTOR.iter_variables(EOPRODUCT.measurements)))
        # glue("N_MEASUREMENTS", N_MEASUREMENTS)
        # Product is composed of {glue:}`N_MEASUREMENTS` measurement variables
        display(product, **kwargs)
        try:
            path = product.url
        except AttributeError:
            pass
        else:
            print("File used to generate documentation")
            if str(path).startswith("s3"):
                print(path)
            else:
                print(path.name)
