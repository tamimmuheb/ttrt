from __future__ import annotations
from typing import List
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cdist


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    # Small, fast model suitable for Lambda CPU
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed_texts(texts: List[str]) -> np.ndarray:
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return np.asarray(embeddings, dtype=np.float32)


def cosine_sim_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # Using cdist for efficiency. Inputs are normalized so cosine distance -> 1 - sim
    dists = cdist(a, b, metric="cosine")
    return 1.0 - dists