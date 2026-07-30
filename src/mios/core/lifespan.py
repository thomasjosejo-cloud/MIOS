"""Application lifespan management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mios.config import get_settings
from mios.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Log application startup and shutdown."""
    settings = get_settings()

    logger.info("Application started")
    logger.info("Environment: %s", settings.APP_ENV)
    logger.info("Version: %s", settings.APP_VERSION)

    yield

    logger.info("Application stopped")
