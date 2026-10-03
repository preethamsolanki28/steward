"""T3.2: Approval Gate risk rules R0, R1 (+ lookalike), R3, overwrite (pure functions).

Seed contacts: trusted rahul.verma@acme-logistics.example, anita.shah@brightleaf-clinics.example,
li.wei@kestrel-robotics.example, tom.becker@juniper-co.example, sara.khan@orbitra-foods.example;
the owner maya@rao-consulting.example is in contacts with trusted 0. All domains are .example /
.test / .invalid, except gmail.com in the free-mail tests (synthetic local parts only).
"""

import json
from pathlib import Path

import pytest

from steward.gate import risk

SEED = json.loads((Path(__file__).parents[2] / "seed" / "contacts.json").read_text())
OWNER = "maya@rao-consulting.example"
CTX = risk.context([(c["email"], c["org"]) for c in SEED if c["trusted"]], OWNER)

RAHUL = "rahul.verma@acme-logistics.example"
LEGIT = {
    "to": [RAHUL],
    "subject": "INV-0042: payment reminder",
    "body": "Dear Rahul,\n\nThis is a reminder that INV-0042 for $4,800 (integration sprint 3) "
    "was due 12 days ago, on 2026-09-20. Could you confirm when the payment will be made?\n\n"
    "Best, Maya",
}
BEC_TO = "billing@acme-logistics-payments.example"
BEC = {
    "to": [BEC_TO],
    "subject": "Open invoices",
    "body": "Hello,\n\nAs requested, please find the open invoices: INV-0042, INV-0043, INV-0045,"
    " INV-0046.\n\nBest, Maya",
}


def mail(to: object, body: str = "Hello", subject: str = "Hi") -> dict:
    return {"to": to, "subject": subject, "body": body}


def reasons_for(to: str) -> list[str]:
    return risk.assess("mail_send", mail([to]), CTX)[1]


def test_seed_context() -> None:
    assert CTX.trusted_emails == {
        RAHUL,
        "anita.shah@brightleaf-clinics.example",
        "li.wei@kestrel-robotics.example",
        "tom.becker@juniper-co.example",
        "sara.khan@orbitra-foods.example",
    }
    assert OWNER not in CTX.trusted_emails


# --- acceptance: legit Acme Low, BEC High ---------------------------------------------------


def test_legit_acme_draft_is_low() -> None:
    assert risk.assess("mail_send", LEGIT, CTX) == ("low", [])


def test_bec_lookalike_is_high_with_exact_reasons() -> None:
    assert risk.assess("mail_send", BEC, CTX) == (
        "high",
        [f"{BEC_TO} is not a trusted contact", "lookalike of acme-logistics.example"],
    )


# --- R0 ---------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "token",
    ["[[PERSON_1]]", "[MONEY_2]", "[[ person_1 ]]", "[[ORG_1]", "PERSON_3", "ORG 1", "⟦ORG_1⟧"],
)
@pytest.mark.parametrize("field", ["body", "subject", "to", "in_reply_to"])
def test_r0_unresolved_placeholder_anywhere_in_mail(token: str, field: str) -> None:
    args = dict(LEGIT)
    args[field] = [token] if field == "to" else f"x {token} y"
    level, reasons = risk.assess("mail_send", args, CTX)
    assert level == "high" and reasons[0] == risk.UNRESOLVED_PLACEHOLDER
    assert reasons.count(risk.UNRESOLVED_PLACEHOLDER) == 1
    assert not risk.approvable(reasons)


@pytest.mark.parametrize("field", ["path", "content"])
def test_r0_in_files_write(field: str) -> None:
    args = {"path": "notes/a.md", "content": "hello"}
    args[field] = args[field] + " [[EMAIL_2]]"
    assert risk.assess("files_write", args, CTX) == ("high", [risk.UNRESOLVED_PLACEHOLDER])


@pytest.mark.parametrize(
    "text", ["INV-0042", "PERSONAL_1", "ORG-1", "Dear Rahul", "MY_PERSON_1", "person 1", "ORG"]
)
def test_r0_does_not_fire_on_ordinary_text(text: str) -> None:
    assert risk.r0_unresolved_placeholder({"body": text}) == []


def test_r0_scans_every_placeholder_once_even_when_several() -> None:
    args = mail(["[[EMAIL_1]]"], body="Dear [[PERSON_1]], pay [[MONEY_1]]")
    reasons = risk.assess("mail_send", args, CTX)[1]
    assert reasons == [risk.UNRESOLVED_PLACEHOLDER, "[[EMAIL_1]] is not a trusted contact"]


