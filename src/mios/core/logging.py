"""Structured logging setup."""

import logging
import sys

from mios.config.constants import DEFAULT_LOG_DATE_FORMAT, DEFAULT_LOG_FORMAT


def configure_logging(level: str) -> None:
    """Configure the root logger once, writing structured records to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(fmt=DEFAULT_LOG_FORMAT, datefmt=DEFAULT_LOG_DATE_FORMAT)
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name."""
    return logging.getLogger(name)
