from fastapi import APIRouter

from app.models.summarize import SummaryRequest
from app.tools.summarize import summarize_text

router = APIRouter()


@router.post("/summarize")
def summarize(req: SummaryRequest):
    return {"summary": summarize_text(req.text)}
