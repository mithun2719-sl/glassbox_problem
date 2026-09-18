from __future__ import annotations
import re
from typing import Any
from config import MAX_CONTEXT_TOKENS


def estimate_tokens(text: str) -> int:
    return max(1, len(re.findall(r"\w+|[^\w\s]", text)))


def build_context(messages: list[dict[str, str]], query: str) -> dict[str, Any]:
    original = sum(estimate_tokens(m["content"]) for m in messages) + estimate_tokens(query)
    recent = messages[-6:]
    old = messages[:-6]
    query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    relevant = [m for m in old if query_terms.intersection(set(re.findall(r"[a-z0-9]+", m["content"].lower())))]
    summary = " ".join(m["content"] for m in old[:20])[:1800] if old else ""
    blocks = [f"Conversation summary: {summary}" if summary else ""]
    blocks += [f"Historical relevant message: {m['content']}" for m in relevant[-4:]]
    blocks += [f"Recent {m['role']}: {m['content']}" for m in recent]
    text = "\n".join(b for b in blocks if b)
    while estimate_tokens(text) + estimate_tokens(query) > MAX_CONTEXT_TOKENS and recent:
        recent.pop(0)
        blocks = [f"Conversation summary: {summary}" if summary else ""] + [f"Historical relevant message: {m['content']}" for m in relevant[-4:]] + [f"Recent {m['role']}: {m['content']}" for m in recent]
        text = "\n".join(b for b in blocks if b)
    final = estimate_tokens(text) + estimate_tokens(query)
    return {"text": text, "original_tokens": original, "final_tokens": final, "recent_messages": len(recent), "old_messages": len(old), "summary_generated": bool(summary), "historical_matches": len(relevant), "messages_removed": max(0, len(messages) - len(recent) - len(relevant[-4:])), "compression_ratio": round(1 - final / max(original, 1), 3), "budget": MAX_CONTEXT_TOKENS}
