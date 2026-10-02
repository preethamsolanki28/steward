"""T2.4: Egress Ledger store, pricing, /api/ledger, /api/ledger/{id}, /api/ledger/stats."""

import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from steward import db, seed
from steward.config import get_settings
from steward.ledger import pricing, store
from steward.main import app
from steward.shield import Shield

LOCAL = "http://127.0.0.1:8787"
LIGHTNING = "nvidia/Nemotron-3_5-Lightning"


@pytest.fixture
def rows() -> dict[str, int]:
    seed.seed_db(get_settings(), datetime(2026, 10, 3, 9, 0, tzinfo=seed.IST))
    with db.connect() as conn:
        shield = Shield(conn)
        sent = shield.outbound(
            {"messages": [{"role": "user", "content": "Chase Rahul Verma at Acme for $4,800"}]}
        )
        llm = store.insert(
            conn,
            channel="llm",
            destination="api.tokenfactory.nebius.com",
            status="ok",
            model=LIGHTNING,
            request_redacted=sent.request,
            response_redacted={
                "choices": [{"message": {"content": "Draft to [[PERSON_1]] for [[MONEY_1]]"}}]
            },
            entities_masked=sent.masked,
            entity_kinds=sent.kinds,
            prompt_tokens=1000,
            completion_tokens=200,
            latency_ms=1500,
            cost_usd=pricing.cost_usd(LIGHTNING, 1000, 200),
        )
        web = store.insert(
            conn,
            channel="web",
            destination="api.tavily.com",
            status="ok",
            request_redacted={"query": "warehouse robotics funding"},
            response_redacted=[{"title": "t"}],
            latency_ms=900,
        )
        blocked = store.insert(
            conn,
            channel="llm",
            destination="api.tokenfactory.nebius.com",
            status="blocked",
            request_redacted={"messages": [{"content": "«BLOCKED:SECRET»"}]},
        )
    return {"llm": llm, "web": web, "blocked": blocked}


def client() -> TestClient:
    return TestClient(app, base_url=LOCAL)


def test_list_newest_first_with_documented_fields(rows: dict[str, int]) -> None:
    with client() as c:
        items = c.get("/api/ledger").json()
        assert [i["id"] for i in items] == [rows["blocked"], rows["web"], rows["llm"]]
        assert set(items[0]) == {
            "id",
            "ts",
            "channel",
            "destination",
            "model",
            "escalated_from",
            "entities_masked",
            "latency_ms",
            "cost_usd",
            "status",
        }
        assert [i["id"] for i in c.get("/api/ledger?channel=web").json()] == [rows["web"]]
        assert len(c.get("/api/ledger?limit=1").json()) == 1
        assert c.get("/api/ledger?channel=fax").status_code == 422


def test_stats_today(rows: dict[str, int]) -> None:
    with client() as c:
        today = c.get("/api/ledger/stats").json()["today"]
    assert today["calls"] == 2 and today["blocked"] == 1
    assert today["entities_masked"] == 3  # Rahul Verma, Acme, $4,800
    assert today["tokens"] == 1200
    assert today["cost_usd"] == pytest.approx(1000 / 1e6 * 0.06 + 200 / 1e6 * 0.24)


def test_detail_local_views_are_reidentified_on_read(rows: dict[str, int]) -> None:
    with client() as c:
        d = c.get(f"/api/ledger/{rows['llm']}").json()
    assert "Rahul" not in d["request_redacted"] and "[[PERSON_" in d["request_redacted"]
    assert "Rahul Verma" in d["request_local"] and "Acme" in d["request_local"]
    assert "$4,800" in d["response_local"]
    assert (
        d["entity_kinds"] == {"PERSON": 1, "ORG": 1, "MONEY": 1}
        or sum(d["entity_kinds"].values()) == 4
    )
    with db.connect() as conn:  # never stored: the table only holds the redacted copy
        stored = conn.execute("SELECT * FROM egress_events WHERE id=?", (rows["llm"],)).fetchone()
    assert "Rahul" not in json.dumps(dict(stored))


def test_blocked_and_web_rows(rows: dict[str, int]) -> None:
    with client() as c:
        blocked = c.get(f"/api/ledger/{rows['blocked']}").json()
        web = c.get(f"/api/ledger/{rows['web']}").json()
        assert c.get("/api/ledger/9999").status_code == 404
    assert blocked["status"] == "blocked" and "«BLOCKED:SECRET»" in blocked["request_local"]
    assert blocked["response_redacted"] is None and blocked["response_local"] is None
    assert web["channel"] == "web" and "warehouse robotics funding" in web["request_local"]


def test_audit_rows_per_channel(rows: dict[str, int]) -> None:
    with db.connect() as conn:
        audit = db.rows(conn.execute("SELECT kind, summary, ref_id FROM audit_events ORDER BY id"))
    assert audit == [
        {
            "kind": "egress",
            "summary": "Nemotron 3.5 Lightning · 3 identifiers masked",
            "ref_id": rows["llm"],
        },
        {"kind": "egress", "summary": "Tavily search", "ref_id": rows["web"]},
        {
            "kind": "policy_block",
            "summary": "Blocked: identifier would have left the Mac",
            "ref_id": rows["blocked"],
        },
    ]


def test_pricing_table() -> None:
    assert pricing.cost_usd("nvidia/nemotron-3-super-120b-a12b", 1_000_000, 1_000_000) == 1.2
    assert pricing.cost_usd("nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B", 1_000_000, 0) == 0.06
    assert pricing.cost_usd(None, 5, 5) == 0.0
    assert pricing.display_name(LIGHTNING) == "Nemotron 3.5 Lightning"
