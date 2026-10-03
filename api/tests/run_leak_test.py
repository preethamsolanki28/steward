"""`make leak-test` (docs/04 T2.5). Runs inside the steward-api image, on the compose network.

1. Replays the committed corpus of recorded Hermes requests (api/tests/fixtures/recorded/
   *.request.json, captured raw in T0.3 and M1) through walk_strings + the leak check, offline, in
   a throwaway DB holding the seed contacts plus the inbox headers mail tools upsert.
2. Scans every egress_events.request_redacted row in the live DB.
Both fail on any seeded identifier (contact aliases >= 4 chars, emails, GSTIN, UPI, amounts) in
the outbound text, and print how many payloads were scanned (must be > 0).
3. Negative control: POSTs fixtures/recorded/blocked.json to the live proxy with
   ${STEWARD_MCP_TOKEN} substituted at runtime (no secret is committed); passes only on 400
   steward_policy_block + exactly one new policy_block audit row + one new 'blocked' ledger row
   with a «BLOCKED:SECRET» span.
"""

import dataclasses
import json
import re
import sqlite3
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

import httpx

from steward import db, seed
from steward.config import get_settings
from steward.shield import Shield

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "recorded"
TITLE = re.compile(r"^(dr|mr|mrs|ms|prof)\.?\s+", re.I)
AMOUNT = re.compile(r"(?:\$|₹)\d[\d,]*(?:\.\d+)?")
GSTIN_UPI = re.compile(r"(?:GSTIN|UPI)[^:]*:\*\*\s*(\S+)")


def seeded_identifiers() -> list[str]:
    terms: set[str] = set()
    contacts = json.loads((seed.SEED_DIR / "contacts.json").read_text())
    inbox = json.loads((seed.SEED_DIR / "inbox.json").read_text())
    people = [(c["name"], c["email"], c["org"]) for c in contacts]
    people += [(m["from_name"], m["from_email"], None) for m in inbox]
    for name, email, org in people:
        bare = TITLE.sub("", name or "")
        local, domain = email.lower().split("@", 1)
        label = domain.rsplit(".", 1)[0]
        for t in [name, bare, *bare.split(), email, local, label, label.replace("-", " ")]:
            if t and len(t) >= 4:
                terms.add(t)
        if org:
            terms.update(x for x in (org, org.split()[0]) if len(x) >= 4)
    for inv in (seed.SEED_DIR / "workspace" / "invoices").glob("*.md"):
        text = inv.read_text()
        terms.update(AMOUNT.findall(text))
        terms.update(GSTIN_UPI.findall(text))
    return sorted({t.casefold() for t in terms}, key=len, reverse=True)


_ESC = re.compile(r"\\+(?:u([0-9a-fA-F]{4})|[nrtbf\"/\\])")


def _plain(text: str) -> str:
    """Decode JSON escape runs (nested JSON), so "\\nRahul" is checked as " Rahul"."""
    return _ESC.sub(lambda m: chr(int(m.group(1), 16)) if m.group(1) else " ", text)


def found_in(text: str, terms: list[str]) -> list[str]:
    """Whole-word, case-insensitive: a term counts unless a letter or digit touches it, so
    "Khan" in "Jharkhand" is not a hit but "Khan" or "Khan's" is."""
    low = unicodedata.normalize("NFKC", _plain(text)).casefold()
    return [t for t in terms if re.search(rf"(?<![^\W_]){re.escape(t)}(?![^\W_])", low)]


def offline_corpus(terms: list[str]) -> tuple[int, list[str]]:
    tmp = Path(tempfile.mkdtemp()) / "leaktest.db"
    settings = dataclasses.replace(get_settings(), db_path=tmp)
    seed.seed_db(settings, datetime.now(seed.IST))
    conn = db.connect(tmp)
    with conn:  # what mail_search/mail_read upsert before the model ever sees a header
        for m in json.loads((seed.SEED_DIR / "inbox.json").read_text()):
            conn.execute(
                "INSERT OR IGNORE INTO contacts (name, email, org, trusted, source, "
                "created_at) VALUES (?, ?, NULL, 0, 'mail', 'leak-test')",
                (m["from_name"], m["from_email"].lower()),
            )
    failures: list[str] = []
    files = sorted(FIXTURES.glob("*.request.json"))
    for path in files:
        out = Shield(conn).outbound(json.loads(path.read_text()))
        if out.leaks:
            failures.append(f"{path.name}: leak check hit {[h.kind for _, h in out.leaks][:5]}")
        hits = found_in(json.dumps(out.request, ensure_ascii=False), terms)
        if hits:
            failures.append(f"{path.name}: seeded identifiers left {hits[:5]}")
    conn.close()
    return len(files), failures


