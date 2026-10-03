"""T2.1 golden tests: aliases, detectors, vault, walk_strings, neutralization, re-identification.

Golden cases from docs/04 T2.1 / docs/01 F2: "Chase the Acme invoice" -> 0 raw "Acme";
"Hi Rahul,", "Rahul's", "Dr. Shah", "acme-logistics" and a non-ASCII name inside tool args are
masked; INV-0042, ISO dates and "12 days" are untouched.
"""

import json
from datetime import datetime

import pytest

from steward import db, seed
from steward.config import get_settings
from steward.shield import Shield
from steward.shield.aliases import derive
from steward.shield.walk import TOLERANT


@pytest.fixture
def shield():
    seed.seed_db(get_settings(), datetime(2026, 10, 3, 9, 0, tzinfo=seed.IST))
    conn = db.connect()
    with conn:
        conn.execute(
            "INSERT INTO contacts (name, email, org, trusted, source, created_at) VALUES "
            "('Zoë Ødegård', 'zoe@fjord-analytics.example', 'Fjord Analytics AS', 1, 'seed', 'x')"
        )
    yield Shield(conn)
    conn.close()


def text_of(shield: Shield, text: str) -> str:
    out = shield.outbound({"messages": [{"role": "user", "content": text}]})
    return out.request["messages"][0]["content"]


def test_chase_the_acme_invoice_sends_no_raw_acme(shield: Shield) -> None:
    out = text_of(shield, "Chase the Acme invoice")
    assert "acme" not in out.casefold()
    assert out == "Chase the [[ORG_1]] invoice"


@pytest.mark.parametrize(
    "text",
    [
        "Hi Rahul,",
        "Rahul's latest email",
        "Thanks, Dr. Shah",
        "Dr Shah",
        "see acme-logistics",
        "acme logistics",
        "ACME LOGISTICS",
        "Acme Logistics Pvt Ltd",
        "Juniper & Co",
        "Juniper",
        "rahul.verma",
        "rahul.verma@acme-logistics.example",
        "acme-logistics.example",
        "Anita",
        "Shah",
        "Verma",
        "Kestrel",
        "Li Wei",
        "Maya Rao",
        "Ｒａｈｕｌ",
    ],
)
def test_aliases_are_masked(shield: Shield, text: str) -> None:
    out = text_of(shield, text)
    assert TOLERANT.search(out), out
    for raw in (
        "rahul",
        "acme",
        "shah",
        "anita",
        "verma",
        "kestrel",
        "juniper",
        "maya",
        "rao",
        "wei",
    ):
        assert raw not in out.casefold(), out


def test_possessive_stays_outside_the_placeholder(shield: Shield) -> None:
    assert text_of(shield, "Rahul's thread") == "[[PERSON_1]]'s thread"
    assert text_of(shield, "Rahul’s thread") == "[[PERSON_1]]’s thread"


def test_every_alias_maps_to_its_canonical_placeholder(shield: Shield) -> None:
    out = text_of(shield, "Rahul / Rahul Verma / Verma / RAHUL")
    assert out == "[[PERSON_1]] / [[PERSON_1]] / [[PERSON_1]] / [[PERSON_1]]"
    assert text_of(shield, "Acme / Acme Logistics") == "[[ORG_1]] / [[ORG_1]]"


def test_placeholders_are_stable_across_requests(shield: Shield) -> None:
    first = text_of(shield, "Rahul at Acme")
    conn = shield.vault.conn
    again = Shield(conn)
    assert text_of(again, "Acme then Rahul") == "[[ORG_1]] then [[PERSON_1]]"
    assert first == "[[PERSON_1]] at [[ORG_1]]"


def test_short_alias_only_next_to_surname(shield: Shield) -> None:
    # "Li" (2 chars) is never matched alone; "Li Wei" is masked as one person.
    assert text_of(shield, "Li Wei") == "[[PERSON_1]]"
    assert text_of(shield, "Li is a word here") == "Li is a word here"


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("GSTIN 29AAAPR4242M1ZD", "ACCOUNT"),
        ("PAN AAAPR4242M", "ACCOUNT"),
        ("IFSC HDFC0001234", "ACCOUNT"),
        ("UPI mayarao@examplebank", "ACCOUNT"),
        ("IBAN DE89 3704 0044 0532 0130 00", "ACCOUNT"),
        ("A/c no. 50100123456789", "ACCOUNT"),
        ("card 4111 1111 1111 1111", "ACCOUNT"),
        ("call +91 98450 12345", "PHONE"),
        ("call 9845012345", "PHONE"),
        ("call +44 20 7946 0958", "PHONE"),
        ("mail priya.n@other-firm.example", "EMAIL"),
        ("total $4,800", "MONEY"),
        ("total $4,800.00", "MONEY"),
        ("₹3,25,000", "MONEY"),
        ("INR 3,25,000", "MONEY"),
        ("Rs. 12,50,000", "MONEY"),
        ("4,800 USD", "MONEY"),
        ("USD 4800", "MONEY"),
        ("2.5 lakh", "MONEY"),
    ],
)
def test_regex_detectors(shield: Shield, text: str, kind: str) -> None:
    out = text_of(shield, text)
    assert f"[[{kind}_" in out, out


