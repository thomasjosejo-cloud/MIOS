"""Recommendation Engine.

Selects the single strike with the highest institutional conviction using an
**ordered, deterministic decision hierarchy** (Sprint 5), not equal-weight
evidence counting. Candidates are first filtered (Stage 1), then ranked by a
lexicographic conviction key built from ordered market evidence (Stages 2-6):

    Stage 2  classification preference (Long Build-up over Short Covering,
             unless market context supports Short Covering)
    Stage 3  unusual-signal conviction (more unusual signals rank higher)
    Stage 4  structure alignment (breakout/breakdown/trend); fighting
             structure is rejected in Stage 1
    Stage 5  CE/PE positioning quality (controlling side, buyer dominance,
             absence of contradiction)
    Stage 6  evidence magnitude (OI / premium / volume change) — the neighbour
             tie-breaker; never the strike number

Selection is performed here. The no-trade decision is made by the No-Trade
Engine, which the Pipeline runs between `rank_candidates` and `build_report`;
this engine never imports or calls it. When the two strongest candidates on a
side are indistinguishable (identical conviction key), no single winner is
named and the No-Trade Engine decides whether conviction is sufficient.

Determinism: every input is a value already computed by an upstream engine;
ranking is a pure sort over a value tuple, with no timestamps, randomness, or
strike-number tie-breaking. Identical input yields identical output.
"""

from dataclasses import dataclass

from mios.schemas.market import (
    Classification,
    ClassificationResult,
    ControllingSide,
    DominantParticipant,
    MarketContext,
    MomentumReport,
    MomentumState,
    NoTradeDecision,
    OptionType,
    RecommendationReport,
    StrikeRecommendation,
    StrikeState,
    StructurePattern,
    StructureState,
    TrendDirection,
    UnusualActivity,
)

#: Classifications a strike must have to be a buy-side candidate at all.
_CANDIDATE_CLASSIFICATIONS = (
    Classification.LONG_BUILDUP,
    Classification.SHORT_COVERING,
)


@dataclass(frozen=True)
class _ConvictionKey:
    """Lexicographically ordered conviction key; higher compares as stronger.

    Fields are ordered most-significant first, mirroring the Stage 2-6
    hierarchy. Comparison is done on `as_tuple()`; no strike number appears.
    """

    classification_rank: int  # Stage 2
    unusual_conviction: int  # Stage 3
    structure_alignment: int  # Stage 4
    positioning_quality: int  # Stage 5
    evidence_oi: float  # Stage 6 (magnitudes)
    evidence_premium: float
    evidence_volume: float

    def as_tuple(self) -> tuple[int, int, int, int, float, float, float]:
        """Return the comparable ordered tuple."""
        return (
            self.classification_rank,
            self.unusual_conviction,
            self.structure_alignment,
            self.positioning_quality,
            self.evidence_oi,
            self.evidence_premium,
            self.evidence_volume,
        )


@dataclass
class _Candidate:
    """A surviving candidate with its conviction key and prepared output."""

    result: ClassificationResult
    key: _ConvictionKey
    conviction: int  # coarse 0-4 sufficiency tier consumed by the No-Trade Engine
    evidence: list[str]
    reason: str


@dataclass
class CandidateRanking:
    """Ranked survivors and the chosen best CE/PE for a single poll.

    `best_ce_score` / `best_pe_score` are the conviction tiers of the chosen
    strikes (or `None` when no confident winner exists); the Pipeline passes
    them to the No-Trade Engine unchanged.
    """

    ranked: list[_Candidate]
    best_ce: _Candidate | None
    best_pe: _Candidate | None
    best_ce_score: int | None
    best_pe_score: int | None


