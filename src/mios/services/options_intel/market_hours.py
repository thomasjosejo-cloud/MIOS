"""Configured market-hours check.

Fyers' `marketStatus` response encodes exchange/segment as numeric codes that
are not reliably documented; rather than guess at that mapping, market open/
closed is determined from the configured hours and timezone, consistent with
the explicit "Market hours" configuration requirement. Both the Fyers-backed
and simulated data sources use this same check.
"""

import datetime as dt
from zoneinfo import ZoneInfo

from mios.config import Settings

_WEEKEND = {5, 6}  # Saturday, Sunday


def is_market_open(settings: Settings, *, now: dt.datetime | None = None) -> bool:
    """Return whether the market is currently open per the configured hours."""
    tz = ZoneInfo(settings.MARKET_TIMEZONE)
    local_now = (now or dt.datetime.now(dt.UTC)).astimezone(tz)

    if local_now.weekday() in _WEEKEND:
        return False

    open_hour, open_minute = (
        int(part) for part in settings.MARKET_OPEN_TIME.split(":")
    )
    close_hour, close_minute = (
        int(part) for part in settings.MARKET_CLOSE_TIME.split(":")
    )
    opens_at = local_now.replace(
        hour=open_hour, minute=open_minute, second=0, microsecond=0
    )
    closes_at = local_now.replace(
        hour=close_hour, minute=close_minute, second=0, microsecond=0
    )

    return opens_at <= local_now <= closes_at
