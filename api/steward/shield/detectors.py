"""Identifier detectors (docs/02 §7a step 5): dictionary aliases + regex, with negative rules.

Matching (docs/04 T2.1): NFKC + casefold, Unicode word boundaries, optional possessive
('s / ’s, left outside the span), longest match first.

Regex kinds -> placeholder kinds (docs/02 §7a step 6): EMAIL -> EMAIL; PHONE -> PHONE;
IBAN/ACCOUNT, CARD, UPI VPA, IFSC, GSTIN, PAN -> ACCOUNT; MONEY -> MONEY.
Negative rules: invoice numbers (INV-\\d+), ISO dates and durations ("12 days") are never masked.
"""

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

from steward.shield.aliases import Alias, normalize


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: str  # placeholder kind
    canonical: str  # vault value
    detector: (
        str  # alias | EMAIL | PHONE | IBAN | ACCOUNT | CARD | UPI | IFSC | GSTIN | PAN | MONEY
    )


# --- normalized view with an index map back to the original text --------------------------------


def normalized_view(text: str) -> tuple[str, list[int]]:
    """Per-character NFKC + casefold. idx[i] is the original index of normalized char i; a final
    sentinel maps the end. Lets spans found on the normalized text be applied to the original."""
    out: list[str] = []
    idx: list[int] = []
    for i, ch in enumerate(text):
        norm = unicodedata.normalize("NFKC", ch).casefold()
        out.append(norm)
        idx.extend([i] * len(norm))
    idx.append(len(text))
    return "".join(out), idx


@lru_cache(maxsize=64)
def _alias_regex(keys: tuple[str, ...]) -> re.Pattern[str] | None:
    if not keys:
        return None
    alts = "|".join(r"\s+".join(re.escape(part) for part in key.split(" ")) for key in keys)
    return re.compile(rf"(?<!\w)(?:{alts})(?!\w)")


class AliasIndex:
    def __init__(self, aliases: list[Alias]) -> None:
        self.by_key: dict[str, Alias] = {normalize(a.text): a for a in aliases}
        keys = tuple(sorted(self.by_key, key=lambda k: (-len(k), k)))
        self.regex = _alias_regex(keys)

    def find(self, text: str) -> list[Span]:
        if self.regex is None or not text:
            return []
        norm, idx = normalized_view(text)
        spans = []
        for m in self.regex.finditer(norm):
            alias = self.by_key.get(" ".join(m.group(0).split()))
            if alias is None:
                continue
            start, end = idx[m.start()], idx[m.end() - 1] + 1
            spans.append(Span(start, end, alias.kind, alias.canonical, "alias"))
        return spans


# --- regex detectors --------------------------------------------------------------------------

_EMAIL = re.compile(
    r"(?<![\w.%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+"
)
# UPI VPA: name@bank where the handle has no dot (that is what tells it apart from an email).
_UPI = re.compile(
    r"(?<![\w.%+-])[A-Za-z0-9._-]{2,}@[A-Za-z][A-Za-z0-9]{1,}(?![\w@-]|\.[A-Za-z0-9])"
)
_PHONE = re.compile(
    r"(?<![\w+])(?:\+91[\s-]?|0)?[6-9]\d{4}[\s-]?\d{5}(?!\d)"  # Indian mobile (+91)
    r"|(?<![\w+])\+\d{1,3}[\s-]?(?:\d[\s-]?){6,12}\d(?!\d)"  # international with +
)
_IBAN = re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){2,7}(?:\s?[A-Z0-9]{1,4})?\b")
_ACCOUNT = re.compile(
    r"(?i)\b(?:a/c|acct|account)(?:\s*(?:no\.?|number|#))?\s*[:\-]?\s*(\d(?:[\d -]{6,22})\d)\b"
)
_CARD = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")
_IFSC = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")
_GSTIN = re.compile(r"\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b")
_PAN = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")
_AMOUNT = r"\d{1,3}(?:,\d{2,3})+(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?"
_MONEY = re.compile(
    rf"(?:₹|\bINR\b\s?|\bRs\.?\s?|\bUSD\b\s?|\bUS\$\s?|\$)\s?(?:{_AMOUNT})(?![\d,])"
    rf"|(?<![\w.,$₹])(?:{_AMOUNT})\s?(?:INR|USD|rupees?|dollars?|lakhs?|crores?)\b",
    re.I,
)

# Negative rules: never masked, and no detector span may overlap them.
_PROTECTED = re.compile(
    r"\bINV-\d+\b"
    r"|\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?\b"
    r"|\b\d+(?:\.\d+)?\s?(?:days?|weeks?|months?|years?|hours?|hrs?|minutes?|mins?)\b",
    re.I,
)


def _luhn(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
    return total % 10 == 0


def regex_spans(text: str) -> list[Span]:
    spans: list[Span] = []

    def add(pattern: re.Pattern[str], kind: str, detector: str, group: int = 0) -> None:
        for m in pattern.finditer(text):
            value = m.group(group)
            if value:
                start, end = m.start(group), m.end(group)
                canonical = value.lower() if detector == "EMAIL" else " ".join(value.split())
                spans.append(Span(start, end, kind, canonical, detector))

    add(_EMAIL, "EMAIL", "EMAIL")
    add(_UPI, "ACCOUNT", "UPI")
    add(_GSTIN, "ACCOUNT", "GSTIN")
    add(_PAN, "ACCOUNT", "PAN")
    add(_IFSC, "ACCOUNT", "IFSC")
    add(_IBAN, "ACCOUNT", "IBAN")
    add(_ACCOUNT, "ACCOUNT", "ACCOUNT", group=1)
    add(_PHONE, "PHONE", "PHONE")
    add(_MONEY, "MONEY", "MONEY")
    for m in _CARD.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and _luhn(digits):
            spans.append(Span(m.start(), m.end(), "ACCOUNT", digits, "CARD"))
    return spans


def protected_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in _PROTECTED.finditer(text)]


def find_spans(text: str, index: AliasIndex) -> list[Span]:
    """Non-overlapping identifier spans, longest first at each position, minus negative rules."""
    if not text:
        return []
    protected = protected_spans(text)
    candidates = [
        s
        for s in index.find(text) + regex_spans(text)
        if not any(s.start < p_end and p_start < s.end for p_start, p_end in protected)
    ]
    candidates.sort(key=lambda s: (s.start, -(s.end - s.start)))
    chosen: list[Span] = []
    for span in sorted(candidates, key=lambda s: (-(s.end - s.start), s.start)):
        if all(span.end <= c.start or span.start >= c.end for c in chosen):
            chosen.append(span)
    return sorted(chosen, key=lambda s: s.start)
