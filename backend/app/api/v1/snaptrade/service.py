from typing import Iterable, List

from app.api.v1.snaptrade.schemas import SnapTradeAccountResponse
from app.core.config import Settings
from app.external.snaptrade_client import SnapTradeClient


class SnapTradeService:
    """
    Service layer for SnapTrade-related operations.

    This class is intentionally kept free of FastAPI-specific constructs
    to make it easily reusable by future AI agents or background workers.
    """

    def __init__(self, settings: Settings, client: SnapTradeClient | None = None) -> None:
        self._settings = settings
        self._client = client or SnapTradeClient.from_settings(settings)

    async def list_accounts(self) -> List[SnapTradeAccountResponse]:
        """
        Fetch and normalize account information from SnapTrade.
        """
        raw_accounts: Iterable[dict] = await self._client.fetch_accounts()
        return [
            SnapTradeAccountResponse(
                id=str(account.get("id")),
                name=account.get("name", "Unknown"),
                currency=account.get("currency"),
            )
            for account in raw_accounts
        ]

