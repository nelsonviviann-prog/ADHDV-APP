"""
Local SQLite layer. Stores anonymised child profiles, parent + teacher
screening sessions, and cross-informant matches. No PII beyond an
optional rater contact (parent phone or teacher school) which the caller
can omit.

Schema
------
children
    id INTEGER PK
    study_id TEXT UNIQUE      -- short opaque ID printed for the rater
    first_name_initial TEXT   -- e.g., 'A' (no full name stored)
    last_name_initial TEXT    -- e.g., 'B'
    age INTEGER
    gender TEXT
    school_level TEXT
    state TEXT
    created_at TEXT

screening_sessions
    id INTEGER PK
    child_id INTEGER FK -> children.id
    rater_type TEXT           -- 'Parent' | 'Teacher'
    rater_contact TEXT        -- optional (phone, school name)
    completed_at TEXT
    responses_json TEXT       -- full item_id -> int dict
    inatt_endorsed INTEGER
    hi_endorsed INTEGER
    impairment_count INTEGER
    presentation TEXT
    risk_level TEXT
    flags_json TEXT
    ml_prediction TEXT        -- ML model's predicted class (may differ from rule-based)

feedback
    id INTEGER PK
    submitted_at TEXT
    role TEXT                 -- who is speaking; free-form, not an auth claim
    rating INTEGER            -- 1..5
    category TEXT
    message TEXT
    contact TEXT              -- optional; the only PII here, and only if volunteered
"""

from __future__ import annotations

import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from . import config as cfg


SCHEMA = """
CREATE TABLE IF NOT EXISTS children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    study_id TEXT NOT NULL UNIQUE,
    first_name_initial TEXT,
    last_name_initial TEXT,
    age INTEGER,
    gender TEXT,
    school_level TEXT,
    state TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS screening_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    rater_type TEXT NOT NULL,
    rater_contact TEXT,
    completed_at TEXT NOT NULL,
    responses_json TEXT NOT NULL,
    inatt_endorsed INTEGER,
    hi_endorsed INTEGER,
    impairment_count INTEGER,
    presentation TEXT,
    risk_level TEXT,
    flags_json TEXT,
    ml_prediction TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_child ON screening_sessions(child_id);
CREATE INDEX IF NOT EXISTS idx_sessions_completed ON screening_sessions(completed_at);

CREATE TABLE IF NOT EXISTS clinician_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clinician_name TEXT NOT NULL,
    action TEXT NOT NULL,          -- 'sign_in' | 'view_study' | 'download_pdf' | 'view_dashboard'
    target_study_id TEXT,          -- nullable; the Study ID acted on (if applicable)
    occurred_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_activity_when ON clinician_activity(occurred_at);
CREATE INDEX IF NOT EXISTS idx_activity_who ON clinician_activity(clinician_name);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submitted_at TEXT NOT NULL,
    role TEXT,                     -- 'Parent' | 'Teacher' | 'Clinician' | 'Other'
    rating INTEGER,                -- 1..5
    category TEXT,                 -- e.g. 'Ease of use' | 'Bug / error'
    message TEXT NOT NULL,
    contact TEXT                   -- optional; only if the user wants a reply
);
CREATE INDEX IF NOT EXISTS idx_feedback_when ON feedback(submitted_at);

CREATE TABLE IF NOT EXISTS consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL UNIQUE,   -- Paystack ref; ALSO the requester's access token
    study_id TEXT,                    -- optional link to a screened child
    requester_role TEXT,              -- 'Parent' | 'Teacher'
    requester_email TEXT NOT NULL,    -- required by Paystack; used to send the receipt
    amount_kobo INTEGER NOT NULL,
    status TEXT NOT NULL,             -- 'pending' | 'paid' | 'closed'
    consultant_name TEXT,             -- clinician who picked it up
    created_at TEXT NOT NULL,
    paid_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_consult_status ON consultations(status);
CREATE INDEX IF NOT EXISTS idx_consult_ref ON consultations(reference);

CREATE TABLE IF NOT EXISTS consultation_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id INTEGER NOT NULL
        REFERENCES consultations(id) ON DELETE CASCADE,
    sender_role TEXT NOT NULL,        -- 'Parent' | 'Teacher' | 'Clinician'
    sender_name TEXT,
    body TEXT NOT NULL,
    sent_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_msg_consult ON consultation_messages(consultation_id, id);
"""


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def _new_study_id() -> str:
    return "ADHD-NG-" + secrets.token_hex(3).upper()


