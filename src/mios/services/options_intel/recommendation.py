"""Recommendation Engine.

Ranks candidate strikes by how many independent, factual signals support them
— never a score or percentage, only the count used internally to order
candidates. Candidates are drawn from strikes showing fresh or renewed buying
interest (Long Build-up or Short Covering); a strike being written against
(Short Build-up) or unwound (Long Unwinding) is not something to buy.

This engine only ranks strikes and builds the report. It does not decide
no-trade: the Pipeline runs the No-Trade Engine and passes the resulting
`NoTradeDecision` into `build_report`. Ranking is exposed via `rank_candidates`
so the Pipeline can feed the best-CE/PE scores to the No-Trade Engine before
the report is assembled.
"""

from dataclasses import dataclass
from decimal import Decimal

from mios.schemas.market import (
    Classification,
    ClassificationResult,
    ControllingSide,
    MarketContext,
    MomentumReport,
    MomentumState,
    NoTradeDecision,
    OptionType,
    RecommendationReport,
    StrikeRecommendation,
    StructurePattern,
    StructureState,
    UnusualActivity,
)

_CANDIDATE_CLASSIFICATIONS = (
    Classification.LONG_BUILDUP,
    Classification.SHORT_COVERING,
)


@dataclass
class CandidateRanking:
    """Ranked candidates and the chosen best CE/PE for a single poll.

    Carries the best-CE and best-PE scores so the Pipeline can pass them to the
    No-Trade Engine, and the intermediate state `build_report` needs to assemble
    the final report without re-ranking.
    """

    ranked: list[tuple[int, ClassificationResult]]
    unusual_strikes: set[Decimal]
    best_ce: ClassificationResult | None
    best_pe: ClassificationResult | None
    best_ce_score: int | None
    best_pe_score: int | None


def rank_candidates(
    classifications: list[ClassificationResult],
    unusual: list[UnusualActivity],
    structure: StructureState,
    momentum: MomentumReport,
    context: MarketContext,
    *,
    min_evidence: int,
) -> CandidateRanking:
    """Rank candidate strikes and choose the best CE and best PE."""
    unusual_strikes = {u.strike for u in unusual}
    ranked = [
        (_rank(c, unusual_strikes, structure, momentum, context), c)
        for c in classifications
        if c.classification in _CANDIDATE_CLASSIFICATIONS
    ]
    ranked.sort(key=lambda pair: (-pair[0], pair[1].strike))

    ce_ranked = [pair for pair in ranked if pair[1].option_type is OptionType.CE]
    pe_ranked = [pair for pair in ranked if pair[1].option_type is OptionType.PE]

    best_ce_score, best_ce = _best(ce_ranked, min_evidence)
    best_pe_score, best_pe = _best(pe_ranked, min_evidence)

    return CandidateRanking(
        ranked=ranked,
        unusual_strikes=unusual_strikes,
        best_ce=best_ce,
        best_pe=best_pe,
        best_ce_score=best_ce_score,
        best_pe_score=best_pe_score,
    )


def build_report(
    ranking: CandidateRanking,
    no_trade: NoTradeDecision,
    structure: StructureState,
    momentum: MomentumReport,
    *,
    top_n: int,
    min_evidence: int,
) -> RecommendationReport:
    """Assemble the report from a ranking and an already-computed no-trade decision."""
    top_candidates = [
        _to_recommendation(result, ranking.unusual_strikes, structure, momentum)
        for rank, result in ranking.ranked[:top_n]
        if rank >= min_evidence
    ]

    return RecommendationReport(
        best_ce=(
            _to_recommendation(
                ranking.best_ce, ranking.unusual_strikes, structure, momentum
            )
            if ranking.best_ce is not None
            else None
        ),
        best_pe=(
            _to_recommendation(
                ranking.best_pe, ranking.unusual_strikes, structure, momentum
            )
            if ranking.best_pe is not None
            else None
        ),
        top_candidates=top_candidates,
        no_trade=no_trade,
    )


def _rank(
    result: ClassificationResult,
    unusual_strikes: set[Decimal],
    structure: StructureState,
    momentum: MomentumReport,
    context: MarketContext,
) -> int:
    """Count the independent factors supporting this candidate."""
    score = 0

    aligned_with_control = (
        result.option_type is OptionType.CE
        and context.controlling_side is ControllingSide.BULLS
    ) or (
        result.option_type is OptionType.PE
        and context.controlling_side is ControllingSide.BEARS
    )
    if aligned_with_control:
        score += 1

    if result.strike in unusual_strikes:
        score += 1

    pattern_confirms = (
        result.option_type is OptionType.CE
        and structure.pattern is StructurePattern.BREAKOUT
    ) or (
        result.option_type is OptionType.PE
        and structure.pattern is StructurePattern.BREAKDOWN
    )
    if pattern_confirms:
        score += 1

    if momentum.state is MomentumState.INCREASING:
        score += 1

    if context.structure_validates_options:
        score += 1

    return score


def _best(
    ranked: list[tuple[int, ClassificationResult]], min_evidence: int
) -> tuple[int | None, ClassificationResult | None]:
    """Return the top-ranked candidate meeting the evidence floor, if any."""
    if not ranked or ranked[0][0] < min_evidence:
        return None, None
    return ranked[0]


def _to_recommendation(
    result: ClassificationResult,
    unusual_strikes: set[Decimal],
    structure: StructureState,
    momentum: MomentumReport,
) -> StrikeRecommendation:
    """Build the public recommendation record, including why it was chosen."""
    evidence = list(result.evidence)
    factors = []

    if result.strike in unusual_strikes:
        evidence.append("Flagged as unusual activity.")
        factors.append("strong OI/volume addition")

    if (
        result.option_type is OptionType.CE
        and structure.pattern is StructurePattern.BREAKOUT
    ) or (
        result.option_type is OptionType.PE
        and structure.pattern is StructurePattern.BREAKDOWN
    ):
        evidence.append(f"Structure confirms {structure.pattern.value}.")
        factors.append(f"price confirming {structure.pattern.value}")

    if momentum.state is MomentumState.INCREASING:
        evidence.append("Momentum increasing.")
        factors.append("increasing momentum")

    reason = result.reason
    if factors:
        reason = f"{reason} Supported by {', '.join(factors)}."

    return StrikeRecommendation(
        strike=result.strike,
        option_type=result.option_type,
        classification=result.classification,
        evidence=evidence,
        reason=reason,
    )
