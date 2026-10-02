"""T1.7: /api/briefs/latest, /api/skills, POST /api/skills/morning-brief/run."""

from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from steward import db, jobs
from steward.main import app
from steward.routers import api

LOCAL = "http://127.0.0.1:8787"
WEB = {"X-Steward-Client": "web"}
REPO_SKILLS = Path(__file__).resolve().parents[2] / "skills"


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(api, "SKILLS_DIR", REPO_SKILLS)
    monkeypatch.setattr(jobs, "_last_manual_trigger", None)
    db.init_schema()
    seen: list[httpx.Request] = []

    def hermes(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.method == "GET" and request.url.path == "/api/jobs/job1":
            return httpx.Response(
                200,
                json={
                    "job": {
                        "id": "job1",
                        "last_run_at": "2026-10-03T08:00:41+05:30",
                        "last_status": "ok",
                        "next_run_at": "2026-10-04T08:00:00+05:30",
                        "prompt": "x",
                    }
                },
            )
        if request.method == "POST" and request.url.path == "/api/jobs/job1/run":
            return httpx.Response(200, json={"job": {"id": "job1"}})
        return httpx.Response(404)

    with TestClient(app, base_url=LOCAL) as c:
        app.state.http = httpx.AsyncClient(transport=httpx.MockTransport(hermes))
        yield c, seen


def test_skills_lists_both_and_only_brief_runnable(calls) -> None:
    c, _ = calls
    skills = c.get("/api/skills").json()
    assert [(s["name"], s["runnable"]) for s in skills] == [
        ("invoice-chase", False),
        ("morning-brief", True),
    ]
    assert all(s["description"] for s in skills)


def test_briefs_latest_empty(calls) -> None:
    c, _ = calls
    assert c.get("/api/briefs/latest").json() == {"brief": None, "job": None}


def test_briefs_latest_with_brief_and_job_status(calls) -> None:
    c, _ = calls
    with db.connect() as conn:
        db.set_setting(conn, "morning_brief_job_id", "job1")
        conn.execute("INSERT INTO briefs (created_at, content_md) VALUES ('t1', '# Old')")
        conn.execute("INSERT INTO briefs (created_at, content_md) VALUES ('t2', '# New')")
    body = c.get("/api/briefs/latest").json()
    assert body["brief"] == {"id": 2, "created_at": "t2", "content_md": "# New"}
    assert body["job"] == {
        "last_run_at": "2026-10-03T08:00:41+05:30",
        "last_status": "ok",
        "next_run_at": "2026-10-04T08:00:00+05:30",
    }


def test_run_now_needs_registered_job(calls) -> None:
    c, seen = calls
    r = c.post("/api/skills/morning-brief/run", headers=WEB)
    assert r.status_code == 503 and seen == []


def test_run_now_calls_hermes_run_and_marks_manual_trigger(calls) -> None:
    c, seen = calls
    with db.connect() as conn:
        db.set_setting(conn, "morning_brief_job_id", "job1")
    assert jobs.skill_run_summary() == "morning-brief · scheduled run"
    assert c.post("/api/skills/morning-brief/run").status_code == 403  # no client header
    r = c.post("/api/skills/morning-brief/run", headers=WEB)
    assert r.status_code == 200 and r.json() == {"ok": True}
    assert (seen[-1].method, seen[-1].url.path) == ("POST", "/api/jobs/job1/run")
    assert seen[-1].headers["authorization"] == "Bearer test-hermes-key"
    assert jobs.skill_run_summary() == "morning-brief · run now"
