from __future__ import annotations
import json
import os
from typing import Any, Dict, List
import numpy as np
import faiss
from app.config import settings
from pathlib import Path

# We store normalized vectors → use Inner Product (cosine equivalence)
_INDEX: faiss.Index | None = None
_META: list[dict] = []
_DIM: int | None = None


def _load_meta():
    global _META
    path = Path(settings.FAISS_META_PATH)
    if path.exists():
        _META = json.loads(path.read_text(encoding="utf-8"))
    else:
        _META = []


def _save_meta():
    Path(settings.FAISS_META_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(settings.FAISS_META_PATH).write_text(
        json.dumps(_META, ensure_ascii=False), encoding="utf-8"
    )


def _load_or_init_index(d: int | None = None):
    global _INDEX, _DIM
    if _INDEX is not None:
        return
    _load_meta()
    idx_path = settings.FAISS_INDEX_PATH
    if os.path.exists(idx_path):
        _INDEX = faiss.read_index(idx_path)
        _DIM = _INDEX.d
    else:
        _INDEX = None
        _DIM = d  # will be set on first add


def _ensure_index(d: int):
    global _INDEX, _DIM
    if _INDEX is None:
        _DIM = d
        _INDEX = faiss.IndexFlatIP(d)  # cosine via normalized vectors


def _persist():
    if _INDEX is not None:
        Path(settings.FAISS_INDEX_PATH).parent.mkdir(
            parents=True, exist_ok=True
        )
        faiss.write_index(_INDEX, settings.FAISS_INDEX_PATH)
    _save_meta()


def add_embeddings(
    ids: List[str], vectors: List[List[float]], metadatas: List[Dict[str, Any]]
) -> None:
    assert len(ids) == len(vectors) == len(metadatas)
    vecs = np.asarray(vectors, dtype=np.float32)
    _load_or_init_index(d=vecs.shape[1])
    _ensure_index(vecs.shape[1])
    _INDEX.add(vecs)  # N x D

    for i, meta in enumerate(metadatas):
        # store id + metadata; keep index-aligned
        _META.append({"id": ids[i], **meta})
    _persist()


def search(vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    q = np.asarray(vector, dtype=np.float32).reshape(1, -1)
    _load_or_init_index(d=q.shape[1])
    _ensure_index(q.shape[1])
    sims, idxs = _INDEX.search(q, top_k)
    results: List[Dict[str, Any]] = []
    for i, s in zip(idxs[0], sims[0]):
        if i < 0 or i >= len(_META):
            continue
        meta = _META[i]
        results.append(
            {
                "id": meta["id"],
                "metadata": meta,
                "score": float(s),  # higher is better
            }
        )
    return results
