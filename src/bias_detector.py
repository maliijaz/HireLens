from __future__ import annotations
import json
import re
from groq import Groq
from scipy import stats
from .models import (
    JobDescription,
    CandidateScore,
    BiasFlag,
    JDLanguageAudit,
    ScoreFairnessResult,
)

# Masculine-coded words per Gaucher et al. (2011) and subsequent research
_MASCULINE_CODED = {
    "rockstar": "top performer",
    "ninja": "skilled practitioner",
    "aggressive": "driven",
    "dominant": "leading",
    "dominate": "excel",
    "competitive": "motivated",
    "fearless": "confident",
    "outspoken": "communicative",
    "headstrong": "determined",
    "independent": "self-directed",
    "analytic": "analytical",
    "ambitious": "goal-oriented",
    "superior": "excellent",
    "hero": "expert",
    "guru": "expert",
    "wizard": "expert",
}

_EXCLUSIONARY = {
    "culture fit": "culture add",
    "must be local": "must be able to commute to",
    "native english": "strong english communication",
    "strong communication skills in english": "strong english communication skills",
}

# First names skewed toward demographic groups (simplified reference subset)
# Source inspired by Bertrand & Mullainathan (2004) audit study
_STEREOTYPICALLY_WHITE = {
    "emily", "anne", "brendan", "greg", "jack", "neil", "todd",
    "allison", "kristen", "meredith", "carrie", "brad", "jay", "matthew",
}
_STEREOTYPICALLY_BLACK = {
    "lakisha", "jamal", "darnell", "tamika", "latoya", "tyrone",
    "kenya", "latonya", "ebony", "shanice", "marquis", "leroy",
}


def audit_jd_language(jd: JobDescription, client: Groq) -> JDLanguageAudit:
    flags: list[BiasFlag] = []
    text_lower = jd.raw_text.lower()

    for term, suggestion in {**_MASCULINE_CODED, **_EXCLUSIONARY}.items():
        if re.search(r"\b" + re.escape(term) + r"\b", text_lower):
            category = "masculine-coded" if term in _MASCULINE_CODED else "exclusionary"
            flags.append(BiasFlag(phrase=term, category=category, suggestion=suggestion))

    llm_prompt = f"""Analyze this job description for potentially biased, exclusionary, or unnecessarily restrictive language.
Focus on: gendered language, ageist language, ableist language, unnecessarily restrictive requirements.

Respond with JSON only:
{{
  "overall_tone": "inclusive|somewhat_inclusive|neutral|somewhat_exclusionary|exclusionary",
  "feedback": "2-3 sentence constructive feedback on the language used"
}}

Job description:
{jd.raw_text[:3000]}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        max_tokens=512,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": llm_prompt}],
    )
    llm_data = json.loads(response.choices[0].message.content)

    return JDLanguageAudit(
        flags=flags,
        llm_feedback=llm_data.get("feedback", ""),
        overall_tone=llm_data.get("overall_tone", "neutral"),
    )


def check_score_fairness(scores: list[CandidateScore]) -> ScoreFairnessResult:
    if len(scores) < 4:
        return ScoreFairnessResult(
            warning_message="Not enough candidates to run a fairness analysis (minimum 4 required)."
        )

    groups: dict[str, list[str]] = {"group_a": [], "group_b": [], "unknown": []}
    group_scores: dict[str, list[float]] = {"group_a": [], "group_b": [], "unknown": []}

    for cs in scores:
        first_name = cs.resume.candidate_name.strip().split()[0].lower() if cs.resume.candidate_name else ""
        if first_name in _STEREOTYPICALLY_WHITE:
            groups["group_a"].append(cs.resume.candidate_name)
            group_scores["group_a"].append(cs.weighted_final_score)
        elif first_name in _STEREOTYPICALLY_BLACK:
            groups["group_b"].append(cs.resume.candidate_name)
            group_scores["group_b"].append(cs.weighted_final_score)
        else:
            groups["unknown"].append(cs.resume.candidate_name)
            group_scores["unknown"].append(cs.weighted_final_score)

    avg_scores = {
        g: round(sum(s) / len(s), 2) if s else 0.0
        for g, s in group_scores.items()
    }

    a_scores = group_scores["group_a"]
    b_scores = group_scores["group_b"]

    significant = False
    p_value = None
    warning = ""

    if len(a_scores) >= 2 and len(b_scores) >= 2:
        _, p_value = stats.ttest_ind(a_scores, b_scores, equal_var=False)
        p_value = round(float(p_value), 4)
        if p_value < 0.05:
            significant = True
            warning = (
                "Statistically significant score disparity detected between name-associated demographic groups "
                f"(p={p_value}). This warrants human review to ensure the scoring criteria are not inadvertently "
                "correlated with candidate names or demographics."
            )
    else:
        warning = (
            "Too few candidates in detectable name groups for statistical testing. "
            "This analysis works best with 10+ diverse candidates."
        )

    return ScoreFairnessResult(
        groups_detected={g: v for g, v in groups.items() if v},
        group_avg_scores={g: v for g, v in avg_scores.items() if groups[g]},
        significant_disparity=significant,
        p_value=p_value,
        warning_message=warning,
    )
