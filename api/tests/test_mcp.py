"""T0.3 stub MCP server: /mcp bearer guard, DNS-rebinding hosts, the 3 stub tools.

T1.3 extends this file for the real steward-tools server.
"""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from steward import t03_experiment
from steward.main import app

TOKEN = "test-mcp-token"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
}


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("STEWARD_MCP_TOKEN", TOKEN)
    monkeypatch.setattr(t03_experiment, "CONTROL_FILE", tmp_path / "control.json")
    monkeypatch.setattr(t03_experiment, "RECORDINGS_DIR", tmp_path / "recordings")
    with TestClient(app, base_url="http://steward-api:8787") as c:
        yield c


def _rpc(client: TestClient, method: str, params: dict, headers: dict | None = None):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    return client.post("/mcp", content=json.dumps(payload), headers=headers or HEADERS)


def test_mcp_requires_bearer(client: TestClient) -> None:
    no_auth = {k: v for k, v in HEADERS.items() if k != "Authorization"}
    assert _rpc(client, "tools/list", {}, headers=no_auth).status_code == 401
    wrong = {**HEADERS, "Authorization": "Bearer nope"}
    assert _rpc(client, "tools/list", {}, headers=wrong).status_code == 401


def test_mcp_rejects_unlisted_host(client: TestClient) -> None:
    r = client.post(
        "http://evil.example/mcp",
        content=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}),
        headers=HEADERS,
    )
    assert r.status_code in (400, 421)


def test_stub_lists_exactly_three_tools(client: TestClient) -> None:
    init = _rpc(
        client,
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "pytest", "version": "0"},
        },
    )
    assert init.status_code == 200
    r = _rpc(client, "tools/list", {})
    assert r.status_code == 200
    names = sorted(t["name"] for t in r.json()["result"]["tools"])
    assert names == ["files_read", "mail_search", "mail_send"]
