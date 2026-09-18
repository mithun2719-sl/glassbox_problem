# GlassBox AI

GlassBox is an observable, context-aware RAG demo for the Glass Box Problem track. It answers questions while exposing the context it selected, documents it retrieved, model calls, token usage, cost, latency, validation, and failures.

## Stack

- FastAPI API and Streamlit UI
- LangGraph pipeline orchestration
- OpenAI chat generation
- Pinecone-ready retrieval configuration
- Tavily-ready extension point for web search
- Local JSON traces that work offline and never depend on an observability service

The default demo works without API keys using the checked-in knowledge base and deterministic fallback generation. Add an OpenAI key to `.env` to enable model generation. Pinecone and Tavily credentials are accepted in the configuration for swapping in hosted retrieval and web search.

## Run

```bash
cd /Users/jiviteshkumar/Downloads/glassbox
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python ingest.py
uvicorn main:app --reload
```

In another terminal:

```bash
cd /Users/jiviteshkumar/Downloads/glassbox
source .venv/bin/activate
streamlit run app.py
```

Open `http://localhost:8501`. The API health endpoint is `http://localhost:8000/`.

## Pipeline

```text
User -> Streamlit -> FastAPI -> LangGraph
                              |-> context budget and history selection
                              |-> Pinecone-ready/local retrieval
                              |-> OpenAI or offline generation
                              |-> grounding and contradiction validation
                              |-> local JSON trace
```

Every request receives a `run_id` and writes `traces/run_<id>.json`. Each trace contains request/session data, context compression metrics, retrieval results and scores, LLM usage and cost, validation findings, latency, status, and the final answer. A configured Langfuse deployment can be added as a forwarding sink without making it a runtime dependency.

## Demo flow

1. Ask `What is the refund policy?` and open the trace viewer.
2. Click `Run unknown question` to see a flagged grounding failure.
3. Click `Run contradiction test` to see the 30-day versus 14-day conflict.
4. Click `Run 20-turn stress test` to see early context preserved by summary and relevant-message selection.

## Tests

```bash
pytest -q
```

The tests cover normal retrieval, unknown questions, contradictions, the context budget, and trace persistence.
