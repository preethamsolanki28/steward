"""DG-1 harness (T0.3), re-run through the FULL Privacy Shield (T2.5).

Each run is one fresh "Chase the Acme invoice" conversation through the real path:
POST /api/chat -> Hermes -> /v1 Shield proxy (pseudonymize, leak check, re-identify) ->
Nebius Token Factory, with the real steward-tools over the seed data. The model under test is set
as settings.model_primary for its batch (the proxy reads the chain from settings) and restored
afterwards.

Per run it records, from the ledger and the audit log:
- tool order: files_read and mail_search executed (mail_send arrives in T3.1, so the DG-1
  "queue mail_send" step is measured as a correct draft in the reply instead);
- argument validity of every tool call the model emitted (ledger response_redacted), as in T0.3:
  a JSON object that matches the schema of an offered tool (the tools[] of that same request:
  required keys present, no unknown keys, top-level types). A JSON-only count is also reported.
  Only calls the model made before /api/chat returned are scored; Hermes' post-reply calls
  (session title, background skill curator) are reported but not scored. Calls to
  mcp__steward__mail_send are counted separately: the skill names it, but the tool and its
  schema only exist from T3.1, and Hermes auto-repairs the unknown name to mail_read;
- whether Hermes paused the steward MCP server (its circuit breaker after 3 rejected calls);
- placeholder integrity: of the placeholder-like tokens Nemotron emitted (bracketed, or bare
  like "ORG_1"), the share that is exact canonical syntax AND a known vault placeholder. The
  DG-1 gate uses the draft (the final assistant message: "placeholders come back intact in the
  draft"); turn outputs (incl. tool args) and all model output (incl. the session title and the
  background curator) are reported too;
- the re-identified reply: greets Rahul, names INV-0042 and $4,800, and contains no
  placeholder-like token (bracketed or bare);
- zero Shield blocks; end-to-end turn latency; tokens (incl. the session-title auxiliary call).

DG-1 PASS (docs/04): for at least one model, >=8/10 runs succeed, >=95% placeholder integrity,
p50 turn latency <=45 s.

Real Token Factory calls (spends credit); never part of `make test`. Run inside the network:

    docker compose run --rm --no-deps -v ./api/tests:/app/tests:ro steward-api \
        python -m tests.harness_t03 [--runs 10]
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

MODELS = {
    "Lightning": "nvidia/Nemotron-3_5-Lightning",
    "Super": "nvidia/nemotron-3-super-120b-a12b",
}
PROMPT = "Chase the Acme invoice"
TURN_TIMEOUT_S = 300.0
TOLERANT = re.compile(r"\[{1,2}\s*([A-Za-z]+)_(\d+)\s*\]{1,2}")
MAIL_SEND = "mcp__steward__mail_send"
CANONICAL = re.compile(r"^\[\[[A-Z]+_\d+\]\]$")
# A placeholder whose brackets the model dropped ("ORG_1", "PERSON 3"). The re-identifier's
# tolerant matcher (docs/04 T2.1) needs brackets, so these reach the user unresolved.
BARE = re.compile(r"(?<![\w⟦])(?:PERSON|ORG|EMAIL|DOMAIN|PHONE|ACCOUNT|MONEY)[ _]\d+(?!\w)")


def placeholder_like(text: str) -> list[str]:
    """Every placeholder-shaped token: bracketed (tolerant) ones plus bare ones."""
    found = [(m.start(), m.end(), m.group(0)) for m in TOLERANT.finditer(text)]
    found += [
        (m.start(), m.end(), m.group(0))
        for m in BARE.finditer(text)
        if not any(a <= m.start() < b for a, b, _ in found)
    ]
    return [t for _, _, t in sorted(found)]


DG1_MIN_SUCCESS, DG1_MIN_INTEGRITY, DG1_MAX_P50_S = 8, 0.95, 45.0


@dataclass
class Run:
    label: str
    model: str
    status: int | None
    latency_s: float
    reply: str
    tools: list[str]
    llm_rows: int
    blocked_rows: int
    error_rows: int
    escalations: int
    tokens: int
    invalid_args: list[str]
    placeholders_total: int  # every model output in the window (turn, title, curator)
    placeholders_intact: int
    turn_placeholders_total: int  # outputs before /api/chat returned (content + tool args)
    turn_placeholders_intact: int
    draft_placeholders_total: int  # the final assistant message = the draft (DG-1 criterion)
    draft_placeholders_intact: int
    unresolved_in_reply: int
    order_ok: bool
    json_ok: bool
    schema_ok: bool
    draft_ok: bool
    mcp_paused: bool
    mail_send_attempts: int
    post_turn_schema_errors: list[str]
    success: bool
    success_json_only: bool
    notes: list[str] = field(default_factory=list)
    window: dict[str, int] = field(default_factory=dict)


_TYPES: dict[str, type | tuple[type, ...]] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
}


TRUSTED_RAHUL = "rahul.verma@acme-logistics.example"


def _flat(text: str) -> str:
    return text.replace("\u2011", "-").replace("\u202f", " ")


def _draft_content_ok(text: str) -> bool:
    return (
        bool(re.search(r"\b(Dear|Hi|Hello)\s+Rahul\b", text))
        and "INV-0042" in text
        and "4,800" in text
        and not placeholder_like(text)
    )


def tool_schemas(request_redacted: str | None) -> dict[str, dict[str, Any]]:
    try:
        req = json.loads(request_redacted or "null")
    except ValueError:
        return {}
    if not isinstance(req, dict):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for tool in req.get("tools") or []:
        fn = (tool or {}).get("function") or {}
        if fn.get("name"):
            out[fn["name"]] = fn.get("parameters") or {}
    return out


def schema_errors(name: str, args: Any, schemas: dict[str, dict[str, Any]]) -> list[str]:
    if name not in schemas:
        return [f"{name}: not an offered tool"]
    if not isinstance(args, dict):
        return [f"{name}: arguments are not a JSON object"]
    schema = schemas[name]
    props = schema.get("properties") or {}
    errs = [f"{name}: missing '{k}'" for k in schema.get("required") or [] if k not in args]
    if props and schema.get("additionalProperties") is not True:
        errs += [f"{name}: unknown '{k}'" for k in args if k not in props]
    for key, value in args.items():
        kind = (props.get(key) or {}).get("type")
        py = _TYPES.get(kind) if isinstance(kind, str) else None
        if py and (not isinstance(value, py) or (kind != "boolean" and isinstance(value, bool))):
            errs.append(f"{name}: '{key}' is not {kind}")
    return errs


def is_path_probe(r: dict[str, Any]) -> bool:
    """An unknown /v1/* request (Hermes sends GET /v1/props on its first model call after a
    restart): 404 + a 'blocked' ledger row holding only {method, path} by design (docs/02 §7a
    step 2). It is not part of the turn, so it is reported but not scored as a Shield block."""
    try:
        req = json.loads(r.get("request_redacted") or "null")
    except ValueError:
        return False
    return isinstance(req, dict) and set(req) == {"method", "path"}


def score(
    label: str,
    model: str,
    status: int | None,
    latency: float,
    reply: str,
    rows: list[dict[str, Any]],
    tools: list[str],
    vault: set[str],
    turn_max_id: int | None = None,
    queued: list[dict[str, Any]] | None = None,
) -> Run:
    """queued: the actions rows created during the run ({tool, args_json, risk}). From T3.1 on,
    mail_send is offered and the DG-1 queue step is scored: exactly one mail_send, after
    files_read and mail_search, that queues a Low-risk draft to the trusted contact."""
    probes = sum(1 for r in rows if r["channel"] == "llm" and is_path_probe(r))
    llm = [r for r in rows if r["channel"] == "llm" and not is_path_probe(r)]
    blocked = sum(r["status"] == "blocked" for r in llm)
    errors = sum(r["status"] == "error" for r in llm)
    tokens = sum((r["prompt_tokens"] or 0) + (r["completion_tokens"] or 0) for r in llm)
    invalid: list[str] = []
    schema_errs: list[str] = []
    post_turn: list[str] = []
    mail_send = 0
    offered = False
    count = {"all": [0, 0], "turn": [0, 0], "draft": [0, 0]}  # [intact, total]
    draft_text = ""
    send_args_raw = ""

    def tally(text: str, *keys: str) -> None:
        for token in placeholder_like(text):
            ok = bool(CANONICAL.match(token)) and token in vault
            for key in keys:
                count[key][0] += ok
                count[key][1] += 1

    for r in llm:
        if r["status"] != "ok" or not r["response_redacted"]:
            continue
        resp = json.loads(r["response_redacted"])
        schemas = tool_schemas(r.get("request_redacted"))
        in_turn = turn_max_id is None or r.get("id", 0) <= turn_max_id
        offered = offered or (in_turn and MAIL_SEND in schemas)
        for choice in resp.get("choices") or []:
            msg = choice.get("message") or {}
            texts = [str(msg.get("content") or "")]
            for call in msg.get("tool_calls") or []:
                fn = call.get("function") or {}
                raw = fn.get("arguments") or ""
                texts.append(raw)
                name = str(fn.get("name"))
                if name == MAIL_SEND and name not in schemas:
                    mail_send += in_turn
                    continue
                if name == MAIL_SEND and in_turn:
                    send_args_raw = raw  # the draft as the model wrote it (placeholders)
                try:
                    args = json.loads(raw)
                except (TypeError, ValueError):
                    args = None
                if not isinstance(args, dict):
                    errs = [f"{name}: not a JSON object"]
                    (invalid if in_turn else post_turn).extend(errs)
                    continue
                errs = schema_errors(name, args, schemas)
                (schema_errs if in_turn else post_turn).extend(errs)
            for text in texts:
                tally(text, "all", *(["turn"] if in_turn else []))
            if in_turn and msg.get("content") and not msg.get("tool_calls"):
                draft_text = str(msg["content"])
    tally(send_args_raw if offered else draft_text, "draft")
    short = [t.removeprefix("mcp__steward__") for t in tools]
    flat = _flat(reply)
    unresolved = len(placeholder_like(flat))
    if offered:
        sends = [i for i, t in enumerate(short) if t == "mail_send"]
        order_ok = (
            len(sends) == 1
            and "files_read" in short[: sends[0]]
            and "mail_search" in short[: sends[0]]
        )
        mails = [a for a in queued or [] if a["tool"] == "mail_send"]
        draft_ok = False
        if len(mails) == 1:
            args = json.loads(mails[0]["args_json"])
            draft_ok = (
                args.get("to") == [TRUSTED_RAHUL]
                and mails[0]["risk"] == "low"
                and _draft_content_ok(_flat(f"{args.get('subject', '')}\n{args.get('body', '')}"))
                and unresolved == 0
            )
    else:
        order_ok = "files_read" in short and "mail_search" in short
        draft_ok = _draft_content_ok(flat)
    json_ok = not invalid
    schema_ok = json_ok and not schema_errs
    paused = any("rejected the last" in (r.get("request_redacted") or "") for r in llm)
    notes = []
    if probes:
        notes.append(f"{probes} /v1 path probe(s) 404'd (not scored)")
    if blocked:
        notes.append(f"{blocked} Shield blocks")
    if errors:
        notes.append(f"{errors} upstream errors")
    if schema_errs:
        notes.append(f"{len(schema_errs)} schema errors: {sorted(set(schema_errs))[:4]}")
    if paused:
        notes.append("Hermes paused the steward MCP server")
    if mail_send:
        notes.append(f"{mail_send} mail_send calls (tool not offered before T3.1)")
    if post_turn:
        notes.append(f"{len(post_turn)} post-reply schema errors (not scored)")
    base = status == 200 and not blocked and not errors and order_ok and draft_ok
    return Run(
        label=label,
        model=model,
        status=status,
        latency_s=round(latency, 2),
        reply=reply,
        tools=short,
        llm_rows=len(llm),
        blocked_rows=blocked,
        error_rows=errors,
        escalations=sum(1 for r in llm if r["escalated_from"]),
        tokens=tokens,
        invalid_args=invalid + schema_errs,
        placeholders_total=count["all"][1],
        placeholders_intact=count["all"][0],
        turn_placeholders_total=count["turn"][1],
        turn_placeholders_intact=count["turn"][0],
        draft_placeholders_total=count["draft"][1],
        draft_placeholders_intact=count["draft"][0],
        unresolved_in_reply=unresolved,
        order_ok=order_ok,
        json_ok=json_ok,
        schema_ok=schema_ok,
        draft_ok=draft_ok,
        mcp_paused=paused,
        mail_send_attempts=mail_send,
        post_turn_schema_errors=post_turn,
        success=base and schema_ok,
        success_json_only=base and json_ok,
        notes=notes,
    )


def summarize(runs: list[Run]) -> list[dict[str, Any]]:
    rows = []
    for label, model in MODELS.items():
        rs = [r for r in runs if r.model == model]
        if not rs:
            continue

        def ratio(kind: str, rs: list[Run] = rs) -> tuple[float | None, str]:
            prefix = "" if kind == "all" else f"{kind}_"
            intact = sum(getattr(r, f"{prefix}placeholders_intact") for r in rs)
            total = sum(getattr(r, f"{prefix}placeholders_total") for r in rs)
            return (intact / total if total else None), f"{intact}/{total}"

        rows.append(
            {
                "label": label,
                "model": model,
                "runs": len(rs),
                "success": sum(r.success for r in rs),
                "success_json_only": sum(r.success_json_only for r in rs),
                "schema_error_runs": sum(not r.schema_ok for r in rs),
                "mcp_paused_runs": sum(r.mcp_paused for r in rs),
                "mail_send_runs": sum(r.mail_send_attempts > 0 for r in rs),
                "integrity": ratio("draft")[0],
                "placeholders": ratio("draft")[1],
                "integrity_turn": ratio("turn")[0],
                "placeholders_turn": ratio("turn")[1],
                "integrity_all": ratio("all")[0],
                "placeholders_all": ratio("all")[1],
                "p50_latency_s": round(statistics.median(r.latency_s for r in rs), 1),
                "mean_tokens": round(statistics.mean(r.tokens for r in rs)),
                "blocked": sum(r.blocked_rows for r in rs),
                "escalations": sum(r.escalations for r in rs),
            }
        )
    return rows


def verdict(rows: list[dict[str, Any]]) -> dict[str, Any]:
    per_model = {
        r["model"]: (
            r["runs"] >= 10
            and r["success"] >= DG1_MIN_SUCCESS
            and r["integrity"] is not None
            and r["integrity"] >= DG1_MIN_INTEGRITY
            and r["p50_latency_s"] <= DG1_MAX_P50_S
        )
        for r in rows
    }
    return {"pass": any(per_model.values()), "per_model": per_model}


def table(rows: list[dict[str, Any]]) -> str:
    out = [
        "| Model | Path | Success (of 10) | Success, JSON-only args | "
        "Placeholder integrity: draft (DG-1) | turn outputs | all model output | "
        "p50 latency | Tokens | Shield blocks | Escalations | Runs with schema errors | "
        "Runs where Hermes paused steward MCP | Runs that called mail_send (pre-T3.1) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    def pct(value: float | None, frac: str) -> str:
        return f"{value * 100:.1f}% ({frac})" if value is not None else f"none emitted ({frac})"

    for r in rows:
        integrity = (
            f"{pct(r['integrity'], r['placeholders'])} | "
            f"{pct(r['integrity_turn'], r['placeholders_turn'])} | "
            f"{pct(r['integrity_all'], r['placeholders_all'])}"
        )
        out.append(
            f"| `{r['model']}` | full Shield | {r['success']}/{r['runs']} | "
            f"{r['success_json_only']}/{r['runs']} | {integrity} | {r['p50_latency_s']} s | "
            f"{r['mean_tokens']:,} per run | {r['blocked']} | {r['escalations']} | "
            f"{r['schema_error_runs']} | {r['mcp_paused_runs']} | {r['mail_send_runs']} |"
        )
    return "\n".join(out)


def queued_in(q: Any, audit_after: int, audit_to: int | None) -> list[dict[str, Any]]:
    """The actions rows a run created (via their action_created audit rows)."""
    return q(
        "SELECT tool, args_json, risk FROM actions WHERE id IN (SELECT ref_id FROM audit_events "
        "WHERE kind = 'action_created' AND id > ? AND id <= ?) ORDER BY id",
        (audit_after, 2**62 if audit_to is None else audit_to),
    )


def rescore(data: dict[str, Any], q: Any) -> list[Run]:
    """Score stored runs again from their ledger/audit windows (no new model calls). The vault
    is read now; it only ever grows, so a placeholder minted after a run counts as known."""
    vault = {v["placeholder"] for v in q("SELECT placeholder FROM vault")}
    runs = []
    for old in data["runs"]:
        w = old["window"]
        rows = q(
            "SELECT * FROM egress_events WHERE id > ? AND id <= ? ORDER BY id",
            (w["egress_after"], w["egress_to"]),
        )
        tools = [
            a["summary"]
            for a in q(
                "SELECT summary FROM audit_events WHERE id > ? AND id <= ? "
                "AND kind = 'tool_call' ORDER BY id",
                (w["audit_after"], w["audit_to"]),
            )
        ]
        run = score(
            old["label"],
            old["model"],
            old["status"],
            old["latency_s"],
            old["reply"],
            rows,
            tools,
            vault,
            turn_max_id=w["egress_reply"],
            queued=queued_in(q, w["audit_after"], w["audit_to"]),
        )
        run.window = w
        runs.append(run)
    return runs


def main(argv: list[str] | None = None) -> int:
    import httpx

    from steward import db

    parser = argparse.ArgumentParser(description="DG-1 through the full Shield")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--models", default=",".join(MODELS))
    # Hermes pauses an MCP server for ~55 s after 3 rejected calls, for every session. The gap
    # keeps one run's pause from leaking into the next run, so runs stay independent.
    parser.add_argument("--gap", type=float, default=60.0, help="seconds between runs")
    parser.add_argument("--rescore", type=Path, help="re-score a results file; no model calls")
    parser.add_argument(
        "--reasoning-effort",
        help="settings.reasoning_effort for this run (DG-1 ladder step 1); restored afterwards",
    )
    args = parser.parse_args(argv)

    def q(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        return db.with_conn(lambda conn: db.rows(conn.execute(sql, params)))

    def set_primary(model: str) -> None:
        db.with_conn(lambda conn: db.set_setting(conn, "model_primary", model))

    if args.rescore:
        data = json.loads(args.rescore.read_text())
        return report(rescore(data, q), f"{data['stamp']}-rescored", data.get("reasoning_effort"))

    original = db.with_conn(lambda conn: db.get_setting(conn, "model_primary"))
    original_effort = db.with_conn(lambda conn: db.get_setting(conn, "reasoning_effort"))
    effort = args.reasoning_effort if args.reasoning_effort is not None else original_effort
    if args.reasoning_effort is not None:
        db.with_conn(lambda conn: db.set_setting(conn, "reasoning_effort", args.reasoning_effort))
    print(f"reasoning_effort: {effort!r}", flush=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    runs: list[Run] = []
    base = "http://steward-api:8787"
    headers = {"Host": "127.0.0.1:8787", "X-Steward-Client": "web"}
    try:
        with httpx.Client() as client:
            for label in [m.strip() for m in args.models.split(",") if m.strip()]:
                model = MODELS[label]
                set_primary(model)
                for i in range(1, args.runs + 1):
                    if runs:
                        time.sleep(args.gap)
                    eg0 = q("SELECT COALESCE(MAX(id), 0) AS m FROM egress_events")[0]["m"]
                    au0 = q("SELECT COALESCE(MAX(id), 0) AS m FROM audit_events")[0]["m"]
                    started = time.monotonic()
                    status, reply = None, ""
                    try:
                        r = client.post(
                            f"{base}/api/chat",
                            json={"message": PROMPT},
                            headers=headers,
                            timeout=TURN_TIMEOUT_S,
                        )
                        status = r.status_code
                        body = r.json()
                        reply = str(body.get("reply") or body.get("detail") or "")
                    except Exception as exc:  # the run fails; the harness goes on
                        reply = f"<harness error: {type(exc).__name__}>"
                    latency = time.monotonic() - started
                    eg_reply = q("SELECT COALESCE(MAX(id), 0) AS m FROM egress_events")[0]["m"]
                    # The session-title auxiliary call lands after the reply: wait until quiet.
                    last, quiet_since = -1, time.monotonic()
                    while (
                        time.monotonic() - quiet_since < 20
                        and time.monotonic() - started < latency + 120
                    ):
                        n = q("SELECT COUNT(*) AS n FROM egress_events WHERE id > ?", (eg0,))[0][
                            "n"
                        ]
                        if n != last:
                            last, quiet_since = n, time.monotonic()
                        time.sleep(1)
                    rows = q("SELECT * FROM egress_events WHERE id > ? ORDER BY id", (eg0,))
                    tools = [
                        a["summary"]
                        for a in q(
                            "SELECT summary FROM audit_events WHERE id > ? AND kind = 'tool_call' "
                            "ORDER BY id",
                            (au0,),
                        )
                    ]
                    vault = {v["placeholder"] for v in q("SELECT placeholder FROM vault")}
                    run = score(
                        f"{label}-{i:02d}",
                        model,
                        status,
                        latency,
                        reply,
                        rows,
                        tools,
                        vault,
                        turn_max_id=eg_reply,
                        queued=queued_in(q, au0, None),
                    )
                    au1 = q("SELECT COALESCE(MAX(id), 0) AS m FROM audit_events")[0]["m"]
                    eg1 = max([eg0, *(r["id"] for r in rows)])
                    run.window = {
                        "egress_after": eg0,
                        "egress_reply": eg_reply,
                        "egress_to": eg1,
                        "audit_after": au0,
                        "audit_to": au1,
                    }
                    runs.append(run)
                    print(
                        f"{run.label}: success={run.success} order={run.order_ok} "
                        f"json={run.json_ok} schema={run.schema_ok} draft={run.draft_ok} "
                        f"ph={run.placeholders_intact}/{run.placeholders_total} "
                        f"unresolved={run.unresolved_in_reply} {run.latency_s}s "
                        f"tokens={run.tokens} tools={run.tools} {'; '.join(run.notes)}",
                        flush=True,
                    )
    finally:
        if original:
            set_primary(original)
        if args.reasoning_effort is not None and original_effort is not None:
            db.with_conn(lambda conn: db.set_setting(conn, "reasoning_effort", original_effort))
    return report(runs, stamp, effort)


def report(runs: list[Run], stamp: str, reasoning_effort: str | None = None) -> int:
    rows = summarize(runs)
    result = verdict(rows)
    out = Path("/data/t03") / f"results-shield-{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "stamp": stamp,
                "reasoning_effort": reasoning_effort,
                "rows": rows,
                "verdict": result,
                "runs": [asdict(r) for r in runs],
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    print("\n" + table(rows))
    print(
        f"\nDG-1 through the full Shield: {'PASS' if result['pass'] else 'FAIL'} "
        f"{result['per_model']}"
    )
    print(f"results: {out}")
    return 0 if runs else 1


if __name__ == "__main__":
    sys.exit(main())
