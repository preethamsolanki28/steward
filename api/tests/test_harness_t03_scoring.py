"""The DG-1-through-Shield scorer itself (no network)."""

import json

from tests.harness_t03 import score, summarize, verdict

VAULT = {"[[PERSON_1]]", "[[EMAIL_1]]", "[[MONEY_1]]"}
GOOD_REPLY = "Hi Rahul Verma,\n\nINV-0042 for $4,800 is overdue.\n\nBest, Maya"


OFFERED = [
    {
        "type": "function",
        "function": {
            "name": "mcp__steward__mail_search",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mcp__steward__mail_read",
            "parameters": {
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"],
            },
        },
    },
]


def row(
    content: str | None = None,
    args: str | None = None,
    status: str = "ok",
    escalated: str | None = None,
    tool: str = "mcp__steward__mail_search",
    request_text: str = "",
) -> dict:
    message: dict = {"content": content}
    if args is not None:
        message["tool_calls"] = [{"function": {"name": tool, "arguments": args}}]
    request = {"messages": [{"role": "tool", "content": request_text}], "tools": OFFERED}
    return {
        "channel": "llm",
        "status": status,
        "escalated_from": escalated,
        "prompt_tokens": 100,
        "completion_tokens": 10,
        "request_redacted": json.dumps(request),
        "response_redacted": json.dumps({"choices": [{"message": message}]}),
    }


TOOLS = ["mcp__steward__files_list", "mcp__steward__files_read", "mcp__steward__mail_search"]


def test_good_run() -> None:
    r = score(
        "x",
        "m",
        200,
        9.0,
        GOOD_REPLY,
        [row(args='{"query": "[[EMAIL_1]]"}'), row("Draft to [[PERSON_1]] for [[MONEY_1]]")],
        TOOLS,
        VAULT,
    )
    assert r.success and (r.placeholders_intact, r.placeholders_total) == (3, 3)
    assert r.tokens == 220


def test_broken_placeholder_unknown_and_unresolved_reply_fail() -> None:
    r = score(
        "x",
        "m",
        200,
        9.0,
        "Hi Rahul, INV-0042 $4,800 [[PERSON_9]]",
        [row("Dear [PERSON_1] [[money_1]] [[PERSON_9]]")],
        TOOLS,
        VAULT,
    )
    assert (r.placeholders_intact, r.placeholders_total) == (0, 3)
    assert r.unresolved_in_reply == 1 and not r.draft_ok and not r.success


def test_block_invalid_json_or_missing_tool_fail() -> None:
    assert not score("x", "m", 200, 1.0, GOOD_REPLY, [row(status="blocked")], TOOLS, VAULT).success
    assert not score("x", "m", 200, 1.0, GOOD_REPLY, [row(args="{bad")], TOOLS, VAULT).success
    assert not score("x", "m", 200, 1.0, GOOD_REPLY, [row("x")], TOOLS[:2], VAULT).success


def test_schema_errors_fail_strict_but_not_json_only() -> None:
    # The M2 failure mode: no mail_send yet, so the model "sends" through mail_read.
    send_via_read = '{"to": ["[[EMAIL_1]]"], "body": "x", "in_reply_to": "11"}'
    r = score(
        "x",
        "m",
        200,
        1.0,
        GOOD_REPLY,
        [row(args=send_via_read, tool="mcp__steward__mail_read")],
        TOOLS,
        VAULT,
    )
    assert r.json_ok and not r.schema_ok
    assert r.success_json_only and not r.success
    assert "mcp__steward__mail_read: missing 'id'" in r.invalid_args
    assert "mcp__steward__mail_read: unknown 'to'" in r.invalid_args


def test_schema_type_mismatch_and_unoffered_tool() -> None:
    wrong_type = row(args='{"query": "x", "limit": "5"}')
    unoffered = row(args='{"query": "x"}', tool="mail_search")
    r = score("x", "m", 200, 1.0, GOOD_REPLY, [wrong_type, unoffered], TOOLS, VAULT)
    assert r.invalid_args == [
        "mcp__steward__mail_search: 'limit' is not integer",
        "mail_search: not an offered tool",
    ]
    assert not r.success


def test_hermes_mcp_pause_is_flagged() -> None:
    paused = row("x", request_text='{"error": "MCP server \'steward\' rejected the last 3 calls"}')
    r = score("x", "m", 200, 1.0, GOOD_REPLY, [paused], TOOLS, VAULT)
    assert r.mcp_paused and "Hermes paused the steward MCP server" in r.notes


def test_v1_path_probe_is_reported_not_scored_but_a_real_block_still_fails() -> None:
    probe = {
        "channel": "llm",
        "status": "blocked",
        "escalated_from": None,
        "prompt_tokens": None,
        "completion_tokens": None,
        "request_redacted": json.dumps({"method": "GET", "path": "/v1/props"}),
        "response_redacted": None,
    }
    good = [row("Draft to [[PERSON_1]]")]
    r = score("x", "m", 200, 1.0, GOOD_REPLY, [probe, *good], TOOLS, VAULT)
    assert r.success and r.blocked_rows == 0 and r.llm_rows == 1
    assert r.notes == ["1 /v1 path probe(s) 404'd (not scored)"]
    real = {
        **probe,
        "request_redacted": json.dumps({"messages": [{"content": "«BLOCKED:PERSON»"}]}),
    }
    assert not score("x", "m", 200, 1.0, GOOD_REPLY, [real, *good], TOOLS, VAULT).success


