import copy
import re
from dataclasses import dataclass, field
from typing import Any, Iterable

import jinja2.environment

from sentineltoolbox.readers.resources import load_resource_file

DEFAULT_VARIABLES = load_resource_file("metadata/product_pattern_variables.json")
CO_JINJA_PATTERN = re.compile(r"\{\{[a-zA-Z0-9_]+\}\}")


@dataclass(kw_only=True)
class Ellipsis:
    """
    A class for pattern matching and string manipulation using regular expressions and Jinja2 templates.

    Attributes
    ----------
    patterns :
        List of pattern strings to match against.
    variables :
        Dictionary of variables used in patterns.
    environment : jinja2.Environment
        Jinja2 environment for template rendering.
    pattern_co : list of re.Pattern
        Compiled regular expression patterns.
    pattern_tpl : list of jinja2.environment.Template
        Jinja2 templates for patterns.
    pattern_vars :
        List of variables used in each pattern.
    pattern_repr :
        List of pattern representations.
    repr_path :
        Mapping of real paths to representation paths.
        For example: '/gr0/var0' -> '/gr<GID>/var<VID>'
    repr_name : dict of {str: str}
        Mapping of representation paths to names.
        For example: '/gr<GID>/var<VID>' -> 'var<VID>'
    repr_description : dict of {str: str}
        Mapping of representation paths to descriptions.
        For example: '/gr<GID>/var<VID>' -> 'Variable <VID>'
    repr_documentation : dict of {str: str}
        Mapping of representation paths to documentation.
        '/gr<GID>/var<VID>' -> 'Documentation for variable <VID>'
    variable_used :
        Dictionary of used variables and their values.
    path_used :
        Dictionary of used paths for each pattern index.
    """

    patterns: list[str]
    variables: dict[str, dict[Any, Any]] = field(default_factory=dict)
    environment = jinja2.Environment(autoescape=False)  # nosec B701
    pattern_co: list[re.Pattern[Any]] = field(init=False)
    pattern_tpl: list[jinja2.environment.Template] = field(init=False)
    pattern_vars: list[list[str]] = field(default_factory=list)
    pattern_repr: list[str] = field(default_factory=list)

    """**REAL** path -> repr path. For example: '/gr0/var0' -> '/gr<GID>/var<VID>'"""
    repr_path: dict[str, str] = field(default_factory=dict)

    """**REPR** path -> repr path. For example: '/gr<GID>/var<VID>' -> 'var<VID>'"""
    repr_name: dict[str, str] = field(default_factory=dict)

    """**REPR** path -> repr path. For example: '/gr<GID>/var<VID>' -> 'Variable <VID>'"""
    repr_description: dict[str, str] = field(default_factory=dict)

    """**REPR** path -> repr path. For example: '/gr<GID>/var<VID>' -> 'Documentation for variable <VID>'"""
    repr_documentation: dict[str, str] = field(default_factory=dict)

    """**REPR** path -> dict: idx -> variable -> alternatives.
    For example: '/gr{{VAR1}}/var{{VAR2}}' -> {0: "VAR1": ["01", "02"], "VAR2": ["a", "b"]}"""
    variable_used: dict[int, dict[str, list[str]]] = field(default_factory=dict)
    path_used: dict[int, list[str]] = field(default_factory=dict)

    def init(self) -> None:
        """
        Initialize the instance by clearing variable_used and path_used dictionaries.
        """
        self.variable_used.clear()
        self.path_used.clear()

    def debug(self, path: Any) -> Any:
        self._debug.append(path)
        return path

    def missing_paths(self, product: Any) -> list[str]:
        paths = set([obj.path for obj in product.walk()])
        return list(sorted(paths.difference(set(self._debug))))

    def __post_init__(self) -> None:
        self.pattern_co = []
        self.pattern_tpl = []
        self.pattern_vars = []
        self.pattern_repr = []
        self._debug: list[Any] = []
        if not self.variables:
            self.variables = copy.copy(DEFAULT_VARIABLES)
        self.variable_used = {}
        self.path_used = {}

        kwargs_re = self.kwargs("re")
        kwargs_repr = self.kwargs("repr")
        for pattern in self.patterns:
            template = self.environment.from_string(pattern)
            pattern_re = f"({template.render(**kwargs_re)})"
            if not pattern_re.startswith("^"):
                pattern_re = "^" + pattern_re
            if not pattern_re.endswith("$"):
                pattern_re += "$"
            self.pattern_co.append(re.compile(pattern_re))
            self.pattern_tpl.append(template)
            self.pattern_vars.append(
                [varname[2:-2] for varname in CO_JINJA_PATTERN.findall(pattern)],
            )
            self.pattern_repr.append(template.render(**kwargs_repr))

    def path(self, path: str) -> str:
        """
        Get the representation path for a given real path.

        Parameters
        ----------
        path : str
            The real path.

        Returns
        -------
        str
            The representation path if it exists, otherwise the original path.
        """
        return self.repr_path.get(path, path)

    def match(self, string: str) -> int | None:
        """
        Match a string against the compiled patterns.

        Parameters
        ----------
        string : str
            The string to match.

        Returns
        -------
        int or None
            The index of the first matching pattern, or None if no match is found.
        """
        for idx, co in enumerate(self.pattern_co):
            if co.match(string):
                return idx
        else:
            return None

    def kwargs(self, mode: str = "use") -> dict[str, Any]:
        return {k: v.get(mode, k) for k, v in self.variables.items()}

    def replace(self, string: str, kwargs: Any = None) -> str:
        idx = self.match(string)
        if idx is None:
            return string
        else:
            if kwargs is None:
                kwargs = self.kwargs("repr")
            template = self.pattern_tpl[idx]
            return template.render(**kwargs)

    def _update_user_variables(self, idx: int, string: str) -> None:
        paths = self.path_used.setdefault(idx, [])
        if string in paths:
            return
        else:
            paths.append(string)

            variables = self.pattern_vars[idx]
            sep = "|PLACEHOLDER|"
            begin = string
            parts = self.replace(string, {k: sep for k in variables}).split(sep)
            values = {}

            for i, varname in enumerate(variables):
                if len(parts) > 1:
                    before = parts[i]
                    begin = begin.replace(before, "", 1)
                    matches = re.findall("^" + self.variables[varname]["re"], begin)
                    if matches:
                        value = matches[0]
                        begin = begin.replace(value, "", 1)
                        values[varname] = value

            for varname, value in values.items():
                self.variable_used.setdefault(idx, {}).setdefault(varname, []).append(
                    value,
                )

    def prune(
        self,
        lst: Iterable[str],
        repr_dict: dict[str, str] | None = None,
        use_dict: dict[str, str] | None = None,
    ) -> list[tuple[str, str]]:
        """
        Prune a list of paths based on patterns.
        For example, with
            VARIABLES = {
                "V01": {"re": "[0-9]{1}", "use": "1", "repr": "<NUM>"},
                "G01": {"re": "[0-9]{1}", "use": "1", "repr": "<ID>"},
            }
        and
            PATTERNS = [
                "/group{{G01}}",
                "/group{{G01}}/group{{G01}}_variable{{V01}}",
            ]

        Path list :
            [
                "/group0/group0_variable0",  # match
                "/group0/group0_variable1",  # match
            ]

        becomes:
            [
                ("/group1/group1_variable1", "/group<ID>/group<ID>_variable<NUM>"),
            ]

        The first part correspond to a real existing path. Use this information to reach data.
        The second part is a generic representation for all paths matching this pattern. Use this for display

        Parameters
        ----------
        lst : Iterable of str
            An iterable of paths to prune.
        repr_dict : dict of {str: str}, optional
            A dictionary for path representations. Default is None.
        use_dict : dict of {str: str}, optional
            A dictionary for path usage. Default is None.

        Returns
        -------
            list of tuple (valid_path, path_representation).
            Use first to access data, use second to display generic name
        """
        pruned = []
        done = set()
        for path in lst:
            idx = self.match(path)
            if idx is None:
                pruned.append((path, path))
                continue
            else:
                self._update_user_variables(idx, path)
                if idx not in done:
                    done.add(idx)
                    if use_dict is None:
                        use_dict = self.kwargs("use")
                    if repr_dict is None:
                        repr_dict = self.kwargs("repr")
                    path_to_use = self.replace(path, use_dict)
                    path_repr = self.replace(path, repr_dict)

                    name = path_to_use.split("/")[-1]
                    repr_name = path_repr.split("/")[-1]
                    self.repr_path[path_to_use] = path_repr
                    self.repr_name[path_repr] = repr_name
                    self.repr_name[name] = repr_name

                    pruned.append((path_to_use, path_repr))
        for lst in self.path_used.values():
            lst.sort()
        return pruned
