from __future__ import annotations
from typing import Any
from langgraph.graph import END, StateGraph
from context_engine import build_context
from llm import generate
from rag import retrieve
from validator import validate


def run_pipeline(query: str, messages: list[dict[str, str]], trace: Any) -> dict[str, Any]:
    state: dict[str, Any] = {"query": query, "messages": messages}
    graph = StateGraph(dict)
    def context_node(s):
        s["context"] = build_context(s["messages"], s["query"])
        trace.event("context_engineering", {k: v for k, v in s["context"].items() if k != "text"})
        return s
    def retrieval_node(s):
        s["retrieval"] = retrieve(s["query"])
        trace.event("retrieval", s["retrieval"])
        return s
    def llm_node(s):
        s["llm"] = generate(s["query"], s["context"]["text"], s["retrieval"]["documents"])
        trace.data["llm_calls"].append({k: v for k, v in s["llm"].items() if k != "prompt"})
        return s
    def validation_node(s):
        s["validation"] = validate(s["llm"]["answer"], s["retrieval"]["documents"])
        trace.event("validation", s["validation"])
        return s
    graph.add_node("context", context_node); graph.add_node("retrieval", retrieval_node); graph.add_node("llm", llm_node); graph.add_node("validation", validation_node)
    graph.set_entry_point("context"); graph.add_edge("context", "retrieval"); graph.add_edge("retrieval", "llm"); graph.add_edge("llm", "validation"); graph.add_edge("validation", END)
    result = graph.compile().invoke(state)
    return result