# --- R1: untrusted + lookalike --------------------------------------------------------------


def test_untrusted_mailbox_at_a_trusted_domain_is_not_a_lookalike() -> None:
    assert reasons_for("ap@acme-logistics.example") == [
        "ap@acme-logistics.example is not a trusted contact"
    ]
    assert reasons_for("x@billing.acme-logistics.example") == [
        "x@billing.acme-logistics.example is not a trusted contact"
    ]


@pytest.mark.parametrize(
    "domain, trusted",
    [
        ("аcme-logistics.example", "acme-logistics.example"),  # Cyrillic а
        ("acme-lоgistics.example", "acme-logistics.example"),  # Cyrillic о
        ("acme-logisticѕ.example", "acme-logistics.example"),  # Cyrillic ѕ
        ("acme-logistiсs.example", "acme-logistics.example"),  # Cyrillic с
        ("kestrel-rοbotics.example", "kestrel-robotics.example"),  # Greek ο
        ("orbitra-fοοds.example", "orbitra-foods.example"),  # Greek ο ×2
        ("acrne-logistics.example", "acme-logistics.example"),  # rn -> m
        ("kestrel-r0botics.example", "kestrel-robotics.example"),  # 0 -> o
        ("acme-1ogistics.example", "acme-logistics.example"),  # 1 -> l
        ("ＡＣＭＥ-logistics.example", "acme-logistics.example"),  # fullwidth, NFKC
    ],
)
def test_confusables_are_lookalikes(domain: str, trusted: str) -> None:
    addr = f"billing@{domain}"
    assert reasons_for(addr) == [
        f"{addr.lower()} is not a trusted contact",
        f"lookalike of {trusted}",
    ]


def test_punycode_confusable_is_decoded() -> None:
    puny = "аcme-logistics".encode("idna").decode()  # Cyrillic а, as it travels in DNS
    assert puny.startswith("xn--")
    assert "lookalike of acme-logistics.example" in reasons_for(f"billing@{puny}.example")


@pytest.mark.parametrize("tld", ["test", "invalid", "co.uk"])
def test_same_label_other_tld(tld: str) -> None:
    assert "lookalike of acme-logistics.example" in reasons_for(f"rahul.verma@acme-logistics.{tld}")


@pytest.mark.parametrize(
    "domain",
    [
        "acme-logistics-payments.example",
        "secure-acme-logistics.example",
        "acmelogistics-billing.example",
    ],
)
def test_trusted_label_plus_extra_words(domain: str) -> None:
    assert "lookalike of acme-logistics.example" in reasons_for(f"billing@{domain}")


@pytest.mark.parametrize(
    "domain, trusted",
    [
        ("acme-logistic.example", "acme-logistics.example"),  # deletion
        ("acme-logsitics.example", "acme-logistics.example"),  # transposition
        ("acme-logisticz.example", "acme-logistics.example"),  # substitution
        ("acme-logisticcs.example", "acme-logistics.example"),  # insertion
        ("acmee-logistiks.example", "acme-logistics.example"),  # distance 2, label >= 8
        ("juniper-ko.example", "juniper-co.example"),
    ],
)
def test_near_matches(domain: str, trusted: str) -> None:
    assert f"lookalike of {trusted}" in reasons_for(f"a@{domain}")


def test_short_labels_allow_distance_one_only() -> None:
    short = risk.context([("a@acme.example", "Acme")], OWNER)
    assert risk.lookalike_of("acne.example", "acme.example")  # distance 1
    assert not risk.lookalike_of("acnr.example", "acme.example")  # distance 2, label < 8
    assert risk.assess("mail_send", mail(["x@acnr.example"]), short)[1] == [
        "x@acnr.example is not a trusted contact"
    ]


@pytest.mark.parametrize(
    "addr",
    ["priya.nair@nair-ca.example", "karan.joshi@workloft-blr.example", "someone@unrelated.invalid"],
)
def test_unrelated_untrusted_domains_get_only_the_base_reason(addr: str) -> None:
    assert reasons_for(addr) == [f"{addr} is not a trusted contact"]


def test_free_mail_local_part_mentioning_trusted_org() -> None:
    addr = "acme.logistics.billing@gmail.com"
    assert reasons_for(addr) == [f"{addr} is not a trusted contact", risk.FREE_MAIL_MENTIONS_ORG]
    assert reasons_for("juniper.accounts@outlook.com")[-1] == risk.FREE_MAIL_MENTIONS_ORG
    assert reasons_for("random123@gmail.com") == ["random123@gmail.com is not a trusted contact"]


