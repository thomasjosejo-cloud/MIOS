"""Persisted Option Engine snapshots.

Every poll's per-strike state is written here as an immutable record, giving
the intelligence pipeline the audit trail required by the Traceability
principle in `docs/24-database-design.md`: what a strike's OI, premium, and
classification were at any point in time. Nothing here is queried by the live
engine itself — it reads from in-memory state — this is the durable record.
"""

import datetime as dt
from decimal import Decimal

from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column

from mios.persistence import Base, IdentityMixin, TimestampMixin, enum_column
from mios.schemas.market import Classification, OptionType


class OptionStrikeSnapshot(IdentityMixin, TimestampMixin, Base):
    """An immutable snapshot of one strike's state at one point in time."""

    __tablename__ = "option_strike_snapshot"
    __table_args__ = (
        Index(
            "ix_option_strike_snapshot_lookup",
            "symbol",
            "strike",
            "option_type",
            "captured_at",
        ),
    )

    symbol: Mapped[str] = mapped_column(index=True)
    strike: Mapped[Decimal]
    option_type: Mapped[OptionType] = mapped_column(
        enum_column(OptionType, "option_type")
    )
    expiry: Mapped[dt.date]

    oi: Mapped[int]
    oi_change: Mapped[int] = mapped_column(default=0)
    premium: Mapped[Decimal]
    premium_change: Mapped[Decimal] = mapped_column(default=Decimal(0))
    volume: Mapped[int]
    volume_change: Mapped[int] = mapped_column(default=0)

    classification: Mapped[Classification | None] = mapped_column(
        enum_column(Classification, "classification"), nullable=True, default=None
    )

    #: When the Fyers observation this snapshot is based on was captured, as
    #: distinct from `created_at` (when this row was written to the database).
    captured_at: Mapped[dt.datetime] = mapped_column(index=True)
