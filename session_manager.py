from __future__ import annotations
from collections import defaultdict

_sessions: dict[str, list[dict[str, str]]] = defaultdict(list)

def history(session_id: str) -> list[dict[str, str]]:
    return _sessions[session_id]

def append(session_id: str, role: str, content: str) -> None:
    _sessions[session_id].append({"role": role, "content": content})
