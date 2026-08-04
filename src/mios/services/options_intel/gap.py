"""Opening-gap classification.

Describes how the session opened relative to the prior trading day's close — a
single, static fact about the open, not a forecast. Pure and side-effect free:
given the captured session-open price and the prior close, it returns the
percentage gap and its category. The opening price itself is captured once per
session by the engine orchestrator; this module only classifies it.

    gap_pct = (session_open - prev_close) / prev_close * 100

    |gap_pct| < 0.1%          -> flat
    0.1% <= |gap_pct| < 0.5%  -> gap_up_marginal / gap_down_marginal
    |gap_pct| >= 0.5%         -> gap_up / gap_down
"""

from decimal import Decimal

from mios.schemas.market import GapClassification

#: Below this absolute percentage the open is treated as flat (no gap).
_FLAT_THRESHOLD_PCT = 0.1
#: At or above this absolute percentage the gap is a full gap, not marginal.
_FULL_THRESHOLD_PCT = 0.5


def classify_gap(
    session_open: Decimal | None,
    prev_close: Decimal | None,
) -> tuple[GapClassification | None, float | None]:
    """Return the gap category and percentage for the session open.

    Returns ``(None, None)`` when the gap cannot be computed yet — no opening
    price captured, no prior close, or a zero prior close.
    """
    if session_open is None or prev_close is None or prev_close == 0:
        return None, None

    gap_pct = float((session_open - prev_close) / prev_close * 100)
    magnitude = abs(gap_pct)

    if magnitude < _FLAT_THRESHOLD_PCT:
        classification = GapClassification.FLAT
    elif magnitude < _FULL_THRESHOLD_PCT:
        classification = (
            GapClassification.GAP_UP_MARGINAL
            if gap_pct > 0
            else GapClassification.GAP_DOWN_MARGINAL
        )
    else:
        classification = (
            GapClassification.GAP_UP if gap_pct > 0 else GapClassification.GAP_DOWN
        )

    return classification, round(gap_pct, 2)
