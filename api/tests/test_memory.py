"""T1.8: GET/PUT /api/memory (entry-aware, limits, atomic write)."""

import pytest
from fastapi.testclient import TestClient

from steward.config import get_settings
from steward.main import app

LOCAL = "http://127.0.0.1:8787"
WEB = {"X-Steward-Client": "web"}
SEED_USER = "Maya prefers concise, friendly emails and signs off 'Best, Maya'"


@pytest.fixture
def client():
    mem = get_settings().memories_dir
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "USER.md").write_text(SEED_USER)
    (mem / "MEMORY.md").write_text("Entry one\n§\nEntry two ₹")
    with TestClient(app, base_url=LOCAL) as c:
        yield c


def test_get_splits_entries_and_counts_code_points(client: TestClient) -> None:
    body = client.get("/api/memory").json()
    assert body["user"] == {"entries": [SEED_USER], "chars": len(SEED_USER), "limit": 1375}
    assert body["memory"]["entries"] == ["Entry one", "Entry two ₹"]
    assert body["memory"]["chars"] == len("Entry one\n§\nEntry two ₹") == 23
    assert body["memory"]["limit"] == 2200


def test_put_writes_joined_entries_atomically(client: TestClient) -> None:
    entries = [SEED_USER, "Rahul at Acme likes short, formal emails."]
    r = client.put("/api/memory", json={"file": "user", "entries": entries}, headers=WEB)
    assert r.status_code == 200 and r.json() == {"ok": True}
    mem = get_settings().memories_dir
    assert (mem / "USER.md").read_text() == "\n§\n".join(entries)
    assert sorted(p.name for p in mem.iterdir()) == ["MEMORY.md", "USER.md"]  # no temp files
    assert client.get("/api/memory").json()["user"]["entries"] == entries


def test_put_drops_blank_entries_and_strips(client: TestClient) -> None:
    client.put("/api/memory", json={"file": "memory", "entries": ["  a  ", "", "b"]}, headers=WEB)
    assert (get_settings().memories_dir / "MEMORY.md").read_text() == "a\n§\nb"


def test_limit_is_inclusive_and_over_limit_is_400(client: TestClient) -> None:
    ok = client.put("/api/memory", json={"file": "user", "entries": ["x" * 1375]}, headers=WEB)
    assert ok.status_code == 200
    over = client.put("/api/memory", json={"file": "user", "entries": ["x" * 1376]}, headers=WEB)
    assert over.status_code == 400 and "over the limit" in over.json()["detail"]
    # Delimiters count too: two entries of 1100 + "\n§\n" = 2203 > 2200.
    two = client.put(
        "/api/memory", json={"file": "memory", "entries": ["y" * 1100, "z" * 1100]}, headers=WEB
    )
    assert two.status_code == 400
    assert (get_settings().memories_dir / "USER.md").read_text() == "x" * 1375  # unchanged


def test_entry_with_delimiter_line_is_rejected(client: TestClient) -> None:
    r = client.put("/api/memory", json={"file": "user", "entries": ["a\n§\nb"]}, headers=WEB)
    assert r.status_code == 400
    assert (get_settings().memories_dir / "USER.md").read_text() == SEED_USER


def test_put_requires_client_header_and_known_file(client: TestClient) -> None:
    assert client.put("/api/memory", json={"file": "user", "entries": []}).status_code == 403
    assert (
        client.put("/api/memory", json={"file": "soul", "entries": []}, headers=WEB).status_code
        == 422
    )
