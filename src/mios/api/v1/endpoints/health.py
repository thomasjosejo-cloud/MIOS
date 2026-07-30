"""Health endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from mios.config import Settings, get_settings
from mios.config.constants import ComponentStatus, HealthStatus
from mios.core.health import check_all
from mios.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": HealthResponse}},
)
async def health(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    """Report application and infrastructure status, verifying connectivity.

    Returns 503 when any component is unreachable, so orchestrators can treat
    the instance as not ready while still reading the detailed component report.
    """
    components = await check_all()
    degraded = any(
        component.status is ComponentStatus.DOWN for component in components.values()
    )

    if degraded:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status=HealthStatus.DEGRADED if degraded else HealthStatus.HEALTHY,
        application=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        components=components,
    )
