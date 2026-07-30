"""One-time Fyers OAuth login flow.

This is operator-driven, not called by the running application: the operator
visits the generated URL, logs in, and pastes the resulting `auth_code` back to
exchange it for an access token, which is then stored as `FYERS_ACCESS_TOKEN`.
The engine itself only ever uses an already-issued token via `FyersClient`.
"""

import hashlib
from urllib.parse import urlencode

import httpx

from mios.config.constants import (
    FYERS_AUTH_BASE_URL,
    FYERS_GENERATE_AUTHCODE_PATH,
    FYERS_VALIDATE_AUTHCODE_PATH,
)
from mios.integrations.fyers.client import FyersAPIError, FyersAuthError


def generate_authcode_url(*, client_id: str, redirect_uri: str, state: str) -> str:
    """Build the URL the operator visits to authorize the app and get an auth code."""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
    }
    return f"{FYERS_AUTH_BASE_URL}{FYERS_GENERATE_AUTHCODE_PATH}?{urlencode(params)}"


async def exchange_auth_code(*, client_id: str, secret_key: str, auth_code: str) -> str:
    """Exchange a one-time auth code for an access token."""
    app_id_hash = hashlib.sha256(f"{client_id}:{secret_key}".encode()).hexdigest()

    async with httpx.AsyncClient(timeout=10.0) as http:
        try:
            response = await http.post(
                f"{FYERS_AUTH_BASE_URL}{FYERS_VALIDATE_AUTHCODE_PATH}",
                json={
                    "grant_type": "authorization_code",
                    "appIdHash": app_id_hash,
                    "code": auth_code,
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise FyersAPIError(f"Auth code exchange failed: {error}") from error

    body = response.json()
    if body.get("s") == "error":
        raise FyersAuthError(f"Auth code exchange rejected: {body.get('message')}")

    access_token = body.get("access_token")
    if not access_token:
        msg = f"Auth code exchange response had no access_token: {body}"
        raise FyersAuthError(msg)

    return str(access_token)
