"""The vault (docs/02 §5 `vault`, §7a step 6): canonical value <-> stable placeholder.

Same (kind, value) -> same placeholder forever: [[PERSON_n]], [[EMAIL_n]], [[ORG_n]],
[[DOMAIN_n]], [[PHONE_n]], [[ACCOUNT_n]], [[MONEY_n]]. n counts up per kind. Minting runs
inside BEGIN IMMEDIATE so two concurrent requests can never mint the same placeholder twice.
Local only: vault values never leave the Mac.
"""

import sqlite3

from steward import db

KINDS = ("PERSON", "EMAIL", "ORG", "DOMAIN", "PHONE", "ACCOUNT", "MONEY")


class Vault:
    """In-memory view of the vault for one request; mints into the DB on first use."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.by_value: dict[tuple[str, str], str] = {}
        self.by_placeholder: dict[str, str] = {}
        for row in conn.execute("SELECT placeholder, kind, value FROM vault"):
            self.by_value[(row["kind"], row["value"])] = row["placeholder"]
            self.by_placeholder[row["placeholder"]] = row["value"]

    def placeholder(self, kind: str, value: str) -> str:
        if kind not in KINDS:
            raise ValueError(f"unknown vault kind {kind!r}")
        hit = self.by_value.get((kind, value))
        if hit:
            return hit
        in_tx = self.conn.in_transaction
        if not in_tx:
            self.conn.execute("BEGIN IMMEDIATE")
        try:
            row = self.conn.execute(
                "SELECT placeholder FROM vault WHERE kind = ? AND value = ?", (kind, value)
            ).fetchone()
            if row:
                placeholder = row["placeholder"]
            else:
                count = self.conn.execute(
                    "SELECT COUNT(*) FROM vault WHERE kind = ?", (kind,)
                ).fetchone()[0]
                placeholder = f"[[{kind}_{count + 1}]]"
                self.conn.execute(
                    "INSERT INTO vault (placeholder, kind, value, created_at) VALUES (?, ?, ?, ?)",
                    (placeholder, kind, value, db.now_iso()),
                )
            if not in_tx:
                self.conn.execute("COMMIT")
        except BaseException:
            if not in_tx:
                self.conn.execute("ROLLBACK")
            raise
        self.by_value[(kind, value)] = placeholder
        self.by_placeholder[placeholder] = value
        return placeholder

    def value(self, placeholder: str) -> str | None:
        return self.by_placeholder.get(placeholder)

    def values(self) -> list[tuple[str, str]]:
        """(kind, value) for every vault entry: the leak check scans for all of them."""
        return list(self.by_value)
