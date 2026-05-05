from __future__ import annotations
import json
import io
import pdfplumber
from groq import Groq
from .models import JobDescription, Resume

_JD_SYSTEM = """You are a structured data extraction assistant. Extract information from job descriptions and return ONLY valid JSON with no markdown or explanation.

Return this exact JSON shape:
{
  "title": "string",
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "experience_years": null_or_integer,
  "education_requirement": null_or_string,
  "responsibilities": ["string"]
}"""

_RESUME_SYSTEM = """You are a structured data extraction assistant. Extract information from resumes and return ONLY valid JSON with no markdown or explanation.

Return this exact JSON shape:
{
  "candidate_name": "string",
  "skills": ["string"],
  "experience_years": null_or_float,
  "education": null_or_string,
  "work_history": ["string describing each role, e.g. 'Software Engineer at Acme Corp (2019-2022)'"]
}"""


def parse_pdf(file_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages).strip()


def parse_job_description(text: str, client: Groq) -> JobDescription:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=1024,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _JD_SYSTEM},
            {"role": "user", "content": f"Extract structured data from this job description:\n\n{text}"},
        ],
    )
    data = json.loads(response.choices[0].message.content)
    return JobDescription(raw_text=text, **data)


def parse_resume(file_bytes: bytes, filename: str, client: Groq) -> Resume:
    text = parse_pdf(file_bytes)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=1024,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _RESUME_SYSTEM},
            {"role": "user", "content": f"Extract structured data from this resume:\n\n{text}"},
        ],
    )
    data = json.loads(response.choices[0].message.content)
    return Resume(filename=filename, raw_text=text, **data)
