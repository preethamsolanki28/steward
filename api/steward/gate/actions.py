"""Pending actions (docs/02 §5 `actions`, §7a "Side effects"; docs/04 T3.1).

mail_send and files_write never send or write. Each validates its arguments, scores them with
the risk rules, inserts an `actions` row with status 'pending' and writes
audit_events(kind='action_created'). A High-risk action is still queued: the Gate decides at
approve time, the agent is never blocked.

args_json is the exact, normalized argument set; it is never modified after the INSERT and is
what the executor sends or writes, byte-for-byte as previewed.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from steward import db
from steward.config import get_settings
from steward.connectors import files
from steward.gate import risk

QUEUED = "Queued for approval as action #{id}. The user will review it."
MAX_CONTENT_BYTES = files.MAX_READ_BYTES  # so a written file can be read back
TOOLS = ("mail_send", "files_write")


class InvalidAction(ValueError):
    """Arguments that can never become a safe action (nothing is queued)."""


def risk_context(conn: sqlite3.Connection) -> risk.RiskContext:
    trusted = conn.execute("SELECT email, org FROM contacts WHERE trusted = 1 ORDER BY id")
    return risk.context([(r["email"], r["org"]) for r in trusted], get_settings().owner_email)


def mail_args(
    to: str | list[str] | None, subject: str, body: str, in_reply_to: str | int | None
) -> dict[str, Any]:
    raw = [to] if isinstance(to, str) else list(to or [])
    if any("\r" in str(x) or "\n" in str(x) for x in [*raw, subject]):
        raise InvalidAction("recipients and subject must be single-line")
    rcpts = risk.normalize_recipients(to)
    if not rcpts:
        raise InvalidAction("to must list at least one recipient")
    args: dict[str, Any] = {"to": rcpts, "subject": subject, "body": body}
    if in_reply_to is not None and str(in_reply_to).strip():
        args["in_reply_to"] = str(in_reply_to).strip()
    return args


def write_target(path: str) -> tuple[str, Path]:
    """safe_path-checked target -> (workspace-relative posix path, resolved path).
    Raises files.UnsafePath or InvalidAction. Touches the filesystem: call off the loop."""
    target = files.safe_path(path)
    base = Path(files.safe_path(""))
    if target == base or target.is_dir():
        raise InvalidAction("path is a directory")
    return target.relative_to(base).as_posix(), target


def files_args(path: str, content: str) -> tuple[dict[str, Any], Path]:
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise InvalidAction("content too large (max 256 KiB)")
    rel, target = write_target(path)
    return {"path": rel, "content": content}, target


def dumps(args: dict[str, Any]) -> tuple[str, str]:
    """(args_json, preview): compact and pretty JSON of the same arguments."""
    return (
        json.dumps(args, ensure_ascii=False, separators=(",", ":")),
        json.dumps(args, ensure_ascii=False, indent=2),
    )


def create(
    conn: sqlite3.Connection, tool: str, args: dict[str, Any], path_exists: bool = False
) -> dict[str, Any]:
    """Insert the pending action and its audit row (same transaction)."""
    if tool not in TOOLS:
        raise InvalidAction(f"unknown action tool {tool!r}")
    level, reasons = risk.assess(tool, args, risk_context(conn), path_exists)
    args_json, preview = dumps(args)
    cur = conn.execute(
        "INSERT INTO actions (created_at, tool, args_json, preview, risk, risk_reasons, status, "
        "decided_at, result) VALUES (?, ?, ?, ?, ?, ?, 'pending', NULL, NULL)",
        (db.now_iso(), tool, args_json, preview, level, json.dumps(reasons, ensure_ascii=False)),
    )
    action_id = int(cur.lastrowid or 0)
    db.audit(conn, "action_created", f"{tool} → queued", ref_table="actions", ref_id=action_id)
    return {
        "action_id": action_id,
        "status": "pending",
        "risk": level,
        "message": QUEUED.format(id=action_id),
    }


def row_to_action(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
    """An actions row as the API serves it (risk_reasons parsed; docs/02 §6, web/lib/types.ts)."""
    d = dict(row)
    d["risk_reasons"] = json.loads(d.get("risk_reasons") or "[]")
    return d
