"""Application settings loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from mios.config import constants


class Settings(BaseSettings):
    """Application configuration, sourced from environment variables or `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = constants.APP_NAME
    APP_VERSION: str = constants.APP_VERSION
    APP_ENV: str = "development"
    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    LOG_LEVEL: str = "INFO"

    API_PREFIX: str = constants.API_V1_PREFIX


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()
