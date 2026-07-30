"""Dashboard aggregation.

Assembles a `DashboardResponse` from the latest pipeline execution held in the
`EngineStore`. This is a thin projection: it performs no analysis and never
runs the pipeline — the background poll loop is the sole producer of the data
read here. The option-chain rows are a join over already-computed strike
states, classifications, unusual activity, and the recommendation's flagged
strikes.
"""

import datetime as dt
from decimal import Decimal

from mios.config.constants import AuthStatus
from mios.schemas.dashboard import (
    DashboardResponse,
    EngineStatus,
    MarketSection,
    OptionChainRow,
)
from mios.schemas.market import (
    Classification,
    OptionType,
    RecommendationReport,
)
from mios.services.options_intel.store import EngineStore


def build_dashboard(
    store: EngineStore, *, now: dt.datetime | None = None
) -> DashboardResponse:
    """Aggregate the store's latest pipeline outputs into one dashboard response."""
    now = now or dt.datetime.now(dt.UTC)

    return DashboardResponse(
        authentication=(
            AuthStatus.CONNECTED
            if store.authenticated
            else AuthStatus.NOT_AUTHENTICATED
        ),
        data_source=store.data_source,
        market=_market(store),
        recommendation=store.recommendation,
        no_trade=store.recommendation.no_trade if store.recommendation else None,
        context=store.context,
        ce_pe=store.cepe,
        top_candidates=(
            store.recommendation.top_candidates if store.recommendation else []
        ),
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


def _option_chain(store: EngineStore) -> list[OptionChainRow]:
    """Project each tracked strike into a dashboard row (no new calculations)."""
    classification_by_key: dict[tuple[Decimal, OptionType], Classification] = {
        (c.strike, c.option_type): c.classification for c in store.classifications
    }
    unusual_by_key: dict[tuple[Decimal, OptionType], list[str]] = {
        (u.strike, u.option_type): u.triggers for u in store.unusual
    }
    recommended = _recommended_keys(store.recommendation)

    rows: list[OptionChainRow] = []
    for state in store.strike_states:
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
    recommendation: RecommendationReport | None,
) -> set[tuple[Decimal, OptionType]]:
    """Collect the (strike, option_type) keys the recommendation flags."""
    if recommendation is None:
        return set()

    keys: set[tuple[Decimal, OptionType]] = set()
    for pick in (recommendation.best_ce, recommendation.best_pe):
        if pick is not None:
            keys.add((pick.strike, pick.option_type))
    for candidate in recommendation.top_candidates:
        keys.add((candidate.strike, candidate.option_type))
    return keys


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
