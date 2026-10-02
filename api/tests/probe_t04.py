"""T0.4 model-dependent probes + DG-2 (docs/04 T0.4, docs/02 §10).

Real Token Factory calls; never part of `make test`. Run inside the compose network:

    docker compose run --rm --no-deps -v ./api/tests:/app/tests:ro steward-api \
        python -m tests.probe_t04 --model <Nemotron ID> --effort <value>

1. DG-2: tell the agent a new preference 5x (a different one each time, each in a new session).
   PASS if MEMORY.md/USER.md actually changes in >=4/5. Memories start from seed/memories.
2. Session continuity: the same X-Hermes-Session-Id reloads history (turn 2 recalls turn 1 and
   the second request carries turn 1's messages).
3. Frozen snapshot: a memory edit made between two turns of one session is NOT in that session's
   next system prompt, but IS in a new session's system prompt.

Prints a summary and writes /data/t03/probe_t04-<stamp>.json.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

import httpx

from steward import t03_experiment
from tests.harness_t03 import _read_jsonl, _settle

HERMES_DATA = Path(os.environ.get("HERMES_DATA_DIR", "/hermes-data"))
MEMORIES = HERMES_DATA / "memories"
SEED_MEMORIES = Path("/app/seed-memories")  # mounted from ./seed/memories (read-only)
DELIM = "\n§\n"

PREFERENCES = [
    "FYI — Rahul at Acme likes short, formal emails.",
    "FYI — Dr. Shah at Brightleaf prefers phone calls before 11 am IST.",
    "FYI — Li Wei at Kestrel wants a weekly status update every Friday.",
    "FYI — Tom Becker at Juniper & Co wants invoices as PDF attachments.",
    "FYI — Sara Khan at Orbitra Foods wants every quote in INR.",
]


def _files() -> dict[str, str]:
    out = {}
    for name in ("MEMORY.md", "USER.md"):
        path = MEMORIES / name
        out[name] = path.read_text(encoding="utf-8") if path.exists() else ""
    return out


def _digest(files: dict[str, str]) -> str:
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def _chat(
    client: httpx.Client, session: str, message: str, run_id: str, model: str, effort: str
) -> dict[str, Any]:
    t03_experiment.CONTROL_FILE.write_text(
        json.dumps(
            {"run_id": run_id, "model": model, "reasoning_effort": effort, "fixture": "plain"}
        ),
        encoding="utf-8",
    )
    started = time.monotonic()
    r = client.post(
        f"{os.environ.get('HERMES_API_URL', 'http://hermes:8642')}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['HERMES_API_KEY']}",
            "X-Hermes-Session-Id": session,
        },
        json={"model": "hermes-agent", "messages": [{"role": "user", "content": message}]},
        timeout=300.0,
    )
    latency = round(time.monotonic() - started, 1)
    body = r.json()
    reply = str(((body.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
    log = t03_experiment.RECORDINGS_DIR / run_id / "proxy.jsonl"
    _settle(log)
    records = _read_jsonl(log)
    tools = [
        c["function"]["name"]
        for rec in records
        if rec.get("status") == 200
        for ch in (rec.get("response") or {}).get("choices") or []
        for c in (ch.get("message") or {}).get("tool_calls") or []
    ]
    return {
        "status": r.status_code,
        "reply": reply,
        "latency_s": latency,
        "tools": tools,
        "records": records,
        "hermes": body.get("hermes"),
    }


def _system_prompt(records: list[dict[str, Any]]) -> str:
    for rec in records:
        msgs = (rec.get("request") or {}).get("messages") or []
        if rec.get("request", {}).get("tools") and msgs and msgs[0].get("role") == "system":
            return str(msgs[0].get("content") or "")
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="T0.4 probes + DG-2")
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", default="")
    args = parser.parse_args()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    report: dict[str, Any] = {"stamp": stamp, "model": args.model, "effort": args.effort}

    # Start DG-2 from the seed memories (what python -m steward.seed will copy in T1.1).
    MEMORIES.mkdir(parents=True, exist_ok=True)
    for name in ("MEMORY.md", "USER.md"):
        shutil.copyfile(SEED_MEMORIES / name, MEMORIES / name)

    with httpx.Client() as client:
        # --- DG-2 ---------------------------------------------------------------------------
        attempts = []
        for i, pref in enumerate(PREFERENCES, 1):
            before = _files()
            res = _chat(
                client, f"t04-dg2-{stamp}-{i}", pref, f"{stamp}-dg2-{i}", args.model, args.effort
            )
            after = _files()
            changed = _digest(before) != _digest(after)
            diff = "".join(
                difflib.unified_diff(
                    (before["MEMORY.md"] + "\n" + before["USER.md"]).splitlines(True),
                    (after["MEMORY.md"] + "\n" + after["USER.md"]).splitlines(True),
                    "before",
                    "after",
                )
            )
            attempts.append(
                {
                    "attempt": i,
                    "preference": pref,
                    "changed": changed,
                    "tools": res["tools"],
                    "reply": res["reply"][:300],
                    "latency_s": res["latency_s"],
                    "diff": diff,
                }
            )
            print(
                f"DG-2 attempt {i}: changed={changed} tools={res['tools']} {res['latency_s']}s",
                flush=True,
            )
        changed_count = sum(a["changed"] for a in attempts)
        report["dg2"] = {"attempts": attempts, "changed": changed_count, "pass": changed_count >= 4}
        report["memory_after_dg2"] = _files()

        # --- Session continuity ---------------------------------------------------------------
        sid = f"t04-cont-{stamp}"
        _chat(
            client,
            sid,
            "For this test my codename is BLUE-HERON-7. Reply only: OK.",
            f"{stamp}-cont-1",
            args.model,
            args.effort,
        )
        t2 = _chat(
            client,
            sid,
            "What is my codename? Reply with the codename only.",
            f"{stamp}-cont-2",
            args.model,
            args.effort,
        )
        second_req_msgs = []
        for rec in t2["records"]:
            msgs = (rec.get("request") or {}).get("messages") or []
            if msgs:
                second_req_msgs = msgs
                break
        carried = any("BLUE-HERON-7" in str(m.get("content")) for m in second_req_msgs[:-1])
        report["continuity"] = {
            "turn2_reply": t2["reply"][:200],
            "recalled": "BLUE-HERON-7" in t2["reply"],
            "history_in_request": carried,
            "turn2_message_roles": [m.get("role") for m in second_req_msgs],
        }
        print(f"continuity: recalled={'BLUE-HERON-7' in t2['reply']} carried={carried}", flush=True)

        # --- Frozen snapshot vs fresh snapshot -------------------------------------------------
        marker = f"Probe marker {stamp}: Maya's office plant is called Fern."
        sid_old = f"t04-snap-old-{stamp}"
        _chat(client, sid_old, "Reply only: OK.", f"{stamp}-snap-1", args.model, args.effort)
        mem = MEMORIES / "MEMORY.md"
        entries = [e for e in mem.read_text(encoding="utf-8").split(DELIM) if e.strip()]
        mem.write_text(DELIM.join([*entries, marker]), encoding="utf-8")  # like PUT /api/memory
        old2 = _chat(
            client, sid_old, "Reply only: OK again.", f"{stamp}-snap-2", args.model, args.effort
        )
        new1 = _chat(
            client,
            f"t04-snap-new-{stamp}",
            "Reply only: OK.",
            f"{stamp}-snap-3",
            args.model,
            args.effort,
        )
        report["snapshot"] = {
            "edit_in_existing_session": marker in _system_prompt(old2["records"]),
            "edit_in_new_session": marker in _system_prompt(new1["records"]),
        }
        print(
            "snapshot: existing_session_sees_edit="
            f"{report['snapshot']['edit_in_existing_session']} "
            f"new_session_sees_edit={report['snapshot']['edit_in_new_session']}",
            flush=True,
        )
        # Remove the probe marker again.
        mem.write_text(DELIM.join(entries), encoding="utf-8")

    t03_experiment.CONTROL_FILE.unlink(missing_ok=True)
    out = t03_experiment.T03_DIR / f"probe_t04-{stamp}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"DG-2: {'PASS' if report['dg2']['pass'] else 'FAIL'} ({changed_count}/5)")
    print(f"report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
