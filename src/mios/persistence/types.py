"""Reusable column types.

Declared once here so every mapped column of a given kind is identical across
the platform. These types carry no business meaning — they describe storage
only.
"""

import datetime as dt
from enum import StrEnum

from sqlalchemy import Dialect, Enum, Numeric, String, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import DateTime

#: Precision for monetary and quantity values. Financial data is never stored as
#: a float: `Numeric` maps to Python `Decimal` and preserves exact scale.
DECIMAL_PRECISION = 38
DECIMAL_SCALE = 18


class UTCDateTime(TypeDecorator[dt.datetime]):
    """Timezone-aware timestamp normalized to UTC.

    PostgreSQL `timestamptz` already stores an absolute instant, but the Python
    value returned depends on the connection. This type guarantees callers both
    write and read aware UTC datetimes, so temporal comparisons never mix naive
    and aware values.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(
        self, value: dt.datetime | None, dialect: Dialect
    ) -> dt.datetime | None:
        """Reject naive datetimes and convert aware ones to UTC."""
        if value is None:
            return None
        if value.tzinfo is None:
            msg = "Naive datetime rejected; timestamps must be timezone-aware UTC"
            raise ValueError(msg)
        return value.astimezone(dt.UTC)

    def process_result_value(
        self, value: dt.datetime | None, dialect: Dialect
    ) -> dt.datetime | None:
        """Return the stored instant as aware UTC."""
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=dt.UTC)
        return value.astimezone(dt.UTC)


#: Native PostgreSQL `uuid`, surfaced as `uuid.UUID` in Python.
UUIDType = PGUUID(as_uuid=True)

#: Binary JSON. Preferred over `json` for indexability.
JSONType = JSONB

#: Exact numeric for prices, quantities, and monetary amounts.
NumericType = Numeric(precision=DECIMAL_PRECISION, scale=DECIMAL_SCALE, asdecimal=True)

#: Identifier of an actor recorded in audit columns.
ActorType = String(255)


def enum_column[EnumT: StrEnum](enum: type[EnumT], name: str) -> Enum:
    """Build a native PostgreSQL enum type for a `StrEnum`.

    Values are stored as the enum's string values rather than its member names,
    so the database is readable and stays stable if members are renamed.
    """
    return Enum(
        enum,
        name=name,
        native_enum=True,
        create_constraint=False,
        values_callable=lambda members: [member.value for member in members],
    )


__all__ = [
    "DECIMAL_PRECISION",
    "DECIMAL_SCALE",
    "ActorType",
    "JSONType",
    "NumericType",
    "UTCDateTime",
    "UUIDType",
    "enum_column",
]
