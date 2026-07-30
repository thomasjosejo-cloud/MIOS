"""Tests for the Option Engine's per-strike state tracking."""

from collections.abc import Callable

from mios.schemas.market import OptionQuote, OptionType
from mios.services.options_intel.option_engine import OptionEngine

Factory = Callable[..., OptionQuote]


def test_first_observation_has_no_deltas(make_option_quote: Factory) -> None:
    engine = OptionEngine()
    state = engine.update(make_option_quote(strike=24700, option_type=OptionType.CE))

    assert state.is_first_observation
    assert state.oi_change == 0
    assert state.oi_change_pct is None
    assert state.oi_velocity_per_min is None


def test_second_observation_computes_deltas(make_option_quote: Factory) -> None:
    engine = OptionEngine()
    engine.update(
        make_option_quote(
            strike=24700, option_type=OptionType.CE, oi=10_000, premium=100
        )
    )
    state = engine.update(
        make_option_quote(
            strike=24700,
            option_type=OptionType.CE,
            oi=12_000,
            premium=120,
            volume=1_500,
            minutes=5,
        )
    )

    assert state.oi_change == 2_000
    assert state.oi_change_pct == 20.0
    assert state.premium_change_pct == 20.0
    assert state.volume_change == 500


def test_oi_velocity_is_per_minute(make_option_quote: Factory) -> None:
    engine = OptionEngine()
    engine.update(make_option_quote(strike=24700, option_type=OptionType.CE, oi=10_000))
    state = engine.update(
        make_option_quote(strike=24700, option_type=OptionType.CE, oi=13_000, minutes=5)
    )

    # 3000 over 5 minutes = 600 per minute.
    assert state.oi_velocity_per_min == 600.0
    assert state.seconds_since_update == 300.0


def test_pct_change_is_none_when_base_is_zero(make_option_quote: Factory) -> None:
    engine = OptionEngine()
    engine.update(make_option_quote(strike=24700, option_type=OptionType.CE, oi=0))
    state = engine.update(
        make_option_quote(strike=24700, option_type=OptionType.CE, oi=5_000, minutes=5)
    )

    assert state.oi_change == 5_000
    assert state.oi_change_pct is None


def test_snapshot_is_ordered_and_independent_per_strike(
    make_option_quote: Factory,
) -> None:
    engine = OptionEngine()
    engine.update(make_option_quote(strike=24800, option_type=OptionType.CE))
    engine.update(make_option_quote(strike=24700, option_type=OptionType.PE))
    engine.update(make_option_quote(strike=24700, option_type=OptionType.CE))

    snapshot = engine.snapshot()

    assert len(snapshot) == 3
    assert [(s.strike, s.option_type.value) for s in snapshot] == [
        (snapshot[0].strike, "CE"),
        (snapshot[1].strike, "PE"),
        (snapshot[2].strike, "CE"),
    ]
    assert snapshot[0].strike < snapshot[2].strike
