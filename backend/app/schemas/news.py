from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NewsArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_ticker: str
    headline: str
    source: str | None
    url: str
    published_at: datetime | None
    sentiment: str | None
    sentiment_score: float | None
    confidence: float | None


class SentimentSummary(BaseModel):
    ticker: str
    article_count: int
    positive: int
    negative: int
    neutral: int
    overall_score: float | None  # mean signed sentiment, -1..1


class SentimentRequest(BaseModel):
    text: str
