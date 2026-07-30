"""Normalizer: raw Fyers JSON → normalized market schemas.

This is the Normalizer stage of the pipeline. Field names and response shapes
were verified against Fyers' response structs (`optionsChain`, `expiryData`,
quote `d[].v`, and `candles` arrays) — see `client.py` for how each shape was
confirmed. Fyers' option-chain response also includes one row for the
underlying index itself alongside the CE/PE rows; that row has no
`option_type` and is skipped here.
"""

import datetime as dt
from decimal import Decimal
from typing import Any

from mios.core.logging import get_logger
from mios.schemas.market import Candle, OptionQuote, OptionType, SpotQuote

logger = get_logger(__name__)

_DATE_FORMATS = ("%d-%m-%Y", "%Y-%m-%d")


def _parse_expiry(value: object) -> dt.date:
    """Parse an expiry value from `expiryData`, tolerating format variance.

    Falls back to today's date with a warning rather than raising, since
    expiry is informational here and must never abort an otherwise-good poll.
    """
    if isinstance(value, int):
        return dt.datetime.fromtimestamp(value, tz=dt.UTC).date()

    if isinstance(value, str):
        candidate = value.strip()
        if candidate.isdigit():
            return dt.datetime.fromtimestamp(int(candidate), tz=dt.UTC).date()
        for fmt in _DATE_FORMATS:
            try:
                return (
                    dt.datetime.strptime(candidate, fmt).replace(tzinfo=dt.UTC).date()
                )
            except ValueError:
                continue

    logger.warning("Could not parse expiry value %r; defaulting to today", value)
    return dt.datetime.now(dt.UTC).date()


def normalize_spot(raw: dict[str, Any], symbol: str) -> SpotQuote:
    """Normalize a `quotes` response for a single symbol into a `SpotQuote`."""
    entries = raw.get("d", [])
    if not entries:
        msg = f"Quotes response for {symbol} contained no data"
        raise ValueError(msg)

    value = entries[0]["v"]
    return SpotQuote(
        symbol=symbol,
        ltp=Decimal(str(value["lp"])),
        timestamp=dt.datetime.now(dt.UTC),
    )


def normalize_option_chain(raw: dict[str, Any], *, symbol: str) -> list[OptionQuote]:
    """Normalize an `options-chain-v3` response into per-strike option quotes."""
    data = raw.get("data", {})
    expiry_entries = data.get("expiryData", [])
    expiry = (
        _parse_expiry(expiry_entries[0].get("date"))
        if expiry_entries
        else (dt.datetime.now(dt.UTC).date())
    )

    now = dt.datetime.now(dt.UTC)
    quotes: list[OptionQuote] = []

    for row in data.get("optionsChain", []):
        option_type = row.get("option_type")
        if option_type not in ("CE", "PE"):
            # The underlying index itself is included as a row with no
            # option_type; it is not a strike and is not part of this stream.
            continue

        quotes.append(
            OptionQuote(
                symbol=str(row.get("symbol", symbol)),
                strike=Decimal(str(row["strike_price"])),
                option_type=OptionType(option_type),
                expiry=expiry,
                premium=Decimal(str(row["ltp"])),
                oi=int(row.get("oi", 0)),
                volume=int(row.get("volume", 0)),
                timestamp=now,
            )
        )

    return quotes


def normalize_candles(raw: dict[str, Any], *, symbol: str) -> list[Candle]:
    """Normalize a `history` response into OHLCV candles, oldest first."""
    candles: list[Candle] = []

    for row in raw.get("candles", []):
        epoch, open_, high, low, close, volume = row
        candles.append(
            Candle(
                symbol=symbol,
                timestamp=dt.datetime.fromtimestamp(epoch, tz=dt.UTC),
                open=Decimal(str(open_)),
                high=Decimal(str(high)),
                low=Decimal(str(low)),
                close=Decimal(str(close)),
                volume=int(volume),
            )
        )

    candles.sort(key=lambda candle: candle.timestamp)
    return candles