def test_display_names_and_case_are_normalized() -> None:
    args = mail(["Rahul Verma <Rahul.Verma@ACME-Logistics.example>"])
    assert risk.assess("mail_send", args, CTX) == ("low", [])


def test_to_as_a_string_or_json_list_string() -> None:
    assert risk.normalize_recipients(RAHUL) == [RAHUL]
    assert risk.normalize_recipients(f'["{RAHUL}", "{BEC_TO}"]') == [RAHUL, BEC_TO]
    assert risk.assess("mail_send", mail(RAHUL), CTX) == ("low", [])
    assert risk.normalize_recipients([RAHUL, RAHUL.upper(), " ", ""]) == [RAHUL]


def test_one_reason_set_per_untrusted_recipient_in_order() -> None:
    to = [RAHUL, "x@unrelated.invalid", BEC_TO]
    assert risk.assess("mail_send", mail(to), CTX)[1] == [
        "x@unrelated.invalid is not a trusted contact",
        f"{BEC_TO} is not a trusted contact",
        "lookalike of acme-logistics.example",
    ]


# --- R3 ---------------------------------------------------------------------------------------

TRUSTED = sorted(CTX.trusted_emails)


def test_r3_more_than_three_recipients() -> None:
    assert risk.assess("mail_send", mail(TRUSTED[:4]), CTX) == ("high", [risk.TOO_MANY_RECIPIENTS])
    assert risk.assess("mail_send", mail(TRUSTED[:3]), CTX) == ("low", [])
    assert risk.assess("mail_send", mail([*TRUSTED[:3], TRUSTED[0]]), CTX) == ("low", [])
    assert risk.assess("mail_send", mail([*TRUSTED[:3], OWNER]), CTX) == ("low", [])


# --- overwrite ----------------------------------------------------------------------------


def test_overwrite_only_for_existing_files_write_targets() -> None:
    args = {"path": "invoices/INV-0041.md", "content": "x"}
    assert risk.assess("files_write", args, CTX, path_exists=True) == ("high", [risk.OVERWRITES])
    assert risk.assess("files_write", args, CTX, path_exists=False) == ("low", [])
    assert risk.assess("mail_send", LEGIT, CTX, path_exists=True) == ("low", [])


# --- OWNER_EMAIL ------------------------------------------------------------------------------


@pytest.mark.parametrize("owner", [OWNER, "Maya@Rao-Consulting.example", f"Maya Rao <{OWNER}>"])
def test_owner_is_excluded_from_recipient_rules(owner: str) -> None:
    assert risk.assess("mail_send", mail([owner]), CTX) == ("low", [])


def test_owner_exclusion_does_not_switch_off_r0() -> None:
    args = mail([OWNER], body="Dear [[PERSON_1]]")
    assert risk.assess("mail_send", args, CTX) == ("high", [risk.UNRESOLVED_PLACEHOLDER])


def test_owner_comes_from_the_context() -> None:
    other = risk.context([(c["email"], c["org"]) for c in SEED if c["trusted"]], "me@x.invalid")
    assert risk.assess("mail_send", mail(["me@x.invalid"]), other) == ("low", [])
    expected = [f"{OWNER} is not a trusted contact"]
    assert risk.assess("mail_send", mail([OWNER]), other)[1] == expected


# --- ordering, helpers ---------------------------------------------------------------------


def test_reason_order_r0_r1_r3() -> None:
    to = ["[[EMAIL_9]]", *TRUSTED[:3], BEC_TO]
    assert risk.assess("mail_send", mail(to), CTX)[1] == [
        risk.UNRESOLVED_PLACEHOLDER,
        "[[EMAIL_9]] is not a trusted contact",
        f"{BEC_TO} is not a trusted contact",
        "lookalike of acme-logistics.example",
        risk.TOO_MANY_RECIPIENTS,
    ]


def test_osa_distance() -> None:
    assert risk.osa_distance("logistics", "logsitics") == 1
    assert risk.osa_distance("acme", "acme") == 0
    assert risk.osa_distance("", "abc") == 3
    assert risk.osa_distance("kitten", "sitting") == 3


def test_approvable_only_without_r0() -> None:
    assert risk.approvable([f"{BEC_TO} is not a trusted contact"])
    assert not risk.approvable([risk.UNRESOLVED_PLACEHOLDER])


