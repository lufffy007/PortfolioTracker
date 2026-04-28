from fastapi import APIRouter, Depends

from app.api.v1.snaptrade.schemas import SnapTradeAccountResponse
from app.api.v1.snaptrade.service import SnapTradeService
from app.core.dependencies import get_settings
from app.core.config import Settings

router = APIRouter()


def get_snaptrade_service(settings: Settings = Depends(get_settings)) -> SnapTradeService:
    """
    Dependency that provides a SnapTradeService instance.
    """
    return SnapTradeService(settings=settings)


@router.get("/accounts", response_model=list[SnapTradeAccountResponse])
async def list_snaptrade_accounts(
    service: SnapTradeService = Depends(get_snaptrade_service),
) -> list[SnapTradeAccountResponse]:
    """
    Placeholder endpoint for listing SnapTrade accounts.

    Actual API calls are encapsulated in the service layer.
    """
    return await service.list_accounts()

