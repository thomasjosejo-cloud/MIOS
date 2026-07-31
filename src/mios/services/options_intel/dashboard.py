"""Dashboard aggregation.

Assembles a `DashboardResponse` from the latest pipeline execution held in the
`EngineStore`. This is a thin projection: it performs no analysis and never runs
the pipeline. Beyond the raw engine outputs it adds the decision-centric
presentation — narrative and dominance (via `presentation`) — and trims the
option chain to the five CE and five PE strikes nearest the money.
"""

import datetime as dt
from decimal import Decimal

from mios.config.constants import AuthStatus
from mios.schemas.dashboard import (
    DashboardResponse,
    EngineStatus,
    MarketDominance,
    MarketNarrative,
    MarketSection,
    OptionChainRow,
)
from mios.schemas.market import Classification, OptionType, TradeQualification
from mios.services.options_intel import presentation
from mios.services.options_intel.store import EngineStore

#: Strikes to show per side around the money (Sprint 10.1: 5 CE + 5 PE).
_CHAIN_PER_SIDE = 5


def build_dashboard(
    store: EngineStore, *, now: dt.datetime | None = None
) -> DashboardResponse:
    """Aggregate the store's latest pipeline outputs into one dashboard response."""
    now = now or dt.datetime.now(dt.UTC)

    return DashboardResponse(
        connection_state=store.connection_state,
        authentication=(
            AuthStatus.CONNECTED
            if store.authenticated
            else AuthStatus.NOT_AUTHENTICATED
        ),
        data_source=store.data_source,
        market=_market(store),
        narrative=_narrative(store),
        dominance=_dominance(store),
        qualification=store.qualification,
        context=store.context,
        ce_pe=store.cepe,
        option_chain=_option_chain(store),
        engine=_engine_status(store, now),
    )


def _market(store: EngineStore) -> MarketSection:
    """Build the market header, deriving spot change from the previous poll."""
    spot = store.spot_price
    previous = store.previous_spot_price

    change: Decimal | None = None
    change_percent: float | None = None
    if spot is not None and previous is not None:
        change = spot - previous
        if previous != 0:
            change_percent = round(float(change / previous * 100), 2)

    return MarketSection(
        spot=spot,
        change=change,
        change_percent=change_percent,
        status="LIVE" if store.market_open else "CLOSED",
        updated_at=store.last_poll_at,
    )


def _narrative(store: EngineStore) -> MarketNarrative | None:
    """Build the plain-language market story from existing engine outputs."""
    if store.context is None or store.structure is None or store.momentum is None:
        return None
    if store.qualification is None or store.spot_price is None:
        return None
    return presentation.build_narrative(
        store.classifications,
        store.context,
        store.structure,
        store.momentum,
        store.qualification,
        spot=store.spot_price,
    )


def _dominance(store: EngineStore) -> MarketDominance | None:
    """Build the market-dominance view from the existing CE/PE analysis."""
    if store.cepe is None:
        return None
    return presentation.build_dominance(store.classifications, store.cepe)


def _option_chain(store: EngineStore) -> list[OptionChainRow]:
    """Project the 5 CE + 5 PE strikes nearest ATM into dashboard rows."""
    classification_by_key: dict[tuple[Decimal, OptionType], Classification] = {
        (c.strike, c.option_type): c.classification for c in store.classifications
    }
    unusual_by_key: dict[tuple[Decimal, OptionType], list[str]] = {
        (u.strike, u.option_type): u.triggers for u in store.unusual
    }
    recommended = _recommended_keys(store.qualification)
    spot = store.spot_price

    def distance(state_strike: Decimal) -> Decimal:
        return abs(state_strike - spot) if spot is not None else state_strike

    ce = sorted(
        (s for s in store.strike_states if s.option_type is OptionType.CE),
        key=lambda s: distance(s.strike),
    )[:_CHAIN_PER_SIDE]
    pe = sorted(
        (s for s in store.strike_states if s.option_type is OptionType.PE),
        key=lambda s: distance(s.strike),
    )[:_CHAIN_PER_SIDE]

    nearest = sorted(ce + pe, key=lambda s: (s.strike, s.option_type.value))

    rows: list[OptionChainRow] = []
    for state in nearest:
        key = (state.strike, state.option_type)
        rows.append(
            OptionChainRow(
                strike=state.strike,
                option_type=state.option_type,
                premium=state.current_premium,
                oi=state.current_oi,
                oi_change=state.oi_change,
                volume=state.current_volume,
                classification=classification_by_key.get(key),
                unusual_flags=unusual_by_key.get(key, []),
                recommendation_flag=key in recommended,
            )
        )
    return rows


def _recommended_keys(
    qualification: TradeQualification | None,
) -> set[tuple[Decimal, OptionType]]:
    """Return the (strike, option_type) of the qualified trade, if any."""
    if qualification is None or qualification.strike is None:
        return set()
    if qualification.option_type is None:
        return set()
    return {(qualification.strike, qualification.option_type)}


def _engine_status(store: EngineStore, now: dt.datetime) -> EngineStatus:
    """Build the engine-status section."""
    data_age_seconds: float | None = None
    if store.last_poll_at is not None:
        data_age_seconds = round((now - store.last_poll_at).total_seconds(), 3)

    healthy = (
        store.engine_running
        and store.last_error is None
        and store.last_poll_at is not None
    )

    return EngineStatus(
        healthy=healthy,
        pipeline_runtime_ms=store.last_pipeline_runtime_ms,
        data_age_seconds=data_age_seconds,
    )
