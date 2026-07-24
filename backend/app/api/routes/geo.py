import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.geo import CountryRiskOut, HeadlineMiniOut
from app.services import geo as geo_service

router = APIRouter(prefix="/geo", tags=["geo"])

_CACHE_TTL = 300  # seconds
_cache: dict[str, tuple[list[CountryRiskOut], float]] = {}


@router.get("/heatmap", response_model=list[CountryRiskOut])
def get_heatmap(
    refresh: bool = Query(False, description="Fetch fresh macro news first (~15s)"),
    db: Session = Depends(get_db),
) -> list[CountryRiskOut]:
    cached = _cache.get("heatmap")
    if not refresh and cached and time.monotonic() - cached[1] < _CACHE_TTL:
        return cached[0]

    if refresh:
        geo_service.fetch_market_news(db)

    result = [
        CountryRiskOut(
            iso2=r.iso2,
            name=r.name,
            score=r.score,
            article_count=r.article_count,
            headlines=[HeadlineMiniOut(**vars(h)) for h in r.headlines],
        )
        for r in geo_service.build_heatmap(db)
    ]
    _cache["heatmap"] = (result, time.monotonic())
    return result
