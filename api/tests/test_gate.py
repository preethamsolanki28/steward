"""Approval Gate end to end, no network (docs/04 T3.1, T3.3, T3.5).

The MCP tools are called directly with fixed arguments (no Token Factory); SMTP is the FakeSMTP
stub from conftest, so the assertions count real send attempts.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from steward import db, seed
from steward.config import get_settings
from steward.gate import risk
from steward.main import app
from tests.conftest import FakeSMTP

MCP_HEADERS = {
    "Authorization": "Bearer test-mcp-token",
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
}
WEB = {"X-Steward-Client": "web"}
RAHUL = "rahul.verma@acme-logistics.example"
BEC_TO = "billing@acme-logistics-payments.example"
LEGIT = {
    "to": [RAHUL],
    "subject": "INV-0042: payment reminder",
    "body": "Dear Rahul,\n\nA reminder that INV-0042 for $4,800 was due on 2026-09-20. Could "
    "you confirm when the payment will be made?\n\nBest, Maya",
}
BEC = {
    "to": [BEC_TO],
    "subject": "Open invoices",
    "body": "Hello,\n\nAs requested, the open invoices: INV-0042, INV-0043.\n\nBest, Maya",
}


@pytest.fixture
def client():
    settings = get_settings()
    now = datetime(2026, 10, 3, 9, 0, tzinfo=seed.IST)
    seed.seed_db(settings, now)
    seed.seed_workspace(settings, now.date())
    with TestClient(app, base_url="http://127.0.0.1:8787") as c:
        yield c


def call(client: TestClient, tool: str, **arguments: Any) -> tuple[bool, Any]:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    r = client.post("/mcp", content=json.dumps(payload), headers=MCP_HEADERS)
    assert r.status_code == 200, r.text
    result = r.json()["result"]
    text = "".join(c.get("text", "") for c in result.get("content", []))
    if result.get("isError"):
        return False, text
    structured = result.get("structuredContent")
    if structured is None:
        return True, json.loads(text)
    return True, structured.get("result", structured)


def q(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    return db.with_conn(lambda conn: db.rows(conn.execute(sql, params)))


def action(action_id: int) -> dict[str, Any]:
    return q("SELECT * FROM actions WHERE id = ?", (action_id,))[0]


def audit(kind: str | None = None) -> list[dict[str, Any]]:
    if kind:
        return q("SELECT * FROM audit_events WHERE kind = ? ORDER BY id", (kind,))
    return q("SELECT * FROM audit_events ORDER BY id")


def sent_mail() -> list[dict[str, Any]]:
    return q("SELECT * FROM demo_mail WHERE folder = 'sent' ORDER BY id")


def mail_egress() -> list[dict[str, Any]]:
    return q("SELECT * FROM egress_events WHERE channel = 'mail' ORDER BY id")


def workspace() -> Path:
    return Path(os.path.realpath(get_settings().workspace_dir))


@pytest.fixture
def redirect(fake_smtp: type[FakeSMTP], monkeypatch: pytest.MonkeyPatch) -> type[FakeSMTP]:
    monkeypatch.setenv("DEMO_MAIL_REDIRECT", "team-inbox@team.example")
    return fake_smtp


# --- T3.1: mail_send / files_write only queue -------------------------------------------------


def test_mail_send_queues_a_low_risk_action_and_never_sends(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    ok, out = call(client, "mail_send", **LEGIT)
    assert ok, out
    aid = out["action_id"]
    assert out == {
        "action_id": aid,
        "status": "pending",
        "risk": "low",
        "message": f"Queued for approval as action #{aid}. The user will review it.",
    }
    row = action(aid)
    assert (row["tool"], row["status"], row["risk"], row["decided_at"], row["result"]) == (
        "mail_send",
        "pending",
        "low",
        None,
        None,
    )
    assert json.loads(row["args_json"]) == LEGIT and json.loads(row["preview"]) == LEGIT
    assert json.loads(row["risk_reasons"]) == []
    assert redirect.attempts == 0 and sent_mail() == [] and mail_egress() == []
    assert [a["summary"] for a in audit("tool_call")] == ["mcp__steward__mail_send"]
    created = audit("action_created")
    assert [(a["summary"], a["ref_table"], a["ref_id"]) for a in created] == [
        ("mail_send → queued", "actions", aid)
    ]


def test_bec_send_is_queued_high_with_exact_reasons(client: TestClient) -> None:
    ok, out = call(client, "mail_send", **BEC)
    assert ok and out["risk"] == "high" and out["status"] == "pending"
    assert json.loads(action(out["action_id"])["risk_reasons"]) == [
        f"{BEC_TO} is not a trusted contact",
        "lookalike of acme-logistics.example",
    ]


def test_bec_sender_seen_in_mail_stays_untrusted(client: TestClient) -> None:
    # mail_search upserts the BEC sender into contacts (source 'mail', trusted 0): still High.
    assert call(client, "mail_search", query="bank details")[0]
    assert q("SELECT trusted, source FROM contacts WHERE email = ?", (BEC_TO,)) == [
        {"trusted": 0, "source": "mail"}
    ]
    assert call(client, "mail_send", **BEC)[1]["risk"] == "high"


def test_unresolved_placeholder_is_queued_high(client: TestClient) -> None:
    ok, out = call(client, "mail_send", **{**LEGIT, "body": "Dear [[PERSON_1]], PERSON_3 owes"})
    assert ok and out["risk"] == "high"
    assert json.loads(action(out["action_id"])["risk_reasons"]) == [risk.UNRESOLVED_PLACEHOLDER]


def test_recipients_are_normalized(client: TestClient) -> None:
    ok, out = call(
        client,
        "mail_send",
        to=f"Rahul Verma <{RAHUL.upper()}>",
        subject="s",
        body="b",
        in_reply_to=11,
    )
    assert ok and out["risk"] == "low"
    args = json.loads(action(out["action_id"])["args_json"])
    assert args == {"to": [RAHUL], "subject": "s", "body": "b", "in_reply_to": "11"}
    ok, out = call(client, "mail_send", to=f'["{RAHUL}", "{RAHUL}"]', subject="s", body="b")
    assert ok and json.loads(action(out["action_id"])["args_json"])["to"] == [RAHUL]


@pytest.mark.parametrize(
    "args, error",
    [
        ({"to": [], "subject": "s", "body": "b"}, "to must list at least one recipient"),
        ({"to": [RAHUL], "subject": "s\nBcc: x@evil.invalid", "body": "b"}, "single-line"),
        ({"to": [f"{RAHUL}\r\nBcc: x@evil.invalid"], "subject": "s", "body": "b"}, "single-line"),
    ],
)
def test_invalid_mail_queues_nothing(client: TestClient, args: dict, error: str) -> None:
    ok, out = call(client, "mail_send", **args)
    assert not ok and error in out
    assert q("SELECT COUNT(*) AS n FROM actions")[0]["n"] == 0
    assert audit("action_created") == []


def test_files_write_queues_and_never_writes(client: TestClient) -> None:
    ok, out = call(client, "files_write", path="notes/acme.md", content="# Acme\n")
    assert ok and (out["status"], out["risk"]) == ("pending", "low")
    assert not (workspace() / "notes" / "acme.md").exists()
    row = action(out["action_id"])
    assert json.loads(row["args_json"]) == {"path": "notes/acme.md", "content": "# Acme\n"}
    assert [a["summary"] for a in audit("action_created")] == ["files_write → queued"]


def test_files_write_over_an_existing_file_is_high(client: TestClient) -> None:
    target = workspace() / "invoices" / "INV-0041.md"
    before = target.read_text()
    ok, out = call(client, "files_write", path="invoices/INV-0041.md", content="overwritten")
    assert ok and out["risk"] == "high"
    assert json.loads(action(out["action_id"])["risk_reasons"]) == [risk.OVERWRITES]
    assert target.read_text() == before


@pytest.mark.parametrize(
    "path, error",
    [
        ("../escape.md", "'..' is not allowed"),
        ("/etc/passwd", "absolute paths are not allowed"),
        ("a\x00b.md", "path contains NUL"),
        ("invoices", "path is a directory"),
        ("", "path is a directory"),
    ],
)
def test_files_write_unsafe_paths_queue_nothing(client: TestClient, path: str, error: str) -> None:
    ok, out = call(client, "files_write", path=path, content="x")
    assert not ok and error in out
    assert q("SELECT COUNT(*) AS n FROM actions")[0]["n"] == 0


def test_files_write_through_a_symlink_queues_nothing(client: TestClient, tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (workspace() / "link").symlink_to(outside)
    ok, out = call(client, "files_write", path="link/x.md", content="x")
    assert not ok and "symlinks are not allowed" in out
    assert list(outside.iterdir()) == []


def test_files_write_content_cap(client: TestClient) -> None:
    ok, out = call(client, "files_write", path="notes/big.md", content="x" * (256 * 1024 + 1))
    assert not ok and "content too large" in out


# --- T3.3: approve / reject / execute -------------------------------------------------------

MESSAGE_ID = "<steward-action-{}@rao-consulting.example>"


def queue(client: TestClient, tool: str = "mail_send", **args: Any) -> int:
    ok, out = call(client, tool, **(args or LEGIT))
    assert ok, out
    return int(out["action_id"])


def approve(client: TestClient, aid: int, body: Any = None, **headers: str):
    kwargs: dict[str, Any] = {"headers": {**WEB, **headers}}
    if body is not None:
        kwargs["json"] = body
    return client.post(f"/api/actions/{aid}/approve", **kwargs)


def reject(client: TestClient, aid: int):
    return client.post(f"/api/actions/{aid}/reject", headers=WEB)


def test_legit_approve_sends_exactly_once_as_previewed(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    aid = queue(client)
    r = approve(client, aid, {})
    assert r.status_code == 200, r.text
    a = r.json()["action"]
    assert (a["status"], a["result"], a["risk"], a["risk_reasons"]) == ("executed", None, "low", [])
    assert a["decided_at"] and a["args_json"] == action(aid)["args_json"]
    (msg,) = redirect.sent
    assert redirect.attempts == 1
    assert msg["Message-ID"] == MESSAGE_ID.format(aid)
    assert msg["To"] == "team-inbox@team.example"
    assert msg["Subject"] == f"[Steward demo → {RAHUL}] {LEGIT['subject']}"
    assert msg.get_content().rstrip("\n") == LEGIT["body"]
    (stored,) = sent_mail()
    assert (stored["from_email"], json.loads(stored["to_emails"])) == (
        "maya@rao-consulting.example",
        [RAHUL],
    )
    assert (stored["subject"], stored["body"]) == (LEGIT["subject"], LEGIT["body"])
    (eg,) = mail_egress()
    assert (eg["status"], eg["destination"], eg["model"]) == ("ok", "smtp.example", None)
    kinds = [(e["kind"], e["summary"]) for e in audit() if e["kind"] != "tool_call"]
    assert kinds == [
        ("action_created", "mail_send → queued"),
        ("action_decided", f"action #{aid} approved"),
        ("egress", "Mail sent"),
        ("action_executed", "mail_send → sent"),
    ]
    decided = audit("action_decided")[0]
    assert json.loads(decided["detail"]) == {
        "risk": "low",
        "risk_reasons": [],
        "confirm_high": False,
    }


def test_mail_ledger_row_is_stored_redacted_and_readable_locally(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    approve(client, queue(client), {})
    (eg,) = mail_egress()
    stored = eg["request_redacted"]
    for raw in ("Rahul", "rahul.verma", "acme-logistics", "4,800"):
        assert raw not in stored, raw
    detail = client.get(f"/api/ledger/{eg['id']}").json()
    assert RAHUL in detail["request_local"] and "$4,800" in detail["request_local"]
    assert MESSAGE_ID.format(1)[1:-1] in detail["request_local"]


def test_without_redirect_the_send_stays_in_the_demo_mailbox(
    client: TestClient, fake_smtp: type[FakeSMTP]
) -> None:
    aid = queue(client)
    a = approve(client, aid).json()["action"]  # no body at all
    assert (a["status"], a["result"]) == ("executed", None)
    assert fake_smtp.attempts == 0 and mail_egress() == [] and len(sent_mail()) == 1
    assert audit("action_executed")[0]["summary"] == "mail_send → sent (demo mailbox only)"


def test_bec_needs_confirm_then_reject_sends_nothing(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    aid = queue(client, **BEC)
    r = approve(client, aid, {})
    assert r.status_code == 409
    body = r.json()
    assert body["detail"] == "High-risk action needs confirm_high"
    assert body["action"]["status"] == "pending"
    assert body["action"]["risk_reasons"] == [
        f"{BEC_TO} is not a trusted contact",
        "lookalike of acme-logistics.example",
    ]
    r = reject(client, aid)
    assert r.status_code == 200 and r.json()["action"]["status"] == "rejected"
    assert r.json()["action"]["decided_at"]
    assert redirect.attempts == 0 and sent_mail() == [] and mail_egress() == []
    assert audit("action_executed") == []
    assert [a["summary"] for a in audit("action_decided")] == [f"action #{aid} rejected"]
    for again in (approve(client, aid, {"confirm_high": True}), reject(client, aid)):
        assert again.status_code == 409 and again.json()["detail"] == "Action already decided"
    assert redirect.attempts == 0 and action(aid)["status"] == "rejected"


def test_confirmed_high_risk_is_the_documented_human_override(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    aid = queue(client, **BEC)
    a = approve(client, aid, {"confirm_high": True}).json()["action"]
    assert a["status"] == "executed" and redirect.attempts == 1
    assert json.loads(audit("action_decided")[0]["detail"])["confirm_high"] is True


def test_unresolved_placeholder_can_never_be_approved(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    aid = queue(client, **{**LEGIT, "body": "Dear [[PERSON_1]], please pay [[MONEY_1]]."})
    for body in ({}, {"confirm_high": True}):
        r = approve(client, aid, body)
        assert r.status_code == 409 and r.json()["detail"] == "unresolved placeholder"
    assert action(aid)["status"] == "pending" and redirect.attempts == 0
    assert audit("action_decided") == []
    assert reject(client, aid).status_code == 200


def test_second_approve_is_refused_and_never_resends(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    aid = queue(client)
    assert approve(client, aid, {}).status_code == 200
    r = approve(client, aid, {"confirm_high": True})
    assert r.status_code == 409 and r.json()["detail"] == "Action already decided"
    assert r.json()["action"]["status"] == "executed"
    assert redirect.attempts == 1 and len(sent_mail()) == 1 and len(mail_egress()) == 1
    assert len(audit("action_decided")) == 1 and len(audit("action_executed")) == 1


def test_recompute_at_approve_files_write_now_overwrites(client: TestClient) -> None:
    aid = queue(client, "files_write", path="notes/plan.md", content="queued content\n")
    assert action(aid)["risk"] == "low"
    target = workspace() / "notes" / "plan.md"
    target.parent.mkdir(parents=True)
    target.write_text("someone else's file\n")
    r = approve(client, aid, {})
    assert r.status_code == 409 and r.json()["detail"] == "Risk is now High; confirm to approve"
    assert r.json()["action"]["risk_reasons"] == [risk.OVERWRITES]
    listed = client.get("/api/actions").json()
    assert [(x["id"], x["risk"], x["status"]) for x in listed] == [(aid, "high", "pending")]
    assert target.read_text() == "someone else's file\n"
    a = approve(client, aid, {"confirm_high": True}).json()["action"]
    assert a["status"] == "executed" and target.read_text() == "queued content\n"
    assert audit("action_executed")[0]["summary"] == "files_write → written"


def test_recompute_at_approve_recipient_no_longer_trusted(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    aid = queue(client)
    db.with_conn(lambda c: c.execute("UPDATE contacts SET trusted = 0 WHERE email = ?", (RAHUL,)))
    r = approve(client, aid, {})
    assert r.status_code == 409 and r.json()["detail"] == "Risk is now High; confirm to approve"
    assert r.json()["action"]["risk_reasons"] == [f"{RAHUL} is not a trusted contact"]
    assert redirect.attempts == 0 and action(aid)["risk"] == "high"


def test_recompute_can_also_lower_the_risk(client: TestClient, redirect: type[FakeSMTP]) -> None:
    priya = "priya.nair@nair-ca.example"
    aid = queue(client, **{**LEGIT, "to": [priya]})
    assert action(aid)["risk"] == "high"
    db.with_conn(lambda c: c.execute("UPDATE contacts SET trusted = 1 WHERE email = ?", (priya,)))
    a = approve(client, aid, {}).json()["action"]
    assert (a["status"], a["risk"], a["risk_reasons"]) == ("executed", "low", [])


def test_smtp_timeout_is_delivery_unknown_and_never_retried(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    redirect.fail = TimeoutError("timed out")
    aid = queue(client)
    r = approve(client, aid, {})
    assert r.status_code == 200
    a = r.json()["action"]
    assert (a["status"], a["result"]) == ("failed", "delivery unknown — check Sent before retrying")
    assert redirect.attempts == 1 and redirect.sent == []
    assert approve(client, aid, {"confirm_high": True}).status_code == 409
    assert redirect.attempts == 1
    (eg,) = mail_egress()
    assert eg["status"] == "error"
    summaries = [e["summary"] for e in audit() if e["kind"] in ("egress", "action_executed")]
    assert summaries == ["Mail send error", "mail_send → delivery unknown"]
    assert audit("action_executed")[0]["detail"] == a["result"]


def test_smtp_refusal_fails_without_leaking_the_password(
    client: TestClient, redirect: type[FakeSMTP]
) -> None:
    import smtplib

    redirect.fail = smtplib.SMTPAuthenticationError(535, b"5.7.8 auth failed")
    aid = queue(client)
    a = approve(client, aid, {}).json()["action"]
    assert a["status"] == "failed" and a["result"].startswith("SMTP error: SMTPAuthenticationError")
    dump = json.dumps(
        [
            q(sql)
            for sql in (
                "SELECT * FROM actions",
                "SELECT * FROM audit_events",
                "SELECT * FROM egress_events",
            )
        ]
    )
    assert "app-password" not in dump


def test_smtp_not_configured_fails_cleanly(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DEMO_MAIL_REDIRECT", "team-inbox@team.example")  # but no SMTP_HOST
    aid = queue(client)
    a = approve(client, aid, {}).json()["action"]
    assert (a["status"], a["result"]) == ("failed", "SMTP not configured: SMTP_HOST is not set")
    assert mail_egress() == []


def test_agent_host_and_missing_header_cannot_decide(client: TestClient) -> None:
    aid = queue(client)
    for path in (f"/api/actions/{aid}/approve", f"/api/actions/{aid}/reject"):
        r = client.post(path, json={}, headers={**WEB, "Host": "steward-api:8787"})
        assert r.status_code == 403
        assert client.post(path, json={}).status_code == 403
    assert client.get("/api/actions", headers={"Host": "steward-api:8787"}).status_code == 403
    assert action(aid)["status"] == "pending"
    assert approve(client, 9999, {}).status_code == 404
    assert reject(client, 9999).json() == {"detail": "action not found"}


def test_list_actions(client: TestClient) -> None:
    first, second = queue(client), queue(client, **BEC)
    third = queue(client)
    reject(client, third)
    pending = client.get("/api/actions").json()
    assert [a["id"] for a in pending] == [first, second]
    assert pending[1]["risk_reasons"][1] == "lookalike of acme-logistics.example"
    assert [a["id"] for a in client.get("/api/actions?status=all").json()] == [third, second, first]
    assert client.get("/api/actions?status=nope").status_code == 422
    assert set(pending[0]) == {
        "id",
        "created_at",
        "tool",
        "args_json",
        "preview",
        "risk",
        "risk_reasons",
        "status",
        "decided_at",
        "result",
    }


def test_files_write_refused_at_approve_when_path_became_unsafe(
    client: TestClient, tmp_path: Path
) -> None:
    aid = queue(client, "files_write", path="drafts/a.md", content="x")
    outside = tmp_path / "outside"
    outside.mkdir()
    (workspace() / "drafts").symlink_to(outside)
    r = approve(client, aid, {"confirm_high": True})
    assert r.status_code == 409 and r.json()["detail"] == "write refused: symlinks are not allowed"
    assert action(aid)["status"] == "pending" and list(outside.iterdir()) == []


def test_execute_time_safe_path_recheck(tmp_path: Path) -> None:
    # The window between claim and write: the executor checks safe_path again.
    from steward.gate import executor

    ws = workspace()
    ws.mkdir(parents=True, exist_ok=True)
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (ws / "late").symlink_to(outside)
    status, result, summary = executor._write_file({"path": "late/x.md", "content": "x"}, False)
    assert (status, result, summary) == (
        "failed",
        "write refused: symlinks are not allowed",
        "files_write → failed",
    )
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize(
    "sep", [" ", " ", "\x85", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\t", "\x00"]
)
def test_any_line_separator_or_control_in_subject_queues_nothing(
    client: TestClient, sep: str
) -> None:
    ok, out = call(client, "mail_send", **{**LEGIT, "subject": f"Re: INV-0042{sep}reminder"})
    assert not ok and "single-line" in out
    assert q("SELECT COUNT(*) AS n FROM actions")[0]["n"] == 0


def test_crlf_hidden_in_a_json_list_recipient_queues_nothing(client: TestClient) -> None:
    to = json.dumps([f"{RAHUL}\r\nBcc: x@evil.invalid"])  # the raw string has no real CR/LF
    assert "\r" not in to
    ok, out = call(client, "mail_send", to=to, subject="s", body="b")
    assert not ok and "single-line" in out
    assert q("SELECT COUNT(*) AS n FROM actions")[0]["n"] == 0


# --- M3 review regressions -------------------------------------------------------------------


def test_two_low_writes_to_one_new_path_never_silently_overwrite(client: TestClient) -> None:
    import anyio

    from steward.gate import executor

    first = queue(client, "files_write", path="notes/plan.md", content="version A\n")
    second = queue(client, "files_write", path="notes/plan.md", content="version B\n")
    claimed: list[dict[str, Any]] = []
    for aid in (first, second):  # both claimed while the file does not exist yet: both Low
        outcome = db.with_conn(lambda c, a=aid: executor.claim_approval(c, a, False))
        assert outcome.status == 200 and outcome.action and outcome.action["risk"] == "low"
        claimed.append(outcome.action)
    done: list[dict[str, Any]] = []

    async def run(a: dict[str, Any]) -> None:
        done.append(await executor.execute(a))

    async def both() -> None:
        async with anyio.create_task_group() as tg:
            for a in claimed:
                tg.start_soon(run, a)

    anyio.run(both)
    assert sorted(d["status"] for d in done) == ["executed", "failed"]
    loser = next(d for d in done if d["status"] == "failed")
    assert loser["result"] == (
        "write refused: the file appeared after approval; queue it again to overwrite"
    )
    winner = next(d for d in done if d["status"] == "executed")
    expected = json.loads(winner["args_json"])["content"]
    assert (workspace() / "notes" / "plan.md").read_text() == expected


def test_error_after_a_real_send_still_finishes_the_row(
    client: TestClient, redirect: type[FakeSMTP], monkeypatch: pytest.MonkeyPatch
) -> None:
    from steward.gate import executor

    def broken_insert(*args: Any, **kwargs: Any) -> int:
        raise RuntimeError("ledger down")

    monkeypatch.setattr(executor.store, "insert", broken_insert)
    aid = queue(client)
    r = approve(client, aid, {})
    assert r.status_code == 200 and r.json()["action"]["status"] == "executed"
    assert redirect.attempts == 1 and action(aid)["status"] == "executed"
    assert [a["summary"] for a in audit("action_executed")] == ["mail_send → sent"]


def test_error_before_any_send_fails_the_row_cleanly(
    client: TestClient, redirect: type[FakeSMTP], monkeypatch: pytest.MonkeyPatch
) -> None:
    from steward.gate import executor

    def broken(*args: Any, **kwargs: Any) -> int:
        raise RuntimeError("disk full")

    monkeypatch.setattr(executor, "_store_sent", broken)
    aid = queue(client)
    a = approve(client, aid, {}).json()["action"]
    assert (a["status"], a["result"]) == ("failed", "execution error: RuntimeError")
    assert redirect.attempts == 0


def test_mail_ledger_row_survives_a_shield_error_without_storing_the_body(
    client: TestClient, redirect: type[FakeSMTP], monkeypatch: pytest.MonkeyPatch
) -> None:
    from steward.gate import executor

    def broken(self: Any, request: Any) -> Any:
        raise RuntimeError("shield down")

    monkeypatch.setattr(executor.Shield, "outbound", broken)
    aid = queue(client)
    assert approve(client, aid, {}).json()["action"]["status"] == "executed"
    (eg,) = mail_egress()
    assert json.loads(eg["request_redacted"]) == {
        "message_id": MESSAGE_ID.format(aid),
        "copy": "not stored (RuntimeError)",
    }


def test_failed_send_records_its_real_latency(client: TestClient, redirect: type[FakeSMTP]) -> None:
    redirect.fail, redirect.delay = TimeoutError("timed out"), 0.05
    approve(client, queue(client), {})
    assert mail_egress()[0]["latency_ms"] >= 50
