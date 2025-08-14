from typing import Any

try:
    import panel  # noqa: F401
    from fsspec.gui import FileSelector
except ImportError:

    class FileSelector:
        pass


from sentineltoolbox.exceptions import S3BucketCredentialNotFoundError
from sentineltoolbox.filesystem_utils import get_universal_path
from sentineltoolbox.models.credentials import S3BucketCredentialsPublic


def browse(path_or_pattern: Any, **kwargs: Any) -> FileSelector:
    try:
        upath = get_universal_path(path_or_pattern, **kwargs)
    except S3BucketCredentialNotFoundError:
        kwargs["credentials"] = S3BucketCredentialsPublic()
        upath = get_universal_path(path_or_pattern, **kwargs)
    return FileSelector(upath.url, kwargs=upath.fs.storage_options)
