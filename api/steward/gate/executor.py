"""Approve / reject / execute pending actions (docs/02 §7a "Approve", docs/04 T3.3).

Approve, in one BEGIN IMMEDIATE transaction (so concurrent approves and rejects serialize):
  1. The action must exist and still be 'pending' (else 404 / 409 "Action already decided").
  2. Risk is recomputed now (contacts, the owner, whether the files_write target exists) and
     stored on the still-pending row.
  3. R0 ("unresolved placeholder") is never approvable, not even with confirm_high (409).
     Any other High needs confirm_high, else 409; the row stays pending so the UI can confirm.
  4. Claim: UPDATE actions SET status='approved', decided_at=? WHERE id=? AND status='pending';
     proceed only if rowcount == 1. Then audit action_decided.
Execute (only after a successful claim; never twice, never retried):
  - mail_send: store args_json exactly in demo_mail 'sent'; if DEMO_MAIL_REDIRECT is set, send
    a real copy over SMTP with Message-ID <steward-action-{id}@rao-consulting.example> and write
    egress_events(channel='mail'). An SMTP timeout -> 'failed', "delivery unknown — check Sent
    before retrying".
  - files_write: safe_path again, then an atomic write of args_json's content.
  Result 'executed' or 'failed', audited as action_executed.
Reject: the same conditional UPDATE to 'rejected'; audited as action_decided.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from dataclasses import dataclass
from typing import Any, Literal

import anyio

from steward import db, seed
from steward.config import get_settings
from steward.connectors import files, mail_demo, smtp
from steward.gate import actions, risk
from steward.ledger import store
from steward.shield import Shield

log = logging.getLogger("steward.gate")
MESSAGE_ID = "<steward-action-{id}@rao-consulting.example>"
ALREADY_DECIDED = "Action already decided"
NOT_FOUND = "action not found"
NEEDS_CONFIRM = "High-risk action needs confirm_high"
NOW_HIGH = "Risk is now High; confirm to approve"


@dataclass
class Outcome:
    """What a decision did: HTTP status, an error detail (None on success) and the row."""

    status: int
    detail: str | None
    action: dict[str, Any] | None


def _get(conn: sqlite3.Connection, action_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM actions WHERE id = ?", (action_id,)).fetchone()


def _must_get(conn: sqlite3.Connection, action_id: int) -> sqlite3.Row:
    row = _get(conn, action_id)
    if row is None:  # only after we saw it inside the same transaction
        raise RuntimeError(f"action #{action_id} vanished")
    return row


def list_actions(conn: sqlite3.Connection, status: Literal["pending", "all"]) -> list[dict]:
    if status == "pending":
        cur = conn.execute("SELECT * FROM actions WHERE status = 'pending' ORDER BY id ASC")
    else:
        cur = conn.execute("SELECT * FROM actions ORDER BY id DESC")
    return [actions.row_to_action(r) for r in cur.fetchall()]


def _current_risk(conn: sqlite3.Connection, row: sqlite3.Row) -> tuple[str, list[str], str | None]:
    """(risk, reasons, refusal): risk as of now. refusal is set when a files_write target is no
    longer a safe place to write (e.g. a symlink planted after queueing)."""
    args = json.loads(row["args_json"])
    exists = False
    if row["tool"] == "files_write":
        try:
            _, target = actions.write_target(str(args.get("path", "")))
        except (files.UnsafePath, actions.InvalidAction) as exc:
            return "high", json.loads(row["risk_reasons"] or "[]"), f"write refused: {exc}"
        exists = target.exists()
    level, reasons = risk.assess(row["tool"], args, actions.risk_context(conn), exists)
    return level, reasons, None


def claim_approval(conn: sqlite3.Connection, action_id: int, confirm_high: bool) -> Outcome:
    """Recompute, gate and claim (docs/02 §7a). Commits on every path, so a recomputed risk is
    kept even when the answer is 409."""
    conn.execute("BEGIN IMMEDIATE")
    row = _get(conn, action_id)
    if row is None:
        return Outcome(404, NOT_FOUND, None)
    if row["status"] != "pending":
        return Outcome(409, ALREADY_DECIDED, actions.row_to_action(row))
    level, reasons, refusal = _current_risk(conn, row)
    if refusal:  # not approvable at all; the stored risk is left as it was
        return Outcome(409, refusal, actions.row_to_action(row))
    was_low = row["risk"] == "low"
    stored_reasons = json.loads(row["risk_reasons"] or "[]")
    if (level, reasons) != (row["risk"], stored_reasons):
        conn.execute(
            "UPDATE actions SET risk = ?, risk_reasons = ? WHERE id = ? AND status = 'pending'",
            (level, json.dumps(reasons, ensure_ascii=False), action_id),
        )
        row = _must_get(conn, action_id)
    if not risk.approvable(reasons):
        return Outcome(409, risk.UNRESOLVED_PLACEHOLDER, actions.row_to_action(row))
    if level == "high" and not confirm_high:
        return Outcome(409, NOW_HIGH if was_low else NEEDS_CONFIRM, actions.row_to_action(row))
    cur = conn.execute(
        "UPDATE actions SET status = 'approved', decided_at = ? "
        "WHERE id = ? AND status = 'pending'",
        (db.now_iso(), action_id),
    )
    if cur.rowcount != 1:
        return Outcome(409, ALREADY_DECIDED, actions.row_to_action(row))
    db.audit(
        conn,
        "action_decided",
        f"action #{action_id} approved",
        detail=json.dumps(
            {"risk": level, "risk_reasons": reasons, "confirm_high": confirm_high},
            ensure_ascii=False,
        ),
        ref_table="actions",
        ref_id=action_id,
    )
    return Outcome(200, None, actions.row_to_action(_must_get(conn, action_id)))


def reject(conn: sqlite3.Connection, action_id: int) -> Outcome:
    conn.execute("BEGIN IMMEDIATE")
    row = _get(conn, action_id)
    if row is None:
        return Outcome(404, NOT_FOUND, None)
    cur = conn.execute(
        "UPDATE actions SET status = 'rejected', decided_at = ? "
        "WHERE id = ? AND status = 'pending'",
        (db.now_iso(), action_id),
    )
    if cur.rowcount != 1:
        return Outcome(409, ALREADY_DECIDED, actions.row_to_action(row))
    db.audit(
        conn,
        "action_decided",
        f"action #{action_id} rejected",
        ref_table="actions",
        ref_id=action_id,
    )
    return Outcome(200, None, actions.row_to_action(_must_get(conn, action_id)))


# --- execution ------------------------------------------------------------------------------


def _finish(
    conn: sqlite3.Connection,
    action_id: int,
    status: Literal["executed", "failed"],
    result: str | None,
    summary: str,
) -> dict[str, Any]:
    conn.execute(
        "UPDATE actions SET status = ?, result = ? WHERE id = ? AND status = 'approved'",
        (status, result, action_id),
    )
    db.audit(conn, "action_executed", summary, detail=result, ref_table="actions", ref_id=action_id)
    return actions.row_to_action(_must_get(conn, action_id))


def _store_sent(conn: sqlite3.Connection, args: dict[str, Any]) -> int:
    owner = get_settings().owner_email
    named = conn.execute(
        "SELECT name FROM contacts WHERE lower(email) = lower(?) AND name IS NOT NULL", (owner,)
    ).fetchone()
    return mail_demo.store_sent(
        conn, named["name"] if named else owner, owner, args["to"], args["subject"], args["body"]
    )


def _copy_not_stored(message_id: str, exc: BaseException) -> dict[str, Any]:
    action_id = message_id.removeprefix("<steward-action-").split("@", 1)[0]
    return {"action_id": action_id, "copy": f"not stored ({type(exc).__name__})"}


def _mail_egress(
    conn: sqlite3.Connection,
    args: dict[str, Any],
    message_id: str,
    status: Literal["ok", "error"],
    latency_ms: int,
    result: str | None,
) -> None:
    """egress_events(channel='mail') for an SMTP attempt. The stored copy goes through the
    Shield like every stored body (the real message went to DEMO_MAIL_REDIRECT); the local view
    re-identifies it on read. If the copy cannot be built, a row with only the Message-ID is
    still written: every SMTP attempt leaves a ledger row."""
    s = get_settings()
    message = {
        "to": [s.demo_mail_redirect],
        "subject": smtp.subject_for(args["to"], args["subject"]),
        "message_id": message_id,
        "body": args["body"],
    }
    try:
        shield = Shield(conn)

        def redacted(body: dict[str, Any]) -> dict[str, Any]:
            out = shield.outbound(body)
            return (out.blocked_request or out.request) if out.leaks else out.request

        request = redacted(message)
        response = redacted({"result": result}) if result else None
    except Exception as exc:  # never lose the row; store nothing that could identify anyone
        request = _copy_not_stored(message_id, exc)
        response = None
    store.insert(
        conn,
        channel="mail",
        destination=s.smtp_host or "smtp",
        status=status,
        request_redacted=request,
        response_redacted=response,
        latency_ms=latency_ms,
    )


async def _execute_mail(action: dict[str, Any], progress: dict[str, str]) -> dict[str, Any]:
    action_id = int(action["id"])
    args = json.loads(action["args_json"])
    if not smtp.enabled():

        def local(conn: sqlite3.Connection) -> dict[str, Any]:
            _store_sent(conn, args)
            return _finish(
                conn, action_id, "executed", None, "mail_send → sent (demo mailbox only)"
            )

        return await db.run(local)

    await db.run(lambda conn: _store_sent(conn, args))
    message_id = MESSAGE_ID.format(id=action_id)
    egress: Literal["ok", "error"] | None = "error"
    status: Literal["executed", "failed"] = "failed"
    result: str | None
    progress["smtp"] = "attempted"
    started = time.monotonic()
    try:
        await smtp.send(args["to"], args["subject"], args["body"], message_id)
        egress, status, result, summary = "ok", "executed", None, "mail_send → sent"
        progress["smtp"] = "sent"
    except smtp.DeliveryUnknown:
        result, summary = smtp.DELIVERY_UNKNOWN, "mail_send → delivery unknown"
    except smtp.SmtpError as exc:
        result, summary = str(exc), "mail_send → failed"
        progress["smtp"] = "not sent"
    except smtp.SmtpNotConfigured as exc:
        egress, result, summary = None, f"SMTP not configured: {exc}", "mail_send → failed"
        progress["smtp"] = "not sent"
    except Exception as exc:  # never retried; the class name only (no message body, no secret)
        result, summary = f"send error: {type(exc).__name__}", "mail_send → failed"
    latency_ms = int((time.monotonic() - started) * 1000)
    progress["latency_ms"] = str(latency_ms)

    def finish(conn: sqlite3.Connection) -> dict[str, Any]:
        if egress is not None:
            _mail_egress(conn, args, message_id, egress, latency_ms, result)
        return _finish(conn, action_id, status, result, summary)

    return await db.run(finish)


# One worker process: this lock makes "does the target exist?" + write atomic across
# concurrently approved files_write actions.
_WRITE_LOCK = threading.Lock()


def _write_file(
    args: dict[str, Any], allow_overwrite: bool
) -> tuple[Literal["executed", "failed"], str | None, str]:
    """Runs in a worker thread: safe_path again at execute time, then an atomic write. A file
    that appeared after approval is not overwritten unless the overwrite was approved."""
    with _WRITE_LOCK:
        try:
            _, target = actions.write_target(str(args["path"]))
        except (files.UnsafePath, actions.InvalidAction) as exc:
            return "failed", f"write refused: {exc}", "files_write → failed"
        if target.exists() and not allow_overwrite:
            return (
                "failed",
                "write refused: the file appeared after approval; queue it again to overwrite",
                "files_write → failed",
            )
        try:
            seed.atomic_write(target, str(args["content"]))
        except OSError as exc:
            return "failed", f"write failed: {type(exc).__name__}", "files_write → failed"
    return "executed", None, "files_write → written"


async def _execute_write(action: dict[str, Any], progress: dict[str, str]) -> dict[str, Any]:
    args = json.loads(action["args_json"])
    allow_overwrite = risk.OVERWRITES in (action.get("risk_reasons") or [])
    status, result, summary = await anyio.to_thread.run_sync(_write_file, args, allow_overwrite)
    if status == "executed":
        progress["write"] = "written"
    return await db.run(lambda conn: _finish(conn, int(action["id"]), status, result, summary))


async def _finish_after_error(
    action: dict[str, Any], exc: BaseException, progress: dict[str, str]
) -> dict[str, Any]:
    """Something broke after the claim (e.g. the database while recording the result). The row
    must not stay 'approved' forever: record what is known, in a fresh transaction. If an SMTP
    attempt was made, its mail ledger row is written too (a copy without the body)."""
    action_id, tool = int(action["id"]), action["tool"]
    status: Literal["executed", "failed"] = "failed"
    egress: Literal["ok", "error"] | None = None
    if progress.get("smtp") == "sent":
        status, result, summary, egress = "executed", None, "mail_send → sent", "ok"
    elif progress.get("smtp") == "attempted":
        result, summary, egress = smtp.DELIVERY_UNKNOWN, "mail_send → delivery unknown", "error"
    elif progress.get("write") == "written":
        status, result, summary = "executed", None, "files_write → written"
    else:
        result, summary = f"execution error: {type(exc).__name__}", f"{tool} → failed"

    def record(conn: sqlite3.Connection) -> dict[str, Any]:
        if egress is not None:
            try:
                store.insert(
                    conn,
                    channel="mail",
                    destination=get_settings().smtp_host or "smtp",
                    status=egress,
                    request_redacted=_copy_not_stored(MESSAGE_ID.format(id=action_id), exc),
                    latency_ms=int(progress.get("latency_ms", "0")),
                )
            except Exception as ledger_exc:  # the action's final state comes first
                # The exception type only: never a body or an address.
                log.error(
                    "action #%s: mail ledger row not written (%s)",
                    action_id,
                    type(ledger_exc).__name__,
                )
        return _finish(conn, action_id, status, result, summary)

    return await db.run(record)


async def execute(action: dict[str, Any]) -> dict[str, Any]:
    """Run a claimed ('approved') action exactly once. Shielded from cancellation, so a client
    that disconnects mid-send cannot leave the row half-finished; any error after the claim
    still ends in 'executed' or 'failed'."""
    done: dict[str, Any] | None = None
    progress: dict[str, str] = {}
    with anyio.CancelScope(shield=True):
        try:
            if action["tool"] == "mail_send":
                done = await _execute_mail(action, progress)
            else:
                done = await _execute_write(action, progress)
        except Exception as exc:
            done = await _finish_after_error(action, exc, progress)
    if done is None:  # a shielded scope is never cancelled; this cannot happen
        raise RuntimeError(f"action #{action['id']} did not finish")
    return done


async def approve(action_id: int, confirm_high: bool) -> Outcome:
    outcome = await db.run(lambda conn: claim_approval(conn, action_id, confirm_high))
    if outcome.status != 200 or outcome.action is None:
        return outcome
    return Outcome(200, None, await execute(outcome.action))


async def reject_action(action_id: int) -> Outcome:
    return await db.run(lambda conn: reject(conn, action_id))
