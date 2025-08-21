# app/middleware/logging_middleware.py
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"➡️ Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"⬅️ Response: status_code={response.status_code}")
            return response
        except Exception as e:
            logger.exception(
                f"🔥 Unhandled exception during request: {request.method} {request.url}"
            )
            raise
