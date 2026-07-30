"""API v1 router."""

from fastapi import APIRouter

from mios.api.v1.endpoints.health import router as health_router
from mios.api.v1.endpoints.market import router as market_router

router = APIRouter()
router.include_router(health_router)
router.include_router(market_router)
