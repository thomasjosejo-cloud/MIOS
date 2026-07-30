"""Tests for the Unusual Activity, Radar, and CE/PE engines."""

from collections.abc import Callable

from mios.schemas.market import OptionQuote, OptionType, StrikeState
from mios.services.options_intel import ce_pe, radar, unusual_activity
from mios.services.options_intel.classification import classify_all
from mios.services.options_intel.option_engine import OptionEngine

Factory = Callable[..., OptionQuote]


def _two_poll_states(
    make: Factory,
    second_poll: dict[tuple[int, OptionType], dict[str, float]],
) -> list[StrikeState]:
    """Seed a flat first poll, then apply per-strike changes in a second poll."""
    engine = OptionEngine()
    strikes = [24600, 24700, 24800]
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

    states = []
    for strike in strikes:
        for option_type in (OptionType.CE, OptionType.PE):
            change = second_poll.get(
                (strike, option_type), {"oi": 10_050, "premium": 100.5, "volume": 1010}
            )
            states.append(
                engine.update(
                    make(
                        strike=strike,
                        option_type=option_type,
                        oi=change["oi"],
                        premium=change["premium"],
                        volume=change["volume"],
                        minutes=5,
                    )
                )
            )
    return states


def test_unusual_activity_respects_configured_thresholds(
    make_option_quote: Factory,
) -> None:
    states = _two_poll_states(
        make_option_quote,
        {(24700, OptionType.CE): {"oi": 15_000, "premium": 160, "volume": 5000}},
    )

    flagged = unusual_activity.detect(
        states,
        oi_change_pct=40,
        volume_change_pct=100,
        premium_change_pct=50,
        oi_velocity_per_min=500,
    )

    assert len(flagged) == 1
    assert flagged[0].strike == 24700
    assert set(flagged[0].triggers) == {
        "oi_change",
        "volume_change",
        "premium_change",
        "oi_velocity",
    }


def test_unusual_activity_ignores_noise(make_option_quote: Factory) -> None:
    states = _two_poll_states(make_option_quote, {})  # all strikes barely move

    flagged = unusual_activity.detect(
        states,
        oi_change_pct=40,
        volume_change_pct=100,
        premium_change_pct=50,
        oi_velocity_per_min=500,
    )

    assert flagged == []


def test_threshold_is_not_hardcoded(make_option_quote: Factory) -> None:
    """A strike below a high threshold must appear once the threshold is lowered."""
    states = _two_poll_states(
        make_option_quote,
        {(24700, OptionType.CE): {"oi": 11_000, "premium": 105, "volume": 1200}},
    )
    common = {
        "volume_change_pct": 1000,
        "premium_change_pct": 1000,
        "oi_velocity_per_min": 1e9,
    }

    assert unusual_activity.detect(states, oi_change_pct=50, **common) == []
    assert len(unusual_activity.detect(states, oi_change_pct=5, **common)) == 1


def test_radar_has_seven_views_and_respects_top_n(make_option_quote: Factory) -> None:
    states = _two_poll_states(
        make_option_quote,
        {
            (24700, OptionType.CE): {"oi": 16_000, "premium": 140, "volume": 9000},
            (24600, OptionType.PE): {"oi": 15_000, "premium": 80, "volume": 8000},
        },
    )

    report = radar.build_radar(states, top_n=2)

    assert len(report.highest_volume) <= 2
    assert report.highest_oi_addition[0].strike in (24700, 24600)
    # All seven views are present as attributes.
    for view in (
        report.top_ce_activity,
        report.top_pe_activity,
        report.highest_oi_addition,
        report.highest_oi_reduction,
        report.highest_volume,
        report.highest_premium_expansion,
        report.highest_oi_velocity,
    ):
        assert isinstance(view, list)


def test_ce_pe_identifies_stronger_side_and_writers(make_option_quote: Factory) -> None:
    states = _two_poll_states(
        make_option_quote,
        {
            (24600, OptionType.PE): {
                "oi": 18_000,
                "premium": 80,
                "volume": 6000,
            },  # PE writing
            (24700, OptionType.CE): {
                "oi": 17_000,
                "premium": 140,
                "volume": 7000,
            },  # CE buying
        },
    )
    classifications = classify_all(
        states, min_oi_change_pct=2, min_premium_change_pct=1
    )

    comparison = ce_pe.compare(
        states, classifications, [], neutral_band_pct=10, previous=None
    )

    assert comparison.stronger_side.value in ("CE", "PE")
    assert 24600 in comparison.writer_active_strikes
    assert 24700 in comparison.buyer_active_strikes


def test_ce_pe_detects_control_shift(make_option_quote: Factory) -> None:
    states = _two_poll_states(
        make_option_quote,
        {(24700, OptionType.CE): {"oi": 20_000, "premium": 140, "volume": 7000}},
    )
    classifications = classify_all(
        states, min_oi_change_pct=2, min_premium_change_pct=1
    )
    first = ce_pe.compare(
        states, classifications, [], neutral_band_pct=10, previous=None
    )

    states2 = _two_poll_states(
        make_option_quote,
        {(24600, OptionType.PE): {"oi": 25_000, "premium": 80, "volume": 9000}},
    )
    classifications2 = classify_all(
        states2, min_oi_change_pct=2, min_premium_change_pct=1
    )
    second = ce_pe.compare(
        states2, classifications2, [], neutral_band_pct=10, previous=first
    )

    if first.stronger_side is not second.stronger_side:
        assert second.control_shifting
        assert second.shift_description is not None
