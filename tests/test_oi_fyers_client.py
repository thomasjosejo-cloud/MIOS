"""Tests for the Fyers REST client, using a mocked httpx transport.

No network calls are made: a `MockTransport` answers requests so the client's
URL construction, header format, and error handling are exercised offline.
"""

import httpx
import pytest

from mios.integrations.fyers.client import FyersAPIError, FyersAuthError, FyersClient


def _client_with(handler: "httpx.MockTransport") -> FyersClient:
    client = FyersClient(client_id="APP-100", access_token="tok", timeout=5)
    client._http = httpx.AsyncClient(
        base_url="https://api-t1.fyers.in/data",
        transport=handler,
        headers={"Authorization": "APP-100:tok", "version": "3"},
    )
    return client


async def test_quotes_builds_symbol_param_and_authorization_header() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        return httpx.Response(200, json={"s": "ok", "d": []})

    client = _client_with(httpx.MockTransport(handler))
    await client.quotes(["NSE:NIFTY50-INDEX", "NSE:SBIN-EQ"])
    await client.aclose()

    assert "symbols=NSE%3ANIFTY50-INDEX%2CNSE%3ASBIN-EQ" in str(captured["url"])
    assert captured["auth"] == "APP-100:tok"


async def test_option_chain_passes_strike_count() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"s": "ok", "data": {"optionsChain": []}})

    client = _client_with(httpx.MockTransport(handler))
    await client.option_chain("NSE:NIFTY50-INDEX", strike_count=10)
    await client.aclose()

    assert "strikecount=10" in str(captured["url"])
    assert "options-chain-v3" in str(captured["url"])


async def test_http_401_raises_auth_error() -> None:
    client = _client_with(
        httpx.MockTransport(lambda _: httpx.Response(401, text="unauthorized"))
    )

    with pytest.raises(FyersAuthError):
        await client.quotes(["NSE:NIFTY50-INDEX"])
    await client.aclose()


async def test_error_body_with_token_message_raises_auth_error() -> None:
    client = _client_with(
        httpx.MockTransport(
            lambda _: httpx.Response(
                200, json={"s": "error", "message": "invalid token"}
            )
        )
    )

    with pytest.raises(FyersAuthError):
        await client.quotes(["NSE:NIFTY50-INDEX"])
    await client.aclose()


async def test_error_body_without_auth_message_raises_api_error() -> None:
    client = _client_with(
        httpx.MockTransport(
            lambda _: httpx.Response(
                200, json={"s": "error", "message": "bad symbol", "code": -300}
            )
        )
    )

    with pytest.raises(FyersAPIError):
        await client.quotes(["BAD"])
    await client.aclose()


async def test_transport_failure_raises_api_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    client = _client_with(httpx.MockTransport(handler))

    with pytest.raises(FyersAPIError):
        await client.quotes(["NSE:NIFTY50-INDEX"])
    await client.aclose()
