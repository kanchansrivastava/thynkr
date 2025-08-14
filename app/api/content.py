
from fastapi import APIRouter, Body,HTTPException
import uuid
from app.utils.embeddings import get_embedding
from app.db import save_content, save_embedding
from app.utils.chunker import chunk_text, CHUNK_SIZE

router = APIRouter()


@router.post("/ingest")
def ingest(text: str = Body(..., embed=True)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    content_id = str(uuid.uuid4())
    save_content(content_id, text)
    chunks = chunk_text(text)
    for idx, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        save_embedding(content_id, idx, chunk, embedding)
    return {"status": "success", "content_id": content_id, "chunks": len(chunks)}


# List content
@router.get("/list")
def list_contents():
    import sqlite3
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT content_id, filename, LENGTH(text)/? AS chunks, created_at FROM content", (CHUNK_SIZE,))
    rows = c.fetchall()
    conn.close()
    contents = [{"content_id": r[0], "filename": r[1], "chunks": int(r[2]), "created_at": r[3]} for r in rows]
    return {"status": "success", "contents": contents}


# View content
@router.get("/view/{content_id}")
def view_content(content_id: str):
    import sqlite3
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT text FROM content WHERE content_id=?", (content_id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Content not found")
    text = row[0]
    c.execute("SELECT chunk_id, text_chunk FROM chunks WHERE content_id=? ORDER BY chunk_id", (content_id,))
    chunks = [{"chunk_id": r[0], "text_chunk": r[1]} for r in c.fetchall()]
    conn.close()
    return {"status": "success", "content_id": content_id, "text": text, "chunks": chunks}
