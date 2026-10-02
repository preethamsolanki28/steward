"""/v1 Privacy Shield proxy (docs/02 §7a steps 1-10). Called by Hermes only.

1. Bearer STEWARD_PROXY_KEY; stream:true -> 400; any other /v1/* path -> 404 + blocked row.
2. Tool allowlist: tools[] names outside ALLOWED_TOOLS -> policy block.
3. The requested model is ignored: settings.model_primary -> model_fallback -> MODEL_FALLBACK_2;
   settings.reasoning_effort injected; upstream always stream:false.
4-6. Neutralize inbound [[ ]], pseudonymize every string leaf (walk_strings) via the vault.
7. Leak check over every outbound leaf; ANY hit or ANY Shield error -> nothing is sent:
   policy_block audit + 'blocked' ledger row (offending spans «BLOCKED:KIND») + 400
   steward_policy_block (Hermes surfaces a 400 without retrying, T0.4).
8. Token Factory: 60 s per attempt, 1 retry on 429/5xx honoring retry-after / x-ratelimit, then one
   walk of the chain. Malformed tool-call JSON, or empty content where a tool call was expected,
   -> one retry on model_fallback, recorded as escalated_from.
9. Re-identify every response leaf. 10. Ledger row + audit row.
If every model fails, the proxy answers 400 steward_upstream_unavailable: a 4xx so Hermes does not
retry it for minutes (it retries 5xx, T0.4); /api/chat maps it to "Model unavailable".
"""

import asyncio
import hmac
import json
import re
import sqlite3
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from steward import db
from steward.config import get_settings
from steward.ledger import pricing, store
from steward.shield import Shield

router = APIRouter()

UPSTREAM_TIMEOUT_S = 60.0
MAX_RETRY_WAIT_S = 10.0
STEWARD_TOOLS = (
    "mail_search",
    "mail_read",
    "mail_send",
    "files_list",
    "files_read",
    "files_write",
    "contacts_lookup",
    "web_search",
    "brief_save",
)
# Exact names the model sees (T0.4). skill_manage: user decision 2026-10-02 (its writes are
# staged by skills.write_approval: true and the skills dir is read-only).
ALLOWED_TOOLS = frozenset(
    {f"mcp__steward__{t}" for t in STEWARD_TOOLS}
    | {"memory", "session_search", "skill_view", "skills_list", "skill_manage"}
)


def _error(status: int, message: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"message": message, "type": "invalid_request_error", "code": code}},
    )


def _policy_block() -> JSONResponse:
    return _error(
        400,
        "Blocked by Steward Privacy Shield: identifier would have left the Mac",
        "steward_policy_block",
    )


def _authorized(request: Request) -> bool:
    expected = get_settings().steward_proxy_key
    supplied = request.headers.get("authorization", "")
    return bool(expected) and hmac.compare_digest(supplied, f"Bearer {expected}")


def _destination() -> str:
    return urlparse(get_settings().token_factory_base_url).hostname or "unknown"


@dataclass
class Chain:
    models: list[str]
    reasoning_effort: str


def _chain(conn: sqlite3.Connection) -> Chain:
    s = get_settings()
    primary = db.get_setting(conn, "model_primary") or s.model_primary
    fallback = db.get_setting(conn, "model_fallback") or s.model_fallback
    effort = db.get_setting(conn, "reasoning_effort")
    models: list[str] = []
    for m in (primary, fallback, s.model_fallback_2):
        if m and m not in models:
            models.append(m)
    return Chain(models, s.reasoning_effort if effort is None else effort)


def _tool_names(body: dict[str, Any]) -> list[str]:
    names = []
    for tool in body.get("tools") or []:
        if isinstance(tool, dict):
            raw_fn = tool.get("function")
            fn: dict[str, Any] = raw_fn if isinstance(raw_fn, dict) else {}
            names.append(str(fn.get("name") or tool.get("name") or ""))
        else:
            names.append(str(tool))
    return names


