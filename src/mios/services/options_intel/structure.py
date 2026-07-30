"""Structure Engine.

Detects swing highs and lows from 5-minute candles using a simple fractal
method (a candle is a swing point if its high/low is the most extreme within a
configurable window on both sides), labels each swing relative to the prior
swing of the same kind (HH/LH, HL/LL), and derives trend, support/resistance,
and the current price-action pattern from that structure.
"""

from decimal import Decimal

from mios.schemas.market import (
    Candle,
    StructurePattern,
    StructureState,
    SwingLabel,
    SwingPoint,
    TrendDirection,
)


def analyze(candles: list[Candle], *, swing_lookback: int) -> StructureState:
    """Derive price structure from a series of candles, oldest first."""
    required = 2 * swing_lookback + 1
    if len(candles) < required:
        return StructureState(
            swing_high=None,
            swing_low=None,
            immediate_support=None,
            immediate_resistance=None,
            pattern=StructurePattern.RANGE,
            trend=TrendDirection.SIDEWAYS,
            swings=[],
            evidence=[
                f"Insufficient candle history for structure analysis "
                f"(need at least {required}, have {len(candles)})"
            ],
        )

    highs, lows = _detect_swings(candles, swing_lookback)
    labeled_highs = _label_swings(highs, SwingLabel.HH, SwingLabel.LH)
    labeled_lows = _label_swings(lows, SwingLabel.HL, SwingLabel.LL)
    swings = sorted(labeled_highs + labeled_lows, key=lambda point: point.timestamp)

    trend = _determine_trend(labeled_highs, labeled_lows)
    swing_high = highs[-1].price if highs else None
    swing_low = lows[-1].price if lows else None
    current_close = candles[-1].close
    previous_close = candles[-2].close if len(candles) >= 2 else current_close

    immediate_support = _nearest_below(lows, current_close)
    immediate_resistance = _nearest_above(highs, current_close)

    pattern = _determine_pattern(
        current_close,
        previous_close,
        immediate_support,
        immediate_resistance,
        trend,
    )

    evidence = _build_evidence(
        labeled_highs,
        labeled_lows,
        immediate_support,
        immediate_resistance,
        current_close,
        pattern,
    )

    return StructureState(
        swing_high=swing_high,
        swing_low=swing_low,
        immediate_support=immediate_support,
        immediate_resistance=immediate_resistance,
        pattern=pattern,
        trend=trend,
        swings=swings,
        evidence=evidence,
    )


def _detect_swings(
    candles: list[Candle], lookback: int
) -> tuple[list[SwingPoint], list[SwingPoint]]:
    """Find fractal swing highs and lows within the candle series.

    A candle counts as a swing point only if it is *strictly* the most extreme
    in its window versus every other candle in it — a tie (a plateau) means no
    single candle is the local extremum, so none are flagged.
    """
    highs: list[SwingPoint] = []
    lows: list[SwingPoint] = []

    for i in range(lookback, len(candles) - lookback):
        window = candles[i - lookback : i + lookback + 1]
        candle = candles[i]
        other_highs = [c.high for c in window if c is not candle]
        other_lows = [c.low for c in window if c is not candle]

        if other_highs and candle.high > max(other_highs):
            highs.append(
                SwingPoint(
                    timestamp=candle.timestamp, price=candle.high, label=SwingLabel.HH
                )
            )
        if other_lows and candle.low < min(other_lows):
            lows.append(
                SwingPoint(
                    timestamp=candle.timestamp, price=candle.low, label=SwingLabel.HL
                )
            )

    return highs, lows


def _label_swings(
    points: list[SwingPoint], higher_label: SwingLabel, lower_label: SwingLabel
) -> list[SwingPoint]:
    """Relabel each swing (after the first) relative to the prior swing of its kind."""
    labeled: list[SwingPoint] = []
    for index, point in enumerate(points):
        if index == 0:
            labeled.append(point)
            continue
        label = higher_label if point.price > points[index - 1].price else lower_label
        labeled.append(point.model_copy(update={"label": label}))
    return labeled


def _determine_trend(highs: list[SwingPoint], lows: list[SwingPoint]) -> TrendDirection:
    """Determine trend from the most recently labeled swing high and low."""
    if len(highs) < 2 or len(lows) < 2:
        return TrendDirection.SIDEWAYS

    latest_high, latest_low = highs[-1].label, lows[-1].label
    if latest_high is SwingLabel.HH and latest_low is SwingLabel.HL:
        return TrendDirection.UPTREND
    if latest_high is SwingLabel.LH and latest_low is SwingLabel.LL:
        return TrendDirection.DOWNTREND
    return TrendDirection.SIDEWAYS


def _nearest_below(points: list[SwingPoint], price: Decimal) -> Decimal | None:
    """Return the most recent swing price at or below `price`, else the latest swing."""
    below = [point for point in points if point.price <= price]
    if below:
        return below[-1].price
    return points[-1].price if points else None


def _nearest_above(points: list[SwingPoint], price: Decimal) -> Decimal | None:
    """Return the most recent swing price at or above `price`, else the latest swing."""
    above = [point for point in points if point.price >= price]
    if above:
        return above[-1].price
    return points[-1].price if points else None


def _determine_pattern(
    current_close: Decimal,
    previous_close: Decimal,
    support: Decimal | None,
    resistance: Decimal | None,
    trend: TrendDirection,
) -> StructurePattern:
    """Determine the current price-action pattern relative to structure."""
    if resistance is not None and current_close > resistance:
        return StructurePattern.BREAKOUT
    if support is not None and current_close < support:
        return StructurePattern.BREAKDOWN
    if trend is TrendDirection.UPTREND and current_close < previous_close:
        return StructurePattern.PULLBACK
    if trend is TrendDirection.DOWNTREND and current_close > previous_close:
        return StructurePattern.PULLBACK
    return StructurePattern.RANGE


def _build_evidence(
    highs: list[SwingPoint],
    lows: list[SwingPoint],
    support: Decimal | None,
    resistance: Decimal | None,
    current_close: Decimal,
    pattern: StructurePattern,
) -> list[str]:
    """Build factual evidence strings describing the detected structure."""
    evidence: list[str] = []
    if highs:
        evidence.append(
            f"Latest swing high: {highs[-1].price} ({highs[-1].label.value})"
        )
    if lows:
        evidence.append(f"Latest swing low: {lows[-1].price} ({lows[-1].label.value})")
    if support is not None:
        evidence.append(f"Immediate support: {support}")
    if resistance is not None:
        evidence.append(f"Immediate resistance: {resistance}")
    evidence.append(f"Current close {current_close} => {pattern.value}")
    return evidence
