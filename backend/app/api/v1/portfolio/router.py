from collections.abc import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.portfolio.schemas import Portfolio
from app.api.v1.portfolio.service import PortfolioService
from app.core.dependencies import get_db

router = APIRouter()


def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioService:
    """
    Dependency that provides a PortfolioService instance.
    """
    return PortfolioService(db=db)


@router.get("/", response_model=Sequence[Portfolio])
def list_portfolios(service: PortfolioService = Depends(get_portfolio_service)) -> Sequence[Portfolio]:
    """
    List user portfolios.

    Once models are implemented, this will return persisted data.
    """
    return service.list_portfolios()

