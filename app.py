import streamlit as st
from dotenv import load_dotenv
from src.database import init_db, list_sessions, load_session, delete_session

load_dotenv()
init_db()

st.set_page_config(
    page_title="AI Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "jd" not in st.session_state:
    st.session_state.jd = None
if "scores" not in st.session_state:
    st.session_state.scores = []
if "jd_audit" not in st.session_state:
    st.session_state.jd_audit = None
if "fairness" not in st.session_state:
    st.session_state.fairness = None

# ── Sidebar: session history ──────────────────────────────────────────────────
with st.sidebar:
    st.title("AI Hiring Assistant")
    st.caption("Powered by Groq (GPT-OSS) + sklearn")
    st.divider()

    st.subheader("Saved Sessions")
    sessions = list_sessions()

    if sessions:
        for s in sessions:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"📂 {s['session_name']}", key=f"load_{s['session_id']}", use_container_width=True):
                    session = load_session(s["session_id"])
                    if session:
                        st.session_state.jd = session.jd
                        st.session_state.scores = session.scores
                        st.session_state.jd_audit = session.jd_audit
                        st.session_state.fairness = session.fairness
                        st.success(f"Loaded: {s['session_name']}")
                        st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{s['session_id']}"):
                    delete_session(s["session_id"])
                    st.rerun()
    else:
        st.caption("No saved sessions yet. Upload a JD and resumes to get started.")

# ── Home page ─────────────────────────────────────────────────────────────────
st.title("AI Hiring Assistant")
st.markdown(
    """
    An end-to-end AI-powered tool that helps hiring teams make faster, fairer shortlisting decisions.

    ### How it works
    1. **Upload** — Provide a job description and candidate resumes (PDF)
    2. **Analyze** — AI extracts skills, scores candidates on multiple dimensions, and ranks them
    3. **Review** — Explore ranked results, reasoning, and a bias audit report
    4. **Export** — Download the ranked shortlist as CSV or Excel

    ### What makes this different
    - **Hybrid scoring**: TF-IDF keyword matching (sklearn) + Groq GPT-OSS semantic scoring
    - **Explainable results**: Every score comes with per-dimension breakdown and reasoning
    - **Bias audit**: Flags exclusionary JD language and checks score fairness across name-associated demographics
    - **Fast inference**: Groq's LPU-based API returns LLM scores in a fraction of the time of typical LLM providers

    ---
    Use the **sidebar** to navigate to Upload or load a previous session.
    """
)

if st.session_state.scores:
    st.success(
        f"Active session: **{st.session_state.jd.title if st.session_state.jd else 'Unknown role'}** — "
        f"{len(st.session_state.scores)} candidates scored. Navigate to Results or Bias Audit."
    )
