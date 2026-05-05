from __future__ import annotations
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .models import AnalysisSession, JobDescription, CandidateScore, JDLanguageAudit, ScoreFairnessResult

DB_PATH = Path(__file__).parent.parent / "sessions.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                session_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                jd_json TEXT NOT NULL,
                scores_json TEXT NOT NULL,
                jd_audit_json TEXT,
                fairness_json TEXT
            )
        """)
        conn.commit()


def save_session(
    session_name: str,
    jd: JobDescription,
    scores: list[CandidateScore],
    jd_audit: JDLanguageAudit | None = None,
    fairness: ScoreFairnessResult | None = None,
) -> str:
    session_id = str(uuid.uuid4())[:8]
    created_at = datetime.now(timezone.utc).isoformat()

    with _get_conn() as conn:
        conn.execute(
            """INSERT INTO sessions
               (session_id, session_name, created_at, jd_json, scores_json, jd_audit_json, fairness_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                session_name,
                created_at,
                jd.model_dump_json(),
                json.dumps([s.model_dump() for s in scores]),
                jd_audit.model_dump_json() if jd_audit else None,
                fairness.model_dump_json() if fairness else None,
            ),
        )
        conn.commit()
    return session_id


def load_session(session_id: str) -> AnalysisSession | None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()

    if not row:
        return None

    return AnalysisSession(
        session_id=row["session_id"],
        session_name=row["session_name"],
        created_at=row["created_at"],
        jd=JobDescription.model_validate_json(row["jd_json"]),
        scores=[CandidateScore.model_validate(s) for s in json.loads(row["scores_json"])],
        jd_audit=JDLanguageAudit.model_validate_json(row["jd_audit_json"]) if row["jd_audit_json"] else None,
        fairness=ScoreFairnessResult.model_validate_json(row["fairness_json"]) if row["fairness_json"] else None,
    )


def list_sessions() -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT session_id, session_name, created_at FROM sessions ORDER BY created_at DESC"
        ).fetchall()
    return [{"session_id": r["session_id"], "session_name": r["session_name"], "created_at": r["created_at"]} for r in rows]


def delete_session(session_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
