from typing import Any, Dict, List
from app.config import settings
from app.vector_backends import faiss_store
from app.utils.embeddings import get_embedding

_BACKEND = settings.VECTOR_DB.lower()


def store_text(
    ids: List[str],
    texts: List[str],
    metadatas: List[Dict[str, Any]] | None = None,
):
    """Convenience: embed and store multiple texts."""
    if metadatas is None:
        metadatas = [{} for _ in ids]
    vectors = [get_embedding(t) for t in texts]
    store_vector(ids, vectors, metadatas)


def store_vector(
    ids: List[str], vectors: List[List[float]], metadatas: List[Dict[str, Any]]
):
    if _BACKEND == "faiss":
        faiss_store.add_embeddings(ids, vectors, metadatas)
    else:
        raise ValueError(
            f"Unsupported VECTOR_DB '{_BACKEND}' for current build"
        )


def search_by_text(query: str, top_k: int = 5):
    vec = get_embedding(query)
    return search_by_vector(vec, top_k)


def search_by_vector(vector: List[float], top_k: int = 5):
    if _BACKEND == "faiss":
        return faiss_store.search(vector, top_k)
    else:
        raise ValueError(
            f"Unsupported VECTOR_DB '{_BACKEND}' for current build"
        )
