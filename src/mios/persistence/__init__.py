"""Persistence layer.

Provides the ORM base, shared metadata, mixins, column types, and helpers that
future models are built from. Declares no tables and holds no business meaning.
"""

from mios.persistence.base import Base
from mios.persistence.metadata import metadata
from mios.persistence.mixins import (
    AuditMixin,
    IdentityMixin,
    SoftDeleteMixin,
    TimestampMixin,
    VersionMixin,
    soft_delete_index,
)
from mios.persistence.types import (
    ActorType,
    JSONType,
    NumericType,
    UTCDateTime,
    UUIDType,
    enum_column,
)
from mios.persistence.utils import INITIAL_VERSION, new_uuid, next_version, utc_now

__all__ = [
    "INITIAL_VERSION",
    "ActorType",
    "AuditMixin",
    "Base",
    "IdentityMixin",
    "JSONType",
    "NumericType",
    "SoftDeleteMixin",
    "TimestampMixin",
    "UTCDateTime",
    "UUIDType",
    "VersionMixin",
    "enum_column",
    "metadata",
    "new_uuid",
    "next_version",
    "soft_delete_index",
    "utc_now",
]
