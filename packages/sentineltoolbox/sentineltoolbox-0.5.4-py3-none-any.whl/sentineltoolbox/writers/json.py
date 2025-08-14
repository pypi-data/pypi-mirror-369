import json
import logging
from typing import Any

import numpy as np
import zarr
from packaging.version import Version
from zarr.storage import MemoryStore

if Version(zarr.__version__) > Version("3.0.0"):
    from zarr.core.attributes import Attributes
else:
    from zarr.attrs import Attributes

logger = logging.getLogger("sentineltoolbox")


class DataTreeJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(sorted(obj))
        elif isinstance(obj, np.dtype):
            return obj.name
        elif isinstance(obj, np.generic):
            return obj.item()
        else:
            try:
                return super().default(obj)
            except TypeError:
                return repr(obj)


def serialize_to_zarr_json(log_data: Any, **kwargs: Any) -> Any:
    store = MemoryStore()
    attrs = Attributes(store)
    errors = kwargs.get("errors", "strict")
    try:
        attrs[""] = log_data
    except TypeError as e:
        if errors == "replace":
            # eschalk: call your code "to_json_best_effort" here
            # and recall serialize_to_zarr(jsonified, errors="strict") to be sure jsonified code
            # can be serialized with zarr
            return json.dumps(log_data, cls=DataTreeJSONEncoder, sort_keys=True)
        elif errors == "ignore":
            logger.warning(f"Cannot log data of type {type(log_data)!r}. replace by 'repr' str to keep information")
            return repr(log_data)
        else:
            logger.warning(f"Cannot log data of type {type(log_data)!r}. zarr cannot serialize it.")
            raise e
    else:
        return log_data
