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
