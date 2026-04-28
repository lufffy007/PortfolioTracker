"""
Thin wrapper around the official SnapTrade Python SDK.

Why this wrapper exists:
- Keep route files simple (similar to keeping controllers thin in .NET).
- Centralize external SDK usage in one place.
- Make it easier to mock/replace later.
"""

from __future__ import annotations

from typing import Any, Dict, List

from snaptrade_client import Configuration
from snaptrade_client.client import SnapTrade

from app.core.config import Settings


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
        """

        response = self._sdk.account_information.get_all_user_holdings(
            user_id=user_id,
            user_secret=user_secret,
        )
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

