from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Portfolio, PortfolioHolding, User
from app.schemas.portfolio import (
    HoldingCreate,
    HoldingOut,
    PortfolioOut,
    PortfolioSummary,
)
from app.services import portfolio as portfolio_service

router = APIRouter(prefix="/portfolios", tags=["portfolio"])


def _get_owned_portfolio(db: Session, portfolio_id: int, user: User) -> Portfolio:
    p = db.get(Portfolio, portfolio_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Portfolio not found")
    return p


@router.get("", response_model=list[PortfolioOut])
def list_portfolios(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[PortfolioOut]:
    rows = db.scalars(select(Portfolio).where(Portfolio.user_id == user.id))
    return [PortfolioOut.model_validate(p) for p in rows]


@router.post("", response_model=PortfolioOut, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    name: str = "My Portfolio",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PortfolioOut:
    p = Portfolio(user_id=user.id, name=name)
    db.add(p)
    db.commit()
    db.refresh(p)
    return PortfolioOut.model_validate(p)


@router.get("/{portfolio_id}", response_model=PortfolioSummary)
def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PortfolioSummary:
    p = _get_owned_portfolio(db, portfolio_id, user)
    return portfolio_service.summarize(p)


@router.post(
    "/{portfolio_id}/holdings",
    response_model=HoldingOut,
    status_code=status.HTTP_201_CREATED,
)
def add_holding(
    portfolio_id: int,
    payload: HoldingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> HoldingOut:
    p = _get_owned_portfolio(db, portfolio_id, user)
    holding = PortfolioHolding(
        portfolio_id=p.id,
        ticker=payload.ticker.upper(),
        quantity=payload.quantity,
        purchase_price=payload.purchase_price,
    )
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return HoldingOut.model_validate(holding)


@router.delete("/{portfolio_id}/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(
    portfolio_id: int,
    holding_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    _get_owned_portfolio(db, portfolio_id, user)
    holding = db.get(PortfolioHolding, holding_id)
    if not holding or holding.portfolio_id != portfolio_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Holding not found")
    db.delete(holding)
    db.commit()
