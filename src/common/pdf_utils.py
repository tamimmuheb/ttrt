from __future__ import annotations
import base64
from typing import Optional

import fitz  # PyMuPDF


def extract_text_from_pdf_base64(pdf_base64: str) -> str:
    pdf_bytes = base64.b64decode(pdf_base64)
    return extract_text_from_pdf_bytes(pdf_bytes)


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    parts = []
    for page in doc:
        parts.append(page.get_text("text"))
    return "\n".join(parts)


def sanitize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    return " ".join(text.split())