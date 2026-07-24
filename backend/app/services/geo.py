"""Geopolitical risk heatmap (country-level news sentiment).

Runs spaCy NER over recent headlines, maps GPE entities to ISO alpha-2
country codes via pycountry, and aggregates FinBERT sentiment per country.
The spaCy model is loaded lazily, same pattern as FinBERT in sentiment.py.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from threading import Lock

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import NewsArticle
from app.services import news as news_service

logger = logging.getLogger(__name__)

_nlp = None
_lock = Lock()

# GPEs spaCy detects in financial news that are not countries.
_GPE_BLOCKLIST = {
    "wall street",
    "capitol hill",
    "silicon valley",
    "bay area",
    "dow jones",
    "federal reserve",
    "main street",
}

# Common aliases pycountry's fuzzy search misses or resolves slowly.
_COUNTRY_ALIASES = {
    "u.s.": "US",
    "u.s": "US",
    "us": "US",
    "usa": "US",
    "america": "US",
    "the united states": "US",
    "united states": "US",
    "uk": "GB",
    "u.k.": "GB",
    "britain": "GB",
    "england": "GB",
    "scotland": "GB",
    "wales": "GB",
    "russia": "RU",
    "south korea": "KR",
    "north korea": "KP",
    "iran": "IR",
    "vietnam": "VN",
    "taiwan": "TW",
    "hong kong": "HK",
    "macau": "MO",
    "uae": "AE",
    "saudi": "SA",
    "saudi arabia": "SA",
    "turkey": "TR",
    "syria": "SY",
    "venezuela": "VE",
    "bolivia": "BO",
    "tanzania": "TZ",
    "moldova": "MD",
    "laos": "LA",
    "czech republic": "CZ",
    "ivory coast": "CI",
    "the netherlands": "NL",
    "holland": "NL",
    "europe": None,  # region, not a country
    "asia": None,
    "africa": None,
    "middle east": None,
    "latin america": None,
    "eurozone": None,
    "eu": None,
}

# Macro + single-country ETFs whose news streams give broad global coverage.
MACRO_TICKERS = [
    # broad / commodities
    "SPY", "EEM", "GLD", "OIL",
    # americas
    "EWZ", "EWC", "EWW", "ARGT", "ECH", "ILF",
    # europe
    "EWG", "EWU", "EWQ", "EWI", "EWP", "EWL", "EWN", "EWD", "EPOL", "GREK", "TUR",
    # asia-pacific
    "FXI", "KWEB", "EWJ", "INDA", "EWY", "EWT", "EWA", "EWS", "EWH", "EWM",
    "THD", "EIDO", "VNM", "EPHE", "ENZL", "PAK",
    # middle east / africa
    "KSA", "UAE", "QAT", "EIS", "EZA", "NGE", "EGPT",
]

# Heatmap aggregation window and thresholds.
_RECENT_ARTICLES = 500
_MIN_MENTIONS = 2
_TOP_HEADLINES = 5


@dataclass
class HeadlineMini:
    headline: str
    url: str
    source: str | None
    ticker: str
    sentiment_score: float | None


@dataclass
class CountryRisk:
    iso2: str
    name: str
    score: float
    article_count: int
    headlines: list[HeadlineMini] = field(default_factory=list)


def _load_nlp():
    global _nlp
    if _nlp is not None:
        return _nlp
    with _lock:
        if _nlp is not None:
            return _nlp
        import spacy  # heavy import, deferred

        logger.info("Loading spaCy model en_core_web_sm")
        _nlp = spacy.load("en_core_web_sm")
        return _nlp


def _to_iso2(gpe: str) -> str | None:
    """Normalize a GPE entity string to an ISO alpha-2 country code."""
    import pycountry

    key = gpe.strip().lower()
    if not key or key in _GPE_BLOCKLIST:
        return None
    if key in _COUNTRY_ALIASES:
        return _COUNTRY_ALIASES[key]
    # Short abbreviations not in the alias map are usually acronyms ("AI",
    # "IT", "EV"), which pycountry would happily match to alpha-2/3 codes.
    if len(key) <= 3:
        return None

    try:
        country = pycountry.countries.lookup(gpe.strip())
        return country.alpha_2
    except LookupError:
        pass
    try:
        matches = pycountry.countries.search_fuzzy(gpe.strip())
        return matches[0].alpha_2 if matches else None
    except LookupError:
        return None


def extract_countries(text: str) -> list[str]:
    """Return unique ISO alpha-2 codes for countries mentioned in text."""
    text = (text or "").strip()
    if not text:
        return []

    try:
        nlp = _load_nlp()
    except Exception as exc:  # model missing
        logger.warning("spaCy unavailable, skipping NER: %s", exc)
        return []

    doc = nlp(text)
    codes: list[str] = []
    for ent in doc.ents:
        if ent.label_ != "GPE":
            continue
        iso2 = _to_iso2(ent.text)
        if iso2 and iso2 not in codes:
            codes.append(iso2)
    return codes


def fetch_market_news(db: Session) -> None:
    """Populate the DB with global macro news (slow: hits providers + FinBERT)."""
    for ticker in MACRO_TICKERS:
        try:
            news_service.fetch_and_store(db, ticker)
        except Exception as exc:  # noqa: BLE001 — one bad ticker shouldn't kill the batch
            logger.warning("Market news fetch failed for %s: %s", ticker, exc)


def build_heatmap(db: Session) -> list[CountryRisk]:
    """Aggregate recent news sentiment by country mentioned in headlines."""
    import pycountry

    articles = list(
        db.scalars(
            select(NewsArticle)
            .order_by(NewsArticle.published_at.desc().nullslast())
            .limit(_RECENT_ARTICLES)
        )
    )

    by_country: dict[str, list[NewsArticle]] = {}
    for article in articles:
        for iso2 in extract_countries(article.headline):
            by_country.setdefault(iso2, []).append(article)

    risks: list[CountryRisk] = []
    for iso2, arts in by_country.items():
        if len(arts) < _MIN_MENTIONS:
            continue

        scored = [a for a in arts if a.sentiment_score is not None]
        # Confidence-weighted average so high-confidence FinBERT calls count more.
        weight_total = sum((a.confidence or 1.0) for a in scored)
        score = (
            sum(a.sentiment_score * (a.confidence or 1.0) for a in scored) / weight_total
            if scored and weight_total
            else 0.0
        )

        country = pycountry.countries.get(alpha_2=iso2)
        name = getattr(country, "common_name", None) or (country.name if country else iso2)

        top = sorted(
            arts,
            key=lambda a: abs(a.sentiment_score or 0.0),
            reverse=True,
        )[:_TOP_HEADLINES]
        risks.append(
            CountryRisk(
                iso2=iso2,
                name=name,
                score=score,
                article_count=len(arts),
                headlines=[
                    HeadlineMini(
                        headline=a.headline,
                        url=a.url,
                        source=a.source,
                        ticker=a.company_ticker,
                        sentiment_score=a.sentiment_score,
                    )
                    for a in top
                ],
            )
        )

    risks.sort(key=lambda r: r.score)
    return risks
