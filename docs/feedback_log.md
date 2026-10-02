# Friction log (Nebius / NVIDIA / Hermes)

One dated line per friction point. Feeds the mandatory Devpost feedback in T5.5
(used / worked / needs work / onboarding / would build again).

- 2026-10-02 — Hermes v2026.9.24: with `/opt/data/.no-bundled-skills` present before first boot, the image still seeds an "essential" bundled skill (`skills/autonomous-ai-agents/hermes-agent`) into `/opt/data/skills`.
- 2026-10-02 — Hermes v2026.9.24: the gateway rewrites the mounted `config.yaml` on every boot (appends `_config_version: 46`, logs "Migrating config schema 0 -> 46", writes backups to `/opt/data/backups/config/`), so a config rendered from a template is migrated again on each start.
- 2026-10-02 — Hermes v2026.9.24: the API server logs "network-accessible (0.0.0.0) AND the terminal backend is 'local' (unsandboxed)" even when the terminal toolset is removed via `platform_toolsets` and `agent.disabled_toolsets`; the warning doesn't reflect the effective toolset.
