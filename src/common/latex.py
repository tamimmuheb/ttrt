from __future__ import annotations
from typing import List, Dict
from datetime import datetime
import re

from .types import Paper


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    value = re.sub(r"\s+", "_", value)
    return value[:60]


def to_bibtex_key(paper: Paper) -> str:
    first_author = paper.authors[0].split()[-1] if paper.authors else "unknown"
    year = paper.year or datetime.now().year
    base = f"{first_author}{year}{slugify(paper.title)[:16]}"
    return base


def to_bibtex_entry(p: Paper) -> str:
    key = p.bibtex_key or to_bibtex_key(p)
    authors = " and ".join(p.authors) if p.authors else "Unknown"
    fields = {
        "title": p.title or "",
        "author": authors,
        "year": str(p.year or ""),
        "journal": p.venue or "",
        "url": p.url or "",
    }
    body = ",\n  ".join([f"{k} = {{{v}}}" for k, v in fields.items() if v])
    return f"@article{{{key},\n  {body}\n}}"


def generate_bibtex(papers: List[Paper]) -> str:
    entries = []
    for p in papers:
        key = to_bibtex_key(p)
        p.bibtex_key = key
        entries.append(to_bibtex_entry(p))
    return "\n\n".join(entries)


def generate_latex_document(hypothesis: str, papers: List[Paper], bib_filename: str = "references.bib") -> str:
    items = []
    for p in papers:
        items.append(f"\\item {p.title} (\\cite{{{p.bibtex_key}}})")
    bibliography = "\n".join(items)

    doc = f"""
\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{hyperref}}

\\title{{Graph-driven Research Hypothesis}}
\\author{{Research GNN Agent}}
\\date{{{datetime.now().strftime('%Y-%m-%d')}}}

\\begin{{document}}
\\maketitle

\\section*{{Hypothesis}}
{hypothesis}

\\section*{{Key Papers}}
\\begin{{itemize}}
{bibliography}
\\end{{itemize}}

\\bibliographystyle{{plain}}
\\bibliography{{{bib_filename[:-4]}}}
\\end{{document}}
"""
    return doc.strip()