"""Persistence baseline

Establishes the database-level infrastructure the persistence layer depends on,
before any business tables exist:

- `timescaledb`, required by the Market Store's future hypertables
  (`docs/00-technology-stack.md`), and validated at startup by
  `mios.db.timescale`. Enabled best-effort: a PostgreSQL server that does not
  ship the extension (e.g. Railway's managed Postgres) logs a warning and
  continues, since no hypertables exist yet. A TimescaleDB-enabled server
  (local dev) still gets the extension created for real.

`gen_random_uuid()`, used as the server-side default for UUID primary keys, is
built into PostgreSQL 13+ core and needs no extension.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-07-30

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy import exc

from mios.config.constants import TIMESCALEDB_EXTENSION
from mios.core.logging import get_logger

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

logger = get_logger(__name__)


def upgrade() -> None:
    """Enable the extensions the persistence layer requires.

    TimescaleDB is enabled best-effort: on a server that cannot provide it the
    server raises SQLSTATE ``0A000`` (``feature_not_supported``), which psycopg
    surfaces as ``sqlalchemy.exc.NotSupportedError``. We swallow that one case,
    log a warning, and continue — no hypertables depend on it yet.
    """
    _try_extension_ddl(
        f"CREATE EXTENSION IF NOT EXISTS {TIMESCALEDB_EXTENSION}",
        "TimescaleDB extension is not available on this PostgreSQL server; "
        "continuing without it (no hypertables exist yet). Use a "
        "TimescaleDB-enabled image for full functionality.",
    )


def downgrade() -> None:
    """Remove the extensions this revision enabled.

    `RESTRICT` is deliberate: if any object still depends on TimescaleDB the
    downgrade fails loudly rather than silently dropping hypertables. Handled
    symmetrically with `upgrade()` so a downgrade on a server without the
    extension degrades gracefully rather than crashing.
    """
    _try_extension_ddl(
        f"DROP EXTENSION IF EXISTS {TIMESCALEDB_EXTENSION} RESTRICT",
        "TimescaleDB extension is not available on this PostgreSQL server; "
        "nothing to drop.",
    )


def _try_extension_ddl(statement: str, unavailable_warning: str) -> None:
    """Run extension DDL, tolerating a server that lacks the extension.

    The statement runs inside a SAVEPOINT. Migrations execute within a single
    transaction, so if the server rejects the extension the transaction enters
    an aborted state — catching the Python exception alone is not enough, since
    Alembic's later write to `alembic_version` would then fail with
    `InFailedSqlTransaction`. Rolling back to the SAVEPOINT clears the aborted
    state while keeping the outer transaction alive, so the migration can
    complete.
    """
    bind = op.get_bind()
    try:
        with bind.begin_nested():
            bind.exec_driver_sql(statement)
    except exc.NotSupportedError:
        logger.warning(unavailable_warning)
