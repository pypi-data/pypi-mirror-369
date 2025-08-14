"""
sentineltoolbox.exceptions provide all Warning and Error classes
"""

# Copyright 2024 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Optional

__all__: list[str] = [
    "CredentialTargetNotSupportedError",
    "DataSemanticConversionError",
    "MissingAdfError",
    "MultipleResultsError",
    "S3BucketCredentialNotFoundError",
    "SecretAliasNotFoundError",
    "SecretFileNotFoundError",
    "DatatreeSchemaAttrsError",
    "DatatreeSchemaKeyError",
    "DatatreeSchemaAttributeError",
    "DatatreeSchemaDimError",
    "DatatreeSchemaDataError",
    "DatatreeSchemaDtypeError",
]


class MissingAdfError(Exception):
    """
    This error is raise if a required ADF is missing
    """


class InputPlatformError(Exception):
    """
    This error is raise if a platform mismatch among inputs.
    For example, inputs contains platform "sentinel-3a" and "sentinel-3b
    """


class S3BucketCredentialNotFoundError(Exception):
    """
    Cannot found S3 Bucket Credentials.
    This error give no information about validity of credentials
    """


class CredentialTargetNotSupportedError(Exception):
    """This error is raised if user tries to convert credentials to kwargs
    for a target that is not supported yet.

    To know list of supported targets, just write: :obj:`sentineltoolbox.typedefs.Credentials.available_targets`
    """


class SecretFileNotFoundError(Exception):
    pass


class SecretAliasNotFoundError(Exception):
    pass


class DataSemanticConversionError(Exception):
    """
    Semantic of a product or ADF cannot be convert "from legacy to new format" or "from new format to legacy"
    because correspondence between legacy and new format is missing. To fix it, you need to pass new semantic
    explicitly or update legacy<->new format mapping, if available.
    """


class MultipleDataSemanticConversionError(Exception):
    """
    Semantic of a product or ADF cannot be convert "from legacy to new format" or "from new format to legacy"
    because there are multiple correspondences. To fix it, you need to pass semantic you want to choose.
    """


class MultipleResultsError(Exception):
    """This error is raised if unique result is expected but matching criteria returns more than one result"""


class LoadingDataError(Exception):
    """This error is raised if data exists but cannot be load (corrupted, wrong type, invalid, ...)"""


class DatatreeSchemaAttrsError(Exception):
    """The .attrs section is not correct in the DataTree instance."""

    def __init__(self, *args: Any, msg: Optional[str] = None, **kwargs: Any):
        super().__init__(msg or self.__doc__, *args, **kwargs)


class DatatreeSchemaKeyError(Exception):
    """A key (node) is missing in DataTree instance."""

    def __init__(self, *args: Any, msg: Optional[str] = None, **kwargs: Any):
        super().__init__(msg or self.__doc__, *args, **kwargs)


class DatatreeSchemaAttributeError(Exception):
    """An attribute (node) is missing in the DataTree instance."""

    def __init__(self, *args: Any, msg: Optional[str] = None, **kwargs: Any):
        super().__init__(msg or self.__doc__, *args, **kwargs)


class DatatreeSchemaDimError(Exception):
    """A dimension of a variable in the datatree is not as expected."""

    def __init__(self, *args: Any, msg: Optional[str] = None, **kwargs: Any):
        super().__init__(msg or self.__doc__, *args, **kwargs)


class DatatreeSchemaDataError(Exception):
    """The datatree instance does not hold the correct data type."""

    def __init__(self, *args: Any, msg: Optional[str] = None, **kwargs: Any):
        super().__init__(msg or self.__doc__, *args, **kwargs)


class DatatreeSchemaDtypeError(Exception):
    """The numpy dtype of a variable is not correct in the DataTree instance."""

    def __init__(self, *args: Any, msg: Optional[str] = None, **kwargs: Any):
        super().__init__(msg or self.__doc__, *args, **kwargs)


class WalkerNotDefinedError(Exception):
    pass
