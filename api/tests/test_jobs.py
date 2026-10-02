"""T1.4: idempotent morning-brief job registration against a mocked Hermes Jobs API."""

import json

import anyio
import httpx
import pytest

from steward import db, jobs


class FakeHermes:
    def __init__(self, jobs_: list[dict] | None = None) -> None:
        self.jobs = list(jobs_ or [])
        self.posts: list[dict] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-hermes-key"
        if request.method == "GET" and request.url.path == "/api/jobs":
            return httpx.Response(200, json={"jobs": self.jobs})
        if request.method == "POST" and request.url.path == "/api/jobs":
            body = json.loads(request.content)
            self.posts.append(body)
            job = {"id": f"job{len(self.jobs) + 1}", **body}
            self.jobs.append(job)
            return httpx.Response(200, json={"job": job})
        return httpx.Response(404)


def _ensure(fake: FakeHermes) -> str:
    async def go() -> str:
        async with httpx.AsyncClient(transport=httpx.MockTransport(fake)) as client:
            return await jobs.ensure_morning_brief_job(client)

    return anyio.run(go)


def _stored() -> str | None:
    db.init_schema()
    with db.connect() as conn:
        return db.get_setting(conn, "morning_brief_job_id")


def test_creates_job_when_missing_and_stores_id() -> None:
    db.init_schema()
    fake = FakeHermes()
    assert _ensure(fake) == "job1"
    assert fake.posts == [
        {
            "name": "morning-brief",
            "schedule": "0 8 * * *",
            "skills": ["morning-brief"],
            "prompt": "Run the morning-brief skill.",
            "deliver": "local",
        }
    ]
    assert _stored() == "job1"


def test_restart_is_idempotent() -> None:
    db.init_schema()
    fake = FakeHermes()
    _ensure(fake)
    _ensure(fake)
    _ensure(fake)
    assert len(fake.posts) == 1 and len(fake.jobs) == 1


def test_reuses_existing_job_by_name() -> None:
    db.init_schema()
    fake = FakeHermes(
        [{"id": "other", "name": "something-else"}, {"id": "abc123", "name": "morning-brief"}]
    )
    assert _ensure(fake) == "abc123"
    assert fake.posts == [] and _stored() == "abc123"


def test_hermes_down_raises_so_startup_retries() -> None:
    db.init_schema()

    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("hermes not up yet")

    async def go() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(down)) as client:
            await jobs.ensure_morning_brief_job(client)

    with pytest.raises(httpx.ConnectError):
        anyio.run(go)
    assert _stored() is None