async def _block(masked: dict[str, Any] | None, count: int, kinds: dict[str, int]) -> JSONResponse:
    stored = masked if masked is not None else {"error": "request not stored (shield error)"}

    def write(conn: sqlite3.Connection) -> None:
        store.insert(
            conn,
            channel="llm",
            destination=_destination(),
            status="blocked",
            request_redacted=stored,
            entities_masked=count,
            entity_kinds=kinds,
        )

    await db.run(write)
    return _policy_block()


@router.get("/v1/models")
async def models(request: Request) -> JSONResponse:
    if not _authorized(request):
        return _error(401, "Invalid proxy key", "invalid_api_key")
    return JSONResponse({"data": [{"id": "steward-auto", "context_length": 131072}]})


@router.post("/v1/chat/completions")
async def chat_completions(request: Request) -> JSONResponse:
    if not _authorized(request):
        return _error(401, "Invalid proxy key", "invalid_api_key")
    try:
        body: dict[str, Any] = await request.json()
        if not isinstance(body, dict):
            raise ValueError
    except ValueError:
        return _error(400, "Request body must be a JSON object", "invalid_json")
    if body.get("stream") is True:
        return _error(400, "stream not supported; send stream:false", "stream_not_supported")

    # Steps 2-7 in a worker thread (vault writes + CPU work); fail closed on any error.
    def shield_out(conn: sqlite3.Connection):
        result = Shield(conn).outbound(body)
        disallowed = [n for n in _tool_names(body) if n not in ALLOWED_TOOLS]
        return result, disallowed, _chain(conn)

    try:
        result, disallowed, chain = await db.run(shield_out)
    except Exception:
        return await _block(None, 0, {})
    if disallowed:
        stored = {**(result.blocked_request or result.request), "steward_blocked_tools": disallowed}
        return await _block(stored, result.masked, result.kinds)
    if result.leaks:
        return await _block(result.blocked_request, result.masked, result.kinds)

    upstream_body = dict(result.request)
    upstream_body["stream"] = False
    if chain.reasoning_effort:
        upstream_body["reasoning_effort"] = chain.reasoning_effort
    expects_tool = bool(body.get("tools"))

    started = time.monotonic()
    outcome = await _call_chain(request.app.state.http, upstream_body, chain, expects_tool)
    latency = int((time.monotonic() - started) * 1000)

    def finish(conn: sqlite3.Connection) -> Any:
        sent = {**upstream_body, "model": outcome.model} if outcome.model else upstream_body
        if outcome.response is None:
            store.insert(
                conn,
                channel="llm",
                destination=_destination(),
                status="error",
                model=outcome.model,
                request_redacted=sent,
                response_redacted={"error": outcome.error},
                entities_masked=result.masked,
                entity_kinds=result.kinds,
                latency_ms=latency,
            )
            return None
        usage = outcome.response.get("usage") or {}
        pt, ct = int(usage.get("prompt_tokens") or 0), int(usage.get("completion_tokens") or 0)
        store.insert(
            conn,
            channel="llm",
            destination=_destination(),
            status="ok",
            model=outcome.model,
            escalated_from=outcome.escalated_from,
            request_redacted=sent,
            response_redacted=outcome.response,
            entities_masked=result.masked,
            entity_kinds=result.kinds,
            prompt_tokens=pt,
            completion_tokens=ct,
            latency_ms=latency,
            cost_usd=pricing.cost_usd(outcome.model, pt, ct),
        )
        restored, _, _ = Shield(conn).inbound(outcome.response)
        return restored

    try:
        restored = await db.run(finish)
    except Exception:
        return _error(
            400,
            "Model unavailable: response could not be processed",
            "steward_upstream_unavailable",
        )
    if restored is None:
        return _error(400, f"Model unavailable: {outcome.error}", "steward_upstream_unavailable")
    return JSONResponse(restored)


