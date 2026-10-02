"""Privacy Shield: aliases, detectors, vault, walk_strings, leak check (docs/02 §7a)."""

import sqlite3
from dataclasses import dataclass, field
from typing import Any

from steward.config import get_settings
from steward.shield import aliases as aliases_mod
from steward.shield.detectors import AliasIndex
from steward.shield.leakcheck import LeakChecker, secret_values
from steward.shield.vault import Vault
from steward.shield.walk import pseudonymize, reidentify


@dataclass
class ShieldResult:
    request: dict[str, Any]
    masked: int
    kinds: dict[str, int]
    leaks: list[tuple[str, Any]] = field(default_factory=list)
    blocked_request: dict[str, Any] | None = None


class Shield:
    """One request's view of contacts + vault. Sync: run it via steward.db.run (worker thread)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.aliases = aliases_mod.load(conn)
        self.index = AliasIndex(self.aliases)
        self.vault = Vault(conn)

    def checker(self) -> LeakChecker:
        return LeakChecker(self.aliases, self.vault.values(), secret_values(get_settings()))

    def outbound(self, request: dict[str, Any]) -> ShieldResult:
        """Neutralize + pseudonymize, then leak-check the result (fail closed on any hit)."""
        sanitized, p = pseudonymize(request, self.index, self.vault)
        checker = self.checker()
        leaks = checker.scan_request(sanitized)
        result = ShieldResult(sanitized, p.masked, dict(p.kinds), leaks)
        if leaks:
            result.blocked_request = checker.mask(sanitized)
        return result

    def inbound(self, response: Any) -> tuple[Any, int, int]:
        restored, r = reidentify(response, self.vault)
        return restored, r.restored, r.unknown
