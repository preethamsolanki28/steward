# Steward — session handoff

Hackathon entry for the Nebius x NVIDIA Global AI Hackathon (Devpost, Personal AI Track). Deadline Fri Oct 30, 2026, 10:00 AM PDT; team target is final submission by Fri Oct 23.

## Where we are (as of Sun Oct 18, 2026)

- M0–M4 are done; M5 is partly done (invoice-chase fix 10/10, STEWARD_DEMO one-shot, CI file, README draft on `t5-3-readme`).
- **Follow docs/06_finish_plan.md** (it replaces docs/04's remaining tasks). First: N1 (the demo brief job never runs after `make demo-reset`), N3 (model fallback), N4 (plain-words UI).
- Target submission Fri Oct 23; hard deadline Fri Oct 30, 10:00 AM PDT.

## Source of truth

- `AGENTS.md` (repo root, imported below) and `docs/00_problem.md` … `docs/05_demo_and_pitch.md`.
- `.claude/context/spec.md` is the locked spec v2 that all docs were generated from. If docs and spec disagree, ask the user; don't pick one.
- Background (facts as of 2026-10-02; re-verify anything version-sensitive before relying on it):
  - `.claude/context/research_brief.md` — tool fact sheet (Hermes, NemoClaw, OpenShell, Nebius Token Factory/Serverless, Nemotron), stack options, risks.
  - `.claude/context/factcheck.md` — adversarially verified claims and resolved contradictions.
  - `.claude/context/research_reports.md` — the 7 raw research reports with source URLs.
  - `.claude/context/critiques.md` — 73 review findings (judge, feasibility, technical, privacy lenses); all are already folded into spec v2.

## How the user wants to work

- Brutally honest, senior-engineer/judge voice. No flattery.
- No scope creep: Won't-do and cut-before-Day-1 items stay cut unless the user explicitly reverses them.
- Team: 2 AI engineers (E1 backend/agent, E2 frontend/product), Macs only (M1 Pro 16 GB, M4 Pro 24 GB).

## Moving to another laptop

1. Clone/copy this folder (including `.claude/`).
2. Run `bash .claude/restore.sh` from the project root. It copies the saved memory and the planning-chat transcript into `~/.claude/projects/<this path>/`.
3. Optional: `claude --resume a018bea7-e496-4575-8242-9102e8744761` to reopen the full planning conversation.

`.claude/session/` holds the full chat transcript and is gitignored. Never push it: the Devpost repo must be public.

@../AGENTS.md
