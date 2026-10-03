"""T0.1: no generated docs routes (the full /api/health payload is tested in test_api_skeleton)."""

from fastapi.testclient import TestClient

from steward.main import app


def test_no_generated_docs_routes() -> None:
    # Unknown paths fall through to the static dashboard (404) or the /mcp guard, never docs.
    with TestClient(app, base_url="http://127.0.0.1:8787") as client:
        for path in ("/docs", "/redoc", "/openapi.json"):
            response = client.get(path)
            assert response.status_code in (401, 404)
            assert "openapi" not in response.text.lower()


# --- Tavily: connector usability with a last-known-good state (pre-M4 fix) -------------------

import types  # noqa: E402

import anyio  # noqa: E402
import httpx  # noqa: E402
import pytest  # noqa: E402

from steward import health  # noqa: E402


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def monotonic(self) -> float:
        return self.now


class Usage:
    """A scripted Tavily /usage endpoint that counts calls."""

    def __init__(self, *responses: httpx.Response | Exception) -> None:
        self.responses, self.calls = list(responses), 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/usage"
        self.calls += 1
        nxt = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        if isinstance(nxt, Exception):
            raise nxt
        return nxt


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    c = Clock()
    monkeypatch.setattr(health, "time", types.SimpleNamespace(monotonic=c.monotonic))
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    return c


def status(usage: Usage) -> str:
    async def run() -> str:
        async with httpx.AsyncClient(transport=httpx.MockTransport(usage)) as client:
            return await health.tavily_status(client)

    return anyio.run(run)


def r429(retry_after: str = "60") -> httpx.Response:
    return httpx.Response(429, headers={"retry-after": retry_after}, json={"detail": "slow down"})


def test_up_is_cached_so_polling_does_not_hit_the_rate_limit(clock: Clock) -> None:
    usage = Usage(httpx.Response(200, json={}))
    for _ in range(30):  # the compose healthcheck polls every 10 s: 5 minutes of polls
        assert status(usage) == "up"
        clock.now += 10
    assert usage.calls == 1
    clock.now += 1
    assert status(usage) == "up" and usage.calls == 2


def test_rate_limit_keeps_a_recent_up_and_waits_for_retry_after(clock: Clock) -> None:
    usage = Usage(httpx.Response(200, json={}), r429("60"))
    assert status(usage) == "up"
    clock.now += health.TAVILY_UP_TTL_S + 1
    assert status(usage) == "up" and usage.calls == 2  # 429, but known good 301 s ago
    clock.now += 59
    assert status(usage) == "up" and usage.calls == 2  # no probe before Retry-After


def test_rate_limit_without_a_recent_up_is_down(clock: Clock) -> None:
    assert status(Usage(r429())) == "down"


def test_known_good_state_expires(clock: Clock) -> None:
    usage = Usage(httpx.Response(200, json={}), r429("60"))
    status(usage)
    clock.now += health.TAVILY_KEEP_UP_S + 1
    assert status(usage) == "down"


@pytest.mark.parametrize("code", [401, 403])
def test_refused_key_is_down_and_forgets_the_last_good_state(clock: Clock, code: int) -> None:
    usage = Usage(httpx.Response(200, json={}), httpx.Response(code), r429())
    status(usage)
    clock.now += health.TAVILY_UP_TTL_S + 1
    assert status(usage) == "down"
    clock.now += health.TAVILY_DOWN_TTL_S + 1
    assert status(usage) == "down"  # a 429 no longer revives the forgotten 'up'


@pytest.mark.parametrize(
    "failure", [httpx.ConnectError("no route"), httpx.ReadTimeout("slow"), httpx.Response(503)]
)
def test_connection_failure_or_server_error_is_down(clock: Clock, failure) -> None:
    usage = Usage(failure)
    assert status(usage) == "down"
    clock.now += health.TAVILY_DOWN_TTL_S - 1
    assert status(usage) == "down" and usage.calls == 1


def test_a_real_search_counts_as_evidence(clock: Clock) -> None:
    health.note_tavily(200)
    usage = Usage(r429())
    assert status(usage) == "up" and usage.calls == 0
    health.note_tavily(401)
    assert status(usage) == "down"


def test_no_key_never_probes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    usage = Usage(httpx.Response(200, json={}))
    assert status(usage) == "no_key" and usage.calls == 0


def test_a_kept_up_never_outlives_the_known_good_window(clock: Clock) -> None:
    usage = Usage(httpx.Response(200, json={}), r429("900"))
    status(usage)  # good at t0
    clock.now += 800
    assert status(usage) == "up" and usage.calls == 2  # 429 at t0+800, Retry-After 900
    clock.now += 99
    assert status(usage) == "up" and usage.calls == 2  # t0+899: still inside 15 minutes
    clock.now += 2
    assert status(usage) == "down" and usage.calls == 3  # t0+901: re-probed, no good state
