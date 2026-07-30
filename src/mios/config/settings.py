"""Application settings loaded from the environment.

Every deployment-specific value is defined here and read from the environment or
`.env`. Connection strings are derived, never hardcoded.
"""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from mios.config import constants
from mios.config.constants import Environment

Port = Annotated[int, Field(ge=1, le=65535)]
LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class Settings(BaseSettings):
    """Application configuration, sourced from environment variables or `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---------------------------------------------------------
    APP_NAME: str = constants.APP_NAME
    APP_VERSION: str = constants.APP_VERSION
    APP_ENV: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: Port = 8000

    API_PREFIX: str = constants.API_V1_PREFIX

    # --- Logging -------------------------------------------------------------
    LOG_LEVEL: LogLevel = "INFO"
    LOG_JSON: bool = False

    # --- Startup -------------------------------------------------------------
    #: When true, startup aborts if a mandatory infrastructure component is
    #: unreachable. Disabled in tests so the app boots without infrastructure.
    STARTUP_VALIDATION: bool = True

    # --- PostgreSQL ----------------------------------------------------------
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: Port = 5432
    POSTGRES_USER: str = "mios"
    POSTGRES_PASSWORD: SecretStr = SecretStr("mios")
    POSTGRES_DB: str = "mios"

    POSTGRES_POOL_SIZE: int = Field(default=10, ge=1)
    POSTGRES_MAX_OVERFLOW: int = Field(default=5, ge=0)
    POSTGRES_POOL_TIMEOUT: float = Field(default=30.0, gt=0)
    POSTGRES_POOL_RECYCLE: int = Field(default=1800, gt=0)
    POSTGRES_POOL_PRE_PING: bool = True
    POSTGRES_CONNECT_TIMEOUT: int = Field(default=10, gt=0)
    POSTGRES_ECHO: bool = False

    # --- TimescaleDB ---------------------------------------------------------
    #: Validate at startup that the TimescaleDB extension is available. No
    #: hypertables are created by this sprint.
    TIMESCALEDB_ENABLED: bool = True

    # --- Redis ---------------------------------------------------------------
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: Port = 6379
    REDIS_DB: int = Field(default=0, ge=0)
    REDIS_PASSWORD: SecretStr | None = None
    REDIS_MAX_CONNECTIONS: int = Field(default=20, ge=1)
    REDIS_SOCKET_TIMEOUT: float = Field(default=5.0, gt=0)
    REDIS_CONNECT_TIMEOUT: float = Field(default=5.0, gt=0)

    # --- NATS JetStream ------------------------------------------------------
    # NoDecode suppresses pydantic-settings' JSON decoding so the validator below
    # can accept a plain comma-separated value from the environment.
    NATS_SERVERS: Annotated[list[str], NoDecode] = ["nats://127.0.0.1:4222"]
    NATS_CONNECT_TIMEOUT: float = Field(default=5.0, gt=0)
    NATS_MAX_RECONNECT_ATTEMPTS: int = Field(default=-1, ge=-1)
    NATS_RECONNECT_TIME_WAIT: float = Field(default=2.0, gt=0)
    NATS_PING_INTERVAL: int = Field(default=30, gt=0)

    @field_validator("NATS_SERVERS", mode="before")
    @classmethod
    def _split_servers(cls, value: object) -> object:
        """Accept a comma-separated server list from the environment."""
        if isinstance(value, str) and not value.strip().startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("API_PREFIX")
    @classmethod
    def _validate_prefix(cls, value: str) -> str:
        """Require a rooted, non-trailing-slash mount point."""
        if not value.startswith("/") or (len(value) > 1 and value.endswith("/")):
            msg = "API_PREFIX must start with '/' and not end with '/'"
            raise ValueError(msg)
        return value

    # DSNs are plain properties, not computed fields, so the embedded
    # credentials never appear in `model_dump()` output or logs.
    @property
    def database_dsn(self) -> str:
        """Async SQLAlchemy DSN for PostgreSQL."""
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return (
            f"{constants.POSTGRES_ASYNC_DRIVER}://"
            f"{self.POSTGRES_USER}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_dsn(self) -> str:
        """Redis connection URL."""
        auth = (
            f":{self.REDIS_PASSWORD.get_secret_value()}@" if self.REDIS_PASSWORD else ""
        )
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def is_production(self) -> bool:
        """Whether the application is running in production."""
        return self.APP_ENV is Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()
