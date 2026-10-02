"""Async client for the Hermes API server (docs/02 §7a "Input"): one chat turn.

POST {HERMES_API_URL}/v1/chat/completions with model `hermes-agent`, ONLY the new user message,
Bearer HERMES_API_KEY, header X-Hermes-Session-Id (Hermes reloads the history for that session
from its state.db), non-streaming, 300 s timeout.

Error mapping (docs/02 §7a "Fallback"; T0.4 finding): Hermes reports a failed turn as HTTP 200
with `finish_reason: "error"` and `hermes.failed: true`, so the body is checked, not only the
status. A timeout means Hermes may still finish and queue actions.
"""

from typing import Any

import httpx

from steward.config import get_settings

TURN_TIMEOUT_S = 300.0
MODEL_UNAVAILABLE = "Model unavailable — this turn did not complete"
STILL_WORKING = "Still working — check Approvals and Activity"


class ChatTimeout(Exception):
    pass


class ChatFailed(Exception):
    pass


def session_id(reset_nonce: str, conversation_id: int) -> str:
    return f"steward-{reset_nonce}-{conversation_id}"


async def chat(client: httpx.AsyncClient, session: str, message: str) -> str:
    s = get_settings()
    try:
        r = await client.post(
            f"{s.hermes_api_url}/v1/chat/completions",
            headers={"Authorization": f"Bearer {s.hermes_api_key}", "X-Hermes-Session-Id": session},
            json={
                "model": "hermes-agent",
                "stream": False,
                "messages": [{"role": "user", "content": message}],
            },
            timeout=TURN_TIMEOUT_S,
        )
    except httpx.TimeoutException as exc:
        raise ChatTimeout(STILL_WORKING) from exc
    except httpx.HTTPError as exc:
        raise ChatFailed(MODEL_UNAVAILABLE) from exc
    if r.status_code != 200:  # e.g. 502 agent_incomplete
        raise ChatFailed(MODEL_UNAVAILABLE)
    try:
        body: dict[str, Any] = r.json()
        choice = (body.get("choices") or [{}])[0]
        reply = str((choice.get("message") or {}).get("content") or "")
    except (ValueError, AttributeError, IndexError) as exc:
        raise ChatFailed(MODEL_UNAVAILABLE) from exc
    meta = body.get("hermes") or {}
    if choice.get("finish_reason") == "error" or meta.get("failed") or not reply.strip():
        raise ChatFailed(MODEL_UNAVAILABLE)
    return reply
