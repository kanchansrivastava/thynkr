from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings


@lru_cache(maxsize=4)
def _get_model(name: str) -> SentenceTransformer:
    return SentenceTransformer(name)


def get_embedding(text: str, model_name: str | None = None) -> list[float]:
    """Return a normalized embedding (unit vector) for cosine search."""
    name = model_name or settings.EMBEDDING_MODEL
    model = _get_model(name)
    vec = model.encode(text, convert_to_numpy=True)  # shape (D,)
    # Normalize for cosine similarity (so IP == cosine)
    norm = np.linalg.norm(vec) or 1.0
    return (vec / norm).astype(np.float32).tolist()


def get_embedding_batch(
    texts: list[str], model_name: str | None = None
) -> list[list[float]]:
    name = model_name or settings.EMBEDDING_MODEL
    model = _get_model(name)
    mat = model.encode(texts, convert_to_numpy=True)  # shape (N, D)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return (mat / norms).astype(np.float32).tolist()