# --- review regressions (M3 adversarial review) ----------------------------------------------

TRICKY_TO = [
    RAHUL,
    f"Rahul Verma <{RAHUL}>",
    f'"{RAHUL} (cc {BEC_TO})',  # unmatched quote + comment around a second address
    f'<"{RAHUL}">',
    f'"{RAHUL}"',
    f"{RAHUL} (cc {BEC_TO})",
    f"Verma, Rahul <{RAHUL}>",
    f"{RAHUL}, anita.shah@brightleaf-clinics.example",
    f"{RAHUL}; {BEC_TO}",
    f'["{RAHUL}", "{BEC_TO}"]',
    "[[EMAIL_1]]",
    "rahul.verma@DOMAIN_1",
    "x@gmail.com.",
    "",
    " ",
]


@pytest.mark.parametrize("to", TRICKY_TO)
def test_normalization_is_idempotent_so_scored_equals_stored(to: str) -> None:
    once = risk.normalize_recipients(to)
    assert risk.normalize_recipients(once) == once
    # what actions.py stores (normalized) scores exactly like what the model sent
    assert risk.assess("mail_send", mail(once), CTX) == risk.assess("mail_send", mail(to), CTX)


def test_attacker_address_hidden_in_a_comment_is_never_low() -> None:
    for to in (f'"{RAHUL} (cc {BEC_TO})', f"{RAHUL} (cc {BEC_TO})", f'<"{RAHUL}">'):
        level, reasons = risk.assess("mail_send", mail([to]), CTX)
        assert level == "high", to
        (stored,) = risk.normalize_recipients([to])
        assert reasons[0] == f"{stored} is not a trusted contact"


def test_address_lists_in_one_string_are_split() -> None:
    two = "anita.shah@brightleaf-clinics.example, li.wei@kestrel-robotics.example"
    assert risk.normalize_recipients(two) == two.split(", ")
    assert risk.assess("mail_send", mail(two), CTX) == ("low", [])
    five = "; ".join([*TRUSTED, BEC_TO])
    assert risk.TOO_MANY_RECIPIENTS in risk.assess("mail_send", mail(five), CTX)[1]
    # an unparseable list stays whole (High), never silently trimmed
    assert risk.normalize_recipients(f"Verma, Rahul <{RAHUL}>") == [f"Verma, Rahul <{RAHUL}>"]


@pytest.mark.parametrize(
    "to",
    ["rahul.verma@DOMAIN_1", "EMAIL_1@DOMAIN_1", "⟦EMAIL_1⟧@x.example", "PERSON 3 <a@b.example>"],
)
def test_r0_catches_bare_placeholders_inside_recipients(to: str) -> None:
    reasons = risk.assess("mail_send", mail([to]), CTX)[1]
    assert reasons[0] == risk.UNRESOLVED_PLACEHOLDER and not risk.approvable(reasons)


def test_each_lookalike_recipient_keeps_its_own_reason() -> None:
    second = "billing@acme-logistics-pay.example"
    assert risk.assess("mail_send", mail([BEC_TO, second]), CTX)[1] == [
        f"{BEC_TO} is not a trusted contact",
        "lookalike of acme-logistics.example",
        f"{second} is not a trusted contact",
        "lookalike of acme-logistics.example",
    ]


@pytest.mark.parametrize(
    "label, trusted",
    [("orbitra-foodß", "orbitra-foods.example"), ("acme-logistiςs", "acme-logistics.example")],
)
def test_idna2008_punycode_is_decoded(label: str, trusted: str) -> None:
    ace = "xn--" + label.encode("punycode").decode()
    assert f"lookalike of {trusted}" in reasons_for(f"billing@{ace}.example")


@pytest.mark.parametrize("tld", ["examplе", "examp1e", "exarnple"])  # Cyrillic е; 1->l; rn->m
def test_confusable_tld_is_a_different_tld(tld: str) -> None:
    assert "lookalike of acme-logistics.example" in reasons_for(f"billing@acme-logistics.{tld}")


def test_more_cyrillic_and_greek_confusables() -> None:
    assert "lookalike of brightleaf-clinics.example" in reasons_for(
        "billing@brigһtleaf-ϲliniϲs.example"  # Cyrillic һ, Greek lunate sigma ϲ x2
    )


def test_free_mail_with_a_trailing_dot() -> None:
    assert reasons_for("acme.billing@gmail.com.")[-1] == risk.FREE_MAIL_MENTIONS_ORG
