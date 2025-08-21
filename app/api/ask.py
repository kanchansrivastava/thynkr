import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.tools.ask import ask_about_content

router = APIRouter()


class AskRequest(BaseModel):
    content_id: str
    query: str
    top_k: int = 3
    mode: str | None = None


@router.post("/ask")
async def ask_content(request: AskRequest):
    try:
        result = ask_about_content(
            content_id=request.content_id,
            query=request.query,
            # top_k=request.top_k,
            # mode=request.mode,
        )
        return {
            "status": "success",
            "content_id": request.content_id,
            "query": request.query,
            "mode": request.mode or "default",
            **result,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
