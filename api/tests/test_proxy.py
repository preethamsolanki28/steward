"""T2.2/T2.3: the /v1 Privacy Shield proxy (no network: Token Factory is a MockTransport)."""

import json
from datetime import datetime

import httpx
import pytest
from fastapi.testclient import TestClient

from steward import db, seed
from steward.config import get_settings
from steward.main import app
from steward.routers import proxy
from steward.shield import Shield

PROXY_KEY = "test-proxy-key"
NEBIUS_KEY = "nebius-test-key-123456"
AUTH = {"Authorization": f"Bearer {PROXY_KEY}"}
LIGHTNING = "nvidia/Nemotron-3_5-Lightning"
SUPER = "nvidia/nemotron-3-super-120b-a12b"
NANO = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"

CHASE = {
    "model": "steward-auto",
    "stream": False,
    "messages": [
        {"role": "system", "content": "Memory: Maya prefers concise emails"},
        {"role": "user", "content": "Chase the Acme invoice"},
        {
            "role": "tool",
            "tool_call_id": "c1",
            "content": "INV-0042 attn. Rahul Verma rahul.verma@acme-logistics.example GSTIN "
            "29AAAPR4242M1ZD UPI mayarao@examplebank total $4,800 due 2026-09-20",
        },
    ],
    "tools": [
        {"type": "function", "function": {"name": "mcp__steward__files_read"}},
        {"type": "function", "function": {"name": "skill_manage"}},
    ],
}
RAW = [
    "Acme",
    "Rahul",
    "Verma",
    "rahul.verma",
    "29AAAPR4242M1ZD",
    "mayarao@examplebank",
    "$4,800",
    "Maya",
]


