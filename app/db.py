# app/db.py
import sqlite3
from datetime import datetime
import json
from pathlib import Path

DB_FILE = "data.db"
Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)  # ensure folder exists


def get_connection():
    """Return a SQLite connection with timeout to avoid 'database is locked'."""
    return sqlite3.connect(DB_FILE, timeout=10, isolation_level=None)  # autocommit mode


def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        # Table for content
        c.execute("""
        CREATE TABLE IF NOT EXISTS content (
            content_id TEXT PRIMARY KEY,
            text TEXT,
            filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        # Table for chunks
        c.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id INTEGER,
            content_id TEXT,
            text_chunk TEXT,
            embedding TEXT,
            PRIMARY KEY(chunk_id, content_id),
            FOREIGN KEY(content_id) REFERENCES content(content_id)
        )""")
        # Table for query history
        c.execute("""
        CREATE TABLE IF NOT EXISTS query_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id TEXT,
            query TEXT,
            answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")


def save_content(content_id: str, text: str, filename: str | None = None):
    """
    Save content safely.
    Uses INSERT OR REPLACE to avoid UNIQUE constraint errors.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO content (content_id, text, filename, created_at) VALUES (?, ?, ?, ?)",
            (content_id, text, filename, datetime.utcnow())
        )


def save_embedding(content_id: str, chunk_id: int, text_chunk: str, embedding: list[float]):
    """Save or update a chunk embedding."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO chunks (chunk_id, content_id, text_chunk, embedding) VALUES (?, ?, ?, ?)",
            (chunk_id, content_id, text_chunk, json.dumps(embedding))
        )


def log_query(content_id: str, query: str, answer: str):
    """Log a user query and answer."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO query_history (content_id, query, answer, created_at) VALUES (?, ?, ?, ?)",
            (content_id, query, answer, datetime.utcnow())
        )


def get_content_text(content_id: str) -> str | None:
    """Return the raw text for a given content_id from SQLite."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT text FROM content WHERE content_id = ?", (content_id,))
        row = c.fetchone()
    return row[0] if row else None
