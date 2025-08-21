import uuid
from pathlib import Path

from fastapi import File, HTTPException, UploadFile

from app.config import get_settings
# from app.services.vector_store import store_text
from app.db import save_content, save_embedding  # your DB functions
from app.utils.chunker import chunk_text
from app.utils.embeddings import get_embedding

ALLOWED_EXTENSIONS = {".txt", ".md", ".html", ".pdf"}

settings = get_settings()
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def handle_upload(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Read file content
    content_bytes = await file.read()
    try:
        text = content_bytes.decode("utf-8")  # assume txt file
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400, detail="Only UTF-8 text files are supported"
        )

    # Generate unique content ID and save raw content
    content_id = str(uuid.uuid4())
    save_content(content_id, text)

    # Split text into chunks
    chunks = chunk_text(text)

    # Generate embeddings for each chunk and save
    for idx, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)  # returns list[float]
        save_embedding(content_id, idx, chunk, embedding)

    # Return success response
    return {
        "status": "success",
        "content_id": content_id,
        "filename": file.filename,
        "chunks": len(chunks),
    }
