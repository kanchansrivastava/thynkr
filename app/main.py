# app/main.py
import logging
import os

import uvicorn
from fastapi import FastAPI

from app.api import summarize, upload, ask, content, agent
from app.config import get_settings
from app.core.logging_config import setup_logging
from app.db import init_db

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


app = FastAPI()
init_db()

app.include_router(summarize.router)
app.include_router(upload.router)
app.include_router(ask.router)
app.include_router(content.router)
app.include_router(agent.router)


@app.get("/")
def home():
    logger.info("Root endpoint called")
    return {"msg": "Hello! Welcome to Thynkr "}


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
