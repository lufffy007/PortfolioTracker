from fastapi import APIRouter

from app.api.v1.portfolio.router import router as portfolio_router
from app.api.v1.snaptrade.router import router as snaptrade_router

api_v1_router = APIRouter()

# Group feature routers here to keep main application setup minimal.
api_v1_router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
api_v1_router.include_router(snaptrade_router, prefix="/snaptrade", tags=["snaptrade"])