def live_ledger(terms: list[str]) -> tuple[int, list[str]]:
    failures: list[str] = []
    rows = db.with_conn(
        lambda c: db.rows(
            c.execute("SELECT id, channel, status, request_redacted FROM egress_events")
        )
    )
    for r in rows:
        hits = found_in(r["request_redacted"] or "", terms)
        if hits:
            failures.append(f"egress_events #{r['id']} ({r['channel']}/{r['status']}): {hits[:5]}")
    return len(rows), failures


def negative_control() -> list[str]:
    s = get_settings()
    token = s.steward_mcp_token
    if not token:
        return ["STEWARD_MCP_TOKEN is not set"]
    body = json.loads(
        (FIXTURES / "blocked.json").read_text().replace("${STEWARD_MCP_TOKEN}", token)
    )

    def max_ids(conn: sqlite3.Connection) -> tuple[int, int]:
        a = conn.execute("SELECT COALESCE(MAX(id), 0) FROM audit_events").fetchone()[0]
        e = conn.execute("SELECT COALESCE(MAX(id), 0) FROM egress_events").fetchone()[0]
        return a, e

    a0, e0 = db.with_conn(max_ids)
    r = httpx.post(
        "http://steward-api:8787/v1/chat/completions",
        json=body,
        timeout=60,
        headers={"Authorization": f"Bearer {s.steward_proxy_key}"},
    )
    failures = []
    code = (
        (r.json().get("error") or {}).get("code")
        if r.headers.get("content-type", "").startswith("application/json")
        else None
    )
    if r.status_code != 400 or code != "steward_policy_block":
        failures.append(
            f"negative control: expected 400 steward_policy_block, got {r.status_code} {code}"
        )
    audits = db.with_conn(
        lambda c: db.rows(
            c.execute("SELECT kind FROM audit_events WHERE id > ? AND kind = 'policy_block'", (a0,))
        )
    )
    blocked = db.with_conn(
        lambda c: db.rows(
            c.execute(
                "SELECT request_redacted FROM egress_events WHERE id > ? AND status = 'blocked'",
                (e0,),
            )
        )
    )
    if len(audits) != 1:
        failures.append(f"negative control: expected 1 policy_block audit row, got {len(audits)}")
    if len(blocked) != 1:
        failures.append(f"negative control: expected 1 blocked ledger row, got {len(blocked)}")
    elif (
        "«BLOCKED:SECRET»" not in blocked[0]["request_redacted"]
        or token in blocked[0]["request_redacted"]
    ):
        failures.append("negative control: blocked row lacks «BLOCKED:SECRET» or holds the token")
    return failures


def main() -> int:
    terms = seeded_identifiers()
    n_corpus, f1 = offline_corpus(terms)
    n_rows, f2 = live_ledger(terms)
    f3 = negative_control()
    print(f"leak-test: {len(terms)} seeded identifiers")
    print(
        f"leak-test: replayed {n_corpus} recorded Hermes requests through walk_strings + leak "
        f"check: {'OK' if not f1 else 'FAIL'}"
    )
    print(
        f"leak-test: scanned {n_rows} egress_events.request_redacted rows: "
        f"{'OK' if not f2 else 'FAIL'}"
    )
    print(f"leak-test: payloads scanned: {n_corpus + n_rows}")
    print(f"leak-test: negative control (blocked.json -> live proxy): {'OK' if not f3 else 'FAIL'}")
    for f in f1 + f2 + f3:
        print("  -", f)
    ok = not (f1 or f2 or f3) and n_corpus + n_rows > 0
    print("leak-test: PASS" if ok else "leak-test: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
