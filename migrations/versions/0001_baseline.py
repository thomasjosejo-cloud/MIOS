"""Persistence baseline

Establishes the database-level infrastructure the persistence layer depends on,
before any business tables exist:

- `timescaledb`, required by the Market Store's future hypertables
  (`docs/00-technology-stack.md`), and validated at startup by
  `mios.db.timescale`.

`gen_random_uuid()`, used as the server-side default for UUID primary keys, is
built into PostgreSQL 13+ core and needs no extension.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-07-30

"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enable the extensions the persistence layer requires."""
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")


def downgrade() -> None:
    """Remove the extensions this revision enabled.

    `RESTRICT` is deliberate: if any object still depends on TimescaleDB the
    downgrade fails loudly rather than silently dropping hypertables.
    """
    op.execute("DROP EXTENSION IF EXISTS timescaledb RESTRICT")
