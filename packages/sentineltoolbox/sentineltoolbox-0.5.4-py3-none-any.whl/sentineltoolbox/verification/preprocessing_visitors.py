from typing import Any, Hashable, Tuple, Type, TypeAlias

from xarray import DataArray, DataTree

from sentineltoolbox.datatree_utils import visit_datatree
from sentineltoolbox.models.filename_generator import filename_generator
from sentineltoolbox.typedefs import DataTreeVisitor

"""
Provide generic filters for reference and converted products.
These filter add or remove attributes to improve compare_datatree outputs.
For example, converted products are sometimes improved and have more information than reference products.
We do not want to display this information as an issue.

Other improvments:
  - alert if long_name is not present in converted product
  - remove _ARRAY_DIMENSIONS attribute from reference product
  - remove all _eopf_attrs attributes from reference product. It is not our responsability to check these attributes.
"""

PreProcVisitor: TypeAlias = Type[DataTreeVisitor]
PreProcVisitorWithPriority = Type[DataTreeVisitor] | tuple[PreProcVisitor, int]


class ReferenceFilterGeneric(DataTreeVisitor):
    def __init__(self, other: DataTree):
        self.other = other
        super().__init__()

    def visit_attrs(
        self,
        root: DataTree,
        path: str,
        obj: dict[Hashable, Any],
        node: Any = None,
    ) -> None | dict[Hashable, Any]:
        # datarray /conditions/sid-216/packet_data_length
        # {'_eopf_attrs': {
        #   'coordinates': ['sensing_time'],
        #   'dimensions': ['packet_number']
        # }}
        changed = False

        try:
            other_attrs = self.other[path].attrs
        except KeyError:
            other_attrs = {}
        # if long_name is neither in reference nor in converted, we need to inform user it could be nice to add it.
        # create a fake long_name in reference product
        if isinstance(node, DataArray) and "long_name" not in other_attrs and "long_name" not in obj:
            obj["long_name"] = "TODO"
            changed = True

        try:
            del obj["_eopf_attrs"]["_ARRAY_DIMENSIONS"]
        except KeyError:
            pass
        else:
            changed = True

        if changed:
            return obj
        else:
            return None


class ConvertedFilterGeneric(DataTreeVisitor):
    def __init__(self, other: DataTree):
        self.other = other
        super().__init__()

    def visit_attrs(
        self,
        root: DataTree,
        path: str,
        obj: dict[Hashable, Any],
        node: Any = None,
    ) -> None | dict[Hashable, Any]:
        changed = False
        try:
            other_attrs = self.other[path].attrs
        except KeyError:
            other_attrs = {}
        # if long_name is present in converted product and is not in reference product,
        # that means that converter has improved product so we do not want to diplay it as an issue
        # delete it from converted product
        if "long_name" not in other_attrs and "long_name" in obj:
            del obj["long_name"]
            changed = True

        for attr_name in ("long_name", "short_name"):
            try:
                del obj["_eopf_attrs"][attr_name]
            except KeyError:
                pass
            else:
                changed = True
        if changed:
            return obj
        else:
            return None


class ReferenceFilterRenamedVariables(DataTreeVisitor):
    def __init__(self, other: DataTree):
        super().__init__()
        self.other = other

    def visit_node(self, root: DataTree, path: str, obj: DataTree) -> None:
        """
        Fix isp shape to fit real data. Fix encoding information chunks and preferred_chunks
        """
        # 'rsvd_spare' -> 'reserved_spare_flags'
        if path == "/conditions":
            try:
                obj["reserved_spare_flags"] = obj["rsvd_spare"]
            except KeyError:
                pass

            root[path].ds = obj.ds.drop_vars(["rsvd_spare"], errors="ignore")  # type: ignore


class ReferenceFilterS01GPSRAW(DataTreeVisitor):
    def __init__(self, other: DataTree):
        self.other = other
        super().__init__()

    def visit_node(self, root: DataTree, path: str, obj: DataTree) -> None:
        """
        Fix isp shape to fit real data. Fix encoding information chunks and preferred_chunks
        """
        if path.startswith("/measurements/sid-"):
            current = self.other[path]
            packet_length = current.dims["packet_length"]  # type: ignore
            subset = obj.isel(packet_length=slice(0, packet_length)).chunk({"packet_length": packet_length})
            for var_path, var_ref in subset.data_vars.items():
                var_conv = current[var_path]
                var_ref.encoding["chunks"] = var_conv.encoding["chunks"]
                var_ref.encoding["preferred_chunks"] = var_conv.encoding["preferred_chunks"]
            root[path] = subset


