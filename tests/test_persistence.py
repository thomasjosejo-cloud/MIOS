"""Tests for the persistence layer.

These tests need no database: mappings are compiled in memory and DDL is
rendered against the PostgreSQL dialect. Behaviour that requires a live server
is covered in `test_persistence_integration.py`.
"""

import datetime as dt
import subprocess
import sys
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Column, Integer, Numeric, String, Table, inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import ColumnDefault, CreateTable

from mios.config.constants import DB_NAMING_CONVENTION
from mios.persistence import (
    INITIAL_VERSION,
    AuditMixin,
    Base,
    IdentityMixin,
    SoftDeleteMixin,
    TimestampMixin,
    VersionMixin,
    metadata,
    new_uuid,
    next_version,
    soft_delete_index,
    utc_now,
)
from mios.persistence.types import (
    DECIMAL_PRECISION,
    DECIMAL_SCALE,
    UTCDateTime,
    enum_column,
)


class Colour(StrEnum):
    """Enum used to exercise `enum_column`."""

    RED = "red"
    BLUE = "blue"


class FullModel(
    IdentityMixin, TimestampMixin, AuditMixin, SoftDeleteMixin, VersionMixin, Base
):
    """Test-only model composing every mixin."""

    __tablename__ = "test_full_model"

    label: Mapped[str] = mapped_column(String(50), nullable=False)


class MinimalModel(IdentityMixin, Base):
    """Test-only model composing only identity."""

    __tablename__ = "test_minimal_model"


