"""Application constants.

Values here are fixed properties of the application itself. Anything that varies
per deployment belongs in `settings.py` and is read from the environment.
"""

from enum import StrEnum

from mios import __version__

APP_NAME = "MIOS"
APP_VERSION = __version__
APP_DESCRIPTION = "Market Intelligence & Operations System"

API_V1_PREFIX = "/api/v1"

DEFAULT_PAGE_SIZE = 50

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

#: Async SQLAlchemy dialect for PostgreSQL, per the psycopg 3 driver.
POSTGRES_ASYNC_DRIVER = "postgresql+psycopg"

#: Extension required by the Market Store's time-series storage.
TIMESCALEDB_EXTENSION = "timescaledb"

#: Naming convention applied to all constraints, so Alembic autogeneration
#: produces stable, predictable migration names.
DB_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_N_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Environment(StrEnum):
    """Deployment environments defined in `docs/30-deployment-model.md`."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ComponentStatus(StrEnum):
    """Operational status of a single infrastructure component."""

    UP = "up"
    DOWN = "down"


class HealthStatus(StrEnum):
    """Overall operational status of the application."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"


# --- Fyers API v3 -------------------------------------------------------------
#
# Endpoints and header format verified directly against the official
# `fyers-apiv3` SDK source (fyersModel.py `Config` class), not documentation
# prose. These are fixed properties of the Fyers API itself, not deployment
# configuration, so they live here rather than in Settings.

FYERS_AUTH_BASE_URL = "https://api-t1.fyers.in/api/v3"
FYERS_DATA_BASE_URL = "https://api-t1.fyers.in/data"

FYERS_GENERATE_AUTHCODE_PATH = "/generate-authcode"
FYERS_VALIDATE_AUTHCODE_PATH = "/validate-authcode"
FYERS_QUOTES_PATH = "/quotes"
FYERS_OPTION_CHAIN_PATH = "/options-chain-v3"
FYERS_HISTORY_PATH = "/history"
FYERS_MARKET_STATUS_PATH = "/marketStatus"

FYERS_API_VERSION_HEADER = "3"
