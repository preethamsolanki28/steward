"""T0.3 passthrough proxy: bearer check, model mapping, reasoning_effort, recording, probes.

T2.2 extends this file with the full Shield proxy rules.
"""

import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from steward import t03_experiment
from steward.main import app

PROXY_KEY = "test-proxy-key"
NEBIUS_KEY = "test-nebius-key"


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("STEWARD_PROXY_KEY", PROXY_KEY)
    monkeypatch.setenv("NEBIUS_API_KEY", NEBIUS_KEY)
    monkeypatch.setenv("MODEL_PRIMARY", "nvidia/Nemotron-3_5-Lightning")
    monkeypatch.setenv("REASONING_EFFORT", "low")
    monkeypatch.setattr(t03_experiment, "CONTROL_FILE", tmp_path / "control.json")
    monkeypatch.setattr(t03_experiment, "RECORDINGS_DIR", tmp_path / "recordings")
    return tmp_path


def _client_with_upstream(handler) -> TestClient:
    client = TestClient(app, base_url="http://steward-api:8787")
    client.__enter__()
    app.state.http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return client


def _auth() -> dict[str, str]:
    return {"Authorization": f"Bearer {PROXY_KEY}"}


def test_rejects_missing_or_wrong_key(env: Path) -> None:
    client = _client_with_upstream(lambda r: httpx.Response(500))
    try:
        assert client.post("/v1/chat/completions", json={}).status_code == 401
        bad = {"Authorization": "Bearer nope"}
        assert client.post("/v1/chat/completions", json={}, headers=bad).status_code == 401
        assert client.get("/v1/models").status_code == 401
    finally:
        client.__exit__(None, None, None)


def test_models_lists_only_steward_auto(env: Path) -> None:
    client = _client_with_upstream(lambda r: httpx.Response(500))
    try:
        r = client.get("/v1/models", headers=_auth())
        assert r.json() == {"data": [{"id": "steward-auto", "context_length": 131072}]}
    finally:
        client.__exit__(None, None, None)


def test_maps_model_injects_effort_and_records_without_secrets(env: Path) -> None:
    seen: dict[str, object] = {}

    def upstream(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        seen["url"] = str(request.url)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    client = _client_with_upstream(upstream)
    try:
        r = client.post(
            "/v1/chat/completions",
            json={
                "model": "steward-auto",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": False,
            },
            headers=_auth(),
        )
    finally:
        client.__exit__(None, None, None)
    assert r.status_code == 200
    body = seen["body"]
    assert isinstance(body, dict)
    assert body["model"] == "nvidia/Nemotron-3_5-Lightning"
    assert body["reasoning_effort"] == "low"
    assert body["stream"] is False
    assert seen["auth"] == f"Bearer {NEBIUS_KEY}"
    assert seen["url"] == "https://api.tokenfactory.nebius.com/v1/chat/completions"
    recorded = (env / "recordings" / "adhoc" / "proxy.jsonl").read_text()
    assert NEBIUS_KEY not in recorded and PROXY_KEY not in recorded
    assert json.loads(recorded)["requested_model"] == "steward-auto"


def test_control_file_selects_model_and_effort(env: Path) -> None:
    (env / "control.json").write_text(
        json.dumps(
            {"run_id": "r1", "model": "nvidia/nemotron-3-super-120b-a12b", "reasoning_effort": ""}
        )
    )
    seen: dict[str, object] = {}

    def upstream(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={})

    client = _client_with_upstream(upstream)
    try:
        client.post(
            "/v1/chat/completions", json={"model": "steward-auto", "messages": []}, headers=_auth()
        )
    finally:
        client.__exit__(None, None, None)
    body = seen["body"]
    assert isinstance(body, dict)
    assert body["model"] == "nvidia/nemotron-3-super-120b-a12b"
    assert "reasoning_effort" not in body
    assert (env / "recordings" / "r1" / "proxy.jsonl").exists()


def test_stream_true_is_rejected(env: Path) -> None:
    client = _client_with_upstream(lambda r: httpx.Response(500))
    try:
        r = client.post("/v1/chat/completions", json={"stream": True}, headers=_auth())
    finally:
        client.__exit__(None, None, None)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "stream_not_supported"


def test_forced_policy_block_probe_returns_400_without_upstream_call(env: Path) -> None:
    (env / "control.json").write_text(json.dumps({"run_id": "pb", "force_policy_block": True}))
    calls = []
    client = _client_with_upstream(lambda r: calls.append(r) or httpx.Response(200, json={}))
    try:
        r = client.post("/v1/chat/completions", json={"messages": []}, headers=_auth())
    finally:
        client.__exit__(None, None, None)
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "steward_policy_block"
    assert calls == []


def test_missing_upstream_key_fails_fast_without_calling_upstream(
    env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("NEBIUS_API_KEY")
    calls = []
    client = _client_with_upstream(lambda r: calls.append(r) or httpx.Response(200, json={}))
    try:
        r = client.post("/v1/chat/completions", json={"messages": []}, headers=_auth())
    finally:
        client.__exit__(None, None, None)
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "no_upstream_key"
    assert calls == []