class FilterHarmonizeStructureS01SXWRAW(DataTreeVisitor):
    def __init__(self, other: DataTree):
        super().__init__()
        self.other = other
        self.paths_to_fix: dict[str, str] = {}

    def start(self, root: DataTree) -> None:
        self.paths_to_fix.clear()

    def visit_node(self, root: DataTree, path: str, obj: DataTree) -> None:
        """
        Fix isp shape to fit real data. Fix encoding information chunks and preferred_chunks
        """
        if path.startswith("/"):
            paths = path.split("/")[1:]
        else:
            paths = path.split("/")
        fixed_paths = []
        for p in paths:
            if p.endswith(".zarr"):
                p = p.replace(".zarr", "")
            try:
                fgen, fdata = filename_generator(p.upper())
            except NotImplementedError:
                # it is a leaf node, break loop as we do not need to fix it.
                return
            else:
                fixed_paths.append(fgen.to_string(extension=""))
        fixed_path = "/" + "/".join(fixed_paths)
        if fixed_path != path and path and fixed_path:
            self.paths_to_fix[path] = fixed_path

    def end(self, root: DataTree) -> None:
        """
                    print(path, "->", fixed_path)
            root[fixed_path] = root[path]
            del root[path]

        :param root:
        :return:
        """
        for path, fixed_path in self.paths_to_fix.items():
            root[fixed_path] = root[path]

        for path in self.paths_to_fix:
            try:
                leaf = root[path]
                parent = leaf.parent
                if parent is not None:
                    del parent[leaf.name]
            except KeyError:
                pass


class ConvertedFilterS01GPSRAW(DataTreeVisitor):
    def __init__(self, other: DataTree):
        self.other = other
        super().__init__()

    def visit_attrs(
        self,
        root: DataTree,
        path: str,
        obj: dict[Hashable, Any],
        node: Any = None,
    ) -> None | dict[Hashable, Any]:
        changed = False

        # obj.setdefault("_eopf_attrs", {})["_ARRAY_DIMENSIONS"] = ["C"]
        if "_eopf_attrs" in obj:
            for attr_id in ("long_name", "short_name"):
                try:
                    del obj["_eopf_attrs"][attr_id]
                except KeyError:
                    pass
                else:
                    changed = True
        if changed:
            return obj
        else:
            return None


DEFAULT_VALIDATION_VISITORS: dict[str, Tuple[list[PreProcVisitorWithPriority], list[PreProcVisitorWithPriority]]] = {
    "S01GPSRAW": (
        [ReferenceFilterGeneric, ReferenceFilterS01GPSRAW],
        [ConvertedFilterGeneric, ConvertedFilterS01GPSRAW],
    ),
    "S01HKMRAW": (
        [ReferenceFilterGeneric, ReferenceFilterRenamedVariables],
        [ConvertedFilterGeneric],
    ),
    "S01SIWRAW": (
        [(FilterHarmonizeStructureS01SXWRAW, 0), ReferenceFilterGeneric],
        [(FilterHarmonizeStructureS01SXWRAW, 0), ConvertedFilterGeneric],
    ),
    "S01SEWRAW": (
        [(FilterHarmonizeStructureS01SXWRAW, 0), ReferenceFilterGeneric],
        [(FilterHarmonizeStructureS01SXWRAW, 0), ConvertedFilterGeneric],
    ),
    "S01SWVRAW": (
        [(FilterHarmonizeStructureS01SXWRAW, 0), ReferenceFilterGeneric],
        [(FilterHarmonizeStructureS01SXWRAW, 0), ConvertedFilterGeneric],
    ),
}


def apply_validation_visitors(ptype: str, xdt_ref: DataTree, xdt_conv: DataTree) -> tuple[DataTree, DataTree]:

    ref_visitors, conv_visitors = DEFAULT_VALIDATION_VISITORS.get(
        ptype,
        ([ReferenceFilterGeneric], [ConvertedFilterGeneric]),
    )

    ref_visitors_by_priority: dict[int, list[Type[DataTreeVisitor]]] = {}
    conv_visitors_by_priority: dict[int, list[Type[DataTreeVisitor]]] = {}

    for visitor in ref_visitors:
        if isinstance(visitor, tuple):
            visitor, priority = visitor
        else:
            priority = 10
        ref_visitors_by_priority.setdefault(priority, []).append(visitor)

    for visitor in conv_visitors:
        if isinstance(visitor, tuple):
            visitor, priority = visitor
        else:
            priority = 10
        conv_visitors_by_priority.setdefault(priority, []).append(visitor)

    priorities = set(list(ref_visitors_by_priority.keys()) + list(conv_visitors_by_priority.keys()))

    for priority in sorted(priorities):
        visitors = [visitor(other=xdt_conv) for visitor in ref_visitors_by_priority.get(priority, [])]
        xdt_ref = visit_datatree(xdt_ref, visitors)

        visitors = [visitor(other=xdt_ref) for visitor in conv_visitors_by_priority.get(priority, [])]
        xdt_conv = visit_datatree(xdt_conv, visitors)

    return xdt_ref, xdt_conv
