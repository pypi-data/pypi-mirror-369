"""
No public API here.
Use root package to import public function and classes
"""

__all__: list[str] = []


from typing import Any

import xarray as xr

from sentineltoolbox.converters import convert_datatree_to_dataset
from sentineltoolbox.readers.open_datatree import open_datatree
from sentineltoolbox.typedefs import Credentials, PathMatchingCriteria, PathOrPattern


def open_dataset(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> xr.Dataset:
    """
    Function to open flat data (json ADF, zarr ADF, ...) from bucket or local path and open it as :obj:`xarray.Dataset`

    .. note::

        Data are lazy loaded. To fully load data in memory, prefer :obj:`~sentineltoolbox.api.load_dataset`

    >>> open_dataset("s3://s2-input/Auxiliary/MSI/S2A_ADF_REOB2_*.json") # doctest: +SKIP

    Optional arguments credentials, match_criteria, ... must be specified by key.

    Parameters
    ----------
    Parameters common to all open_* and load_*:
        see :obj:`sentineltoolbox.typedefs` for details on
            - path_or_pattern
            - credentials
            - match_criteria
    """
    xdt = open_datatree(path_or_pattern, credentials=credentials, match_criteria=match_criteria, **kwargs)
    return convert_datatree_to_dataset(xdt)


def load_dataset(
    path_or_pattern: PathOrPattern,
    *,
    credentials: Credentials | None = None,
    match_criteria: PathMatchingCriteria = "last_creation_date",
    **kwargs: Any,
) -> xr.Dataset:
    """
    Function to load flat data (json ADF, zarr ADF, ...) from bucket or local path and load it as :obj:`xarray.Dataset`

    .. warning::
        all data are loaded in memory. Use it only for small readers.

        To lazy load data, prefer :obj:`~sentineltoolbox.api.open_dataset`


    >>> load_dataset("s3://s2-input/Auxiliary/MSI/S2A_ADF_REOB2_*.json") # doctest: +SKIP

    Optional arguments credentials, match_criteria, ... must be specified by key.

    Parameters
    ----------
    Parameters common to all open_* and load_*:
        see :obj:`sentineltoolbox.typedefs` for details on
            - path_or_pattern
            - credentials
            - match_criteria
    """
    # check if path is a direct path or a pattern
    # if pattern:
    #   -> list all paths matching patterns
    #   -> filter paths using match criteria
    #   -> keep only one path
    # check if path targets a s3 bucket

    # If credentials not passed by user tries to extract it from env and user config
    # if is_bucket and credentials is None:
    #    credentials = UserCredentialsDataclass.from_env()

    # check if path exists

    # check if JSON or Zarr

    # load adf

    # convert to dict of Dataset

    # return dict
    return xr.Dataset()
