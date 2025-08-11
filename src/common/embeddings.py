from __future__ import annotations
from typing import List
from functools import lru_cache

import numpy as np
from scipy.spatial.distance import cdist

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
    _has_st = True
except Exception:
    SentenceTransformer = None  # type: ignore
    _has_st = False

try:
    from rapidfuzz.fuzz import token_set_ratio  # type: ignore
    _has_rapidfuzz = True
except Exception:
    _has_rapidfuzz = False


@lru_cache(maxsize=1)
def _get_model():
    if not _has_st:
        return None
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed_texts(texts: List[str]) -> np.ndarray:
    model = _get_model()
    if model is None:
        # Fallback: return normalized dummy vectors to preserve shapes
        arr = np.zeros((len(texts), 384), dtype=np.float32)
        if len(texts) > 0:
            arr[:, 0] = 1.0
        return arr
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return np.asarray(embeddings, dtype=np.float32)


def cosine_sim_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    dists = cdist(a, b, metric="cosine")
    return 1.0 - dists


def safe_similarity_scores(query_text: str, candidates: List[str]) -> np.ndarray:
    if _has_st:
        embs = embed_texts([query_text] + candidates)
        sims = cosine_sim_matrix(embs[:1], embs[1:]).flatten()
        return sims
    # Fallback on rapidfuzz
    scores = []
    for c in candidates:
        if _has_rapidfuzz:
            s = token_set_ratio(query_text or "", c or "") / 100.0
        else:
            # minimal fallback: Jaccard on tokens
            qa = set((query_text or "").lower().split())
            ca = set((c or "").lower().split())
            inter = len(qa & ca)
            union = len(qa | ca) or 1
            s = inter / union
        scores.append(s)
    return np.asarray(scores, dtype=np.float32)