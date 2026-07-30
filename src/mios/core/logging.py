"""Structured logging setup.

`docs/00-technology-stack.md` mandates structured JSON logs across services. A
human-readable console format is retained for local development.
"""

import json
import logging
import sys
from typing import Any

from mios.config.constants import DEFAULT_LOG_DATE_FORMAT, DEFAULT_LOG_FORMAT

#: Attributes present on every LogRecord; anything else was supplied by the
#: caller via `extra=` and is emitted as a structured field.
_RESERVED_ATTRS = frozenset(
    logging.LogRecord("", 0, "", 0, "", None, None).__dict__
) | {"message", "asctime", "taskName"}


class JSONFormatter(logging.Formatter):
    """Render log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize a record, including any `extra` fields and exception info."""
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, DEFAULT_LOG_DATE_FORMAT),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in _RESERVED_ATTRS:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(level: str, *, json_format: bool = False) -> None:
    """Configure the root logger, writing structured records to stdout."""
    formatter: logging.Formatter = (
        JSONFormatter()
        if json_format
        else logging.Formatter(fmt=DEFAULT_LOG_FORMAT, datefmt=DEFAULT_LOG_DATE_FORMAT)
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name."""
    return logging.getLogger(name)