def rank_candidates(
    classifications: list[ClassificationResult],
    unusual: list[UnusualActivity],
    strike_states: list[StrikeState],
    structure: StructureState,
    momentum: MomentumReport,
    context: MarketContext,
    *,
    min_conviction: int,
    min_oi: int,
    min_volume: int,
    max_staleness_seconds: float,
) -> CandidateRanking:
    """Filter, evaluate, and rank candidates by the ordered decision hierarchy."""
    states = {(s.strike, s.option_type): s for s in strike_states}
    unusual_index = {(u.strike, u.option_type): u for u in unusual}

    survivors: list[_Candidate] = []
    for result in classifications:
        state = states.get((result.strike, result.option_type))
        if state is None:
            continue
        if _rejected(
            result, state, structure, min_oi, min_volume, max_staleness_seconds
        ):
            continue
        survivors.append(
            _evaluate(
                result,
                state,
                unusual_index.get((result.strike, result.option_type)),
                structure,
                momentum,
                context,
            )
        )

    survivors.sort(key=lambda c: c.key.as_tuple(), reverse=True)

    ce = [c for c in survivors if c.result.option_type is OptionType.CE]
    pe = [c for c in survivors if c.result.option_type is OptionType.PE]
    best_ce = _select_best(ce, min_conviction)
    best_pe = _select_best(pe, min_conviction)

    return CandidateRanking(
        ranked=survivors,
        best_ce=best_ce,
        best_pe=best_pe,
        best_ce_score=best_ce.conviction if best_ce is not None else None,
        best_pe_score=best_pe.conviction if best_pe is not None else None,
    )


def build_report(
    ranking: CandidateRanking,
    no_trade: NoTradeDecision,
    *,
    top_n: int,
    min_conviction: int,
) -> RecommendationReport:
    """Assemble the report from a ranking and an already-computed no-trade decision."""
    top_candidates = [
        _to_recommendation(candidate)
        for candidate in ranking.ranked[:top_n]
        if candidate.conviction >= min_conviction
    ]
    return RecommendationReport(
        best_ce=_to_recommendation(ranking.best_ce) if ranking.best_ce else None,
        best_pe=_to_recommendation(ranking.best_pe) if ranking.best_pe else None,
        top_candidates=top_candidates,
        no_trade=no_trade,
    )


# --- Stage 1: rejection ------------------------------------------------------


def _rejected(
    result: ClassificationResult,
    state: StrikeState,
    structure: StructureState,
    min_oi: int,
    min_volume: int,
    max_staleness_seconds: float,
) -> bool:
    """Reject a candidate that fails any Stage-1 gate. See module docstring."""
    if result.classification not in _CANDIDATE_CLASSIFICATIONS:
        return True  # Short Build-up / Long Unwinding are never buy candidates
    if state.current_oi < min_oi or state.current_volume < min_volume:
        return True  # below minimum liquidity
    if state.current_premium <= 0:
        return True  # invalid premium
    if max_staleness_seconds > 0 and state.seconds_since_update > max_staleness_seconds:
        return True  # stale data
    if _fights_structure(result.option_type, structure):
        return True  # Stage 4: reject candidates fighting structure
    return False


def _fights_structure(option_type: OptionType, structure: StructureState) -> bool:
    """Whether a candidate is directionally opposed to price structure."""
    if option_type is OptionType.CE:
        return (
            structure.trend is TrendDirection.DOWNTREND
            or structure.pattern is StructurePattern.BREAKDOWN
        )
    return (
        structure.trend is TrendDirection.UPTREND
        or structure.pattern is StructurePattern.BREAKOUT
    )


# --- Stages 2-6: evaluation --------------------------------------------------


def _evaluate(
    result: ClassificationResult,
    state: StrikeState,
    unusual: UnusualActivity | None,
    structure: StructureState,
    momentum: MomentumReport,
    context: MarketContext,
) -> _Candidate:
    """Compute the ordered conviction key, sufficiency tier, and evidence."""
    controlling_match = _controlling_matches(result.option_type, context)

    # Stage 2 — classification preference.
    if result.classification is Classification.LONG_BUILDUP:
        classification_rank = 2
    elif result.classification is Classification.SHORT_COVERING and controlling_match:
        classification_rank = 2  # context supports Short Covering
    else:
        classification_rank = 1  # Short Covering without contextual support

    # Stage 3 — unusual-signal conviction (more signals = stronger).
    unusual_conviction = len(unusual.triggers) if unusual is not None else 0

    # Stage 4 — structure alignment (fighting structure already rejected).
    structure_alignment = _structure_alignment(result.option_type, structure)

    # Stage 5 — positioning quality, ordered: control match > buyer dominance
    # > absence of contradiction.
    buyers_dominant = context.dominant_participant is DominantParticipant.BUYERS
    no_contradiction = context.contradiction is None
    positioning_quality = (
        (4 if controlling_match else 0)
        + (2 if buyers_dominant else 0)
        + (1 if no_contradiction else 0)
    )

    key = _ConvictionKey(
        classification_rank=classification_rank,
        unusual_conviction=unusual_conviction,
        structure_alignment=structure_alignment,
        positioning_quality=positioning_quality,
        evidence_oi=abs(state.oi_change_pct or 0.0),
        evidence_premium=abs(state.premium_change_pct or 0.0),
        evidence_volume=abs(state.volume_change_pct or 0.0),
    )

    # Coarse conviction tier (0-4) for the No-Trade Engine's sufficiency and
    # cross-side comparison. This summarises which stages are positively
    # satisfied; it is NOT used to rank strikes (the key above does that).
    conviction = (
        (1 if classification_rank >= 2 else 0)
        + (1 if unusual_conviction >= 1 else 0)
        + (1 if structure_alignment >= 1 else 0)
        + (1 if controlling_match else 0)
    )

    evidence, reason = _describe(
        result,
        structure,
        momentum,
        context,
        unusual,
        controlling_match,
        buyers_dominant,
    )
    return _Candidate(
        result=result, key=key, conviction=conviction, evidence=evidence, reason=reason
    )


