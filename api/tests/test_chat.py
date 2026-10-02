"""T1.6: /api/chat, conversations, Hermes session ids, error mapping, memory_edit audit."""

import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from steward import db
from steward.config import get_settings
from steward.main import app

LOCAL = "http://127.0.0.1:8787"
WEB = {"X-Steward-Client": "web"}


def _setup() -> None:
    db.init_schema()
    with db.connect() as conn:
        db.set_setting(conn, "reset_nonce", "n0nce")
    mem = get_settings().memories_dir
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "MEMORY.md").write_text("General entry")
    (mem / "USER.md").write_text("Maya prefers concise, friendly emails and signs off 'Best, Maya'")


def _client(handler) -> TestClient:
    _setup()
    client = TestClient(app, base_url=LOCAL)
    client.__enter__()
    app.state.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return client


def _ok(text: str):
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200, json={"choices": [{"message": {"content": text}, "finish_reason": "stop"}]}
        )

    return handler, seen


def test_new_conversation_session_header_and_only_new_message() -> None:
    handler, seen = _ok("Draft for INV-0042")
    c = _client(handler)
    try:
        r = c.post("/api/chat", json={"message": "Chase the Acme invoice"}, headers=WEB)
        assert r.status_code == 200
        body = r.json()
        assert body["reply"] == "Draft for INV-0042" and body["conversation_id"] == 1
        req = seen[0]
        assert req.url == "http://hermes:8642/v1/chat/completions"
        assert req.headers["x-hermes-session-id"] == "steward-n0nce-1"
        assert req.headers["authorization"] == "Bearer test-hermes-key"
        sent = json.loads(req.content)
        assert sent["model"] == "hermes-agent" and sent["stream"] is False
        assert sent["messages"] == [{"role": "user", "content": "Chase the Acme invoice"}]

        r2 = c.post(
            "/api/chat", json={"conversation_id": 1, "message": "Make it shorter"}, headers=WEB
        )
        assert r2.json()["conversation_id"] == 1
        assert seen[1].headers["x-hermes-session-id"] == "steward-n0nce-1"
        assert json.loads(seen[1].content)["messages"] == [
            {"role": "user", "content": "Make it shorter"}
        ]

        r3 = c.post("/api/chat", json={"message": "New topic"}, headers=WEB)
        assert seen[2].headers["x-hermes-session-id"] == "steward-n0nce-2"
        assert r3.json()["conversation_id"] == 2

        convs = c.get("/api/conversations").json()
        assert [x["id"] for x in convs] == [2, 1]
        detail = c.get("/api/conversations/1").json()
        assert [m["role"] for m in detail["messages"]] == ["user", "assistant", "user", "assistant"]
        assert c.get("/api/conversations/99").status_code == 404
        assert (
            c.post(
                "/api/chat", json={"conversation_id": 99, "message": "x"}, headers=WEB
            ).status_code
            == 404
        )
    finally:
        c.__exit__(None, None, None)


@pytest.mark.parametrize(
    ("response", "status", "detail"),
    [
        (httpx.TimeoutException("slow"), 504, "Still working — check Approvals and Activity"),
        (
            httpx.Response(502, json={"error": "agent_incomplete"}),
            502,
            "Model unavailable — this turn did not complete",
        ),
        (
            httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {"content": "Provider said: HTTP 401"},
                            "finish_reason": "error",
                        }
                    ],
                    "hermes": {"failed": True},
                },
            ),
            502,
            "Model unavailable — this turn did not complete",
        ),
        (httpx.ConnectError("hermes down"), 502, "Model unavailable — this turn did not complete"),
    ],
)
def test_error_mapping(response, status: int, detail: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if isinstance(response, Exception):
            raise response
        return response

    c = _client(handler)
    try:
        r = c.post("/api/chat", json={"message": "hi"}, headers=WEB)
    finally:
        c.__exit__(None, None, None)
    assert r.status_code == status and r.json()["detail"] == detail
    with db.connect() as conn:
        roles = [x["role"] for x in conn.execute("SELECT role FROM messages")]
    assert roles == ["user"]  # no assistant message for a turn that did not complete


def test_memory_change_during_turn_is_audited_with_diff() -> None:
    mem: Path = get_settings().memories_dir

    def handler(request: httpx.Request) -> httpx.Response:
        (mem / "USER.md").write_text(
            "Maya prefers concise, friendly emails and signs off 'Best, Maya'\n§\n"
            "Rahul at Acme likes short, formal emails."
        )
        return httpx.Response(200, json={"choices": [{"message": {"content": "Noted."}}]})

    c = _client(handler)
    try:
        c.post(
            "/api/chat",
            json={"message": "FYI — Rahul at Acme likes short, formal emails."},
            headers=WEB,
        )
    finally:
        c.__exit__(None, None, None)
    with db.connect() as conn:
        rows = db.rows(conn.execute("SELECT * FROM audit_events WHERE kind='memory_edit'"))
    assert len(rows) == 1 and rows[0]["summary"] == "Memory changed by Steward"
    assert "+Rahul at Acme likes short, formal emails." in rows[0]["detail"]
    assert "a/USER.md" in rows[0]["detail"]


def test_no_memory_audit_without_change() -> None:
    handler, _ = _ok("OK")
    c = _client(handler)
    try:
        c.post("/api/chat", json={"message": "hi"}, headers=WEB)
    finally:
        c.__exit__(None, None, None)
    with db.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0] == 0
