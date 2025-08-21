# search.py
import json

import numpy as np

from app.db import get_connection, save_embedding
from app.utils.chunker import chunk_text
from app.utils.embeddings import get_embedding


def search_chunks(content_id: str, query: str, top_k: int = 3):
    query_emb = np.array(get_embedding(query))
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT chunk_id, text_chunk, embedding FROM chunks WHERE content_id=?",
            (content_id,),
        )
        results = []
        for chunk_id, text_chunk, emb_json in c.fetchall():
            chunk_emb = np.array(json.loads(emb_json))
            score = float(np.dot(query_emb, chunk_emb))  # cosine similarity
            results.append(
                {
                    "chunk_id": chunk_id,
                    "text_chunk": text_chunk,
                    "score": score,
                }
            )
        conn.close()
        results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def embed_content(text: str, content_id: str, chunk_size: int = 500) -> None:
    chunks = chunk_text(text=text, max_tokens=chunk_size)
    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        save_embedding(content_id, f"{content_id}_chunk_{i}", chunk, emb)


def embed_query(query: str) -> list[float]:
    return get_embedding(query)
