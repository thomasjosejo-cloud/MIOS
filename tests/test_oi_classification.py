"""Tests for the Classification Engine."""

from collections.abc import Callable

import pytest

from mios.schemas.market import (
    Classification,
    OptionQuote,
    OptionType,
    StrikeState,
)
from mios.services.options_intel.classification import classify
from mios.services.options_intel.option_engine import OptionEngine

Factory = Callable[..., OptionQuote]


def _second_state(
    make: Factory, *, oi: int, premium: float, volume: int = 2000
) -> StrikeState:
    engine = OptionEngine()
    engine.update(
        make(
            strike=24700, option_type=OptionType.CE, oi=10_000, premium=100, volume=1000
        )
    )
    return engine.update(
        make(
            strike=24700,
            option_type=OptionType.CE,
            oi=oi,
            premium=premium,
            volume=volume,
            minutes=5,
        )
    )


@pytest.mark.parametrize(
    ("oi", "premium", "expected"),
    [
        (13_000, 130, Classification.LONG_BUILDUP),  # OI up, premium up
        (13_000, 70, Classification.SHORT_BUILDUP),  # OI up, premium down
        (7_000, 70, Classification.LONG_UNWINDING),  # OI down, premium down
        (7_000, 130, Classification.SHORT_COVERING),  # OI down, premium up
    ],
)
def test_four_classifications(
    make_option_quote: Factory, oi: int, premium: float, expected: Classification
) -> None:
    state = _second_state(make_option_quote, oi=oi, premium=premium)
    result = classify(state, min_oi_change_pct=2, min_premium_change_pct=1)

    assert result is not None
    assert result.classification is expected


def test_long_buildup_evidence_and_reason(make_option_quote: Factory) -> None:
    state = _second_state(make_option_quote, oi=13_000, premium=130)
    result = classify(state, min_oi_change_pct=2, min_premium_change_pct=1)

    assert result is not None
    assert any("OI ↑" in item for item in result.evidence)
    assert any("Premium ↑" in item for item in result.evidence)
    assert "open interest and premium" in result.reason


def test_no_classification_below_noise_floor(make_option_quote: Factory) -> None:
    state = _second_state(
        make_option_quote, oi=10_100, premium=100.5
    )  # ~1% OI, 0.5% prem

    assert classify(state, min_oi_change_pct=2, min_premium_change_pct=1) is None


def test_first_observation_is_not_classified(make_option_quote: Factory) -> None:
    engine = OptionEngine()
    state = engine.update(make_option_quote(strike=24700, option_type=OptionType.CE))

    assert classify(state, min_oi_change_pct=2, min_premium_change_pct=1) is None
