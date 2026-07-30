"""Health response schemas."""

from pydantic import BaseModel

from mios.config.constants import ComponentStatus, HealthStatus


class ComponentHealth(BaseModel):
    """Operational status of a single infrastructure component."""

    name: str
    status: ComponentStatus
    latency_ms: float


class HealthResponse(BaseModel):
    """Operational status of the application and its infrastructure."""

    status: HealthStatus
    application: str
    version: str
    environment: str
    components: dict[str, ComponentHealth]
