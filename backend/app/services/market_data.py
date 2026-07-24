"""Market data (Phase 2).

Quotes are resolved through the provider chain (Finnhub → yfinance) so the app
works with zero keys and improves when keys are added. Quotes are cached briefly
in-process to soften upstream rate limits. Price history stays on yfinance
(free OHLCV for charts).
"""

from __future__ import annotations

import time
from threading import Lock

import yfinance as yf

from app.schemas.market import PriceHistory, PricePoint, StockQuote
from app.services.providers import get_quote_providers
from app.services.providers.yfinance_provider import _safe

_CACHE_TTL = 60  # seconds
_cache: dict[str, tuple[float, StockQuote]] = {}
_resolved: dict[str, str] = {}  # input symbol -> exchange-suffixed symbol that worked
_lock = Lock()

# Yahoo suffixes for Indian exchanges (NSE first — most liquid, then BSE).
_INDIA_SUFFIXES = (".NS", ".BO")


def _candidates(ticker: str) -> list[str]:
    """Symbols to try. A bare symbol (no exchange suffix) also tries Indian
    exchanges, so users can type `RELIANCE` or `TCS` and get NSE data."""
    if "." in ticker:
        return [ticker]
    return [ticker, *(f"{ticker}{sfx}" for sfx in _INDIA_SUFFIXES)]


def resolve_symbol(ticker: str) -> str:
    """Return the exchange-suffixed symbol that actually has data (cached)."""
    ticker = ticker.upper().strip()
    if ticker in _resolved:
        return _resolved[ticker]
    get_quote(ticker)  # populates _resolved as a side effect
    return _resolved.get(ticker, ticker)


def get_quote(ticker: str) -> StockQuote:
    ticker = ticker.upper().strip()
    now = time.time()

    with _lock:
        hit = _cache.get(ticker)
        if hit and now - hit[0] < _CACHE_TTL:
            return hit[1]

    last_error: Exception | None = None
    for symbol in _candidates(ticker):
        for provider in get_quote_providers():
            try:
                quote = provider.get_quote(symbol)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue
            if quote is not None:
                with _lock:
                    _cache[ticker] = (now, quote)
                    _resolved[ticker] = symbol
                return quote

    raise ValueError(
        f"No market data found for '{ticker}'"
        + (f" ({last_error})" if last_error else "")
    )


def get_history(ticker: str, period: str = "1y", interval: str = "1d") -> PriceHistory:
    ticker = ticker.upper().strip()
    symbol = resolve_symbol(ticker)  # handles .NS/.BO for Indian names
    df = yf.Ticker(symbol).history(period=period, interval=interval)
    if df.empty:
        raise ValueError(f"No price history for '{ticker}'")

    points = [
        PricePoint(
            date=idx.strftime("%Y-%m-%d"),
            open=_safe(row.get("Open")),
            high=_safe(row.get("High")),
            low=_safe(row.get("Low")),
            close=_safe(row.get("Close")),
            volume=_safe(row.get("Volume")),
        )
        for idx, row in df.iterrows()
    ]
    return PriceHistory(ticker=ticker, period=period, interval=interval, points=points)


def get_current_price(ticker: str) -> float | None:
    """Lightweight price lookup used by portfolio valuation."""
    try:
        return get_quote(ticker).price
    except ValueError:
        return None
