"""Option Engine: per-strike state tracking.

Holds the latest observation for every tracked strike in memory and computes
deltas against the previous observation. Persistence of snapshots is handled
by the orchestrator (`engine.py`), not here — this class only tracks state.
"""

from mios.schemas.market import OptionQuote, OptionType, StrikeState


class OptionEngine:
    """In-memory latest-state tracker for every strike."""

    def __init__(self) -> None:
        """Start with no tracked strikes."""
        self._state: dict[tuple[str, OptionType], StrikeState] = {}

    def update(self, quote: OptionQuote) -> StrikeState:
        """Fold a new observation into the strike's tracked state and return it."""
        key = (str(quote.strike), quote.option_type)
        previous = self._state.get(key)
        state = self._compute_state(quote, previous)
        self._state[key] = state
        return state

    def update_all(self, quotes: list[OptionQuote]) -> list[StrikeState]:
        """Fold a full chain snapshot into tracked state, returning the new states."""
        return [self.update(quote) for quote in quotes]

    def snapshot(self) -> list[StrikeState]:
        """Return the latest state for every tracked strike, ordered by strike."""
        return sorted(
            self._state.values(), key=lambda s: (s.strike, s.option_type.value)
        )

    @staticmethod
    def _compute_state(quote: OptionQuote, previous: StrikeState | None) -> StrikeState:
        """Compute the strike's new state, deriving deltas if a prior state exists."""
        if previous is None:
            return StrikeState(
                strike=quote.strike,
                option_type=quote.option_type,
                expiry=quote.expiry,
                current_oi=quote.oi,
                current_premium=quote.premium,
                current_volume=quote.volume,
                last_updated=quote.timestamp,
                seconds_since_update=0.0,
            )

        elapsed_seconds = max(
            0.0, (quote.timestamp - previous.last_updated).total_seconds()
        )
        oi_change = quote.oi - previous.current_oi
        premium_change = quote.premium - previous.current_premium
        volume_change = quote.volume - previous.current_volume

        return StrikeState(
            strike=quote.strike,
            option_type=quote.option_type,
            expiry=quote.expiry,
            current_oi=quote.oi,
            previous_oi=previous.current_oi,
            oi_change=oi_change,
            oi_change_pct=_pct_change(previous.current_oi, oi_change),
            oi_velocity_per_min=_per_minute(oi_change, elapsed_seconds),
            current_premium=quote.premium,
            previous_premium=previous.current_premium,
            premium_change=premium_change,
            premium_change_pct=_pct_change(
                float(previous.current_premium), float(premium_change)
            ),
            current_volume=quote.volume,
            previous_volume=previous.current_volume,
            volume_change=volume_change,
            volume_change_pct=_pct_change(previous.current_volume, volume_change),
            last_updated=quote.timestamp,
            seconds_since_update=elapsed_seconds,
        )


def _pct_change(base: float, change: float) -> float | None:
    """Return `change` as a percentage of `base`, or `None` if `base` is zero."""
    if base == 0:
        return None
    return (change / base) * 100


def _per_minute(change: float, elapsed_seconds: float) -> float | None:
    """Return `change` normalized to a per-minute rate, or `None` if no time elapsed."""
    if elapsed_seconds <= 0:
        return None
    return change / (elapsed_seconds / 60)
