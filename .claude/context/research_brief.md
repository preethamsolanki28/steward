# Personal AI Hackathon: Planning Brief

*As of 2026-10-02. Based only on the research reports and the fact-check. Where the fact-check overrides a report, the text says so. Anything marked (unverified) has not been confirmed.*

---

## 0. Bottom line

1. **The hackathon is confirmed: the Nebius x NVIDIA Global AI Hackathon on Devpost.** The deadline is **Fri Oct 30, 2026, 10:00am PDT**, which is 28 days away. A 15-day build therefore leaves about 2 weeks of buffer. The demo must stay testable for free until **Dec 15, 2026, 12:00pm PT**.
2. **Hard gate, judged pass/fail.** At runtime the app must call **Nebius Token Factory** or run on **Nebius AI Cloud** compute, and it must use **at least one NVIDIA open model**.
   - NemoClaw's default inference path (NVIDIA Endpoints / build.nvidia.com) **does not satisfy this gate**. Neither does a local-only Ollama setup.
   - The Token Factory call must be the default path and must be visible in the video.
3. **NemoClaw, OpenShell, Hermes and Nebius Serverless are suggested, not required.** The track text says "tools such as". They help theme fit and the Quality of Idea score; none of them is a scored line item.
4. **The dev Mac (M1 Pro, 16 GB, verified) cannot run any 30B-class Nemotron.** That rules out Nano 30B, Lightning, Omni and Super locally. All inference is hosted. No NVIDIA GPU is needed for any recommended option.
5. **The biggest technical trap is NemoClaw combined with Nebius.**
   - Custom-endpoint onboarding can reject `https://api.tokenfactory.nebius.com/v1` with "DNS-backed HTTPS endpoint is not supported".
   - The documented workaround is `inference set` on an existing sandbox. It goes through the HTTPS Pin adapter, which has a **30-second total deadline** covering connect, TLS and the full response. Later responses are dropped.
   - Long Nemotron reasoning turns can exceed that. Hermes itself raises its stall timeout to 600s for Super and Ultra.
   - Run this as a day-1 spike with kill criteria.