def _structure_alignment(option_type: OptionType, structure: StructureState) -> int:
    """2 when a directional breakout confirms, 1 for trend alignment, else 0."""
    if option_type is OptionType.CE:
        if structure.pattern is StructurePattern.BREAKOUT:
            return 2
        if structure.trend is TrendDirection.UPTREND:
            return 1
    else:
        if structure.pattern is StructurePattern.BREAKDOWN:
            return 2
        if structure.trend is TrendDirection.DOWNTREND:
            return 1
    return 0


def _controlling_matches(option_type: OptionType, context: MarketContext) -> bool:
    """Whether the option direction matches the side controlling the market."""
    return (
        option_type is OptionType.CE
        and context.controlling_side is ControllingSide.BULLS
    ) or (
        option_type is OptionType.PE
        and context.controlling_side is ControllingSide.BEARS
    )


# --- Selection ---------------------------------------------------------------


def _select_best(side: list[_Candidate], min_conviction: int) -> _Candidate | None:
    """Return the top candidate for a side, or `None` when there is no clear one.

    `None` is returned when the side is empty, the top candidate is below the
    minimum conviction tier, or the top two are indistinguishable (identical
    conviction key) — in which case the No-Trade Engine decides. Selection never
    falls back to the strike number.
    """
    if not side:
        return None
    top = side[0]
    if top.conviction < min_conviction:
        return None
    if len(side) >= 2 and side[1].key.as_tuple() == top.key.as_tuple():
        return None
    return top


# --- Evidence / explanation --------------------------------------------------


def _describe(
    result: ClassificationResult,
    structure: StructureState,
    momentum: MomentumReport,
    context: MarketContext,
    unusual: UnusualActivity | None,
    controlling_match: bool,
    buyers_dominant: bool,
) -> tuple[list[str], str]:
    """Build factual evidence lines and a traceable reason from engine outputs."""
    evidence = list(result.evidence)  # OI / premium / volume % from Classification
    factors: list[str] = []

    if unusual is not None:
        evidence.append(f"Unusual activity: {', '.join(unusual.triggers)}.")
        factors.append(f"{len(unusual.triggers)} unusual signal(s)")

    alignment = _structure_alignment(result.option_type, structure)
    if alignment == 2:
        evidence.append(f"Structure confirms {structure.pattern.value}.")
        factors.append(f"price confirming {structure.pattern.value}")
    elif alignment == 1:
        evidence.append(f"Aligned with {structure.trend.value}.")
        factors.append(f"aligned with {structure.trend.value}")

    if momentum.state is MomentumState.INCREASING:
        evidence.append("Momentum increasing.")
        factors.append("increasing momentum")

    if controlling_match:
        evidence.append(f"Controlling side: {context.controlling_side.value}.")
        factors.append("controlling side matches")
    if buyers_dominant:
        evidence.append("Buyers dominant.")
        factors.append("buyer dominance")
    if context.contradiction is None:
        evidence.append("No contradiction.")

    reason = result.reason
    if factors:
        reason = f"{reason} Supported by {', '.join(factors)}."
    return evidence, reason


def _to_recommendation(candidate: _Candidate) -> StrikeRecommendation:
    """Wrap a candidate as the public recommendation record."""
    return StrikeRecommendation(
        strike=candidate.result.strike,
        option_type=candidate.result.option_type,
        classification=candidate.result.classification,
        evidence=candidate.evidence,
        reason=candidate.reason,
    )
