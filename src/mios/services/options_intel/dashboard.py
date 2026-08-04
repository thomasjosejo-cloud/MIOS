"""Dashboard aggregation.

Assembles a `DashboardResponse` from the latest pipeline execution held in the
`EngineStore`. This is a thin projection: it performs no analysis and never runs
the pipeline. Beyond the raw engine outputs it adds the decision-centric
presentation — narrative and dominance (via `presentation`) — and trims the
option chain to the five CE and five PE strikes nearest the money.
"""

import datetime as dt
from decimal import Decimal

from mios.config import get_settings
from mios.config.constants import AuthStatus
from mios.core.logging import get_logger
from mios.schemas.dashboard import (
    DashboardResponse,
    EngineStatus,
    MarketDominance,
    MarketNarrative,
    MarketSection,
    OptionChainRow,
    ParticipationRow,
)
from mios.schemas.market import Classification, OptionType, TradeQualification
from mios.services.options_intel import consistency, presentation
from mios.services.options_intel.store import EngineStore

logger = get_logger(__name__)

#: Strikes to show per side around the money (Sprint 10.1: 5 CE + 5 PE).
_CHAIN_PER_SIDE = 5


def build_dashboard(
    store: EngineStore, *, now: dt.datetime | None = None
) -> DashboardResponse:
    """Aggregate the store's latest pipeline outputs into one dashboard response."""
    now = now or dt.datetime.now(dt.UTC)

    narrative = _narrative(store)
    dominance = _dominance(store)
    _log_consistency(store, dominance, narrative)

    return DashboardResponse(
        connection_state=store.connection_state,
        authentication=(
            AuthStatus.CONNECTED
            if store.authenticated
            else AuthStatus.NOT_AUTHENTICATED
        ),
        data_source=store.data_source,
        market=_market(store, get_settings().OPTION_STRIKE_STEP),
        narrative=narrative,
        dominance=dominance,
        qualification=store.qualification,
        participation=_participation(store),
        context=store.context,
        ce_pe=store.cepe,
        option_chain=_option_chain(store),
        engine=_engine_status(store, now),
    )


#: How many strongest-participation strikes the radar panel shows.
_PARTICIPATION_TOP_N = 8


def _participation(store: EngineStore) -> list[ParticipationRow]:
    """Rank strikes by fresh OI positioning (Radar engine's OI-addition order).

    Reuses the already-computed OI change to order strikes, and attaches each
    strike's existing classification and percentage changes. No new score or
    ranking metric is introduced — this is assembly of existing engine output.
    """
    classification_by_key: dict[tuple[Decimal, OptionType], Classification] = {
        (c.strike, c.option_type): c.classification for c in store.classifications
    }
    # Strongest fresh positioning first (largest OI addition), matching the
    # Radar engine's `highest_oi_addition` ordering.
    ranked = sorted(
        store.strike_states,
        key=lambda s: s.oi_change,
        reverse=True,
    )[:_PARTICIPATION_TOP_N]

    return [
        ParticipationRow(
            rank=index + 1,
            strike=state.strike,
            option_type=state.option_type,
            classification=classification_by_key.get((state.strike, state.option_type)),
            oi_change=state.oi_change,
            oi_change_pct=state.oi_change_pct,
            premium_change_pct=state.premium_change_pct,
            volume_change_pct=state.volume_change_pct,
        )
        for index, state in enumerate(ranked)
    ]


def _log_consistency(
    store: EngineStore,
    dominance: MarketDominance | None,
    narrative: MarketNarrative | None,
) -> None:
    """Run the pre-publish consistency validator; log any contradiction found.

    The dashboard is never blocked — this only surfaces contradictions so they
    are not silently published. With one canonical bias driving control, a
    warning here means a genuine regression to investigate.
    """
    if (
        store.bias is None
        or store.context is None
        or dominance is None
        or store.structure is None
        or store.qualification is None
        or narrative is None
    ):
        return
    warnings = consistency.check(
        bias=store.bias,
        context=store.context,
        dominance=dominance,
        structure=store.structure,
        qualification=store.qualification,
        narrative=narrative,
    )
    if warnings:
        logger.warning(
            "Dashboard consistency check flagged contradictions",
            extra={"contradictions": warnings},
        )


def _market(store: EngineStore, strike_step: int) -> MarketSection:
    """Build the market header.

    The day's change is measured against the previous trading day's close (from
    the feed), matching the exchange — never against the previous poll's price.
    `atm_strike` is the strike nearest spot on the strike ladder — the same
    `round(spot / step) * step` the audit and qualification paths already use —
    provided here purely to anchor the Participation Radar's ATM window.
    """
    spot = store.spot_price
    prev_close = store.spot_prev_close

    change: Decimal | None = None
    change_percent: float | None = None
    if spot is not None and prev_close is not None:
        change = spot - prev_close
        if prev_close != 0:
            change_percent = round(float(change / prev_close * 100), 2)

    atm_strike: Decimal | None = None
    if spot is not None and strike_step > 0:
        atm_strike = Decimal(round(spot / strike_step) * strike_step)

    return MarketSection(
        spot=spot,
        atm_strike=atm_strike,
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
    """Build the market-dominance view from the canonical market bias."""
    if store.bias is None:
        return None
    return presentation.build_dominance(
        store.bias,
        store.classifications,
        previous_control=store.previous_controlling_side,
    )


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
