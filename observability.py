from __future__ import annotations
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from config import TRACES_DIR


def new_run_id() -> str:
    return f"run_{uuid.uuid4().hex[:8]}"


class Trace:
    def __init__(self, run_id: str, session_id: str, query: str):
        self.data: dict[str, Any] = {
            "run_id": run_id, "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_query": query, "status": "RUNNING", "errors": [],
            "context_engineering": {}, "retrieval": {}, "llm_calls": [],
            "validation": {}, "metrics": {}, "final_answer": ""
        }
        self.started = time.perf_counter()

    def event(self, name: str, payload: dict[str, Any]) -> None:
        self.data[name] = payload

    def error(self, component: str, error: Exception | str) -> None:
        self.data["errors"].append({"component": component, "message": str(error), "timestamp": datetime.now(timezone.utc).isoformat()})

    def finish(self, answer: str, status: str) -> dict[str, Any]:
        self.data["final_answer"] = answer
        self.data["status"] = status
        self.data["metrics"]["latency_ms"] = round((time.perf_counter() - self.started) * 1000, 2)
        TRACES_DIR.mkdir(exist_ok=True)
        (TRACES_DIR / f"{self.data['run_id']}.json").write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        return self.data


def load_trace(run_id: str) -> dict[str, Any] | None:
    path = TRACES_DIR / f"{run_id}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def list_traces() -> list[dict[str, Any]]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(TRACES_DIR.glob("run_*.json"), reverse=True)]
