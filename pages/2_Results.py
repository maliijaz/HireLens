import io
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Results — HireLens", page_icon="📊", layout="wide")
st.title("Candidate Rankings")

if not st.session_state.get("scores"):
    st.warning("No analysis results yet. Go to **Upload** to analyze candidates.")
    st.stop()

jd = st.session_state.jd
scores = st.session_state.scores

st.caption(f"Role: **{jd.title}** | {len(scores)} candidates ranked")
st.divider()

# ── Summary metrics ───────────────────────────────────────────────────────────
top = scores[0]
avg_score = sum(s.weighted_final_score for s in scores) / len(scores)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Candidates Analyzed", len(scores))
m2.metric("Top Candidate", top.resume.candidate_name)
m3.metric("Top Score", f"{top.weighted_final_score:.1f} / 100")
m4.metric("Average Score", f"{avg_score:.1f} / 100")

st.divider()

# ── Score breakdown bar chart ─────────────────────────────────────────────────
st.subheader("Score Breakdown by Candidate")

names = [s.resume.candidate_name for s in scores]
fig = go.Figure()
fig.add_trace(go.Bar(name="Skills (LLM)", x=names, y=[s.skills_score * 10 for s in scores], marker_color="#4C78A8"))
fig.add_trace(go.Bar(name="Experience (LLM)", x=names, y=[s.experience_score * 10 for s in scores], marker_color="#54A24B"))
fig.add_trace(go.Bar(name="Education (LLM)", x=names, y=[s.education_score * 10 for s in scores], marker_color="#F58518"))
fig.add_trace(go.Bar(name="TF-IDF Keyword Match", x=names, y=[s.tfidf_score * 100 for s in scores], marker_color="#B279A2"))
fig.update_layout(
    barmode="group",
    yaxis_title="Score (0–100 scale)",
    xaxis_title="Candidate",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=400,
)
st.plotly_chart(fig, width="stretch")

# ── Final score ranking chart ─────────────────────────────────────────────────
st.subheader("Overall Ranking")
rank_fig = px.bar(
    x=[s.weighted_final_score for s in scores],
    y=names,
    orientation="h",
    color=[s.weighted_final_score for s in scores],
    color_continuous_scale=["#d73027", "#fee08b", "#1a9850"],
    labels={"x": "Weighted Final Score (0–100)", "y": "Candidate"},
    range_color=[0, 100],
)
rank_fig.update_layout(height=max(300, len(scores) * 50), coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
st.plotly_chart(rank_fig, width="stretch")

st.divider()

# ── Candidate detail expanders ────────────────────────────────────────────────
st.subheader("Candidate Details")

for rank, cs in enumerate(scores, start=1):
    score_color = "🟢" if cs.weighted_final_score >= 70 else "🟡" if cs.weighted_final_score >= 45 else "🔴"
    with st.expander(f"{score_color} #{rank} — {cs.resume.candidate_name}  |  Score: {cs.weighted_final_score:.1f} / 100"):
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("**Dimension Scores**")
            d1, d2, d3 = st.columns(3)
            d1.metric("Skills", f"{cs.skills_score:.1f}/10")
            d2.metric("Experience", f"{cs.experience_score:.1f}/10")
            d3.metric("Education", f"{cs.education_score:.1f}/10")

            st.markdown(f"**TF-IDF Keyword Score:** {cs.tfidf_score:.3f}")
            st.markdown(f"**LLM Overall Score:** {cs.overall_llm_score:.1f}/10")

            st.markdown("**Strengths**")
            for s in cs.strengths:
                st.markdown(f"- {s}")

            st.markdown("**Gaps**")
            for g in cs.gaps:
                st.markdown(f"- {g}")

        with col_right:
            st.markdown("**AI Reasoning**")
            st.info(cs.reasoning)

            st.markdown("**Extracted Skills**")
            if cs.resume.skills:
                st.markdown(", ".join(cs.resume.skills))
            else:
                st.caption("None extracted")

            st.markdown("**Work History**")
            for wh in cs.resume.work_history:
                st.markdown(f"- {wh}")

st.divider()

# ── Export ────────────────────────────────────────────────────────────────────
st.subheader("Export Results")

rows = []
for rank, cs in enumerate(scores, start=1):
    rows.append({
        "Rank": rank,
        "Candidate": cs.resume.candidate_name,
        "Final Score (0-100)": cs.weighted_final_score,
        "Skills Score (0-10)": cs.skills_score,
        "Experience Score (0-10)": cs.experience_score,
        "Education Score (0-10)": cs.education_score,
        "LLM Overall (0-10)": cs.overall_llm_score,
        "TF-IDF Score (0-1)": round(cs.tfidf_score, 4),
        "Strengths": "; ".join(cs.strengths),
        "Gaps": "; ".join(cs.gaps),
        "Reasoning": cs.reasoning,
    })

df = pd.DataFrame(rows)

col_csv, col_excel = st.columns(2)

with col_csv:
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv_bytes, file_name=f"{jd.title}_rankings.csv", mime="text/csv", width="stretch")

with col_excel:
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Rankings")
    excel_bytes = excel_buf.getvalue()
    st.download_button("Download Excel", excel_bytes, file_name=f"{jd.title}_rankings.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
