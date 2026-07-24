"""Provider interface. Subclasses override only what they support."""

from __future__ import annotations

from app.schemas.market import StockQuote


class DataProvider:
    name: str = "base"

    @property
    def available(self) -> bool:
        """Whether this provider is configured (e.g. has an API key)."""
        return True

    def get_quote(self, ticker: str) -> StockQuote | None:
        return None

    def get_news(self, ticker: str, limit: int = 20) -> list[dict] | None:
        """Return list of {headline, url, source, published_at(datetime|None)}."""
        return None

    def get_financials(self, ticker: str):
        """Return a FinancialsResponse or None if unsupported."""
        return None
