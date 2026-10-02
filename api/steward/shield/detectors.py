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


# JSON escape runs inside strings (tool results are JSON nested in JSON, so a newline can reach us
# as the two characters backslash + n, or more backslashes). Without this, "\\nRahul" would put
# a word character right before the name and defeat the word boundary (live finding, T2.2).
_ESCAPE = re.compile(r"\\+(?:u([0-9a-fA-F]{4})|[nrtbf\"/\\])")


def normalized_view(text: str) -> tuple[str, list[int], list[int]]:
    """Per-character NFKC + casefold, with JSON escape runs turned into a separator (or, for
    \\uXXXX, the decoded character). starts[i] / ends[i] give the original span covered by
    normalized char i, so matches on the normalized text map back exactly."""
    out: list[str] = []
    starts: list[int] = []
    ends: list[int] = []
    i, n = 0, len(text)
    while i < n:
        if text[i] == "\\":
            m = _ESCAPE.match(text, i)
            if m:
                code = m.group(1)
                ch = chr(int(code, 16)) if code else " "
                if 0xD800 <= ord(ch) <= 0xDFFF:
                    ch = " "
                for c in unicodedata.normalize("NFKC", ch).casefold() or " ":
                    out.append(c)
                    starts.append(i)
                    ends.append(m.end())
                i = m.end()
                continue
        for c in unicodedata.normalize("NFKC", text[i]).casefold():
            out.append(c)
            starts.append(i)
            ends.append(i + 1)
        i += 1
    return "".join(out), starts, ends


def regex_view(text: str) -> str:
    """Same length as `text`, with JSON escape runs blanked, so regex spans keep their indices."""
    return _ESCAPE.sub(lambda m: " " * len(m.group(0)), text)


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
        norm, starts, ends = normalized_view(text)
        spans = []
        for m in self.regex.finditer(norm):
            alias = self.by_key.get(" ".join(m.group(0).split()))
            if alias is None:
                continue
            spans.append(
                Span(starts[m.start()], ends[m.end() - 1], alias.kind, alias.canonical, "alias")
            )
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
    original = text
    text = regex_view(text)
    spans: list[Span] = []

    def add(pattern: re.Pattern[str], kind: str, detector: str, group: int = 0) -> None:
        for m in pattern.finditer(text):
            value = original[m.start(group) : m.end(group)] if m.group(group) else ""
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
    return [(m.start(), m.end()) for m in _PROTECTED.finditer(regex_view(text))]


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
