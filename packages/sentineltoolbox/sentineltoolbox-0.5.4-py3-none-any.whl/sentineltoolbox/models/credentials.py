"""
No public API here.
Use root package to import public function and classes
"""

import base64
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sentineltoolbox._utils import fix_url
from sentineltoolbox.configuration import Configuration, get_config
from sentineltoolbox.exceptions import (
    CredentialTargetNotSupportedError,
    S3BucketCredentialNotFoundError,
    SecretAliasNotFoundError,
    SecretFileNotFoundError,
)
from sentineltoolbox.typedefs import Credentials

__all__: list[str] = []


def _s3_env_variables_found() -> bool:
    for envvar in {"S3_KEY", "S3_SECRET", "S3_URL"}:
        if envvar not in os.environ:
            return False
    return True


def _aws_env_variables_found() -> bool:
    for envvar in {"AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_ENDPOINT_URL"}:
        if envvar not in os.environ:
            return False
    return True


def _get_secrets(secret_alias: str, **kwargs: Any) -> dict[str, Any]:
    """
    If user pass kwargs secret_alias="xxx" it means that a secret file exists and contains alias "xxx".
    If it is not the case these errors are raise:
      - :obj:`~sentineltoolbox.exceptions.SecretFileNotFoundError`
      - :obj:`~sentineltoolbox.exceptions.SecretAliasNotFoundError`

    Search secrets file in this order:
      - S3_SECRETS_JSON_BASE64
      - kwargs: secret_file_path
      - ~/.eopf/secrets.json
    """
    path = Path(kwargs.get("secret_file_path", Path.home() / ".eopf/secrets.json"))
    env_file = os.environ.get("S3_SECRETS_JSON_BASE64")

    if env_file:
        err_path = "S3_SECRETS_JSON_BASE64"
        json_str = base64.b64decode(env_file).decode("utf-8")
        secrets = json.loads(json_str)
    elif path.is_file():
        err_path = str(path)
        with open(str(path)) as f:
            secrets = json.load(f)
    else:
        raise SecretFileNotFoundError(f"Secret file {path} doesn't exist")
    try:
        return secrets[secret_alias]
    except KeyError:
        aliases = ", ".join(secrets.keys())
        raise SecretAliasNotFoundError(f"No alias {secret_alias} in {err_path}. Possible aliases: {aliases}")