@contextmanager
def connect():
    cfg.DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(cfg.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


# ---------------------------------------------------------------------------
# Children
# ---------------------------------------------------------------------------

def upsert_child(
    *,
    study_id: str | None,
    first_name_initial: str,
    last_name_initial: str,
    age: int,
    gender: str,
    school_level: str,
    state: str,
) -> dict:
    """Insert a new child or update an existing one (by study_id)."""
    init_db()
    sid = (study_id or "").strip().upper() or _new_study_id()
    with connect() as conn:
        existing = conn.execute(
            "SELECT * FROM children WHERE study_id = ?", (sid,)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE children SET age=?, gender=?, school_level=?, state=?, "
                "first_name_initial=?, last_name_initial=? WHERE study_id=?",
                (age, gender, school_level, state, first_name_initial, last_name_initial, sid),
            )
            row = conn.execute("SELECT * FROM children WHERE study_id=?", (sid,)).fetchone()
        else:
            conn.execute(
                "INSERT INTO children (study_id, first_name_initial, last_name_initial, "
                "age, gender, school_level, state, created_at) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (sid, first_name_initial, last_name_initial, age, gender, school_level, state, _now()),
            )
            row = conn.execute("SELECT * FROM children WHERE study_id=?", (sid,)).fetchone()
        return dict(row)


def find_child(study_id: str) -> dict | None:
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM children WHERE study_id = ?", (study_id.strip().upper(),)
        ).fetchone()
        return dict(row) if row else None


def list_children(limit: int = 100) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM children ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

def save_session(
    *,
    child_id: int,
    rater_type: str,
    rater_contact: str | None,
    responses: dict,
    result,  # scoring.ScreeningResult; avoid circular import
    ml_prediction: str | None,
) -> int:
    init_db()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO screening_sessions (child_id, rater_type, rater_contact, "
            "completed_at, responses_json, inatt_endorsed, hi_endorsed, "
            "impairment_count, presentation, risk_level, flags_json, ml_prediction) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                child_id,
                rater_type,
                rater_contact,
                _now(),
                json.dumps(responses),
                result.inattention_endorsed,
                result.hyperactivity_endorsed,
                result.impairment_count,
                result.presentation,
                result.risk_level,
                json.dumps(result.flags),
                ml_prediction,
            ),
        )
        return int(cur.lastrowid)


def sessions_for_child(child_id: int) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM screening_sessions WHERE child_id = ? ORDER BY completed_at DESC",
            (child_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def recent_sessions(limit: int = 50) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT s.*, c.study_id, c.age, c.gender, c.school_level, c.state "
            "FROM screening_sessions s JOIN children c ON c.id = s.child_id "
            "ORDER BY s.completed_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Clinician activity audit log
# ---------------------------------------------------------------------------

def log_activity(
    *, clinician_name: str, action: str, target_study_id: str | None = None
) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            "INSERT INTO clinician_activity (clinician_name, action, target_study_id, occurred_at) "
            "VALUES (?,?,?,?)",
            (clinician_name, action, target_study_id, _now()),
        )


def recent_activity(limit: int = 30) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM clinician_activity ORDER BY occurred_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# User feedback
# ---------------------------------------------------------------------------

def save_feedback(
    *,
    role: str | None,
    rating: int | None,
    category: str | None,
    message: str,
    contact: str | None = None,
) -> int:
    """Store one feedback submission. `message` is the only required field.

    Nothing here is linked to a child or a screening session — feedback is
    deliberately anonymous. `contact` is the sole piece of PII and is only
    present when the user volunteered it to get a reply.
    """
    init_db()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO feedback (submitted_at, role, rating, category, message, contact) "
            "VALUES (?,?,?,?,?,?)",
            (_now(), role, rating, category, message.strip(), (contact or "").strip() or None),
        )
        return int(cur.lastrowid)


def recent_feedback(limit: int = 50) -> list[dict]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM feedback ORDER BY submitted_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def feedback_stats() -> dict:
    """Aggregate counts for the clinician dashboard. Returns zeros on an empty table."""
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total, AVG(rating) AS avg_rating FROM feedback"
        ).fetchone()
        by_cat = conn.execute(
            "SELECT category, COUNT(*) AS n FROM feedback "
            "GROUP BY category ORDER BY n DESC"
        ).fetchall()
        return {
            "total": int(row["total"] or 0),
            "avg_rating": float(row["avg_rating"]) if row["avg_rating"] is not None else None,
            "by_category": {r["category"] or "Uncategorised": int(r["n"]) for r in by_cat},
        }


