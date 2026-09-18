import os
import requests
import streamlit as st

st.set_page_config(page_title="GlassBox AI", page_icon="◈", layout="wide")
BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown("""<style>
:root { --ink:#17232b; --muted:#66757d; --teal:#0f766e; --cream:#f6f1e8; --line:#d9d4ca; }
.stApp { background:var(--cream); color:var(--ink); }
.block-container { max-width:1400px; padding-top:2rem; }
.hero { padding:1rem 0 1.5rem; border-bottom:1px solid var(--line); margin-bottom:1.5rem; }
.hero h1 { font-family:Georgia,serif; font-size:3.5rem; letter-spacing:0; margin:0; color:var(--ink); }
.hero p { color:var(--muted); font-size:1.05rem; margin:.35rem 0 0; }
.tracebox { background:#fffdf8; border:1px solid var(--line); padding:1rem; }
.badge { color:#fff; background:var(--teal); padding:.25rem .5rem; font-size:.75rem; font-weight:700; }
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>GLASSBOX</h1><p>AI that answers in public. Every context decision, retrieval, token, cost, and failure stays visible.</p></div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "last" not in st.session_state: st.session_state.last = None

chat, side = st.columns([1.65, 1], gap="large")
with chat:
    st.subheader("Chat")
    for item in st.session_state.messages:
        with st.chat_message(item["role"]): st.markdown(item["content"])
    prompt = st.chat_input("Ask about the company knowledge base")
    if prompt:
        try:
            response = requests.post(f"{BACKEND}/chat", json={"session_id":"demo-session", "message":prompt}, timeout=60)
            response.raise_for_status(); data = response.json(); st.session_state.last = data
            st.session_state.messages += [{"role":"user","content":prompt},{"role":"assistant","content":data["answer"]}]
            st.rerun()
        except Exception as exc: st.error(f"Backend unavailable: {exc}")

with side:
    st.subheader("Run status")
    if st.session_state.last:
        data = st.session_state.last; metrics = data["metrics"]; validation = data["validation"]
        st.markdown(f'<span class="badge">{"PASS" if validation["status"] == "PASS" else "FLAGGED"}</span>', unsafe_allow_html=True)
        st.caption(f"Run ID: {data['run_id']}")
        a,b = st.columns(2); a.metric("Latency", f"{metrics['latency_ms']} ms"); b.metric("Cost", f"${metrics['cost']:.7f}")
        a,b = st.columns(2); a.metric("Tokens", metrics["total_tokens"]); b.metric("LLM calls", metrics["llm_calls"])
        st.write("Sources", ", ".join(data["sources"]) or "None")
        st.write("Grounding", validation["status"])
        with st.expander("Trace viewer", expanded=True):
            trace = requests.get(f"{BACKEND}/trace/{data['run_id']}", timeout=10).json()
            for key in ["context_engineering", "retrieval", "llm_calls", "validation", "metrics"]:
                with st.expander(key.replace("_", " ").title()): st.json(trace.get(key))
            with st.expander("Final response"): st.write(trace["final_answer"])

st.divider()
st.subheader("Failure Lab")
fa, fb, fc = st.columns(3)
if fa.button("Run unknown question"):
    st.session_state.last = requests.post(f"{BACKEND}/chat", json={"session_id":"failure-lab", "message":"What will the company's revenue be in 2030?"}, timeout=60).json(); st.rerun()
if fb.button("Run contradiction test"):
    st.session_state.last = requests.post(f"{BACKEND}/chat", json={"session_id":"failure-lab", "message":"What is the refund period?"}, timeout=60).json(); st.rerun()
if fc.button("Run 20-turn stress test"):
    session = "stress-test"
    turns = ["Our project uses Python.", "We are building a RAG system.", "We need complete observability."] + [f"Unrelated planning note {i}: discuss scheduling." for i in range(4, 20)] + ["What programming language does the project use?"]
    result = None
    for turn in turns: result = requests.post(f"{BACKEND}/chat", json={"session_id":session, "message":turn}, timeout=60).json()
    st.session_state.last = result; st.rerun()
