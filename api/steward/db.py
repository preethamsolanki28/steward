"""SQLite store (stdlib sqlite3, no ORM, no migrations: a schema change means make demo-reset).

Tables and columns are exactly docs/02 §5. Every call opens a short-lived connection; async code
reaches the database only through `run()` (anyio.to_thread), so the single Uvicorn worker never
blocks its event loop on disk IO (docs/02 §4 rule 8).
"""

import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import anyio

from steward.config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    org TEXT,
    trusted INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS vault (
    id INTEGER PRIMARY KEY,
    placeholder TEXT UNIQUE,
    kind TEXT,
    value TEXT,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS egress_events (
    id INTEGER PRIMARY KEY,
    ts TEXT,
    channel TEXT,
    destination TEXT,
    model TEXT,
    escalated_from TEXT,
    request_redacted TEXT,
    response_redacted TEXT,
    entities_masked INTEGER,
    entity_kinds TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    latency_ms INTEGER,
    cost_usd REAL,
    status TEXT
);
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY,
    created_at TEXT,
    tool TEXT,
    args_json TEXT,
    preview TEXT,
    risk TEXT,
    risk_reasons TEXT,
    status TEXT,
    decided_at TEXT,
    result TEXT
);
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY,
    ts TEXT,
    kind TEXT,
    summary TEXT,
    detail TEXT,
    ref_table TEXT,
    ref_id INTEGER
);
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    title TEXT,
    hermes_session_id TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role TEXT,
    content TEXT,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS briefs (
    id INTEGER PRIMARY KEY,
    created_at TEXT,
    content_md TEXT
);
CREATE TABLE IF NOT EXISTS demo_mail (
    id INTEGER PRIMARY KEY,
    folder TEXT,
    from_name TEXT,
    from_email TEXT,
    to_emails TEXT,
    subject TEXT,
    body TEXT,
    ts TEXT,
    is_read INTEGER
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""

AUDIT_KINDS = frozenset(
    {
        "tool_call",
        "egress",
        "policy_block",
        "action_created",
        "action_decided",
        "action_executed",
        "memory_edit",
        "skill_run",
    }
)


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def connect(path: Path | None = None) -> sqlite3.Connection:
    db_path = path or get_settings().db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_schema(path: Path | None = None) -> None:
    with connect(path) as conn:
        conn.executescript(SCHEMA)


def with_conn[T](fn: Callable[[sqlite3.Connection], T]) -> T:
    conn = connect()
    try:
        with conn:
            return fn(conn)
    finally:
        conn.close()


async def run[T](fn: Callable[[sqlite3.Connection], T]) -> T:
    """Run a sync DB function in a worker thread (never on the event loop)."""
    return await anyio.to_thread.run_sync(with_conn, fn)


def audit(
    conn: sqlite3.Connection,
    kind: str,
    summary: str,
    detail: str | None = None,
    ref_table: str | None = None,
    ref_id: int | None = None,
) -> int:
    if kind not in AUDIT_KINDS:
        raise ValueError(f"unknown audit kind {kind!r}")
    cur = conn.execute(
        "INSERT INTO audit_events (ts, kind, summary, detail, ref_table, ref_id) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (now_iso(), kind, summary, detail, ref_table, ref_id),
    )
    return int(cur.lastrowid or 0)


def get_setting(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return None if row is None else str(row["value"])


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def rows(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
    return [dict(r) for r in cursor.fetchall()]
