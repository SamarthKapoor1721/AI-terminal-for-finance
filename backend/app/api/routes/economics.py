from fastapi import APIRouter

from app.services import economics as economics_service

router = APIRouter(prefix="/economics", tags=["economics"])


@router.get("")
def get_dashboard() -> dict:
    """Economic indicators (Inflation, Rates, GDP, Unemployment) from FRED."""
    return economics_service.dashboard()


@router.get("/series/{series_id}")
def get_series(series_id: str, start: str = "2015-01-01") -> dict:
    return {"series_id": series_id, "points": economics_service.get_series(series_id, start)}
