import os
from logging.config import dictConfig


def setup_logging():
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir, "app.log"
    )  # base name (rotated automatically)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "formatter": "default",
                    "filename": log_file,
                    "when": "midnight",  # Rotate at midnight
                    "backupCount": 7,  # Keep last 7 days of logs
                    "encoding": "utf-8",
                    "utc": True,  # Optional: use UTC time
                },
            },
            "root": {"level": "INFO", "handlers": ["console", "file"]},
        }
    )
