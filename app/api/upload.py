# app/routes/upload.py
from fastapi import APIRouter, File, UploadFile

from app.services.upload_service import handle_upload

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return await handle_upload(file)