def completion(content: str | None = None, tool_args: dict | str | None = None) -> dict:
    message: dict = {"role": "assistant", "content": content}
    if tool_args is not None:
        args = tool_args if isinstance(tool_args, str) else json.dumps(tool_args)
        message["tool_calls"] = [
            {
                "id": "c2",
                "type": "function",
                "function": {"name": "mcp__steward__mail_search", "arguments": args},
            }
        ]
    return {
        "id": "x",
        "choices": [{"message": message, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 1000, "completion_tokens": 100},
    }


class Upstream:
    def __init__(self, *responses: httpx.Response | Exception) -> None:
        self.responses = list(responses)
        self.requests: list[dict] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == f"Bearer {NEBIUS_KEY}"
        self.requests.append(json.loads(request.content))
        r = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        if isinstance(r, Exception):
            raise r
        return r


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEBIUS_API_KEY", NEBIUS_KEY)
    seed.seed_db(get_settings(), datetime(2026, 10, 3, 9, 0, tzinfo=seed.IST))

    async def no_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(proxy.asyncio, "sleep", no_sleep)


def post(upstream: Upstream, body: dict = CHASE, path: str = "/v1/chat/completions"):
    with TestClient(app, base_url="http://steward-api:8787") as c:
        app.state.http = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        return c.post(path, json=body, headers=AUTH)


def ledger() -> list[dict]:
    with db.connect() as conn:
        return db.rows(conn.execute("SELECT * FROM egress_events ORDER BY id"))


def audit(kind: str) -> list[dict]:
    with db.connect() as conn:
        return db.rows(conn.execute("SELECT * FROM audit_events WHERE kind=? ORDER BY id", (kind,)))


def test_auth_stream_and_models(env: None) -> None:
    up = Upstream(httpx.Response(200, json=completion("hi")))
    with TestClient(app, base_url="http://steward-api:8787") as c:
        assert c.post("/v1/chat/completions", json=CHASE).status_code == 401
        assert c.get("/v1/models").status_code == 401
        assert c.get("/v1/models", headers=AUTH).json() == {
            "data": [{"id": "steward-auto", "context_length": 131072}]
        }
    r = post(up, {**CHASE, "stream": True})
    assert r.status_code == 400 and r.json()["error"]["code"] == "stream_not_supported"
    assert up.requests == []


def test_only_placeholders_leave_and_response_is_reidentified(env: None) -> None:
    up = Upstream(
        httpx.Response(
            200,
            json=completion(
                "Draft to [[PERSON_1]] for [[MONEY_1]]", tool_args={"query": "[[EMAIL_1]]"}
            ),
        )
    )
    r = post(up)
    assert r.status_code == 200
    sent = up.requests[0]
    flat = json.dumps(sent, ensure_ascii=False)
    for raw in RAW:
        assert raw not in flat, raw
    assert "INV-0042" in flat and "2026-09-20" in flat
    assert sent["model"] == LIGHTNING and sent["reasoning_effort"] == "low"
    assert sent["stream"] is False
    msg = r.json()["choices"][0]["message"]
    with db.connect() as conn:
        vault = dict(conn.execute("SELECT placeholder, value FROM vault").fetchall())
    assert msg["content"] == f"Draft to {vault['[[PERSON_1]]']} for {vault['[[MONEY_1]]']}"
    assert json.loads(msg["tool_calls"][0]["function"]["arguments"]) == {
        "query": vault["[[EMAIL_1]]"]
    }
    (row,) = ledger()
    assert (row["channel"], row["status"], row["model"]) == ("llm", "ok", LIGHTNING)
    assert row["destination"] == "api.tokenfactory.nebius.com"
    assert row["entities_masked"] == 7 and json.loads(row["entity_kinds"])["ACCOUNT"] == 2
    assert (row["prompt_tokens"], row["completion_tokens"]) == (1000, 100)
    assert row["cost_usd"] == pytest.approx(1000 / 1e6 * 0.06 + 100 / 1e6 * 0.24)
    for raw in RAW:
        assert raw not in row["request_redacted"]
    (eg,) = audit("egress")
    assert eg["summary"] == f"Nemotron 3.5 Lightning · {row['entities_masked']} identifiers masked"
    assert eg["ref_id"] == row["id"]


def test_tool_outside_allowlist_is_blocked(env: None) -> None:
    up = Upstream(httpx.Response(200, json=completion("hi")))
    body = {
        **CHASE,
        "tools": CHASE["tools"] + [{"type": "function", "function": {"name": "terminal"}}],
    }
    r = post(up, body)
    assert r.status_code == 400 and r.json()["error"]["code"] == "steward_policy_block"
    assert up.requests == []
    (row,) = ledger()
    assert row["status"] == "blocked" and "terminal" in row["request_redacted"]
    for raw in RAW:
        assert raw not in row["request_redacted"]
    assert audit("policy_block")[0]["summary"] == "Blocked: identifier would have left the Mac"


def test_secret_in_request_is_blocked_and_masked(
    env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("STEWARD_MCP_TOKEN", "mcp-token-secret-value-42")
    up = Upstream(httpx.Response(200, json=completion("hi")))
    body = {
        **CHASE,
        "messages": CHASE["messages"]
        + [{"role": "user", "content": "the token is mcp-token-secret-value-42 ok"}],
    }
    r = post(up, body)
    assert r.status_code == 400 and r.json()["error"]["code"] == "steward_policy_block"
    assert up.requests == []
    (row,) = ledger()
    assert row["status"] == "blocked" and "«BLOCKED:SECRET»" in row["request_redacted"]
    assert "mcp-token-secret-value-42" not in row["request_redacted"]
    assert len(audit("policy_block")) == 1


def test_identifier_in_unwalked_field_is_blocked(env: None) -> None:
    up = Upstream(httpx.Response(200, json=completion("hi")))
    body = {
        **CHASE,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "mcp__steward__files_read",
                    "description": "files for Rahul Verma",
                },
            }
        ],
    }
    r = post(up, body)
    assert r.status_code == 400 and up.requests == []
    assert "«BLOCKED:PERSON»" in ledger()[0]["request_redacted"]


