"""The DG-1 scorer itself (no network): order, JSON validity, recipient, placeholder integrity."""

import json

from tests.harness_t03 import dg1_verdict, score_run, summarize


def _proxy(*calls: tuple[str, object]) -> list[dict]:
    tool_calls = [
        {
            "function": {
                "name": name,
                "arguments": args if isinstance(args, str) else json.dumps(args),
            }
        }
        for name, args in calls
    ]
    return [
        {
            "status": 200,
            "response": {
                "usage": {"prompt_tokens": 100, "completion_tokens": 10},
                "choices": [{"message": {"tool_calls": tool_calls}}],
            },
        }
    ]


GOOD_SEND = {
    "to": ["[[EMAIL_1]]"],
    "subject": "INV-0042",
    "body": "Dear [[PERSON_1]], [[MONEY_1]] is due.",
}


def test_correct_pseudonymized_run_scores_success_and_full_integrity() -> None:
    tools = [
        {"tool": "files_read", "args": {"path": "invoices/INV-0042.md"}},
        {"tool": "mail_search", "args": {"query": "[[ORG_1]]"}},
        {"tool": "mail_send", "args": GOOD_SEND},
    ]
    r = score_run(
        "r",
        "m",
        "pseudonymized",
        200,
        12.0,
        "Queued for [[PERSON_1]].",
        _proxy(
            ("mcp__steward__files_read", {"path": "invoices/INV-0042.md"}),
            ("mcp__steward__mail_search", {"query": "[[ORG_1]]"}),
            ("mcp__steward__mail_send", GOOD_SEND),
        ),
        tools,
    )
    assert r.success and r.order_ok and r.json_ok and r.recipient_ok
    assert (r.placeholders_intact, r.placeholders_total) == (4, 4)
    assert r.tokens == 110


def test_broken_placeholder_and_wrong_order_are_caught() -> None:
    send = {
        "to": ["[[EMAIL_1]]"],
        "subject": "x",
        "body": "Dear [PERSON_1], [[money_1]] and [[PERSON_9]]",
    }
    tools = [{"tool": "mail_send", "args": send}, {"tool": "files_read", "args": {"path": "p"}}]
    r = score_run("r", "m", "pseudonymized", 200, 1.0, "", _proxy(), tools)
    assert not r.order_ok and not r.success
    assert r.placeholders_total == 4 and r.placeholders_intact == 1
    assert set(r.bad_placeholders) == {"[PERSON_1]", "[[money_1]]", "[[PERSON_9]]"}


def test_invalid_json_args_fail_the_run() -> None:
    tools = [
        {"tool": "files_read", "args": {}},
        {"tool": "mail_search", "args": {}},
        {"tool": "mail_send", "args": GOOD_SEND},
    ]
    r = score_run(
        "r",
        "m",
        "plain",
        200,
        1.0,
        "",
        _proxy(
            ("mcp__steward__mail_send", "{not json"), ("mcp__steward__mail_search", {"limit": 3})
        ),
        tools,
    )
    assert not r.json_ok and not r.success
    assert len(r.invalid_json_args) == 2


def test_gate_needs_ten_runs_eight_successes_integrity_and_latency() -> None:
    tools = [
        {"tool": "files_read", "args": {}},
        {"tool": "mail_search", "args": {}},
        {"tool": "mail_send", "args": GOOD_SEND},
    ]
    runs = [
        score_run(
            f"r{i}",
            "nvidia/Nemotron-3_5-Lightning",
            "pseudonymized",
            200,
            20.0,
            "",
            _proxy(("mcp__steward__mail_send", GOOD_SEND)),
            tools,
        )
        for i in range(10)
    ]
    assert dg1_verdict(summarize(runs))["pass"] is True
    slow = [
        score_run(
            f"s{i}",
            "nvidia/Nemotron-3_5-Lightning",
            "pseudonymized",
            200,
            50.0,
            "",
            _proxy(("mcp__steward__mail_send", GOOD_SEND)),
            tools,
        )
        for i in range(10)
    ]
    assert dg1_verdict(summarize(slow))["pass"] is False
