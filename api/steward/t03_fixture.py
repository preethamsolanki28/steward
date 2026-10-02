"""T0.3 self-contained Acme fixture: INV-0042, 2 emails, 2 contacts (docs/04 T0.3).

Two variants of the same data:
- PLAIN: real (synthetic) values, as Hermes would see them without a Shield.
- PSEUDONYMIZED: the same text hand-pseudonymized into [[KIND_n]] placeholders, as Nemotron
  sees it once the Shield runs (M2). In T0.3 there is no re-identification, so Hermes and the
  stub tools work on the placeholders directly.

All values are synthetic and use .example domains.
"""

from typing import Any, Literal

FixtureName = Literal["plain", "pseudonymized"]

# Canonical value -> placeholder, numbered the way the vault would mint them (docs/02 §7a step 6).
PLACEHOLDERS: dict[str, str] = {
    "Rahul Verma": "[[PERSON_1]]",
    "Rahul": "[[PERSON_1]]",
    "Maya Rao": "[[PERSON_2]]",
    "Maya": "[[PERSON_2]]",
    "Acme Logistics": "[[ORG_1]]",
    "Acme": "[[ORG_1]]",
    "rahul.verma@acme-logistics.example": "[[EMAIL_1]]",
    "maya@rao-consulting.example": "[[EMAIL_2]]",
    "29AAAPR4242M1ZD": "[[ACCOUNT_1]]",
    "mayarao@examplebank": "[[ACCOUNT_2]]",
    "$4,800": "[[MONEY_1]]",
}

PLACEHOLDER_VOCAB: frozenset[str] = frozenset(PLACEHOLDERS.values())

_INVOICE = """---
invoice: INV-0042
client: Acme Logistics
bill_to: Rahul Verma
bill_to_email: rahul.verma@acme-logistics.example
amount: "$4,800"
currency: USD
issued: "2026-08-21"
due: "2026-09-20"
status: unpaid
---

# Invoice INV-0042

From: Maya Rao, Rao Consulting, Bengaluru · maya@rao-consulting.example
GSTIN: 29AAAPR4242M1ZD
UPI: mayarao@examplebank

Bill to: Acme Logistics, attn. Rahul Verma (CFO) · rahul.verma@acme-logistics.example

| Item | Qty | Rate | Amount |
|---|---|---|---|
| Integration sprint 3: shipment-tracking API | 40 h | $120/h | $4,800 |

Total due: $4,800 (USD) · Terms: net 30 · Status: unpaid (12 days overdue)
"""

_EMAILS: list[dict[str, Any]] = [
    {
        "id": "m-2",
        "from": "Rahul Verma <rahul.verma@acme-logistics.example>",
        "to": "maya@rao-consulting.example",
        "subject": "Re: INV-0042 for integration sprint 3",
        "date": "2026-09-22T10:14:00+05:30",
        "body": "Hi Maya,\n\nQuick update: our AP team says INV-0042 is in this week's "
        "payment run.\n\n"
        "Best,\nRahul Verma\nCFO, Acme Logistics",
    },
    {
        "id": "m-1",
        "from": "Rahul Verma <rahul.verma@acme-logistics.example>",
        "to": "maya@rao-consulting.example",
        "subject": "Re: INV-0042 for integration sprint 3",
        "date": "2026-08-22T09:02:00+05:30",
        "body": "Hi Maya,\n\nThanks, INV-0042 received. I've passed it to our AP team for "
        "processing.\n\n"
        "Best,\nRahul Verma\nCFO, Acme Logistics",
    },
]

PROMPT_PLAIN = (
    "Chase the overdue Acme invoice. It is INV-0042; invoices are at invoices/INV-00NN.md. "
    "Read the invoice, find the latest email thread with the client contact, then draft a short, "
    "formal payment reminder to that contact and queue it with mail_send. "
    "Reply with the draft when it is queued."
)


def _pseudonymize(text: str) -> str:
    # Longest canonical value first, so "Rahul Verma" wins over "Rahul".
    for value in sorted(PLACEHOLDERS, key=len, reverse=True):
        text = text.replace(value, PLACEHOLDERS[value])
    return text


def invoice(fixture: FixtureName) -> str:
    return _INVOICE if fixture == "plain" else _pseudonymize(_INVOICE)


def emails(fixture: FixtureName) -> list[dict[str, Any]]:
    if fixture == "plain":
        return [dict(e) for e in _EMAILS]
    return [
        {k: _pseudonymize(v) if isinstance(v, str) else v for k, v in e.items()} for e in _EMAILS
    ]


def prompt(fixture: FixtureName) -> str:
    return PROMPT_PLAIN if fixture == "plain" else _pseudonymize(PROMPT_PLAIN)


def expected_recipient(fixture: FixtureName) -> str:
    email = "rahul.verma@acme-logistics.example"
    return email if fixture == "plain" else PLACEHOLDERS[email]
