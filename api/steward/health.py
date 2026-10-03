"""GET /api/health probes (docs/02 §6): hermes, token_factory, tavily, mail_mode, model_primary.

Upstream probes are cached because the compose healthcheck (every 10 s) and the dashboard poll
this endpoint. No probe spends inference or search credit: Token Factory GET /models, Tavily
GET /usage, Hermes GET /health.

Tavily reports connector usability, not the health of its /usage endpoint, which rate-limits
far sooner than search does:
- 200 -> 'up', remembered as the last known good state, re-probed after 5 minutes;
- 429 -> keeps a known-good 'up' from the last 15 minutes, else 'down'; no new probe before
  the server's Retry-After (60 s by default), so polling never feeds the rate limit;
- 401/403 (key refused) -> 'down', and the last good state is forgotten;
- any other status or a connection error -> 'down', re-probed after 60 s.
A real web_search that succeeds (or is refused for the key) updates the same state.
"""

import time
from typing import Literal

import httpx

from steward.config import get_settings

UpDown = Literal["up", "down"]
UpDownNoKey = Literal["up", "down", "no_key"]

_CACHE_S = 30.0
TAVILY_UP_TTL_S = 300.0
TAVILY_DOWN_TTL_S = 60.0
TAVILY_KEEP_UP_S = 900.0
TAVILY_MAX_RETRY_AFTER_S = 900.0
# name -> (expires_at, value) for cached probe results; "tavily_ok" -> (seen_at, "up").
_cache: dict[str, tuple[float, str]] = {}


async def _cached(name: str, probe) -> str:
    hit = _cache.get(name)
    if hit and time.monotonic() < hit[0]:
        return hit[1]
    value = await probe()
    _cache[name] = (time.monotonic() + _CACHE_S, value)
    return value


def _retry_after(response: httpx.Response) -> float:
    try:
        seconds = float(response.headers.get("retry-after", ""))
    except ValueError:
        return TAVILY_DOWN_TTL_S
    return min(max(seconds, 1.0), TAVILY_MAX_RETRY_AFTER_S)


def note_tavily(status_code: int) -> None:
    """Called by the web_search connector after a real Tavily call."""
    now = time.monotonic()
    if status_code == 200:
        _cache["tavily_ok"] = (now, "up")
        _cache["tavily"] = (now + TAVILY_UP_TTL_S, "up")
    elif status_code in (401, 403):
        _cache.pop("tavily_ok", None)
        _cache["tavily"] = (now + TAVILY_DOWN_TTL_S, "down")


async def hermes_status(client: httpx.AsyncClient) -> UpDown:
    try:
        r = await client.get(f"{get_settings().hermes_api_url}/health", timeout=3.0)
        return "up" if r.status_code == 200 else "down"
    except httpx.HTTPError:
        return "down"


async def token_factory_status(client: httpx.AsyncClient) -> UpDownNoKey:
    s = get_settings()
    if not s.nebius_api_key:
        return "no_key"

    async def probe() -> str:
        try:
            r = await client.get(
                f"{s.token_factory_base_url}/models",
                timeout=5.0,
                headers={"Authorization": f"Bearer {s.nebius_api_key}"},
            )
            return "up" if r.status_code == 200 else "down"
        except httpx.HTTPError:
            return "down"

    return await _cached("token_factory", probe)  # type: ignore[return-value]


async def tavily_status(client: httpx.AsyncClient) -> UpDownNoKey:
    s = get_settings()
    if not s.tavily_api_key:
        return "no_key"
    hit = _cache.get("tavily")
    if hit and time.monotonic() < hit[0]:
        return hit[1]  # type: ignore[return-value]
    try:
        r = await client.get(
            "https://api.tavily.com/usage",
            timeout=5.0,
            headers={"Authorization": f"Bearer {s.tavily_api_key}"},
        )
    except httpx.HTTPError:
        value, ttl = "down", TAVILY_DOWN_TTL_S
    else:
        now = time.monotonic()
        if r.status_code == 200:
            _cache["tavily_ok"] = (now, "up")
            value, ttl = "up", TAVILY_UP_TTL_S
        elif r.status_code == 429:
            seen = _cache.get("tavily_ok")
            if seen is not None and now - seen[0] <= TAVILY_KEEP_UP_S:
                # Keep the known-good 'up', but never past 15 minutes after that evidence.
                value, ttl = "up", min(_retry_after(r), seen[0] + TAVILY_KEEP_UP_S - now)
            else:
                value, ttl = "down", _retry_after(r)
        else:
            if r.status_code in (401, 403):
                _cache.pop("tavily_ok", None)
            value, ttl = "down", TAVILY_DOWN_TTL_S
    _cache["tavily"] = (time.monotonic() + ttl, value)
    return value  # type: ignore[return-value]


async def health(client: httpx.AsyncClient) -> dict[str, object]:
    s = get_settings()
    return {
        "ok": True,  # steward-api itself is serving; connector state is in the other fields
        "hermes": await hermes_status(client),
        "token_factory": await token_factory_status(client),
        "tavily": await tavily_status(client),
        "mail_mode": s.mail_mode,
        "model_primary": s.model_primary,
    }
