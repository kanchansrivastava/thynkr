# app/main.py
from fastapi import FastAPI
import uvicorn
import os
from app.core.logging_config import setup_logging
from app.api import summarize
from app.config import get_settings
import logging



setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


app = FastAPI()

app.include_router(summarize.router)


@app.get("/")
def home():
    logger.info("Root endpoint called")
    return {"msg": "Hello! Welcome to Thynkr "}

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    uvicorn.run("app.main:app", host=host, port=port, reload=reload)

