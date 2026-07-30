"""Integration tests for the persistence layer against a real PostgreSQL server.

Skipped automatically when the configured database is unreachable, so the suite
still passes without infrastructure. To run them:

    docker compose up -d postgres
    docker compose exec -T postgres createdb -U mios mios_test
"""

import datetime as dt
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import String, Table, select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.exc import StaleDataError

from mios.config import get_settings
from mios.persistence import (
    INITIAL_VERSION,
    AuditMixin,
    Base,
    IdentityMixin,
    SoftDeleteMixin,
    TimestampMixin,
    VersionMixin,
    utc_now,
)

pytestmark = pytest.mark.integration


class IntegrationModel(
    IdentityMixin, TimestampMixin, AuditMixin, SoftDeleteMixin, VersionMixin, Base
):
    """Test-only table exercising every mixin against a real server."""

    __tablename__ = "test_integration_model"

    label: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


def integration_table() -> Table:
    """Return the mapped Table for the test model."""
    table = IntegrationModel.__table__
    assert isinstance(table, Table)
    return table


@pytest.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    """Create the test table, or skip if the database is unreachable.

    Only connection failures are skipped; any other error is a real defect and
    must surface rather than being reported as missing infrastructure.
    """
    engine = create_async_engine(get_settings().database_dsn)

    try:
        async with engine.begin() as connection:
            await connection.run_sync(integration_table().create, checkfirst=True)
    except (OSError, DBAPIError) as error:
        await engine.dispose()
        pytest.skip(f"PostgreSQL unavailable: {type(error).__name__}: {error}")

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(integration_table().drop, checkfirst=True)
    await engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Yield a session and clean the table afterwards."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as connection:
        await connection.execute(integration_table().delete())


async def test_insert_populates_identity_and_timestamps(session: AsyncSession) -> None:
    record = IntegrationModel(label="inserted")

    session.add(record)
    await session.commit()

    assert record.id is not None
    assert record.created_at.tzinfo is not None
    assert record.updated_at.tzinfo is not None
    assert record.version == INITIAL_VERSION
    assert record.deleted_at is None


async def test_timestamps_round_trip_as_utc(session: AsyncSession) -> None:
    session.add(IntegrationModel(label="utc"))
    await session.commit()
    session.expire_all()

    fetched = (await session.execute(select(IntegrationModel))).scalar_one()

    assert fetched.created_at.tzinfo is not None
    assert fetched.created_at.utcoffset() == dt.timedelta(0)


async def test_update_advances_updated_at_and_version(session: AsyncSession) -> None:
    record = IntegrationModel(label="before")
    session.add(record)
    await session.commit()
    original_updated_at = record.updated_at

    record.label = "after"
    await session.commit()

    assert record.version == INITIAL_VERSION + 1
    assert record.updated_at >= original_updated_at
    assert record.created_at <= record.updated_at


async def test_optimistic_locking_detects_a_concurrent_update(
    engine: AsyncEngine, session: AsyncSession
) -> None:
    record = IntegrationModel(label="contended")
    session.add(record)
    await session.commit()

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as other:
        competitor = (await other.execute(select(IntegrationModel))).scalar_one()
        competitor.label = "winner"
        await other.commit()

    record.label = "loser"
    with pytest.raises(StaleDataError):
        await session.commit()


async def test_soft_delete_persists(session: AsyncSession) -> None:
    record = IntegrationModel(label="removable")
    session.add(record)
    await session.commit()

    record.soft_delete()
    await session.commit()
    session.expire_all()

    fetched = (await session.execute(select(IntegrationModel))).scalar_one()
    assert fetched.is_deleted is True
    assert fetched.deleted_at is not None

    fetched.restore()
    await session.commit()
    assert fetched.deleted_at is None


async def test_audit_columns_persist_actors(session: AsyncSession) -> None:
    record = IntegrationModel(label="audited", created_by="tester")
    session.add(record)
    await session.commit()

    record.updated_by = "reviewer"
    await session.commit()
    session.expire_all()

    fetched = (await session.execute(select(IntegrationModel))).scalar_one()
    assert fetched.created_by == "tester"
    assert fetched.updated_by == "reviewer"


async def test_naming_convention_applies_to_real_constraints(
    session: AsyncSession,
) -> None:
    """A convention-derived constraint name must be what the server reports."""
    session.add(IntegrationModel(label="duplicate"))
    await session.commit()

    session.add(IntegrationModel(label="duplicate"))
    with pytest.raises(IntegrityError, match="uq_test_integration_model_label"):
        await session.commit()


async def test_server_side_uuid_default_applies_outside_the_orm(
    engine: AsyncEngine,
) -> None:
    """Inserts that bypass the ORM still receive an identifier."""
    table = integration_table()

    async with engine.begin() as connection:
        identifier = await connection.scalar(
            table.insert()
            .values(label="raw", created_at=utc_now(), updated_at=utc_now())
            .returning(table.c.id)
        )

    assert identifier is not None
