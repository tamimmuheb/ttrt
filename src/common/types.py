from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PipelineRequest(BaseModel):
    query: str
    text: Optional[str] = None
    pdf_base64: Optional[str] = None
    top_k: int = 20
    llm_provider: Optional[str] = None
    polish_latex: bool = False


class Paper(BaseModel):
    paperId: str
    title: str
    abstract: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    url: Optional[str] = None
    externalIds: Dict[str, Any] = Field(default_factory=dict)
    citationCount: Optional[int] = None
    referenceCount: Optional[int] = None
    embedding: Optional[List[float]] = None
    rank: Optional[float] = None
    community: Optional[int] = None
    summary: Optional[str] = None
    bibtex_key: Optional[str] = None


class GraphNode(BaseModel):
    id: str
    type: str  # 'input' | 'paper'
    label: str
    score: Optional[float] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str  # 'similarity' | 'cites' | 'author' | 'venue'
    weight: float


class GraphResult(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    communities: List[Dict[str, Any]]


class PipelineResponse(BaseModel):
    query: str
    paper_count: int
    graph: GraphResult
    papers: List[Paper]
    hypothesis: str
    latex: str
    bibtex: str
    artifacts: Dict[str, str]