# docstr-coverage: inherited
def _to_fsspec_filesystem_kwargs(credentials: Credentials, *, url: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """
    Use it like this:

    .. code-block:: python

        import fsspec
        credentials = Credentials(...)
        fsspec.filesystem(**to_fsspec_filesystem_kwargs(credentials))

    Parameters
    ----------
    url, optional
        - if url is set, extract information from url to generate kwargs, including url argument
        - if url is None, generate only credential kwargs. url, filename, store, ...
        must be pass explicitly to open function in this case

    Returns
    -------
        kwargs to pass to function
    """
    kwargs = credentials.to_kwargs(url=url, target="storage_options", **kwargs)
    kwargs["protocol"] = "s3"

    return kwargs


# docstr-coverage: inherited
def _to_zarr_open_kwargs(credentials: Credentials, *, url: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """
    Use it like this:

    .. code-block:: python

        import zarr
        credentials = Credentials(...)
        url = "s3://data/xxx.zarr"
        zarr.open_consolidated(**to_zarr_open_kwargs(credentials, url=url))

    Parameters
    ----------
    url, optional
        - if url is set, extract information from url to generate kwargs, including url argument
        - if url is None, generate only credential kwargs. url, filename, store, ...
        must be pass explicitly to open function in this case

    Returns
    -------
        kwargs to pass to function
    """
    if url is None:
        kwargs = {"storage_options": {"s3": _to_fsspec_filesystem_kwargs(credentials, **kwargs)}}
        del kwargs["storage_options"]["s3"]["protocol"]
        return kwargs
    else:
        kwargs = _to_zarr_open_kwargs(credentials, **kwargs)
        kwargs["store"] = fix_url(url)
        return kwargs


# docstr-coverage: inherited
def _to_datatree_open_kwargs(credentials: Credentials, *, url: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """
    Use it like this:

    .. code-block:: python

        import xarray
        credentials = Credentials(...)
        url = "s3://data/xxx.zarr"
        xarray.open_datatree(**to_datatree_open_kwargs(credentials, url=url))

    Parameters
    ----------
    url, optional
        - if url is set, extract information from url to generate kwargs, including url argument
        - if url is None, generate only credential kwargs. url, filename, store, ...
        must be pass explicitly to open function in this case

    Returns
    -------
        kwargs to pass to function
    """
    # backend_kwargs = dict(consolidated=True, compression="infer", decode_cf=True)
    kwargs.update(
        dict(
            consolidated=True,
            decode_cf=True,
        ),
    )
    if url is not None:
        import s3fs
        from fsspec import filesystem

        fs = filesystem(**_to_fsspec_filesystem_kwargs(credentials, **kwargs))
        kwargs["filename_or_obj"] = s3fs.S3Map(root=url, s3=fs, check=False)
    return kwargs


def _to_xarray_open_dataset(credentials: Credentials, *, url: str | None = None, **kwargs: Any) -> dict[str, Any]:
    """
    Use it like this:

    .. code-block:: python

        import xarray
        credentials = Credentials(...)
        url = "s3://data/xxx.zarr"
        xarray.open_zarr(**to_xarray_open_zarr_kwargs(credentials, url=url))

    Parameters
    ----------
    url, optional
        - if url is set, extract information from url to generate kwargs, including url argument
        - if url is None, generate only credential kwargs. url, filename, store, ...
        must be pass explicitly to open function in this case

    Returns
    -------
        kwargs to pass to function
    """
    backend_kwargs = _to_zarr_open_kwargs(credentials, **kwargs)
    group = kwargs.get("group", "/")

    kwargs = dict(
        backend_kwargs=backend_kwargs,
        group=group,
        **kwargs,
    )
    if url is not None:
        kwargs["filename_or_obj"] = url

    return kwargs


def map_secret_aliases(map: dict[str, str | list[str]], **kwargs: Any) -> None:
    """
    Function to associate secret_alias to paths.
    Map is updated each time you call map_secret_aliases.

    >>> map_secret_aliases({"alias1": ["s3://bucket1", "s3://bukcet2"]})

    :param map: dict secret_alias -> path or list of paths
    :param kwargs:
    :return:
    """
    configuration = kwargs.get("configuration", Configuration.instance())
    configuration.map_secret_aliases(map)


def list_secret_alias_mappings(**kwargs: Any) -> dict[str, list[str]]:
    return get_config(**kwargs).secret_aliases


@dataclass(kw_only=True, frozen=True, repr=False)
class S3BucketCredentials(Credentials):
    key: str
    secret: str
    endpoint_url: str
    region_name: str | None = None

    available_targets: Any = field(
        default=(
            "fsspec.filesystem",
            "zarr.open_consolidated",
            "xarray.open_datatree",
            "xarray.open_dataset",
            "AnyPath",
        ),
        init=False,
        repr=False,
    )

    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> "S3BucketCredentials":
        """
        extract credential from kwargs
        """
        key = kwargs.get("key")
        secret = kwargs.get("secret")
        client_kwargs = kwargs.get("client_kwargs", kwargs)
        endpoint_url = client_kwargs.get("endpoint_url")
        region_name = client_kwargs.get("region_name")
        if key is None or secret is None or endpoint_url is None:
            raise ValueError("Cannot extract credentials from kwargs")
        else:
            return S3BucketCredentials(key=key, secret=secret, endpoint_url=endpoint_url, region_name=region_name)

    @classmethod
    def from_env(cls, **kwargs: Any) -> "S3BucketCredentials":
        """
        Tries to find credentials from environements and kwargs.

        Resolve order is ... (tries first, if not found tries seconds, ...)

        #. if path is mapped to a secret_alias (see map_secret_aliases), set secret_alias with this value
        #. if secret_alias is set, search secret json file
        #. EOPF env variables
        #. AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ...
        #. AWS_CONFIG_FILE + AWS_PROFILE
        #. AWS_SHARED_CREDENTIALS_FILE + AWS_PROFILE

        If all fails, raise :obj:`~sentineltoolbox.exceptions.S3BucketCredentialNotFoundError`

        **secret_alias**
        If user pass kwargs secret_alias="xxx" it means that a secret file exists and contains alias "xxx".
        If it is not the case these errors are raise:
          - :obj:`~sentineltoolbox.exceptions.SecretFileNotFoundError`
          - :obj:`~sentineltoolbox.exceptions.SecretAliasNotFoundError`

        Search secrets file in this order:
          - kwargs: secret_file_path
          - ~/.eopf/secrets.json
          - S3_SECRETS_JSON_BASE64

        **EOPF env variables**

        * S3_KEY
        * S3_SECRET
        * S3_URL
        * S3_REGION


        **AWS env variables**

        * AWS_ACCESS_KEY_ID - The access key for your AWS account.
        * AWS_SECRET_ACCESS_KEY - The secret key for your AWS account.
        * AWS_DEFAULT_REGION
        * AWS_ENDPOINT_URL

        * AWS_SHARED_CREDENTIALS_FILE. If not set ~/.aws/credentials
        * AWS_CONFIG_FILE. If not set ~/.aws/config
        * AWS_PROFILE: define which env to use in AWS_CONFIG_FILE / AWS_SHARED_CREDENTIALS_FILE

        See
        `Boto 3 doc <BOTO>`_ and `AWS Cli doc <AWS>`_

        Sample of AWS config file

        .. code-block:: ini

            [default]
            aws_access_key_id=foo
            aws_secret_access_key=bar

            [profile dev]
            aws_access_key_id=foo2
            aws_secret_access_key=bar2

        .. _AWS: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html
        .. _BOTO: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables

        :param kwargs:
        :return:
        """
        if "secret_alias" in kwargs:
            return S3BucketCredentials(**_get_secrets(**kwargs))
        elif _s3_env_variables_found():
            return S3BucketCredentials(
                key=os.environ["S3_KEY"],
                secret=os.environ["S3_SECRET"],
                endpoint_url=os.environ["S3_URL"],
                region_name=os.environ.get("S3_REGION", ""),
            )
        elif _aws_env_variables_found():
            return S3BucketCredentials(
                key=os.environ["AWS_ACCESS_KEY_ID"],
                secret=os.environ["AWS_SECRET_ACCESS_KEY"],
                endpoint_url=os.environ["AWS_ENDPOINT_URL"],
                region_name=os.environ.get("AWS_DEFAULT_REGION", ""),
            )
        else:
            raise S3BucketCredentialNotFoundError()

    def to_kwargs(self, *, url: str | None = None, target: Any = None, **kwargs: Any) -> dict[str, Any]:

        if target is not None and not isinstance(target, str):
            try:
                target = target.__module__ + "." + target.__name__
            except AttributeError:
                pass

        if target:
            # could be extended using entry point if necessary
            if target in ("fsspec.registry.filesystem", "fsspec.filesystem"):
                return _to_fsspec_filesystem_kwargs(self, url=url, **kwargs)
            elif target in ("zarr.convenience.open_consolidated", "zarr.open_consolidated"):
                return _to_zarr_open_kwargs(self, url=url, **kwargs)
            elif target in (
                "datatree.io.open_datatree",
                "xarray.io.open_datatree",
                "datatree.open_datatree",
                "xarray.open_datatree",
            ):
                return _to_datatree_open_kwargs(self, url=url, **kwargs)
            elif target in ("xarray.backends.api.open_dataset", "xarray.open_dataset"):
                return _to_xarray_open_dataset(self, url=url, **kwargs)
            elif target in ("storage_options",):
                kwargs = {
                    "key": self.key,
                    "secret": self.secret,
                    "client_kwargs": {"endpoint_url": self.endpoint_url},
                }
                if self.region_name:
                    kwargs["client_kwargs"]["region_name"] = self.region_name
                return kwargs
            elif target in ("eopf.common.file_utils.AnyPath", "AnyPath"):
                kwargs = self.to_kwargs(url=url, target="storage_options", **kwargs)
                if url:
                    kwargs["url"] = url
                return kwargs
            else:
                str_targets = ", ".join(sorted(self.available_targets))
                msg = f"Credentials.to_kwargs does not support {target=}. Supported targets are {str_targets}"
                raise CredentialTargetNotSupportedError(msg)
        else:
            return {
                "key": self.key,
                "secret": self.secret,
                "endpoint_url": self.endpoint_url,
                "region_name": self.region_name,
            }


class S3BucketCredentialsPublic(Credentials):

    def __init__(self) -> None:
        pass

    def to_kwargs(self, *, url: str | None = None, target: Any = None, **kwargs: Any) -> dict[str, Any]:
        if target is not None and not isinstance(target, str):
            try:
                target = target.__module__ + "." + target.__name__
            except AttributeError:
                pass

        final_kwargs = {}
        if target:
            # could be extended using entry point if necessary
            if target in ("fsspec.registry.filesystem", "fsspec.filesystem"):

                final_kwargs["protocol"] = "s3"
        return final_kwargs

    @classmethod
    def from_env(cls) -> "Credentials":
        """
        Tries to generate credential instance from environment variables
        """
        return S3BucketCredentialsPublic()

    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> "Credentials":
        """
        Tries to generate credential instance from given kwargs
        """
        return S3BucketCredentialsPublic()
