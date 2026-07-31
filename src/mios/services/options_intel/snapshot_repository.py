"""Persistence of Option Engine snapshots.

The writer of `OptionStrikeSnapshot` (per poll) and the single read it backs:
the per-strike historical progression the Strike Evolution panel renders. Kept
separate from the engines so they stay pure — they compute state; this stores
and retrieves it.
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mios.models.options import OptionStrikeSnapshot
from mios.schemas.dashboard import StrikeHistory, StrikeHistoryPoint
from mios.schemas.market import ClassificationResult, OptionType, StrikeState


def _pct(change: Decimal, current: Decimal) -> float | None:
    """Percent change from the prior value, derived from stored current+delta."""
    previous = current - change
    if previous == 0:
        return None
    return round(float(change / previous * 100), 2)


def build_rows(
    states: list[StrikeState],
    classifications: list[ClassificationResult],
    *,
    symbol: str,
) -> list[OptionStrikeSnapshot]:
    """Build one snapshot row per strike, attaching any classification."""
    by_key = {
        (result.strike, result.option_type): result.classification
        for result in classifications
    }

    return [
        OptionStrikeSnapshot(
            symbol=symbol,
            strike=state.strike,
            option_type=state.option_type,
            expiry=state.expiry,
            oi=state.current_oi,
            oi_change=state.oi_change,
            premium=state.current_premium,
            premium_change=state.premium_change,
            volume=state.current_volume,
            volume_change=state.volume_change,
            classification=by_key.get((state.strike, state.option_type)),
            captured_at=state.last_updated,
        )
        for state in states
    ]


async def persist_snapshots(
    session: AsyncSession,
    states: list[StrikeState],
    classifications: list[ClassificationResult],
    *,
    symbol: str,
) -> int:
    """Persist a poll's snapshots in one transaction, returning the row count."""
    rows = build_rows(states, classifications, symbol=symbol)
    session.add_all(rows)
    await session.flush()
    return len(rows)


async def load_strike_history(
    session: AsyncSession,
    *,
    symbol: str,
    strike: Decimal,
    option_type: OptionType,
    limit: int,
) -> StrikeHistory:
    """Load a strike's persisted snapshots (oldest first) for Strike Evolution.

    Percentage changes are derived in the backend from the stored current value
    and per-poll delta, so the frontend only renders. Returns an empty series
    when no history has been captured yet.
    """
    stmt = (
        select(OptionStrikeSnapshot)
        .where(
            OptionStrikeSnapshot.symbol == symbol,
            OptionStrikeSnapshot.strike == strike,
            OptionStrikeSnapshot.option_type == option_type,
        )
        .order_by(OptionStrikeSnapshot.captured_at.desc())
        .limit(limit)
    )
    rows = list((await session.execute(stmt)).scalars().all())
    rows.reverse()  # oldest first for a left-to-right progression

    points = [
        StrikeHistoryPoint(
            captured_at=row.captured_at,
            oi=row.oi,
            oi_change=row.oi_change,
            oi_change_pct=_pct(Decimal(row.oi_change), Decimal(row.oi)),
            premium=row.premium,
            premium_change=row.premium_change,
            premium_change_pct=_pct(row.premium_change, row.premium),
            volume=row.volume,
            volume_change=row.volume_change,
            volume_change_pct=_pct(Decimal(row.volume_change), Decimal(row.volume)),
            classification=row.classification,
        )
        for row in rows
    ]
    return StrikeHistory(strike=strike, option_type=option_type, points=points)
