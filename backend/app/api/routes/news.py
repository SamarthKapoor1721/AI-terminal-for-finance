from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.news import NewsArticleOut, SentimentRequest, SentimentSummary
from app.services import news as news_service
from app.services import sentiment as sentiment_service

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/{ticker}", response_model=list[NewsArticleOut])
def get_news(
    ticker: str,
    refresh: bool = Query(False, description="Fetch fresh articles from source"),
    db: Session = Depends(get_db),
) -> list[NewsArticleOut]:
    if refresh:
        news_service.fetch_and_store(db, ticker)
    articles = news_service.list_articles(db, ticker)
    return [NewsArticleOut.model_validate(a) for a in articles]


@router.get("/{ticker}/sentiment", response_model=SentimentSummary)
def get_sentiment_summary(
    ticker: str,
    db: Session = Depends(get_db),
) -> SentimentSummary:
    articles = news_service.list_articles(db, ticker)
    scored = [a for a in articles if a.sentiment]
    pos = sum(1 for a in scored if a.sentiment == "positive")
    neg = sum(1 for a in scored if a.sentiment == "negative")
    neu = sum(1 for a in scored if a.sentiment == "neutral")
    overall = (
        sum(a.sentiment_score for a in scored if a.sentiment_score is not None) / len(scored)
        if scored
        else None
    )
    return SentimentSummary(
        ticker=ticker.upper(),
        article_count=len(scored),
        positive=pos,
        negative=neg,
        neutral=neu,
        overall_score=overall,
    )


@router.post("/analyze")
def analyze_text(payload: SentimentRequest) -> dict:
    result = sentiment_service.analyze(payload.text)
    return {
        "sentiment": result.sentiment,
        "confidence": result.confidence,
        "score": result.score,
    }
