# app/services/upload_service.py
import shutil
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.utils.file_reader import read_document

ALLOWED_EXTENSIONS = {".txt", ".md", ".html", ".pdf"}
UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def handle_upload(file: UploadFile, save_to_disk: bool = False):
    ext = Path(file.filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if save_to_disk:
        # Save uploaded file to disk
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Reset stream
        with file_path.open("rb") as saved_file:
            file.file = saved_file
            normalized_text = await read_document(file)
    else:
        # Read directly from memory (file not saved to disk)
        normalized_text = await read_document(file)

    return {
        "message": f"{file.filename} uploaded and processed successfully",
        "preview": normalized_text[:200],
    }
