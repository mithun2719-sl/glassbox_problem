from context_engine import build_context
from observability import Trace, load_trace, new_run_id
from graph import run_pipeline


def run(query, messages=None):
    trace = Trace(new_run_id(), "test", query)
    result = run_pipeline(query, messages or [], trace)
    trace.finish(result["llm"]["answer"], result["validation"]["status"])
    return result, trace


def test_normal_rag():
    result, _ = run("What is the refund policy?")
    assert result["retrieval"]["documents"]
    assert result["validation"]["evidence_count"] > 0


def test_unknown_question_is_flagged():
    result, _ = run("What will the company revenue be in 2030?")
    assert result["validation"]["status"] == "FAIL"
    assert result["validation"]["grounded"] is False


def test_contradiction_is_detected():
    result, _ = run("What is the refund period?")
    assert result["validation"]["conflicts"]


def test_long_context_stays_in_budget():
    messages = [{"role": "user", "content": f"Turn {i}: unrelated planning detail."} for i in range(20)]
    messages[0]["content"] = "The project uses Python."
    result, _ = run("What language does the project use?", messages)
    assert result["context"]["final_tokens"] <= result["context"]["budget"]


def test_trace_exists():
    result, trace = run("What is pricing?")
    assert load_trace(trace.data["run_id"])["run_id"] == trace.data["run_id"]
