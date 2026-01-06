from __future__ import annotations

import os
import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Lightweight retrieval (TF-IDF) so the project runs locally without heavy models.
# If you later want true embedding-based retrieval, you can swap the vectorizer layer.

_ROOT = Path(__file__).resolve().parents[1]
_INDEX_PATH = _ROOT / "db" / "rag_index.pkl"
_DATA_PATH = _ROOT / "data" / "site_pages.json"
_FAQ_PATH = _ROOT / "data" / "faq.json"

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception as e:  # pragma: no cover
    TfidfVectorizer = None
    cosine_similarity = None


@dataclass
class RagChunk:
    text: str
    meta: Dict[str, Any]


@dataclass
class RagIndex:
    vectorizer: Any
    matrix: Any
    chunks: List[RagChunk]


def _safe_read_json(path: Path) -> Any:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _build_chunks() -> List[RagChunk]:
    pages = _safe_read_json(_DATA_PATH)
    faq = _safe_read_json(_FAQ_PATH)

    chunks: List[RagChunk] = []

    # Site pages (mostly snippets in this project)
    for p in pages:
        title = (p.get("title") or "").strip()
        snippet = (p.get("snippet") or "").strip()
        keywords = p.get("keywords") or []
        url = p.get("url") or ""

        text_parts = [title, snippet, " ".join(keywords)]
        text = "\n".join([x for x in text_parts if x])
        if not text:
            continue

        chunks.append(
            RagChunk(
                text=text,
                meta={
                    "type": "site_page",
                    "title": title or url,
                    "url": url,
                    "snippet": snippet[:240] if snippet else "",
                },
            )
        )

    # FAQ
    for f in faq:
        q = (f.get("question") or "").strip()
        a = (f.get("answer") or "").strip()
        if not (q or a):
            continue
        chunks.append(
            RagChunk(
                text=f"Soru: {q}\nCevap: {a}",
                meta={"type": "faq", "title": q[:80] or "FAQ", "url": "", "snippet": a[:240]},
            )
        )

    return chunks


def build_index(force: bool = False) -> RagIndex:
    if TfidfVectorizer is None:
        raise RuntimeError(
            "scikit-learn yüklü değil. Lütfen `pip install -r requirements.txt` çalıştırın."
        )

    if _INDEX_PATH.exists() and not force:
        return load_index()

    chunks = _build_chunks()
    corpus = [c.text for c in chunks]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=60000,
        stop_words=None,  # Turkish stopword list not included by default; keep None for now.
    )
    matrix = vectorizer.fit_transform(corpus)

    _INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_INDEX_PATH, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}, f)

    return RagIndex(vectorizer=vectorizer, matrix=matrix, chunks=chunks)


def load_index() -> RagIndex:
    with open(_INDEX_PATH, "rb") as f:
        data = pickle.load(f)
    return RagIndex(vectorizer=data["vectorizer"], matrix=data["matrix"], chunks=data["chunks"])


def ensure_index() -> RagIndex:
    if _INDEX_PATH.exists():
        return load_index()
    return build_index(force=False)


def retrieve(query: str, k: int = 5) -> List[Tuple[float, RagChunk]]:
    idx = ensure_index()
    q_vec = idx.vectorizer.transform([query])
    sims = cosine_similarity(q_vec, idx.matrix).ravel()
    # top k
    top_idx = sims.argsort()[::-1][:k]
    results = [(float(sims[i]), idx.chunks[int(i)]) for i in top_idx]
    return results


def answer_with_sources(question: str, k: int = 5, min_score: float = 0.08) -> Dict[str, Any]:
    """
    Returns the API schema used by /chat:
      { "answer": str, "items": [{"title":..., "url":..., "snippet":...}, ...] }

    This is a *RAG* flow:
      1) Retrieval: find best matching chunks from the local index
      2) Generation: produce an answer grounded in retrieved chunks
         - If an LLM key is configured, you can plug it in later.
         - Default: extractive + source list (no hallucination).
    """
    hits = retrieve(question, k=k)
    good = [(s, c) for (s, c) in hits if s >= min_score]

    if not good:
        return {
            "answer": "Bu soruya yanıt verebilmek için kaynaklarda yeterli bilgi bulamadım. "
                      "İstersen biraz daha spesifik sorabilir misin? 😅",
            "items": [],
        }

    # Simple grounded answer (extractive). We do NOT invent facts.
    # We present the best snippet(s) and sources.
    best_score, best_chunk = good[0]
    best_meta = best_chunk.meta

    # Build a short, safe answer using snippets
    lines = []
    if best_meta.get("type") == "faq":
        # For FAQ chunks, we can safely show the extracted answer portion
        text = best_chunk.text
        # Try to pull after "Cevap:"
        if "Cevap:" in text:
            lines.append(text.split("Cevap:", 1)[1].strip())
        else:
            lines.append(best_meta.get("snippet", "").strip())
    else:
        # For site pages, we only have snippet; guide the user to the page(s)
        lines.append("Web sitemizde bu konuyla ilgili aşağıdaki sayfa(ları) buldum. "
                     "Detay için bağlantılara tıklayabilirsin:")

    items = []
    for score, chunk in good[: min(k, 5)]:
        m = chunk.meta
        items.append(
            {
                "title": m.get("title") or "Kaynak",
                "url": m.get("url") or "",
                "snippet": (m.get("snippet") or "") + f" (Benzerlik: {score:.2f})",
            }
        )

    return {"answer": "\n".join(lines), "items": items}
