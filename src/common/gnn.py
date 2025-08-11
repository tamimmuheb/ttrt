from __future__ import annotations
from typing import Dict
import networkx as nx
import numpy as np


def propagate_scores(
    G: nx.Graph,
    seed_scores: Dict[str, float],
    alpha: float = 0.85,
    num_iters: int = 20,
    weight_key: str = "weight",
) -> Dict[str, float]:
    """
    Simple score propagation akin to a graph convolution / personalized PageRank.
    r_{t+1} = (1 - alpha) * s + alpha * D^{-1} A r_t

    - G: weighted undirected graph
    - seed_scores: initial scores s (for nodes not in s, s_i = 0)
    - alpha: propagation strength
    - num_iters: number of iterations
    - Returns: final scores for all nodes
    """
    nodes = list(G.nodes())
    index_of = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)

    s = np.zeros(n, dtype=np.float32)
    for k, v in seed_scores.items():
        if k in index_of:
            s[index_of[k]] = float(v)

    # Build row-stochastic matrix P = D^{-1} A
    rows = [[] for _ in range(n)]
    weights = [[] for _ in range(n)]
    for u in nodes:
        i = index_of[u]
        total_w = 0.0
        neighs = list(G[u].items())
        for v, attrs in neighs:
            w = float(attrs.get(weight_key, 1.0))
            total_w += w
        if total_w <= 0:
            continue
        for v, attrs in neighs:
            j = index_of[v]
            w = float(attrs.get(weight_key, 1.0)) / total_w
            rows[i].append(j)
            weights[i].append(w)

    r = s.copy()
    for _ in range(num_iters):
        r_next = (1.0 - alpha) * s
        # r_next += alpha * P r
        for i in range(n):
            acc = 0.0
            for j, w in zip(rows[i], weights[i]):
                acc += w * r[j]
            r_next[i] += alpha * acc
        r = r_next

    # Normalize to 0-1 range for stability
    r_min, r_max = float(r.min()), float(r.max())
    if r_max > r_min:
        r = (r - r_min) / (r_max - r_min)

    return {node: float(r[index_of[node]]) for node in nodes}