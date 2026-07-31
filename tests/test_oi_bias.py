"""Sprint 11 tests for the Bias Engine — the single canonical market control.

These lock in the eight-branch classification->sentiment table and the rule
that control is decided from classification-resolved sentiment weighted by OI
change, never from raw OI direction.
"""

import datetime as dt
from decimal import Decimal

import pytest

from mios.schemas.market import (
    Classification,
    ClassificationResult,
    ControllingSide,
    OptionType,
    Sentiment,
    StrikeState,
)
from mios.services.options_intel import bias as bias_engine

_T0 = dt.datetime(2026, 1, 1, 10, 0, tzinfo=dt.UTC)


def _state(strike: int, ot: OptionType, *, oi_change: int) -> StrikeState:
    return StrikeState(
        strike=Decimal(strike),
        option_type=ot,
        expiry=dt.date(2026, 1, 8),
        current_oi=100_000 + oi_change,
        previous_oi=100_000,
        oi_change=oi_change,
        oi_change_pct=round(oi_change / 100_000 * 100, 1),
        current_premium=Decimal(100),
        previous_premium=Decimal(100),
        premium_change=Decimal(0),
        premium_change_pct=0.0,
        current_volume=1000,
        previous_volume=900,
        volume_change=100,
        volume_change_pct=11.0,
        last_updated=_T0,
        seconds_since_update=5.0,
    )


def _cls(strike: int, ot: OptionType, c: Classification) -> ClassificationResult:
    return ClassificationResult(
        strike=Decimal(strike),
        option_type=ot,
        classification=c,
        evidence=["x"],
        reason="r",
    )


# --- The canonical eight-branch sentiment table ------------------------------


@pytest.mark.parametrize(
    ("option_type", "classification", "expected"),
    [
        (OptionType.CE, Classification.LONG_BUILDUP, Sentiment.BULLISH),
        (OptionType.CE, Classification.SHORT_COVERING, Sentiment.BULLISH),
        (OptionType.CE, Classification.SHORT_BUILDUP, Sentiment.BEARISH),
        (OptionType.CE, Classification.LONG_UNWINDING, Sentiment.BEARISH),
        (OptionType.PE, Classification.SHORT_BUILDUP, Sentiment.BULLISH),
        (OptionType.PE, Classification.LONG_UNWINDING, Sentiment.BULLISH),
        (OptionType.PE, Classification.LONG_BUILDUP, Sentiment.BEARISH),
        (OptionType.PE, Classification.SHORT_COVERING, Sentiment.BEARISH),
    ],
)
def test_sentiment_table_is_canonical(
    option_type: OptionType, classification: Classification, expected: Sentiment
) -> None:
    assert bias_engine.sentiment_of(option_type, classification) is expected


# --- The reported defect: put writing must read bullish ----------------------


def test_put_writing_is_bullish_not_bearish() -> None:
    # PE Short Build with a huge OI addition — the exact case that used to be
    # mislabeled "PE dominance = bears" by the old raw-OI logic.
    classifications = [
        _cls(24300, OptionType.PE, Classification.SHORT_BUILDUP),
        _cls(24350, OptionType.PE, Classification.SHORT_BUILDUP),
    ]
    states = [
        _state(24300, OptionType.PE, oi_change=300_000),
        _state(24350, OptionType.PE, oi_change=360_000),
    ]

    bias = bias_engine.assess(classifications, states, neutral_band_pct=10)

    assert bias.controlling_side is ControllingSide.BULLS
    assert bias.bull_score == pytest.approx(660_000)
    assert bias.bear_score == 0


def test_weight_is_oi_change_magnitude() -> None:
    classifications = [_cls(24700, OptionType.CE, Classification.LONG_BUILDUP)]
    states = [_state(24700, OptionType.CE, oi_change=45_000)]

    bias = bias_engine.assess(classifications, states, neutral_band_pct=10)

    assert bias.contributions[0].sentiment is Sentiment.BULLISH
    assert bias.contributions[0].weight == 45_000
    assert bias.contributions[0].signed_score == 45_000.0


def test_balanced_conviction_is_neutral() -> None:
    classifications = [
        _cls(24700, OptionType.CE, Classification.LONG_BUILDUP),  # bullish
        _cls(24750, OptionType.CE, Classification.SHORT_BUILDUP),  # bearish
    ]
    states = [
        _state(24700, OptionType.CE, oi_change=50_000),
        _state(24750, OptionType.CE, oi_change=50_000),
    ]

    bias = bias_engine.assess(classifications, states, neutral_band_pct=10)

    assert bias.controlling_side is ControllingSide.NEUTRAL
    assert bias.net_score == 0


def test_bearish_when_put_buying_dominates() -> None:
    classifications = [
        _cls(24700, OptionType.PE, Classification.LONG_BUILDUP),  # put buying = bearish
        _cls(
            24700, OptionType.CE, Classification.SHORT_BUILDUP
        ),  # call writing = bearish
    ]
    states = [
        _state(24700, OptionType.PE, oi_change=80_000),
        _state(24700, OptionType.CE, oi_change=40_000),
    ]

    bias = bias_engine.assess(classifications, states, neutral_band_pct=10)

    assert bias.controlling_side is ControllingSide.BEARS
    assert bias.bear_score == pytest.approx(120_000)


def test_no_classifications_is_neutral() -> None:
    bias = bias_engine.assess([], [], neutral_band_pct=10)

    assert bias.controlling_side is ControllingSide.NEUTRAL
    assert bias.bull_score == 0
    assert bias.bear_score == 0
    assert bias.contributions == []
