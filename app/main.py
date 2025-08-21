# app/main.py
import logging
import os
import traceback

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import agent, ask, content, summarize, upload
from app.config import get_settings
from app.core.logging_config import setup_logging
from app.db import init_db
from app.middleware.logging_middleware import LoggingMiddleware

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


app = FastAPI()
init_db()
app.add_middleware(LoggingMiddleware)

app.include_router(summarize.router)
app.include_router(upload.router)
app.include_router(ask.router)
app.include_router(content.router)
app.include_router(agent.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Catch all unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_trace = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    logger.error(
        f"Unhandled error: {exc}\n"
        f"URL: {request.url}\n"
        f"Method: {request.method}\n"
        f"Traceback:\n{error_trace}"
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
