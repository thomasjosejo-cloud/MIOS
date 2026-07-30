"""Low-level Fyers OAuth flow primitives.

The single home for the Fyers authentication protocol: building the login URL,
exchanging an auth code for an access token, and validating a token against the
live API. Endpoints and payloads were verified against the official
`fyers-apiv3` SDK. No auth logic lives outside `mios.services.fyers_auth`.
"""

import hashlib
from urllib.parse import urlencode

import httpx

from mios.config.constants import (
    FYERS_AUTH_BASE_URL,
    FYERS_GENERATE_AUTHCODE_PATH,
    FYERS_VALIDATE_AUTHCODE_PATH,
)
from mios.integrations.fyers.client import FyersAPIError, FyersAuthError, FyersClient


def login_url(*, client_id: str, redirect_uri: str, state: str) -> str:
    """Build the Fyers hosted-login URL the user visits to authorize the app."""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
    }
    return f"{FYERS_AUTH_BASE_URL}{FYERS_GENERATE_AUTHCODE_PATH}?{urlencode(params)}"


async def exchange_auth_code(
    *, client_id: str, secret_key: str, auth_code: str, timeout: float = 10.0
) -> str:
    """Exchange a one-time auth code for an access token.

    Raises `FyersAuthError` when Fyers rejects the code (invalid/expired/hash
    mismatch) and `FyersAPIError` on transport failure.
    """
    app_id_hash = hashlib.sha256(f"{client_id}:{secret_key}".encode()).hexdigest()

    async with httpx.AsyncClient(timeout=timeout) as http:
        try:
            response = await http.post(
                f"{FYERS_AUTH_BASE_URL}{FYERS_VALIDATE_AUTHCODE_PATH}",
                json={
                    "grant_type": "authorization_code",
                    "appIdHash": app_id_hash,
                    "code": auth_code,
                },
            )
        except httpx.HTTPError as error:
            raise FyersAPIError(f"Auth code exchange failed: {error}") from error

    if response.status_code >= 400:
        raise FyersAuthError(
            f"Auth code exchange rejected (HTTP {response.status_code}): "
            f"{response.text}"
        )

    body = response.json()
    if body.get("s") == "error":
        raise FyersAuthError(f"Auth code exchange rejected: {body.get('message')}")

    access_token = body.get("access_token")
    if not access_token:
        raise FyersAuthError(f"Auth code exchange response had no access_token: {body}")
    return str(access_token)


async def validate_token(
    *, client_id: str, access_token: str, probe_symbol: str, timeout: float = 10.0
) -> bool:
    """Return whether a token authenticates, by making one live authed call.

    A successful quotes call proves the token is valid; `FyersAuthError` means
    it is not. Any other error is treated as "cannot confirm" and returns
    `False` rather than raising, so startup never crashes on a bad token.
    """
    client = FyersClient(
        client_id=client_id, access_token=access_token, timeout=timeout
    )
    try:
        await client.quotes([probe_symbol])
    except FyersAuthError:
        return False
    except FyersAPIError:
        return False
    else:
        return True
    finally:
        await client.aclose()
