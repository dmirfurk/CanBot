"""
Build / refresh the local RAG index.

Usage:
  python -m scripts.build_rag_index
or
  python scripts/build_rag_index.py
"""

from rag.rag_engine import build_index

if __name__ == "__main__":
    idx = build_index(force=True)
    print(f"✅ RAG index built. Chunks: {len(idx.chunks)}")
