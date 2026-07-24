from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.market import PriceHistory, StockQuote
from app.services import market_data

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/{ticker}", response_model=StockQuote)
def get_stock(ticker: str) -> StockQuote:
    try:
        return market_data.get_quote(ticker)
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))


@router.get("/{ticker}/history", response_model=PriceHistory)
def get_stock_history(
    ticker: str,
    period: str = Query("1y", pattern="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|max)$"),
    interval: str = Query("1d", pattern="^(1d|1wk|1mo)$"),
) -> PriceHistory:
    try:
        return market_data.get_history(ticker, period=period, interval=interval)
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