# ---------------------------------------------------------------------------
# Paid consultations + live messaging
#
# NOTE: `reference` is a bearer token. Anyone holding it can open the thread.
# That is acceptable because it is unguessable (10 hex chars) and the thread
# contains no PII beyond what the requester typed -- but it means a consultation
# link must be treated like a password, not shared.
# ---------------------------------------------------------------------------

def create_consultation(
    *,
    reference: str,
    study_id: str | None,
    requester_role: str,
    requester_email: str,
    amount_kobo: int,
) -> int:
    init_db()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO consultations (reference, study_id, requester_role, "
            "requester_email, amount_kobo, status, created_at) "
            "VALUES (?,?,?,?,?,'pending',?)",
            (
                reference,
                (study_id or "").strip().upper() or None,
                requester_role,
                requester_email.strip(),
                int(amount_kobo),
                _now(),
            ),
        )
        return int(cur.lastrowid)


def find_consultation(reference: str) -> dict | None:
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM consultations WHERE reference = ?",
            (reference.strip().upper(),),
        ).fetchone()
        return dict(row) if row else None


def mark_consultation_paid(reference: str) -> None:
    """Idempotent: re-verifying an already-paid reference must not reset it or
    double-count. The requester WILL hit this more than once (browser refresh
    on the callback URL is normal)."""
    init_db()
    with connect() as conn:
        conn.execute(
            "UPDATE consultations SET status='paid', paid_at=COALESCE(paid_at, ?) "
            "WHERE reference=? AND status != 'closed'",
            (_now(), reference.strip().upper()),
        )


def close_consultation(reference: str) -> None:
    init_db()
    with connect() as conn:
        conn.execute(
            "UPDATE consultations SET status='closed' WHERE reference=?",
            (reference.strip().upper(),),
        )


def claim_consultation(reference: str, consultant_name: str) -> None:
    """First clinician to reply owns the thread."""
    init_db()
    with connect() as conn:
        conn.execute(
            "UPDATE consultations SET consultant_name = COALESCE(consultant_name, ?) "
            "WHERE reference = ?",
            (consultant_name, reference.strip().upper()),
        )


def list_consultations(status: str | None = None, limit: int = 50) -> list[dict]:
    init_db()
    with connect() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM consultations WHERE status = ? "
                "ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM consultations ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]


def post_message(
    *, consultation_id: int, sender_role: str, sender_name: str | None, body: str
) -> int:
    init_db()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO consultation_messages (consultation_id, sender_role, "
            "sender_name, body, sent_at) VALUES (?,?,?,?,?)",
            (int(consultation_id), sender_role, sender_name, body.strip(), _now()),
        )
        return int(cur.lastrowid)


def messages_for(consultation_id: int) -> list[dict]:
    """Oldest-first: this renders as a chat transcript, top to bottom."""
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM consultation_messages WHERE consultation_id = ? "
            "ORDER BY id ASC",
            (int(consultation_id),),
        ).fetchall()
        return [dict(r) for r in rows]


def unread_count(consultation_id: int, *, not_from_role: str) -> int:
    """How many messages in this thread were NOT sent by `not_from_role`.
    Used to badge the clinician inbox with waiting replies."""
    init_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM consultation_messages "
            "WHERE consultation_id = ? AND sender_role != ?",
            (int(consultation_id), not_from_role),
        ).fetchone()
        return int(row["n"] or 0)


def latest_parent_and_teacher(child_id: int) -> tuple[dict | None, dict | None]:
    """Return the most-recent Parent and Teacher sessions (if any) for one child."""
    init_db()
    with connect() as conn:
        p = conn.execute(
            "SELECT * FROM screening_sessions WHERE child_id=? AND rater_type='Parent' "
            "ORDER BY completed_at DESC LIMIT 1",
            (child_id,),
        ).fetchone()
        t = conn.execute(
            "SELECT * FROM screening_sessions WHERE child_id=? AND rater_type='Teacher' "
            "ORDER BY completed_at DESC LIMIT 1",
            (child_id,),
        ).fetchone()
        return (dict(p) if p else None, dict(t) if t else None)