@router.api_route("/v1/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def other_v1(path: str, request: Request) -> JSONResponse:
    if not _authorized(request):
        return _error(401, "Invalid proxy key", "invalid_api_key")

    def write(conn: sqlite3.Connection) -> None:
        # Never store the body of an unknown request: only its method and path.
        store.insert(
            conn,
            channel="llm",
            destination=_destination(),
            status="blocked",
            request_redacted={"method": request.method, "path": f"/v1/{path}"},
        )

    await db.run(write)
    return _error(404, "Not found", "not_found")


# --- upstream ----------------------------------------------------------------------------------


@dataclass
class Outcome:
    response: dict[str, Any] | None
    model: str | None
    escalated_from: str | None
    error: str


_DURATION = re.compile(r"^\s*([\d.]+)\s*(ms|s|m)?\s*$")


def _retry_wait(headers: httpx.Headers) -> float:
    for name in ("retry-after", "x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"):
        m = _DURATION.match(headers.get(name) or "")
        if m:
            value, unit = float(m.group(1)), m.group(2) or "s"
            seconds = value / 1000 if unit == "ms" else value * 60 if unit == "m" else value
            return max(0.0, min(seconds, MAX_RETRY_WAIT_S))
    return 1.0


async def _attempt(client: httpx.AsyncClient, body: dict[str, Any], model: str) -> httpx.Response:
    s = get_settings()
    return await client.post(
        f"{s.token_factory_base_url}/chat/completions",
        json={**body, "model": model},
        headers={"Authorization": f"Bearer {s.nebius_api_key}"},
        timeout=UPSTREAM_TIMEOUT_S,
    )


def _retriable(status: int) -> bool:
    return status == 429 or status >= 500


async def _call_model(
    client: httpx.AsyncClient, body: dict[str, Any], model: str
) -> httpx.Response:
    r = await _attempt(client, body, model)
    if _retriable(r.status_code):
        await asyncio.sleep(_retry_wait(r.headers))
        r = await _attempt(client, body, model)
    return r


def _malformed(response: dict[str, Any], expects_tool: bool) -> bool:
    try:
        message = (response.get("choices") or [{}])[0].get("message") or {}
    except (AttributeError, IndexError):
        return True
    calls = message.get("tool_calls") or []
    for call in calls:
        try:
            parsed = json.loads((call.get("function") or {}).get("arguments") or "")
        except (TypeError, ValueError):
            return True
        if not isinstance(parsed, dict):
            return True
    content = message.get("content")
    return expects_tool and not calls and not (isinstance(content, str) and content.strip())


async def _call_chain(
    client: httpx.AsyncClient, body: dict[str, Any], chain: Chain, expects_tool: bool
) -> Outcome:
    if not get_settings().nebius_api_key:
        return Outcome(None, None, None, "NEBIUS_API_KEY is not set")
    errors: list[str] = []
    fallback = chain.models[1] if len(chain.models) > 1 else None
    for model in chain.models:
        try:
            r = await _call_model(client, body, model)
        except httpx.HTTPError as exc:
            errors.append(f"{model}: {type(exc).__name__}")
            continue
        if r.status_code == 200:
            try:
                data = r.json()
            except ValueError:
                errors.append(f"{model}: non-JSON response")
                continue
            if _malformed(data, expects_tool) and fallback and fallback != model:
                try:
                    r2 = await _call_model(client, body, fallback)
                    if r2.status_code == 200:
                        data2 = r2.json()
                        if not _malformed(data2, expects_tool):
                            return Outcome(data2, fallback, model, "")
                except (httpx.HTTPError, ValueError):
                    pass
            return Outcome(data, model, None, "")
        errors.append(f"{model}: HTTP {r.status_code}")
        if not _retriable(r.status_code):
            break  # 4xx (bad key, bad request): another model will not fix it
    return Outcome(None, None, None, "; ".join(errors) or "no model configured")
