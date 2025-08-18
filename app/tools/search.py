# search.py
import sqlite3
import json
import numpy as np
from app.utils.embeddings import get_embedding
from app.db import DB_FILE, save_embedding


def search_chunks(content_id: str, query: str, top_k: int = 3):
    query_emb = np.array(get_embedding(query))
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT chunk_id, text_chunk, embedding FROM chunks WHERE content_id=?", (content_id,))
    results = []
    for chunk_id, text_chunk, emb_json in c.fetchall():
        chunk_emb = np.array(json.loads(emb_json))
        score = float(np.dot(query_emb, chunk_emb))  # cosine similarity
        results.append({"chunk_id": chunk_id, "text_chunk": text_chunk, "score": score})
    conn.close()
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def embed_text(text: str, content_id: str, chunk_size: int = 500) -> None:
    """
    Splits text into chunks, generates embeddings, and stores them.
    """
    # Simple chunking by characters (can be improved)
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk)  # Replace with actual embedding call
        save_embedding(content_id, f"{content_id}_chunk_{i}", chunk, emb)