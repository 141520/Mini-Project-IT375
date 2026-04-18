"""Test PDF chunking logic (no PDF file required)."""
from services.pdf_parser import chunk_text


def test_chunk_text_short():
    assert chunk_text("สั้นมาก") == ["สั้นมาก"]


def test_chunk_text_overlap():
    txt = "A" * 1200
    chunks = chunk_text(txt, chunk_size=500, overlap=80)
    assert len(chunks) >= 2
    assert all(len(c) <= 500 for c in chunks)


def test_chunk_text_breaks_on_sentences():
    txt = "ประโยคแรก. ประโยคสอง. ประโยคสาม. " + "ข้อความยาว" * 100
    chunks = chunk_text(txt, chunk_size=200, overlap=30)
    assert len(chunks) >= 2
