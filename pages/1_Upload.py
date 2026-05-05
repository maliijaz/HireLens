import os
import streamlit as st
from groq import Groq
from src.parsers import parse_pdf, parse_job_description, parse_resume
from src.ml_scorer import compute_tfidf_scores
from src.llm_scorer import score_all_candidates
from src.bias_detector import audit_jd_language, check_score_fairness
from src.database import save_session

st.set_page_config(page_title="Upload — AI Hiring Assistant", page_icon="📤", layout="wide")
st.title("Upload Job Description & Resumes")

api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    st.error("GROQ_API_KEY not found. Create a `.env` file with your key (see `.env.example`).")
    st.stop()

client = Groq(api_key=api_key)

# ── Settings ──────────────────────────────────────────────────────────────────
with st.expander("⚙️ Settings", expanded=False):
    model_choice = st.selectbox(
        "Scoring model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        help="70B gives higher quality scores; 8B is faster with lower rate limits.",
    )
    session_name = st.text_input("Session name", value="My Hiring Session", max_chars=60)

st.divider()

# ── JD Upload ────────────────────────────────────────────────────────────────
st.subheader("1. Job Description")
jd_col1, jd_col2 = st.columns([1, 1])

with jd_col1:
    jd_file = st.file_uploader("Upload JD (PDF or TXT)", type=["pdf", "txt"], key="jd_file")

with jd_col2:
    jd_text_input = st.text_area(
        "Or paste the job description text here",
        height=200,
        placeholder="Paste the full job description...",
    )

# ── Resume Upload ─────────────────────────────────────────────────────────────
st.subheader("2. Candidate Resumes")
resume_files = st.file_uploader(
    "Upload resumes (PDF) — multiple files allowed",
    type=["pdf"],
    accept_multiple_files=True,
    key="resume_files",
)

if resume_files:
    st.caption(f"{len(resume_files)} resume(s) uploaded: {', '.join(f.name for f in resume_files)}")

st.divider()

# ── Analyze Button ────────────────────────────────────────────────────────────
analyze_clicked = st.button("Analyze Candidates", type="primary", use_container_width=True)

if analyze_clicked:
    jd_raw_text = ""
    if jd_file:
        file_bytes = jd_file.read()
        jd_raw_text = parse_pdf(file_bytes) if jd_file.name.endswith(".pdf") else file_bytes.decode("utf-8", errors="replace")
    elif jd_text_input.strip():
        jd_raw_text = jd_text_input.strip()
    else:
        st.error("Please upload a job description file or paste the text.")
        st.stop()

    if not resume_files:
        st.error("Please upload at least one resume.")
        st.stop()

    progress_container = st.container()
    with progress_container:
        st.info("Starting analysis... this may take a moment.")

        # Step 1: Parse JD
        with st.spinner("Parsing job description..."):
            jd = parse_job_description(jd_raw_text, client)
        st.success(f"Job Description parsed: **{jd.title}**")

        # Step 2: Parse resumes
        resumes = []
        resume_progress = st.progress(0, text="Parsing resumes...")
        for i, rf in enumerate(resume_files):
            resume = parse_resume(rf.read(), rf.name, client)
            resumes.append(resume)
            resume_progress.progress((i + 1) / len(resume_files), text=f"Parsed {resume.candidate_name}")
        resume_progress.empty()
        st.success(f"{len(resumes)} resume(s) parsed.")

        # Step 3: TF-IDF baseline
        with st.spinner("Computing TF-IDF similarity scores..."):
            tfidf_scores = compute_tfidf_scores(jd.raw_text, [r.raw_text for r in resumes])
        st.success("TF-IDF scores computed.")

        # Step 4: LLM scoring
        score_progress = st.progress(0, text="Scoring candidates with AI...")

        def on_progress(done, total, name):
            score_progress.progress(done / total, text=f"Scored {name} ({done}/{total})")

        scores = score_all_candidates(jd, resumes, tfidf_scores, client, model=model_choice, progress_callback=on_progress)
        score_progress.empty()
        st.success(f"All {len(scores)} candidates scored and ranked.")

        # Step 5: Bias audit
        with st.spinner("Running bias audit..."):
            jd_audit = audit_jd_language(jd, client)
            fairness = check_score_fairness(scores)
        st.success("Bias audit complete.")

        # Step 6: Persist
        st.session_state.jd = jd
        st.session_state.scores = scores
        st.session_state.jd_audit = jd_audit
        st.session_state.fairness = fairness

        saved_id = save_session(session_name, jd, scores, jd_audit, fairness)
        st.success(f"Session saved (ID: `{saved_id}`). Navigate to **Results** or **Bias Audit** in the sidebar.")

        if jd_audit.flags:
            st.warning(
                f"Bias audit flagged **{len(jd_audit.flags)} term(s)** in the job description. "
                "See the Bias Audit page for details."
            )
