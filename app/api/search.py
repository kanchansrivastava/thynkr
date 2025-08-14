# app/routers/search.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.vector_store import store_text, search_by_text


router = APIRouter()


class IngestItem(BaseModel):
    id: str
    text: str
    metadata: dict | None = None


class QueryItem(BaseModel):
    query: str
    top_k: int = 5


@router.post("/ingest")
def ingest(items: list[IngestItem]):
    ids = [i.id for i in items]
    texts = [i.text for i in items]
    metas = [i.metadata or {} for i in items]
    store_text(ids, texts, metas)
    return {"inserted": len(items)}


@router.post("/search")
def search(body: QueryItem):
    results = search_by_text(body.query, body.top_k)
    return {"results": results}
