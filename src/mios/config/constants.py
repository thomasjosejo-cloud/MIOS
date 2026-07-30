"""Application constants.

Values here are fixed properties of the application itself. Anything that varies
per deployment belongs in `settings.py` and is read from the environment.
"""

from mios import __version__

APP_NAME = "MIOS"
APP_VERSION = __version__
APP_DESCRIPTION = "Market Intelligence & Operations System"

API_V1_PREFIX = "/api/v1"

DEFAULT_PAGE_SIZE = 50

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
