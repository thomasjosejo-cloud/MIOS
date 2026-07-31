"""Tests for the Context engine.

The Recommendation and No-Trade engines these tests once covered were replaced
by the Trade Qualification Engine (Sprint 10); see `test_oi_qualification.py`.
"""

from collections.abc import Callable
from decimal import Decimal

from mios.schemas.market import (
    Candle,
    ControllingSide,
    OptionQuote,
    OptionType,
    StrikeState,
    TrendDirection,
)
from mios.services.options_intel import (
    ce_pe,
    unusual_activity,
)
from mios.services.options_intel import (
    context as context_engine,
)
from mios.services.options_intel import (
    momentum as momentum_engine,
)
from mios.services.options_intel import (
    structure as structure_engine,
)
from mios.services.options_intel.classification import classify_all
from mios.services.options_intel.option_engine import OptionEngine

QuoteFactory = Callable[..., OptionQuote]
CandleFactory = Callable[[list[float]], list[Candle]]


def _bullish_states(make: QuoteFactory) -> list[StrikeState]:
    """Put writing at 24600 (support) and call buying at 24800 (above spot 24750)."""
    engine = OptionEngine()
    strikes = [24600, 24700, 24750, 24800]
    for strike in strikes:
        for option_type in (OptionType.CE, OptionType.PE):
            engine.update(
                make(
                    strike=strike,
                    option_type=option_type,
                    oi=10_000,
                    premium=100,
                    volume=1000,
                )
            )

    changes = {
        (24600, OptionType.PE): {"oi": 18_000, "premium": 80, "volume": 6000},
        (24800, OptionType.CE): {"oi": 17_000, "premium": 140, "volume": 7000},
    }
    states = []
    for strike in strikes:
        for option_type in (OptionType.CE, OptionType.PE):
            c = changes.get(
                (strike, option_type), {"oi": 10_050, "premium": 100.5, "volume": 1010}
            )
            states.append(
                engine.update(
                    make(
                        strike=strike,
                        option_type=option_type,
                        oi=c["oi"],
                        premium=c["premium"],
                        volume=c["volume"],
                        minutes=5,
                    )
                )
            )
    return states


def test_context_is_evidence_backed_and_names_control(
    make_option_quote: QuoteFactory,
    make_candles: CandleFactory,
    zigzag_uptrend_closes: list[float],
) -> None:
    states = _bullish_states(make_option_quote)
    classifications = classify_all(
        states, min_oi_change_pct=2, min_premium_change_pct=1
    )
    unusual = unusual_activity.detect(
        states,
        oi_change_pct=40,
        volume_change_pct=100,
        premium_change_pct=20,
        oi_velocity_per_min=500,
    )
    cepe = ce_pe.compare(
        states, classifications, unusual, neutral_band_pct=10, previous=None
    )
    candles = make_candles(zigzag_uptrend_closes)
    structure = structure_engine.analyze(candles, swing_lookback=2)
    momentum = momentum_engine.analyze(
        candles, structure, lookback=5, acceleration_threshold=0.2
    )

    context = context_engine.build_context(
        cepe, structure, momentum, classifications, spot=Decimal(24750)
    )

    assert context.controlling_side is ControllingSide.BULLS
    assert context.evidence  # never empty
    assert any("Put Writing" in s for s in context.statements)
    assert any("Call Buying" in s for s in context.statements)


def test_context_flags_contradiction(
    make_option_quote: QuoteFactory, make_candles: CandleFactory
) -> None:
    # Bullish options activity but a downtrend in price structure.
    states = _bullish_states(make_option_quote)
    classifications = classify_all(
        states, min_oi_change_pct=2, min_premium_change_pct=1
    )
    cepe = ce_pe.compare(
        states, classifications, [], neutral_band_pct=10, previous=None
    )

    down_closes: list[int] = []
    points = [24800, 24700, 24760, 24620, 24680, 24540]
    for i in range(len(points) - 1):
        s, e = points[i], points[i + 1]
        down_closes.extend(range(s, e, 1 if e > s else -1))
    down_closes.append(points[-1])
    candles = make_candles([float(c) for c in down_closes])
    structure = structure_engine.analyze(candles, swing_lookback=2)
    momentum = momentum_engine.analyze(
        candles, structure, lookback=5, acceleration_threshold=0.2
    )

    context = context_engine.build_context(
        cepe, structure, momentum, classifications, spot=Decimal(24750)
    )

    if (
        structure.trend is TrendDirection.DOWNTREND
        and context.controlling_side is ControllingSide.BULLS
    ):
        assert context.contradiction is not None
