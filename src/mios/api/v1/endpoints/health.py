"""Health endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from mios.config import Settings, get_settings
from mios.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    """Report that the application is operational."""
    return HealthResponse(
        status="healthy",
        application=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
