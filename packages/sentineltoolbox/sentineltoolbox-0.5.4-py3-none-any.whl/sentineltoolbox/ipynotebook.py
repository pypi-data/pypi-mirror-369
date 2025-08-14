from typing import Literal

from xarray import DataTree


def configure_notebook(*, output_mode: Literal["auto", "text"] = "auto") -> None:
    # trace dask compute
    # define cell output types
    # css style
    try:
        ipython = get_ipython()  # type: ignore
    except NameError:
        pass
    else:
        if output_mode == "text":
            ipy_formatter = ipython.display_formatter.formatters["text/html"]
            ipy_formatter.for_type(DataTree, lambda xdt: f"<pre>{str(xdt)}</pre>")
