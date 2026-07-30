"""MIOS application entrypoint."""

from fastapi import FastAPI

from mios.api.router import router as api_router
from mios.config import get_settings
from mios.config.constants import APP_DESCRIPTION
from mios.core.lifespan import lifespan
from mios.core.logging import configure_logging


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL, json_format=settings.LOG_JSON)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=APP_DESCRIPTION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()
