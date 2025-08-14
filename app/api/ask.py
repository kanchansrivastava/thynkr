from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.tools.claude_client import query_claude
from app.tools.search import search_chunks
from app.db import get_content_text


router = APIRouter()


class AskRequest(BaseModel):
    content_id: str
    query: str
    top_k: int = 3
    mode: str | None = None  # New: prompt mode


@router.post("/ask")
async def ask_content(request: AskRequest):
    # Load content
    text = get_content_text(request.content_id)
    if not text:
        raise HTTPException(status_code=404, detail="Content not found")

    # Fetch top chunks
    chunks = search_chunks(text, request.query, top_k=request.top_k)

    # Build prompt depending on mode
    if request.mode == "eli5":
        prompt = f"Explain like I'm 5:\n\n{request.query}\n\nContext:\n{''.join(chunks)}"
    elif request.mode == "bullet":
        prompt = f"Summarize in bullet points:\n\n{request.query}\n\nContext:\n{''.join(chunks)}"
    elif request.mode == "pros_cons":
        prompt = f"List pros and cons:\n\n{request.query}\n\nContext:\n{''.join(chunks)}"
    else:
        prompt = f"Answer the query:\n\n{request.query}\n\nContext:\n{''.join(chunks)}"

    # Call Claude
    answer = query_claude(prompt)

    return {
        "status": "success",
        "content_id": request.content_id,
        "query": request.query,
        "mode": request.mode or "default",
        "answer": answer,
        "used_chunks": len(chunks),
    }
