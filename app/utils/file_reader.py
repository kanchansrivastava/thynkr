import os

import fitz  # PyMuPDF
from fastapi import HTTPException, UploadFile

ALLOWED_TEXT_EXTENSIONS = {".txt", ".md", ".html", ".pdf"}


async def read_document(file: UploadFile) -> str:
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_TEXT_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail="Unsupported file type for reading"
        )

    try:
        content_bytes = await file.read()

        if ext == ".pdf":
            return extract_text_from_pdf(content_bytes)
        else:
            return extract_text_from_text_file(content_bytes)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read document: {str(e)}"
        )


def extract_text_from_text_file(content_bytes: bytes) -> str:
    content = content_bytes.decode("utf-8", errors="ignore")
    normalized = " ".join(content.split())
    return normalized


def extract_text_from_pdf(content_bytes: bytes) -> str:
    text = ""
    try:
        with fitz.open(stream=content_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        normalized = " ".join(text.split())
        return normalized
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text from PDF: {str(e)}",
        )
