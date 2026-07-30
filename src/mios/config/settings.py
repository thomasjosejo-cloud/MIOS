"""Application settings loaded from the environment.

Every deployment-specific value is defined here and read from the environment or
`.env`. Connection strings are derived, never hardcoded.
"""

from functools import lru_cache
from typing import Annotated, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

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

    # --- Fyers integration -----------------------------------------------------
    #: Master switch for the live options intelligence engine. Off by default so
    #: the application, tests, and environments without Fyers credentials are
    #: unaffected; enabling it without credentials fails fast at startup.
    OPTIONS_ENGINE_ENABLED: bool = False

    FYERS_CLIENT_ID: str | None = None
    FYERS_SECRET_KEY: SecretStr | None = None
    FYERS_REDIRECT_URI: str | None = None
    #: Obtained once via the OAuth exchange (see `mios.integrations.fyers.auth`)
    #: and supplied back to the application as a normal secret from then on.
    FYERS_ACCESS_TOKEN: SecretStr | None = None
    FYERS_REQUEST_TIMEOUT: float = Field(default=10.0, gt=0)

    # --- Instrument scope --------------------------------------------------------
    NIFTY_SPOT_SYMBOL: str = "NSE:NIFTY50-INDEX"
    OPTION_STRIKE_STEP: int = Field(default=50, gt=0)
    #: Strikes tracked on each side of the at-the-money strike. Matches Fyers'
    #: `strikecount` option-chain parameter.
    OPTION_STRIKE_COUNT: int = Field(default=10, gt=0)
    #: Expiry timestamp (epoch seconds) to request. `None` means the nearest
    #: expiry, per the Fyers option-chain API.
    OPTION_EXPIRY_TIMESTAMP: int | None = None

    # --- Live engine ---------------------------------------------------------
    ENGINE_POLL_INTERVAL_SECONDS: float = Field(default=15.0, gt=0)
    CANDLE_RESOLUTION_MINUTES: int = Field(default=5, gt=0)
    #: Number of candles fetched per poll for structure/momentum analysis.
    CANDLE_LOOKBACK_COUNT: int = Field(default=60, ge=10)

    # --- Market hours ----------------------------------------------------------
    MARKET_OPEN_TIME: str = "09:15"
    MARKET_CLOSE_TIME: str = "15:30"
    MARKET_TIMEZONE: str = "Asia/Kolkata"

    # --- Unusual activity thresholds ------------------------------------------
    #: Percentage change thresholds, e.g. 100.0 means a 100% change. Never
    #: hardcoded in engine logic — always read from here.
    UNUSUAL_OI_CHANGE_PCT: float = Field(default=100.0, gt=0)
    UNUSUAL_VOLUME_CHANGE_PCT: float = Field(default=100.0, gt=0)
    UNUSUAL_PREMIUM_CHANGE_PCT: float = Field(default=50.0, gt=0)
    UNUSUAL_OI_VELOCITY_PER_MIN: float = Field(default=5000.0, gt=0)

    # --- Classification noise floor --------------------------------------------
    #: Minimum change required before a strike is classified at all. Below
    #: this, the change is noise rather than a build-up/unwinding signal.
    CLASSIFICATION_MIN_OI_CHANGE_PCT: float = Field(default=2.0, ge=0)
    CLASSIFICATION_MIN_PREMIUM_CHANGE_PCT: float = Field(default=1.0, ge=0)

    # --- Structure engine ------------------------------------------------------
    #: Candles required on each side of a point for it to count as a swing.
    STRUCTURE_SWING_LOOKBACK: int = Field(default=2, ge=1)

    # --- Momentum engine ---------------------------------------------------------
    MOMENTUM_LOOKBACK_CANDLES: int = Field(default=5, ge=2)
    #: Relative change in slope magnitude that counts as acceleration or
    #: deceleration, e.g. 0.2 means a 20% change in the rate of movement.
    MOMENTUM_ACCELERATION_THRESHOLD: float = Field(default=0.2, gt=0)

    # --- CE/PE engine ------------------------------------------------------------
    #: Net OI-change gap (as a fraction of the larger side) below which CE and
    #: PE are considered balanced rather than one side being stronger.
    CE_PE_NEUTRAL_BAND_PCT: float = Field(default=10.0, ge=0)

    # --- Radar -------------------------------------------------------------------
    RADAR_TOP_N: int = Field(default=5, ge=1)

    # --- Recommendation engine ---------------------------------------------------
    RECOMMENDATION_TOP_N: int = Field(default=5, ge=1)
    #: Minimum number of supporting evidence factors before a strike is
    #: eligible to be recommended at all.
    RECOMMENDATION_MIN_EVIDENCE: int = Field(default=2, ge=1)

    # --- No-Trade engine -----------------------------------------------------
    #: Rank gap (out of the evidence-factor count) below which the best CE and
    #: best PE are considered conflicting rather than one side leading.
    NO_TRADE_RANK_TIE_MARGIN: int = Field(default=1, ge=0)
    #: Number of independent negative conditions required before the engine
    #: declares NO TRADE, so a single flaky signal cannot trigger it alone.
    NO_TRADE_MIN_REASONS: int = Field(default=2, ge=1)

    @field_validator("MARKET_OPEN_TIME", "MARKET_CLOSE_TIME")
    @classmethod
    def _validate_market_time(cls, value: str) -> str:
        """Require 24-hour `HH:MM` formatted market hours."""
        try:
            hour, minute = value.split(":")
            if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                raise ValueError
        except ValueError as error:
            msg = f"Expected HH:MM, got {value!r}"
            raise ValueError(msg) from error
        return value

    @field_validator("MARKET_TIMEZONE")
    @classmethod
    def _validate_timezone(cls, value: str) -> str:
        """Require a valid IANA timezone name."""
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            msg = f"Unknown IANA timezone: {value!r}"
            raise ValueError(msg) from error
        return value

    @property
    def fyers_configured(self) -> bool:
        """Whether enough Fyers configuration is present to make API calls."""
        return bool(self.FYERS_CLIENT_ID and self.FYERS_ACCESS_TOKEN)

    @property
    def is_production(self) -> bool:
        """Whether the application is running in production."""
        return self.APP_ENV is Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()
