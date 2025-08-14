# db.py
import sqlite3
from datetime import datetime
import json

DB_FILE = "data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS content (
        content_id TEXT PRIMARY KEY,
        text TEXT,
        filename TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        chunk_id INTEGER,
        content_id TEXT,
        text_chunk TEXT,
        embedding TEXT,
        PRIMARY KEY(chunk_id, content_id),
        FOREIGN KEY(content_id) REFERENCES content(content_id)
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS query_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_id TEXT,
        query TEXT,
        answer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def save_content(content_id: str, text: str, filename: str | None = None):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO content (content_id, text, filename) VALUES (?, ?, ?)",
              (content_id, text, filename))
    conn.commit()
    conn.close()

def save_embedding(content_id: str, chunk_id: int, text_chunk: str, embedding: list[float]):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chunks (chunk_id, content_id, text_chunk, embedding) VALUES (?, ?, ?, ?)",
              (chunk_id, content_id, text_chunk, json.dumps(embedding)))
    conn.commit()
    conn.close()

def log_query(content_id: str, query: str, answer: str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO query_history (content_id, query, answer, created_at) VALUES (?, ?, ?, ?)",
              (content_id, query, answer, datetime.utcnow()))
    conn.commit()
    conn.close()
