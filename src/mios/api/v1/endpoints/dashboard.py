"""Dashboard endpoint.

A single, thin aggregation over the latest pipeline execution held in the
shared engine store. It runs no analysis and triggers no pipeline run — it
reads what the background poll loop already produced — so one request maps to
one already-computed pipeline execution and one response. Always returns 200
with a well-formed envelope; when no poll has completed yet, sections are null
or empty and `engine.healthy` is false.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from mios.schemas.dashboard import DashboardResponse
from mios.services.options_intel.dashboard import build_dashboard
from mios.services.options_intel.runtime import get_store
from mios.services.options_intel.store import EngineStore

router = APIRouter(tags=["dashboard"])

StoreDep = Annotated[EngineStore, Depends(get_store)]


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(store: StoreDep) -> DashboardResponse:
    """Return the full dashboard state from the latest pipeline execution."""
    return build_dashboard(store)
