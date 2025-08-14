import logging
from logging.config import dictConfig
from typing import Any

from sentineltoolbox.readers.resources import load_resource_file

logger = logging.getLogger("sentineltoolbox")

try:
    from colorama import Back, Fore, Style
except ImportError:
    DEFAULT_STDOUT_FORMATTER = "%(asctime)s [%(levelname)+8s] %(name)s\n    (%(funcName)s):" " %(message)s"
else:
    # For the sake of convenience, split log header from content
    DEFAULT_STDOUT_FORMATTER = (
        f"{Fore.YELLOW}%(asctime)s %(relativeCreated)12d"
        f" {Fore.WHITE}[{Style.BRIGHT}%(levelname)+8s{Style.RESET_ALL}]"
        f" {Fore.BLUE}{Fore.GREEN}%(name)s{Fore.RESET}\n   "
        f" {Fore.CYAN}%(funcName)s{Style.RESET_ALL}{Back.RESET}{Fore.RESET}:"
        f" {Fore.WHITE}%(message)s{Style.RESET_ALL}"
    )

DEFAULT_STDOUT_FORMATTER_NO_COLOR = "%(asctime)s [%(levelname)+8s] %(name)s\n    (%(funcName)s):" " %(message)s"


def build_colored_json_logging_config() -> dict[Any, Any]:
    file_formatter = "%(asctime)s %(relativeCreated)12d [%(levelname)+8s] %(name)s::(%(funcName)s): %(message)s"

    try:
        from colorama import Back, Fore, Style

        # For the sake of convenience, split log header from content
        console_formatter = (
            f"{Fore.YELLOW}%(asctime)s %(relativeCreated)12d"
            f" {Fore.WHITE}[{Style.BRIGHT}%(levelname)+8s{Style.RESET_ALL}]"
            f" {Fore.BLUE}{Fore.GREEN}%(name)s{Fore.RESET}\n   "
            f" {Fore.CYAN}%(funcName)s{Style.RESET_ALL}{Back.RESET}{Fore.RESET}:"
            f" {Fore.WHITE}%(message)s{Style.RESET_ALL}"
        )
    except ImportError:
        console_formatter = file_formatter

    json_dict = build_json_logging_config(console_formatter, file_formatter)

    return json_dict


def build_json_logging_config(console_formatter: str, file_formatter: str) -> dict[Any, Any]:
    json_dict = {
        "version": 1,
        "loggers": {
            "eopf": {"handlers": ["console"], "propagate": 0},
        },
        "formatters": {
            "console": {"format": console_formatter},
            "file": {"format": file_formatter},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "console",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "file",
                "filename": "s2msi_l2a_proto.log",
            },
        },
        "root": {"level": "INFO", "handlers": ["file", "console"]},
    }

    return json_dict


def init_logging(logging_conf: str = "myst.json") -> None:
    # os.environ["EOPF_LOGGING_LEVEL"] = "DEBUG"
    # EOConfiguration().register_requested_param(param_name = "logging_level", param_default_value = "DEBUG")
    # EOConfiguration().reset()
    # TODO: clean eopf conf
    try:
        conf = load_resource_file(f"logging_conf/{logging_conf}")
    except FileNotFoundError:
        logger.warning(f"Cannot find logging config {logging_conf!r} in sentineltoolbox/resources/logging_conf")
    else:
        dictConfig(conf)