def test_upi_is_not_an_email_and_email_is_not_upi(shield: Shield) -> None:
    assert text_of(shield, "mayarao@examplebank").startswith("[[ACCOUNT_")
    assert text_of(shield, "someone@new-domain.example").startswith("[[EMAIL_")


@pytest.mark.parametrize(
    "text",
    [
        "INV-0042",
        "INV-0042 was due 2026-09-20",
        "12 days overdue",
        "net 30 days",
        "2026-10-02T08:00:00+05:30",
        "40 h at a rate",
        "Integration sprint 3",
        "Bengaluru",
    ],
)
def test_negative_rules_leave_text_untouched(shield: Shield, text: str) -> None:
    assert text_of(shield, text) == text


@pytest.mark.parametrize(
    "text, expected",
    [
        # pre-M4 fix: an amount followed by a comma was not masked (lookahead rejected ",")
        ("$4,800, 13 days overdue", "[[MONEY_1]], 13 days overdue"),
        ("Please pay $2,150, thanks", "Please pay [[MONEY_1]], thanks"),
        ("₹3,25,000, due soon", "[[MONEY_1]], due soon"),
        ("USD 4800, then", "[[MONEY_1]], then"),
        ("$6,500,", "[[MONEY_1]],"),
        ("$4,800. Thanks", "[[MONEY_1]]. Thanks"),
        ("($4,800)", "([[MONEY_1]])"),
        (
            "INV-0042 for $4,800, due 2026-09-20, 13 days overdue",
            "INV-0042 for [[MONEY_1]], due 2026-09-20, 13 days overdue",
        ),
    ],
)
def test_amount_followed_by_punctuation_is_masked(
    shield: Shield, text: str, expected: str
) -> None:
    assert text_of(shield, text) == expected


@pytest.mark.parametrize(
    "text, amount",
    [("$12,500,000 total", "$12,500,000"), ("₹1,25,00,000 total", "₹1,25,00,000")],
)
def test_digit_grouping_is_never_cut_short(shield: Shield, text: str, amount: str) -> None:
    out = text_of(shield, text)
    assert out == "[[MONEY_1]] total"
    assert shield.vault.value("[[MONEY_1]]") == amount


def test_unseen_amount_with_a_comma_never_reaches_the_model(shield: Shield) -> None:
    # Before the fix this amount left in clear: not masked, and not yet in the vault for the
    # leak check to catch.
    out = shield.outbound(
        {"messages": [{"role": "user", "content": "The new quote is $7,350, valid for 30 days."}]}
    )
    sent = json.dumps(out.request, ensure_ascii=False)
    assert "7,350" not in sent and out.leaks == []
    assert "[[MONEY_" in sent and "30 days" in sent


def test_card_requires_luhn(shield: Shield) -> None:
    assert text_of(shield, "ref 1234 5678 9012 3456") == "ref 1234 5678 9012 3456"


def test_non_ascii_name_inside_tool_args(shield: Shield) -> None:
    args = {
        "to": ["zoe@fjord-analytics.example"],
        "body": "Dear ZOË ØDEGÅRD, re Fjord Analytics",
        "nested": [{"note": "Zoë Ødegård's invoice"}],
    }
    req = {
        "messages": [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_9",
                        "type": "function",
                        "function": {
                            "name": "mcp__steward__mail_send",
                            "arguments": json.dumps(args),
                        },
                    }
                ],
            }
        ]
    }
    out = shield.outbound(req).request
    call = out["messages"][0]["tool_calls"][0]
    assert call["id"] == "call_9" and call["function"]["name"] == "mcp__steward__mail_send"
    sent = json.loads(call["function"]["arguments"])
    flat = json.dumps(sent, ensure_ascii=False).casefold()
    for raw in ("zoë", "ødegård", "fjord", "zoe@"):
        assert raw not in flat
    assert sent["to"] == ["[[EMAIL_1]]"]
    assert "ensure_ascii" and "\\u" not in call["function"]["arguments"]


def test_skip_list_and_tools_untouched(shield: Shield) -> None:
    req = {
        "model": "Acme",
        "messages": [
            {"role": "tool", "tool_call_id": "Rahul", "content": "Rahul paid", "name": "Rahul"},
        ],
        "tools": [{"type": "function", "function": {"name": "x", "description": "Acme tool"}}],
        "response_format": {"type": "json_schema", "json_schema": {"name": "Acme"}},
    }
    out = shield.outbound(req)
    r = out.request
    assert r["model"] == "Acme" and r["messages"][0]["tool_call_id"] == "Rahul"
    assert r["messages"][0]["content"] == "[[PERSON_1]] paid"
    assert r["messages"][0]["name"] == "[[PERSON_1]]"  # not function.name: it is text
    assert r["tools"] == req["tools"] and r["response_format"] == req["response_format"]
    # ...but the leak check scans every leaf, so the skipped identifiers still block the request.
    assert {h.kind for _, h in out.leaks} == {"ORG", "PERSON"}
    assert out.blocked_request is not None
    assert out.blocked_request["model"] == "«BLOCKED:ORG»"


