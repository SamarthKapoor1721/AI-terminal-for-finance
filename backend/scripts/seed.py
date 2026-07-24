"""Seed a demo user and a sample portfolio.

Run from the backend dir:  python -m scripts.seed
(or inside docker:  docker compose exec backend python -m scripts.seed)
"""

from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models import Portfolio, PortfolioHolding, User
from sqlalchemy import select

DEMO_EMAIL = "demo@terminal.ai"
DEMO_PASSWORD = "demo12345"

SAMPLE_HOLDINGS = [
    ("AAPL", 10, 180.0),
    ("NVDA", 5, 95.0),
    ("MSFT", 8, 380.0),
]


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if not user:
            user = User(
                email=DEMO_EMAIL,
                name="Demo Analyst",
                password_hash=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print("Demo user already exists.")

        if not user.portfolios:
            portfolio = Portfolio(user_id=user.id, name="Demo Portfolio")
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
            for ticker, qty, price in SAMPLE_HOLDINGS:
                db.add(
                    PortfolioHolding(
                        portfolio_id=portfolio.id,
                        ticker=ticker,
                        quantity=qty,
                        purchase_price=price,
                    )
                )
            db.commit()
            print(f"Seeded portfolio with {len(SAMPLE_HOLDINGS)} holdings.")
        else:
            print("Demo portfolio already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
