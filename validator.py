from __future__ import annotations
import re
from typing import Any


def validate(answer: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    conflicts = []
    for i, left in enumerate(evidence):
        for right in evidence[i + 1:]:
            ldays = re.search(r"(\d+)\s*days", left["text"], re.I)
            rdays = re.search(r"(\d+)\s*days", right["text"], re.I)
            if ldays and rdays and ldays.group(1) != rdays.group(1):
                conflicts.append({"source_a": left["source"], "claim_a": ldays.group(0), "source_b": right["source"], "claim_b": rdays.group(0)})
    unsupported = [] if evidence and not answer.lower().startswith("i don't have enough") else (["No supporting evidence"] if not evidence else [])
    grounded = bool(evidence) and not unsupported and not conflicts
    return {"grounded": grounded, "evidence_count": len(evidence), "unsupported_claims": unsupported, "conflicts": conflicts, "status": "FAIL" if not grounded or conflicts else "PASS"}
