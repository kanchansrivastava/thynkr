# app/config.py

from functools import lru_cache

from pydantic_settings import BaseSettings


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
    SYSTEM_PROMPT: str = (
        "You are a fast, helpful assistant for development testing."
    )
    VECTOR_DB: str = "faiss"  # faiss | pgvector | pinecone | weaviate
    UPLOAD_DIR: str = "data"
    FAISS_INDEX_PATH: str = "data/faiss.index"
    FAISS_META_PATH: str = "data/faiss_meta.json"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"  # Auto-load env vars from .env


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
