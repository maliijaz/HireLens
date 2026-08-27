import re
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Bias Audit — HireLens", page_icon="⚖️", layout="wide")
st.title("Bias Audit Report")

st.info(
    "**Disclaimer:** This tool highlights patterns for human review. "
    "Hiring decisions must comply with applicable employment law. "
    "AI-assisted analysis is a supplement to — not a replacement for — human judgment."
)

if not st.session_state.get("scores"):
    st.warning("No analysis results yet. Go to **Upload** to analyze candidates.")
    st.stop()

jd = st.session_state.jd
jd_audit = st.session_state.get("jd_audit")
fairness = st.session_state.get("fairness")
scores = st.session_state.scores

# ── Section 1: JD Language Audit ──────────────────────────────────────────────
st.subheader("1. Job Description Language Audit")

if jd_audit is None:
    st.warning("No JD audit data available for this session.")
else:
    tone_colors = {
        "inclusive": "🟢",
        "somewhat_inclusive": "🟡",
        "neutral": "⚪",
        "somewhat_exclusionary": "🟠",
        "exclusionary": "🔴",
    }
    tone_icon = tone_colors.get(jd_audit.overall_tone, "⚪")
    st.markdown(f"**Overall Tone:** {tone_icon} `{jd_audit.overall_tone.replace('_', ' ').title()}`")

    if jd_audit.llm_feedback:
        st.markdown(f"**AI Feedback:** {jd_audit.llm_feedback}")

    if jd_audit.flags:
        st.markdown(f"**{len(jd_audit.flags)} flagged term(s) detected:**")
        flag_rows = [
            {"Term": f.phrase, "Category": f.category, "Suggested Alternative": f.suggestion}
            for f in jd_audit.flags
        ]
        st.table(flag_rows)

        st.markdown("**Highlighted Job Description (flagged terms bolded):**")
        highlighted = jd.raw_text
        for f in jd_audit.flags:
            highlighted = re.sub(
                r"\b(" + re.escape(f.phrase) + r")\b",
                r"**\1**",
                highlighted,
                flags=re.IGNORECASE,
            )
        st.markdown(highlighted[:3000] + ("..." if len(highlighted) > 3000 else ""))
    else:
        st.success("No flagged terms detected in the job description language.")

st.divider()

# ── Section 2: Score Fairness Check ──────────────────────────────────────────
st.subheader("2. Score Fairness Analysis")

if fairness is None:
    st.warning("No fairness data available for this session.")
else:
    if fairness.significant_disparity:
        st.error(f"Significant disparity detected: {fairness.warning_message}")
    elif fairness.warning_message:
        st.warning(fairness.warning_message)
    else:
        st.success("No statistically significant score disparity detected across name-associated demographic groups.")

    if fairness.p_value is not None:
        st.markdown(f"**Statistical test p-value:** `{fairness.p_value}`  *(p < 0.05 indicates potential disparity)*")

    if fairness.group_avg_scores:
        st.markdown("**Average scores by detected name group:**")

        group_labels = {
            "group_a": "Group A (names skewing majority)",
            "group_b": "Group B (names skewing minority)",
            "unknown": "Unclassified",
        }
        chart_data = [
            {"Group": group_labels.get(g, g), "Average Score": v}
            for g, v in fairness.group_avg_scores.items()
            if v > 0
        ]

        if chart_data:
            bar_fig = px.bar(
                chart_data,
                x="Group",
                y="Average Score",
                color="Average Score",
                color_continuous_scale=["#d73027", "#fee08b", "#1a9850"],
                range_color=[0, 100],
                range_y=[0, 100],
                title="Average Candidate Score by Name Group",
            )
            bar_fig.update_layout(coloraxis_showscale=False, height=350)
            st.plotly_chart(bar_fig, width="stretch")

        if fairness.groups_detected:
            with st.expander("See candidate name classifications"):
                for g, names in fairness.groups_detected.items():
                    if names:
                        st.markdown(f"**{group_labels.get(g, g)}:** {', '.join(names)}")

    st.caption(
        "Name-group inference uses a reference first-name dataset (Bertrand & Mullainathan, 2004). "
        "This is an imperfect heuristic — many names cross demographic boundaries. "
        "Treat this as a prompt for review, not a definitive finding."
    )

st.divider()

# ── Section 3: All scores at a glance ────────────────────────────────────────
st.subheader("3. All Candidate Scores")
for rank, cs in enumerate(scores, start=1):
    cols = st.columns([3, 1, 1, 1, 2])
    cols[0].markdown(f"**#{rank} {cs.resume.candidate_name}**")
    cols[1].markdown(f"Skills: `{cs.skills_score:.1f}`")
    cols[2].markdown(f"Exp: `{cs.experience_score:.1f}`")
    cols[3].markdown(f"Edu: `{cs.education_score:.1f}`")
    cols[4].markdown(f"Final: **`{cs.weighted_final_score:.1f}/100`**")
