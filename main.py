from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import run_pipeline
from observability import Trace, load_trace, list_traces, new_run_id
from session_manager import append, history

app = FastAPI(title="GlassBox AI", version="1.0")

class ChatRequest(BaseModel):
    session_id: str = "demo-session"
    message: str

@app.get("/")
def health():
    return {"name": "GlassBox AI", "status": "ok", "trace_count": len(list_traces())}

@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(400, "message is required")
    run_id = new_run_id(); trace = Trace(run_id, request.session_id, request.message)
    try:
        messages = history(request.session_id)
        result = run_pipeline(request.message, messages, trace)
        answer = result["llm"]["answer"]; validation = result["validation"]; llm = result["llm"]
        append(request.session_id, "user", request.message); append(request.session_id, "assistant", answer)
        trace.data["metrics"] = {k: llm[k] for k in ("input_tokens", "output_tokens", "total_tokens", "cost", "latency_ms")}
        trace.data["metrics"]["retrieval_calls"] = 1; trace.data["metrics"]["llm_calls"] = len(trace.data["llm_calls"])
        trace.finish(answer, "FLAGGED" if validation["status"] == "FAIL" else "SUCCESS")
        return {"run_id": run_id, "answer": answer, "grounded": validation["grounded"], "sources": [d["source"] for d in result["retrieval"]["documents"]], "validation": validation, "metrics": trace.data["metrics"]}
    except Exception as exc:
        trace.error("pipeline", exc); trace.finish("The pipeline failed. Inspect the trace for details.", "ERROR"); raise HTTPException(500, str(exc))

@app.get("/trace/{run_id}")
def trace(run_id: str):
    data = load_trace(run_id)
    if not data: raise HTTPException(404, "trace not found")
    return data

@app.get("/session/{session_id}")
def session(session_id: str):
    return {"session_id": session_id, "messages": history(session_id)}

@app.get("/traces")
def traces():
    return list_traces()
