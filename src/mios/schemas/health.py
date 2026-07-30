"""Health response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Operational status of the application."""

    status: str
    application: str
    version: str
