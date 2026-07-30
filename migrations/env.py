"""Alembic migration environment.

Runs migrations against the async engine, resolving the connection from Settings
so no credentials live in `alembic.ini`.
"""

import asyncio
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import SchemaItem

import mios.models  # noqa: F401  (side-effect: registers ORM tables on `metadata`)
from mios.config import get_settings
from mios.persistence import metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The single metadata object for the platform. All models are registered on it
# via the `mios.models` import above.
target_metadata = metadata

config.set_main_option("sqlalchemy.url", get_settings().database_dsn)

#: Schemas owned by extensions rather than by MIOS. `include_schemas=True` makes
#: autogenerate reflect every schema, so without this filter it would compare
#: TimescaleDB's internal catalogs against our empty metadata and emit
#: `drop_table` operations that would dismantle the extension.
EXTENSION_SCHEMAS = frozenset(
    {
        "_timescaledb_cache",
        "_timescaledb_catalog",
        "_timescaledb_config",
        "_timescaledb_debug",
        "_timescaledb_functions",
        "_timescaledb_internal",
        "timescaledb_experimental",
        "timescaledb_information",
    }
)


def include_name(
    name: str | None,
    type_: str,
    parent_names: dict[str, str | None],
) -> bool:
    """Exclude extension-owned schemas from autogeneration."""
    if type_ == "schema":
        return name not in EXTENSION_SCHEMAS
    return parent_names.get("schema_name") not in EXTENSION_SCHEMAS


def include_object(
    object_: SchemaItem,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: SchemaItem | None,
) -> bool:
    """Exclude objects that live in an extension-owned schema."""
    return getattr(object_, "schema", None) not in EXTENSION_SCHEMAS


def migration_options() -> dict[str, Any]:
    """Return the context options shared by online and offline runs."""
    return {
        "target_metadata": target_metadata,
        "compare_type": True,
        "compare_server_default": True,
        "include_schemas": True,
        "include_name": include_name,
        "include_object": include_object,
    }


def run_migrations_offline() -> None:
    """Emit SQL to stdout without connecting to a database."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **migration_options(),
    )

    with context.begin_transaction():
        context.run_migrations()


def _run_migrations(connection: Connection) -> None:
    """Run migrations on an established synchronous connection."""
    context.configure(connection=connection, **migration_options())

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Connect with the async engine and run migrations."""
    engine: AsyncEngine = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=NullPool,
    )

    async with engine.connect() as connection:
        await connection.run_sync(_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
