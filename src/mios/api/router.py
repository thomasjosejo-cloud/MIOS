"""Root API router aggregating all API versions."""

from fastapi import APIRouter

from mios.api.v1.router import router as v1_router

router = APIRouter()
router.include_router(v1_router)
