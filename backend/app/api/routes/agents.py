from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.services import agents as agents_service

router = APIRouter(prefix="/agents", tags=["agents"])


class MemoRequest(BaseModel):
    ticker: str
    query: str = "Should I invest in this company?"


@router.post("/research")
def run_research(
    payload: MemoRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Run the multi-agent research workflow and return findings + final memo."""
    return agents_service.run(db, ticker=payload.ticker, query=payload.query)
