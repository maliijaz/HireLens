# HireLens

An end-to-end AI-powered tool that helps hiring teams make faster, fairer shortlisting decisions. Built with Python, Streamlit, and the Groq API (free tier).

This project is open source under the [MIT License](LICENSE) — contributions are welcome.

## Features

- **Hybrid ML + LLM scoring** — TF-IDF keyword matching (scikit-learn) combined with GPT-OSS semantic scoring (via Groq) for robust, explainable rankings
- **Structured extraction** — LLM parses job descriptions and resumes into structured data automatically
- **Multi-dimension scoring** — Skills, Experience, Education scored separately with full reasoning
- **Bias audit** — Flags exclusionary/gendered language in job descriptions and checks score fairness across name-associated demographic groups
- **Session persistence** — SQLite stores analyses; reload and compare past sessions
- **Export** — Download ranked shortlists as CSV or Excel

## Scoring Formula

```text
weighted_final_score = normalize(0.3 × tfidf_score + 0.7 × llm_overall_score)
```

TF-IDF catches keyword matching; the LLM catches semantic fit and experience depth. Neither alone is sufficient.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API key

```bash
cp .env.example .env
# Edit .env and add your Groq API key (free tier: https://console.groq.com/keys)
```

### 3. Run

```bash
streamlit run app.py
```

## Project Structure

```text
├── app.py                   # Streamlit entry point + session sidebar
├── pages/
│   ├── 1_Upload.py          # JD + resume upload, full analysis pipeline
│   ├── 2_Results.py         # Ranked candidates dashboard + export
│   └── 3_Bias_Audit.py      # JD language audit + score fairness check
├── src/
│   ├── models.py            # Pydantic data models
│   ├── parsers.py           # PDF parsing + Groq (GPT-OSS) structured extraction
│   ├── ml_scorer.py         # TF-IDF cosine similarity baseline
│   ├── llm_scorer.py        # Groq (GPT-OSS) API scoring
│   ├── bias_detector.py     # Bias wordlist + statistical fairness test
│   └── database.py          # SQLite session CRUD
├── requirements.txt
└── .env.example
```

## Technical Highlights

### Fast, Free-Tier Inference

Scoring calls run against Groq's LPU-based API using OpenAI's open-weight GPT-OSS models (`openai/gpt-oss-120b` for scoring quality, `openai/gpt-oss-20b` for fast structured extraction), which keeps a full batch analysis fast and free-tier friendly.

### Bias Detection

- **JD Language Audit:** Checks for masculine-coded words (Gaucher et al., 2011) and exclusionary phrasing, then uses GPT-OSS (via Groq) for nuanced tone assessment
- **Score Fairness:** Uses Welch's t-test to detect statistically significant score disparity between name-associated demographic groups (Bertrand & Mullainathan, 2004)

### Hybrid Scoring Rationale

| Method     | Strength                             | Weakness                             |
| ---------- | ------------------------------------- | ------------------------------------- |
| TF-IDF     | Fast, reproducible, keyword coverage  | Misses semantic meaning               |
| LLM        | Semantic depth, reasoning, context    | Expensive at scale, can hallucinate   |
| **Hybrid** | Best of both                          | —                                      |

## Usage

1. Navigate to **Upload** in the sidebar
2. Upload a job description (PDF or paste text)
3. Upload candidate resumes (multiple PDFs)
4. Click **Analyze Candidates**
5. View ranked results in **Results**
6. Review the bias report in **Bias Audit**
7. Export the shortlist as CSV or Excel

## Disclaimer

This tool is designed to assist human reviewers, not replace them. Hiring decisions must comply with applicable employment law. The bias audit highlights patterns for review — it is not a legal compliance tool.

## Contributing

Issues and pull requests are welcome. For anything non-trivial, please open an issue first to discuss the change. See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup and guidelines.

## License

MIT — see [LICENSE](LICENSE) for details.
