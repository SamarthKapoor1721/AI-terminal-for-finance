from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import ResearchReport, User
from app.services import reports as reports_service

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportOut(BaseModel):
    id: int
    ticker: str
    title: str
    content_md: str
    created_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_model(cls, r: ResearchReport) -> "ReportOut":
        return cls(
            id=r.id, ticker=r.ticker, title=r.title,
            content_md=r.content_md, created_at=r.created_at.isoformat(),
        )


class GenerateRequest(BaseModel):
    ticker: str


def _owned(db: Session, report_id: int, user: User) -> ResearchReport:
    r = db.get(ResearchReport, report_id)
    if not r or r.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found")
    return r


@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def generate(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReportOut:
    report = reports_service.generate_report(db, user_id=user.id, ticker=payload.ticker)
    return ReportOut.from_model(report)


@router.get("", response_model=list[ReportOut])
def list_reports(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ReportOut]:
    rows = db.scalars(
        select(ResearchReport)
        .where(ResearchReport.user_id == user.id)
        .order_by(ResearchReport.created_at.desc())
    )
    return [ReportOut.from_model(r) for r in rows]


@router.get("/{report_id}", response_model=ReportOut)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReportOut:
    return ReportOut.from_model(_owned(db, report_id, user))


@router.get("/{report_id}/pdf")
def download_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    report = _owned(db, report_id, user)
    pdf = reports_service.render_pdf(report)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{report.ticker}_report.pdf"'},
    )
