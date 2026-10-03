"""T3.5: Approval Gate end to end against a real Uvicorn server (no network, no secrets).

- Legit chase: mail_send to the trusted Acme contact -> Low -> approve -> exactly one send.
- BEC: mail_send to billing@acme-logistics-payments.example -> High "lookalike of
  acme-logistics.example" -> reject -> nothing sent.
- Concurrent approvals of the same action -> exactly one send.

The MCP tool is called directly with fixed arguments (docs/04 T3.5), so no Token Factory call
runs; SMTP is the FakeSMTP stub, slowed down so concurrent requests really overlap.
"""

import asyncio
import json
import socket
import threading
import time
from collections.abc import Iterator
from datetime import datetime
from typing import Any

import httpx
import pytest
import uvicorn

from steward import db, seed
from steward.config import get_settings
from steward.main import app
from tests.conftest import FakeSMTP

API = {"Host": "127.0.0.1:8787", "X-Steward-Client": "web"}
MCP = {
    "Authorization": "Bearer test-mcp-token",
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
}
RAHUL = "rahul.verma@acme-logistics.example"
BEC_TO = "billing@acme-logistics-payments.example"
LEGIT = {
    "to": [RAHUL],
    "subject": "INV-0042: payment reminder",
    "body": "Dear Rahul,\n\nA reminder that INV-0042 for $4,800 was due on 2026-09-20.\n\n"
    "Best, Maya",
}
BEC = {
    "to": [BEC_TO],
    "subject": "Open invoices",
    "body": "Hello,\n\nAs requested, the open invoices: INV-0042, INV-0043.\n\nBest, Maya",
}


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def live(fake_smtp: type[FakeSMTP], monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    monkeypatch.setenv("DEMO_MAIL_REDIRECT", "team-inbox@team.example")
    settings = get_settings()
    now = datetime(2026, 10, 3, 9, 0, tzinfo=seed.IST)
    seed.seed_db(settings, now)
    seed.seed_workspace(settings, now.date())
    port = _free_port()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, workers=1, log_level="warning")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 10
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    assert server.started
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=10)


def mail_send(base: str, args: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "mail_send", "arguments": args},
    }
    r = httpx.post(f"{base}/mcp", content=json.dumps(payload), headers=MCP, timeout=10)
    result = r.json()["result"]
    assert not result.get("isError"), result
    return result["structuredContent"]


def count(sql: str) -> int:
    return db.with_conn(lambda conn: conn.execute(sql).fetchone()[0])


def ledger_and_audit() -> dict[str, int]:
    return {
        "demo_mail_sent": count("SELECT COUNT(*) FROM demo_mail WHERE folder = 'sent'"),
        "mail_egress": count("SELECT COUNT(*) FROM egress_events WHERE channel = 'mail'"),
        "decided": count("SELECT COUNT(*) FROM audit_events WHERE kind = 'action_decided'"),
        "executed": count("SELECT COUNT(*) FROM audit_events WHERE kind = 'action_executed'"),
    }


async def _post_all(base: str, requests: list[tuple[str, dict[str, Any]]]) -> list[httpx.Response]:
    async with httpx.AsyncClient(timeout=30) as client:
        return await asyncio.gather(
            *(client.post(f"{base}{path}", json=body, headers=API) for path, body in requests)
        )


def test_legit_chase_low_approve_exactly_one_send(live: str, fake_smtp: type[FakeSMTP]) -> None:
    queued = mail_send(live, LEGIT)
    assert (queued["status"], queued["risk"]) == ("pending", "low")
    r = httpx.post(f"{live}/api/actions/{queued['action_id']}/approve", json={}, headers=API)
    assert r.status_code == 200 and r.json()["action"]["status"] == "executed"
    assert fake_smtp.attempts == 1 and len(fake_smtp.sent) == 1
    assert fake_smtp.sent[0]["Message-ID"] == (
        f"<steward-action-{queued['action_id']}@rao-consulting.example>"
    )
    assert ledger_and_audit() == {
        "demo_mail_sent": 1,
        "mail_egress": 1,
        "decided": 1,
        "executed": 1,
    }


def test_bec_high_lookalike_reject_nothing_sent(live: str, fake_smtp: type[FakeSMTP]) -> None:
    queued = mail_send(live, BEC)
    assert queued["risk"] == "high"
    aid = queued["action_id"]
    listed = httpx.get(f"{live}/api/actions", headers=API).json()
    assert listed[0]["risk_reasons"] == [
        f"{BEC_TO} is not a trusted contact",
        "lookalike of acme-logistics.example",
    ]
    blocked = httpx.post(f"{live}/api/actions/{aid}/approve", json={}, headers=API)
    assert blocked.status_code == 409 and blocked.json()["action"]["status"] == "pending"
    r = httpx.post(f"{live}/api/actions/{aid}/reject", headers=API)
    assert r.status_code == 200 and r.json()["action"]["status"] == "rejected"
    assert fake_smtp.attempts == 0
    assert ledger_and_audit() == {
        "demo_mail_sent": 0,
        "mail_egress": 0,
        "decided": 1,
        "executed": 0,
    }


@pytest.mark.parametrize("approvers", [2, 8])
def test_concurrent_double_approve_sends_once(
    live: str, fake_smtp: type[FakeSMTP], approvers: int
) -> None:
    fake_smtp.delay = 0.5  # the first send is still in flight when the others arrive
    aid = mail_send(live, LEGIT)["action_id"]
    path = f"/api/actions/{aid}/approve"
    responses = asyncio.run(_post_all(live, [(path, {"confirm_high": True})] * approvers))
    codes = sorted(r.status_code for r in responses)
    assert codes == [200] + [409] * (approvers - 1), [r.text for r in responses]
    assert all(
        r.json()["detail"] == "Action already decided" for r in responses if r.status_code == 409
    )
    assert fake_smtp.attempts == 1 and len(fake_smtp.sent) == 1
    assert ledger_and_audit() == {
        "demo_mail_sent": 1,
        "mail_egress": 1,
        "decided": 1,
        "executed": 1,
    }
    final = httpx.get(f"{live}/api/actions?status=all", headers=API).json()[0]
    assert final["status"] == "executed"


def test_concurrent_approve_and_reject_exactly_one_wins(
    live: str, fake_smtp: type[FakeSMTP]
) -> None:
    fake_smtp.delay = 0.3
    aid = mail_send(live, LEGIT)["action_id"]
    approve_r, reject_r = asyncio.run(
        _post_all(live, [(f"/api/actions/{aid}/approve", {}), (f"/api/actions/{aid}/reject", {})])
    )
    assert sorted([approve_r.status_code, reject_r.status_code]) == [200, 409]
    state = httpx.get(f"{live}/api/actions?status=all", headers=API).json()[0]["status"]
    if approve_r.status_code == 200:
        assert state == "executed" and fake_smtp.attempts == 1
    else:
        assert state == "rejected" and fake_smtp.attempts == 0
    assert ledger_and_audit()["decided"] == 1
