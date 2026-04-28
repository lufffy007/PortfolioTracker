from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PortfolioBase(BaseModel):
    """
    Shared fields for portfolio representations.
    """

    name: str
    description: str | None = None


class PortfolioCreate(PortfolioBase):
    """
    Payload for creating a new portfolio.
    """


class Portfolio(PortfolioBase):
    """
    Read model for portfolio resources.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class HoldingBase(BaseModel):
    symbol: str
    quantity: float


class HoldingCreate(HoldingBase):
    portfolio_id: int


class Holding(HoldingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    portfolio_id: int
    created_at: datetime

