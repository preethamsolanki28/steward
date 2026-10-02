"""/v1 proxy. T0.3: minimal PASSTHROUGH (docs/04 T0.3), not the Privacy Shield.

It verifies the bearer key, maps Hermes' `steward-auto` to the configured Nemotron ID, injects
reasoning_effort, forwards to Token Factory with stream:false and records the request/response.
It does NOT pseudonymize, leak-check, enforce the tool allowlist or write the ledger: that is
the full Shield pipeline of T2.1-T2.3. T1.1 carries this passthrough over; T2.2 replaces it.
"""

import hmac
import os
import time
from typing import Any

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from steward import t03_experiment

router = APIRouter()

# Per-attempt upstream timeout for the M0 experiment. Generous on purpose so DG-1 measures real
# turn latency; T2.2 sets the production rule (60 s per attempt, 1 retry, fallback chain).
UPSTREAM_TIMEOUT_S = 180.0

POLICY_BLOCK_BODY = {
    "error": {
        "message": "Blocked by Steward Privacy Shield: identifier would have left the Mac",
        "type": "invalid_request_error",
        "code": "steward_policy_block",
    }
}


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default) or default


def _authorized(request: Request) -> bool:
    expected = _env("STEWARD_PROXY_KEY")
    supplied = request.headers.get("authorization", "")
    return bool(expected) and hmac.compare_digest(supplied, f"Bearer {expected}")


def _error(status: int, message: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"message": message, "type": "invalid_request_error", "code": code}},
    )


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
    except ValueError:
        return _error(400, "Request body must be JSON", "invalid_json")
    if body.get("stream") is True:
        # Hermes runs with model.streaming:false and falls back on this 400 (docs/02 §7a step 1).
        return _error(400, "stream not supported; send stream:false", "stream_not_supported")

    control = await t03_experiment.read_control()
    run_id = str(control.get("run_id") or "adhoc")
    requested_model = body.get("model")

    if control.get("force_policy_block"):
        # T0.4 probe only: how does Hermes surface a 400 steward_policy_block?
        await t03_experiment.record(
            run_id,
            "proxy.jsonl",
            {
                "requested_model": requested_model,
                "request": body,
                "status": 400,
                "response": POLICY_BLOCK_BODY,
                "latency_ms": 0,
                "forced_policy_block": True,
            },
        )
        return JSONResponse(status_code=400, content=POLICY_BLOCK_BODY)

    upstream_body = dict(body)
    upstream_body["model"] = control.get("model") or _env(
        "MODEL_PRIMARY", "nvidia/Nemotron-3_5-Lightning"
    )
    upstream_body["stream"] = False
    effort = control.get("reasoning_effort", _env("REASONING_EFFORT"))
    if effort:
        upstream_body["reasoning_effort"] = effort

    if not _env("NEBIUS_API_KEY"):
        # Fail fast: an empty key would make an invalid header, and Hermes retries 5xx for minutes.
        missing = {"error": {"message": "NEBIUS_API_KEY is not set", "code": "no_upstream_key"}}
        await t03_experiment.record(
            run_id,
            "proxy.jsonl",
            {
                "requested_model": requested_model,
                "request": upstream_body,
                "status": 401,
                "response": missing,
                "latency_ms": 0,
            },
        )
        return JSONResponse(status_code=401, content=missing)

    base_url = _env("TOKEN_FACTORY_BASE_URL", "https://api.tokenfactory.nebius.com/v1").rstrip("/")
    client: httpx.AsyncClient = request.app.state.http
    started = time.monotonic()
    try:
        upstream = await client.post(
            f"{base_url}/chat/completions",
            json=upstream_body,
            headers={"Authorization": f"Bearer {_env('NEBIUS_API_KEY')}"},
            timeout=UPSTREAM_TIMEOUT_S,
        )
        status = upstream.status_code
        try:
            payload: Any = upstream.json()
        except ValueError:
            payload = {"error": {"message": upstream.text[:500], "code": "upstream_non_json"}}
    except httpx.HTTPError as exc:
        status = 502
        payload = {
            "error": {"message": f"upstream error: {type(exc).__name__}", "code": "upstream_error"}
        }
    latency_ms = int((time.monotonic() - started) * 1000)

    await t03_experiment.record(
        run_id,
        "proxy.jsonl",
        {
            "requested_model": requested_model,
            "request": upstream_body,
            "status": status,
            "response": payload,
            "latency_ms": latency_ms,
        },
    )
    return JSONResponse(status_code=status, content=payload)
