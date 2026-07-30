"""Async REST client for Fyers API v3.

Endpoints, headers, and payload shapes were verified directly against the
official `fyers-apiv3` SDK source (`fyersModel.py`), not documentation prose,
since Fyers' hosted docs did not yield machine-readable endpoint details.

This client only ever receives an already-issued access token; it never
performs credential exchange itself (see `auth.py` for the one-time login
flow) and never logs a token value.
"""

from types import TracebackType
from typing import Any, Self

import httpx

from mios.config.constants import (
    FYERS_API_VERSION_HEADER,
    FYERS_DATA_BASE_URL,
    FYERS_HISTORY_PATH,
    FYERS_MARKET_STATUS_PATH,
    FYERS_OPTION_CHAIN_PATH,
    FYERS_QUOTES_PATH,
)
from mios.core.logging import get_logger

logger = get_logger(__name__)


class FyersAuthError(Exception):
    """The Fyers API rejected the current credentials."""


class FyersAPIError(Exception):
    """The Fyers API returned an error response."""

    def __init__(self, message: str, *, code: int | None = None) -> None:
        """Store the message and optional Fyers error code."""
        super().__init__(message)
        self.code = code


class FyersClient:
    """Thin async wrapper over the Fyers v3 data endpoints.

    Holds one `httpx.AsyncClient` for connection reuse across polls; use as an
    async context manager or call `aclose()` explicitly when done.
    """

    def __init__(
        self,
        *,
        client_id: str,
        access_token: str,
        timeout: float = 10.0,
    ) -> None:
        """Build the client with an `appid:token` Authorization header."""
        self._client_id = client_id
        header = f"{client_id}:{access_token}"
        self._http = httpx.AsyncClient(
            base_url=FYERS_DATA_BASE_URL,
            timeout=timeout,
            headers={
                "Authorization": header,
                "Content-Type": "application/json",
                "version": FYERS_API_VERSION_HEADER,
            },
        )

    async def __aenter__(self) -> Self:
        """Enter the async context, returning the client."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Close the HTTP connection pool on context exit."""
        await self.aclose()

    async def aclose(self) -> None:
        """Release the underlying HTTP connection pool."""
        await self._http.aclose()

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        """Issue a GET request and raise on transport or API-level failure.

        Fyers does not publish a stable numeric error code for an
        expired/invalid access token, so authentication failure is detected
        the standard way: an HTTP 401/403 status, or an "error" body whose
        message plainly says so.
        """
        try:
            response = await self._http.get(path, params=params)
        except httpx.HTTPError as error:
            raise FyersAPIError(f"Fyers API {path} request failed: {error}") from error

        if response.status_code in (401, 403):
            raise FyersAuthError(
                f"Fyers API {path} rejected the credentials "
                f"(HTTP {response.status_code}): {response.text}"
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise FyersAPIError(
                f"Fyers API {path} returned {error.response.status_code}: "
                f"{error.response.text}",
                code=error.response.status_code,
            ) from error

        body: dict[str, Any] = response.json()
        if body.get("s") == "error":
            message = str(body.get("message", "unknown error"))
            code = body.get("code")
            if any(term in message.lower() for term in ("token", "auth", "unauthoriz")):
                raise FyersAuthError(f"Fyers authentication rejected: {message}")
            raise FyersAPIError(f"Fyers API {path} error: {message}", code=code)

        return body

    async def quotes(self, symbols: list[str]) -> dict[str, Any]:
        """Fetch live quotes for up to 50 symbols."""
        return await self._get(FYERS_QUOTES_PATH, {"symbols": ",".join(symbols)})

    async def option_chain(
        self,
        symbol: str,
        *,
        strike_count: int,
        timestamp: int | None = None,
    ) -> dict[str, Any]:
        """Fetch the option chain for `symbol`.

        `timestamp` is the expiry as an epoch timestamp; omitted for the
        nearest expiry.
        """
        params: dict[str, Any] = {"symbol": symbol, "strikecount": strike_count}
        if timestamp is not None:
            params["timestamp"] = timestamp
        return await self._get(FYERS_OPTION_CHAIN_PATH, params)

    async def history(
        self,
        symbol: str,
        *,
        resolution: str,
        range_from: int,
        range_to: int,
    ) -> dict[str, Any]:
        """Fetch OHLCV candles for `symbol` between two epoch timestamps."""
        return await self._get(
            FYERS_HISTORY_PATH,
            {
                "symbol": symbol,
                "resolution": resolution,
                "date_format": "0",
                "range_from": str(range_from),
                "range_to": str(range_to),
                "cont_flag": "1",
            },
        )

    async def market_status(self) -> dict[str, Any]:
        """Fetch the current status of all exchanges/segments."""
        return await self._get(FYERS_MARKET_STATUS_PATH, {})
