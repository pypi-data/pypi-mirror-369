import importlib
import importlib.resources
import logging
import os
from html import escape
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any, Literal

from sentineltoolbox.readers.resources import load_resource_file
from sentineltoolbox.resources.data import DATAFILE_METADATA, TERMS_METADATA

#
from .logging_utils import init_logging


class EopfFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.module == "log" and record.funcName == "get_logger":
            return False
        else:
            return True


def init_ipython(ipython: Any, env: Literal["doc", "notebook"] = "notebook") -> None:
    from IPython.core.display import HTML

    if env == "notebook":
        width = "100%"
    else:
        width = "800px"

    css = load_resource_file("autodoc/static/css/common.css")
    ipython.displayhook(
        HTML(
            """
    <style>
    .jp-OutputArea-output {
        max-width: %(width)s;
    }

    %(css)s
    </style>
    """
            % dict(css=css, width=width),
        ),
    )

    try:
        from itables import init_notebook_mode
    except ImportError:
        pass
    else:
        init_notebook_mode(all_interactive=True)


def init(
    logging_conf: str = "myst.json",
    ipy_formatters: bool = False,
    env: Literal["doc", "notebook"] = "notebook",
) -> None:
    """
    Update logging configuration with logging conf

    We can use this function to associate custome __repr_html__ to any object (including read-only, third party objects)
    using this code:
    html = ipython.display_formatter.formatters['text/html']
    html.for_type(ClassToExtend, repr_html_function)

    Parameters
    ----------
    logging_conf, optional
        conf to use to customize logging, by default "myst.json"
    ipy_formatters, optional
        if set, update IPython to use sentinelutils builtins formatters to represent data
    """
    # os.environ["EOPF_LOGGING_LEVEL"] = "DEBUG"
    # EOConfiguration().register_requested_param(param_name = "logging_level", param_default_value = "DEBUG")
    # EOConfiguration().reset()
    if logging_conf is not None:
        init_logging(logging_conf)
    if ipy_formatters is True:
        from sentineltoolbox.autodoc.rendering import IpythonHtmlFormatter

        IpythonHtmlFormatter().ipython_install("text/html")

    try:
        ipython = get_ipython()  # type: ignore
    except NameError:
        pass
    else:
        init_ipython(ipython=ipython, env=env)


def export_terms() -> dict[str, str]:
    aliases = {}

    for db in (DATAFILE_METADATA, TERMS_METADATA):
        for name, metadata in db.items():
            for field, value in metadata.items():
                aliases[f"_{name}_{field.replace(':', '_')}"] = value

    return aliases


def display_enum(enum_cls: Any) -> None:
    from IPython.display import HTML, display

    display(HTML(enum_cls))


def get_source_path() -> Path:
    docutilsconfig = Path(
        os.environ.get("DOCUTILSCONFIG", Path("./docutils.conf").absolute()),
    )
    return docutilsconfig.parent.absolute()


def _guess_static_path(root: Path | str | None = None) -> Path:
    if root is None:
        root = get_source_path()
    root = Path(root).absolute()
    for path in root.iterdir():
        if path.is_dir() and "static" in str(path):
            return path
    else:
        return get_source_path() / "_static"


def get_static_path(root: Path | str | None = None, conf_module: str = "conf") -> Path:
    if conf_module:
        try:
            conf = importlib.import_module("conf")
        except ImportError:
            return _guess_static_path(root)
        else:
            if hasattr(conf, "html_static_path"):
                lst = conf.html_static_path
                if isinstance(lst, str):
                    return get_source_path() / lst
                elif isinstance(lst, list) and lst:
                    return get_source_path() / lst[0]
                else:
                    return _guess_static_path(root)
            else:
                return _guess_static_path(root)
    else:
        return _guess_static_path(root)


def replace_static_path(
    builddir: str | Path,
    html_static_relpath: Path | str | None = None,
    placeholder: str = "<STATIC_PATH_TO_REPLACE>",
) -> None:
    if html_static_relpath is None:
        html_static_relpath = get_static_path().relative_to(get_source_path())
    html_static_relpath = str(html_static_relpath)
    buildir = Path(builddir).absolute()
    from fileinput import input

    # loop on generated html
    placeholder = escape(placeholder)
    for p in buildir.rglob("*.html"):
        if p.relative_to(buildir).parts[0] in (
            "_static",
            "api",
            "search.html",
            "permalink.html",
            "py-modindex.html",
        ):
            continue
        with input(str(p), inplace=True, encoding="utf-8") as f:
            replacement = ""
            # generate relative path for this file
            parts = p.relative_to(buildir).parent.parts
            if parts:
                relpath = "/".join([".." for _ in parts]) + "/" + html_static_relpath
            else:
                relpath = html_static_relpath

            # iter on lines to find placeholder
            for line in f:
                if placeholder in line:
                    # if found, replace placeholder with relative path, set flag
                    print(line.replace(placeholder, relpath), end="")
                    replacement = relpath
                else:
                    print(line, end="")

            if replacement:
                print(
                    f"{p.relative_to(buildir)}: replace {placeholder} with {replacement}",
                )


def _copy_traversable(root: Traversable, currentdir: Traversable, static_dir_path: str | Path) -> None:
    for src in currentdir.iterdir():
        if src.is_dir():
            _copy_traversable(root, src, static_dir_path)
        else:
            try:
                relpath = src.relative_to(root)  # type: ignore
            except AttributeError:
                relpath = src.name
            dest = Path(static_dir_path, relpath)
            if not dest.parent.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
            print("copy", src, "->", dest)
            with open(dest, "wb") as f:
                f.write(src.read_bytes())


def copy_static_files(static_dir_path: str | None | Path = None) -> None:
    if static_dir_path is None:
        static_dir_path = get_static_path()
    root = importlib.resources.files("sentineltoolbox.resources.autodoc") / "static"
    _copy_traversable(root, root, static_dir_path)


def run_after_build(html_static_relpath: str | None = None, html_build_dir: str = "build/html/") -> None:
    print("replace static paths with relative path in %s ..." % html_build_dir)
    replace_static_path(html_build_dir, html_static_relpath=html_static_relpath)
    print("done")


def remove_eopf_dumps() -> None:
    import shutil

    eopf = Path(get_static_path(get_source_path()), "eopf").absolute()
    if eopf.is_dir():
        print("remove", str(eopf))
        shutil.rmtree(str(eopf))


def run_before_build(html_static_dir: str = "_static") -> None:
    copy_static_files(html_static_dir)
    print("TODO: copy_static_files only if has changed")
