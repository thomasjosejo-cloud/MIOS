"""Trade Qualification Engine.

Replaces scattered recommendation rules with four transparent gates. A trade is
recommended only when every mandatory gate passes; otherwise the engine returns
NO_TRADE and lists exactly which gates failed and why. MIOS is willing to stand
aside indefinitely — qualified trades are the exception, not the goal.

    Gate 1  Market Regime         (weight 30, mandatory)  — from Structure
    Gate 2  Options Participation (weight 30, mandatory)  — from Classification
    Gate 3  CE vs PE Control      (weight 25, mandatory)  — from CE/PE
    Gate 4  Strike Quality        (weight 15)             — from the strike state

Confidence = sum of the weights of the passing gates (0-100). Because the three
mandatory gates must all pass for a BUY, a qualified trade is always High or
Very High confidence; marginal setups are NO_TRADE. Every gate reads existing
engine output only — no new market calculations are performed here.
"""

from decimal import Decimal

from mios.config import Settings
from mios.schemas.market import (
    BestCandidate,
    Classification,
    ClassificationResult,
    ConfidenceBand,
    ControllingSide,
    GateName,
    MarketBias,
    MarketContext,
    OptionType,
    QualificationGate,
    StrikeState,
    StructurePattern,
    StructureState,
    TradeDecision,
    TradeQualification,
    TrendDirection,
    UnusualActivity,
)

_WEIGHTS: dict[GateName, int] = {
    GateName.MARKET_REGIME: 30,
    GateName.OPTIONS_PARTICIPATION: 30,
    GateName.CE_PE_CONTROL: 25,
    GateName.STRIKE_QUALITY: 15,
}
_MANDATORY = {
    GateName.MARKET_REGIME,
    GateName.OPTIONS_PARTICIPATION,
    GateName.CE_PE_CONTROL,
}
#: Buy-side positioning: strikes worth buying show fresh longs or covering.
_BUY_CLASSIFICATIONS = (Classification.LONG_BUILDUP, Classification.SHORT_COVERING)


def qualify(
    classifications: list[ClassificationResult],
    unusual: list[UnusualActivity],
    strike_states: list[StrikeState],
    structure: StructureState,
    context: MarketContext,
    bias: MarketBias,
    *,
    spot: Decimal,
    settings: Settings,
) -> TradeQualification:
    """Evaluate the four gates and return the qualification decision.

    Direction and the control gate both read the canonical `bias`, so the trade
    MIOS qualifies always points the same way as the Dominance and Narrative.
    """
    states = {(s.strike, s.option_type): s for s in strike_states}
    unusual_strikes = {(u.strike, u.option_type) for u in unusual}

    # Direction comes from who controls the market (canonical Bias Engine).
    side = _direction(bias.controlling_side)

    # Candidate strikes: buy-side classifications on the controlling side,
    # ranked by liquidity so the best available strike leads.
    candidates = _candidates(classifications, states, side)
    chosen = candidates[0] if candidates else None
    chosen_state = states.get((chosen.strike, chosen.option_type)) if chosen else None

    gates = [
        _gate_market_regime(structure),
        _gate_participation(chosen),
        _gate_control(bias),
        _gate_strike_quality(chosen_state, spot=spot, settings=settings),
    ]

    confidence = sum(gate.weight for gate in gates if gate.passed)
    failed = [gate.name for gate in gates if not gate.passed]
    mandatory_ok = all(gate.passed for gate in gates if gate.mandatory)
    qualified = mandatory_ok and chosen is not None

    reasons = _reasons(chosen, chosen_state, structure, context, unusual_strikes)
    best = _best_candidate(chosen, chosen_state, structure, mandatory_ok)

    if qualified and chosen is not None:
        decision = (
            TradeDecision.BUY_CE
            if chosen.option_type is OptionType.CE
            else TradeDecision.BUY_PE
        )
        return TradeQualification(
            decision=decision,
            qualified=True,
            strike=chosen.strike,
            option_type=chosen.option_type,
            classification=chosen.classification,
            confidence=confidence,
            band=_band(confidence),
            gates=gates,
            failed_gates=failed,
            reasons=reasons,
            best_candidate=best,
        )

    return TradeQualification(
        decision=TradeDecision.NO_TRADE,
        qualified=False,
        strike=None,
        option_type=None,
        classification=None,
        confidence=confidence,
        band=_band(confidence),
        gates=gates,
        failed_gates=failed,
        reasons=reasons,
        best_candidate=best,
    )


# --- direction & candidate selection -----------------------------------------


def _direction(control: ControllingSide) -> OptionType | None:
    """Map who controls the market to the option side to buy."""
    if control is ControllingSide.BULLS:
        return OptionType.CE
    if control is ControllingSide.BEARS:
        return OptionType.PE
    return None


def _candidates(
    classifications: list[ClassificationResult],
    states: dict[tuple[Decimal, OptionType], StrikeState],
    side: OptionType | None,
) -> list[ClassificationResult]:
    """Buy-side classified strikes on the controlling side, most liquid first."""
    if side is None:
        return []
    matches = [
        c
        for c in classifications
        if c.option_type is side and c.classification in _BUY_CLASSIFICATIONS
    ]

    def liquidity(result: ClassificationResult) -> tuple[int, int]:
        state = states.get((result.strike, result.option_type))
        if state is None:
            return (0, 0)
        return (state.current_oi, state.current_volume)

    return sorted(matches, key=liquidity, reverse=True)


# --- gates -------------------------------------------------------------------


