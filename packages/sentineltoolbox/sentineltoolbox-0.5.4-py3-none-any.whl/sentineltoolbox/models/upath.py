import os
from pathlib import Path, PurePosixPath
from typing import Any, Generator, Iterator, Self

from sentineltoolbox._utils import to_posix_str
from sentineltoolbox.typedefs import DataPath

try:
    from pandas.io.formats.format import EngFormatter
except ImportError:

    def bytes_formatter(value: float) -> str:
        return "%.2gb" % value

else:
    formatter = EngFormatter(accuracy=2, use_eng_prefix=True)

    def bytes_formatter(value: float) -> str:
        return formatter(value).strip() + "b"


class PathFsspec(DataPath):
    """
    Class to manage Amazon S3 Bucket.
    This path must be absolute and must start with s3://
    """

    def __init__(
        self,
        path: str | Path | PurePosixPath,
        fs: Any,
        **kwargs: Any,
    ) -> None:
        """
        Parameters
        ----------
        path
            s3 absolute path
        fs
            fsspec.filesystem

        Raises
        ------
        ValueError
            if path is not an absolute s3 path
        """
        self.fs = fs
        self.options = kwargs.get("options", {})
        if "://" in str(path):
            raise ValueError(f"{self.__class__.__name__} expect path, not url. Please remove protocol:// part.")
        self.compression: str | None = "infer"
        super().__init__(to_posix_str(path))
        self.original_url = kwargs.get("original_url", self.url)

    def __str__(self) -> str:
        """return absolute and canonical str representation of itself."""
        if "file" in self.fs.protocol:
            return str(Path(self.path))
        else:
            return self.url

    def __truediv__(self, relpath: str) -> Self:
        other = self.__class__(relpath, fs=self.fs)
        # Windows absolute path
        if ":\\" in other.path:
            drive, path = other.path.split(":\\")
            return self.__class__(other.path, fs=self.fs)
        # Unix absolute path
        elif other.path.startswith("/"):
            return self.__class__(relpath, fs=self.fs)
        elif self.path.endswith("/"):
            return self.__class__(self.path + other.path, fs=self.fs)
        else:
            return self.__class__(self.path + "/" + other.path, fs=self.fs)

    def __hash__(self) -> int:
        return hash(self.url)

    def _get_protocols(self) -> Any:
        return self.fs.protocol

    # docstr-coverage: inherited
    def is_file(self) -> bool:
        return self.fs.isfile(self.path)

    # docstr-coverage: inherited
    def is_dir(self) -> bool:
        return self.fs.isdir(self.path)

    # docstr-coverage: inherited
    @property
    def name(self) -> str:
        return PurePosixPath(self.path).name

    # docstr-coverage: inherited
    @property
    def parent(self) -> Self:
        # TODO: use pathlib for file://
        return self.__class__("/".join(str(self.path).split("/")[:-1]), fs=self.fs)

    def stat(self, *, follow_symlinks: bool = True) -> os.stat_result:
        """
        Returns information about this path (similarly to boto3's ObjectSummary).
        For compatibility with pathlib, the returned object some similar attributes like os.stat_result.
        The result is looked up at each call to this method
        """
        # os.stat_result(st_mode=1, st_ino=2, st_dev=3, st_nlink=4, st_uid=5, st_gid=6, st_size=7, st_atime=8,
        # st_mtime=9, st_ctime=10)
        st_mode = -1
        st_ino = -1
        st_dev = -1
        st_nlink = -1
        st_uid = -1
        st_gid = -1
        st_size: float = self.fs.size(self.path)
        st_atime = -1
        try:
            st_mtime: float = self.fs.modified(self.path).timestamp()
        except IsADirectoryError:
            st_mtime = 0
        st_ctime = -1
        return os.stat_result(
            (
                st_mode,
                st_ino,
                st_dev,
                st_nlink,
                st_uid,
                st_gid,
                st_size,
                st_atime,
                st_mtime,
                st_ctime,
            ),
        )

    def open(
        self,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: Any = None,
        **kwargs: Any,
    ) -> Any:
        # path, mode='rb', block_size=None, cache_options=None, compression=None, **kwargs
        kwargs["compression"] = kwargs.get("compression", self.compression)
        return self.fs.open(self.path, mode=mode, encoding=encoding, errors=errors, buffering=buffering, **kwargs)

    def exists(self) -> bool:
        return self.fs.exists(self.path)

    def mkdir(self, exist_ok: bool = False, parents: bool = False) -> None:
        """
        Create a new directory
        """
        # If parents=True, we need to mimic the behavior of creating all necessary directories
        if parents:
            self.fs.makedirs(self.path, exist_ok=exist_ok)
        else:
            if not exist_ok and self.fs.exists(self.path):
                raise FileExistsError(f"The directory '{self.path}' already exists.")
            self.fs.mkdir(self.path)

    def glob(self, pattern: str) -> Generator[Self, None, None]:
        for relpath in self.fs.glob(f"{self.path}/{pattern}"):
            yield self.__class__(relpath, fs=self.fs)

    def rglob(self, pattern: str) -> Generator[Self, None, None]:
        for relpath in self.fs.glob(f"{self.path}/**/{pattern}"):
            yield self.__class__(relpath, fs=self.fs)

    @property
    def url(self) -> str:
        return self.fs.protocol[0] + "://" + self.path

    def iterdir(self) -> Iterator[Self]:
        """Iterate over the files in this directory.  Does not yield any
        result for the special paths '.' and '..'.
        """
        for name in self.fs.ls(self.path):
            yield self.__class__(name, fs=self.fs)

    def _repr_html_(self) -> str:
        html = f"<b>{self.name}</b><br><span style='font-size: 8pt; color: grey;'>({self.url})</span>"
        if self.is_dir():
            html += "<ul>"
            for child in self.iterdir():
                html += f"\n<li>{child.name} ({bytes_formatter(child.stat().st_size)})</li>"
            html += "</ul>"
        return html
