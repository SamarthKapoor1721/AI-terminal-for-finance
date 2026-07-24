"""Provider priority chains. Keyed providers come first; yfinance is the
always-free fallback that closes every chain.
"""

from __future__ import annotations

from app.services.providers.base import DataProvider
from app.services.providers.finnhub_provider import FinnhubProvider
from app.services.providers.fmp_provider import FMPProvider
from app.services.providers.yfinance_provider import YFinanceProvider

# Singletons (cheap; hold no heavy state).
_yfinance = YFinanceProvider()
_finnhub = FinnhubProvider()
_fmp = FMPProvider()


def _active(providers: list[DataProvider]) -> list[DataProvider]:
    return [p for p in providers if p.available]


def get_quote_providers() -> list[DataProvider]:
    return _active([_finnhub, _yfinance])


def get_news_providers() -> list[DataProvider]:
    return _active([_finnhub, _yfinance])


def get_financials_providers() -> list[DataProvider]:
    return _active([_fmp, _yfinance])
