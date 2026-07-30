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
