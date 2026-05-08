"""
SnapTrade-related API endpoints.

In ASP.NET terms, this is similar to:
- `SnapTradeController` with route prefix `[Route("api/[controller]")]`

We expose simple endpoints that call our `SnapTradeClientWrapper` and
return JSON to the frontend (Streamlit or any other client).
"""

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import Settings, get_settings
from app.external.snaptrade_client import SnapTradeClientWrapper
from app.services.portfolio_analytics import (
    activity_to_row,
    allocation_by_symbol,
    flatten_holdings,
    holdings_summary_dataframe,
)
router = APIRouter()


def get_snaptrade_client(settings: Settings = Depends(get_settings)) -> SnapTradeClientWrapper:
    """
    FastAPI dependency that builds a `SnapTradeClientWrapper`.

    This is conceptually similar to dependency injection in ASP.NET:
    you ask for `ISnapTradeClient` in your controller constructor.
    """

    try:
        return SnapTradeClientWrapper(settings=settings)
    except ValueError as ex:
        # Beginner-friendly config error instead of generic 500.
        raise HTTPException(status_code=400, detail=str(ex))


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
        error_text = str(ex)
        if "already exist" in error_text:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"SnapTrade user '{user_id}' already exists. "
                    "Use a different user_id or continue with login-link/holdings using this existing user."
                ),
            )
        raise HTTPException(status_code=500, detail=error_text)


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


@router.get("/accounts", tags=["SnapTrade"])
def list_snaptrade_accounts(
    user_id: str = Query(..., description="SnapTrade user id"),
    user_secret: str = Query(..., description="SnapTrade user secret"),
    client: SnapTradeClientWrapper = Depends(get_snaptrade_client),
) -> List[Dict[str, Any]]:
    """Linked brokerage accounts for this user."""

    try:
        return client.get_accounts(user_id=user_id, user_secret=user_secret)
    except Exception as ex:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/transactions", tags=["SnapTrade"])
def list_snaptrade_transactions(
    user_id: str = Query(...),
    user_secret: str = Query(...),
    start_date: Optional[str] = Query(
        None,
        description="ISO date YYYY-MM-DD (recommended for large histories)",
    ),
    end_date: Optional[str] = Query(
        None,
        description="ISO date YYYY-MM-DD",
    ),
    client: SnapTradeClientWrapper = Depends(get_snaptrade_client),
) -> List[Dict[str, Any]]:
    """
    Historical activities / transactions.

    SnapTrade may return many rows; prefer passing start_date / end_date.
    """

    try:
        sd: Optional[date] = date.fromisoformat(start_date) if start_date else None
        ed: Optional[date] = date.fromisoformat(end_date) if end_date else None
        raw = client.get_transactions(
            user_id=user_id,
            user_secret=user_secret,
            start_date=sd,
            end_date=ed,
        )
        return [activity_to_row(a) for a in raw]
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {ve}")
    except Exception as ex:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/portfolio/summary", tags=["SnapTrade"])
def portfolio_summary(
    user_id: str = Query(...),
    user_secret: str = Query(...),
    client: SnapTradeClientWrapper = Depends(get_snaptrade_client),
) -> Dict[str, Any]:
    """
    Aggregated portfolio metrics + holdings rows + allocation for charts.

    Uses pandas in the service layer to compute market value and percentages.
    """

    try:
        accounts = client.get_accounts(user_id=user_id, user_secret=user_secret)
        raw_holdings = client.get_all_holdings(user_id=user_id, user_secret=user_secret)
        rows = flatten_holdings(raw_holdings)
        summary_df, total_value = holdings_summary_dataframe(rows)
        alloc_df = allocation_by_symbol(rows)

        holdings_records = summary_df.to_dict(orient="records")
        allocation_records = [
            {
                "symbol": r["symbol"],
                "market_value": float(r["market_value"]),
                "pct": float(r["pct"]),
            }
            for r in alloc_df.to_dict(orient="records")
        ]

        return {
            "total_portfolio_value": total_value,
            "num_accounts": len(accounts),
            "num_holdings": len(rows),
            "accounts_raw": accounts,
            "holdings_table": holdings_records,
            "allocation": allocation_records,
            "note": "Total value is sum of position market values (units × price). Cash balances may appear separately in SnapTrade.",
        }
    except Exception as ex:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(ex))

