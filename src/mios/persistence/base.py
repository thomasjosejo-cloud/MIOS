"""The single ORM base for the platform.

Every mapped class in MIOS inherits from `Base`, so all tables share one
metadata object, one naming convention, and one set of type mappings.
"""

import datetime as dt
from decimal import Decimal
from typing import Any, ClassVar
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase

from mios.persistence.metadata import metadata
from mios.persistence.types import (
    JSONType,
    NumericType,
    UTCDateTime,
    UUIDType,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models.

    `type_annotation_map` means annotating a column `Mapped[UUID]`,
    `Mapped[datetime]`, `Mapped[Decimal]`, or `Mapped[dict]` yields the shared
    type from `types.py` without restating it per column.
    """

    metadata = metadata

    type_annotation_map: ClassVar[dict[Any, Any]] = {
        UUID: UUIDType,
        dt.datetime: UTCDateTime,
        Decimal: NumericType,
        dict[str, Any]: JSONType,
    }

    def __repr__(self) -> str:
        """Return an unambiguous representation using the primary key."""
        keys = [column.name for column in self.__table__.primary_key]
        values = ", ".join(f"{key}={getattr(self, key, None)!r}" for key in keys)
        return f"{type(self).__name__}({values})"
