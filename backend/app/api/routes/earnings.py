from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_current_user
from app.models import User
from app.services import earnings as earnings_service

router = APIRouter(prefix="/earnings", tags=["earnings"])

_ALLOWED = (".pdf", ".txt")


@router.post("/analyze")
async def analyze_transcript(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
) -> dict:
    if not file.filename or not file.filename.lower().endswith(_ALLOWED):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only PDF and TXT are supported")
    data = await file.read()
    try:
        return earnings_service.analyze_transcript(file.filename, data)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
