"""PDF text extraction and chunking for RAG."""
from typing import List, Dict
import re

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def extract_pages(pdf_path: str) -> List[Dict]:
    """Extract text from each PDF page. Returns [{page, text}, ...]."""
    if fitz is None:
        raise RuntimeError("PyMuPDF (pymupdf) is not installed")
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text") or ""
        text = _clean(text)
        if text.strip():
            pages.append({"page": i, "text": text})
    doc.close()
    return pages


def _clean(text: str) -> str:
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks (by chars, simple & reliable)."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        # try to break at a sentence or newline
        if end < len(text):
            for sep in ("\n\n", "\n", ". ", " "):
                idx = text.rfind(sep, start, end)
                if idx > start + chunk_size // 2:
                    end = idx + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break  # prevent infinite loop when we reach the end
        start = end - overlap
        if start <= 0:
            start = end  # safeguard
    return chunks


def chunk_pdf(pdf_path: str) -> List[Dict]:
    """Return chunks with metadata: [{text, page}, ...]"""
    pages = extract_pages(pdf_path)
    results = []
    for p in pages:
        for chunk in chunk_text(p["text"]):
            results.append({"text": chunk, "page": p["page"]})
    return results
