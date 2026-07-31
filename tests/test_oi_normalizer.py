"""Tests for the Fyers response normalizer."""

from decimal import Decimal

from mios.integrations.fyers.normalizer import (
    normalize_candles,
    normalize_option_chain,
    normalize_spot,
)
from mios.schemas.market import OptionType


def test_normalize_spot_extracts_last_price_and_prev_close() -> None:
    raw = {
        "s": "ok",
        "d": [
            {
                "n": "NSE:NIFTY50-INDEX",
                "v": {
                    "lp": 24400.45,
                    "prev_close_price": 24317.15,
                    "ch": 83.3,
                    "chp": 0.34,
                },
            }
        ],
    }

    quote = normalize_spot(raw, "NSE:NIFTY50-INDEX")

    assert quote.ltp == Decimal("24400.45")
    assert quote.symbol == "NSE:NIFTY50-INDEX"
    # The previous trading day's close is captured from the feed...
    assert quote.prev_close == Decimal("24317.15")
    # ...and the day's change is derived from it, matching Fyers' ch/chp.
    assert quote.change == Decimal("83.30")
    assert quote.change_percent == 0.34


def test_normalize_spot_tolerates_missing_prev_close() -> None:
    raw = {"s": "ok", "d": [{"n": "NSE:NIFTY50-INDEX", "v": {"lp": 24705.5}}]}

    quote = normalize_spot(raw, "NSE:NIFTY50-INDEX")

    assert quote.ltp == Decimal("24705.5")
    assert quote.prev_close is None
    assert quote.change is None
    assert quote.change_percent is None


def test_normalize_option_chain_skips_the_index_row() -> None:
    raw = {
        "data": {
            "expiryData": [{"date": "08-01-2026", "expiry": "1"}],
            "optionsChain": [
                {
                    "symbol": "NSE:NIFTY50-INDEX",
                    "strike_price": 0,
                    "option_type": "",
                    "ltp": 24700,
                },
                {
                    "symbol": "CE1",
                    "strike_price": 24700,
                    "option_type": "CE",
                    "ltp": 120.5,
                    "oi": 15000,
                    "volume": 3000,
                },
                {
                    "symbol": "PE1",
                    "strike_price": 24700,
                    "option_type": "PE",
                    "ltp": 95.0,
                    "oi": 12000,
                    "volume": 2500,
                },
            ],
        }
    }

    quotes = normalize_option_chain(raw, symbol="NSE:NIFTY50-INDEX")

    assert len(quotes) == 2  # index row skipped
    ce = next(q for q in quotes if q.option_type is OptionType.CE)
    assert ce.strike == Decimal(24700)
    assert ce.premium == Decimal("120.5")
    assert ce.oi == 15000


def test_normalize_candles_sorts_oldest_first() -> None:
    raw = {
        "candles": [
            [1735707600, 24700, 24710, 24695, 24705, 1000],
            [1735707300, 24690, 24705, 24688, 24700, 900],
        ]
    }

    candles = normalize_candles(raw, symbol="NSE:NIFTY50-INDEX")

    assert len(candles) == 2
    assert candles[0].timestamp < candles[1].timestamp
    assert candles[0].close == Decimal("24700")


def test_normalize_option_chain_tolerates_missing_expiry() -> None:
    raw = {
        "data": {
            "optionsChain": [
                {
                    "symbol": "CE1",
                    "strike_price": 24700,
                    "option_type": "CE",
                    "ltp": 120,
                    "oi": 1,
                    "volume": 1,
                },
            ]
        }
    }

    quotes = normalize_option_chain(raw, symbol="NSE:NIFTY50-INDEX")

    assert len(quotes) == 1
    assert quotes[0].expiry is not None
