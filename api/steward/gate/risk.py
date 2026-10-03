"""Approval Gate risk rules (docs/02 §7a, docs/04 T3.2): R0, R1 (+ lookalike), R3, overwrite.

Pure functions: everything they need (trusted contacts, the owner's address, whether a
files_write target exists) comes in through the arguments.

- R0: any argument still contains a placeholder pattern -> High, Approve disabled
  ("unresolved placeholder"). The pattern is the Shield's tolerant bracketed matcher plus bare
  upper-case tokens such as PERSON_3 or ORG 1 (docs/02 §12, "R0 scope").
- R1: a recipient who isn't a trusted contact -> High ("<addr> is not a trusted contact"). Adds
  "lookalike of <trusted domain>" when the registrable label is a near-match, a confusable, the
  same label with another TLD, or a trusted label plus extra words; for free-mail addresses it
  adds "local part mentions trusted org" instead.
- R3: more than 3 recipients -> High.
- overwrite: files_write to an existing path -> High ("overwrites existing file").

OWNER_EMAIL is excluded from all rules: the owner is never a recipient for R1 or R3. R0 and
overwrite look at the content and the path, not at recipients, so they still apply.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from email.utils import getaddresses
from encodings import idna
from typing import Any, Literal

from steward.shield.walk import TOLERANT

Risk = Literal["low", "high"]

UNRESOLVED_PLACEHOLDER = "unresolved placeholder"
OVERWRITES = "overwrites existing file"
TOO_MANY_RECIPIENTS = "more than 3 recipients"
FREE_MAIL_MENTIONS_ORG = "local part mentions trusted org"
MAX_RECIPIENTS = 3

# Bare placeholders whose brackets the model dropped (T2.5): "PERSON_3", "ORG 1". "⟦ORG_1⟧"
# (a neutralized placeholder echoed back) also matches, because ⟦ is not a word character.
BARE = re.compile(r"\b(?:PERSON|ORG|EMAIL|DOMAIN|PHONE|ACCOUNT|MONEY)[_ ]\d+\b")
# Recipients are lower-cased when normalized, so inside `to` the bare form matches any case
# ("rahul.verma@domain_1" was "rahul.verma@DOMAIN_1").
BARE_ANY_CASE = re.compile(BARE.pattern, re.IGNORECASE)
# A plain addr-spec: no whitespace (Unicode line separators included), quotes, comments, angle
# brackets, commas, semicolons, colons or square brackets. Only these are normalized.
_ADDR_SPEC = re.compile(r'[^\s"(),:;<>@\[\]\\]+@[^\s"(),:;<>@\[\]\\]+')

# Confusable folding (docs/02 §7a): Cyrillic and Greek lookalikes of Latin letters, then
# rn -> m, 0 -> o, 1 -> l. Nothing else.
_CONFUSABLES = str.maketrans(
    {
        # Cyrillic
        "а": "a",
        "е": "e",
        "о": "o",
        "р": "p",
        "с": "c",
        "у": "y",
        "х": "x",
        "і": "i",
        "ј": "j",
        "ѕ": "s",
        "ԁ": "d",
        "ӏ": "l",
        "к": "k",
        "м": "m",
        # Greek
        "α": "a",
        "ο": "o",
        "ε": "e",
        "ι": "i",
        "κ": "k",
        "ν": "v",
        "ρ": "p",
        "τ": "t",
        "υ": "u",
        "χ": "x",
        "ϲ": "c",
        "ϳ": "j",
        # more Cyrillic
        "һ": "h",
        "ԛ": "q",
        "ԝ": "w",
        "ү": "y",
    }
)

# No library and no doc defines free-mail providers; these are the common ones.
FREE_MAIL = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "yahoo.com",
        "icloud.com",
        "me.com",
        "aol.com",
        "proton.me",
        "protonmail.com",
        "gmx.com",
        "zoho.com",
        "yandex.com",
        "mail.com",
    }
)

# Second-level labels under a two-letter country TLD ("example.co.uk").
_SECOND_LEVEL = frozenset({"co", "com", "net", "org", "ac", "gov", "edu"})


@dataclass(frozen=True)
class TrustedContact:
    email: str
    org: str | None = None


@dataclass(frozen=True)
class RiskContext:
    trusted: tuple[TrustedContact, ...]
    owner_email: str

    @property
    def trusted_emails(self) -> frozenset[str]:
        return frozenset(c.email.strip().lower() for c in self.trusted)

    @property
    def trusted_domains(self) -> tuple[str, ...]:
        return tuple(sorted({_domain(e) for e in self.trusted_emails if "@" in e}))


def context(trusted: Iterable[tuple[str, str | None]], owner_email: str) -> RiskContext:
    """trusted: (email, org) of every contact with trusted=1."""
    return RiskContext(
        tuple(TrustedContact(email.strip().lower(), org) for email, org in trusted if email),
        owner_email.strip().lower(),
    )


# --- helpers -------------------------------------------------------------------------------


def normalize_recipients(to: str | Sequence[Any] | None) -> list[str]:
    """`to` as the model sent it -> distinct recipients, in order. Idempotent: the list it
    returns normalizes to itself, so the recipients that are scored are exactly the ones stored
    in args_json and sent.

    A string may be a JSON list of strings ('["a@x.example"]'), one address, "Name <a@x>", or
    several addresses separated by commas or semicolons. Each address becomes its lower-case
    addr-spec. A string that does not parse cleanly into plain addresses (e.g. an unresolved
    "[[EMAIL_1]]", a stray quote, or a "(comment)" that could hide another address) is kept
    whole, as written: it is never a trusted contact, so it always scores High."""
    if to is None:
        return []
    items: list[Any]
    if isinstance(to, str):
        items = [to]
        stripped = to.strip()
        if stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
            except ValueError:
                parsed = None
            if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                items = parsed
    else:
        items = list(to)
    out: list[str] = []
    for item in items:
        for value in _split_recipients(str(item).strip()):
            if value and value not in out:
                out.append(value)
    return out


def _canonical(addr: str) -> str | None:
    addr = addr.strip()
    return addr.lower() if _ADDR_SPEC.fullmatch(addr) else None


def _split_recipients(raw: str) -> list[str]:
    if not raw:
        return []
    plain = _canonical(raw)
    if plain:
        return [plain]
    if "(" in raw or ")" in raw:  # RFC 5322 comments would be silently dropped by the parser
        return [raw]
    pairs = getaddresses([raw.replace(";", ",")])
    addrs = [_canonical(addr) for _, addr in pairs]
    if addrs and all(addrs):
        return [a for a in addrs if a]
    return [raw]


def _domain(email: str) -> str:
    return email.rsplit("@", 1)[1].strip().lower().rstrip(".")


def _label_to_unicode(label: str) -> str:
    if not label.startswith("xn--"):
        return label
    try:
        return idna.ToUnicode(label)
    except UnicodeError:
        # encodings.idna is IDNA2003 and refuses IDNA2008 labels with ß or ς; decode the raw
        # punycode instead (RFC 3492, stdlib codec).
        try:
            return label[4:].encode("ascii").decode("punycode")
        except (UnicodeError, ValueError):
            return label


def _to_unicode(host: str) -> str:
    return ".".join(_label_to_unicode(label) for label in host.split("."))


def fold(text: str) -> str:
    """IDNA-decode, NFKC + casefold, confusable fold (docs/02 §7a)."""
    s = unicodedata.normalize("NFKC", _to_unicode(text)).casefold()
    s = s.translate(_CONFUSABLES)
    return s.replace("rn", "m").replace("0", "o").replace("1", "l")


def registrable(host: str) -> tuple[str, str]:
    """(registrable label, public suffix) without a public-suffix list."""
    labels = [label for label in _to_unicode(host.lower()).split(".") if label]
    if len(labels) < 2:
        return (labels[0] if labels else "", "")
    if len(labels) >= 3 and labels[-2] in _SECOND_LEVEL and len(labels[-1]) == 2:
        return labels[-3], ".".join(labels[-2:])
    return labels[-2], labels[-1]


def osa_distance(a: str, b: str) -> int:
    """Optimal string alignment distance (Damerau-Levenshtein, adjacent transposition = 1)."""
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[len(a)][len(b)]


def lookalike_of(host: str, trusted_domain: str) -> bool:
    """Does `host` imitate `trusted_domain`? The trusted domain itself and its real subdomains
    are not lookalikes."""
    host = host.lower().rstrip(".")
    if host == trusted_domain or host.endswith("." + trusted_domain):
        return False
    raw_c, tld_c = registrable(host)
    raw_t, tld_t = registrable(trusted_domain)
    fc, tc = fold(raw_c), fold(raw_t)
    if not fc or not tc:
        return False
    if fc == tc:  # confusable spelling, or the same label under another (raw) TLD
        return raw_c != raw_t or tld_c != tld_t
    if 1 <= osa_distance(fc, tc) <= (1 if len(tc) < 8 else 2):
        return True
    core = tc.replace("-", "")
    return len(core) >= 4 and core in fc.replace("-", "")  # trusted label plus extra words


def _alnum(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", fold(text))


def _org_needles(ctx: RiskContext) -> set[str]:
    needles: set[str] = set()
    for c in ctx.trusted:
        if "@" in c.email:
            needles.add(_alnum(registrable(_domain(c.email))[0]))
        if c.org:
            needles.add(_alnum(c.org))
            words = c.org.split()
            if words:
                needles.add(_alnum(words[0]))
    return {n for n in needles if len(n) >= 4}


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _strings(v)


# --- rules ---------------------------------------------------------------------------------


def r0_unresolved_placeholder(args: Mapping[str, Any]) -> list[str]:
    for text in _strings(args):
        if TOLERANT.search(text) or BARE.search(text):
            return [UNRESOLVED_PLACEHOLDER]
    if any(BARE_ANY_CASE.search(text) for text in _strings(args.get("to"))):
        return [UNRESOLVED_PLACEHOLDER]
    return []


def recipients(args: Mapping[str, Any], ctx: RiskContext) -> list[str]:
    """Normalized recipients, minus the owner."""
    return [r for r in normalize_recipients(args.get("to")) if r != ctx.owner_email]


def r1_untrusted_recipients(rcpts: Sequence[str], ctx: RiskContext) -> list[str]:
    reasons: list[str] = []
    trusted = ctx.trusted_emails
    needles = _org_needles(ctx)
    for addr in rcpts:
        if addr in trusted:
            continue
        reasons.append(f"{addr} is not a trusted contact")
        if "@" not in addr:
            continue
        local, domain = addr.rsplit("@", 1)
        domain = domain.rstrip(".")
        if domain in FREE_MAIL:
            if any(n in _alnum(local) for n in needles):
                reasons.append(FREE_MAIL_MENTIONS_ORG)
            continue
        reasons += [f"lookalike of {t}" for t in ctx.trusted_domains if lookalike_of(domain, t)]
    return reasons


def r3_too_many_recipients(rcpts: Sequence[str]) -> list[str]:
    return [TOO_MANY_RECIPIENTS] if len(rcpts) > MAX_RECIPIENTS else []


def overwrite(tool: str, path_exists: bool) -> list[str]:
    return [OVERWRITES] if tool == "files_write" and path_exists else []


def assess(
    tool: str, args: Mapping[str, Any], ctx: RiskContext, path_exists: bool = False
) -> tuple[Risk, list[str]]:
    """Risk and reasons for a mail_send / files_write action. Every rule means High. Reasons are
    not deduplicated across recipients: each untrusted recipient keeps its own reasons."""
    reasons = r0_unresolved_placeholder(args)
    if tool == "mail_send":
        rcpts = recipients(args, ctx)
        reasons += r1_untrusted_recipients(rcpts, ctx)
        reasons += r3_too_many_recipients(rcpts)
    reasons += overwrite(tool, path_exists)
    return ("high" if reasons else "low"), reasons


def approvable(reasons: Sequence[str]) -> bool:
    """R0 disables Approve outright; every other High needs an explicit confirmation."""
    return UNRESOLVED_PLACEHOLDER not in reasons
