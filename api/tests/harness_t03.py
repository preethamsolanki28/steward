"""T0.3 riskiest-assumption harness + DG-1 scorer (docs/04 T0.3, docs/02 §10).

M0 artifact: it drove the T0.3 stub MCP server (retired in T1.3, which reads the seed data
instead of the fixture). TODO(T2.5): adapt it to the real steward-tools before re-running DG-1
through the full Shield.

Runs the invoice-chase prompt N times (default 10) for each of {Lightning, Super} x {plain,
pseudonymized} through the real chain: Hermes (pinned image) -> T0.3 passthrough proxy ->
Nebius Token Factory, with the stub `steward` MCP server over the self-contained Acme fixture.

It makes REAL Token Factory calls and spends credit, so it is never part of `make test`. Run it
deliberately, inside the compose network (Hermes 8642 is not published):

    docker compose run --rm --no-deps -v ./api/tests:/app/tests:ro steward-api \
        python -m tests.harness_t03 [--runs 10] [--effort low]

Per run it records: tool order + JSON-arg validity, placeholder integrity in the draft,
end-to-end turn latency and tokens. Results go to /data/t03/results-<stamp>.json, and the
4-row DG-1 table is printed in the docs/02 format.

DG-1 PASS (docs/04): for at least one model, >=8/10 runs call the right tools in order with
valid JSON args, >=95% of placeholders come back intact in the draft, and p50 end-to-end turn
latency <=45 s. The gate is applied to each model's PSEUDONYMIZED row (the production path);
the plain row is the control that shows what pseudonymization costs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from steward import t03_experiment, t03_fixture

MODELS = {
    "Lightning": "nvidia/Nemotron-3_5-Lightning",
    "Super": "nvidia/nemotron-3-super-120b-a12b",
}
FIXTURES: tuple[t03_fixture.FixtureName, ...] = ("plain", "pseudonymized")
TURN_TIMEOUT_S = 300.0  # same as /api/chat -> Hermes (docs/02 §7a)

STEWARD_TOOL = re.compile(r"^mcp_{1,2}steward_{1,2}(files_read|mail_search|mail_send)$")
TOLERANT_PLACEHOLDER = re.compile(r"\[{1,2}\s*([A-Za-z]+)_(\d+)\s*\]{1,2}")
CANONICAL_PLACEHOLDER = re.compile(r"^\[\[[A-Z]+_\d+\]\]$")

REQUIRED_ARGS: dict[str, dict[str, type]] = {
    "files_read": {"path": str},
    "mail_search": {"query": str},
    "mail_send": {"to": list, "subject": str, "body": str},
}

DG1_MIN_SUCCESS = 8
DG1_MIN_INTEGRITY = 0.95
DG1_MAX_P50_S = 45.0


@dataclass
class RunResult:
    run_id: str
    model: str
    fixture: str
    hermes_status: int | None
    latency_s: float
    reply: str
    proxy_calls: int
    proxy_errors: list[int]
    tokens: int
    executed_tools: list[str]
    model_tool_calls: list[str]
    invalid_json_args: list[str]
    order_ok: bool
    json_ok: bool
    completed: bool
    success: bool
    recipient_ok: bool
    placeholders_total: int
    placeholders_intact: int
    bad_placeholders: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _short_tool(name: str) -> str | None:
    match = STEWARD_TOOL.match(name)
    return match.group(1) if match else None


def _validate_args(short: str | None, raw: Any) -> str | None:
    """None if the raw tool-call arguments are a valid JSON object for the tool, else a reason."""
    try:
        args = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        return "not JSON"
    if not isinstance(args, dict):
        return "not a JSON object"
    for key, typ in REQUIRED_ARGS.get(short or "", {}).items():
        if not isinstance(args.get(key), typ):
            return f"missing/invalid '{key}'"
    if short == "mail_send" and not (args["to"] and all(isinstance(t, str) for t in args["to"])):
        return "'to' must be a non-empty list of strings"
    return None


def score_run(
    run_id: str,
    model: str,
    fixture: t03_fixture.FixtureName,
    hermes_status: int | None,
    latency_s: float,
    reply: str,
    proxy_records: list[dict[str, Any]],
    tool_records: list[dict[str, Any]],
) -> RunResult:
    notes: list[str] = []
    tokens = 0
    model_tool_calls: list[str] = []
    invalid: list[str] = []
    proxy_errors = [int(r.get("status") or 0) for r in proxy_records if r.get("status") != 200]
    for rec in proxy_records:
        resp = rec.get("response") or {}
        if rec.get("status") != 200 or not isinstance(resp, dict):
            continue
        usage = resp.get("usage") or {}
        tokens += int(usage.get("prompt_tokens") or 0) + int(usage.get("completion_tokens") or 0)
        for choice in resp.get("choices") or []:
            for call in (choice.get("message") or {}).get("tool_calls") or []:
                fn = call.get("function") or {}
                name = str(fn.get("name") or "")
                model_tool_calls.append(name)
                reason = _validate_args(_short_tool(name), fn.get("arguments"))
                if reason:
                    invalid.append(f"{name}: {reason}")

    executed = [str(r.get("tool")) for r in tool_records]
    sends = [i for i, t in enumerate(executed) if t == "mail_send"]
    reads = [i for i, t in enumerate(executed) if t == "files_read"]
    searches = [i for i, t in enumerate(executed) if t == "mail_search"]
    order_ok = (
        len(sends) == 1 and any(i < sends[0] for i in reads) and any(i < sends[0] for i in searches)
    )
    if len(sends) != 1:
        notes.append(f"mail_send executed {len(sends)}x")
    json_ok = not invalid
    completed = hermes_status == 200 and not proxy_errors and bool(proxy_records)
    if proxy_errors:
        notes.append(f"proxy/upstream errors: {proxy_errors}")

    send_args: dict[str, Any] = next(
        (r.get("args") or {} for r in tool_records if r.get("tool") == "mail_send"), {}
    )
    recipient_ok = send_args.get("to") == [t03_fixture.expected_recipient(fixture)]

    total = intact = 0
    bad: list[str] = []
    if fixture == "pseudonymized":
        draft = " ".join(
            [
                " ".join(map(str, send_args.get("to") or [])),
                str(send_args.get("subject") or ""),
                str(send_args.get("body") or ""),
                reply,
            ]
        )
        for match in TOLERANT_PLACEHOLDER.finditer(draft):
            total += 1
            text = match.group(0)
            if CANONICAL_PLACEHOLDER.match(text) and text in t03_fixture.PLACEHOLDER_VOCAB:
                intact += 1
            else:
                bad.append(text)
        if total == 0:
            notes.append("no placeholders in draft")

    return RunResult(
        run_id=run_id,
        model=model,
        fixture=fixture,
        hermes_status=hermes_status,
        latency_s=round(latency_s, 2),
        reply=reply,
        proxy_calls=len(proxy_records),
        proxy_errors=proxy_errors,
        tokens=tokens,
        executed_tools=executed,
        model_tool_calls=model_tool_calls,
        invalid_json_args=invalid,
        order_ok=order_ok,
        json_ok=json_ok,
        completed=completed,
        success=completed and order_ok and json_ok,
        recipient_ok=recipient_ok,
        placeholders_total=total,
        placeholders_intact=intact,
        bad_placeholders=bad,
        notes=notes,
    )


def summarize(results: list[RunResult]) -> list[dict[str, Any]]:
    rows = []
    for label, model in MODELS.items():
        for fixture in FIXTURES:
            runs = [r for r in results if r.model == model and r.fixture == fixture]
            if not runs:
                continue
            total = sum(r.placeholders_total for r in runs)
            intact = sum(r.placeholders_intact for r in runs)
            rows.append(
                {
                    "label": label,
                    "model": model,
                    "fixture": fixture,
                    "runs": len(runs),
                    "success": sum(r.success for r in runs),
                    "recipient_ok": sum(r.recipient_ok for r in runs),
                    "integrity": (intact / total)
                    if (fixture == "pseudonymized" and total)
                    else None,
                    "placeholders": f"{intact}/{total}" if fixture == "pseudonymized" else "n/a",
                    "p50_latency_s": round(statistics.median(r.latency_s for r in runs), 1),
                    "mean_tokens": round(statistics.mean(r.tokens for r in runs)),
                }
            )
    return rows


def dg1_verdict(rows: list[dict[str, Any]]) -> dict[str, Any]:
    per_model = {}
    for row in rows:
        if row["fixture"] != "pseudonymized":
            continue
        passed = (
            row["runs"] >= 10
            and row["success"] >= DG1_MIN_SUCCESS
            and row["integrity"] is not None
            and row["integrity"] >= DG1_MIN_INTEGRITY
            and row["p50_latency_s"] <= DG1_MAX_P50_S
        )
        per_model[row["model"]] = passed
    return {"pass": any(per_model.values()), "per_model": per_model}


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Model | Fixture | Tool-order success (of 10) | Placeholder integrity | p50 latency "
        "| Tokens |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        integrity = (
            f"{r['integrity'] * 100:.1f}% ({r['placeholders']})"
            if r["integrity"] is not None
            else ("n/a" if r["fixture"] == "plain" else f"none in draft ({r['placeholders']})")
        )
        lines.append(
            f"| `{r['model']}` | {r['fixture']} | {r['success']}/{r['runs']} | {integrity} | "
            f"{r['p50_latency_s']} s | {r['mean_tokens']} per run |"
        )
    return "\n".join(lines)


def _write_control(control: dict[str, Any]) -> None:
    t03_experiment.CONTROL_FILE.parent.mkdir(parents=True, exist_ok=True)
    t03_experiment.CONTROL_FILE.write_text(json.dumps(control), encoding="utf-8")


def _settle(proxy_log: Path, quiet_s: float = 20.0, max_s: float = 120.0) -> None:
    """Wait until the proxy has been quiet for quiet_s: Hermes makes an auxiliary call (no
    tools, short prompt) AFTER replying, and it must be attributed to this run, not the next.
    Not part of the measured turn latency."""
    deadline = time.monotonic() + max_s
    last_count, last_change = -1, time.monotonic()
    while time.monotonic() < deadline:
        count = len(_read_jsonl(proxy_log))
        if count != last_count:
            last_count, last_change = count, time.monotonic()
        elif time.monotonic() - last_change >= quiet_s:
            return
        time.sleep(1.0)


def run_once(
    client: Any, run_id: str, model: str, fixture: t03_fixture.FixtureName, effort: str
) -> RunResult:
    _write_control(
        {"run_id": run_id, "model": model, "reasoning_effort": effort, "fixture": fixture}
    )
    started = time.monotonic()
    status: int | None = None
    reply = ""
    try:
        response = client.post(
            f"{os.environ.get('HERMES_API_URL', 'http://hermes:8642')}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['HERMES_API_KEY']}",
                "X-Hermes-Session-Id": f"t03-{run_id}",
            },
            json={
                "model": "hermes-agent",
                "messages": [{"role": "user", "content": t03_fixture.prompt(fixture)}],
            },
            timeout=TURN_TIMEOUT_S,
        )
        status = response.status_code
        body = response.json()
        reply = str(((body.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
    except Exception as exc:  # timeout or transport error: the run fails, the harness goes on
        reply = f"<harness error: {type(exc).__name__}>"
    latency = time.monotonic() - started
    run_dir = t03_experiment.RECORDINGS_DIR / run_id
    _settle(run_dir / "proxy.jsonl")
    return score_run(
        run_id,
        model,
        fixture,
        status,
        latency,
        reply,
        _read_jsonl(run_dir / "proxy.jsonl"),
        _read_jsonl(run_dir / "tools.jsonl"),
    )


def main(argv: list[str] | None = None) -> int:
    import httpx

    parser = argparse.ArgumentParser(description="T0.3 DG-1 harness")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--effort", default=os.environ.get("REASONING_EFFORT", ""))
    parser.add_argument("--models", default=",".join(MODELS))
    parser.add_argument("--fixtures", default=",".join(FIXTURES))
    args = parser.parse_args(argv)

    if not os.environ.get("NEBIUS_API_KEY"):
        print(
            "NEBIUS_API_KEY is not set: refusing to start (every run would fail).", file=sys.stderr
        )
        return 2
    labels = [m.strip() for m in args.models.split(",") if m.strip()]
    fixtures = [f.strip() for f in args.fixtures.split(",") if f.strip()]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    results: list[RunResult] = []
    with httpx.Client() as client:
        for label in labels:
            for fixture in fixtures:
                for i in range(1, args.runs + 1):
                    run_id = f"{stamp}-{label}-{fixture}-{i:02d}"
                    result = run_once(client, run_id, MODELS[label], fixture, args.effort)  # type: ignore[arg-type]
                    results.append(result)
                    print(
                        f"{run_id}: success={result.success} order={result.order_ok} "
                        f"json={result.json_ok} recipient={result.recipient_ok} "
                        f"ph={result.placeholders_intact}/{result.placeholders_total} "
                        f"{result.latency_s}s tokens={result.tokens} "
                        f"tools={result.executed_tools} {'; '.join(result.notes)}",
                        flush=True,
                    )
    t03_experiment.CONTROL_FILE.unlink(missing_ok=True)

    rows = summarize(results)
    verdict = dg1_verdict(rows)
    out = t03_experiment.T03_DIR / f"results-{stamp}.json"
    out.write_text(
        json.dumps(
            {
                "stamp": stamp,
                "reasoning_effort": args.effort,
                "rows": rows,
                "verdict": verdict,
                "runs": [asdict(r) for r in results],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print("\n" + markdown_table(rows))
    print(f"\nreasoning_effort: {args.effort or '(not sent)'}")
    print(f"DG-1: {'PASS' if verdict['pass'] else 'FAIL'} {verdict['per_model']}")
    print(f"results: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
