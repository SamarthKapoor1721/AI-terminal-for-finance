"""Always-available free provider backed by yfinance (no API key)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import yfinance as yf

from app.schemas.market import StockQuote
from app.services.providers.base import DataProvider

logger = logging.getLogger(__name__)


def _safe(value, cast=float):
    if value is None:
        return None
    try:
        out = cast(value)
        if isinstance(out, float) and out != out:  # NaN
            return None
        return out
    except (TypeError, ValueError):
        return None


class YFinanceProvider(DataProvider):
    name = "yfinance"

    def get_quote(self, ticker: str) -> StockQuote | None:
        try:
            info = yf.Ticker(ticker).info or {}
        except Exception as exc:
            logger.warning("yfinance quote failed for %s: %s", ticker, exc)
            return None
        if not info or (info.get("regularMarketPrice") is None and not info.get("longName")):
            return None

        price = _safe(info.get("currentPrice") or info.get("regularMarketPrice"))
        prev_close = _safe(info.get("previousClose"))
        change = change_pct = None
        if price is not None and prev_close:
            change = price - prev_close
            change_pct = change / prev_close * 100

        return StockQuote(
            ticker=ticker.upper(),
            name=info.get("longName") or info.get("shortName"),
            price=price,
            currency=info.get("currency"),
            change=_safe(change),
            change_percent=_safe(change_pct),
            market_cap=_safe(info.get("marketCap")),
            pe_ratio=_safe(info.get("trailingPE")),
            eps=_safe(info.get("trailingEps")),
            volume=_safe(info.get("volume") or info.get("regularMarketVolume")),
            week52_high=_safe(info.get("fiftyTwoWeekHigh")),
            week52_low=_safe(info.get("fiftyTwoWeekLow")),
            sector=info.get("sector"),
            industry=info.get("industry"),
        )

    def get_news(self, ticker: str, limit: int = 20) -> list[dict] | None:
        try:
            raw = yf.Ticker(ticker).news or []
        except Exception as exc:
            logger.warning("yfinance news failed for %s: %s", ticker, exc)
            return None

        out: list[dict] = []
        for item in raw[:limit]:
            content = item.get("content") or item
            headline = content.get("title") or item.get("title")
            url = (
                (content.get("canonicalUrl") or {}).get("url")
                or content.get("link")
                or item.get("link")
            )
            if not headline or not url:
                continue
            provider = content.get("provider") or {}
            source = (
                provider.get("displayName")
                if isinstance(provider, dict)
                else item.get("publisher")
            )
            out.append(
                {
                    "headline": headline,
                    "url": url,
                    "source": source or item.get("publisher"),
                    "published_at": self._published(item),
                }
            )
        return out

    @staticmethod
    def _published(item: dict) -> datetime | None:
        ts = item.get("providerPublishTime")
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        content = item.get("content") or {}
        pub = content.get("pubDate") or item.get("pubDate")
        if isinstance(pub, str):
            try:
                return datetime.fromisoformat(pub.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

    def get_financials(self, ticker: str):
        # Implemented in services.financials (kept there to reuse ratio logic).
        from app.services.financials import _yfinance_financials

        return _yfinance_financials(ticker)
