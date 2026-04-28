"""
SnapTrade-related API endpoints.

In ASP.NET terms, this is similar to:
- `SnapTradeController` with route prefix `[Route("api/[controller]")]`

We expose simple endpoints that call our `SnapTradeClientWrapper` and
return JSON to the frontend (Streamlit or any other client).
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import Settings, get_settings
from app.external.snaptrade_client import SnapTradeClientWrapper

router = APIRouter()


def get_snaptrade_client(settings: Settings = Depends(get_settings)) -> SnapTradeClientWrapper:
    """
    FastAPI dependency that builds a `SnapTradeClientWrapper`.

    This is conceptually similar to dependency injection in ASP.NET:
    you ask for `ISnapTradeClient` in your controller constructor.
    """

    return SnapTradeClientWrapper(settings=settings)


@router.post("/users/register", tags=["SnapTrade"])
def register_snaptrade_user(
    user_id: str = Query(..., description="Your internal user identifier"),
    client: SnapTradeClientWrapper = Depends(get_snaptrade_client),
) -> Dict[str, Any]:
    """
    Register a user with SnapTrade.

    Example:
    - You call this once per logical user in your system.
    - The returned data includes a SnapTrade `userId` that you can reuse.
    """

    try:
        return client.register_user(user_id=user_id)
    except Exception as ex:  # pragma: no cover - minimal demo error handling
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/users/login-link", tags=["SnapTrade"])
def get_snaptrade_login_link(
    user_id: str = Query(..., description="User ID previously registered with SnapTrade"),
    user_secret: str = Query(..., description="User secret returned by SnapTrade registration"),
    redirect_uri: str = Query(
        ...,
        description="URL SnapTrade should send the user back to after connecting.",
    ),
    client: SnapTradeClientWrapper = Depends(get_snaptrade_client),
) -> Dict[str, Any]:
    """
    Create a "login / connect brokerage" link for the user.

    The response contains a URL. The frontend (Streamlit) will:
    - Redirect the user to that URL in the browser.
    """

    try:
        # The wrapper already returns a plain dictionary.
        return client.create_login_redirect(
            user_id=user_id,
            user_secret=user_secret,
            redirect_uri=redirect_uri,
        )
    except Exception as ex:  # pragma: no cover - minimal demo error handling
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/holdings", tags=["SnapTrade"])
def get_snaptrade_holdings(
    user_id: str = Query(..., description="User ID whose holdings should be fetched"),
    user_secret: str = Query(..., description="User secret returned by SnapTrade registration"),
    client: SnapTradeClientWrapper = Depends(get_snaptrade_client),
) -> List[Dict[str, Any]]:
    """
    Fetch holdings for all connected accounts of a given user.

    Later we will display these in Streamlit as tables and charts.
    """

    try:
        return client.get_all_holdings(user_id=user_id, user_secret=user_secret)
    except Exception as ex:  # pragma: no cover - minimal demo error handling
        raise HTTPException(status_code=500, detail=str(ex))

