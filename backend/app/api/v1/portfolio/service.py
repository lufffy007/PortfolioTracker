from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.api.v1.portfolio.schemas import Holding, HoldingCreate, Portfolio, PortfolioCreate
from app.db.models import Base  # Placeholder import for future concrete models.


class PortfolioService:
    """
    Service layer for portfolio and holding operations.

    Remains decoupled from FastAPI to support reuse by agents and scripts.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def list_portfolios(self) -> Sequence[Portfolio]:
        """
        List portfolios.

        Currently returns an empty collection until models are implemented.
        """
        return []

    def create_portfolio(self, data: PortfolioCreate) -> Portfolio:
        """
        Create a new portfolio.

        This is a stub implementation; persistence will be added once
        models are defined.
        """
        raise NotImplementedError("Portfolio creation is not implemented yet.")

    def add_holding(self, data: HoldingCreate) -> Holding:
        """
        Add a holding to a portfolio.
        """
        raise NotImplementedError("Holding creation is not implemented yet.")

