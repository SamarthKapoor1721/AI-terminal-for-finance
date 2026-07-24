"""Pluggable data providers.

Each provider implements best-effort methods and returns None when it can't
answer (no key, rate-limited, not supported). The resolver tries providers in
priority order and falls back to the always-free yfinance provider, so the
platform works with zero API keys and transparently improves as keys are added.
"""

from app.services.providers.base import DataProvider
from app.services.providers.registry import (
    get_quote_providers,
    get_news_providers,
    get_financials_providers,
)

__all__ = [
    "DataProvider",
    "get_quote_providers",
    "get_news_providers",
    "get_financials_providers",
]
