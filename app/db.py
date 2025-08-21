# app/db.py
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from app.config import settings

DB_FILE = Path(settings.SQLITE_DB_FILE)
DB_FILE.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Return a SQLite connection with timeout to avoid 'database is locked'."""
    return sqlite3.connect(
        DB_FILE, timeout=10, isolation_level=None
    )  # autocommit mode


def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        # Table for content
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS content (
            text TEXT,
            content_id TEXT PRIMARY KEY,
            filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
        )
        # Table for chunks
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id INTEGER,
            content_id TEXT,
            text_chunk TEXT,
            embedding TEXT,
            PRIMARY KEY(chunk_id, content_id),
            FOREIGN KEY(content_id) REFERENCES content(content_id)
        )"""
        )
        # Table for query history
        c.execute(
            """
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT,
            query TEXT,
            answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
        )


def save_content(content_id: str, text: str, filename: str | None = None):
    """
    Save content safely.
    Uses INSERT to avoid UNIQUE constraint errors.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO content (content_id, text, filename, created_at) VALUES (?, ?, ?, ?)",
            (content_id, text, filename, datetime.utcnow()),
        )


def save_embedding(
    content_id: str, chunk_id: int, text_chunk: str, embedding: list[float]
):
    """Save or update a chunk embedding."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO chunks (chunk_id, content_id, text_chunk, embedding) VALUES (?, ?, ?, ?)",
            (chunk_id, content_id, text_chunk, json.dumps(embedding)),
        )


def log_query(content_id: str, query: str, answer: str):
    """Log a user query and answer."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO query_history (content_id, query, answer, created_at) VALUES (?, ?, ?, ?)",
            (content_id, query, answer, datetime.utcnow()),
        )


def get_content_text(content_id: str) -> str | None:
    """Return the raw text for a given content_id from SQLite."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT text FROM content WHERE content_id = ?", (content_id,)
        )
        row = c.fetchone()
    return row[0] if row else None


def retrieve_relevant_chunks(
    content_id: str, query_embedding: list[float], top_k=3
):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT text_chunk, embedding FROM chunks WHERE content_id = ?",
            (content_id,),
        )
        all_chunks = c.fetchall()

    scored_chunks = []
    for text_chunk, embedding_json in all_chunks:
        if not embedding_json:
            continue
        try:
            embedding = json.loads(embedding_json)
            if not embedding:
                continue
        except Exception:
            continue

        score = sum(q * e for q, e in zip(query_embedding, embedding))
        scored_chunks.append((score, text_chunk))

    scored_chunks.sort(reverse=True)
    return scored_chunks[:top_k]
