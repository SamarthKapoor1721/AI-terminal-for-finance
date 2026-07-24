from fastapi import APIRouter, HTTPException, status

from app.schemas.financials import FinancialsResponse
from app.services import financials as financials_service

router = APIRouter(prefix="/financials", tags=["financials"])


@router.get("/{ticker}", response_model=FinancialsResponse)
def get_financials(ticker: str) -> FinancialsResponse:
    try:
        return financials_service.get_financials(ticker)
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
