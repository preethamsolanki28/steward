"""Tavily web search behind the identifier guard (docs/02 §7a "web_search", D10).

The final query is capped at 120 chars and re-checked for identifiers. Any hit blocks the
search: nothing is sent, an audit_events(kind='policy_block') row and an egress_events row with
status 'blocked' (offending spans as «BLOCKED:KIND») are written. Allowed queries are sent in
clear to Tavily (topics only, Tavily's own retention) and logged as egress_events(channel='web').

The check is the full Privacy Shield (T2.1): dictionary aliases + every regex detector, plus the
leak checker's vault values, contact aliases (>= 4 chars) and secret env values. Any vault entity
(incl. ORG, MONEY, DOMAIN) blocks the query.
"""

import sqlite3
import time
from typing import Any

import httpx

from steward import db
from steward.config import get_settings
from steward.ledger import store
from steward.shield import Shield
from steward.shield.detectors import find_spans

TAVILY_URL = "https://api.tavily.com/search"
DESTINATION = "api.tavily.com"
MAX_QUERY_CHARS = 120


class SearchBlocked(Exception):
    pass


class SearchFailed(Exception):
    pass


def find_identifiers(conn: sqlite3.Connection, query: str) -> list[tuple[int, int, str]]:
    """Spans (start, end, KIND) of identifiers in the final query, using the full Shield."""
    shield = Shield(conn)
    spans = [(s.start, s.end, s.kind) for s in find_spans(query, shield.index)]
    spans += [(h.start, h.end, h.kind) for h in shield.checker().scan(query)]
    merged: list[tuple[int, int, str]] = []
    for start, end, kind in sorted(spans, key=lambda x: (x[0], -(x[1] - x[0]))):
        if merged and start < merged[-1][1]:
            continue
        merged.append((start, end, kind))
    return merged


def mask_blocked(query: str, spans: list[tuple[int, int, str]]) -> str:
    out, last = [], 0
    for start, end, kind in spans:
        out.append(query[last:start])
        out.append(f"«BLOCKED:{kind}»")
        last = end
    out.append(query[last:])
    return "".join(out)


async def search(client: httpx.AsyncClient, query: str, max_results: int = 5) -> list[dict]:
    settings = get_settings()
    final = " ".join(query.split())[:MAX_QUERY_CHARS]
    max_results = max(1, min(int(max_results), 10))

    def guard(conn: sqlite3.Connection) -> bool:
        """Write the blocked ledger + audit rows and COMMIT them before refusing."""
        spans = find_identifiers(conn, final)
        if spans:
            masked = {"query": mask_blocked(final, spans), "max_results": max_results}
            store.insert(
                conn,
                channel="web",
                destination=DESTINATION,
                status="blocked",
                request_redacted=masked,
            )
        return bool(spans)

    if await db.run(guard):
        raise SearchBlocked(
            "Blocked by Steward: the search query contained a client identifier. "
            "Search only the client's watch topic, never names, orgs, emails or amounts."
        )
    if not settings.tavily_api_key:
        raise SearchFailed("Tavily is not configured (no TAVILY_API_KEY).")

    request = {"query": final, "max_results": max_results}
    started = time.monotonic()
    try:
        r = await client.post(
            TAVILY_URL,
            json=request,
            timeout=30.0,
            headers={"Authorization": f"Bearer {settings.tavily_api_key}"},
        )
        status = "ok" if r.status_code == 200 else "error"
        payload: dict[str, Any] = r.json() if status == "ok" else {"error": f"HTTP {r.status_code}"}
    except (httpx.HTTPError, ValueError) as exc:
        status, payload = "error", {"error": type(exc).__name__}
    latency = int((time.monotonic() - started) * 1000)
    raw: list[dict[str, Any]] = payload.get("results") or [] if status == "ok" else []
    results = [
        {
            "title": str(x.get("title") or ""),
            "url": str(x.get("url") or ""),
            "snippet": str(x.get("content") or "")[:500],
        }
        for x in raw
        if isinstance(x, dict)
    ]

    def log(conn: sqlite3.Connection) -> None:
        store.insert(
            conn,
            channel="web",
            destination=DESTINATION,
            status=status,
            request_redacted=request,
            response_redacted=results if status == "ok" else payload,
            latency_ms=latency,
        )

    await db.run(log)
    if status != "ok":
        raise SearchFailed("Tavily search failed; the brief can go without watch topics.")
    return results
