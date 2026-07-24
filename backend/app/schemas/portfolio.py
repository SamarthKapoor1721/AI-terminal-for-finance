from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HoldingCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=16)
    quantity: float = Field(gt=0)
    purchase_price: float = Field(gt=0)


class HoldingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    quantity: float
    purchase_price: float
    purchased_at: datetime


class HoldingValuation(BaseModel):
    id: int
    ticker: str
    quantity: float
    purchase_price: float
    current_price: float | None
    cost_basis: float
    market_value: float | None
    gain: float | None
    gain_percent: float | None
    weight: float | None  # share of portfolio market value


class PortfolioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


class PortfolioSummary(BaseModel):
    portfolio: PortfolioOut
    holdings: list[HoldingValuation]
    total_cost: float
    total_value: float | None
    total_gain: float | None
    total_gain_percent: float | None
    volatility: float | None      # annualized stdev of portfolio returns
    sharpe_ratio: float | None
