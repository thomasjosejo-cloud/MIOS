"""Persistence of Option Engine snapshots.

The only writer of `OptionStrikeSnapshot`. Kept separate from the engines so
they stay pure and testable — they compute state; this stores it. Not a
general repository: it exposes exactly the one write the orchestrator needs.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from mios.models.options import OptionStrikeSnapshot
from mios.schemas.market import ClassificationResult, StrikeState


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
