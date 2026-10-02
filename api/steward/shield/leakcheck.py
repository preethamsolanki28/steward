"""Fail-closed leak check (docs/02 §7a step 7, docs/04 T2.3).

Runs AFTER pseudonymization over EVERY outbound string leaf (no skip-list: tools[] definitions,
response_format, ids and the model name are scanned too) for:
- any vault value (normalized matcher),
- any contact alias of >= 4 chars (normalized matcher),
- the literal value of every secret env var (NEBIUS_API_KEY, TAVILY_API_KEY, SMTP_PASSWORD and the
  STEWARD_* / HERMES_API_KEY bearer secrets).
Any hit means the request is NOT sent. `mask` rewrites each offending span as «BLOCKED:KIND».
"""

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from steward.config import Settings
from steward.shield.aliases import Alias, normalize
from steward.shield.detectors import normalized_view

MIN_ALIAS_CHARS = 4
MIN_SECRET_CHARS = 8


@dataclass(frozen=True)
class Hit:
    start: int
    end: int
    kind: str


def secret_values(settings: Settings) -> list[str]:
    values = [
        settings.nebius_api_key,
        settings.tavily_api_key,
        settings.smtp_password,
        settings.steward_proxy_key,
        settings.steward_mcp_token,
        settings.hermes_api_key,
    ]
    return sorted({v for v in values if v and len(v) >= MIN_SECRET_CHARS}, key=len, reverse=True)


@lru_cache(maxsize=32)
def _terms_regex(keys: tuple[str, ...]) -> re.Pattern[str] | None:
    if not keys:
        return None
    alts = "|".join(r"\s+".join(re.escape(p) for p in k.split(" ")) for k in keys)
    return re.compile(rf"(?<!\w)(?:{alts})(?!\w)")


class LeakChecker:
    def __init__(
        self, aliases: list[Alias], vault_values: list[tuple[str, str]], secrets: list[str]
    ) -> None:
        self.kind_by_key: dict[str, str] = {}
        for kind, value in vault_values:
            key = normalize(value)
            if key:
                self.kind_by_key.setdefault(key, kind)
        for alias in aliases:
            key = normalize(alias.text)
            if len(key) >= MIN_ALIAS_CHARS:
                self.kind_by_key.setdefault(key, alias.kind)
        keys = tuple(sorted(self.kind_by_key, key=lambda k: (-len(k), k)))
        self.regex = _terms_regex(keys)
        self.secrets = secrets

    def scan(self, text: str) -> list[Hit]:
        hits: list[Hit] = []
        for secret in self.secrets:
            start = text.find(secret)
            while start != -1:
                hits.append(Hit(start, start + len(secret), "SECRET"))
                start = text.find(secret, start + 1)
        if self.regex is not None and text:
            norm, starts, ends = normalized_view(text)
            for m in self.regex.finditer(norm):
                kind = self.kind_by_key.get(" ".join(m.group(0).split()), "IDENTIFIER")
                hits.append(Hit(starts[m.start()], ends[m.end() - 1], kind))
        hits.sort(key=lambda h: (h.start, -(h.end - h.start)))
        merged: list[Hit] = []
        for h in hits:
            if merged and h.start < merged[-1].end:
                continue
            merged.append(h)
        return merged

    def scan_request(self, request: Any) -> list[tuple[str, Hit]]:
        """(leaf path, hit) for every hit in every string leaf of the request."""
        found: list[tuple[str, Hit]] = []

        def visit(obj: Any, path: str) -> None:
            if isinstance(obj, str):
                found.extend((path, h) for h in self.scan(obj))
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    visit(v, f"{path}[{i}]")
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    visit(k, f"{path}.<key>")
                    visit(v, f"{path}.{k}")

        visit(request, "$")
        return found

    def mask(self, obj: Any) -> Any:
        """Copy of the request with every offending span replaced by «BLOCKED:KIND»."""
        if isinstance(obj, str):
            hits = self.scan(obj)
            if not hits:
                return obj
            parts, last = [], 0
            for h in hits:
                parts.append(obj[last : h.start])
                parts.append(f"«BLOCKED:{h.kind}»")
                last = h.end
            parts.append(obj[last:])
            return "".join(parts)
        if isinstance(obj, list):
            return [self.mask(v) for v in obj]
        if isinstance(obj, dict):
            return {self.mask(k): self.mask(v) for k, v in obj.items()}
        return obj
