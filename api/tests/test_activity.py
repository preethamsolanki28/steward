"""T3.4: GET /api/activity?after_id= (audit_events, oldest first)."""

from fastapi.testclient import TestClient

from steward import db
from steward.main import app
from steward.routers import api

LOCAL = "http://127.0.0.1:8787"


def _audit(n: int) -> list[int]:
    db.init_schema()
    return db.with_conn(
        lambda conn: [
            db.audit(conn, "tool_call", f"mcp__steward__files_read #{i}") for i in range(n)
        ]
    )


def test_activity_pages_forward_in_id_order() -> None:
    ids = _audit(5)
    with TestClient(app, base_url=LOCAL) as c:
        everything = c.get("/api/activity").json()
        assert [e["id"] for e in everything] == ids
        assert set(everything[0]) == {
            "id",
            "ts",
            "kind",
            "summary",
            "detail",
            "ref_table",
            "ref_id",
        }
        assert [e["id"] for e in c.get(f"/api/activity?after_id={ids[2]}").json()] == ids[3:]
        assert c.get(f"/api/activity?after_id={ids[-1]}").json() == []
        assert c.get("/api/activity?after_id=-1").status_code == 422


def test_activity_is_capped_per_page(monkeypatch) -> None:
    monkeypatch.setattr(api, "ACTIVITY_PAGE", 2)
    ids = _audit(3)
    with TestClient(app, base_url=LOCAL) as c:
        assert [e["id"] for e in c.get("/api/activity").json()] == ids[:2]
        assert [e["id"] for e in c.get(f"/api/activity?after_id={ids[1]}").json()] == ids[2:]


def test_activity_is_behind_the_host_guard() -> None:
    _audit(1)
    with TestClient(app, base_url="http://steward-api:8787") as c:
        assert c.get("/api/activity").status_code == 403
