from typing import Any

import xarray as xr


def init_jupyter_env(**kwargs: Any) -> None:
    xr.set_options(display_expand_attrs=False)
