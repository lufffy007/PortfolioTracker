"""
Thin wrapper around the official SnapTrade Python SDK.

Why this wrapper exists:
- Keep route files simple (similar to keeping controllers thin in .NET).
- Centralize external SDK usage in one place.
- Make it easier to mock/replace later.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from snaptrade_client import Configuration
from snaptrade_client.client import SnapTrade

from app.core.config import Settings
from app.services.portfolio_analytics import flatten_holdings, total_market_value


class SnapTradeClientWrapper:
    """
    Beginner-friendly SnapTrade service layer.

    In .NET terms:
    - Similar to a typed service class injected into controllers.
    """

    def __init__(self, settings: Settings) -> None:
        # Validate keys early so route handlers can return a friendly error.
        if not settings.SNAPTRADE_CLIENT_ID or not settings.SNAPTRADE_CONSUMER_KEY:
            raise ValueError(
                "SnapTrade keys are missing. Create `backend/.env` from `.env.example` "
                "and set SNAPTRADE_CLIENT_ID + SNAPTRADE_CONSUMER_KEY."
            )

        # Build SnapTrade SDK client once for this wrapper instance.
        # In this SDK version, the main entry point is `SnapTrade`.
        configuration = Configuration(
            client_id=settings.SNAPTRADE_CLIENT_ID,
            consumer_key=settings.SNAPTRADE_CONSUMER_KEY,
        )
        self._sdk = SnapTrade(configuration=configuration)

    def register_user(self, user_id: str) -> Dict[str, Any]:
        """
        Register a user in SnapTrade.

        `user_id` should be your internal app's user ID.
        """

        response = self._sdk.authentication.register_snap_trade_user(user_id=user_id)
        return self._normalize_response(response)

    def create_login_redirect(
        self,
        user_id: str,
        user_secret: str,
        redirect_uri: str,
    ) -> Dict[str, Any]:
        """
        Get a brokerage connection/login link for this user.
        """

        response = self._sdk.authentication.login_snap_trade_user(
            user_id=user_id,
            user_secret=user_secret,
            custom_redirect=redirect_uri,
        )
        return self._normalize_response(response)

    def get_all_holdings(self, user_id: str, user_secret: str) -> List[Dict[str, Any]]:
        """
        Fetch holdings for all connected accounts for one user.

        Returns the raw list of account blocks from SnapTrade (each may contain positions).
        """

        response = self._sdk.account_information.get_all_user_holdings(
            user_id=user_id,
            user_secret=user_secret,
        )
        payload = self._normalize_response(response)
        if isinstance(payload, list):
            return payload
        return [payload]

    def get_accounts(self, user_id: str, user_secret: str) -> List[Dict[str, Any]]:
        """
        List all brokerage accounts for the user.
        """

        response = self._sdk.account_information.list_user_accounts(
            user_id=user_id,
            user_secret=user_secret,
        )
        payload = self._normalize_response(response)
        if isinstance(payload, list):
            return payload
        return [payload]

    def get_total_portfolio_value(self, user_id: str, user_secret: str) -> float:
        """
        Total portfolio value estimated as sum of (units × price) across all positions.

        This matches what we show in the UI table; cash-only balances are not included here.
        """

        raw = self.get_all_holdings(user_id, user_secret)
        rows = flatten_holdings(raw)
        return total_market_value(rows)

    def get_transactions(
        self,
        user_id: str,
        user_secret: str,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Historical activities (transactions). Uses SnapTrade reporting endpoint.

        Date filters help avoid huge payloads for old accounts.
        """

        kwargs: Dict[str, Any] = {
            "user_id": user_id,
            "user_secret": user_secret,
        }
        if start_date is not None:
            kwargs["start_date"] = start_date
        if end_date is not None:
            kwargs["end_date"] = end_date

        response = self._sdk.transactions_and_reporting.get_activities(**kwargs)
        payload = self._normalize_response(response)
        if isinstance(payload, list):
            return payload
        return [payload]

    @staticmethod
    def _normalize_response(response: Any) -> Any:
        """
        Convert SDK response objects into plain Python structures.
        """

        body = getattr(response, "body", response)
        if hasattr(body, "to_dict"):
            return body.to_dict()
        if isinstance(body, (dict, list)):
            return body
        if hasattr(body, "__dict__"):
            return dict(body.__dict__)
        return {"raw": str(body)}

