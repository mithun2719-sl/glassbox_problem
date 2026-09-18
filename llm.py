from __future__ import annotations
import time
import re
from typing import Any
from config import OPENAI_API_KEY, OPENAI_MODEL
from context_engine import estimate_tokens

SYSTEM = """You are GlassBox AI. Answer only from supplied evidence and context. Do not invent facts. If evidence is absent, say you do not have enough evidence. If sources conflict, report the conflict and cite sources. Keep answers concise."""


def generate(query: str, context: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.perf_counter()
    evidence_text = "\n\n".join(f"[{e['source']}] {e['text']}" for e in evidence)
    prompt = f"{SYSTEM}\n\nContext:\n{context}\n\nEvidence:\n{evidence_text}\n\nQuestion: {query}"
    provider_error = None
    openai_key = OPENAI_API_KEY
    if openai_key:
        try:
            from openai import OpenAI
            response = OpenAI(api_key=openai_key).chat.completions.create(model=OPENAI_MODEL, temperature=0, messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}])
            answer = response.choices[0].message.content or ""
            usage = response.usage
            input_tokens = getattr(usage, "prompt_tokens", estimate_tokens(prompt))
            output_tokens = getattr(usage, "completion_tokens", estimate_tokens(answer))
            mode = "openai"
        except Exception as exc:
            provider_error = str(exc)
            openai_key = ""
    if not openai_key:
        if not evidence:
            answer = "I don't have enough evidence in the available knowledge base to answer that reliably."
            input_tokens, output_tokens, mode = estimate_tokens(prompt), estimate_tokens(answer), "offline-fallback"
        else:
            day_claims = [(e["source"], re.search(r"\d+\s*days", e["text"], re.I).group(0)) for e in evidence if re.search(r"\d+\s*days", e["text"], re.I)]
            if len({claim for _, claim in day_claims}) > 1:
                answer = "The available sources conflict: " + "; ".join(f"{source} says {claim}" for source, claim in day_claims) + "."
            else:
                answer = "Based on the available evidence: " + " ".join(e["text"].splitlines()[1] if "\n" in e["text"] else e["text"][:240] for e in evidence[:2])
            input_tokens, output_tokens, mode = estimate_tokens(prompt), estimate_tokens(answer), "openai-error-fallback" if provider_error else "offline-fallback"
    return {"answer": answer, "model": OPENAI_MODEL if mode == "openai" else mode, "provider_error": provider_error, "prompt": prompt, "input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": input_tokens + output_tokens, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "cost": round((input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000, 7), "mode": mode}