def test_gate() -> None:
    runs = [
        score(
            f"r{i}",
            "nvidia/Nemotron-3_5-Lightning",
            200,
            20.0,
            GOOD_REPLY,
            [row("[[PERSON_1]]")],
            TOOLS,
            VAULT,
        )
        for i in range(10)
    ]
    assert verdict(summarize(runs))["pass"] is True
    slow = [
        score(
            f"s{i}",
            "nvidia/Nemotron-3_5-Lightning",
            200,
            50.0,
            GOOD_REPLY,
            [row("[[PERSON_1]]")],
            TOOLS,
            VAULT,
        )
        for i in range(10)
    ]
    assert verdict(summarize(slow))["pass"] is False


def test_mail_send_before_t3_1_is_counted_not_scored() -> None:
    call = row(args='{"to": "[\\"[[EMAIL_1]]\\"]", "body": "x"}', tool="mcp__steward__mail_send")
    r = score("x", "m", 200, 1.0, GOOD_REPLY, [call], TOOLS, VAULT)
    assert r.mail_send_attempts == 1 and r.schema_ok and r.success
    assert "1 mail_send calls (tool not offered before T3.1)" in r.notes


def test_post_reply_calls_are_reported_not_scored() -> None:
    turn = {**row(args='{"query": "x"}'), "id": 5}
    curator = {**row(args='{"operations": "x"}', tool="skill_manage"), "id": 6}
    r = score("x", "m", 200, 1.0, GOOD_REPLY, [turn, curator], TOOLS, VAULT, turn_max_id=5)
    assert r.success and r.post_turn_schema_errors == ["skill_manage: not an offered tool"]
    late_bad = {**row(args="{bad"), "id": 4}
    assert not score("x", "m", 200, 1.0, GOOD_REPLY, [late_bad], TOOLS, VAULT, 5).success


def test_bare_placeholders_count_as_broken_and_unresolved() -> None:
    model_out = row("Invoice (ORG_1) for [[PERSON_1]], cc PERSON 3; ⟦PERSON_9⟧ is user text")
    r = score("x", "m", 200, 1.0, GOOD_REPLY + " (ORG 1)", [model_out], TOOLS, VAULT)
    assert (r.placeholders_intact, r.placeholders_total) == (1, 3)
    assert r.unresolved_in_reply == 1 and not r.draft_ok and not r.success


def test_draft_turn_and_all_integrity_are_separate() -> None:
    search = {**row(args='{"query": "ORG_1 invoice"}'), "id": 1}
    draft = {**row("Hi [[PERSON_1]], [[MONEY_1]] is due"), "id": 2}
    title = {**row('{"title": "Chase ORG_1 invoice"}'), "id": 3}
    r = score("x", "m", 200, 1.0, GOOD_REPLY, [search, draft, title], TOOLS, VAULT, 2)
    assert (r.draft_placeholders_intact, r.draft_placeholders_total) == (2, 2)
    assert (r.turn_placeholders_intact, r.turn_placeholders_total) == (2, 3)
    assert (r.placeholders_intact, r.placeholders_total) == (2, 4)


SEND_SCHEMA = {
    "type": "function",
    "function": {
        "name": "mcp__steward__mail_send",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"anyOf": []},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
    },
}
TOOLS_T31 = [*TOOLS, "mcp__steward__mail_send"]
DRAFT = {
    "to": ["rahul.verma@acme-logistics.example"],
    "subject": "INV-0042",
    "body": "Hi Rahul,\n\nINV-0042 for $4,800 is overdue.\n\nBest, Maya",
}


def send_row(
    args: str = '{"to": ["[[EMAIL_1]]"], "subject": "s", "body": "Hi [[PERSON_1]]"}',
) -> dict:
    r = row(args=args, tool="mcp__steward__mail_send")
    request = json.loads(r["request_redacted"])
    request["tools"] = [*OFFERED, SEND_SCHEMA]
    return {**r, "request_redacted": json.dumps(request)}


def queued(args: dict = DRAFT, level: str = "low") -> list[dict]:
    return [{"tool": "mail_send", "args_json": json.dumps(args), "risk": level}]


def test_t31_queue_step_scored_once_mail_send_is_offered() -> None:
    reply = "Queued for your approval as action #1."
    good = score("x", "m", 200, 1.0, reply, [send_row()], TOOLS_T31, VAULT, queued=queued())
    assert good.success and good.order_ok and good.draft_ok and good.mail_send_attempts == 0
    assert (good.draft_placeholders_intact, good.draft_placeholders_total) == (2, 2)
    twice = [*TOOLS_T31, "mcp__steward__mail_send"]
    assert not score("x", "m", 200, 1.0, reply, [send_row()], twice, VAULT, queued=queued()).success
    early = ["mcp__steward__files_read", "mcp__steward__mail_send", "mcp__steward__mail_search"]
    assert not score("x", "m", 200, 1.0, reply, [send_row()], early, VAULT, queued=queued()).success
    high = queued(level="high")
    assert not score("x", "m", 200, 1.0, reply, [send_row()], TOOLS_T31, VAULT, queued=high).success
    leaked = queued({**DRAFT, "body": "Hi Rahul, INV-0042 $4,800, see PERSON_3"})
    assert not score(
        "x", "m", 200, 1.0, reply, [send_row()], TOOLS_T31, VAULT, queued=leaked
    ).success
    assert not score("x", "m", 200, 1.0, reply, [send_row()], TOOLS_T31, VAULT, queued=[]).success
