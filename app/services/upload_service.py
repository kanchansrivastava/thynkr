import shutil
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile
from app.config import get_settings
from app.utils.file_reader import read_document
from app.services.vector_store import store_text

ALLOWED_EXTENSIONS = {".txt", ".md", ".html", ".pdf"}

settings = get_settings()
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def handle_upload(file: UploadFile, save_to_disk: bool = False):
    filename = file.filename or "uploaded"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if save_to_disk:
        file_path = UPLOAD_DIR / filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        with file_path.open("rb") as saved_file:
            file.file = saved_file
            normalized_text = await read_document(file)
    else:
        normalized_text = await read_document(file)

    if not normalized_text.strip():
        raise HTTPException(
            status_code=400, detail="No text extracted from file"
        )

    doc_id = str(uuid.uuid4())
    store_text(
        doc_id, normalized_text, metadata={"filename": filename, "ext": ext}
    )

    return {
        "message": f"{filename} uploaded, processed, and indexed",
        "doc_id": doc_id,
        "preview": normalized_text[:200],
    }
