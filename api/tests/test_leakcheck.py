"""T2.3: fail-closed leak check (normalized matcher, >=4-char aliases, vault values, secrets).

Golden test: the full recorded Hermes system prompt passes with 0 blocks, and every recorded
request in the corpus (api/tests/fixtures/recorded/*.request.json, raw requests captured in
T0.3 and M1 before the Shield existed) leaves zero seeded identifiers after pseudonymization.
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from steward import db, seed
from steward.config import get_settings
from steward.shield import Shield

CORPUS = sorted((Path(__file__).parent / "fixtures" / "recorded").glob("*.request.json"))
SEEDED = [
    "Rahul",
    "Verma",
    "rahul.verma",
    "acme-logistics",
    "Acme",
    "Brightleaf",
    "Anita",
    "Kestrel",
    "Juniper",
    "Becker",
    "Orbitra",
    "Sara Khan",
    "Maya",
    "maya@",
    "29AAAPR4242M1ZD",
    "mayarao@examplebank",
    "$4,800",
    "4,800",
]


@pytest.fixture
def shield():
    seed.seed_db(get_settings(), datetime(2026, 10, 3, 9, 0, tzinfo=seed.IST))
    conn = db.connect()
    yield Shield(conn)
    conn.close()


def test_corpus_is_not_empty() -> None:
    assert len(CORPUS) >= 5


def test_recorded_hermes_system_prompt_passes_with_zero_blocks(shield: Shield) -> None:
    request = json.loads(CORPUS_BY_NAME("t03-lightning-plain-step1-agent").read_text())
    system = request["messages"][0]
    assert system["role"] == "system" and len(system["content"]) > 5000
    assert shield.checker().scan(system["content"]) == []
    out = shield.outbound({"messages": [system], "tools": request["tools"]})
    assert out.leaks == []


@pytest.mark.parametrize("path", CORPUS, ids=lambda p: p.stem)
def test_recorded_requests_leave_no_seeded_identifier(shield: Shield, path: Path) -> None:
    request = json.loads(path.read_text())
    out = shield.outbound(request)
    assert out.leaks == [], out.leaks[:3]
    sent = json.dumps(out.request, ensure_ascii=False).casefold()
    for raw in SEEDED:
        assert raw.casefold() not in sent, raw


def test_secret_values_are_caught_and_masked(
    shield: Shield, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in (
        "NEBIUS_API_KEY",
        "TAVILY_API_KEY",
        "SMTP_PASSWORD",
        "STEWARD_PROXY_KEY",
        "STEWARD_MCP_TOKEN",
        "HERMES_API_KEY",
    ):
        secret = f"{name.lower()}-value-1234567"
        monkeypatch.setenv(name, secret)
        out = shield.outbound({"messages": [{"role": "user", "content": f"x {secret} y"}]})
        assert [h.kind for _, h in out.leaks] == ["SECRET"], name
        masked = out.blocked_request["messages"][0]["content"]  # type: ignore[index]
        assert masked == "x «BLOCKED:SECRET» y"


def test_short_secret_values_are_ignored(shield: Shield, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SMTP_PASSWORD", "abc")  # too short to scan without false positives
    out = shield.outbound({"messages": [{"role": "user", "content": "abc"}]})
    assert out.leaks == []


def test_identifier_that_escaped_pseudonymization_is_caught(shield: Shield) -> None:
    checker = shield.checker()
    hits = checker.scan("from Rahul Verma at ACME LOGISTICS (rahul.verma)")
    assert [h.kind for h in hits] == ["PERSON", "ORG", "EMAIL"]
    assert checker.mask("Dear Rahul,") == "Dear «BLOCKED:PERSON»,"


def test_vault_values_are_scanned(shield: Shield) -> None:
    shield.outbound(
        {"messages": [{"role": "user", "content": "total $4,800 GSTIN 29AAAPR4242M1ZD"}]}
    )
    checker = Shield(shield.vault.conn).checker()
    assert {h.kind for h in checker.scan("paid 29AAAPR4242M1ZD")} == {"ACCOUNT"}


def test_aliases_shorter_than_four_chars_are_not_leak_terms(shield: Shield) -> None:
    # "Rao" (3) and "Tom" (3) are masked by the pseudonymizer but are not leak-check terms on their
    # own, which avoids blocking ordinary words; "Maya" (4) is.
    checker = shield.checker()
    assert checker.scan("Rao and Tom") == []
    assert [h.kind for h in checker.scan("Maya")] == ["PERSON"]


def CORPUS_BY_NAME(stem: str) -> Path:  # noqa: N802 - tiny helper
    return next(p for p in CORPUS if p.stem == f"{stem}.request" or p.stem == stem)
