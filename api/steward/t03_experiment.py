"""T0.3/T0.4 experiment plumbing (M0 only; removed when T1.1/T2.2 replace the passthrough).

The DG-1 harness (api/tests/harness_t03.py) drives runs by writing a small control file,
/data/t03/control.json:

    {"run_id": "...", "model": "<Nemotron ID>", "reasoning_effort": "low" | "" ,
     "fixture": "plain" | "pseudonymized", "force_policy_block": false}

The passthrough proxy and the stub MCP server read it per request. Without a control file the
proxy uses MODEL_PRIMARY / REASONING_EFFORT and the stub serves the plain fixture.

Every proxied request/response body and every stub tool call is recorded under
/data/t03/recordings/<run_id>/ (gitignored ./data). Recordings hold bodies only, never headers,
so no bearer token is ever written. This is the T0.3 "record the request and response" step,
not logging: nothing here goes to stdout.
"""

import json
import os
import time
from pathlib import Path
from typing import Any

import anyio

T03_DIR = Path(os.environ.get("STEWARD_DB_PATH", "/data/steward.db")).parent / "t03"
CONTROL_FILE = T03_DIR / "control.json"
RECORDINGS_DIR = T03_DIR / "recordings"


def _read_control_sync() -> dict[str, Any]:
    try:
        return json.loads(CONTROL_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


async def read_control() -> dict[str, Any]:
    return await anyio.to_thread.run_sync(_read_control_sync)


def _safe_run_id(run_id: object) -> str:
    text = str(run_id or "adhoc")
    return "".join(ch for ch in text if ch.isalnum() or ch in "-_") or "adhoc"


def _append_sync(run_id: str, name: str, record: dict[str, Any]) -> None:
    run_dir = RECORDINGS_DIR / _safe_run_id(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / name).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


async def record(run_id: str, name: str, record_: dict[str, Any]) -> None:
    record_ = {"ts": time.time(), **record_}
    await anyio.to_thread.run_sync(_append_sync, run_id, name, record_)
