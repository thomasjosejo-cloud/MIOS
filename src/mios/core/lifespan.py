"""Application lifespan management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mios.config import get_settings
from mios.core.logging import get_logger
from mios.core.startup import connect_infrastructure, disconnect_infrastructure

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Connect infrastructure on startup and release it on shutdown."""
    settings = get_settings()

    logger.info("Application started")
    logger.info("Environment: %s", settings.APP_ENV)
    logger.info("Version: %s", settings.APP_VERSION)

    try:
        await connect_infrastructure(settings)
    except Exception:
        # Release whatever did connect before aborting startup.
        await disconnect_infrastructure()
        logger.exception("Startup failed")
        raise

    logger.info("Startup completed")

    yield

    await disconnect_infrastructure()
    logger.info("Shutdown completed")
    logger.info("Application stopped")
