from __future__ import annotations
from typing import Dict, List, Tuple, Any

import networkx as nx
import community as community_louvain
import numpy as np


def build_graph(
    input_node_id: str,
    paper_ids: List[str],
    title_sims: Dict[Tuple[str, str], float],
    citation_edges: List[Tuple[str, str]],
    author_edges: List[Tuple[str, str]] | None = None,
    venue_edges: List[Tuple[str, str]] | None = None,
) -> nx.Graph:
    G = nx.Graph()
    # Add input node and paper nodes
    G.add_node(input_node_id, type="input", label="input", score=1.0)
    for pid in paper_ids:
        G.add_node(pid, type="paper")

    # Similarity edges (input -> paper)
    for (src, dst), w in title_sims.items():
        if w > 0:
            if not G.has_node(src):
                G.add_node(src, type="paper")
            if not G.has_node(dst):
                G.add_node(dst, type="paper")
            G.add_edge(src, dst, relation="similarity", weight=float(w))

    # Citation edges (paper <-> paper)
    for a, b in citation_edges:
        if a in G and b in G:
            w = 1.0
            if G.has_edge(a, b):
                G[a][b]["weight"] = G[a][b].get("weight", 0.0) + w
            else:
                G.add_edge(a, b, relation="cites", weight=w)

    # Optional edges
    def add_simple_edges(edges: List[Tuple[str, str]] | None, relation: str):
        if not edges:
            return
        for a, b in edges:
            if a in G and b in G:
                if G.has_edge(a, b):
                    G[a][b]["weight"] = G[a][b].get("weight", 0.0) + 0.25
                else:
                    G.add_edge(a, b, relation=relation, weight=0.25)

    add_simple_edges(author_edges, "author")
    add_simple_edges(venue_edges, "venue")

    return G


def analyze_graph(G: nx.Graph) -> Dict[str, Any]:
    # Weighted PageRank
    pr = nx.pagerank(G, weight="weight")

    # Communities via Louvain
    partition = community_louvain.best_partition(G, weight="weight")

    # Build summaries
    communities: Dict[int, List[str]] = {}
    for node, cid in partition.items():
        communities.setdefault(cid, []).append(node)

    return {"pagerank": pr, "communities": communities}


def top_k_nodes(pr: Dict[str, float], k: int) -> List[str]:
    return [node for node, _ in sorted(pr.items(), key=lambda x: x[1], reverse=True)[:k]]