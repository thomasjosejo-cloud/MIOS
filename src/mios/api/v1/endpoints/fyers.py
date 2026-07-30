"""Fyers OAuth endpoints.

The browser login flow:

    GET /api/v1/fyers/login     -> 307 redirect to the Fyers hosted login
    (user logs in; Fyers redirects back with an auth code)
    GET /api/v1/fyers/callback  -> exchange code, persist session, start engine

All authentication work is delegated to `mios.services.fyers_auth`; these
handlers only translate outcomes into HTTP responses.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from mios.config import Settings, get_settings
from mios.core.logging import get_logger
from mios.integrations.fyers.client import FyersAPIError, FyersAuthError
from mios.services.fyers_auth import (
    FyersAuthManager,
    FyersNotConfiguredError,
    get_auth_manager,
)
from mios.services.options_intel.runtime import connect_authenticated_engine

logger = get_logger(__name__)

router = APIRouter(prefix="/fyers", tags=["fyers"])

ManagerDep = Annotated[FyersAuthManager, Depends(get_auth_manager)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.get("/login", response_model=None)
async def login(
    manager: ManagerDep, *, json: bool = False
) -> RedirectResponse | dict[str, str]:
    """Redirect to the Fyers hosted login (or return the URL with `?json=1`)."""
    try:
        url = manager.login_url()
    except FyersNotConfiguredError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)
        ) from error

    if json:
        return {"login_url": url}
    return RedirectResponse(url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/callback")
async def callback(
    manager: ManagerDep,
    settings: SettingsDep,
    auth_code: Annotated[str | None, Query()] = None,
    code: Annotated[str | None, Query()] = None,
    s: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
) -> dict[str, object]:
    """Receive the Fyers redirect, exchange the auth code, and connect the engine."""
    if s == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fyers login was cancelled or returned an error",
        )

    received = auth_code or code
    if not received:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing auth_code in callback",
        )

    try:
        session = await manager.complete_login(received)
    except FyersNotConfiguredError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)
        ) from error
    except FyersAuthError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
        ) from error
    except FyersAPIError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)
        ) from error

    # Connect the engine automatically now that we are authenticated.
    await connect_authenticated_engine(settings)
    logger.info("Fyers authenticated; engine connecting")

    return {
        "status": "connected",
        "client_id": session.client_id,
        "expires_at": session.expires_at.isoformat(),
    }


@router.get("/status")
async def auth_status(manager: ManagerDep) -> dict[str, object]:
    """Report the current Fyers authentication status."""
    session = manager.session
    return {
        "authentication": manager.status().value,
        "client_id": session.client_id if session else None,
        "expires_at": session.expires_at.isoformat() if session else None,
    }
