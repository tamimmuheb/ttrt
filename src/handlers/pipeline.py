from __future__ import annotations
import json
from typing import Any, Dict, List, Tuple

import numpy as np

from ..common.types import PipelineRequest, PipelineResponse, Paper, GraphNode, GraphEdge, GraphResult
from ..common.pdf_utils import extract_text_from_pdf_base64, sanitize_text
from ..common import semantic_scholar as s2
from ..common.embeddings import embed_texts, cosine_sim_matrix
from ..common.graph_builder import build_graph, analyze_graph
from ..common.latex import generate_bibtex, generate_latex_document
from ..common.llm import summarize_text, generate_hypothesis, polish_latex
from ..common.gnn import propagate_scores


def _safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur = d
    for p in path:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur


def _to_paper(obj: Dict[str, Any]) -> Paper:
    authors = [a.get("name") for a in obj.get("authors", []) if a.get("name")]
    return Paper(
        paperId=obj.get("paperId"),
        title=obj.get("title", ""),
        abstract=obj.get("abstract"),
        authors=authors,
        year=obj.get("year"),
        venue=obj.get("venue"),
        url=obj.get("url"),
        externalIds=obj.get("externalIds", {}),
        citationCount=obj.get("citationCount"),
        referenceCount=obj.get("referenceCount"),
    )


def pipeline(request: PipelineRequest) -> PipelineResponse:
    # 1) Input text
    input_text = sanitize_text(request.text or "")
    if not input_text and request.pdf_base64:
        input_text = sanitize_text(extract_text_from_pdf_base64(request.pdf_base64))

    # 2) Search
    raw_papers = s2.search_papers(request.query, limit=request.top_k)
    papers: List[Paper] = [_to_paper(p) for p in raw_papers]

    # 3) Embeddings and similarity
    texts = [input_text] + [f"{p.title}. {p.abstract or ''}" for p in papers]
    embs = embed_texts(texts)
    input_emb = embs[:1]
    paper_embs = embs[1:]
    sims = cosine_sim_matrix(input_emb, paper_embs).flatten()
    for p, s in zip(papers, sims):
        p.embedding = None
        p.rank = float(s)

    # 4) Citation edges (limited)
    citation_edges: List[Tuple[str, str]] = []
    for p in papers[: min(10, len(papers))]:
        try:
            refs = s2.get_paper_references(p.paperId, limit=50)
            for r in refs:
                if any(pp.paperId == r for pp in papers):
                    citation_edges.append((p.paperId, r))
        except Exception:
            pass

    # 4b) Author and venue co-relations
    author_edges: List[Tuple[str, str]] = []
    venue_edges: List[Tuple[str, str]] = []
    n = len(papers)
    for i in range(n):
        pi = papers[i]
        ai = set(pi.authors)
        vi = (pi.venue or '').strip().lower()
        for j in range(i + 1, n):
            pj = papers[j]
            # Author overlap
            if ai and ai.intersection(set(pj.authors)):
                author_edges.append((pi.paperId, pj.paperId))
            # Same venue
            vj = (pj.venue or '').strip().lower()
            if vi and vj and vi == vj:
                venue_edges.append((pi.paperId, pj.paperId))

    # 5) Graph
    title_sims = { ("input", p.paperId): float(s) for p, s in zip(papers, sims) }
    G = build_graph("input", [p.paperId for p in papers], title_sims, citation_edges, author_edges, venue_edges)
    analysis = analyze_graph(G)

    # 5b) GNN-style propagation to refine ranks
    seed = {"input": 1.0}
    for p, s in zip(papers, sims):
        seed[p.paperId] = float(max(0.0, s))
    propagated = propagate_scores(G, seed_scores=seed, alpha=0.85, num_iters=25)

    # Normalize ranks into papers
    for p in papers:
        base = p.rank or 0.0
        pr = analysis["pagerank"].get(p.paperId, base)
        gn = propagated.get(p.paperId, 0.0)
        # Blend: similarity 0.4, PageRank 0.3, propagation 0.3
        p.rank = float(0.4 * base + 0.3 * pr + 0.3 * gn)

    # Communities
    node_to_comm = {}
    for cid, members in analysis["communities"].items():
        for m in members:
            node_to_comm[m] = cid
    for p in papers:
        p.community = node_to_comm.get(p.paperId)

    # 6) Summaries per paper
    for p in papers:
        text = p.abstract or p.title
        p.summary = summarize_text(text)

    # 7) Hypothesis
    notes = [f"{p.title} — rank={p.rank:.4f}: {p.summary}" for p in sorted(papers, key=lambda x: x.rank or 0, reverse=True)]
    hypothesis = generate_hypothesis(request.query, notes)

    # 8) LaTeX + BibTeX
    bibtex = generate_bibtex(papers)
    latex = generate_latex_document(hypothesis, sorted(papers, key=lambda x: x.rank or 0, reverse=True))
    if request.polish_latex:
        latex = polish_latex(latex)

    # 9) Graph export
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
    nodes.append(GraphNode(id="input", type="input", label="input", score=1.0))
    for p in papers:
        nodes.append(GraphNode(id=p.paperId, type="paper", label=p.title, score=p.rank))
    for (a, b) in citation_edges:
        edges.append(GraphEdge(source=a, target=b, relation="cites", weight=1.0))
    for (a, b) in author_edges:
        edges.append(GraphEdge(source=a, target=b, relation="author", weight=0.25))
    for (a, b) in venue_edges:
        edges.append(GraphEdge(source=a, target=b, relation="venue", weight=0.25))
    for p, s in zip(papers, sims):
        edges.append(GraphEdge(source="input", target=p.paperId, relation="similarity", weight=float(s)))

    graph = GraphResult(
        nodes=nodes,
        edges=edges,
        communities=[{"id": cid, "members": mbs} for cid, mbs in analysis["communities"].items()],
    )

    return PipelineResponse(
        query=request.query,
        paper_count=len(papers),
        graph=graph,
        papers=papers,
        hypothesis=hypothesis,
        latex=latex,
        bibtex=bibtex,
        artifacts={"latex_filename": "hypothesis.tex", "bib_filename": "references.bib"},
    )


def handler(event, context):
    # Support both direct invocation with JSON and API Gateway HTTP proxy events
    payload: Dict[str, Any]
    http_method = None
    if isinstance(event, dict):
        rc = event.get("requestContext", {})
        http = rc.get("http", {})
        http_method = http.get("method") or event.get("requestContext", {}).get("httpMethod")

    # Handle CORS preflight
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
            "body": "{}",
        }

    if isinstance(event, str):
        try:
            payload = json.loads(event)
        except Exception:
            payload = {"query": event}
    elif isinstance(event, dict) and "body" in event:
        # API Gateway HTTP API proxy
        try:
            body = event.get("body")
            if isinstance(body, str):
                payload = json.loads(body)
            else:
                payload = body or {}
        except Exception:
            payload = {}
    else:
        payload = event or {}

    req = PipelineRequest(**payload)
    resp = pipeline(req)
    body_str = resp.json()

    # If invoked via API Gateway, return proxy response
    if isinstance(event, dict) and ("requestContext" in event or "version" in event or "body" in event):
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": body_str,
        }

    # Direct invocation
    return json.loads(body_str)