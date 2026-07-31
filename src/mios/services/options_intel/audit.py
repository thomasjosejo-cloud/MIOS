"""Snapshot audit / decision-trace tool.

Builds a single structured report for the current market snapshot: each nearby
strike's raw deltas and its signed contribution to the canonical bias, followed
by the derived regime, dominance, qualification, and narrative, plus any
consistency contradictions. This is MIOS's primary debugging tool — it makes
every dashboard conclusion traceable back to the raw evidence it came from.

It computes nothing new: it reads the store's existing pipeline outputs and the
same presentation projections the dashboard uses.
"""

from decimal import Decimal

from mios.config import Settings
from mios.schemas.dashboard import AuditReport, AuditStrikeRow
from mios.schemas.market import OptionType, StrikeContribution
from mios.services.options_intel import consistency, presentation
from mios.services.options_intel.store import EngineStore

ContributionMap = dict[tuple[Decimal, OptionType], StrikeContribution]


def build_audit_report(
    store: EngineStore, *, settings: Settings, atm_window: int = 2
) -> AuditReport:
    """Assemble the decision trace for the store's latest snapshot."""
    spot = store.spot_price
    step = settings.OPTION_STRIKE_STEP
    atm = Decimal(round(spot / step) * step) if spot is not None else None

    contribution_by: ContributionMap = {
        (c.strike, c.option_type): c
        for c in (store.bias.contributions if store.bias else [])
    }

    strikes = _nearby_rows(store, atm, step, atm_window, contribution_by)

    dominance = None
    if store.bias is not None:
        dominance = presentation.build_dominance(
            store.bias,
            store.classifications,
            previous_control=store.previous_controlling_side,
        )

    narrative = None
    if (
        store.context is not None
        and store.structure is not None
        and store.momentum is not None
        and store.qualification is not None
        and spot is not None
    ):
        narrative = presentation.build_narrative(
            store.classifications,
            store.context,
            store.structure,
            store.momentum,
            store.qualification,
            spot=spot,
        )

    warnings: list[str] = []
    if (
        store.bias is not None
        and store.context is not None
        and dominance is not None
        and store.structure is not None
        and store.qualification is not None
        and narrative is not None
    ):
        warnings = consistency.check(
            bias=store.bias,
            context=store.context,
            dominance=dominance,
            structure=store.structure,
            qualification=store.qualification,
            narrative=narrative,
        )

    return AuditReport(
        spot=spot,
        atm=atm,
        strikes=strikes,
        bias=store.bias,
        structure_trend=store.structure.trend if store.structure else None,
        structure_pattern=store.structure.pattern if store.structure else None,
        momentum=store.momentum.state if store.momentum else None,
        dominance=dominance,
        qualification=store.qualification,
        narrative=narrative,
        consistency_warnings=warnings,
    )


def _nearby_rows(
    store: EngineStore,
    atm: Decimal | None,
    step: int,
    atm_window: int,
    contribution_by: ContributionMap,
) -> list[AuditStrikeRow]:
    """Build audit rows for strikes within `atm_window` steps of the money."""
    max_distance = Decimal(step * atm_window)

    def near(strike: Decimal) -> bool:
        return atm is None or abs(strike - atm) <= max_distance

    rows: list[AuditStrikeRow] = []
    for state in store.strike_states:
        if not near(state.strike):
            continue
        contribution = contribution_by.get((state.strike, state.option_type))
        rows.append(
            AuditStrikeRow(
                strike=state.strike,
                option_type=state.option_type,
                oi_change=state.oi_change,
                oi_change_pct=state.oi_change_pct,
                premium_change_pct=state.premium_change_pct,
                volume_change_pct=state.volume_change_pct,
                classification=contribution.classification if contribution else None,
                sentiment=contribution.sentiment if contribution else None,
                weight=contribution.weight if contribution else 0,
                signed_score=contribution.signed_score if contribution else 0.0,
            )
        )
    rows.sort(key=lambda r: (r.strike, r.option_type.value))
    return rows
