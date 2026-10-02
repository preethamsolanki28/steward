"""MAIL_MODE=demo mailbox: the `demo_mail` table (folders 'inbox' and 'sent'), docs/02 §5.

Sync functions taking a sqlite3 connection; callers run them via steward.db.run (worker thread).
"""

import json
import sqlite3
from typing import Any

from steward import db


def _row(r: sqlite3.Row) -> dict[str, Any]:
    d = dict(r)
    d["to_emails"] = json.loads(d.get("to_emails") or "[]")
    return d


def search(
    conn: sqlite3.Connection, query: str, limit: int = 10, folder: str = "inbox"
) -> list[dict[str, Any]]:
    """Newest first. An email matches when ANY query term appears in the sender, recipients,
    subject or body (case-insensitive). An empty query lists the folder."""
    terms = [t.casefold() for t in query.split() if t.strip()]
    rows = conn.execute(
        "SELECT * FROM demo_mail WHERE folder = ? ORDER BY ts DESC, id DESC", (folder,)
    ).fetchall()
    hits = []
    for r in rows:
        haystack = " ".join(
            str(r[k] or "") for k in ("from_name", "from_email", "to_emails", "subject", "body")
        ).casefold()
        if not terms or any(term in haystack for term in terms):
            hits.append(_row(r))
        if len(hits) >= max(0, limit):
            break
    return hits


def read(conn: sqlite3.Connection, mail_id: int) -> dict[str, Any] | None:
    r = conn.execute("SELECT * FROM demo_mail WHERE id = ?", (mail_id,)).fetchone()
    if r is None:
        return None
    if r["folder"] == "inbox" and not r["is_read"]:
        conn.execute("UPDATE demo_mail SET is_read = 1 WHERE id = ?", (mail_id,))
    return _row(r)


def store_sent(
    conn: sqlite3.Connection,
    from_name: str,
    from_email: str,
    to: list[str],
    subject: str,
    body: str,
) -> int:
    cur = conn.execute(
        "INSERT INTO demo_mail (folder, from_name, from_email, to_emails, subject, body, ts, "
        "is_read) VALUES ('sent', ?, ?, ?, ?, ?, ?, 1)",
        (from_name, from_email, json.dumps(to), subject, body, db.now_iso()),
    )
    return int(cur.lastrowid or 0)