def _gate_market_regime(structure: StructureState) -> QualificationGate:
    """Gate 1: trade only when a trend exists or a breakout/breakdown confirmed."""
    trending = structure.trend in (TrendDirection.UPTREND, TrendDirection.DOWNTREND)
    broke = structure.pattern in (
        StructurePattern.BREAKOUT,
        StructurePattern.BREAKDOWN,
    )
    passed = trending or broke
    if trending:
        reason = f"Structure is {structure.trend.value}."
    elif broke:
        reason = f"Confirmed {structure.pattern.value}."
    else:
        reason = "No trend or breakout; market is sideways/choppy."
    return _gate(GateName.MARKET_REGIME, passed, reason)


def _gate_participation(chosen: ClassificationResult | None) -> QualificationGate:
    """Gate 2: professional option positioning must be present on the traded side."""
    if chosen is None:
        return _gate(
            GateName.OPTIONS_PARTICIPATION,
            passed=False,
            reason="No clear option participation on the controlling side.",
        )
    label = chosen.classification.value.replace("_", " ").title()
    return _gate(
        GateName.OPTIONS_PARTICIPATION,
        passed=True,
        reason=f"{label} at {chosen.strike} {chosen.option_type.value}.",
    )


def _gate_control(bias: MarketBias) -> QualificationGate:
    """Gate 3: one side must clearly control the market (canonical bias).

    Exposes the measurable bull/bear scores behind the decision rather than a
    generic verdict, so a failed gate is fully explainable.
    """
    passed = bias.controlling_side is not ControllingSide.NEUTRAL
    scores = f"bull {bias.bull_score:,.0f} vs bear {bias.bear_score:,.0f}"
    if passed:
        reason = f"{bias.controlling_side.value.capitalize()} in control ({scores})."
    else:
        reason = f"Neither side clearly controls the market ({scores})."
    return _gate(GateName.CE_PE_CONTROL, passed, reason)


def _gate_strike_quality(
    state: StrikeState | None, *, spot: Decimal, settings: Settings
) -> QualificationGate:
    """Gate 4: the chosen strike must be liquid, near ATM, and priced."""
    if state is None:
        return _gate(
            GateName.STRIKE_QUALITY,
            passed=False,
            reason="No tradable strike available.",
        )

    step = settings.OPTION_STRIKE_STEP
    atm = round(spot / step) * step
    steps_from_atm = int(abs(state.strike - atm) / step) if step else 0

    if state.current_oi < settings.STRIKE_QUALITY_MIN_OI:
        return _gate(GateName.STRIKE_QUALITY, False, "Open interest too low.")
    if state.current_volume < settings.STRIKE_QUALITY_MIN_VOLUME:
        return _gate(GateName.STRIKE_QUALITY, False, "Traded volume too low.")
    if state.current_premium <= 0:
        return _gate(GateName.STRIKE_QUALITY, False, "No valid premium.")
    if steps_from_atm > settings.STRIKE_QUALITY_MAX_ATM_STEPS:
        return _gate(
            GateName.STRIKE_QUALITY,
            False,
            f"Strike is {steps_from_atm} steps from ATM (too far).",
        )

    return _gate(
        GateName.STRIKE_QUALITY,
        passed=True,
        reason=f"Liquid and {steps_from_atm} step(s) from ATM.",
    )


def _gate(name: GateName, passed: bool, reason: str) -> QualificationGate:
    return QualificationGate(
        name=name,
        passed=passed,
        reason=reason,
        weight=_WEIGHTS[name],
        mandatory=name in _MANDATORY,
    )


# --- evidence & best candidate -----------------------------------------------


def _reasons(
    chosen: ClassificationResult | None,
    state: StrikeState | None,
    structure: StructureState,
    context: MarketContext,
    unusual_strikes: set[tuple[Decimal, OptionType]],
) -> list[str]:
    """Factual evidence lines — only what actually holds, never invented."""
    reasons: list[str] = []
    if chosen is not None:
        reasons.extend(chosen.evidence)  # OI/premium/volume % from Classification
    if state is not None and (state.strike, state.option_type) in unusual_strikes:
        reasons.append("Unusual activity flagged")
    if context.dominant_participant.value == "buyers":
        reasons.append("Buyers dominant")
    if context.controlling_side is ControllingSide.BULLS:
        reasons.append("Bulls control market")
    elif context.controlling_side is ControllingSide.BEARS:
        reasons.append("Bears control market")
    if context.contradiction is None:
        reasons.append("No contradiction")
    if context.structure_validates_options:
        reasons.append("Trend supports options activity")
    return reasons


def _best_candidate(
    chosen: ClassificationResult | None,
    state: StrikeState | None,
    structure: StructureState,
    mandatory_ok: bool,
) -> BestCandidate | None:
    """Return the strongest watched strike, populated even during NO TRADE."""
    if chosen is None or state is None:
        return None

    # A light qualification score for the watched strike: participation is
    # present (it is a candidate), so weight it plus any structural support.
    score = 55
    if structure.trend in (TrendDirection.UPTREND, TrendDirection.DOWNTREND):
        score += 20
    if structure.pattern in (StructurePattern.BREAKOUT, StructurePattern.BREAKDOWN):
        score += 16

    if mandatory_ok:
        reason = "Qualified: option activity and market structure aligned."
    else:
        reason = "Good option activity, but market structure has not confirmed yet."

    return BestCandidate(
        strike=chosen.strike,
        option_type=chosen.option_type,
        classification=chosen.classification,
        qualification=min(score, 100),
        reason=reason,
    )


def _band(confidence: int) -> ConfidenceBand:
    """Map a 0-100 confidence to its band."""
    if confidence >= 90:
        return ConfidenceBand.VERY_HIGH
    if confidence >= 75:
        return ConfidenceBand.HIGH
    if confidence >= 60:
        return ConfidenceBand.MEDIUM
    if confidence >= 40:
        return ConfidenceBand.LOW
    return ConfidenceBand.VERY_LOW
