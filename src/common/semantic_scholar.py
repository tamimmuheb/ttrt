from __future__ import annotations
import os
from typing import List, Dict, Any, Optional

import requests

BASE_URL = "https://api.semanticscholar.org/graph/v1"


def _headers() -> Dict[str, str]:
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    headers = {"User-Agent": "research-gnn-agent/1.0"}
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def search_papers(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    fields = [
        "paperId","title","abstract","authors","year","venue","url",
        "externalIds","citationCount","referenceCount"
    ]
    params = {
        "query": query,
        "limit": limit,
        "fields": ",".join(fields)
    }
    url = f"{BASE_URL}/paper/search"
    resp = requests.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def get_paper_references(paper_id: str, limit: int = 50) -> List[str]:
    url = f"{BASE_URL}/paper/{paper_id}/references"
    params = {"fields": "paperId", "limit": limit}
    resp = requests.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    ids = []
    for ref in data.get("data", []):
        cited = ref.get("citedPaper", {})
        pid = cited.get("paperId")
        if pid:
            ids.append(pid)
    return ids


def get_paper_citations(paper_id: str, limit: int = 50) -> List[str]:
    url = f"{BASE_URL}/paper/{paper_id}/citations"
    params = {"fields": "paperId", "limit": limit}
    resp = requests.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    ids = []
    for ref in data.get("data", []):
        citing = ref.get("citingPaper", {})
        pid = citing.get("paperId")
        if pid:
            ids.append(pid)
    return ids