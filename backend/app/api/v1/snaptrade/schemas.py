from pydantic import BaseModel, ConfigDict


class SnapTradeAccountResponse(BaseModel):
    """
    Lightweight projection of a SnapTrade account.

    Kept decoupled from any external client library models.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    currency: str | None = None

