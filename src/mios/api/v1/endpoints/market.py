"""Options intelligence endpoints.

All endpoints read the latest engine output from the shared in-memory store.
When the engine has not yet produced a given view (no poll has completed, or
the engine is disabled), the analysis endpoints return 503 rather than a
misleading empty body — except `/market/status`, which always reports the
engine's current operational state.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from mios.config import Settings, get_settings
from mios.schemas.market import (
    MarketContext,
    MarketStatusReport,
    OptionsReport,
    RadarReport,
    StructureReport,
    TradeQualification,
)
from mios.services.options_intel.market_hours import is_market_open
from mios.services.options_intel.runtime import get_store
from mios.services.options_intel.store import EngineStore

router = APIRouter(prefix="/market", tags=["market"])

StoreDep = Annotated[EngineStore, Depends(get_store)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

_NOT_READY = "Engine has not produced this view yet; check /market/status"


def _require(value: object) -> None:
    """Raise 503 when a required engine output is not yet available."""
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=_NOT_READY
        )


@router.get("/context", response_model=MarketContext)
async def market_context(store: StoreDep) -> MarketContext:
    """Return the synthesized, evidence-backed market context."""
    _require(store.context)
    assert store.context is not None
    return store.context


@router.get("/options", response_model=OptionsReport)
async def market_options(store: StoreDep) -> OptionsReport:
    """Return per-strike options positioning: state, classification, and CE/PE."""
    _require(store.cepe)
    assert store.cepe is not None
    return OptionsReport(
        spot_price=store.spot_price,
        strikes=store.strike_states,
        classifications=store.classifications,
        unusual_activity=store.unusual,
        ce_pe=store.cepe,
    )


@router.get("/recommendation", response_model=TradeQualification)
async def market_recommendation(store: StoreDep) -> TradeQualification:
    """Return the trade qualification: gates, confidence, and the decision."""
    _require(store.qualification)
    assert store.qualification is not None
    return store.qualification


@router.get("/radar", response_model=RadarReport)
async def market_radar(store: StoreDep) -> RadarReport:
    """Return the seven ranked options activity views."""
    _require(store.radar)
    assert store.radar is not None
    return store.radar


@router.get("/structure", response_model=StructureReport)
async def market_structure(store: StoreDep) -> StructureReport:
    """Return price structure and momentum."""
    _require(store.structure)
    _require(store.momentum)
    assert store.structure is not None
    assert store.momentum is not None
    return StructureReport(structure=store.structure, momentum=store.momentum)


@router.get("/status", response_model=MarketStatusReport)
async def market_status(store: StoreDep, settings: SettingsDep) -> MarketStatusReport:
    """Return the engine and market operational status. Always available."""
    session = "open" if is_market_open(settings) else "closed"
    return MarketStatusReport(
        market_open=store.market_open,
        session=session,
        spot_price=store.spot_price,
        engine_running=store.engine_running,
        last_poll_at=store.last_poll_at,
        last_error=store.last_error,
    )
