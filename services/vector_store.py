"""Local TF-IDF vector store for RAG retrieval.

No API calls, no heavy ML models. Stores TF-IDF vectorizer + matrix
per game as pickle files under settings.CHROMA_DIR.
"""
from typing import List, Dict
import os
import pickle
from config import settings


def _store_dir() -> str:
    os.makedirs(settings.CHROMA_DIR, exist_ok=True)
    return settings.CHROMA_DIR


def _store_path(game_id: int) -> str:
    return os.path.join(_store_dir(), f"game_{game_id}.pkl")


def index_chunks(game_id: int, chunks: List[Dict]) -> int:
    """Build TF-IDF index for a game's chunks. Returns number indexed."""
    if not chunks:
        # remove existing index if empty
        p = _store_path(game_id)
        if os.path.exists(p):
            os.remove(p)
        return 0

    from sklearn.feature_extraction.text import TfidfVectorizer

    texts = [c["text"] for c in chunks]
    pages = [c["page"] for c in chunks]

    print(f"[vector_store] building TF-IDF index for {len(texts)} chunks...")
    # char n-grams work well for Thai (no spaces between words)
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 4),
        max_features=20000,
    )
    matrix = vectorizer.fit_transform(texts)

    with open(_store_path(game_id), "wb") as f:
        pickle.dump(
            {"vectorizer": vectorizer, "matrix": matrix, "texts": texts, "pages": pages},
            f,
        )
    print(f"[vector_store] indexed {len(texts)} chunks (TF-IDF)")
    return len(chunks)


def search(game_id: int, query: str, top_k: int = 4) -> List[Dict]:
    path = _store_path(game_id)
    if not os.path.exists(path):
        return []

    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    with open(path, "rb") as f:
        data = pickle.load(f)

    q_vec = data["vectorizer"].transform([query])
    sims = cosine_similarity(q_vec, data["matrix"])[0]
    top_idx = np.argsort(-sims)[:top_k]

    results = []
    for i in top_idx:
        results.append(
            {
                "text": data["texts"][i],
                "page": data["pages"][i],
                "score": float(sims[i]),
            }
        )
    return results


def delete_game(game_id: int) -> None:
    p = _store_path(game_id)
    if os.path.exists(p):
        os.remove(p)