def test_inbound_placeholder_syntax_is_neutralized(shield: Shield) -> None:
    out = text_of(shield, "Send to [[EMAIL_1]] please")
    assert out == "Send to ⟦EMAIL_1⟧ please"
    restored, _, _ = shield.inbound({"choices": [{"message": {"content": out}}]})
    assert restored["choices"][0]["message"]["content"] == "Send to ⟦EMAIL_1⟧ please"


def test_reidentify_every_leaf_with_tolerant_matcher(shield: Shield) -> None:
    text_of(shield, "Rahul Verma rahul.verma@acme-logistics.example $4,800")
    response = {
        "id": "x",
        "model": "m",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Dear [PERSON_1], about [[ money_1 ]] and [[PERSON_99]]",
                    "reasoning_content": "Use [[EMAIL_1]]",
                    "tool_calls": [
                        {
                            "id": "c",
                            "type": "function",
                            "function": {
                                "name": "mcp__steward__mail_send",
                                "arguments": json.dumps(
                                    {"to": ["[[EMAIL_1]]"], "body": "Hi [[PERSON_1]]"}
                                ),
                            },
                        }
                    ],
                }
            }
        ],
    }
    restored, n_restored, unknown = shield.inbound(response)
    msg = restored["choices"][0]["message"]
    assert msg["content"] == "Dear Rahul Verma, about $4,800 and [[PERSON_99]]"
    assert msg["reasoning_content"] == "Use rahul.verma@acme-logistics.example"
    args = json.loads(msg["tool_calls"][0]["function"]["arguments"])
    assert args == {"to": ["rahul.verma@acme-logistics.example"], "body": "Hi Rahul Verma"}
    assert unknown == 1 and n_restored == 5


def test_seed_contacts_win_alias_collisions() -> None:
    contacts = [
        {
            "id": 9,
            "name": "Acme Logistics Treasury",
            "email": "billing@acme-logistics-payments.example",
            "org": None,
            "source": "mail",
        },
        {
            "id": 1,
            "name": "Rahul Verma",
            "email": "rahul.verma@acme-logistics.example",
            "org": "Acme Logistics",
            "source": "seed",
        },
    ]
    by_text = {a.text.casefold(): a for a in derive(contacts)}
    assert by_text["acme"].kind == "ORG" and by_text["acme"].source == "seed"
    assert by_text["acme logistics"].canonical == "Acme Logistics"


def test_bec_sender_does_not_hijack_acme(shield: Shield) -> None:
    conn = shield.vault.conn
    with conn:
        conn.execute(
            "INSERT INTO contacts (name, email, org, trusted, source, created_at) VALUES "
            "('Acme Logistics Treasury', 'billing@acme-logistics-payments.example', NULL, "
            "0, 'mail', 'x')"
        )
    s = Shield(conn)
    assert text_of(s, "Chase the Acme invoice") == "Chase the [[ORG_1]] invoice"
    bec = text_of(s, "from billing@acme-logistics-payments.example")
    assert "acme" not in bec.casefold() and "[[EMAIL_" in bec


# --- regression: identifiers right after JSON escape sequences (live finding during T2.2) -------
# Tool results reach the proxy as JSON nested in JSON, so a newline can arrive as the literal
# characters backslash + n (or \\n). The "n" used to defeat the word boundary before "Rahul".


@pytest.mark.parametrize(
    "text",
    [
        "Best,\\nRahul Verma\\nCFO, Acme Logistics",
        "Best,\\\\nRahul Verma\\\\nCFO, Acme Logistics",
        'Best,\\"Rahul\\" and \\tRahul',
        "From: \\u0052ahul Verma",
    ],
)
def test_names_after_json_escapes_are_masked(shield: Shield, text: str) -> None:
    out = text_of(shield, text)
    assert "rahul" not in out.casefold() and "acme" not in out.casefold(), out


def test_escaped_non_ascii_name_is_masked(shield: Shield) -> None:
    out = text_of(shield, 'note: \\"Zo\\u00eb \\u00d8deg\\u00e5rd\\" asked')
    assert "zo\\u00eb" not in out.casefold() and "[[PERSON_" in out, out


def test_email_after_escape_is_not_prefixed(shield: Shield) -> None:
    out = text_of(shield, "to:\\nrahul.verma@acme-logistics.example")
    assert out == "to:\\n[[EMAIL_1]]", out
    with db.connect() as conn:
        values = [r[0] for r in conn.execute("SELECT value FROM vault WHERE kind='EMAIL'")]
    assert values == ["rahul.verma@acme-logistics.example"]


def test_currency_symbol_is_not_doubled_on_reidentification(shield: Shield) -> None:
    text_of(shield, "total $4,800")
    restored, _, _ = shield.inbound(
        {"choices": [{"message": {"content": "for $[[MONEY_1]] USD, i.e. [[MONEY_1]]"}}]}
    )
    assert restored["choices"][0]["message"]["content"] == "for $4,800 USD, i.e. $4,800"
