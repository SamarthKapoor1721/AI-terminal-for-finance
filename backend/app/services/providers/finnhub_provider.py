"""Finnhub provider (free tier, 60 req/min). Quotes + company news.

Docs: https://finnhub.io/docs/api
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings
from app.schemas.market import StockQuote
from app.services.providers.base import DataProvider

logger = logging.getLogger(__name__)

_BASE = "https://finnhub.io/api/v1"


class FinnhubProvider(DataProvider):
    name = "finnhub"

    @property
    def available(self) -> bool:
        return bool(settings.FINNHUB_API_KEY)

    def _get(self, path: str, params: dict) -> dict | list | None:
        params = {**params, "token": settings.FINNHUB_API_KEY}
        try:
            with httpx.Client(timeout=15) as client:
                r = client.get(f"{_BASE}{path}", params=params)
                r.raise_for_status()
                return r.json()
        except Exception as exc:
            logger.warning("Finnhub %s failed: %s", path, exc)
            return None

    def get_quote(self, ticker: str) -> StockQuote | None:
        ticker = ticker.upper()
        quote = self._get("/quote", {"symbol": ticker})
        if not quote or quote.get("c") in (None, 0):
            return None
        profile = self._get("/stock/profile2", {"symbol": ticker}) or {}
        metrics = (self._get("/stock/metric", {"symbol": ticker, "metric": "all"}) or {}).get(
            "metric", {}
        )

        price = quote.get("c")
        prev = quote.get("pc")
        change = quote.get("d")
        change_pct = quote.get("dp")
        # market cap from profile is in millions
        mcap = profile.get("marketCapitalization")
        mcap = mcap * 1_000_000 if mcap else None

        return StockQuote(
            ticker=ticker,
            name=profile.get("name"),
            price=price,
            currency=profile.get("currency"),
            change=change,
            change_percent=change_pct,
            market_cap=mcap,
            pe_ratio=metrics.get("peTTM") or metrics.get("peBasicExclExtraTTM"),
            eps=metrics.get("epsTTM"),
            volume=metrics.get("10DayAverageTradingVolume"),
            week52_high=metrics.get("52WeekHigh"),
            week52_low=metrics.get("52WeekLow"),
            sector=profile.get("finnhubIndustry"),
            industry=profile.get("finnhubIndustry"),
        )

    def get_news(self, ticker: str, limit: int = 20) -> list[dict] | None:
        to = datetime.now(timezone.utc).date()
        frm = to - timedelta(days=14)
        data = self._get(
            "/company-news",
            {"symbol": ticker.upper(), "from": frm.isoformat(), "to": to.isoformat()},
        )
        if not data:
            return None
        out = []
        for item in data[:limit]:
            if not item.get("headline") or not item.get("url"):
                continue
            ts = item.get("datetime")
            out.append(
                {
                    "headline": item["headline"],
                    "url": item["url"],
                    "source": item.get("source"),
                    "published_at": datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None,
                }
            )
        return out
