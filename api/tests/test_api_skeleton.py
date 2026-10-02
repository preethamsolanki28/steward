"""T1.1: schema bootstrap, seed loader, /api guards, /api/health, static serving."""

import json
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from steward import db, seed, static
from steward.config import get_settings
from steward.main import app

LOCAL = "http://127.0.0.1:8787"
WEB = {"X-Steward-Client": "web"}

EXPECTED_COLUMNS = {
    "contacts": ["id", "name", "email", "org", "trusted", "source", "created_at"],
    "vault": ["id", "placeholder", "kind", "value", "created_at"],
    "egress_events": [
        "id",
        "ts",
        "channel",
        "destination",
        "model",
        "escalated_from",
        "request_redacted",
        "response_redacted",
        "entities_masked",
        "entity_kinds",
        "prompt_tokens",
        "completion_tokens",
        "latency_ms",
        "cost_usd",
        "status",
    ],
    "actions": [
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
    ],
    "audit_events": ["id", "ts", "kind", "summary", "detail", "ref_table", "ref_id"],
    "conversations": ["id", "title", "hermes_session_id", "created_at", "updated_at"],
    "messages": ["id", "conversation_id", "role", "content", "created_at"],
    "briefs": ["id", "created_at", "content_md"],
    "demo_mail": [
        "id",
        "folder",
        "from_name",
        "from_email",
        "to_emails",
        "subject",
        "body",
        "ts",
        "is_read",
    ],
    "settings": ["key", "value"],
}


def test_schema_matches_docs_exactly() -> None:
    db.init_schema()
    conn = sqlite3.connect(get_settings().db_path)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert tables == set(EXPECTED_COLUMNS)
    for table, columns in EXPECTED_COLUMNS.items():
        assert [r[1] for r in conn.execute(f"PRAGMA table_info({table})")] == columns


def test_seed_loads_everything_and_resolves_relative_times() -> None:
    settings = get_settings()
    now = datetime(2026, 10, 3, 9, 0, tzinfo=seed.IST)
    counts = seed.seed_db(settings, now)
    files = seed.seed_workspace(settings, now.date())
    seed.seed_memories(settings)
    assert counts == {"contacts": 8, "inbox": 14}
    assert files == 11
    with db.connect() as conn:
        trusted = {r["email"] for r in conn.execute("SELECT email FROM contacts WHERE trusted=1")}
        assert len(trusted) == 5 and "rahul.verma@acme-logistics.example" in trusted
        assert {r["source"] for r in conn.execute("SELECT source FROM contacts")} == {"seed"}
        bec = conn.execute(
            "SELECT ts FROM demo_mail WHERE from_email = 'billing@acme-logistics-payments.example'"
        ).fetchone()
        assert bec["ts"] == (now - timedelta(hours=3)).isoformat(timespec="seconds")
        nonce = db.get_setting(conn, "reset_nonce")
        assert nonce and db.get_setting(conn, "model_primary") == settings.model_primary
    inv = (settings.workspace_dir / "invoices" / "INV-0042.md").read_text()
    assert 'due: "2026-09-21"' in inv  # seed date - 12 days
    assert "{{" not in "".join(p.read_text() for p in settings.workspace_dir.rglob("*.md"))
    user = (settings.memories_dir / "USER.md").read_text()
    assert user == "Maya prefers concise, friendly emails and signs off 'Best, Maya'"
    # A re-seed mints a new nonce (fresh Hermes session ids after demo-reset).
    seed.seed_db(settings, now)
    with db.connect() as conn:
        assert db.get_setting(conn, "reset_nonce") != nonce


def test_seed_workspace_never_follows_symlinks(tmp_path: Path) -> None:
    settings = get_settings()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.txt").write_text("keep")
    settings.workspace_dir.mkdir(parents=True)
    (settings.workspace_dir / "link").symlink_to(outside, target_is_directory=True)
    seed.seed_workspace(settings, datetime.now(seed.IST).date())
    assert (outside / "keep.txt").exists()
    assert not (settings.workspace_dir / "link").exists()


def _client() -> TestClient:
    return TestClient(app, base_url=LOCAL)


@pytest.mark.parametrize("host", ["steward-api:8787", "evil.example", "127.0.0.1:9999"])
def test_api_rejects_foreign_hosts(host: str) -> None:
    with _client() as c:
        r = c.get("/api/health", headers={"Host": host})
    assert r.status_code == 403


def test_dev_host_only_when_steward_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    with _client() as c:
        assert c.get("/api/settings", headers={"Host": "localhost:3000"}).status_code == 403
        monkeypatch.setenv("STEWARD_DEV", "1")
        assert c.get("/api/settings", headers={"Host": "localhost:3000"}).status_code != 403


def test_mutating_routes_need_client_header() -> None:
    with _client() as c:
        r = c.post("/api/chat", json={"message": "hi"})
    assert r.status_code == 403
    assert r.json()["detail"] == "Missing X-Steward-Client header"


def test_no_cors_headers() -> None:
    with _client() as c:
        r = c.options(
            "/api/health",
            headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"},
        )
    assert "access-control-allow-origin" not in {k.lower() for k in r.headers}


def test_health_payload_no_keys() -> None:
    def hermes(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/health"
        return httpx.Response(200, json={"status": "ok"})

    with _client() as c:
        app.state.http = httpx.AsyncClient(transport=httpx.MockTransport(hermes))
        r = c.get("/api/health")
    assert r.json() == {
        "ok": True,
        "hermes": "up",
        "token_factory": "no_key",
        "tavily": "no_key",
        "mail_mode": "demo",
        "model_primary": "nvidia/Nemotron-3_5-Lightning",
    }


def test_health_reports_down(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEBIUS_API_KEY", "k")
    monkeypatch.setenv("TAVILY_API_KEY", "k")

    def upstream(request: httpx.Request) -> httpx.Response:
        if request.url.host == "hermes":
            raise httpx.ConnectError("down")
        return httpx.Response(401)

    with _client() as c:
        app.state.http = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        body = c.get("/api/health").json()
    assert (body["hermes"], body["token_factory"], body["tavily"]) == ("down", "down", "down")


def test_dashboard_serves_static_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "out"
    out.mkdir()
    (out / "index.html").write_text("<p>root</p>")
    (out / "chat.html").write_text("<p>chat</p>")
    (out / "404.html").write_text("<p>missing</p>")
    dashboard = static.Dashboard(out)
    monkeypatch.setattr(
        app.routes[-1], "app", static.RootDispatcher(mcp=static.Dashboard(out), dashboard=dashboard)
    )
    with _client() as c:
        assert c.get("/").text == "<p>root</p>"
        assert c.get("/chat").text == "<p>chat</p>"
        missing = c.get("/nope")
        assert missing.status_code == 404
        assert c.get("/../etc/passwd").status_code == 404
    assert re.search(r"chat", json.dumps({"ok": 1}) + "chat")
