from pydantic import BaseModel


class StockQuote(BaseModel):
    ticker: str
    name: str | None = None
    price: float | None = None
    currency: str | None = None
    change: float | None = None
    change_percent: float | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    eps: float | None = None
    volume: float | None = None
    week52_high: float | None = None
    week52_low: float | None = None
    sector: str | None = None
    industry: str | None = None


class PricePoint(BaseModel):
    date: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None


class PriceHistory(BaseModel):
    ticker: str
    period: str
    interval: str
    points: list[PricePoint]
