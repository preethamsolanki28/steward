"""Egress Ledger store (docs/02 §5 `egress_events`, §7a step 10, docs/04 T2.4).

Every insert also writes its audit_events row in the same transaction:
- status 'blocked' -> policy_block, "Blocked: identifier would have left the Mac"
- llm rows         -> egress, "<model display name> · N identifiers masked"
- web rows         -> egress, "Tavily search"
- mail rows        -> egress, "Mail sent" (or "Mail send error" when the SMTP attempt failed)
The redacted request/response stored here is the ONLY place a body is kept. Nothing is logged.
"""

import json
import sqlite3
from typing import Any

from steward import db
from steward.ledger.pricing import display_name

BLOCK_SUMMARY = "Blocked: identifier would have left the Mac"


def _text(value: Any) -> str | None:
    if value is None or isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def insert(
    conn: sqlite3.Connection,
    *,
    channel: str,
    destination: str,
    status: str,
    request_redacted: Any,
    response_redacted: Any = None,
    model: str | None = None,
    escalated_from: str | None = None,
    entities_masked: int = 0,
    entity_kinds: dict[str, int] | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    latency_ms: int = 0,
    cost_usd: float = 0.0,
) -> int:
    if channel not in ("llm", "web", "mail") or status not in ("ok", "error", "blocked"):
        raise ValueError(f"bad ledger row {channel=} {status=}")
    cur = conn.execute(
        "INSERT INTO egress_events (ts, channel, destination, model, escalated_from, "
        "request_redacted, response_redacted, entities_masked, entity_kinds, prompt_tokens, "
        "completion_tokens, latency_ms, cost_usd, status) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            db.now_iso(),
            channel,
            destination,
            model,
            escalated_from,
            _text(request_redacted),
            _text(response_redacted),
            int(entities_masked),
            json.dumps(entity_kinds or {}),
            prompt_tokens,
            completion_tokens,
            int(latency_ms),
            float(cost_usd),
            status,
        ),
    )
    row_id = int(cur.lastrowid or 0)
    if status == "blocked":
        db.audit(conn, "policy_block", BLOCK_SUMMARY, ref_table="egress_events", ref_id=row_id)
    elif channel == "llm":
        db.audit(
            conn,
            "egress",
            f"{display_name(model)} · {entities_masked} identifiers masked",
            ref_table="egress_events",
            ref_id=row_id,
        )
    elif channel == "web":
        db.audit(conn, "egress", "Tavily search", ref_table="egress_events", ref_id=row_id)
    else:  # mail: an SMTP attempt that failed must not read "Mail sent"
        summary = "Mail sent" if status == "ok" else "Mail send error"
        db.audit(conn, "egress", summary, ref_table="egress_events", ref_id=row_id)
    return row_id
