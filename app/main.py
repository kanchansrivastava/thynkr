# app/main.py
from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv
from app.core.logging_config import setup_logging
import logging

load_dotenv()  # Load values from .env into environment


setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def home():
    logger.info("Root endpoint called")
    return {"msg": "Hello! Welcome "}

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    uvicorn.run("app.main:app", host=host, port=port, reload=reload)

