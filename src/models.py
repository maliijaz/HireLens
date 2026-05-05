from __future__ import annotations
from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    raw_text: str
    title: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_years: int | None = None
    education_requirement: str | None = None
    responsibilities: list[str] = Field(default_factory=list)


class Resume(BaseModel):
    filename: str
    raw_text: str
    candidate_name: str
    skills: list[str] = Field(default_factory=list)
    experience_years: float | None = None
    education: str | None = None
    work_history: list[str] = Field(default_factory=list)


class CandidateScore(BaseModel):
    resume: Resume
    tfidf_score: float = Field(ge=0.0, le=1.0)
    skills_score: float = Field(ge=0.0, le=10.0)
    experience_score: float = Field(ge=0.0, le=10.0)
    education_score: float = Field(ge=0.0, le=10.0)
    overall_llm_score: float = Field(ge=0.0, le=10.0)
    weighted_final_score: float = Field(ge=0.0, le=100.0)
    reasoning: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class BiasFlag(BaseModel):
    phrase: str
    category: str
    suggestion: str


class JDLanguageAudit(BaseModel):
    flags: list[BiasFlag] = Field(default_factory=list)
    llm_feedback: str = ""
    overall_tone: str = ""


class ScoreFairnessResult(BaseModel):
    groups_detected: dict[str, list[str]] = Field(default_factory=dict)
    group_avg_scores: dict[str, float] = Field(default_factory=dict)
    significant_disparity: bool = False
    p_value: float | None = None
    warning_message: str = ""


class AnalysisSession(BaseModel):
    session_id: str
    session_name: str
    created_at: str
    jd: JobDescription
    scores: list[CandidateScore]
    jd_audit: JDLanguageAudit | None = None
    fairness: ScoreFairnessResult | None = None
