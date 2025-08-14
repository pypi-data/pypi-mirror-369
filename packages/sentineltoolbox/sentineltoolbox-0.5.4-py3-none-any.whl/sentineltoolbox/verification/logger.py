import logging
import sys
from typing import Any, TextIO

try:
    from colorlog import ColoredFormatter
except ImportError:
    ColoredFormatter = logging.Formatter  # type: ignore


def get_logger(
    name: str = __name__,
    formatter: Any | None = None,
    level: int = logging.DEBUG,
    stream: TextIO | Any = sys.stderr,
) -> logging.Logger:
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    # Create handlers
    c_handler = logging.StreamHandler(stream=stream)
    c_handler.setLevel(level)

    # Create formatters and add them to the handlers
    if formatter is None:
        c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        c_handler.setFormatter(c_format)
    else:
        c_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(c_handler)

    return logger


def get_passed_logger(name: str = __name__, stream: TextIO | Any = sys.stderr) -> logging.Logger:
    passed_formatter = ColoredFormatter(
        # "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
        "%(log_color)s*** PASSED: %(reset)s %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "INFO": "bold_green",
        },
        stream=stream,
    )

    return get_logger(
        name,
        level=logging.INFO,
        formatter=passed_formatter,
        stream=stream,
    )


def get_failed_logger(name: str = __name__, stream: TextIO | Any = sys.stderr) -> logging.Logger:
    failed_formatter = ColoredFormatter(
        # "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%(log_color)s*** FAILED: %(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "INFO": "bold_red",
        },
        stream=stream,
    )

    return get_logger(
        name,
        level=logging.INFO,
        formatter=failed_formatter,
        stream=stream,
    )


class CustomHandler(logging.Handler):
    """
    Custom logging handler for capturing and directing log records.

    This class extends the standard `logging.Handler` to support capturing log
    entries into a list and optionally redirecting them to a provided stream.
    It provides flexibility for customized log handling and storage.

    :ivar stream: The output stream where log messages are written.
    :ivar logs: List for storing formatted log records.
    :type logs: list[str]
    """

    def __init__(self, stream: TextIO | Any = sys.stderr, level: int = logging.NOTSET):
        super().__init__(level)
        self.stream = stream
        self.logs: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        self.logs.append(log_entry)
        self.stream.write(log_entry + "\n")
        self.stream.flush()


def get_validation_handler(stream: TextIO | Any = sys.stderr, fmt: str = "%(message)s") -> logging.Handler:
    handler = CustomHandler(stream=stream, level=logging.INFO)
    handler.setFormatter(logging.Formatter(fmt))
    return handler


def get_validation_logger(
    stream: TextIO | Any = sys.stderr,
    handlers: list[logging.Handler] | None = None,
    fmt: str = "%(message)s",
) -> logging.Logger:
    if handlers is None:
        handlers = [get_validation_handler(stream=stream, fmt=fmt)]
    logger = logging.Logger("validation")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in handlers:
        logger.addHandler(handler)
    return logger