6. **Pin every version on day 1 and do not upgrade during the build.**
   - NemoClaw is alpha. The installer installs `lkg` = v0.0.124, while the docs track main = v0.0.130.
   - NemoClaw pins OpenShell to exactly 0.0.116, but standalone OpenShell is 0.1.2, which is a breaking API. A migration is coming (epic #12558, opened 2026-10-01).
   - Hermes releases every 3-7 days, each bundling hundreds of PRs.
7. **Differentiation matters more than the plumbing.** There are 15,706 registrants. Several Personal AI repos using Nemotron on Token Factory are already public, and NVIDIA's own nemoclaw-community already ships a chief-of-staff, a Chrome side panel and a bot team. "Memory + Telegram + morning brief" is a cliché.

---

## 1. Tool fact sheet

### 1.1 NVIDIA NemoClaw

| Item | Fact |
|---|---|
| What | Host CLI, versioned blueprint and agent integration layer that runs an agent inside an OpenShell (0.0.116) sandbox. Agents: **OpenClaw** (default), **Hermes** (`nemohermes`), **LangChain Deep Agents Code**. The landscape report also listed "Pi (RC)"; the fact-check found it nowhere in the README or support matrix, so treat it as unconfirmed. |
| Repo / license | github.com/NVIDIA/NemoClaw, Apache-2.0, created 2026-03-15, ~22.6k stars, ~748 open issues and PRs |
| Maturity | **Alpha, "Early preview", no SLA.** About 130 `v0.0.x` tags since March; latest tag v0.0.130 (2026-10-01). Installer default is `lkg` = **v0.0.124** (2026-09-14, commit 6f3cced). |
| Pins | OpenShell `min = max = 0.0.116` on main and on v0.0.124. OpenClaw 2026.7.1 at lkg, 2026.9.2 on main. Hermes v2026.9.14 (0.21.3) in its managed image. |
| Install (pinned) | `curl -fsSL https://www.nvidia.com/nemoclaw.sh \| NEMOCLAW_INSTALL_REF= NEMOCLAW_INSTALL_TAG=v0.0.124 NEMOCLAW_NON_INTERACTIVE=1 NEMOCLAW_ACCEPT_THIRD_PARTY_SOFTWARE=1 NEMOCLAW_AGENT=hermes NEMOCLAW_PROVIDER=build NVIDIA_INFERENCE_API_KEY=nvapi-... NEMOCLAW_SANDBOX_NAME=pa bash`. Env vars go on the bash side of the pipe. **Do not** use `npm i -g nemoclaw`: it installs a placeholder 0.1.0 package with no binary. Recovery: `nemoclaw onboard --resume` or `--fresh`. |
| OS / hardware | Linux + Docker is "Tested" and the primary path (Ubuntu 24.04). **macOS Apple Silicon** with Docker Desktop or Colima is "Tested with limitations". Intel Mac and native Windows are unsupported; WSL2 is "Tested with limitations". RTX hosts are "Deferred" despite the March marketing. Minimum 4 vCPU / 8 GB / 20 GB disk; recommended 16 GB / 40 GB. **Node >= 22.19** (the fact-check corrected the landscape report's "22.16"; the Mac has 22.21.1). npm 10+, Xcode CLT, python3. Sandbox image ~2.4 GB. No GPU needed with hosted inference. |
| macOS specifics | Start Docker Desktop or Colima first and give the VM at least 4 vCPU / 8 GB (Colima: `colima start --cpu 6 --memory 12 --disk 100`). Default Colima at 2 vCPU / 2 GiB **stalls the build silently**. Landlock falls back to `best_effort` inside the Docker VM. Read-only `--host-mount` is unsupported. Open bugs: **#12367** (Colima `docker.sock` regression; workaround `export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock`), **#11984**, **#12501**, **#3136** (`host.docker.internal` not resolving). |
| Inference | Menu options include NVIDIA Endpoints (default `nvidia/nemotron-3-super-120b-a12b`, fallback Ultra), OpenRouter, OpenAI, Anthropic, Gemini, "Other OpenAI-compatible", Local Ollama (>= 0.32.9; the Mac has **0.13.1**) and an experimental Model Router. The agent only ever calls `inference.local`; the key stays on the host. **There is no Nebius provider.** |
| Nebius path (fact-check) | Onboarding with `NEMOCLAW_PROVIDER=custom NEMOCLAW_ENDPOINT_URL=https://api.tokenfactory.nebius.com/v1 ...` **may be rejected** (DNS-backed HTTPS). Documented workaround: onboard with NVIDIA Endpoints, then run `COMPATIBLE_API_KEY=$NEBIUS_API_KEY nemoclaw pa inference set --provider compatible-endpoint --model <id> --endpoint-url https://api.tokenfactory.nebius.com/v1 --credential-env COMPATIBLE_API_KEY --inference-api openai-completions`. This routes through the HTTPS Pin adapter on host port 11438 with a **hard 30s total deadline**. The equivalent command for a Hermes sandbox is (unverified); a "Hermes host-side config set write" is one of the rejection cases. `NEMOCLAW_REASONING=true` skips the tool-call and streaming checks. `NEMOCLAW_REASONING_EFFORT` sends `reasoning_effort`, not Nemotron's `chat_template_kwargs`. |
| Features | Workspace memory in `/sandbox/.openclaw/workspace` (SOUL.md, USER.md, MEMORY.md, `memory/YYYY-MM-DD.md`). `skill install` (SKILL.md with `name` frontmatter; limits 1,024 files / 64 MiB). Heartbeats via `NEMOCLAW_AGENT_HEARTBEAT_EVERY`. Cron through `openclaw automations` / `openclaw cron`; **each job needs a manual `operator.admin` approval** (`openclaw devices approve <id>`). Managed MCP is **HTTPS Streamable HTTP with bearer auth only** (`mcp add --url --env`). Channels: Telegram, Slack and Discord "Tested"; WhatsApp (Web QR) and WeChat "Tested with limitations"; Teams and Google Chat Experimental (the fact-check confirmed this split). Snapshots: `snapshot create|restore`; `destroy` deletes memory unless a snapshot exists. |
| Network policy | Deny-by-default. Tiers are Restricted, Balanced (default), Open and Personal; Personal allows any host on 80/443 and undercuts the privacy story. Unlisted hosts **block until approved** in `openshell term`. |
| Security baggage | NVIDIA bulletin 2026-08-25 (a_id 5872): OpenShell sandbox-escape CVEs rated CVSS 9.9 and an Ollama-on-0.0.0.0 CVE (details from a secondary source; the NVIDIA page returned 403). OpenClaw has 722 GitHub advisories in 2026, CVE-2026-25253, and ClawHub malware (ClawHavoc). XDA review: prompt injection is unsolved and data can be exfiltrated through allowed endpoints. OpenShell telemetry is **on by default**; how to disable it on a NemoClaw-managed gateway is (unverified). |
| Always-on | The demo should run on a headless Ubuntu VM over SSH ("Tested with limitations"). Keep the dashboard on loopback (`ssh -N -L 18789:127.0.0.1:18789`). **Reboot recovery is manual and not guaranteed.** |
| Our likely use | The **sandbox and policy shell** around Hermes (`nemohermes`), demoed for credential isolation and egress denials, **only if** the day-1 spike shows Nebius inference stays under the 30s cap. |

### 1.2 NVIDIA OpenShell

| Item | Fact |
|---|---|
| What | Rust sandbox runtime. Untrusted workload plus a trusted supervisor: Landlock, seccomp, non-root execution. Every TCP/DNS connection is policy-checked, with L7 inspection (REST, GraphQL, MCP tool names, JSON-RPC, WebSocket). Credentials appear only as `openshell:resolve:env:KEY` placeholders. |
| License / repo | Apache-2.0, github.com/NVIDIA/OpenShell, created 2026-02-24, ~14.1k stars, ~526 open issues and PRs |
| Versions | **v0.1.2 (2026-09-28)** is current. **v0.1.0 (2026-09-25) was breaking**: it removed `inference.local`, `openshell inference *`, built-in provider profiles, the community images (`--from openclaw`/`ollama`/`base`) and Dockerfile builds in `sandbox create`. The fact-check confirms that `--from openclaw` and `inference.local` exist **only on 0.0.x**, i.e. inside NemoClaw. The March launch blog, HermesClaw and `uv tool install openshell` are stale. The PyPI `openshell` package is the SDK only. Weekly Tuesday releases; security fixes cover N-1. |
| Install | `curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh \| OPENSHELL_VERSION=v0.1.2 sh`, then `openshell status`. On macOS it installs as a brew service at `https://localhost:17670`. |
| OS / hardware | Linux Debian/Ubuntu amd64 and arm64 (kernel 6.2+ for Landlock ABI v3). macOS **Apple Silicon only**: Homebrew, **Docker Desktop 28+ with host networking ON and Enhanced Container Isolation OFF**. WSL2 experimental. No GPU required. The MicroVM driver on macOS is rough (#3955, #3506, #3095), so use the Docker driver. |
| **Version conflict** | NemoClaw needs exactly 0.0.116; standalone is 0.1.2. **They cannot share a gateway; pick one track per machine.** |
| BYOC requirements | Standard Linux base (not distroless or scratch), **non-root USER**, writable `/sandbox`, `iproute2`, start command after `--` (ENTRYPOINT is replaced). Run: `openshell sandbox create --name X --from img:local --provider P --policy policy.yaml --detach -- <cmd>`. `--upload` cannot be combined with a trailing command (#3995). |
| Policy | YAML `version: 1`. Filesystem, landlock and process settings are fixed at start; **network rules hot-reload**. Rules name the **real interpreter path** (e.g. `/usr/bin/python3.12`; symlinks fail). Binaries are hashed on first use. Loopback and 169.254.169.254 are always blocked; reach host services via `host.openshell.internal` (whether this works on macOS is unverified). |
| Inference in 0.1.x | No router. Attach a provider profile per sandbox and call the native endpoint. A Nebius profile must be written by hand (YAML in the openshell report: `id: nebius-tf`, host `api.tokenfactory.nebius.com:443`, bearer). |
| Demo-grade features | `openshell logs X --tail` gives OCSF ALLOWED/DENIED lines naming the policy. `openshell term` is a TUI. The policy advisor (`agent_policy_proposals_enabled`) lets the agent propose a rule, a human approve it (`openshell rule approve`), and the rule hot-reload. Policy revisions with rollback. `openshell-prover check` returns `within_boundary` or `exceeds_boundary` but reports MCP/GraphQL rules as unsupported. Supervisor middleware (external gRPC, can redact bodies; API still evolving; the built-in regex only catches `sk-`). |
| Landmines | OCSF JSONL file not written on Docker Desktop/WSL2 (#3895). The gateway log buffer is lost on restart. **The sandbox main process does not auto-restart.** Sandboxes stuck in Error need delete and recreate (#3308). Telemetry is on; set `OPENSHELL_TELEMETRY_ENABLED=false` (how to apply that to the brew service is unverified). |
| Our likely use | Either via NemoClaw (0.0.116), or standalone 0.1.2 wrapping a custom non-root Hermes image or a custom agent. The live **"DENIED → agent proposes rule → human approves → hot reload"** sequence is the strongest 20-second segment for the video. |

### 1.3 Nous Research Hermes Agent

| Item | Fact |
|---|---|
| What | Python agent framework covering nearly every problem-statement feature: persistent memory, self-written skills, MCP client, cron, subagents, a 20+ platform messaging gateway, and an OpenAI-compatible API server on `:8642`. |
| License / repo | MIT, github.com/NousResearch/hermes-agent, ~250.7k stars. **v0.21.5 = tag v2026.9.24** (2026-09-24). Releases every 3-7 days with roughly 460-1,800 PRs each. 14.4k open issues; the install/update E2E matrix was **red** on 2026-09-29 (#128399). |
| Install | `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash`, pinned with `--commit <sha>` or `--branch`. It brings Python 3.14, Node, ripgrep and FFmpeg. pip, uv and brew installs are unsupported. **Do not run `hermes update` mid-build** (macOS update and launchd bugs #126883, #105938). |
| OS | macOS Apple Silicon, Linux, WSL2 and Windows are Tier 1. Docker image `nousresearch/hermes-agent` for amd64 and arm64. The image **ends as `USER root` with ENTRYPOINT `entrypoint-dispatch.sh`**; the fact-check corrected "s6 /init". It is unusable on standalone OpenShell as-is and needs a custom non-root image. |
| Providers | `provider: nvidia` (`NVIDIA_API_KEY`, `https://integrate.api.nvidia.com/v1`; full `nvidia/` IDs required; **never define a custom provider named `nvidia`**, #123997). `provider: nebius-token-factory` (aliases `nebius`, `nebius-tf`; `NEBIUS_API_KEY`; base `https://api.tokenfactory.nebius.com/v1`; aux default `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`). **Both built-in fallback lists contain removed model IDs; set the model and fallbacks explicitly.** Whether `reasoning_effort` reaches Nemotron is **unclear** per the fact-check ("nemotron" is not in the allowlist, but `supports_reasoning` can still trigger it), so set `extra_body.chat_template_kwargs` explicitly and test. |
| Model constraints | **Minimum context 64,000 tokens.** Ollama defaults to 4K, so set `OLLAMA_CONTEXT_LENGTH=64000`. Stall-timeout floor is 600s for Super and Ultra and 300s for Nano and Lightning; hosted NIM idles streams after 60-180s. |
| Memory | `~/.hermes/memories/MEMORY.md` (**2,200 chars**) and `USER.md` (**1,375 chars**), loaded as a **frozen snapshot at session start**. The gateway chat is one endless session, so new memories only appear after `/new`. History lives in SQLite FTS5 at `~/.hermes/state.db` (`session_search`). Pluggable providers: Honcho, Mem0, Hindsight, OpenViking. `memory.write_approval` is on/off only. |
| Skills / cron | `~/.hermes/skills/<cat>/<name>/SKILL.md` (agentskills.io format). The agent self-authors skills via `skill_manage`; `skills.write_approval` stages writes in `~/.hermes/pending/skills/`. A curator marks skills stale after 14 days and archives them after 30. Cron: `hermes cron create "every 1h" "..." --skill X`; **fires only while the gateway runs**. |
| Messaging | Telegram (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`) is the safe choice. The default WhatsApp adapter is **Baileys (unofficial, ToS and ban risk)**; WhatsApp Cloud API is official. Inside the OpenShell proxy, the Slack (#90601) and Mattermost (#70116) adapters are broken (open issues). |
| In NemoClaw | "Tested", but **"production parity with OpenClaw not yet asserted"**. Its model-compatibility registry is empty, there are no Hermes-specific unit tests, and web search is Tavily only. Open: #90623 (SessionDB write failures in long-running NemoHermes). Hermes strips secret-looking env vars from skill subprocesses (#4429), so **OpenShell placeholders never reach skill scripts**. |
| Our likely use | **The agent runtime.** Its native Nebius provider avoids NemoClaw's 30s adapter, and memory, skills, cron and Telegram come free. Our own code goes into skills, a memory provider, and the trust layer (section 5). |

### 1.4 Nebius (Token Factory + Serverless AI)

| Item | Token Factory | AI Cloud Serverless AI |
|---|---|---|
| What | OpenAI-compatible per-token inference. Base **`https://api.tokenfactory.nebius.com/v1`**; global URL only, since regional URLs "may stop working" (fact-check). Endpoints include `/v1/chat/completions` (tools, `tool_choice`, `response_format`, `reasoning_effort`), `/v1/embeddings`, `/v1/rerank`, `/v1/responses` and `/v1/models`. | Run any container: **Endpoints** (managed HTTPS URL plus optional bearer token), **Jobs** (1h minimum, 168h maximum timeout; no schedule flag documented), **Devlabs/DevPods**. CPU-only is allowed (`--platform cpu-d3`). |
| Sign-up | Google or GitHub login at tokenfactory.nebius.com. **Bank card mandatory.** $1 trial. A failed card charge **suspends the account**. | console.nebius.com. **Card charged $25 upfront** as prepaid balance. Separate billing from Token Factory. |
| Credits | **$25** promo `NEBIUS-DEVPOST-GLOBAL26` plus **$25** Builders Program (expires 90 days after issue). Whether each team member can claim separately is (unverified). | **No hackathon credit found.** Out of pocket. |
| Status | Public endpoints are "best suited for testing and non-critical workloads". Dynamic rate limits (example baseline 60 RPM / 400K TPM) with 429s and `x-ratelimit-*` headers. | **Preview, no SLA**, single node, no autoscaling or scale-to-zero, no auto-recovery. **Stopping an endpoint deletes its VM and disk**, so persist state on a mounted bucket or shared filesystem. Provisioning can fail with `NotEnoughResources` after 30 minutes. |
| Privacy | Inputs and outputs are **retained by default** for speculative decoding (Finland) and never used for training. **Turn on Zero Data Retention** (org-level toggle in the profile) and say so in the README and video. Public endpoints route "Global" with no region guarantee. | Your own container in your own tenant. |
| Model churn | Removed Aug 31: Nemotron-3-Nano-Omni, Llama-3.1-Nemotron-Ultra, Hermes-4-70B and others, with **no rerouting**. A model could disappear before Dec judging. The Nebius Nemotron marketing page is stale. | Cold starts are about 5 min (vLLM GPU) or 8-12 min (NIM; pulls straight from nvcr.io often fail, so mirror to Nebius CR). CPU cold start is unknown. |
| CLI | n/a | `curl -sSL https://artifacts.nebius.cloud/cli/install.sh \| bash`, then `nebius profile create ...`. Example: `nebius ai endpoint create --name hermes-gw --image <img> --platform cpu-d3 --preset 2vcpu-8gb --disk-size 30Gi --container-port 8642 --env-secret ... --volume <fs>:/opt/data:rw --public --subnet-id $SUBNET_ID` (adapted, untested). Set `--disk-size` explicitly: the default is 250Gi (~$17.75/month). |
| Unknowns | Whether `chat_template_kwargs` (`enable_thinking`, `force_nonempty_content`) passes through; default per-account rate limits; whether the global URL serves every Nemotron model (Super and Ultra are listed in us-central1); Qwen3-Embedding-8B context (40,960 vs 32K, unresolved). | **Privileged mode or Docker-in-Docker is undocumented**, so NemoClaw/OpenShell inside a Serverless Endpoint is (unverified, likely no); use a Compute VM for those. Whether Nebius `--auth token` forwards the `Authorization` header. |
| Our likely use | **The gate.** All Nemotron runtime calls go here. | One **Serverless Job** (e.g. a nightly memory-consolidation or audit digest) to show "Nebius Serverless" on camera. Optionally host a Hermes-only gateway as a CPU Endpoint. One of the judges is Nebius's **Serverless AI PM**. |

### 1.5 NVIDIA open models

**IDs differ by platform, and a typo breaks onboarding validation.**

| Model | Nebius Token Factory ID (verified live) | build.nvidia.com ID (verified live) | $ in/out per 1M (Nebius) | Context | License |
|---|---|---|---|---|---|
| Nemotron 3.5 Lightning 30B-A3B (Aug 11, 2026) | `nvidia/Nemotron-3_5-Lightning` | `nvidia/nemotron-3.5-lightning-30b-a3b` | 0.06 / 0.24 (~314 tok/s) | 1M | OpenMDW-1.1 |
| Nemotron 3 Super 120B-A12B | `nvidia/nemotron-3-super-120b-a12b` | `nvidia/nemotron-3-super-120b-a12b` | 0.30 / 0.90 (~127 tok/s) | 256K | NVIDIA Nemotron Open Model License |
| Nemotron 3 Ultra 550B-A55B | `nvidia/Nemotron-3-Ultra-550b-a55b` | `nvidia/nemotron-3-ultra-550b-a55b` | 1.00 / 3.00 | 1M | OpenMDW-1.1 |
| Nemotron 3 Nano 30B-A3B | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | `nvidia/nemotron-nano-3-30b-a3b` (sic) | 0.06 / 0.24 (~60 tok/s) | 262K | Nemotron OML |
| Nemotron 3 Nano 4B | not hosted | not listed | local only | 262K | Nemotron OML |
| Nemotron 3 Nano Omni | **removed** Aug 31 | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | n/a | 256K | NVIDIA Open Model Agreement |
| Nemotron-3-Embed-1B | **not on Nebius** (only Qwen/Qwen3-Embedding-8B) | `nvidia/nemotron-3-embed-1b` | n/a | 32K seq | OpenMDW-1.1 |
| Nemotron-3.5-Content-Safety (4B guard) | not on Nebius | `nvidia/nemotron-3.5-content-safety` | n/a | n/a | OpenMDW-1.1 (+ Gemma terms) |

All four Nebius Nemotron models are tagged `function_calling`. None has had independent tool-call testing (no key was available during research).

Vendor benchmark trade-offs (Lightning vs Super):

- **Lightning is ahead on:** PinchBench 85.4 vs 80.4, BrowseComp 37.0 vs 22.8.
- **Super is ahead on:** Terminal-Bench 39.6 vs 24.6, SWE-bench Verified 63.1 vs 51.6, AA-LCR 58.4 vs 52.0.

All Nemotron 3 models **reason by default**; disable it with `chat_template_kwargs.enable_thinking=false`. Pass-through on Nebius is unverified.

Known quirk: given many tool definitions, Super has replied to plain chat with a tool call and empty content (NemoClaw #1193, fixed). `force_nonempty_content=True` is the documented mitigation.

Local on the 16 GB Mac:

- Only `nemotron-3-nano:4b` (2.8 GB at Q4) fits. Its vendor BFCL v3 score is 61.1.
- It is unvalidated in NemoClaw, its 64K context in Hermes is untested, and it needs Ollama >= 0.32.9 (installed: 0.13.1).
- **Local inference cannot satisfy the gate.**

---

## 2. Realistic stack assemblies

Capacity: 2 people × ~13 working days ≈ **26 person-days (pd)**, plus ~2 weeks of calendar buffer before Oct 30. Every option uses **Nemotron on Token Factory** for the gate.

### Option A: NemoClaw + OpenClaw (default agent), Token Factory through `inference set`

- **Shape:** NemoClaw v0.0.124 (OpenShell 0.0.116, OpenClaw 2026.7.1). Onboard with NVIDIA Endpoints, then `inference set` to Token Factory. Custom SKILL.md skills, Telegram, heartbeat, managed HTTPS MCP. Demo host is an Ubuntu 24.04 VM (4 vCPU / 16 GB) on Nebius Compute.
- **Effort:** setup and VM 3-5 pd. Nebius wiring 1-3 pd, failure-prone. Cron approval scripting 1 pd. Differentiator 10-12 pd. Video, README, clean-install testing 4 pd. **Total ≈ 20-25 pd.**
- **Demo-ability:** high. Dashboard, OpenShell denials and the official NVIDIA "reference stack" story.
- **Failure risk: high.**
  - The 30s adapter deadline with reasoning models.
  - Docs track OpenClaw 2026.9.x while lkg ships 2026.7.1, so config keys can mismatch.
  - OpenClaw's security reputation (722 advisories, ClawHavoc) weakens a "private" pitch.
  - `operator.admin` approval for each cron job.
  - Highest overlap with NVIDIA's own recipes.
- **Platform:** Mac dev works with limitations. Linux VM recommended for the always-on demo. No NVIDIA GPU needed.

### Option B: Hermes Agent sandboxed by OpenShell, Nemotron on Token Factory (two variants)

**B1: `nemohermes` (official, OpenShell 0.0.116)**

- **Shape:** NemoClaw v0.0.124 with `NEMOCLAW_AGENT=hermes`, then switch inference to Token Factory. The Hermes version is whatever NemoClaw's managed image pins (v2026.9.14).
- **Effort ≈ 20-25 pd**, the same as A.
- **Failure risk: high.** It inherits A's 30s cap and rejection issues. On top of that: "parity not asserted", an empty model registry, the Slack adapter broken in the proxy, #90623 SessionDB failures, and possibly no clean Nebius path for Hermes sandboxes, since the host-side config write rejects DNS-backed HTTPS (unverified for `inference set`).

**B2: Hermes (pinned v2026.9.24) on standalone OpenShell v0.1.2 (recommended primary, pending the spike)**

- **Shape:**
  - A custom non-root image (`python:3.12-slim` + iproute2, user `agent`, `HERMES_HOME=/sandbox/.hermes`).
  - A hand-written `nebius-tf` provider profile, so the native `nebius-token-factory` provider has no 30s adapter.
  - A policy allowing only `api.tokenfactory.nebius.com`, `api.telegram.org` and the chosen tool hosts.
  - Policy advisor enabled for the live approval demo.
  - Host: Mac (Docker Desktop with host networking on and ECI off) for dev; Nebius Compute VM for always-on.
- **Effort:** image, profile and policy plumbing 4-7 pd (undocumented combination). Hermes config, skills and Telegram 2-3 pd. Differentiator 10-12 pd. Video and README 4 pd. **Total ≈ 22-28 pd. Tight.**
- **Demo-ability:** high. Current OpenShell API with OCSF logs, advisor and prover, plus Hermes's self-written skills.
- **Failure risk: medium.**
  - Hermes on 0.1.x is **undocumented and untested by NVIDIA**.
  - The long-running command (`hermes gateway`) inside the sandbox is unverified.
  - Seccomp-mediated DNS behavior with Hermes's web and messaging tools is unknown.
  - Placeholder credentials do not reach skill subprocesses (#4429).
  - Binary-hash denials appear after pip changes.
- **Platform:** Mac or Linux. No NVIDIA GPU. **Cannot coexist with B1 or A on the same machine**, because the OpenShell versions conflict.

### Option C: Thin custom agent (Python, OpenAI SDK to Token Factory) inside OpenShell 0.1.2 BYOC

- **Shape:** A ~1.5-3k LOC agent with tool loop, SKILL.md-compatible skills, a provenance-tagged memory store (SQLite), a Telegram Bot API channel, an APScheduler cron, and its own approval queue. The BYOC sandbox is the documented happy path (non-root image + `-- python /sandbox/app.py`). Background work runs as a Nebius Serverless Job. The Hermes-free variant can also run directly as a **CPU Serverless Endpoint** (no OpenShell there).
- **Effort:** core agent, memory, skills, channel and cron 8-11 pd. OpenShell BYOC 2-3 pd. Differentiator 7-9 pd (it is the product). Video and README 4 pd. **Total ≈ 22-27 pd.**
- **Demo-ability:** medium-high. Full control of UX and receipts, but it looks less "assembled from NVIDIA/Nous tools".
- **Failure risk:** **low technically, medium on judging.** The judges' bar warns against "a chatbot with a system prompt", and the track names Hermes and NemoClaw. We rebuild memory and skills that Hermes provides.
- **Platform:** Mac or Linux. No NVIDIA GPU.

### Decision rule (Days 1-2 spike; one person per track, on different machines)

| Spike | Pass criterion | If it fails |
|---|---|---|
| S1 (all): `curl` Token Factory with `tools` on Lightning and Super | Structured `tool_calls` returned; latency p95 measured with `enable_thinking` on and off; whether `chat_template_kwargs` and `reasoning_content` behave | Model choice changes. If both fail tool calls, stop and re-plan. |
| S2 (Dev 1, Mac): `nemohermes` v0.0.124, then `inference set` to Nebius, 20 tool-using turns | Fewer than 5% of turns exceed 30s; the Hermes sandbox accepts the custom endpoint | Drop A/B1 as the inference path |
| S3 (Dev 2, VM or second machine): Hermes v2026.9.24 in an OpenShell 0.1.2 BYOC image with the `nebius-tf` profile and Telegram egress | `hermes gateway` stays up 2h, answers on Telegram, and a DENIED line appears in `openshell logs` | Fall back to C (same BYOC skeleton, our own loop) |

**Default bet: B2, with C as the fallback.** The sandbox skeleton and differentiator code transfer between them. A/B1 are kept only if S2 passes cleanly, because they carry the official NVIDIA path.

---

## 3. Model choice

**Recommendation**

- **Interactive / primary:** `nvidia/nemotron-3-super-120b-a12b` on Token Factory. It is the known-good default for both NemoClaw (OpenClaw and Hermes) and the Hermes docs, and it is stronger on terminal, coding and long context. Set `force_nonempty_content` if it is passed through.
- **Always-on executor** (heartbeats, cron, Hermes `auxiliary.background_review`, classification): `nvidia/Nemotron-3_5-Lightning`. It is 5x cheaper and about 2.5x faster, and NVIDIA positions it for always-on agents. Caveats: it is about 7 weeks old and **not in NemoClaw's validated lists**. Promote it to primary if S1 shows equal tool-call reliability.
- **Fallback chain:** set explicitly in config (Super ↔ Lightning ↔ `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`). **Never rely on Hermes's built-in fallback lists**, which contain removed IDs.
- **Dev only:** build.nvidia.com with the same IDs (see the table in 1.5), a free nvapi key (~1,000 credits, ~40 RPM observed, trial or evaluation terms). **Not for the judged runtime.** It fails the gate and the trial terms are unsuited to a live demo through Dec 15.
- **Optional local:** `nemotron-3-nano:4b` via Ollama (upgrade to >= 0.32.9 with `brew upgrade ollama`) for an on-device PII and triage pre-pass only. Weak tool calling, unvalidated, and the 16 GB RAM is shared with an 8 GB Docker VM. Frame privacy as "your Nebius tenant + ZDR + sandbox policy + optional on-device redaction", **not** "everything runs on my laptop".
- **Skip:** Ultra (cost), Omni (not on Token Factory; needs an L40S self-host at about $1.55/h), and the NeMo ASR/TTS/safety stack (documented for Linux + NVIDIA GPU only). Voice, if wanted, is `parakeet-mlx` on the Mac.
- **Embeddings:** Token Factory has only `Qwen/Qwen3-Embedding-8B` (not NVIDIA). Nemotron-3-Embed-1B is on build.nvidia.com (trial) or would need a GPU self-host. Plain Hermes FTS5 plus curated MEMORY.md may be enough; avoid vector memory unless the differentiator needs it.

**Licenses:** we call the models through an API and do not redistribute weights, so the risk is low. Add a NOTICE file anyway: Nemotron OML attribution for Super and Nano, OpenMDW-1.1 for Lightning. The repo itself must be Apache-2.0, MIT or MPL-2.0. Hermes is MIT; NemoClaw and OpenShell are Apache-2.0.

**Cost estimate (assumptions are mine and unverified; prompt-caching discounts on Token Factory were not researched)**

Assumptions: ~20K input tokens per agent call (system prompt, tools, memory, history) and ~2K output including reasoning. Dev usage is 2 devs × 15 days × 250 calls = 7,500 calls, i.e. about 150M in / 15M out. Always-on runs Oct 15 to Dec 15 (~60 days) with a 30-minute heartbeat (48 calls/day, i.e. ~60M in / ~3M out total).

| Item | Lightning | Super | Ultra |
|---|---|---|---|
| Dev (15 days) | ~$13 | ~$59 | ~$195 |
| Always-on heartbeat through Dec 15 | ~$4 | ~$21 | ~$66 |
| Demo and judge traffic | <$5 | <$15 | n/a |
| **Token total** | **~$20** | **~$95** | don't |

Credits are ~$51 per Token Factory account ($25 promo + $25 Builders + $1 trial). Per-member stacking is unverified. **Strategy:** Super for interactive turns and Lightning for every loop lands at about $40-60. Lengthen heartbeats to 2h or more, or make them no-LLM script checks.

| Hosting (cpu-d3 at $0.015/vCPU-h + $0.0045/GiB-h) | Per day | Oct 15–Dec 15 |
|---|---|---|
| Compute VM 4 vCPU / 16 GB (NemoClaw or OpenShell host) | ~$3.17 | **~$190** plus ~$6 for a 40 GiB disk |
| Serverless CPU Endpoint 2 vCPU / 8 GB (Hermes-only gateway, no OpenShell) | ~$1.58 | ~$95 |
| Nightly Serverless Job, 2 vCPU, ~10 min actual (1h maximum timeout, per-second billing) | ~$0.01 | <$1 |
| L40S GPU endpoint | ~$37 | do not |

Add the $25 card pre-charge on AI Cloud. Whether an Indian card works for auto-charge is (unverified), and a failed charge suspends Token Factory.

---

## 4. Hackathon facts

| Item | Fact |
|---|---|
| Name | **Nebius x NVIDIA Global AI Hackathon**, "Build the next frontier of AI on open infrastructure". Sponsor Nebius B.V., administered by Devpost, NVIDIA co-organizing, Tavily as partner. |
| URL | https://nebiusglobalaihackathon.devpost.com/ (rules at `/rules`). The fact-check confirmed the Personal AI text matches word for word. |
| Track / PS ID | **"Personal AI" track. No PS ID exists on Devpost**; tracks are named only (Coding and Agentic Engineering, Best Apps and Agents, Personal AI, Physical AI). If a PS ID was seen elsewhere, it was not found. |
| Dates | Submissions Aug 26, 2026 9:00am PT to **Oct 30, 2026 10:00am PDT** (17:00 UTC / 22:30 IST). **No edits after the deadline.** Judging Dec 1, 9:00am PT to **Dec 15, 2026 12:00pm PT**. Winners around Jan 11, 2027. |
| Gate (Stage One, pass/fail) | (a) Reasonably fits the theme; a "superficial rebrand" fails. (b) **Runtime call to the Token Factory inference API, or deployment on Nebius AI Cloud compute (Serverless Jobs, Serverless Endpoints, DevPods).** (c) **At least one NVIDIA open model** (Nemotron 3 Ultra/Super/Nano, GR00T, Cosmos, Sonic named). Whether a plain Nebius Compute VM counts as "AI Cloud compute" is (unverified); the Token Factory call makes it moot. |
| Stage Two criteria | **Four criteria, equally weighted (25% each):** (1) **Technological Implementation**: build quality plus how effectively it uses Token Factory or AI Cloud models and Nemotron. (2) **Design**: a complete, coherent product, not a proof of concept. (3) **Potential Impact**: a credible, specific case for a real problem and audience. (4) **Quality of the Idea**: a creative, non-obvious use of Nebius and NVIDIA open models. Ties are broken in that order. **The 1-5 scale appears only in update 46204, not in the Rules.** |
| Track bar (update 46204) | "a chatbot with a system prompt is fine", but what judges hope to see is "an assistant that remembers context across sessions and takes real action on your behalf". "Judges love to see tracks pushed further than the basics." |
| Submission | (1) Working project. (2) **URL to a working demo, hosted app or test build.** (3) Text description. (4) **Public GitHub, GitLab or Bitbucket repo with an Apache-2.0, MIT or MPL-2.0 license visible at the top**, and a README with setup steps that **calls out the NVIDIA model and the Nebius tools**. (5) **Public YouTube video under 3 minutes** showing the project running on its target device; organizers advise naming Nebius and NVIDIA **with audio**. (6) Track. (7) **Mandatory specific feedback** on Token Factory, AI Cloud and NVIDIA tools. (8) If code pre-existed, an explanation of the significant updates. |
| Other rules | **Functionality:** "successfully installed and running consistently on the platform for which it is intended and must function as depicted in the video". **Free testing access without restriction until Dec 15** (credentials in the testing instructions if gated). **Third-party integrations must be authorized under their terms.** New or significantly updated after Aug 26 (keep the git history). Multiple submissions only if substantially different. |
| Prizes | $20k / $10k / $6k overall. **Personal AI track prize = one Jetson Orin Nano (hardware only).** Best Use of Tavily $3k (needs a functional runtime Tavily call). 20 City awards of $500 (IRL attendees; no Indian city). 10 feedback awards of $100. **A project can win one Overall award, or one Track award plus one Bonus award.** |
| Credits | $25 Token Factory (`NEBIUS-DEVPOST-GLOBAL26`), $25 Token Factory plus $25 Tavily via Builders, Tavily code `BBDEVPOST`. **No NVIDIA credits found.** |
| Judges | 23 from NVIDIA, Nebius and Tavily, including Nebius's **Serverless AI TPM** and **Token Factory founding PMM**. |
| Competition | **15,706 registrants.** Public Personal AI repos already exist (Alvnvnc/mitra, fawad07/nebius-personal-ai, Akshat-Soni02/nxn-global-ai-hackathon-personal-agent, ProttoyDip/talkback). |
| Eligibility | Excludes Brazil, Quebec, Russia, Crimea, Cuba, Iran, North Korea and sanctioned regions. India is not excluded. No team-size cap stated. W-8BEN for non-US winners. |

**Not found or unclear:**

- A PS ID.
- The Devpost form fields (no login).
- Whether a local install or GitHub release counts as a "test build" for this track (wording suggests yes; low-medium confidence).
- **Whether judges bring their own Nebius key or expect a working hosted demo.** Plan for a hosted, funded demo through Dec 15.
- Whether each member can claim the credits.
- Whether using NemoClaw, OpenShell or Hermes earns explicit credit (it does not appear in the criteria).
- Exact dates of the update posts (approximate).

---

## 5. Competitive landscape

| Player | Type | Status (Oct 2026) | Relevance to us |
|---|---|---|---|
| OpenClaw | OSS always-on agent | 391k stars, v2026.9.7. **722 advisories in 2026** (14 critical); 40k+ exposed instances (secondary source); ClawHub malware (341 of 2,857, later ~1,103 of 14,706, secondary); compaction drops constraints (Summer Yue inbox wipe); $200-500/day bills reported | The default everyone forks; its security story is our foil |
| Hermes Agent | OSS agent framework | 250.7k stars, v2026.9.24. MPBench (Jun 2026): **memory poisoning ASR 66.67% on Hermes** vs 34.25% on OpenClaw (Hermes version unknown). Write approval is a global on/off. Several 2026 CVEs in skills and code-exec (secondary). Open requests: #39250 (per-goal cost), #11701, #5528, #16462 | Our runtime and its weaknesses |
| NemoClaw + OpenShell | NVIDIA secure wrapper | Alpha, 0.0.116 vs 0.1.2 split. **OpenShell "Privacy Guard" (#1043) and streaming DLP (#2763) closed `not_planned` 2026-09-21.** OCSF audit is "best-effort". | Room exists for content-aware egress and provenance; NVIDIA won't fill it soon |
| nemoclaw-community recipes | NVIDIA reference apps | Memory-Driven Chief of Staff (email/Slack, obligation ledger), Ask NemoClaw Chrome side panel, Sandboxed Hermes Bot Team, Payment Ops (human release), PR Review Advisor | **Do not rebuild these**; cite or extend |
| NanoClaw / ZeroClaw / nanobot / IronClaw | OSS OpenClaw alternatives | 30.9k / 32.9k / 48.7k / 12.6k stars; container per chat, Rust, "AI never sees your passwords" | Lighter or safer claws; already crowded |
| AnythingLLM, Jan, LibreChat, Mem0, n8n | Components and chat apps | Active (AnythingLLM has memories and cron; Mem0 claims LongMemEval 94.4) | Building blocks, not secure always-on agents |
| Khoj, Reor, Leon, Open Interpreter, Letta | Older second brains | Stalled, archived or pivoted | "Chat with your notes" is dated |
| Meta Muse (Sep 8) | Commercial, cloud VM | Sentinel approval agent plus a claimed full audit trail; US only | **Already markets "approval + audit"**, so our version must be *verifiable and local*, not just claimed |
| xAI Grok Bot (Aug 11) | Commercial, cloud computer | Approval rules for send, delete and buy; bots share one machine and its credentials | Shows that per-agent isolation is a real gap |
| Claude Cowork | Commercial, local VM | Unified memory (Aug 25); PromptArmor exfiltration; reported "ShareRoot" Mac escape (Jul) | Precedent for sandbox failures |
| ChatGPT Pulse plus "Dreaming", Google CC (household, Sep 17), Gemini Personal Intelligence, Siri on iOS 27, Lindy, Notion agents, Superhuman Go | Commercial assistants | Briefings, inbox, curated memory | **They do briefings and triage better than we can in 15 days** |

**Gaps a 2-person team could own** (from the landscape report; each needs deterministic enforcement, not just an LLM judge):

1. **Taint-aware least privilege ("trifecta breaker").** Once untrusted content (email body, web page, vCard, shared file) enters a session, hot-swap the OpenShell network policy to a locked tier: no new hosts, no sends, no memory or skill writes. Restore it only on approval. Demo: a hidden-injection email is blocked live, with the OCSF DENIED line on screen. Nothing in Hermes or NemoClaw does session-level information-flow control today.
2. **Provenance-gated memory and skill firewall.** A Hermes memory provider plus skill-write reviewer that tags every write with its origin (user words, tool output, tainted session). Auto-approve user-originated writes; quarantine the rest with a diff UI and rollback. Evidence: MPBench, SkillJack (80% persistence after deletion), and the binary `write_approval` switch.
3. **Content-aware egress DLP / "what left my machine" ledger.** Redact PII and secrets before prompts reach Token Factory, optionally with local Nano 4B or regex+NER. Fills the gap left by the closed Privacy Guard. OpenShell 0.1.x supervisor middleware can inspect and redact bodies (openshell report; the API is evolving, and it is unavailable or unverified on NemoClaw's 0.0.116).
4. **Plain-language action receipts with undo.** Join the Hermes tool log, OCSF events and connector side effects into an append-only timeline. Classify actions as reversible or not, pin "confirm irreversible" so compaction cannot drop it, and offer compensating actions.
5. **Cost and locality governor.** Per-goal token attribution and budgets: loops forced onto Lightning, escalation to Super only within budget and only for non-sensitive data, plus a kill switch. This directly scores "effective use of Token Factory + Nemotron".

Gaps 1, 2 and 4 combine into a single **"trust layer for a personal agent"**, with 5 as the Nebius/Nemotron showcase. **Be careful:** Muse already sells "approval + audit trail". The pitch must be *open, deterministic, user-owned and verifiable* (show the policy diff and the prover output), not a feature list.

**Clichés to avoid as the headline:** morning briefing to Telegram (weather, calendar, news); inbox triage or digest (a Hermes Gurugram meetup on 2026-10-04 builds exactly this); chat-with-your-notes RAG; Telegram calendar bot; multi-agent "teams"; email/Slack chief of staff (NVIDIA recipe exists); generic "chatbot with memory"; trading or DeFi agents. These can appear *as the workload* the trust layer protects, never as the pitch.

---

## 6. Top 10 risks and unknowns (ranked by likelihood of killing a 15-day build)

1. **The Nebius gate wired through the sandbox fails or is flaky.** NemoClaw can reject the DNS-backed Token Factory URL at onboarding. The `inference set` adapter has a 30s total cap, which Nemotron reasoning turns can exceed. Hermes-in-NemoClaw may not accept it at all (unverified). **Mitigation:** spikes S1 and S2 on day 1; prefer Hermes's native `nebius-token-factory` provider (B2 or C); keep a direct Token Factory call visible in the video.
2. **Version churn and stale docs.** NemoClaw lkg v0.0.124 vs docs at v0.0.130; the OpenShell 0.0.116 vs 0.1.2 API split with a migration epic opened Oct 1; Hermes's red E2E matrix. Most blogs and tutorials, including NVIDIA's March blog and the Hermes+NemoClaw blog pinned to OpenShell v0.0.38, are stale. **Mitigation:** pin `NEMOCLAW_INSTALL_TAG`, `OPENSHELL_VERSION=v0.1.2` and `install.sh --commit`; one track per machine; record versions in the README.
3. **Always-on demo availability through Dec 15.** Laptops sleep. NemoClaw reboot recovery is manual. The OpenShell main process does not auto-restart. Serverless is Preview with no SLA and deletes the disk on stop. Hosting is out of pocket (~$100-200) and needs a card. **Mitigation:** Nebius Compute VM with a scripted `recover.sh`, a systemd unit, a health-check cron, state on a persistent volume, and a recorded fallback demo.
4. **Nemotron behavior in agent loops.** Reasoning-only `reasoning_content` (#3279 pattern), empty content with many tools (#1193 pattern), minutes-long Super turns (Hermes 600s floor), unknown `chat_template_kwargs` pass-through on Nebius, and Lightning not yet validated anywhere. **Mitigation:** S1 bake-off, `enable_thinking=false` on the fast path, explicit fallbacks, trimmed tool lists.
5. **Functionality rule: a clean, reproducible install on the declared platform.** Open macOS bugs (#12367, #11984, #12501), Docker Desktop host-networking requirements, and API keys judges may not have. **Mitigation:** declare "Linux (Ubuntu 24.04) + Docker" as the platform with a hosted demo URL; ship `setup.sh` and test it from scratch on a fresh VM twice.
6. **Differentiation and judging.** 15.7k registrants, already-public in-track repos and NVIDIA recipes. Design is 25% and wants a coherent product, not plumbing. **Mitigation:** commit to the trust-layer angle by day 3; spend at least 4 pd on UX (receipts timeline, approval UI) and the video script.
7. **Integration and egress friction.** Deny-by-default holds unlisted hosts until approved. Managed MCP is HTTPS-bearer only (no stdio, no OAuth). Slack and Mattermost break inside the proxy. Hermes strips placeholder secrets from skill subprocesses (#4429). OpenClaw cron needs `operator.admin` approval. Gmail OAuth Testing-mode refresh tokens **expire after 7 days**. **Mitigation:** limit to 2-3 integrations (Telegram plus one Google or IMAP account plus Tavily); pre-declare policies; re-consent OAuth before recording.
8. **The memory demo fails to show "remembers me".** Hermes memory is 2,200 + 1,375 chars, frozen per session, and needs `/new`. OpenClaw compaction drops context. **Mitigation:** script session boundaries in the video; lean on `session_search` and our own provenance store.
9. **Privacy claim credibility.** Token Factory retains I/O by default (**enable ZDR**). OpenShell telemetry is on by default (disabling it under NemoClaw is unverified). Hermes `web.keyless_fallback=true` sends queries to third-party free tiers. The Personal policy tier opens everything. Cloud inference is not "local". **Mitigation:** a privacy checklist in the README and video; state the limits honestly.
10. **Accounts, credits, model deprecation and ToS.** Card-mandatory sign-ups (Indian card e-mandate unverified; a failed charge suspends the account). Credits are about $51 per account. A Nemotron ID could be retired before Dec judging with no rerouting. The WhatsApp Baileys bridge risks the third-party terms rule. **Mitigation:** sign up on day 1, keep model IDs in config with a fallback, use Telegram Bot API only, submit by Oct 28-29.

**Other unknowns to close in week 1:**

- Per-member credit stacking.
- Whether judges supply keys.
- `host.openshell.internal` behavior on macOS.
- Privileged-mode support on Serverless Endpoints.
- Actual Token Factory account rate limits.
- Whether NemoClaw moves `lkg` or OpenShell to 0.1.x before Oct 30.

---

## 7. Sources (key URLs)

**Hackathon**
- https://nebiusglobalaihackathon.devpost.com/
- https://nebiusglobalaihackathon.devpost.com/rules
- https://nebiusglobalaihackathon.devpost.com/resources
- https://nebiusglobalaihackathon.devpost.com/updates/46204-here-s-how-judging-works
- https://nebiusglobalaihackathon.devpost.com/updates/46205-how-to-build-a-winning-project
- https://nebiusglobalaihackathon.devpost.com/updates/46203-kickoff-tips
- https://dev.nebius.com/builders

**NemoClaw**
- https://github.com/NVIDIA/NemoClaw (README, `nemoclaw-blueprint/blueprint.yaml`, `package.json`)
- https://github.com/NVIDIA/NemoClaw/blob/main/docs/reference/platform-support.mdx
- https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html and `.../quickstart-hermes.html`, `.../prerequisites.html`
- `docs/inference/custom-endpoint-security.mdx` (30s Pin adapter), `docs/reference/troubleshooting.mdx` (DNS-backed HTTPS), `docs/inference/set-up-openai-compatible-endpoint.mdx`, `docs/reference/network-policies.mdx`, `docs/deployment/deploy-to-headless-server.mdx`
- Issues #12558, #12367, #11984, #12501, #3136, #3279, #1193
- https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-NemoClaw-for-the-OpenClaw-Community/default.aspx
- https://cyber.gc.ca/en/alerts-advisories/nvidia-security-advisory-av26-849 ; https://nvidia.custhelp.com/app/answers/detail/a_id/5872
- https://github.com/NVIDIA/nemoclaw-community/tree/main/examples/recipes/nvidia

**OpenShell**
- https://github.com/NVIDIA/OpenShell (releases, `examples/bring-your-own-container/README.md`, `providers/`)
- https://docs.nvidia.com/openshell/about/support-matrix.md ; `.../upgrade/0-1-0.md` ; `.../how-it-works/inference.md` ; `.../how-it-works/policies/schema.md` ; `.../how-it-works/policies/advisor.md` ; `.../how-it-works/policies/prover.md` ; `.../observability/accessing-logs.md` ; `.../extensibility/supervisor-middleware.md` ; `.../observability/telemetry.md`
- https://docs.nvidia.com/openshell/v0.0.116/ (the docs version NemoClaw uses)
- Issues #3955, #3895, #3995, #3308, #1043, #2763

**Hermes Agent**
- https://github.com/NousResearch/hermes-agent (releases, SECURITY.md, Dockerfile, `plugins/model-providers/nebius-token-factory/__init__.py`, `plugins/model-providers/nvidia/__init__.py`, `agent/model_metadata.py`, `agent/reasoning_timeouts.py`)
- https://hermes-agent.nousresearch.com/docs/getting-started/installation ; `.../docs/integrations/providers` ; `.../docs/user-guide/features/memory` ; `.../features/skills` ; `.../features/cron` ; `.../user-guide/messaging/`
- Issues #4429, #90601, #70116, #90623, #123997, #128399, #126883
- https://developer.nvidia.com/blog/deploy-self-evolving-agents-for-faster-more-secure-research-with-a-hermes-agent-and-nvidia-nemoclaw/

**Nebius**
- https://docs.tokenfactory.nebius.com/quickstart ; https://tokenfactory.nebius.com/api/public/models_info ; https://api.tokenfactory.nebius.com/openapi.json
- https://docs.tokenfactory.nebius.com/legal/legal-quick-guide (ZDR, regional URL warning)
- https://docs.tokenfactory.nebius.com/ai-models-inference/rate-limits ; https://docs.tokenfactory.nebius.com/august-2026-deprecation-notice
- https://docs.nebius.com/serverless/overview ; `.../serverless/endpoints/manage` ; `.../serverless/jobs/manage` ; https://docs.nebius.com/legal/specific-terms/serverless-ai ; https://docs.nebius.com/compute/resources/pricing
- https://github.com/nebius/serverless-ai-cookbook (OpenClaw recipe is stale)

**Models**
- https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 ; https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8 ; https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF
- https://integrate.api.nvidia.com/v1/models (live ID list)
- https://developer.nvidia.com/blog/nvidia-nemotron-3-5-lightning-delivers-fast-accurate-specialized-task-execution-for-long-running-agents/
- https://ollama.com/library/nemotron-3-nano/tags
- https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-nemotron-open-model-license/ ; https://openmdw.ai/license/1-1/

**Landscape and security**
- https://arxiv.org/abs/2606.04329 (MPBench) ; https://arxiv.org/abs/2608.03509 (SkillJack)
- https://labs.cloudsecurityalliance.org/research/csa-research-note-openclaw-indirect-prompt-injection/
- https://thehackernews.com/2026/06/new-attacks-trick-openclaw-ai-agent.html ; https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html
- https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
- https://www.xda-developers.com/ran-nvidia-nemoclaw-openclaw-finally-safe-same-problems/
- https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification