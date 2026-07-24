from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Document, User
from app.services import edgar as edgar_service
from app.services import rag as rag_service

router = APIRouter(prefix="/research", tags=["research"])

_ALLOWED = (".pdf", ".txt")


class DocumentOut(BaseModel):
    id: int
    title: str
    ticker: str | None
    doc_type: str
    status: str
    chunk_count: int

    class Config:
        from_attributes = True


class AskRequest(BaseModel):
    question: str
    ticker: str | None = None


@router.post("/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    ticker: str | None = Form(None),
    doc_type: str = Form("other"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DocumentOut:
    if not file.filename or not file.filename.lower().endswith(_ALLOWED):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only PDF and TXT are supported")

    data = await file.read()
    try:
        doc = rag_service.ingest(
            db,
            user_id=user.id,
            title=title,
            filename=file.filename,
            data=data,
            ticker=ticker,
            doc_type=doc_type,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Ingestion failed: {exc}")
    return DocumentOut.model_validate(doc)


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[DocumentOut]:
    rows = db.scalars(select(Document).where(Document.user_id == user.id))
    return [DocumentOut.model_validate(d) for d in rows]


@router.post("/ask")
def ask(
    payload: AskRequest,
    user: User = Depends(get_current_user),
) -> dict:
    return rag_service.answer(payload.question, ticker=payload.ticker)


# --- SEC EDGAR (no API key) ---


@router.get("/filings/{ticker}")
def list_filings(ticker: str, user: User = Depends(get_current_user)) -> dict:
    try:
        filings = edgar_service.list_filings(ticker)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"EDGAR error: {exc}")
    if not filings:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No filings found for '{ticker}'")
    return {"ticker": ticker.upper(), "filings": filings}


class IngestFilingRequest(BaseModel):
    ticker: str
    url: str
    form: str = "filing"
    date: str | None = None


@router.post("/filings/ingest", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def ingest_filing(
    payload: IngestFilingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DocumentOut:
    try:
        text = edgar_service.fetch_filing_text(payload.url)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Could not fetch filing: {exc}")
    if not text:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Filing had no extractable text")

    title = f"{payload.ticker.upper()} {payload.form}" + (f" ({payload.date})" if payload.date else "")
    doc = rag_service.ingest(
        db,
        user_id=user.id,
        title=title,
        filename="filing.txt",
        data=text.encode("utf-8"),
        ticker=payload.ticker,
        doc_type="filing",
    )
    return DocumentOut.model_validate(doc)
