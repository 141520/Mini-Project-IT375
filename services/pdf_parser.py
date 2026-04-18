"""PDF text extraction (text-based + OCR fallback) and chunking for RAG."""
from typing import List, Dict
import re

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def _ocr_page(page) -> str:
    """OCR a single PyMuPDF page using pytesseract as fallback."""
    try:
        import pytesseract
        from PIL import Image
        import io
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img, lang="eng+tha", config="--psm 3")
        return text or ""
    except Exception as e:
        print(f"[pdf_parser] OCR failed on page: {e}")
        return ""


def extract_pages(pdf_path: str) -> List[Dict]:
    """Extract text from each PDF page. Falls back to OCR for image-based pages."""
    if fitz is None:
        raise RuntimeError("PyMuPDF (pymupdf) is not installed")
    doc = fitz.open(pdf_path)
    pages = []
    ocr_used = False
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text") or ""
        text = _clean(text)
        # If less than 50 chars of real text, try OCR
        if len(text.strip()) < 50:
            ocr_text = _clean(_ocr_page(page))
            if len(ocr_text.strip()) > len(text.strip()):
                text = ocr_text
                ocr_used = True
        if text.strip():
            pages.append({"page": i, "text": text})
    doc.close()
    if ocr_used:
        print(f"[pdf_parser] OCR was used for some pages in {pdf_path}")
    return pages


def _clean(text: str) -> str:
    text = re.sub(r"\s+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks (by chars)."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
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
            break
        start = end - overlap
        if start <= 0:
            start = end
    return chunks


def chunk_pdf(pdf_path: str) -> List[Dict]:
    """Return chunks with metadata: [{text, page}, ...]"""
    pages = extract_pages(pdf_path)
    results = []
    for p in pages:
        for chunk in chunk_text(p["text"]):
            results.append({"text": chunk, "page": p["page"]})
    return results
