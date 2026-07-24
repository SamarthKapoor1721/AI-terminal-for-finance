"""Portfolio valuation + risk metrics (Phase 9)."""

from __future__ import annotations

import numpy as np
import yfinance as yf

from app.models import Portfolio
from app.schemas.portfolio import (
    HoldingValuation,
    PortfolioOut,
    PortfolioSummary,
)
from app.services import market_data

_RISK_FREE_RATE = 0.04  # annual; could be sourced from FRED (Phase 11)
_TRADING_DAYS = 252


def _portfolio_risk(tickers: list[str], weights: dict[str, float]) -> tuple[float | None, float | None]:
    """Annualized volatility and Sharpe ratio from 1y daily returns."""
    if not tickers:
        return None, None
    try:
        data = yf.download(
            tickers, period="1y", interval="1d", progress=False, auto_adjust=True
        )["Close"]
    except Exception:
        return None, None
    if data is None or data.empty:
        return None, None

    if isinstance(data, np.ndarray) or data.ndim == 1:
        data = data.to_frame(tickers[0])

    returns = data.pct_change().dropna()
    if returns.empty:
        return None, None

    w = np.array([weights.get(t, 0.0) for t in returns.columns])
    if w.sum() == 0:
        return None, None
    w = w / w.sum()

    port_returns = returns.to_numpy() @ w
    daily_mean = port_returns.mean()
    daily_std = port_returns.std()
    if daily_std == 0:
        return 0.0, None

    annual_vol = daily_std * np.sqrt(_TRADING_DAYS)
    annual_return = daily_mean * _TRADING_DAYS
    sharpe = (annual_return - _RISK_FREE_RATE) / annual_vol if annual_vol else None
    return float(annual_vol), (float(sharpe) if sharpe is not None else None)


def summarize(portfolio: Portfolio) -> PortfolioSummary:
    holdings = portfolio.holdings
    prices = {h.ticker: market_data.get_current_price(h.ticker) for h in holdings}

    valuations: list[HoldingValuation] = []
    total_cost = 0.0
    total_value = 0.0
    has_value = False

    for h in holdings:
        price = prices.get(h.ticker)
        cost_basis = h.quantity * h.purchase_price
        market_value = h.quantity * price if price is not None else None
        gain = (market_value - cost_basis) if market_value is not None else None
        gain_pct = (gain / cost_basis * 100) if gain is not None and cost_basis else None

        total_cost += cost_basis
        if market_value is not None:
            total_value += market_value
            has_value = True

        valuations.append(
            HoldingValuation(
                id=h.id,
                ticker=h.ticker,
                quantity=h.quantity,
                purchase_price=h.purchase_price,
                current_price=price,
                cost_basis=cost_basis,
                market_value=market_value,
                gain=gain,
                gain_percent=gain_pct,
                weight=None,
            )
        )

    # Fill in weights now that total_value is known.
    weights: dict[str, float] = {}
    if has_value and total_value > 0:
        for v in valuations:
            if v.market_value is not None:
                v.weight = v.market_value / total_value * 100
                weights[v.ticker] = v.market_value / total_value

    total_gain = (total_value - total_cost) if has_value else None
    total_gain_pct = (total_gain / total_cost * 100) if total_gain is not None and total_cost else None

    volatility, sharpe = _portfolio_risk([v.ticker for v in valuations], weights)

    return PortfolioSummary(
        portfolio=PortfolioOut.model_validate(portfolio),
        holdings=valuations,
        total_cost=total_cost,
        total_value=total_value if has_value else None,
        total_gain=total_gain,
        total_gain_percent=total_gain_pct,
        volatility=volatility,
        sharpe_ratio=sharpe,
    )
