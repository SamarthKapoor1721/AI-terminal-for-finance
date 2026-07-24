from fastapi import APIRouter

from app.api.routes import (
    agents,
    auth,
    earnings,
    economics,
    financials,
    geo,
    news,
    portfolio,
    reports,
    research,
    screener,
    stocks,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(stocks.router)
api_router.include_router(financials.router)
api_router.include_router(news.router)
api_router.include_router(portfolio.router)
api_router.include_router(screener.router)
api_router.include_router(research.router)
api_router.include_router(reports.router)
api_router.include_router(agents.router)
api_router.include_router(earnings.router)
api_router.include_router(economics.router)
api_router.include_router(geo.router)
