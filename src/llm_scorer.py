from __future__ import annotations
import json
from groq import Groq
from .models import JobDescription, Resume, CandidateScore

_SCORING_RUBRIC = """
## Scoring Rubric (each dimension 0–10)

- **skills_score**: How well the candidate's skills match the required and preferred skills in the JD.
  - 9-10: Covers nearly all required skills and several preferred ones
  - 7-8: Covers most required skills with minor gaps
  - 4-6: Covers roughly half the required skills
  - 0-3: Few or no required skills present

- **experience_score**: How well the candidate's experience level and domain matches the JD expectations.
  - 9-10: Meets or exceeds years required, directly relevant domain
  - 7-8: Slightly under required years but strong domain match
  - 4-6: Moderate mismatch in years or domain
  - 0-3: Significant mismatch

- **education_score**: How well education meets stated requirements.
  - 9-10: Meets or exceeds requirements
  - 5-8: Partially meets or closely related
  - 0-4: Does not meet requirements (if no requirement stated, score 7)

- **overall_score**: Holistic assessment of the candidate's fit, considering all factors plus intangible signals like career trajectory and role relevance.

Return ONLY valid JSON (no markdown) in this exact shape:
{
  "skills_score": float,
  "experience_score": float,
  "education_score": float,
  "overall_score": float,
  "reasoning": "2-3 sentence overall assessment",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "gaps": ["gap 1", "gap 2"]
}"""


def _build_system_prompt(jd: JobDescription) -> str:
    skills_req = ", ".join(jd.required_skills) if jd.required_skills else "Not specified"
    skills_pref = ", ".join(jd.preferred_skills) if jd.preferred_skills else "Not specified"
    responsibilities = "\n".join(f"- {r}" for r in jd.responsibilities) if jd.responsibilities else "Not specified"

    return f"""You are an expert technical recruiter scoring candidates against a job description.

## Job Description
**Title:** {jd.title}
**Required Skills:** {skills_req}
**Preferred Skills:** {skills_pref}
**Experience Required:** {jd.experience_years} years
**Education Required:** {jd.education_requirement or 'Not specified'}

**Responsibilities:**
{responsibilities}

{_SCORING_RUBRIC}"""


def score_candidate(
    jd: JobDescription,
    resume: Resume,
    tfidf_score: float,
    client: Groq,
    model: str = "llama-3.3-70b-versatile",
) -> CandidateScore:
    system_prompt = _build_system_prompt(jd)

    candidate_text = f"""## Candidate Resume

**Name:** {resume.candidate_name}
**Skills:** {', '.join(resume.skills) if resume.skills else 'Not listed'}
**Years of Experience:** {resume.experience_years if resume.experience_years is not None else 'Unknown'}
**Education:** {resume.education or 'Not listed'}

**Work History:**
{chr(10).join(f'- {w}' for w in resume.work_history) if resume.work_history else 'Not listed'}

**Full Resume Text:**
{resume.raw_text[:3000]}"""

    response = client.chat.completions.create(
        model=model,
        max_tokens=1024,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Score this candidate:\n\n{candidate_text}"},
        ],
    )

    data = json.loads(response.choices[0].message.content)

    llm_overall = float(data["overall_score"])
    raw_weighted = 0.3 * tfidf_score + 0.7 * (llm_overall / 10.0)
    weighted_final = round(raw_weighted * 100, 1)

    return CandidateScore(
        resume=resume,
        tfidf_score=tfidf_score,
        skills_score=float(data["skills_score"]),
        experience_score=float(data["experience_score"]),
        education_score=float(data["education_score"]),
        overall_llm_score=llm_overall,
        weighted_final_score=weighted_final,
        reasoning=data["reasoning"],
        strengths=data.get("strengths", []),
        gaps=data.get("gaps", []),
    )


def score_all_candidates(
    jd: JobDescription,
    resumes: list[Resume],
    tfidf_scores: list[float],
    client: Groq,
    model: str = "llama-3.3-70b-versatile",
    progress_callback=None,
) -> list[CandidateScore]:
    results = []
    for i, (resume, tfidf) in enumerate(zip(resumes, tfidf_scores)):
        score = score_candidate(jd, resume, tfidf, client, model)
        results.append(score)
        if progress_callback:
            progress_callback(i + 1, len(resumes), resume.candidate_name)

    results.sort(key=lambda s: s.weighted_final_score, reverse=True)
    return results
