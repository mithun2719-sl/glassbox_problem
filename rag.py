from __future__ import annotations
import re
import time
from pathlib import Path
from typing import Any
from config import DOCUMENTS_DIR, PINECONE_API_KEY, PINECONE_INDEX

STOPWORDS = {"a", "an", "and", "are", "be", "company", "does", "for", "how", "in", "is", "may", "of", "the", "to", "what", "when", "will", "with"}


def local_documents() -> list[dict[str, Any]]:
    docs = []
    for path in DOCUMENTS_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        docs.append({"source": path.name, "text": text, "terms": set(re.findall(r"[a-z0-9]+", text.lower()))})
    return docs


def retrieve(query: str, top_k: int = 3) -> dict[str, Any]:
    started = time.perf_counter()
    documents = local_documents()
    query_terms = set(re.findall(r"[a-z0-9]+", query.lower())) - STOPWORDS
    ranked = []
    for doc in documents:
        score = len(query_terms & doc["terms"]) / max(len(query_terms), 1)
        if score >= 0.2:
            ranked.append({"source": doc["source"], "text": doc["text"], "score": round(score, 3)})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    mode = "pinecone" if PINECONE_API_KEY else "local-demo"
    return {"query": query, "top_k": top_k, "documents": ranked[:top_k], "mode": mode, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "pinecone_index": PINECONE_INDEX if PINECONE_API_KEY else None}
