from pydantic import BaseModel


class HeadlineMiniOut(BaseModel):
    headline: str
    url: str
    source: str | None
    ticker: str
    sentiment_score: float | None


class CountryRiskOut(BaseModel):
    iso2: str  # "US", "CN", "IN", ...
    name: str  # "United States", "China", "India"
    score: float  # confidence-weighted signed sentiment, -1..1
    article_count: int
    headlines: list[HeadlineMiniOut]  # top 5 by sentiment magnitude
