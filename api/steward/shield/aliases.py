"""Dictionary aliases derived in memory from `contacts` (docs/02 §7a step 5, docs/04 T2.1).

For every contact:
- name forms (PERSON, canonical = stored name): full name, name without title, first name,
  last name, title + last name ("Dr. Shah").
- org forms (ORG, canonical = org): org name, org minus legal suffix, org first word if >=4 chars.
- email forms: email and email local part (EMAIL, canonical = email); email domain and the
  domain label without TLD incl. hyphen/space variants (DOMAIN, canonical = domain).
Aliases under 3 chars are not matched on their own; they are covered when they appear next to
the surname, through the full-name alias ("Li Wei").

Collision rule (decided 2026-10-02, docs/02 §7a step 6): when two contacts yield the same alias,
contacts with source='seed' win over contacts upserted from mail headers (attacker-controlled
display names and addresses); within one source the lower contact id wins. Within one contact,
person forms come first, then org forms, then email forms.
"""

import re
import sqlite3
import unicodedata
from dataclasses import dataclass

TITLE = re.compile(r"^(dr|mr|mrs|ms|mx|prof)\.?\s+", re.I)
LEGAL_SUFFIX = re.compile(
    r"[\s,]*(?:&\s*co\.?|and\s+co\.?|pvt\.?\s*ltd\.?|private\s+limited|ltd\.?|limited|llc|llp|"
    r"inc\.?|corp\.?|gmbh|plc)$",
    re.I,
)
MIN_ALIAS_CHARS = 3


@dataclass(frozen=True)
class Alias:
    text: str
    kind: str  # PERSON | ORG | EMAIL | DOMAIN
    canonical: str
    contact_id: int
    source: str


def normalize(text: str) -> str:
    """NFKC + casefold, whitespace collapsed: the key every matcher compares on."""
    folded = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(folded.split())


def _person_forms(name: str) -> list[str]:
    name = " ".join(name.split())
    bare = TITLE.sub("", name)
    parts = bare.split()
    forms = [name, bare]
    if parts:
        forms += [parts[0], parts[-1]]
        title = TITLE.match(name)
        if title and len(parts) > 1:
            t = title.group(1)
            forms += [f"{t}. {parts[-1]}", f"{t} {parts[-1]}"]
    return forms


def _org_forms(org: str) -> list[str]:
    org = " ".join(org.split())
    stripped = LEGAL_SUFFIX.sub("", org).strip(" ,")
    forms = [org, stripped]
    first = stripped.split()[0] if stripped.split() else ""
    if len(first) >= 4:
        forms.append(first)
    return forms


def _email_forms(email: str) -> list[tuple[str, str, str]]:
    email = email.strip().lower()
    if "@" not in email:
        return []
    local, domain = email.split("@", 1)
    label = domain.rsplit(".", 1)[0] if "." in domain else domain
    out = [(email, "EMAIL", email), (local, "EMAIL", email), (domain, "DOMAIN", domain)]
    for variant in (label, label.replace("-", " "), label.replace("-", "")):
        out.append((variant, "DOMAIN", domain))
    return out


def derive(contacts: list[dict]) -> list[Alias]:
    """All aliases, de-duplicated by normalized text using the collision rule above."""
    ordered = sorted(contacts, key=lambda c: (c.get("source") != "seed", int(c["id"])))
    chosen: dict[str, Alias] = {}
    for c in ordered:
        candidates: list[tuple[str, str, str]] = []
        name = (c.get("name") or "").strip()
        if name:
            candidates += [(f, "PERSON", name) for f in _person_forms(name)]
        org = (c.get("org") or "").strip()
        if org:
            candidates += [(f, "ORG", org) for f in _org_forms(org)]
        candidates += _email_forms(c.get("email") or "")
        for text, kind, canonical in candidates:
            key = normalize(text)
            if len(key) < MIN_ALIAS_CHARS or key in chosen:
                continue
            chosen[key] = Alias(text, kind, canonical, int(c["id"]), str(c.get("source") or ""))
    return sorted(chosen.values(), key=lambda a: -len(normalize(a.text)))


def load(conn: sqlite3.Connection) -> list[Alias]:
    rows = conn.execute("SELECT id, name, email, org, source FROM contacts").fetchall()
    return derive([dict(r) for r in rows])
