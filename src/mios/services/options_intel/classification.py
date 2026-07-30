"""Classification Engine.

Classifies a strike's positioning behaviour from the direction of its OI and
premium change. A strike is only classified once both changes clear their
configured noise floors — otherwise there is no real signal to classify, and
`None` is returned rather than forcing it into one of the four categories.
"""

from mios.schemas.market import Classification, ClassificationResult, StrikeState

_REASONS = {
    Classification.LONG_BUILDUP: (
        "Fresh long positions are being added: open interest and premium are "
        "both rising."
    ),
    Classification.SHORT_BUILDUP: (
        "Fresh short positions are being written: open interest is rising "
        "while premium falls."
    ),
    Classification.LONG_UNWINDING: (
        "Existing long positions are being closed: open interest and premium "
        "are both falling."
    ),
    Classification.SHORT_COVERING: (
        "Short positions are being covered: open interest is falling while "
        "premium rises."
    ),
}


def classify(
    state: StrikeState,
    *,
    min_oi_change_pct: float,
    min_premium_change_pct: float,
) -> ClassificationResult | None:
    """Classify a strike's positioning, or `None` if there is no clear signal."""
    if (
        state.oi_change_pct is None
        or state.premium_change_pct is None
        or abs(state.oi_change_pct) < min_oi_change_pct
        or abs(state.premium_change_pct) < min_premium_change_pct
    ):
        return None

    oi_up = state.oi_change > 0
    premium_up = state.premium_change > 0

    if oi_up and premium_up:
        classification = Classification.LONG_BUILDUP
    elif oi_up and not premium_up:
        classification = Classification.SHORT_BUILDUP
    elif not oi_up and not premium_up:
        classification = Classification.LONG_UNWINDING
    else:
        classification = Classification.SHORT_COVERING

    evidence = [
        f"OI {'↑' if oi_up else '↓'} {abs(state.oi_change_pct):.1f}%",
        f"Premium {'↑' if premium_up else '↓'} {abs(state.premium_change_pct):.1f}%",
    ]
    if state.volume_change_pct is not None:
        direction = "↑" if state.volume_change_pct >= 0 else "↓"
        evidence.append(f"Volume {direction} {abs(state.volume_change_pct):.1f}%")
    else:
        evidence.append("Volume unchanged")

    return ClassificationResult(
        strike=state.strike,
        option_type=state.option_type,
        classification=classification,
        evidence=evidence,
        reason=_REASONS[classification],
    )


def classify_all(
    states: list[StrikeState],
    *,
    min_oi_change_pct: float,
    min_premium_change_pct: float,
) -> list[ClassificationResult]:
    """Classify every strike, skipping those with no clear signal."""
    results = (
        classify(
            state,
            min_oi_change_pct=min_oi_change_pct,
            min_premium_change_pct=min_premium_change_pct,
        )
        for state in states
    )
    return [result for result in results if result is not None]
