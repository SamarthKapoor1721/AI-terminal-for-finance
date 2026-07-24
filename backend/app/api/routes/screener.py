from pydantic import BaseModel
from fastapi import APIRouter

from app.services import screener as screener_service

router = APIRouter(prefix="/screener", tags=["screener"])


class ScreenRequest(BaseModel):
    min_market_cap: float | None = None
    max_pe: float | None = None
    min_revenue_growth: float | None = None
    max_debt_to_equity: float | None = None
    industry: str | None = None
    universe: list[str] | None = None
    market: str | None = "us"  # us | india | all


@router.post("")
def run_screen(payload: ScreenRequest) -> dict:
    matches = screener_service.screen(
        min_market_cap=payload.min_market_cap,
        max_pe=payload.max_pe,
        min_revenue_growth=payload.min_revenue_growth,
        max_debt_to_equity=payload.max_debt_to_equity,
        industry=payload.industry,
        universe=payload.universe,
        market=payload.market,
    )
    return {"count": len(matches), "results": matches}
