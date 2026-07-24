"""News aggregation + sentiment (Phases 4 & 5).

Pulls headlines through the provider chain (Finnhub → yfinance), scores each
with FinBERT, and upserts into the news_articles table.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import NewsArticle
from app.services import sentiment as sentiment_service
from app.services.providers import get_news_providers

logger = logging.getLogger(__name__)


def _fetch_raw(ticker: str, limit: int) -> list[dict]:
    for provider in get_news_providers():
        try:
            items = provider.get_news(ticker, limit=limit)
        except Exception as exc:  # noqa: BLE001
            logger.warning("News provider %s failed: %s", provider.name, exc)
            continue
        if items:
            return items
    return []


def fetch_and_store(db: Session, ticker: str, limit: int = 20) -> list[NewsArticle]:
    from app.services.market_data import resolve_symbol

    ticker = ticker.upper().strip()
    # Fetch news for the correct exchange listing (e.g. TCS -> TCS.NS = Tata
    # Consultancy), but store under the symbol the user typed.
    symbol = resolve_symbol(ticker)
    raw = _fetch_raw(symbol, limit)

    stored: list[NewsArticle] = []
    for item in raw:
        if not item.get("headline") or not item.get("url"):
            continue

        existing = db.scalar(select(NewsArticle).where(NewsArticle.url == item["url"]))
        if existing:
            stored.append(existing)
            continue

        result = sentiment_service.analyze(item["headline"])
        article = NewsArticle(
            company_ticker=ticker,
            headline=item["headline"],
            url=item["url"],
            source=item.get("source"),
            published_at=item.get("published_at"),
            sentiment=result.sentiment,
            sentiment_score=result.score,
            confidence=result.confidence,
        )
        db.add(article)
        stored.append(article)

    db.commit()
    for a in stored:
        db.refresh(a)
    return stored


def list_articles(db: Session, ticker: str, limit: int = 50) -> list[NewsArticle]:
    return list(
        db.scalars(
            select(NewsArticle)
            .where(NewsArticle.company_ticker == ticker.upper())
            .order_by(NewsArticle.published_at.desc().nullslast())
            .limit(limit)
        )
    )
