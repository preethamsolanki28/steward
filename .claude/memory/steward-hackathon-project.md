---
name: steward-hackathon-project
description: "Steward — the team's Nebius x NVIDIA Global AI Hackathon (Personal AI Track) entry; deadline, hard gate, locked plan and where the docs live"
metadata:
  node_type: memory
  type: project
  originSessionId: a018bea7-e496-4575-8242-9102e8744761
  modified: 2026-10-02T07:49:18.910Z
---

The user and one teammate are building "Steward" for the Nebius x NVIDIA Global AI Hackathon on Devpost (Personal AI Track; Devpost lists no numeric PS ID). Hard deadline Fri 2026-10-30 10:00 AM PDT; team target is final submission by 2026-10-23; judging 2026-12-01 to 2026-12-15 (judge testing must stay free until then).

Concept (locked 2026-10-02): Hermes Agent (pinned v2026.9.24) + NVIDIA Nemotron on Nebius Token Factory, with a local Privacy Shield proxy that pseudonymizes client identifiers before inference, an Egress Ledger ("On your Mac" vs "Sent to Nebius"), and an Approval Gate with a BEC lookalike-domain guard. Persona: freelancer Maya Rao (they/them). Build Day 1 = 2026-10-03.

**Why:** Stage One gate requires a runtime Token Factory call + an NVIDIA open model (local-only fails); NemoClaw/OpenShell are alpha and deferred to a gated spike; Telegram deferred on purpose.

**How to apply:** the six docs in docs/ plus AGENTS.md in the project root are the source of truth (tasks T0.1–T5.7, gates DG-1/DG-2 recorded in docs/02). Check them before suggesting scope changes; never reintroduce cut items without the user asking. Related: [[team-and-hardware]].
