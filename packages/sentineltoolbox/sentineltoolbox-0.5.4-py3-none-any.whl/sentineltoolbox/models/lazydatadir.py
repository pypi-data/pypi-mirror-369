import logging
from abc import ABC
from datetime import datetime
from functools import reduce
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any, Generator, Iterable, List

from sentineltoolbox.exceptions import LoadingDataError
from sentineltoolbox.filesystem_utils import get_universal_path
from sentineltoolbox.models.upath import PathFsspec
from sentineltoolbox.typedefs import DataPath, T_DataPath, T_Paths

logger = logging.getLogger("sentineltoolbox")


def html_header(lazydatadir: "LazyDataDir") -> str:
    paths: str = ", ".join([repr(path.url) for path in lazydatadir.root_paths])
    html = r"""
        <style>
        .info {
            color: grey;
            font-size: smaller;
        }
        </style>"""
    html += f"<div class='info'>Search paths: {paths}</div>"
    return html


def render_html_lazydatadir_as_table(lazydatadir: "LazyDataDir", **kwargs: Any) -> str:
    data_filter = kwargs.get("data_filter")
    html = html_header(lazydatadir)
    html += "<ul>"
    for k, v in lazydatadir.map().items():
        isgroup: bool = (
            isinstance(v, lazydatadir.__class__)
            or isinstance(v, (Path, DataPath))
            and lazydatadir.data_filter.is_group_path(v)
        )
        kstr = f"[{k}]" if isgroup else k
        if k in lazydatadir:
            data = lazydatadir[k]
            if data_filter:
                html += f"<li>{kstr}: {data_filter.to_html(data)}</li>"
            else:
                try:
                    html += f"<li>{kstr}: {data._repr_html_()}</li>"
                except AttributeError:
                    html += f"<li>{kstr}: {str(data)}</li>"
        else:
            html += f"<li>{kstr} <span class='info'>({v}, NOT LOADED)</span></li>"
    html += "</ul>"
    if lazydatadir._invalid_key:
        html += "Ignored keys (path or data not readable)<ul>"
        for k in lazydatadir._invalid_key:
            html += f"<li>{k}</li>"
        html += "</ul>"
    return html


def render_html_lazydatadir_as_pandas_table(lazydatadir: "LazyDataDir", recursive: bool = False, **kwargs: Any) -> str:
    html = html_header(lazydatadir)
    from pandas import DataFrame, Timestamp

    try:
        import itables.options as opt  # noqa: F401

    except ImportError:
        logger.info("You can install itables to get interactives tables")

    keys: list[str] = []
    formats: list[str] = []
    dates: list[Timestamp] = []
    data: list[str] = []

    map = lazydatadir.map()
    for k in lazydatadir.iter_groups(recursive=False):
        keys.append(k)
        formats.append("n/a")
        # types.append("folder")

    for k in lazydatadir.iter_data(recursive=False):
        keys.append(k)
        formats.append("?")
    # types.append(v.__class__.__name__)

    for k in keys:
        v = map[k]
        try:
            stat = v.stat()  # type: ignore
        except AttributeError:
            ts = Timestamp(datetime.now())
        else:
            ts = Timestamp(datetime.fromtimestamp(stat.st_mtime))
        dates.append(ts)

        if isinstance(v, (Path, DataPath, PathFsspec)):
            data.append(v.name)
        elif isinstance(v, LazyDataDir):
            data.append("Directory")
        else:
            data.append(f"{k} loaded as {type(v).__name__!r}")
            # try:
            #    data.append(v._repr_html_().replace("\n", ""))
            # except AttributeError:
            #    data.append(str(v))

    df = DataFrame(
        {
            "key": keys,
            "format": formats,
            # "type": types,
            # "date": dates,
            "path/product": data,
        },
    )
    try:
        from itables import to_html_datatable  # type: ignore
    except ImportError:
        return html + df._repr_html_()  # type: ignore
    else:
        return html + to_html_datatable(
            df,
            columnDefs=[
                {
                    "width": "10%",
                    "targets": [
                        1,
                    ],
                },  # [1, 2, 3]
                {
                    "width": "35%",
                    "targets": [
                        0,
                    ],
                },  # [0, 2, 4]
            ],
        )


