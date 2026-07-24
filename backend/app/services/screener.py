"""Stock screener (Phase 10).

yfinance has no bulk screening API, so this evaluates a candidate universe
(seeded set of large/mid caps) against the requested filters. Swap the
universe for a fundamentals database in production.
"""

from __future__ import annotations

from app.services import market_data
from app.services.financials import get_financials

# A small default universe so the screener returns results out of the box.
US_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
    "JPM", "V", "MA", "UNH", "HD", "PG", "XOM", "JNJ", "WMT", "KO",
    "CRM", "NFLX", "AMD", "INTC", "ORCL", "ADBE", "CSCO", "PEP",
]

# NSE large-caps (Yahoo `.NS` suffix).
INDIA_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
]

DEFAULT_UNIVERSE = US_UNIVERSE

# Selectable named universes for the screener `market` filter.
MARKETS = {"us": US_UNIVERSE, "india": INDIA_UNIVERSE, "all": US_UNIVERSE + INDIA_UNIVERSE}


def screen(
    *,
    min_market_cap: float | None = None,
    max_pe: float | None = None,
    min_revenue_growth: float | None = None,
    max_debt_to_equity: float | None = None,
    industry: str | None = None,
    universe: list[str] | None = None,
    market: str | None = None,
) -> list[dict]:
    tickers = universe or MARKETS.get((market or "us").lower(), US_UNIVERSE)
    results: list[dict] = []

    for ticker in tickers:
        try:
            quote = market_data.get_quote(ticker)
        except ValueError:
            continue

        if min_market_cap and (quote.market_cap or 0) < min_market_cap:
            continue
        if max_pe is not None and (quote.pe_ratio is None or quote.pe_ratio > max_pe):
            continue
        if industry and (quote.industry or "").lower() != industry.lower():
            continue

        # Fundamentals-based filters require statement pulls (slower).
        rev_growth = None
        dte = None
        if min_revenue_growth is not None or max_debt_to_equity is not None:
            try:
                ratios = get_financials(ticker).ratios
                rev_growth = ratios.revenue_growth
                dte = ratios.debt_to_equity
            except ValueError:
                continue
            if min_revenue_growth is not None and (rev_growth is None or rev_growth < min_revenue_growth):
                continue
            if max_debt_to_equity is not None and (dte is None or dte > max_debt_to_equity):
                continue

        results.append(
            {
                "ticker": quote.ticker,
                "name": quote.name,
                "currency": quote.currency,
                "market_cap": quote.market_cap,
                "pe_ratio": quote.pe_ratio,
                "revenue_growth": rev_growth,
                "debt_to_equity": dte,
                "sector": quote.sector,
                "industry": quote.industry,
            }
        )

    return results