def test_any_shield_error_fails_closed(env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(self, request):
        raise RuntimeError("detector crashed")

    monkeypatch.setattr(Shield, "outbound", boom)
    up = Upstream(httpx.Response(200, json=completion("hi")))
    r = post(up)
    assert r.status_code == 400 and r.json()["error"]["code"] == "steward_policy_block"
    assert up.requests == []
    (row,) = ledger()
    assert row["status"] == "blocked" and "Rahul" not in row["request_redacted"]


def test_other_v1_path_is_404_with_blocked_row(env: None) -> None:
    up = Upstream(httpx.Response(200, json={}))
    r = post(up, {"input": "Rahul Verma"}, path="/v1/responses")
    assert r.status_code == 404 and up.requests == []
    (row,) = ledger()
    assert row["status"] == "blocked"
    assert json.loads(row["request_redacted"]) == {"method": "POST", "path": "/v1/responses"}


def test_retry_once_on_429_then_success(env: None) -> None:
    up = Upstream(
        httpx.Response(429, headers={"retry-after": "0"}),
        httpx.Response(200, json=completion("ok")),
    )
    assert post(up).status_code == 200
    assert [r["model"] for r in up.requests] == [LIGHTNING, LIGHTNING]
    assert ledger()[0]["model"] == LIGHTNING


def test_fallback_chain_after_5xx(env: None) -> None:
    up = Upstream(
        httpx.Response(500), httpx.Response(503), httpx.Response(200, json=completion("ok"))
    )
    assert post(up).status_code == 200
    assert [r["model"] for r in up.requests] == [LIGHTNING, LIGHTNING, SUPER]
    row = ledger()[0]
    assert row["model"] == SUPER and row["escalated_from"] is None


def test_timeout_walks_the_chain(env: None) -> None:
    up = Upstream(httpx.ReadTimeout("slow"), httpx.Response(200, json=completion("ok")))
    assert post(up).status_code == 200
    assert [r["model"] for r in up.requests] == [LIGHTNING, SUPER]


def test_escalation_on_malformed_tool_call(env: None) -> None:
    up = Upstream(
        httpx.Response(200, json=completion(None, tool_args="{not json")),
        httpx.Response(200, json=completion(None, tool_args={"query": "x"})),
    )
    assert post(up).status_code == 200
    row = ledger()[0]
    assert (row["model"], row["escalated_from"]) == (SUPER, LIGHTNING)


def test_escalation_on_empty_reply_when_tools_offered(env: None) -> None:
    up = Upstream(
        httpx.Response(200, json=completion("")),
        httpx.Response(200, json=completion("Here is the draft")),
    )
    assert post(up).status_code == 200
    assert ledger()[0]["escalated_from"] == LIGHTNING


def test_all_models_fail_is_400_upstream_unavailable_with_error_row(env: None) -> None:
    up = Upstream(httpx.Response(502))
    r = post(up)
    assert r.status_code == 400 and r.json()["error"]["code"] == "steward_upstream_unavailable"
    assert [r["model"] for r in up.requests] == [LIGHTNING] * 2 + [SUPER] * 2 + [NANO] * 2
    (row,) = ledger()
    assert row["status"] == "error" and "HTTP 502" in row["response_redacted"]


def test_non_retriable_4xx_stops_the_chain(env: None) -> None:
    up = Upstream(httpx.Response(401, json={"error": "bad key"}))
    r = post(up)
    assert r.status_code == 400 and len(up.requests) == 1
    assert ledger()[0]["status"] == "error"


def test_missing_key_never_calls_upstream(env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NEBIUS_API_KEY")
    up = Upstream(httpx.Response(200, json=completion("hi")))
    r = post(up)
    assert r.status_code == 400 and up.requests == []
    assert "NEBIUS_API_KEY" in ledger()[0]["response_redacted"]


def test_model_chain_comes_from_settings(env: None) -> None:
    with db.connect() as conn:
        db.set_setting(conn, "model_primary", SUPER)
        db.set_setting(conn, "reasoning_effort", "")
    up = Upstream(httpx.Response(200, json=completion("ok")))
    post(up)
    assert up.requests[0]["model"] == SUPER and "reasoning_effort" not in up.requests[0]
