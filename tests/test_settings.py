"""Tests for configuration loading and validation."""

from typing import Any

import pytest
from pydantic import ValidationError

from mios.config import Settings, get_settings
from mios.config.constants import API_V1_PREFIX, APP_NAME, Environment


def test_settings_come_from_env_test(settings: Settings) -> None:
    assert settings.APP_ENV is Environment.TESTING
    assert settings.DEBUG is False
    assert settings.LOG_LEVEL == "WARNING"
    assert settings.PORT == 8001
    assert settings.STARTUP_VALIDATION is False


def test_constant_defaults_are_applied(settings: Settings) -> None:
    assert settings.APP_NAME == APP_NAME
    assert settings.API_PREFIX == API_V1_PREFIX


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()


def test_database_dsn_uses_async_driver(settings: Settings) -> None:
    assert settings.database_dsn.startswith("postgresql+psycopg://")
    assert f"/{settings.POSTGRES_DB}" in settings.database_dsn


def test_database_dsn_embeds_credentials() -> None:
    settings = Settings(
        POSTGRES_HOST="db.internal",
        POSTGRES_PORT=6543,
        POSTGRES_USER="alice",
        POSTGRES_PASSWORD="s3cret",
        POSTGRES_DB="mios_prod",
    )

    assert settings.database_dsn == (
        "postgresql+psycopg://alice:s3cret@db.internal:6543/mios_prod"
    )


def test_secrets_are_not_exposed_by_model_dump() -> None:
    dumped = str(Settings(POSTGRES_PASSWORD="s3cret").model_dump())

    assert "s3cret" not in dumped


def test_redis_dsn_without_password(settings: Settings) -> None:
    assert settings.redis_dsn == (
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    )


def test_redis_dsn_with_password() -> None:
    settings = Settings(
        REDIS_HOST="cache", REDIS_PORT=6379, REDIS_DB=0, REDIS_PASSWORD="pw"
    )

    assert settings.redis_dsn == "redis://:pw@cache:6379/0"


def test_nats_servers_accept_comma_separated_list() -> None:
    settings = Settings(NATS_SERVERS="nats://a:4222, nats://b:4222")

    assert settings.NATS_SERVERS == ["nats://a:4222", "nats://b:4222"]


def test_is_production() -> None:
    assert Settings(APP_ENV="production").is_production is True
    assert Settings(APP_ENV="development").is_production is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("PORT", 0),
        ("PORT", 70000),
        ("POSTGRES_PORT", -1),
        ("POSTGRES_POOL_SIZE", 0),
        ("POSTGRES_MAX_OVERFLOW", -1),
        ("POSTGRES_POOL_TIMEOUT", 0),
        ("REDIS_MAX_CONNECTIONS", 0),
        ("REDIS_DB", -1),
        ("NATS_MAX_RECONNECT_ATTEMPTS", -2),
        ("NATS_CONNECT_TIMEOUT", 0),
        ("LOG_LEVEL", "VERBOSE"),
        ("APP_ENV", "staging-2"),
        ("API_PREFIX", "api/v1"),
        ("API_PREFIX", "/api/v1/"),
    ],
)
def test_invalid_values_are_rejected(field: str, value: object) -> None:
    overrides: Any = {field: value}

    with pytest.raises(ValidationError):
        Settings(**overrides)