class AnnotatedModel(IdentityMixin, Base):
    """Test-only model exercising the annotation-to-type map."""

    __tablename__ = "test_annotated_model"

    when: Mapped[dt.datetime] = mapped_column(nullable=False)
    amount: Mapped[Decimal] = mapped_column(nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(nullable=False)
    other_id: Mapped[UUID] = mapped_column(nullable=False)


def table_of(model: type[Base]) -> Table:
    """Return a model's mapped Table."""
    table = model.__table__
    assert isinstance(table, Table)
    return table


def pg_dialect() -> Dialect:
    """Return a PostgreSQL dialect for rendering DDL and type processors."""
    return PGDialect()  # type: ignore[no-untyped-call]


def python_default(column: Column[object]) -> ColumnDefault:
    """Return a column's Python-side default."""
    default = column.default
    assert isinstance(default, ColumnDefault)
    return default


def ddl(model: type[Base]) -> str:
    """Render a model's CREATE TABLE against PostgreSQL."""
    return str(CreateTable(table_of(model)).compile(dialect=pg_dialect()))


# --- Base and metadata -------------------------------------------------------


def test_base_uses_the_shared_metadata() -> None:
    assert Base.metadata is metadata


def test_all_models_share_one_metadata() -> None:
    for model in (FullModel, MinimalModel, AnnotatedModel):
        assert table_of(model).metadata is metadata


def test_metadata_uses_the_naming_convention() -> None:
    assert dict(metadata.naming_convention) == DB_NAMING_CONVENTION


def test_primary_key_constraint_follows_the_convention() -> None:
    assert table_of(MinimalModel).primary_key.name == "pk_test_minimal_model"


def test_repr_includes_the_primary_key() -> None:
    identifier = uuid4()

    assert repr(MinimalModel(id=identifier)) == f"MinimalModel(id={identifier!r})"


def test_production_code_declares_no_tables() -> None:
    """Sprint 3 ships infrastructure only; models arrive later.

    Checked in a subprocess so the test-only models above cannot mask a real
    table declared by production code.
    """
    probe = "import mios.persistence as p; print(len(p.metadata.tables))"
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.strip() == "0"


# --- IdentityMixin -----------------------------------------------------------


def test_identity_is_a_uuid_primary_key() -> None:
    column = table_of(MinimalModel).c.id

    assert column.primary_key is True
    assert isinstance(column.type, postgresql.UUID)
    assert column.type.as_uuid is True


def test_identity_default_generates_a_uuid() -> None:
    default = python_default(table_of(MinimalModel).c.id)

    assert callable(default.arg)
    assert isinstance(default.arg(None), UUID)


def test_identity_has_a_server_side_default() -> None:
    assert "gen_random_uuid()" in ddl(MinimalModel)


# --- TimestampMixin ----------------------------------------------------------


@pytest.mark.parametrize("name", ["created_at", "updated_at"])
def test_timestamps_are_utc_aware_and_not_nullable(name: str) -> None:
    column = table_of(FullModel).c[name]

    assert isinstance(column.type, UTCDateTime)
    assert column.nullable is False
    assert column.default is not None


def test_timestamps_render_as_timestamptz() -> None:
    assert ddl(FullModel).count("TIMESTAMP WITH TIME ZONE") >= 2


def test_only_updated_at_has_an_onupdate_hook() -> None:
    assert table_of(FullModel).c.created_at.onupdate is None
    assert table_of(FullModel).c.updated_at.onupdate is not None


# --- AuditMixin --------------------------------------------------------------


@pytest.mark.parametrize("name", ["created_by", "updated_by"])
def test_audit_columns_are_nullable_strings(name: str) -> None:
    column = table_of(FullModel).c[name]

    assert column.nullable is True
    assert isinstance(column.type, String)


# --- SoftDeleteMixin ---------------------------------------------------------


def test_deleted_at_is_nullable_and_indexed() -> None:
    column = table_of(FullModel).c.deleted_at

    assert column.nullable is True
    assert column.index is True


def test_soft_delete_marks_and_restores() -> None:
    record = FullModel(label="x")

    assert record.is_deleted is False

    record.soft_delete()
    assert record.is_deleted is True
    assert record.deleted_at is not None
    assert record.deleted_at.tzinfo is not None

    record.restore()
    assert record.is_deleted is False
    assert record.deleted_at is None


def test_soft_delete_is_idempotent() -> None:
    record = FullModel(label="x")
    record.soft_delete()
    first = record.deleted_at

    record.soft_delete()

    assert record.deleted_at == first


def test_soft_delete_accepts_an_explicit_instant() -> None:
    moment = dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
    record = FullModel(label="x")

    record.soft_delete(at=moment)

    assert record.deleted_at == moment


def test_soft_delete_index_is_partial_and_unique() -> None:
    index = soft_delete_index("test_full_model", "label")

    assert index.unique is True
    assert index.name == "ix_test_full_model_label_live"
    assert "deleted_at IS NULL" in str(index.dialect_options["postgresql"]["where"])


# --- VersionMixin ------------------------------------------------------------


def test_version_column_is_registered_for_optimistic_locking() -> None:
    column = table_of(FullModel).c.version
    mapper = inspect(FullModel)

    assert isinstance(column.type, Integer)
    assert column.nullable is False
    assert mapper.version_id_col is column


def test_version_starts_at_the_initial_value() -> None:
    assert python_default(table_of(FullModel).c.version).arg == INITIAL_VERSION


# --- Mixin independence ------------------------------------------------------


def test_mixins_are_independent() -> None:
    """A model composing one mixin gains no columns from the others."""
    assert set(table_of(MinimalModel).c) - {table_of(MinimalModel).c.id} == set()


def test_each_model_gets_its_own_column_objects() -> None:
    """`declared_attr` must not share Column instances between models."""
    assert table_of(MinimalModel).c.id is not table_of(AnnotatedModel).c.id


# --- Types -------------------------------------------------------------------


def test_annotation_map_resolves_shared_types() -> None:
    columns = table_of(AnnotatedModel).c

    assert isinstance(columns.when.type, UTCDateTime)
    assert isinstance(columns.other_id.type, postgresql.UUID)
    assert isinstance(columns.payload.type, postgresql.JSONB)
    amount = columns.amount.type
    assert isinstance(amount, Numeric)
    assert amount.precision == DECIMAL_PRECISION
    assert amount.scale == DECIMAL_SCALE
    assert amount.asdecimal is True


def test_numeric_renders_with_exact_precision() -> None:
    assert f"NUMERIC({DECIMAL_PRECISION}, {DECIMAL_SCALE})" in ddl(AnnotatedModel)


def test_utc_datetime_rejects_naive_values() -> None:
    dialect = pg_dialect()
    processor = UTCDateTime().bind_processor(dialect)
    assert processor is not None

    with pytest.raises(ValueError, match="timezone-aware"):
        processor(dt.datetime(2026, 1, 1))


def test_utc_datetime_converts_to_utc_on_bind() -> None:
    dialect = pg_dialect()
    processor = UTCDateTime().bind_processor(dialect)
    assert processor is not None
    offset = dt.timezone(dt.timedelta(hours=5))

    bound = processor(dt.datetime(2026, 1, 1, 12, tzinfo=offset))

    assert bound == dt.datetime(2026, 1, 1, 7, tzinfo=dt.UTC)


def test_utc_datetime_returns_aware_values() -> None:
    dialect = pg_dialect()
    processor = UTCDateTime().result_processor(dialect, None)
    assert processor is not None

    result = processor(dt.datetime(2026, 1, 1, 7))

    assert result == dt.datetime(2026, 1, 1, 7, tzinfo=dt.UTC)


def test_enum_column_stores_values_not_member_names() -> None:
    column = enum_column(Colour, "colour")

    assert column.name == "colour"
    assert column.enums == ["red", "blue"]


# --- Utilities ---------------------------------------------------------------


def test_new_uuid_is_unique() -> None:
    assert new_uuid() != new_uuid()


def test_utc_now_is_timezone_aware_utc() -> None:
    now = utc_now()

    assert now.tzinfo is dt.UTC


def test_next_version_increments() -> None:
    assert next_version(INITIAL_VERSION) == INITIAL_VERSION + 1


def test_next_version_rejects_values_below_the_initial_version() -> None:
    with pytest.raises(ValueError, match="must be >="):
        next_version(0)
