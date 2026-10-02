"""GET /api/health probes (docs/02 §6): hermes, token_factory, tavily, mail_mode, model_primary.

Upstream probes are cached briefly because the compose healthcheck and the dashboard poll this
endpoint. No probe spends inference or search credit: Token Factory GET /models, Tavily
GET /usage, Hermes GET /health.
"""

import time
from typing import Literal

import httpx

from steward.config import get_settings

UpDown = Literal["up", "down"]
UpDownNoKey = Literal["up", "down", "no_key"]

_CACHE_S = 30.0
_cache: dict[str, tuple[float, str]] = {}


async def _cached(name: str, probe) -> str:
    hit = _cache.get(name)
    if hit and time.monotonic() - hit[0] < _CACHE_S:
        return hit[1]
    value = await probe()
    _cache[name] = (time.monotonic(), value)
    return value


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

    async def probe() -> str:
        try:
            r = await client.get(
                "https://api.tavily.com/usage",
                timeout=5.0,
                headers={"Authorization": f"Bearer {s.tavily_api_key}"},
            )
            return "up" if r.status_code == 200 else "down"
        except httpx.HTTPError:
            return "down"

    return await _cached("tavily", probe)  # type: ignore[return-value]


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
