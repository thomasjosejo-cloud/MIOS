"""Tests for configuration loading."""

from mios.config import get_settings
from mios.config.constants import API_V1_PREFIX, APP_NAME


def test_settings_come_from_env_test() -> None:
    settings = get_settings()

    assert settings.APP_ENV == "test"
    assert settings.DEBUG is False
    assert settings.LOG_LEVEL == "WARNING"
    assert settings.PORT == 8001


def test_constant_defaults_are_applied() -> None:
    settings = get_settings()

    assert settings.APP_NAME == APP_NAME
    assert settings.API_PREFIX == API_V1_PREFIX
