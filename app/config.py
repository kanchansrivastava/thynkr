# app/config.py

from pydantic_settings import BaseSettings

from functools import lru_cache

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DEBUG: bool = False
    DATABASE_URL: str
    ENV: str = "dev"
    CLAUDE_MODEL: str = "claude-3-haiku-20240307"
    MAX_TOKENS: int = 512
    TEMPERATURE: float = 0.7
    SYSTEM_PROMPT: str = "You are a fast, helpful assistant for development testing."

    class Config:
        env_file = ".env"  # Auto-load env vars from .env

@lru_cache()
def get_settings():
    return Settings()