class DataFilter:
    """
    A DataFilter ...
      - filters inputs, for example remove invalid data or file that not correspond to expected data
      - is able to load data and return python object representing this data. See :meth:`open_data`.
      - possibly change representation of file and directories. See :meth:`data_key` and :meth:`group_key`.
    """

    def data_keys(self, path: T_DataPath) -> list[str]:
        """
        Generate a list of keys from data path.
        Override this function to use simplified key instead of path name:
        For example S3A_ADF_OLINS_20160216T000000_20991231T235959_20231031T104035.zarr -> [S3A_ADF_OLINS]

        Default implementation: return one item list containing path name
        """
        return [path.name]

    def group_keys(self, path: T_DataPath) -> list[str]:
        """
        Generate a key from data path.
        Override this function to use simplified key instead of path name:

        Default implementation: return path name
        """
        return [path.name]

    def is_group_path(self, path: T_DataPath) -> bool:
        """
        Return True if path target a place (directory, bucket, ...) containing data, else return False.
        For example ...
        a FileSystemDataDir will return True if path is a directory.
        for xarray data browser, a directory ending with .zarr is not considered as group path but is consider as data

        A path can be neither "data" nor "group" and is considered as invalid path

        Default implementation: True if path is a directory
        """
        return path.is_dir()

    def is_data_path(self, path: T_DataPath) -> bool:
        """
        Return True if path target a supported data, else return False.
        For example, an ImageDataDir will return True for *.png, *jpg, ... but return False for *.txt, *.csv, ...
        A valid data path can be what you want. For example .zarr data are directories, not files.

        A path can be neither "data" nor "group" and is considered as invalid path

        Default implementation: True if path is a file
        """
        return path.is_file()

    def open_data(self, path: T_DataPath) -> Any:
        """
        Must raise ErrorLoadingData if data cannot be loaded (seems to be valid but cannot be open)

        Default implementation: return absolute path to data. Keep this if you want to let user manage data.
        """
        return path

    def paths(self, paths: Iterable[T_DataPath]) -> list[T_DataPath]:
        """
        Return filtered list of paths.

        For example, use this function to keep only most recent files.
        """
        return [p for p in paths]

    def to_html(self, data: Any) -> str:
        try:
            return data._repr_html_()
        except AttributeError:
            return str(data)


class ExtensionFilter(DataFilter):
    """
    Filter data based on extension list:
    A path is considered as valid data if it match extension.
    """

    # docstr-coverage: inherited
    def __init__(self, extensions: list[str]) -> None:
        """
        Parameters
        ----------
        extensions
            list of extension. For example [".tar.gz", ".zip"]
        """
        self.extensions = extensions
        super().__init__()

    # docstr-coverage: inherited
    def is_data_path(self, path: T_DataPath) -> bool:
        suffixes = "".join(Path(str(path)).suffixes)
        for ext in self.extensions:
            if suffixes.endswith(ext):
                return True
        return False


