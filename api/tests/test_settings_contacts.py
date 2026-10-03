"""T4.5: GET /api/settings and GET /api/contacts (docs/02 §6), read-only, for the System tab."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from steward import db, seed
from steward.config import get_settings
from steward.main import app

LOCAL = "http://127.0.0.1:8787"
WEB = {"X-Steward-Client": "web"}
ZDR = "ZDR is an org-level setting in your Token Factory profile; Steward cannot verify it"


@pytest.fixture
def seeded() -> None:
    seed.seed_db(get_settings(), datetime(2026, 10, 3, 9, 0, tzinfo=seed.IST))


def test_settings_falls_back_to_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_PRIMARY", "nvidia/nemotron-3-super-120b-a12b")
    monkeypatch.setenv("MODEL_FALLBACK", "nvidia/Nemotron-3_5-Lightning")
    monkeypatch.setenv("REASONING_EFFORT", "low")
    monkeypatch.setenv("MAIL_MODE", "demo")
    with TestClient(app, base_url=LOCAL) as c:
        r = c.get("/api/settings")
    assert r.status_code == 200
    assert r.json() == {
        "model_primary": "nvidia/nemotron-3-super-120b-a12b",
        "model_fallback": "nvidia/Nemotron-3_5-Lightning",
        "reasoning_effort": "low",
        "mail_mode": "demo",
        "shield": "on",
        "zdr_note": ZDR,
    }


def test_settings_table_wins_over_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """The System tab shows what the proxy uses, and the proxy reads the table first."""
    monkeypatch.setenv("MODEL_PRIMARY", "nvidia/nemotron-3-super-120b-a12b")
    monkeypatch.setenv("REASONING_EFFORT", "low")
    with TestClient(app, base_url=LOCAL) as c:
        with db.connect() as conn:
            db.set_setting(conn, "model_primary", "nvidia/Nemotron-3_5-Lightning")
            db.set_setting(conn, "reasoning_effort", "medium")
        body = c.get("/api/settings").json()
    assert body["model_primary"] == "nvidia/Nemotron-3_5-Lightning"
    assert body["reasoning_effort"] == "medium"
    assert "model_fallback_2" not in body


def test_contacts_lists_every_row_in_the_contact_shape(seeded: None) -> None:
    with TestClient(app, base_url=LOCAL) as c:
        r = c.get("/api/contacts")
    assert r.status_code == 200
    rows = r.json()
    fields = {"id", "name", "email", "org", "trusted", "source", "created_at"}
    assert rows and set(rows[0]) == fields
    trusted = {(x["name"], x["org"]) for x in rows if x["trusted"] == 1}
    assert ("Rahul Verma", "Acme Logistics") in trusted
    assert all(x["email"].endswith(".example") for x in rows)


def test_contacts_include_untrusted_mail_upserts(seeded: None) -> None:
    with TestClient(app, base_url=LOCAL) as c:
        with db.connect() as conn:
            conn.execute(
                "INSERT INTO contacts (name, email, org, trusted, source, created_at)"
                " VALUES (NULL, 'someone@unknown.example', NULL, 0, 'mail', ?)",
                (db.now_iso(),),
            )
        rows = c.get("/api/contacts").json()
    upsert = next(x for x in rows if x["email"] == "someone@unknown.example")
    assert upsert["name"] is None and upsert["org"] is None and upsert["trusted"] == 0


@pytest.mark.parametrize("path", ["/api/settings", "/api/contacts"])
def test_read_only(path: str, seeded: None) -> None:
    with TestClient(app, base_url=LOCAL) as c:
        for method in ("post", "put", "delete", "patch"):
            r = getattr(c, method)(path, headers=WEB)
            assert r.status_code in (404, 405), (method, r.status_code)
        before = c.get(path).json()
        assert c.get(path).json() == before


@pytest.mark.parametrize("path", ["/api/settings", "/api/contacts"])
def test_host_guard(path: str) -> None:
    with TestClient(app, base_url=LOCAL) as c:
        assert c.get(path, headers={"Host": "evil.example"}).status_code == 403