class LazyDataDir(ABC, dict[str, Any]):
    """
    "Dict like" to store data lazily: Subdir and Data are loaded only on demand

    Nevertheless you can browse tree using ...
      - meth:`keys`: return all available keys as expected
      - meth:`map`: return a dict key -> path
      - In jupyter notebook, you can use default object representation

    Use [] or meth:`get` to get and load data
    Use meth:`load` to load all direct data. Use recursive to load all data in all subdirectories. Can be very slow!

    Behind the scene,
      - data loading is delegated to DataFilter
      - iteration on data is delegated to DataWalker and filtered by DataFilter

    By default, local file system ("file://path" or "/path") and S3 buckets ("s3://path") are supported
    """

    def __init__(
        self,
        paths: (
            T_Paths | PathFsspec | Iterable[PathFsspec] | Traversable | Iterable[Traversable] | dict[str, Path | str]
        ),
        data_filter: DataFilter = DataFilter(),
        **kwargs: Any,
    ) -> None:
        """_summary_

        Parameters
        ----------
        paths
            paths containing data
        data_filter, optional
            DataFilter you want to use to identify and open data
        walker_cls, optional
            dict protocol->DataWalker. For example: {"zip": ArchiveDataWalker}. See :func:`urllib.urlparse` scheme
            For local filesystem, use "file" protocol. Internally, "" is an alias for "file".
        options, optional
            pass options to walker constructors. options is a dict path->walker kwargs.
            For example: {
                "ftp://ftp.example.org": {"user": "myname", "passwd": "xxxx"},
                "ftp://ftp.othersite.fr": {"user": ...}
                }
        """
        super().__init__()

        self.data_filter: DataFilter = data_filter

        # store all options in kwargs to simplify recursive creation of LazyDataDir
        self.kwargs = kwargs
        self.kwargs["data_filter"] = data_filter

        # dict: key -> data path (PathFsspec if not loaded else Any if data or LazyDataDir if data dir)
        self.paths: dict[str, PathFsspec | Any] = {}
        self.root_paths: list[PathFsspec] = []  # dict of root path to iterate on to find data
        if isinstance(paths, dict):
            for key, path in paths.items():
                self.paths[key] = get_universal_path(path)
        else:
            if isinstance(paths, (list, set, tuple)):
                for path in paths:
                    self.register_path(path, **kwargs)
            elif isinstance(paths, (Path, str, PathFsspec, Traversable)):
                self.register_path(paths, **kwargs)
            else:
                raise TypeError(f"LazyDataDir doesn't support path(s) of type {type(paths)}.")

        # store other inputs
        self.kwargs = kwargs

        # define internal data
        self._invalid_path: list[T_DataPath] = []
        self._invalid_key: list[str] = []
        self._loaded: bool = False
        self._aliases: dict[str, str] = {}
        self._identical_data: dict[str, list[str]] = {}

    def register_path(self, path: Path | str | PathFsspec | Traversable, **kwargs: Any) -> None:
        if isinstance(path, DataPath):
            pathstr = path.url
        else:
            pathstr = str(path)
        if pathstr in self.paths:
            return

        if isinstance(path, DataPath):
            self.root_paths.append(path)
        else:
            try:
                upath = get_universal_path(path, **kwargs)
            except ValueError:
                logger.warning(f"path {path} is not valid and has been ignored")
            else:
                self.root_paths.append(upath)

    def clear(self) -> None:
        """clear all loaded data"""
        super().clear()
        self._invalid_path.clear()
        self._invalid_key.clear()
        self._loaded = False

    def walk(self) -> Generator[Any | tuple[Any, Any], Any, None]:
        self.load()
        for k, v in self._items():
            if isinstance(v, LazyDataDir):
                yield from v.walk()
            else:
                yield (k, v)

    def load(self, recursive: bool = False, force: bool = False) -> None:
        """_summary_

        Parameters
        ----------
        recursive, optional
            if True, load all data recursively. Can be very slow and/or memory consuming
        force, optional
            if True, force to reload data
        """
        if self._loaded is False or force:
            self._loaded = True
            for k in self.keys():
                try:
                    v = self.get_data(k, force=force)
                except LoadingDataError:
                    pass
                else:
                    if isinstance(v, LazyDataDir) and recursive:
                        v.load(recursive=recursive, force=force)

    def get_data(self, key: str, force: bool = False) -> Any:
        """
        return data associated to key. If force, reload data at each call.
        """
        if force is True and key in self:
            del self[key]
        return self[key]

    def __missing__(self, key: str) -> Any:
        # Not in dict because invalid
        # but user tries explicitly to load it => exception
        if key in self._invalid_key:
            raise LoadingDataError(key)

        # load map to get associated path
        map = self.map()
        if key in map:
            refkey = self._aliases[key]
            path = map[refkey]
            if self.data_filter.is_data_path(path):
                try:
                    data = self.data_filter.open_data(path)
                except LoadingDataError:
                    for key in self._identical_data[refkey]:
                        self._invalid_key.append(key)
                        self._invalid_path.append(path)
                    raise LoadingDataError(path)
                else:
                    for key in self._identical_data[refkey]:
                        self[key] = data
                    return data
            elif self.data_filter.is_group_path(path):
                datadir = self.__class__(str(path), **self.kwargs)
                for key in self._identical_data[refkey]:
                    self[key] = datadir
                return datadir
            else:
                for key in self._identical_data[refkey]:
                    self._invalid_key.append(key)
                    self._invalid_path.append(path)
                raise LoadingDataError(path)
        else:
            # Not in map, not considered as invalid
            # Sorry, really this key doesn't exists
            raise KeyError(key)

    def __repr__(self) -> str:
        paths = ", ".join([repr(path.url) for path in self.root_paths])
        return f"{self.__class__.__name__}({paths})"

    def __str__(self) -> str:
        paths: str = ", ".join([path.url for path in self.root_paths])
        return f"{self.__class__.__name__}({paths})\n{self.keys()}"

    def _ipython_key_completions_(self) -> List[str]:
        return self.keys()

    def _repr_html_(self) -> str:
        try:
            return render_html_lazydatadir_as_pandas_table(self, data_filter=self.data_filter)
        except ImportError:
            return render_html_lazydatadir_as_table(self, data_filter=self.data_filter)

    def map(self) -> dict[str, Any]:
        """
        Returns
        -------
            dict key->path (data not loaded yet) or key->data (data has been loaded)
        """
        # first copy already loaded keys
        map = {k: v for k, v in super().items()}

        # then iterate on directory children to add it.
        # Children can ben data, subdir or invalid data
        paths = []
        p: Path | DataPath
        for root_path in self.root_paths:
            for p in root_path.iterdir():
                # ignore data already in map or invalid
                if p in self._invalid_path:
                    continue
                paths.append(p)

        # use data_filter to class to keep only path matching criteria
        for p in self.data_filter.paths(paths):
            # Then identify kind of data and add it to map if valid
            if self.data_filter.is_data_path(p):
                keys = self.data_filter.data_keys(p)
                refkey = keys[0]
                for key in keys:
                    if key not in map:
                        map[key] = p
                        self._aliases[key] = refkey
                        self._identical_data.setdefault(refkey, []).append(key)
            elif self.data_filter.is_group_path(p):
                keys = self.data_filter.group_keys(p)
                refkey = keys[0]
                for key in keys:
                    if key not in map:
                        map[key] = p
                        self._aliases[key] = refkey
                        self._identical_data.setdefault(refkey, []).append(key)
            else:
                self._invalid_path.append(p)

        # iterate on paths set explicitly by user
        for key, p in self.paths.items():
            if key in self._invalid_key or p in self._invalid_path:
                continue
            if self.data_filter.is_data_path(p) or self.data_filter.is_group_path(p):
                map[key] = p
            else:
                self._invalid_key.append(key)
                self._invalid_path.append(p)

        return map

    def iter_groups(
        self,
        recursive: bool = False,
        path: str = "",
    ) -> Generator[str | Any, Any, None]:
        for k, v in self.map().items():
            if isinstance(v, self.__class__) or isinstance(v, (Path, DataPath)) and self.data_filter.is_group_path(v):
                yield path + k
                if recursive:
                    for subgroup_k in self[k].iter_groups(
                        recursive=recursive,
                        path=k + "/",
                    ):
                        yield subgroup_k

    def iter_data(
        self,
        recursive: bool = False,
        path: str = "",
    ) -> Generator[Any | str, Any, None]:
        for k, v in self.map().items():
            if isinstance(v, (Path, DataPath)):
                if self.data_filter.is_group_path(v):
                    if recursive:
                        yield from self[k].iter_data(
                            recursive=recursive,
                            path=path + k + "/",
                        )
                else:
                    yield path + k
            else:
                if isinstance(v, self.__class__):
                    if recursive:
                        yield from v.iter_data(recursive=recursive, path=path + k + "/")
                else:
                    yield path + k

    def _items(self) -> Any:
        return super().items()

    def _keys(self) -> Any:
        return super().keys()

    def _values(self) -> Any:
        return super().values()

    def all_values(self, recursive: bool = False) -> Any:
        """
        Load all values and return it. Warning, this can be slow
        """
        self.load(recursive=recursive)
        return self._values()

    def all_items(self, recursive: bool = False) -> Any:
        """
        Load all values and return it. Warning, this can be slow
        """
        self.load(recursive=recursive)
        return self._items()

    def keys(self) -> list[str]:  # type: ignore[override]
        """
        return sorted list of keys.

        # TODO: delegate sort to DataFilter
        """
        return list(sorted(self.map().keys()))

    def items(self) -> Any:
        """
        Override dict method to avoid ambiguity due to "on demand" loading.
        raise error message to list available method and force user to choose the right one
        """
        cname = self.__class__.__name__
        raise AttributeError(f"Please use {cname}.map() or {cname}.all_items() instead")

    def values(self) -> Any:
        """
        Override dict method to avoid ambiguity due to "on demand" loading.
        raise error message to list available method and force user to choose the right one
        """
        cname = self.__class__.__name__
        raise AttributeError(
            f"Please use {cname}[key] instead. To get all values, use {cname}.all_values()",
        )

    def __getitem__(self, key: str) -> Any:
        """
        Override method to allow path notation:
        lazydir["x/y/z"] is equivalent to lazydir["x"]["y"]["z"]
        """
        if "/" in key:
            return reduce(self.__class__.__getitem__, key.split("/"), self)
        else:
            return super().__getitem__(key)
