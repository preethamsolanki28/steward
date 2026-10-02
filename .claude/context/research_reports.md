

# REPORT: Hackathon identification: Nebius x NVIDIA Global AI Hackathon (Devpost), Personal AI track

## Summary
Found it. The problem statement is the Personal AI Track of the "Nebius x NVIDIA Global AI Hackathon", hosted on Devpost at https://nebiusglobalaihackathon.devpost.com/. The sponsor is Nebius B.V., Devpost administers it, NVIDIA co-organizes, and Tavily is a bonus-prize partner. Submissions opened Aug 26, 2026 at 9:00 am PT and close Fri Oct 30, 2026 at 10:00 am PT. That is PDT (UTC-7), so 17:00 UTC or 22:30 IST. Today is Oct 2, so 28 days remain, which is more than the planned 10-15 day build. Judging runs Dec 1-15, 2026 and winners are announced around Jan 11, 2027. There are four tracks with names only and no PS IDs: Coding and Agentic Engineering, Best Apps and Agents, Personal AI, and Physical AI. The hard technical gate is that the project must run on Nebius Token Factory or Nebius AI Cloud. The rules define this as a runtime call to the Token Factory inference API, or deployment on Serverless Jobs, Serverless Endpoints or DevPods. It must also use at least one NVIDIA open model (Nemotron 3 Ultra/Super/Nano, GR00T, Cosmos or Sonic). NemoClaw, OpenShell, Hermes Agent and Nebius Serverless are only suggested ("tools such as"), not required, so a purely local model on the Mac would fail Stage One. Judging has two stages. Stage One is pass/fail: does the project fit the theme and apply the required APIs. Stage Two scores four equally weighted criteria (Technological Implementation, Design, Potential Impact, Quality of the Idea), reportedly on a 1-5 scale, with ties broken in that order. The judging update spells out the Personal AI bar: "a chatbot with a system prompt is fine" versus "an assistant that remembers context across sessions and takes real action on your behalf". The submission needs: a demo/hosted-app/test-build URL, a text description, a public GitHub/GitLab/Bitbucket repo with a visible Apache-2.0/MIT/MPL-2.0 license and a README with setup steps, a public YouTube video under 3 minutes, the track selection, and mandatory, specific feedback on Nebius and NVIDIA tools. The project must stay free to test until Dec 15, 2026. Prizes: $20k, $10k and $6k overall, a Jetson Orin Nano per track (the Personal AI track prize is hardware only), $3k for Best Use of Tavily, 20 city awards of $500, and 10 feedback awards of $100. A project can win one Overall award, or one Track plus one Bonus award. Credits: $25 of Token Factory credit with code NEBIUS-DEVPOST-GLOBAL26, plus another $25 Token Factory and $25 Tavily via the free Nebius Builders Program, and a Tavily code BBDEVPOST. No NVIDIA-specific credits were found. Competition is heavy: 15,706 registrants, and several Personal AI repos (Nemotron on Token Factory) are already public on GitHub.

## Platform requirements
Gate requirement for every submission: (a) a runtime call to the Nebius Token Factory inference API, or deployment on Nebius AI Cloud (Serverless Endpoints, Serverless Jobs, or DevPods); and (b) at least one NVIDIA open model (Nemotron 3 Nano/Super/Ultra, GR00T, Cosmos, Sonic).

A Mac-local-only model (e.g., an MLX or Ollama Nemotron) does NOT satisfy the "runs on Nebius" rule on its own. The Nemotron call must reach Token Factory or a Nebius-hosted endpoint at runtime.

Platform declaration: the submission must state the intended platform, and the Functionality rule requires it to "install and run consistently" there and behave as shown in the video. Declare only what you test, e.g., "macOS 14+ on Apple Silicon (client) + Nebius Token Factory (inference)", or "Linux/Docker" if NemoClaw/OpenShell needs it.

Deliverables:
- Public repo with an Apache-2.0/MIT/MPL-2.0 LICENSE visible at the repo top, and a README with setup steps that calls out the Nemotron model ID and the Nebius services used.
- Public YouTube video under 3 minutes showing the project running on the target device.
- A demo URL, hosted app, or "test build" (a downloadable or installable build likely qualifies for a local app).
- A text description, the track ("Personal AI"), and specific written feedback on Token Factory, AI Cloud and the NVIDIA tools.

Judges must be able to test free of charge until Dec 15, 2026 12:00 pm PT. Include credentials or test accounts if anything is gated.

Deadline: Oct 30, 2026 10:00 am PDT (17:00 UTC / 22:30 IST). No edits after that.

## Integration notes
For the Personal AI track, the hackathon names NVIDIA NemoClaw, OpenShell, Hermes Agent and Nebius Serverless as suggested tools ("use tools such as"), not hard requirements. Stage One only checks theme fit plus "required APIs/SDKs", which means Nebius Token Factory/AI Cloud plus an NVIDIA open model.

The scoring criteria explicitly reward how effectively the build uses Token Factory or AI Cloud models and Nemotron (Technological Implementation), and a creative, non-obvious use of them (Quality of Idea). Using NemoClaw, OpenShell or Hermes is a theme-fit and story bonus, not a scored line item. Judges include Nebius's Serverless AI PM, so a real Serverless Endpoint or Job is likely noticed.

Natural fit for a 2-person, 10-15 day build:
- Hermes Agent supplies persistent memory and self-written skills. The organizers linked its install guide: https://hermes-agent.nousresearch.com/docs/getting-started/installation.
- Point Hermes at Nemotron on Token Factory (OpenAI-compatible API).
- Wrap it in NemoClaw/OpenShell for sandboxing and egress policy (NVIDIA ships a "NemoClaw for Hermes Agent" blueprint: https://build.nvidia.com/nvidia/nemoclaw-for-hermes-agent).
- Optionally run background or scheduled tasks as a Nebius Serverless Job, or serve a dedicated Nemotron endpoint for a fixed region.

Privacy story: enable Token Factory Zero Data Retention (account profile page, org-wide) and say so in the video and README. Content is never used for training. A dedicated endpoint pins the region.

Tavily: a functional runtime Tavily API call makes the project eligible for the $3k Best Use of Tavily bonus, stackable with the Track award (Tavily promo code BBDEVPOST; $25 more via the Builders Program).

Credits:
- $25 Token Factory via code NEBIUS-DEVPOST-GLOBAL26 at https://nebius.com/promo-code?utm_promo_event_code=2026-devpost-global-ai-hack&utm_promo_code_type=Token_Factory&utm_promo_activation_code=NEBIUS-DEVPOST-GLOBAL26
- $25 more via https://dev.nebius.com/builders
- Each team member can likely claim their own; unverified.

Exact Nemotron model IDs on Token Factory, plus NemoClaw/OpenShell macOS support, were not verified in this research and need checking separately.

## Risks
- Hard gate: if the Nemotron call does not go through Nebius Token Factory or Nebius AI Cloud at runtime (e.g., only a local MLX or Ollama Nemotron on the Mac), the project fails Stage One pass/fail. Make the Token Factory call the default path and show it on screen in the video.
- Privacy-theme tension: 'data under your control' versus cloud inference. Enable Token Factory Zero Data Retention (default retains I/O for speculative decoding), keep memory and data stores local or encrypted, and explain this clearly. Otherwise Potential Impact and Quality of Idea suffer.
- Functionality rule: the project must install and run consistently on the declared platform. If NemoClaw/OpenShell need Linux or Docker, or are flaky on macOS Apple Silicon, the declared platform and README must match what judges can actually reproduce. Test a clean install on a second machine.
- Judges must be able to test free of charge until Dec 15, 2026, about 6 weeks after submission. Hosted demos or Serverless endpoints must stay up and funded beyond the $25+$25 credits. Prefer a local install with a Token Factory key the judge supplies, or budget for hosting. Whether judges must supply their own key is unclear.
- Competition is heavy: 15,706 registrants, and multiple Personal AI repos using Nemotron on Token Factory plus memory, skills or voice are already public. A generic 'chatbot with memory' will not stand out. Judges explicitly want cross-session memory plus real actions on the user's behalf.
- The Personal AI track prize is only a Jetson Orin Nano. Cash comes only from the overall top 3 ($20k/$10k/$6k) or bonuses (Tavily $3k, feedback $100). A project can win one Overall award, or one Track plus one Bonus award.
- Third-party integrations (Gmail, Calendar, Slack, GitHub, etc.) must be used within their ToS. Use official OAuth/APIs and your own test accounts, and avoid scraping or credential sharing. Also avoid unlicensed trademarks or copyrighted material in the video.
- Required paperwork is easy to miss and could disqualify the entry or cost points: an OSI license detectable at the repo top, a README with setup steps and an explicit Nemotron/Nebius callout, a public YouTube video under 3 minutes with audio naming the Nebius and NVIDIA tools, the track selection, and mandatory specific feedback.
- No changes are allowed after Oct 30, 2026 10:00 am PT. Submit a day early to avoid Devpost and YouTube processing problems.
- If any existing code is reused, document the 'significant updates' made after Aug 26, 2026. Keep the git history showing new work within the period.
- Eligibility check: the rules exclude residents of Brazil, Quebec, Russia, Crimea, Cuba, Iran, North Korea and other sanctioned places. India (likely team location) is not listed as excluded, and no Indian city is eligible for the $500 City Winner awards. Tax form W-8BEN is required for non-US winners.

## Unknowns
- There are no official problem-statement IDs (PS IDs) on Devpost. Tracks are identified only by name ('Personal AI Track'). If the team saw a PS ID elsewhere (e.g., a regional mirror or college listing), it was not found. Confidence that no ID exists on the official page: medium-high.
- The exact Devpost submission form fields (e.g., a dedicated 'platform' field or a testing-instructions field) are not visible without logging in and starting a submission.
- Whether a local-only install (a GitHub release as the 'test build') fully satisfies the 'URL to working demo, hosted application, or test build' requirement for non-Physical-AI tracks. The wording suggests yes, but it is not confirmed (confidence: low-medium).
- Whether judges will bring their own Nebius API key or expect the team to provide a working key or hosted endpoint for testing through Dec 15, 2026.
- The 1-5 per-criterion scale comes from an organizer update post, not the Official Rules.
- Exact posting dates of the update posts. Devpost showed relative times ('7/21/23/28 days ago' as of 2026-10-02), so the dates given here are approximate.
- Whether using NemoClaw, OpenShell, Hermes Agent or Nebius Serverless earns explicit extra credit. It is not stated in the criteria; it only helps theme fit and Quality of Idea.
- Whether NVIDIA offers any hackathon-specific credits (build.nvidia.com, Brev). None were found.
- Whether each team member can claim the $25 promo and the Builders Program credits separately.
- Which Builders & Brews city events remain after Oct 2, 2026. The Luma listing did not show dates. This is irrelevant unless the team attends one of the 20 listed cities.
- Exact Nemotron model IDs and pricing available on Token Factory as of Oct 2026, and NemoClaw/OpenShell support for macOS Apple Silicon. Both are outside this topic's scope and should be verified by the other research threads.

## Facts
- The official name is "Nebius x NVIDIA Global AI Hackathon" with the tagline "Build the next frontier of AI on open infrastructure". It is hosted on Devpost. [high] (https://nebiusglobalaihackathon.devpost.com/)
- The Sponsor is Nebius B.V. (Schiphol Boulevard 165, 1118 BG Schiphol, NL). The Administrator is Devpost, Inc. NVIDIA co-organizes, and Tavily is a partner (bonus prize, judges). [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- The Submission Period runs from Wed Aug 26, 2026 9:00 am PT to Fri Oct 30, 2026 10:00 am PT. Devpost shows the deadline as 'Oct 30, 2026 @ 10:00am PDT' (= 1:00 pm EDT = 17:00 UTC = 22:30 IST). [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- The Judging Period runs Tue Dec 1, 2026 9:00 am PT to Tue Dec 15, 2026 12:00 pm PT. Winners will be announced on or around Mon Jan 11, 2027 at 12:00 pm PT. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- There are four tracks: Coding and Agentic Engineering; Best Apps and Agents; Personal AI; Physical AI. Devpost gives them no numeric problem-statement IDs and identifies tracks by name only. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- Personal AI track text: 'Build an always-on, private assistant that works for you while keeping your data under your control. Give it persistent memory, reusable skills, access to the tools and information you choose, and the ability to carry out tasks across your daily workflows. Use at least one NVIDIA open source model, and use tools such as NVIDIA NemoClaw, OpenShell, Hermes Agent, and Nebius Serverless...' [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- Mandatory for every track: a working software application that 'runs on either Nebius Token Factory or Nebius AI Cloud and uses at least one NVIDIA open source model'. 'Runs on' means a runtime call to the Token Factory inference API, or deployment using Nebius AI Cloud compute (Serverless Jobs, Serverless Endpoints, or DevPods). [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- The NVIDIA open models the hackathon names are Nemotron (Nemotron 3 Ultra, Super, Nano), GR00T, Cosmos, and Sonic. The rules say 'NVIDIA Nemotron or other NVIDIA open source models' without a strict definition. [high] (https://nebiusglobalaihackathon.devpost.com/updates/46203-kickoff-tips)
- Judging Stage One (pass/fail): the project must 'reasonably fit the theme' and 'reasonably apply the required APIs/SDKs'. A genuine attempt at the track's goal passes; 'a superficial rebrand' does not. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- Judging Stage Two uses four equally weighted criteria. (1) Technological Implementation: how well it is built and how effectively it uses Token Factory/AI Cloud models and NVIDIA Nemotron or other NVIDIA open models. (2) Design: a complete, coherent product experience, not just a technical proof of concept. (3) Potential Impact: a credible, specific case for solving a real problem for a real audience. (4) Quality of the Idea: a creative, non-obvious use of Nebius and NVIDIA open models. Ties are broken by the highest score on the first criterion listed, in order. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- Each criterion is scored 1-5, according to the organizer update. The Official Rules page itself does not state the scale. [medium] (https://nebiusglobalaihackathon.devpost.com/updates/46204-here-s-how-judging-works)
- Judges' guidance for Personal AI: 'a chatbot with a system prompt is fine' versus 'an assistant that remembers context across sessions and takes real action on your behalf'. 'Judges love to see tracks pushed further than the basics.' [high] (https://nebiusglobalaihackathon.devpost.com/updates/46204-here-s-how-judging-works)
- The Functionality rule: 'The Project must be capable of being successfully installed and running consistently on the platform for which it is intended and must function as depicted in the video' (and/or text description). The Platforms rule: it must run on the platform specified in the Submission Requirements. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- Submission requirements: (1) a project meeting the requirements; (2) a URL to a working demo, hosted application, or test build (Physical AI exempt); (3) a text description of features and functionality; (4) a public GitHub/GitLab/Bitbucket repo with all source, assets and instructions, an open source license (Apache 2.0, MIT, or MPL 2.0) 'detectable and visible at the top of the repository page', and a README with setup and run instructions that highlights NVIDIA model usage and the Nebius tools used; (5) a demo video under 3 minutes, publicly visible on YouTube, showing the project functioning on its target device; (6) the track; (7) feedback on Token Factory, AI Cloud and NVIDIA tools; (8) if the project pre-existed, an explanation of the significant updates. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- Testing access: 'The Entrant must make the Project available free of charge and without any restriction, for testing, evaluation and use by the Sponsor, Administrator and Judges until the Judging Period ends' (Dec 15, 2026 12:00 pm PT). A private site must include login credentials in the testing instructions. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- New & Existing rule: projects must be newly created, or, if they existed before Aug 26, 2026, 'significantly updated after the start of the Hackathon Submission Period'. Open source use is allowed if licenses are complied with and the entrant 'creates software that enhances and builds upon' the underlying open source product. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- Third Party Integrations: 'If a Project integrates any third-party SDK, APIs and/or data, Entrant must be authorized to use them in accordance with any terms and conditions or licensing requirements of the tool.' [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- No changes are allowed after the Submission Period ends, except removals the Sponsor permits (infringing content, PII, inappropriate material). Multiple submissions are allowed only if each is 'unique and substantially different'. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- Prizes: Grand $20,000; 2nd $10,000; 3rd $6,000; 4 Track awards of one NVIDIA Jetson Orin Nano each (incl. Personal AI); Best Use of Tavily $3,000 (requires a functional runtime Tavily API call); 20 City Winner awards of $500 (Builders & Brews IRL attendees only); 10 Most Valuable Feedback awards of $100 plus an NVIDIA swag pack. 'Each Project is eligible for one (1) Overall Award OR one (1) Track Award and one (1) Bonus Award.' [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- The City Winner cities are Tokyo, Da Nang, Seoul, Kuala Lumpur, Singapore, Taipei, Tel Aviv, London, Copenhagen, Stockholm, Warsaw, Amsterdam, Berlin, Paris, Mexico City, New York City, Toronto, Boston, San Francisco, and Los Angeles. No Indian city is listed. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- Credits: $25 of Nebius Token Factory credit via the form https://nebius.com/promo-code?utm_promo_event_code=2026-devpost-global-ai-hack&utm_promo_code_type=Token_Factory&utm_promo_activation_code=NEBIUS-DEVPOST-GLOBAL26 with activation code NEBIUS-DEVPOST-GLOBAL26. Another $25 of Token Factory credit comes from joining the free Nebius Builders Program (https://dev.nebius.com/builders). [high] (https://nebiusglobalaihackathon.devpost.com/resources)
- The Nebius Builders Program offers $25 Token Factory, $100 LangSmith, $50 Toloka, $50 Tandem and $25 Tavily credit, Nebius certification for $1, office hours and Discord. [medium] (https://dev.nebius.com/builders)
- A Tavily promo code BBDEVPOST was published for hackathon participants. The build-session post also links the Hermes Agent install guide (https://hermes-agent.nousresearch.com/docs/getting-started/installation), and the live session configured Hermes Desktop Agent locally against Token Factory models (MiniMax-M3, Kimi K2.7, which are not NVIDIA models). [medium] (https://nebiusglobalaihackathon.devpost.com/updates/46337-build-session-recording-resources-available-live-coding-your-first-app-with-nebius)
- No NVIDIA-specific credits (e.g., build.nvidia.com or Brev) are offered for this hackathon on the Devpost pages. [medium] (https://nebiusglobalaihackathon.devpost.com/resources)
- Organizer tips: name Nebius Token Factory/AI Cloud and the NVIDIA model in the description and the Built With field, and call them out 'with audio' in the video. Treat the video as a pitch (problem, working solution, impact). Keep API keys in env/.env, never in code. Feedback must be specific: what you used, what worked, what needs work, onboarding (zero to hello world), and whether you'd build again and why. [high] (https://nebiusglobalaihackathon.devpost.com/updates/46205-how-to-build-a-winning-project)
- 23 judges are listed, from NVIDIA, Nebius and Tavily. They include Mikhail Rozhkov (Technical Product Manager - Serverless AI, Nebius), Dylan Bristot (Founding PMM, Token Factory), Daniel Myers (Director of DevRel, Nebius), and several NVIDIA engineers. [high] (https://nebiusglobalaihackathon.devpost.com/)
- 15,706 participants were registered as of the fetch. The project gallery is not yet published. [high] (https://nebiusglobalaihackathon.devpost.com/)
- Eligibility: of legal age of majority. Residents of places where US or local law prohibits participation are excluded, 'including, but not limited to, Brazil, Quebec, Russia, Crimea, Cuba, Iran, and North Korea'. Teams name one Representative who allocates prizes. No team size limit is stated. Winners provide a W-9 or W-8BEN. [high] (https://nebiusglobalaihackathon.devpost.com/rules)
- The Devpost page suggests Nebius Serverless Endpoints for real-time inference and Serverless Jobs for background or asynchronous work, mainly in the Best Apps and Physical AI descriptions, as optional tools. [medium] (https://nebiusglobalaihackathon.devpost.com/)
- Token Factory privacy: by default, inputs and outputs are retained (for speculative decoding). Zero Data Retention can be enabled on the account profile page and applies org-wide. Content is never used for training in either mode. Public endpoints have dynamic processing location; dedicated endpoints have a fixed region. [high] (https://docs.tokenfactory.nebius.com/legal/legal-quick-guide)
- Several Personal AI track projects are already public on GitHub, e.g., Alvnvnc/mitra, fawad07/nebius-personal-ai, Akshat-Soni02/nxn-global-ai-hackathon-personal-agent, and ProttoyDip/talkback. Most use Nemotron on Token Factory plus memory, skills or voice. [medium] (https://github.com/Alvnvnc/mitra)


# REPORT: NVIDIA OpenShell: secure sandbox runtime for autonomous agents (policies, install, platforms, Hermes/custom-agent support, observability, maturity)

## Summary
OpenShell is NVIDIA's open-source runtime (Apache 2.0, Rust, repo created 2026-02-24) for running agents inside sandboxes. Policy is enforced outside the agent's process. Landlock handles the filesystem, seccomp plus an unprivileged non-root identity handles processes, and a trusted "supervisor" checks every TCP and DNS connection against a declarative YAML policy. That network check can inspect requests at the HTTP level (REST method/path, GraphQL, MCP tool names, JSON-RPC, WebSocket), not just hosts. Credentials never enter the sandbox. The agent sees opaque placeholders such as `openshell:resolve:env:NVIDIA_API_KEY`, and the supervisor swaps in the real key only for endpoints the provider profile allows. The current stable release is v0.1.2 (2026-09-28). v0.1.0 (2026-09-25) was a big breaking release: it removed the `inference.local` "privacy router" and the `openshell inference set` commands, removed built-in provider profiles and the community image catalog (`--from openclaw`, `--from ollama`), and stopped building Dockerfiles in `sandbox create`. Most blog posts, the March 2026 NVIDIA launch blog, and community projects such as HermesClaw describe the old 0.0.x model and are now stale. This split matters for the build. NemoClaw, the official way to run Hermes Agent inside OpenShell (`nemohermes onboard`), pins OpenShell to exactly 0.0.116 (min=max in its blueprint) and still routes models through `inference.local`. Standalone OpenShell 0.1.x does not document Hermes at all; it lists Claude Code, OpenCode, Codex and Copilot CLI and says any agent in an OCI image can run. Any custom Python agent (or a hand-built Hermes image) can still run on 0.1.2. The image needs a non-root USER, a writable /sandbox, the start command passed after `--` (the image ENTRYPOINT is replaced by the supervisor), a provider profile per model API (NVIDIA build or Nebius Token Factory), and a policy that names the real interpreter path, e.g. /usr/bin/python3.12. On macOS, only Apple Silicon is supported, through Homebrew plus Docker Desktop 28+ with host networking turned on and Enhanced Container Isolation off. Intel Macs are unsupported, the Mac has no GPU passthrough, and the MicroVM backend on macOS still needs manual fixes (open issue #3955). Local models must be reached on the host through `host.openshell.internal`, e.g. Ollama with a Nemotron model, or called in the cloud. The demo-friendly features are strong: live OCSF audit logs (`openshell logs --tail`) showing ALLOWED/DENIED with the matching policy name, the `openshell term` TUI dashboard, the policy advisor (the agent proposes a rule after a denial, a human approves it, and it hot-reloads without a restart), policy revisions and rollback, the `openshell-prover` formal boundary check, OCSF JSONL export and gateway OTLP traces. For a 15-day build, pick one track on Day 1 and pin it. (a) NemoClaw/nemohermes on OpenShell 0.0.116 means less plumbing and official Hermes support, but older docs and many open Hermes bugs. (b) Standalone OpenShell v0.1.2 with your own agent image means the current API and docs, but you must solve the Hermes packaging yourself. The two cannot share one gateway.

## Platform requirements
macOS (the team's laptop): Apple Silicon only, since Intel Macs are rejected by the installer. Homebrew is required. Docker Desktop must be 28.0+ with "host networking" enabled and Enhanced Container Isolation off. The installer sets up the CLI, openshell-prover and a gateway running as a brew service at https://localhost:17670.

On macOS the kernel features (Landlock ABI v3 / Linux 6.2+, seccomp user-notify) run inside the Docker Desktop Linux VM. The Mac has no NVIDIA GPU, so local models must run on the host and be reached at host.openshell.internal (e.g. Ollama), or be called in the cloud (NVIDIA build API, Nebius Token Factory, OpenRouter).

The MicroVM driver (Hypervisor.framework) exists but is rough on macOS v0.1.2 (#3955). Use the Docker driver.

Linux: Debian/Ubuntu on amd64 or arm64, with a kernel at 6.2+ (Landlock ABI v3) and 5.19+ recommended. Packages are Debian/RPM (glibc 2.28+) or snap. The gateway runs as a systemd user service. Podman 5.x with cgroups v2 is an alternative runtime. GPU sandboxes need an NVIDIA driver plus Docker CDI (nvidia-container-toolkit).

Windows WSL2 is experimental and has open bugs (#3880, #3842).

Workload images must be standard Linux OCI images (not distroless or scratch), run as a non-root USER, have a writable /sandbox, include iproute2, and receive the start command after `--`.

The Python SDK needs Python 3.11+.

Version pin: standalone OpenShell is v0.1.2. NemoClaw/nemohermes requires exactly OpenShell 0.0.116, so pick one track per machine.

## Integration notes
TRACK A: Hermes through NemoClaw (official, but pinned to OpenShell 0.0.116)
- Install: `export NEMOCLAW_AGENT=hermes; curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash`, or `nemohermes onboard`.
- Daily commands: `nemohermes my-hermes status`, `nemohermes my-hermes dashboard-url --quiet`, `nemohermes launch my-hermes`, `nemohermes my-hermes connect`.
- NemoClaw installs or verifies the pinned OpenShell Homebrew formula itself.
- Model traffic goes through `inference.local`, configured with `openshell inference set --provider <p> --model nvidia/nemotron-3-nano-30b-a3b` or via `nemohermes inference set`. NemoClaw docs list Ollama models such as `nemotron-3-nano:30b`.
- Use the v0.0.116 OpenShell docs (https://docs.nvidia.com/openshell/v0.0.116/), not /latest, because the policy schema and CLI differ.

TRACK B: standalone OpenShell v0.1.2 with your own agent (custom Python agent or hand-packaged Hermes)
1) Install: `curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | OPENSHELL_VERSION=v0.1.2 sh`, then `openshell status`.
2) Image: base it on python:3.12-slim or ubuntu:24.04, add iproute2, ca-certificates and git, create a non-root user, run `install -d -o agent -g agent /sandbox`, set `USER agent` and `HERMES_HOME=/sandbox/.hermes` so memory and skills live in the persistent workspace, then `docker build -t hermes-os:local .`. Do not reuse the official Hermes image as-is: it ends as root and expects the s6 /init entrypoint.
3) Provider profile for Nemotron. Copy https://raw.githubusercontent.com/NVIDIA/OpenShell/main/providers/nvidia.yaml and give it a new id plus `binaries: [/usr/local/bin/python3.12, /sandbox/.venv/**]` (use the real interpreter path from `readlink -f`). For Nebius, use the same shape:
```
id: nebius-tf
category: inference
inference_capable: true
credentials:
  - name: api_key
    env_vars: [NEBIUS_API_KEY]
    required: true
    auth_style: bearer
    header_name: authorization
discovery:
  credentials: [api_key]
endpoints:
  - host: api.tokenfactory.nebius.com
    port: 443
    protocol: rest
    access: read-write
    enforcement: enforce
binaries: [/usr/local/bin/python3.12]
```
Then run `openshell profile lint -f nebius.yaml && openshell profile import -f nebius.yaml` and `NEBIUS_API_KEY=... openshell provider create --name nebius --type nebius-tf --from-existing`.
4) Local model on the Mac host. Use a credentialless profile with `host: host.openshell.internal, port: 11434, protocol: rest, access: read-write`, and start the sandbox with `--env OPENAI_BASE_URL=http://host.openshell.internal:11434/v1`. Ollama may need OLLAMA_HOST=0.0.0.0; test this on Day 1.
5) policy.yaml (version: 1) contents:
- `filesystem_policy`: read_only [/usr, /lib, /etc], read_write [/sandbox, /tmp].
- `network_policies` per tool, e.g. Telegram `api.telegram.org:443` for the python binary.
- An MCP endpoint with `protocol: mcp` and rules that allow initialize, notifications/initialized and tools/call for chosen tools, plus a deny rule for `tool: send_email`.
- GitHub read-only via `access: read-only`.
6) Run: `openshell sandbox create --name hermes --from hermes-os:local --provider nebius --policy policy.yaml --detach -- hermes gateway`. The exact Hermes subcommand is unverified. Use `--expose <port>` or `openshell forward start <port> hermes -d` for a local UI or API. Remember `--upload` cannot be combined with a trailing command.
7) Set the env var HERMES_ENVIRONMENT_HINT="Running inside an OpenShell sandbox." Be aware that Hermes strips placeholder secrets from skill subprocesses (#4429). Keep API calls in the main Hermes process, or bind the credential through a provider endpoint the main process uses.

Demo commands (both tracks, syntax shown is 0.1.x)
- `openshell term` for the live dashboard.
- `openshell logs hermes --tail` to show OCSF ALLOWED/DENIED lines naming the policy.
- `openshell settings set --global --key agent_policy_proposals_enabled --value true --yes`, then `openshell rule get hermes --status pending` and `openshell rule approve hermes --chunk-id <id>` to show the agent asking for access and a human approving it, with hot reload.
- `openshell policy list hermes`, then `openshell policy get hermes --rev N` to show the audit trail and rollback.
- `openshell-prover check candidate.yaml --boundary boundary.yaml` for formal verification.
- `openshell settings set hermes --key ocsf_json_enabled --value true` for JSONL (may not appear on Docker Desktop, #3895).
- `[openshell.gateway.otlp]` in gateway.toml for OpenTelemetry traces.
- Set OPENSHELL_TELEMETRY_ENABLED=false for the privacy story.

Nebius Serverless: OpenShell runs only on a Docker/Podman/K8s/VM gateway host. A cloud deployment would mean a Linux VM or Kubernetes, e.g. on Nebius, running the gateway (Helm chart oci://ghcr.io/nvidia/openshell/helm-chart). Calling Nebius serverless or Token Factory endpoints from the sandbox is just a provider profile, as above.

Dev aid: the OpenShell docs MCP server is at https://docs.nvidia.com/openshell/_mcp/server, and agent skills install with `npx skills add NVIDIA/OpenShell`.

## Risks
- Version split: NemoClaw/nemohermes requires exactly OpenShell 0.0.116 (with `inference.local` and `openshell inference set`). The default installer gives 0.1.2, where those were removed. Installing the wrong one, or following mixed tutorials, can cost days. Choose a track on Day 1 and pin it (OPENSHELL_VERSION=v0.1.2, or let the NemoClaw installer manage 0.0.116).
- Most third-party material is stale after the 2026-09-25 v0.1.0 breaking release. That includes the NVIDIA launch blog, HermesClaw, and 'uv tool install openshell'. Stale advice includes the privacy router, `--from openclaw/ollama/base`, OpenShell-Community images, Dockerfile builds in `sandbox create`, and `tls: terminate`.
- Weekly stable releases with active breaking-change churn (526 open issues/PRs). An upgrade mid-build may force sandbox recreation (0.0.x to 0.1.0 had no in-place upgrade). Freeze versions for the demo and the judges' install instructions.
- Hermes on standalone 0.1.x is undocumented and untested by NVIDIA. The official Hermes image (root + s6 /init) does not fit OpenShell's non-root, entrypoint-replaced model, so a custom image is needed. Hermes strips placeholder credentials from skill subprocesses (#4429). NemoClaw itself has many open Hermes bugs (rebuild, credential refresh, SOUL.md/skills dropped in #12360).
- macOS specifics: Docker Desktop needs host networking on and ECI off. Whether host.openshell.internal reaches the Mac's loopback services is unverified. The MicroVM driver needs manual repair (#3955). Intel Macs are unsupported. There is no local NVIDIA GPU, so Nemotron must run via Ollama/Metal on the host or a cloud endpoint.
- The judges' 'installs and runs consistently' criterion: setup needs Homebrew, Docker Desktop configuration, a first image pull (nvcr.io/ghcr), imported provider profiles and API keys. Script all of it (Makefile or setup.sh) and test from scratch on a second machine.
- Binary matching must use real interpreter paths (python3 is a symlink to python3.12). Executables are hashed on first use, so pip-upgrading an interpreter or rebuilding the image mid-session can trigger denials. Easy to misdiagnose.
- Doc inconsistencies: `--upload` with a trailing command is rejected (#3995) although a tutorial uses it. An example README says 'export the built-in profile' although built-ins were removed. OCSF JSONL file is missing on Docker Desktop (#3895). Build the demo on `openshell logs` and `openshell term` rather than JSONL files.
- 'Always-on' gaps: runtimes do not auto-restart the sandbox main process. The gateway log buffer is lost on gateway restart. A sandbox stuck in Error after a supervisor disconnect (#3308) may need delete+recreate, so persist agent memory outside throwaway state (e.g. /sandbox with stop/start, or a labeled Docker volume).
- Supervisor middleware (e.g. a PII-redaction proxy to cloud LLMs) needs a custom gRPC service, and its API is still changing. The built-in openshell/regex only redacts `sk-`. Probably out of scope for 15 days.
- Telemetry is on by default; turn it off explicitly so the private-by-design claim holds.

## Unknowns
- Whether `host.openshell.internal` resolves to the macOS host (e.g. Ollama on 127.0.0.1:11434) with the Docker Desktop driver on v0.1.2, or whether Ollama must bind 0.0.0.0. Not documented for macOS; low confidence.
- Whether Hermes Agent (v2026.9.x) runs cleanly as a non-root main process in standalone OpenShell 0.1.2. Unverified: the exact install method inside a custom image (git clone + uv, or an installer script), the right long-running command (e.g. `hermes gateway`), and how its web, browser and messaging tools behave with seccomp-mediated DNS.
- When NemoClaw will move from OpenShell 0.0.116 to 0.1.x. No public date found; it could land mid-hackathon and change commands.
- Whether a sandbox and its main process come back automatically after a Mac reboot or Docker Desktop restart. Docs only say the sandbox returns to Ready after the supervisor reconnects, and that runtimes do not restart the main process.
- How to set OPENSHELL_TELEMETRY_ENABLED=false for the Homebrew brew-service gateway on macOS (plist env vs gateway.toml). Not documented.
- Whether OCSF JSONL export writes a file on macOS Docker Desktop with 0.1.2. Only the WSL2 failure (#3895) is reported.
- Exact Nebius Token Factory hostname and model IDs for the team's account (global vs region-specific endpoint). Confirm in the Nebius console.
- Whether hackathon judges will treat NemoClaw's pinned OpenShell 0.0.116 as acceptable 'use of OpenShell', or expect the latest version. The hackathon rules page was not checked here.
- Real resource overhead per sandbox on a laptop (two containers per sandbox: workload plus supervisor) and first-pull time for nvcr.io/ghcr images. Not measured.

## Facts
- OpenShell describes itself as 'the safe, private runtime for fleets of autonomous AI agents'. It runs agents in sandboxes with kernel-level isolation, uses declarative YAML policy, and formally verifies policy changes before they are applied. [high] (https://docs.nvidia.com/openshell/about/overview.md ; https://docs.nvidia.com/openshell/about/architecture.md)
- License is Apache-2.0. The repo NVIDIA/OpenShell was created 2026-02-24 and has about 14.1k stars, 1.6k forks and 526 open issues+PRs (GitHub API count). It is written in Rust. [high] (https://api.github.com/repos/NVIDIA/OpenShell ; https://docs.nvidia.com/openshell/resources/license.md)
- Latest stable release is v0.1.2 (2026-09-28). v0.1.1 shipped 2026-09-26, v0.1.0 on 2026-09-25, and the last 0.0.x was v0.0.116 on 2026-08-28. Stable releases target Tuesdays roughly every week. Security fixes cover the latest minor release and the one before it (N-1). Experimental interfaces can change in patch releases. [high] (https://github.com/NVIDIA/OpenShell/releases ; https://docs.nvidia.com/openshell/about/support-matrix.md)
- Install with: `curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh`, then check with `openshell status`. Pin a version with `... | OPENSHELL_VERSION=v0.1.2 sh`. The installer puts the CLI, the policy prover (`openshell-prover`) and a local gateway on the machine. [high] (https://docs.nvidia.com/openshell/about/installation.md ; https://github.com/NVIDIA/OpenShell/releases/tag/v0.1.2)
- On macOS, the installer uses Homebrew (required) and runs the gateway as a brew service at https://localhost:17670. The gateway config lives at ~/.config/openshell/gateway.toml or $(brew --prefix)/var/openshell/gateway.toml. Manage it with `brew services restart openshell`. Intel Macs are rejected because no x86_64-apple-darwin assets are published. [high] (https://docs.nvidia.com/openshell/about/installation.md ; https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh (lines ~20-25, 710, 717))
- Supported hosts are Linux Debian/Ubuntu (amd64 and arm64) and macOS Apple Silicon with Docker Desktop. Windows WSL2 with Docker Desktop is Experimental. Runtimes are Docker (Docker Desktop/Engine 28.0+), Podman 5.x (Linux, cgroups v2), MicroVM (Hypervisor.framework on macOS, KVM on Linux) and Kubernetes 1.29+ with Helm 3. [high] (https://docs.nvidia.com/openshell/about/support-matrix.md)
- The sandbox needs Landlock ABI v3 (Linux 6.2+) and specific seccomp user-notification features; Linux 5.19+ is recommended. On macOS these run inside the Docker Desktop Linux VM, not the host kernel. If these features are missing, launch fails closed. [high] (https://docs.nvidia.com/openshell/about/support-matrix.md)
- Docker Desktop must have host networking enabled and cannot use Enhanced Container Isolation. The supervisor container runs on the host network. Configure Docker CDI before starting the gateway if you need GPU sandboxes. [high] (https://docs.nvidia.com/openshell/how-it-works/sandboxes/runtimes.md ; https://docs.nvidia.com/openshell/how-it-works/gateways/configuration.md)
- No GPU is required. `--gpu` / `--gpu N` uses NVIDIA CDI devices (Docker/Podman) or nvidia.com/gpu (Kubernetes). The default workload image is nvcr.io/nvidia/base/ubuntu:24.04, which contains no agent CLIs. [high] (https://docs.nvidia.com/openshell/how-it-works/sandboxes/overview.md ; https://docs.nvidia.com/openshell/about/support-matrix.md)
- Architecture: the gateway is the control plane. Each sandbox has an untrusted workload side (the openshell-sandbox binary owns the agent process tree) and a trusted supervisor. The workload has networking turned off. Its only egress is an authenticated HTTP/2 channel to the supervisor, which checks policy, injects credentials, resolves DNS and opens upstream connections. If the supervisor disconnects, the agent is frozen. [high] (https://docs.nvidia.com/openshell/about/architecture.md)
- A policy is a YAML file (max 4 MiB, unknown fields rejected) with `version: 1` plus filesystem_policy (read_only/read_write/include_workdir; max 256 paths), landlock (compatibility: best_effort|hard_requirement), process (run_as_user/run_as_group; root rejected), network_policies, and network_middlewares. Filesystem, landlock and process settings are fixed at startup. Network rules and middleware hot-reload while the sandbox runs. [high] (https://docs.nvidia.com/openshell/how-it-works/policies/schema.md ; https://docs.nvidia.com/openshell/how-it-works/policies/overview.md)
- All egress is denied by default. Each network rule pairs endpoints (host/port/ports/path/allowed_ips) with binaries (the real executable path, not a symlink; for a Python script you list the interpreter, e.g. /usr/bin/python3.12). Child processes of a listed binary inherit the rule. Executables are hashed on first use and denied if the file changes. Loopback, link-local and 169.254.169.254 destinations are always blocked. [high] (https://docs.nvidia.com/openshell/how-it-works/policies/network-rules.md ; https://docs.nvidia.com/openshell/how-it-works/policies/schema.md)
- Request inspection: protocol rest|websocket|graphql|mcp|json-rpc|tcp. enforcement is audit (the default: log only) or enforce. Access presets are read-only/read-write/full. deny_rules override allow rules. MCP rules can allow or deny specific tool names, e.g. allow tools/call for [search_web] and deny `send_email`. Tool arguments are not inspected. [high] (https://docs.nvidia.com/openshell/how-it-works/policies/schema.md)
- Credentials: providers are created from imported provider profiles (YAML with credentials, endpoints, binaries). The sandbox only gets placeholders of the form `openshell:resolve:env:KEY`. The proxy replaces them with real values only at endpoints the profile authorizes. Plain `--env` values are visible to the agent, and the CLI warns about names that look like secrets. [high] (https://docs.nvidia.com/openshell/how-it-works/providers/overview.md ; https://docs.nvidia.com/openshell/how-it-works/inference.md ; https://docs.nvidia.com/openshell/how-it-works/sandboxes/overview.md)
- Inference routing in 0.1.x: there is no longer a managed router. v0.1.0 removed `openshell inference` commands, the route APIs and the `inference.local` endpoint. Instead you attach a provider per sandbox, and the agent calls the native endpoint (e.g. https://integrate.api.nvidia.com/v1) with the real model ID (example: nvidia/nemotron-3-super-120b-a12b). Any choice between local and cloud models must be made by the agent or app; OpenShell only enforces which endpoints are allowed. [high] (https://docs.nvidia.com/openshell/how-it-works/inference.md ; https://docs.nvidia.com/openshell/upgrade/0-1-0.md)
- In 0.0.116 (the version NemoClaw uses), `inference.local` was a privacy router. It stripped caller credentials, injected backend credentials, and served one provider and model per gateway. It was configured with `openshell inference set --provider nvidia-prod --model nvidia/nemotron-3-nano-30b-a3b` and supported OpenAI-compatible paths and Anthropic /v1/messages. [high] (https://docs.nvidia.com/openshell/v0.0.116/sandboxes/inference-routing.md)
- Host-local model servers (e.g. Ollama) are reached at `host.openshell.internal` (e.g. http://host.openshell.internal:11434/v1) through a custom credentialless profile. Do not use localhost or 127.0.0.1. [high] (https://docs.nvidia.com/openshell/how-it-works/inference.md)
- The 0.1.x docs list Claude Code, OpenCode, Codex and GitHub Copilot CLI as use cases and say OpenShell 'can run any agent that is available in a sandbox image'. The example provider profiles in the repo are anthropic, aws-bedrock, aws-s3, aws, claude-code, codex, copilot, cursor, deepinfra, github, google-cloud, google-vertex-ai, nvidia, oci-genai, openai, openrouter and pypi. There is no Hermes profile. [high] (https://docs.nvidia.com/openshell/about/overview.md ; https://docs.nvidia.com/openshell/about/run-your-first-agent.md ; https://github.com/NVIDIA/OpenShell/tree/main/providers)
- The v0.0.116 'Supported Agents' page lists Hermes Agent and OpenClaw as 'Blueprint-managed' through NemoClaw. The 0.1.x docs have no supported-agents page and do not mention Hermes. [high] (https://docs.nvidia.com/openshell/v0.0.116/about/supported-agents.md)
- NemoClaw pins OpenShell exactly: min_openshell_version and max_openshell_version are both "0.0.116" in nemoclaw-blueprint/blueprint.yaml, and its CI fails on any other version. NemoClaw's Hermes path still routes model traffic through `inference.local`. [high] (https://github.com/NVIDIA/NemoClaw/blob/main/nemoclaw-blueprint/blueprint.yaml ; https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/get-started/quickstart.md)
- Official Hermes-in-OpenShell path: `export NEMOCLAW_AGENT=hermes; curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash`, or `nemohermes onboard`. Then use `nemohermes my-hermes status`, `nemohermes my-hermes dashboard-url --quiet` or `nemohermes launch my-hermes`. NemoClaw rates Hermes 'Tested' but says 'production parity with OpenClaw is not yet asserted'. NemoClaw on macOS Apple Silicon (Colima or Docker Desktop) is 'Tested with limitations'. [high] (https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/get-started/quickstart.md ; https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/reference/platform-support.md)
- Hermes Agent's own SECURITY.md names NVIDIA OpenShell as a supported whole-process sandbox. It recommends the OpenShell Provider store for credentials and OpenShell network policy for egress. Hermes also reads a HERMES_ENVIRONMENT_HINT env var, e.g. 'Running inside an OpenShell sandbox.' [high] (https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md ; https://github.com/NousResearch/hermes-agent/blob/main/tests/agent/test_prompt_builder.py)
- Hermes strips env vars that look like secrets from tool subprocesses. OpenShell credential placeholders therefore never reach skill subprocesses (e.g. SLACK_BOT_TOKEN), and `env_passthrough` cannot override this. Open feature request #4429. [high] (https://github.com/NousResearch/hermes-agent/issues/4429)
- The official Hermes Docker image is not usable in OpenShell as-is. It ends as `USER root`, uses s6-overlay `/init` as PID 1 with usermod/groupmod, and puts state in /opt/data. OpenShell rejects root images unless the policy sets a non-root run_as_user, and it replaces the image ENTRYPOINT. A custom non-root image or policy override is needed. [medium] (https://github.com/NousResearch/hermes-agent/blob/main/Dockerfile ; https://github.com/NousResearch/hermes-agent/blob/main/docker-compose.yml ; https://docs.nvidia.com/openshell/how-it-works/policies/default-policy.md)
- Requirements for a custom image (BYOC): standard Linux base (not distroless or scratch), a non-root OCI USER, a /sandbox directory writable by that user, iproute2 installed, and the start command passed after `--`. Build it with the same engine as the gateway (`docker build -t my-agent:local .`) and run with `openshell sandbox create --from my-agent:local -- python /sandbox/app.py`. [high] (https://github.com/NVIDIA/OpenShell/blob/main/examples/bring-your-own-container/README.md ; https://docs.nvidia.com/openshell/how-it-works/sandboxes/overview.md)
- Core CLI: `openshell sandbox create --name X --from IMG --provider P --policy policy.yaml [--detach] [--cpu 2 --memory 4Gi] [--forward 8080|--expose 8080] -- cmd`; `sandbox connect/exec/upload/download/stop/start/delete/list/get`; `openshell policy get X --base|--full`; `policy set X --policy f.yaml --wait`; `policy update X --rule-name r --binary /usr/bin/curl --add-endpoint api.github.com:443:read-only:rest:enforce --wait`; `policy list X`; `policy get X --rev N`; `openshell profile lint|import -f p.yaml`; `openshell provider create --name n --type <profile-id> --from-existing`; `openshell sandbox provider attach X n --wait`. [high] (https://docs.nvidia.com/openshell/how-it-works/sandboxes/overview.md ; https://docs.nvidia.com/openshell/how-it-works/policies/manage-policies.md ; https://docs.nvidia.com/openshell/how-it-works/inference.md)
- Observability: `openshell logs X --tail [--source sandbox --level warn --since 5m]` streams OCSF v1.8.0 shorthand events such as 'NET:OPEN [MED] DENIED /usr/bin/curl(64) -> httpbin.org:443 [policy:- engine:opa] [reason:no matching policy]' and 'HTTP:POST [MED] DENIED ...', plus CONFIG:* events for policy changes. `openshell term` is a live TUI dashboard. The gateway's log buffer is in memory and lost when the gateway restarts. [high] (https://docs.nvidia.com/openshell/observability/accessing-logs.md ; https://docs.nvidia.com/openshell/observability/logging.md ; https://docs.nvidia.com/openshell/how-it-works/sandboxes/overview.md)
- OCSF JSONL export is turned on with `openshell settings set --global --key ocsf_json_enabled --value true` and writes /var/log/openshell-ocsf.YYYY-MM-DD.log (rotates daily, keeps 3 files). Open bug #3895: on Docker Desktop/WSL2 with 0.1.1 the file is never created, although events are emitted. The gateway can also export OpenTelemetry traces via `[openshell.gateway.otlp]`. [high] (https://docs.nvidia.com/openshell/observability/ocsf-json-export.md ; https://github.com/NVIDIA/OpenShell/issues/3895 ; https://docs.nvidia.com/openshell/how-it-works/gateways/configuration.md)
- Policy advisor (off by default; turn on with `openshell settings set --global --key agent_policy_proposals_enabled --value true --yes`): after a denial, the agent reads /etc/openshell/skills/policy_advisor.md and submits a narrow rule through http://policy.local. Review with `openshell rule get X --status pending`, then `openshell rule approve X --chunk-id ID` or `rule reject ... --reason`. Approved rules hot-reload. An auto mode exists (`--key proposal_approval_mode --value auto`). [high] (https://docs.nvidia.com/openshell/how-it-works/policies/advisor.md ; https://docs.nvidia.com/openshell/about/run-your-first-agent.md)
- Policy prover: `openshell-prover check candidate.yaml --boundary boundary.yaml` returns within_boundary (exit 0) or exceeds_boundary (exit 1, with a counterexample such as 'filesystem write /tmp'). It covers filesystem, L4 network, REST, process and landlock, and reports 'unsupported' for MCP and GraphQL rules. [high] (https://docs.nvidia.com/openshell/how-it-works/policies/prover.md)
- Supervisor middleware (`network_middlewares`) can inspect, redact or block HTTP bodies and WebSocket text using an external gRPC service. The built-in `openshell/regex` is demo-only and redacts only a fixed `sk-` pattern. The middleware API is still evolving. [high] (https://docs.nvidia.com/openshell/extensibility/supervisor-middleware.md ; https://docs.nvidia.com/openshell/extensibility/supervisor-middleware/configure.md)
- Anonymous telemetry is on by default. Disable it with OPENSHELL_TELEMETRY_ENABLED=false on the gateway, or compile it out with --no-default-features --features defaults-without-telemetry. [high] (https://docs.nvidia.com/openshell/observability/telemetry.md)
- The `openshell` PyPI package (0.1.2, Python >= 3.11) is the SDK only and does not install the CLI (`uv add openshell`; `from openshell import SandboxClient`). Older guides that say `uv tool install -U openshell` installs the CLI are stale. [high] (https://docs.nvidia.com/openshell/sdk/python.md ; https://pypi.org/pypi/openshell/json)
- NVIDIA/OpenShell-Community (the sandbox image catalog: base, ollama, pi, etc.) is retired. Bare names like `--from openclaw`, `--from ollama` and `--from base` are no longer expanded in 0.1.x. [high] (https://github.com/NVIDIA/OpenShell-Community ; https://docs.nvidia.com/openshell/upgrade/0-1-0.md)
- The NVIDIA launch blog (2026-03-16) shows `openshell sandbox create --remote spark --from openclaw` and describes a privacy router. Both are pre-0.1.0 behavior and are now stale. [high] (https://developer.nvidia.com/blog/run-autonomous-self-evolving-agents-more-safely-with-nvidia-openshell)
- Lifecycle: the sandbox main process is not restarted automatically by compute runtimes. `sandbox stop`/`start` keeps the persistent workspace, policies and provider attachments. `delete` purges everything. Docker named volumes can be mounted through `--driver-config-json` only after `allow_driver_config = true` and volume labels openshell.ai/sandbox-attachable=true. [high] (https://docs.nvidia.com/openshell/how-it-works/sandboxes/overview.md ; https://docs.nvidia.com/openshell/how-it-works/sandboxes/runtimes.md)
- The macOS MicroVM path is not yet smooth on v0.1.2. Issue #3955 reports the VM driver needed local signing, there were launch-auth config pitfalls, and leftover staging data after a failed create. Separate issues report a missing hypervisor entitlement (#3506) and no usable Landlock ABI in the packaged macOS ARM64 VM runtime (#3095). [high] (https://github.com/NVIDIA/OpenShell/issues/3955 ; https://github.com/NVIDIA/OpenShell/issues/3506 ; https://github.com/NVIDIA/OpenShell/issues/3095)
- The docs contradict themselves on uploads. The sandboxes page says `--upload` cannot be combined with a trailing main command, and issue #3995 confirms create rejects it. The Pi tutorial still shows `--upload .:/workspace -- pi`. Workaround: create the sandbox, `sandbox upload`, then `sandbox exec`, or bake the files into the image. [high] (https://docs.nvidia.com/openshell/how-it-works/sandboxes/overview.md ; https://github.com/NVIDIA/OpenShell/issues/3995 ; https://docs.nvidia.com/openshell/tutorials/run-pi-with-openrouter.md)
- The official Run Your First Agent example uses OpenRouter's free NVIDIA model: `openshell sandbox create --name my-agent --from ghcr.io/anomalyco/opencode:latest --provider openrouter -- opencode -m openrouter/nvidia/nemotron-3.5-lightning:free`. [medium] (https://docs.nvidia.com/openshell/about/run-your-first-agent.md)
- In 0.0.x, Hermes inside OpenShell hit an SSRF/DNS problem: getaddrinfo was blocked and all egress went through a proxy at 10.200.0.1:3128. Hermes issue #32217 is closed as completed (2026-07-24). In 0.1.x, DNS is mediated by seccomp and the supervisor, so the old proxy-env behavior may differ. [medium] (https://github.com/NousResearch/hermes-agent/issues/32217 ; https://docs.nvidia.com/openshell/about/architecture.md)
- Nebius Token Factory has an OpenAI-compatible base URL https://api.tokenfactory.nebius.com/v1/ (regional variant api.tokenfactory.us-central1.nebius.com) and serves nvidia/nemotron-3-super-120b-a12b. OpenShell would need a custom provider profile for this host. [medium] (https://docs.tokenfactory.nebius.com/api-reference ; https://nebius.com/services/token-factory/nemotron)


# REPORT: Nous Research Hermes Agent (open-source agent framework): features, install, providers (NVIDIA NIM / Nebius / local), Nemotron fit, OpenShell/NemoClaw integration, known issues. Researched 2026-10-02 against repo main @00373b5 (2026-10-01) and release v0.21.5 (tag v2026.9.24).

## Summary
Hermes Agent (github.com/NousResearch/hermes-agent) is an MIT-licensed Python agent framework. It is very active: about 250.7k stars, pushed on 2026-10-02, and the latest release is v0.21.5 (tag v2026.9.24, published 2026-09-24). Releases come out every few days and each one rolls up roughly 460 to 1,800 PRs, so plan to pin one version. It covers almost every requirement in the problem statement. Persistent memory uses two curated files, ~/.hermes/memories/MEMORY.md (2,200 chars) and USER.md (1,375 chars), plus a SQLite FTS5 history of every session (~/.hermes/state.db) that the agent can search with session_search. Skills are SKILL.md folders compatible with agentskills.io; the agent writes and patches them itself with the skill_manage tool after a background review, and a curator later marks unused ones stale and archives them. It also has MCP client support, a cron scheduler (cronjob_manage tool, natural-language schedules), subagents (delegate_task, 10 in parallel by default) and an OpenAI-compatible API server on port 8642. One gateway process handles Telegram, Discord, Slack, WhatsApp, Signal, Email and about 20 more platforms. Install on macOS (Apple Silicon is Tier 1) with `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`; it brings its own Python 3.14, Node and ripgrep. Linux and WSL2 are also Tier 1, and there is a native Windows installer and a Docker image. NVIDIA is a built-in provider: set `provider: nvidia` with NVIDIA_API_KEY, and the default base URL is https://integrate.api.nvidia.com/v1, which NVIDIA_BASE_URL can point at a local NIM instead. The docs' example model is nvidia/nemotron-3-super-120b-a12b, and the built-in catalog also lists nemotron-3-ultra-550b-a55b, nemotron-3.5-lightning-30b-a3b and nemotron-3-nano-omni-30b-a3b-reasoning. Nebius Token Factory is also built in (provider nebius-token-factory, NEBIUS_API_KEY). Its default auxiliary model is nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B. Ollama, vLLM, llama.cpp and LM Studio connect through `provider: custom` + `base_url`, but Hermes refuses any model whose context window is under 64,000 tokens. That rules out Ollama's default settings and small local setups. The NVIDIA integration is the strongest finding. NVIDIA's NemoClaw repo describes itself as 'Run agents like Hermes, LangChain Deep Agents, and OpenClaw more securely inside NVIDIA OpenShell'. It ships a first-class `nemohermes` CLI (one-line install with NEMOCLAW_AGENT=hermes) that puts Hermes in an OpenShell sandbox with managed inference. When you pick NVIDIA Endpoints the default model is Nemotron 3 Super, and NVIDIA published a Hermes+NemoClaw reference blog/example on 2026-06-02. Hermes' own SECURITY.md names NVIDIA OpenShell as one of the two supported ways to run the whole Hermes process inside a sandbox. OpenShell is not one of Hermes' terminal backends (those are local, docker, ssh, modal, daytona, vercel_sandbox and singularity); you run Hermes inside OpenShell, usually through NemoClaw. On macOS, NemoClaw is 'Tested with limitations' on Apple Silicon and needs Colima or Docker Desktop; Intel Macs are unsupported. NemoClaw's own platform table says production parity for Hermes is not yet asserted and its Hermes model-compatibility registry is empty. Main risks for a 15-day build:
- **Churn:** 14.4k open issues, macOS `hermes update`/launchd bugs, and the install/update E2E test matrix was red on 2026-09-29.
- **Memory demo:** memory is small and only reloads when a new session starts, so a demo has to use `/new` for saved memory to show up.
- **Nemotron reasoning stalls:** Super and Ultra on hosted NIM can think for minutes; Hermes raises its stall timeout to 600s for them, which can make the demo video slow.
- **Sandbox networking:** OpenShell allows outbound traffic only through a proxy, which breaks some messaging adapters (Slack issue #90601 and Mattermost issue #70116 are still open).
- **WhatsApp terms:** the default WhatsApp adapter uses the unofficial Baileys bridge, which may fail the judges' rule that integrations be authorized under their terms; prefer Telegram.

## Platform requirements
**Hermes on the macOS dev laptop**
- Apple Silicon macOS is Tier 1. Install with `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`.
- Needs git, curl, tar and shasum; the installer brings Python 3.14, Node, ripgrep and FFmpeg itself.
- The Desktop DMG is Apple Silicon only. Intel Macs work only through the CLI install or the darwin-x64 desktop bundle.
- Data lives in ~/.hermes/: config.yaml, .env, memories/, skills/, state.db and cron/.

**Other platforms**
- Linux (x86_64/aarch64, glibc + systemd) and WSL2 are Tier 1.
- Native Windows works through install.ps1 or MSIX (Windows 11 22H2+ for MSIX).
- Docker image: nousresearch/hermes-agent (x86_64/aarch64).
- pip, uv and brew installs are unsupported.

**Model requirements**
- Any OpenAI-compatible endpoint with tool calling and at least 64K context.
- Cloud Nemotron needs a free NVIDIA API key from build.nvidia.com (`nvapi-...`).
- Nebius needs a Token Factory key.
- Local models need enough unified memory for the model plus a 64K KV cache. The docs suggest a 9B Q4 model needs about 10 GB with a quantized KV cache; 27-35B models need 32 GB+.

**Always-on mode**
- The gateway runs as a launchd service on macOS (`hermes gateway install`), or in Docker or on a VPS.
- Cron only fires while the gateway runs.

**NemoHermes (Hermes inside OpenShell via NemoClaw)**
- Needs Docker (Colima or Docker Desktop on macOS Apple Silicon, 'Tested with limitations'), or Linux with Docker or rootless Podman.
- Intel Mac is unsupported.
- Local NIM or vLLM needs an NVIDIA GPU; on a Mac, use hosted NVIDIA Endpoints.
- The first sandbox start pulls a managed image, which takes several minutes.
- Host ports: dashboard 18789 (falls back up to 18799), API 8642 (up to 8652).

## Integration notes
**1. NVIDIA Nemotron via build.nvidia.com (simplest way to meet the 'NVIDIA open model' requirement)**

In `~/.hermes/.env`:
```
NVIDIA_API_KEY=nvapi-...
```
In `~/.hermes/config.yaml`:
```yaml
model:
  provider: "nvidia"
  default: "nvidia/nemotron-3-super-120b-a12b"
```
- One-off run: `hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b`.
- Switch mid-session with `/model`.
- Other catalog IDs: nvidia/nemotron-3-ultra-550b-a55b, nvidia/nemotron-3.5-lightning-30b-a3b, nvidia/nemotron-3-nano-omni-30b-a3b-reasoning.
- For a local NIM, set `NVIDIA_BASE_URL=http://localhost:8000/v1`.
- Always use the full `nvidia/` prefix.
- Do NOT define a custom provider named 'nvidia' (bug #123997).
- You can run a faster or cheaper model for the background memory/skill review with:
  ```yaml
  auxiliary:
    background_review:
      provider: nvidia
      model: nvidia/nemotron-3.5-lightning-30b-a3b
  ```
- Cron jobs can pin their own model: `hermes cron create ... --model ... --provider ...`, or set `cron.model` / `cron.model_provider`.

**2. Nebius**

In `.env`:
```
NEBIUS_API_KEY=...
```
- Provider `nebius` (aliases: nebius-token-factory, nebius-tf); base URL https://api.tokenfactory.nebius.com/v1 (override with NEBIUS_BASE_URL).
- Example: `hermes chat --provider nebius --model <id from /v1/models>`.
- Hermes' default auxiliary model on Nebius is `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`, so a Nemotron model is likely available there. Verify against the live /v1/models list.
- To use a Nebius 'Serverless' custom endpoint instead, treat it as a generic OpenAI-compatible endpoint:
  ```yaml
  model:
    provider: custom
    base_url: <nebius endpoint>/v1
    key_env: NEBIUS_API_KEY
    default: <model>
  ```
  Or use a named entry under `providers:` with `/model custom:<name>:<model>`.

**3. Local models**

```yaml
model:
  provider: custom
  base_url: http://localhost:11434/v1   # Ollama; llama-server :8080, vLLM :8000
  default: <model>
  context_length: 64000
```
- Ollama: `OLLAMA_CONTEXT_LENGTH=64000 ollama serve`.
- vLLM: `--enable-auto-tool-choice --tool-call-parser <parser>`.
- llama-server: `--jinja -c 64000`.

**4. OpenShell / NemoClaw**

NemoClaw is the supported way to run Hermes inside OpenShell. Hermes itself has no OpenShell terminal backend; OpenShell wraps the whole Hermes process.

Commands:
```
curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_AGENT=hermes NEMOCLAW_SANDBOX_NAME=my-hermes bash
nemohermes my-hermes status
nemohermes launch my-hermes                     # or: nemohermes my-hermes connect, then: hermes
nemohermes my-hermes dashboard-url --quiet      # dashboard on :18789
nemohermes my-hermes gateway-token --quiet      # bearer token for the API at http://127.0.0.1:8642/v1
nemohermes inference set --model nvidia/nemotron-3-super-120b-a12b --provider <p> --sandbox my-hermes
nemohermes my-hermes snapshot create --name before-demo
nemohermes my-hermes gateway restart
```
- Set `NVIDIA_INFERENCE_API_KEY` in the host shell. Inside the sandbox, Hermes calls `https://inference.local/v1` through the OpenShell L7 proxy and never sees the real key.
- Managed config is written to `/sandbox/.hermes/config.yaml`.
- Messaging channels (Telegram, Discord, Slack, ...) and MCP servers should be added with host-side NemoClaw commands so OpenShell creates the matching credential binding and egress policy.
- A custom image is possible with `nemohermes onboard --from <Dockerfile>`.
- Reference example: NVIDIA/nemoclaw-community `examples/personal-community-sentiment-triage` (Hermes + NemoClaw + Nemotron 3 Super; Outlook, Slack, GitHub).

**5. Messaging and API**
- Telegram: put `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` in `.env`, run `hermes gateway setup`, then `hermes gateway install` (launchd) and `hermes gateway start`.
- API for a custom UI: put `API_SERVER_ENABLED=true` and `API_SERVER_KEY=...` in `.env`, run `hermes gateway`, and POST to `http://127.0.0.1:8642/v1/chat/completions` with model `hermes-agent`.

**6. MCP and skills**
- Add MCP servers with an `mcp_servers:` block in config.yaml.
- Custom skills are SKILL.md folders in `~/.hermes/skills/<category>/<name>/`, or an external skills dir.
- To gate learning during a demo, set `skills.write_approval: true` / `memory.write_approval: true`.

**7. Privacy hardening**
- `web.keyless_fallback: false` with `web.search_backend: searxng` and `SEARXNG_URL` set.
- Avoid the Nous Tool Gateway.
- `terminal.backend: docker` for shell isolation, or OpenShell for whole-process isolation.
- Optional observability: NeMo Relay via `HERMES_NEMO_RELAY_PLUGINS_TOML`.

**8. Version pinning**
- `install.sh --commit <sha>` or `--branch`, or `hermes update --set-channel stable`.
- Don't run `hermes update` mid-build.

## Risks
- Upstream churn: 14.4k open issues (552 labeled bug), releases every 3-7 days rolling up hundreds to ~1,800 PRs each, and the install/update E2E matrix red on 2026-09-29 (#128399). Pin one commit or tag (e.g. v2026.9.24) on day 1, record it in the README for the judges' 'installs and runs consistently' check, and don't run `hermes update` during the build.
- macOS-specific gateway and update bugs: `hermes update` exits 1 or the launchd restart misbehaves (#126883, #105938), and Hermes-Setup and the Desktop app share /Applications/Hermes.app (#125249). Prefer the CLI install and run the gateway in the foreground or in Docker for the demo.
- Memory is small (2,200 + 1,375 chars) and frozen at session start. Gateway chats are one endless session, so newly saved memories don't show until `/new`. A demo of 'remembers me' must script session boundaries or use session_search, an external memory provider (Mem0, Honcho, Hindsight), or the team's own memory layer.
- Tool-calling reliability depends on the model. Small or local models (under ~30B) often claim a memory or skill save without calling the tool. Nemotron 3 Super/Ultra are the most-referenced Nemotron models for Hermes, but no published Hermes benchmark exists; test the exact model early.
- Latency: hosted NIM Nemotron 3 Super/Ultra can think for minutes. Hermes raises its stall timeout to 600s for them, and NIM idles out streams after about 120s. Expect slow turns in the demo video; consider nemotron-3.5-lightning or nano for fast paths and lower reasoning_effort.
- Hermes needs at least 64K context. That rules out Ollama defaults (4K under 24 GB VRAM) and many small local configurations on a Mac; a fully local Nemotron on the Mac may be impractical depending on RAM.
- OpenShell/NemoClaw path: macOS is 'Tested with limitations' (needs Colima or Docker Desktop), Hermes' model-compatibility registry in NemoClaw is empty, and 'production parity not yet asserted'. Proxy-only egress has broken adapters: Slack #90601 and Mattermost #70116 are open; the SSRF/DNS bug #32217 was fixed 2026-07-24. Use Telegram, which NemoClaw supports, and verify each integration inside the sandbox early.
- Two moving targets (NemoClaw and Hermes) pinned to each other: NemoClaw uses its own release-pinned managed Hermes image digest, so the in-sandbox Hermes version may differ from your local one. Develop custom skills and plugins so they work on both.
- Third-party terms (a judging criterion): Hermes' default WhatsApp adapter is the unofficial Baileys bridge with ban risk. Use Telegram (official Bot API), Slack or Discord bots, or WhatsApp Cloud API instead. Also check Gmail/Outlook OAuth app terms if used.
- Privacy story conflicts: the recommended Nous Portal path and its Tool Gateway send data to Nous-managed services, and web.keyless_fallback (default true) sends queries to third-party free tiers. Configure these off explicitly to back a 'data under your control' claim.
- Stale docs: the free Nemotron 3 Ultra promo ended 2026-06-18 (#53729), the curated NVIDIA model list was stale (#47977), and the NVIDIA blog pins OpenShell v0.0.38 (current is about v0.0.101+). Verify model IDs against the live https://integrate.api.nvidia.com/v1/models.
- Custom-provider pitfall: naming a custom provider 'nvidia' breaks CLI startup (#123997). Use built-in `provider: nvidia`.
- Originality rule: Hermes and NemoClaw are existing frameworks. The submission's new value has to be visible in the team's own skills, plugins, MCP servers, integrations and UX, with git history inside the submission window.

## Unknowns
- build.nvidia.com free-tier rate limits and credit quotas for Nemotron 3 Super/Ultra as of Oct 2026; not checked in this research.
- Whether 'Nebius Serverless' in the hackathon statement means Nebius Token Factory (inference API, natively supported by Hermes) or a separate Nebius serverless compute/endpoint product. If it is the latter, no Hermes-native integration was found; it would be wired as a generic OpenAI-compatible custom endpoint (low confidence on the product details).
- Exact Nemotron model IDs live on Nebius Token Factory (Hermes code references nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B as its auxiliary default; not verified against the live /v1/models list).
- Quantitative tool-calling quality of each Nemotron variant (Ultra vs Super vs 3.5 Lightning vs Nano) inside Hermes; no Hermes-published eval was found.
- Whether a Nemotron GGUF (e.g. nemotron-3-nano / 3.5-lightning 30B-A3B) runs acceptably on the team's Mac via llama.cpp at 64K context; depends on unified memory size, which is unknown.
- Exact Hermes version inside NemoClaw's current managed hermes-sandbox image digest, and whether the in-sandbox Telegram adapter works through the OpenShell proxy in the latest release (NemoClaw docs say Telegram is supported; not independently tested).
- Whether the hackathon judges count NemoClaw/OpenShell use as satisfying the 'use tools such as NemoClaw, OpenShell, Hermes, Nebius' clause, and how much weight each carries.
- Release cadence over the next 15 days; a breaking change in a pinned dependency or the PM-managed runtime could affect fresh installs by judges if the version is not pinned.

## Facts
- Hermes Agent repo is NousResearch/hermes-agent, license MIT, primary language Python, ~250,657 stars, last push 2026-10-02T06:37Z, default branch main. [high] (https://github.com/NousResearch/hermes-agent (GitHub API via gh, queried 2026-10-02))
- Latest release is 'Hermes Agent v0.21.5 (v2026.9.24)', tag v2026.9.24, published 2026-09-24; prior: v0.21.4 (2026-09-21), v0.21.3 (2026-09-14), v0.21.2 (2026-09-11), v0.21.1 (2026-09-07), v0.21.0 (2026-08-31). v0.21.4 reportedly bundled ~1,800 PRs, v0.21.5 ~460 PRs. [high] (https://github.com/NousResearch/hermes-agent/releases)
- Install (Linux/macOS/WSL2): `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`; Windows: `iex (irm https://hermes-agent.nousresearch.com/install.ps1)`; then `source ~/.zshrc` and `hermes`. Installer flags include --branch, --commit, --dir, --hermes-home, --non-interactive, --skip-browser, --skip-computer-use, --include-desktop. Code goes to ~/.hermes/hermes-agent/, launcher ~/.local/bin/hermes, data ~/.hermes/. [high] (https://hermes-agent.nousresearch.com/docs/getting-started/installation ; repo scripts/install.sh)
- Platform support Tier 1: macOS Apple Silicon (Desktop app or install.sh), Windows 10/11 x86_64/aarch64, Linux/WSL2 x86_64/aarch64, Docker image. Tier 2: Nix, Android/Termux aarch64. Unsupported: pip/uv/pypi installs, brew installs, AUR. macOS DMG installer is Apple Silicon only. [high] (https://hermes-agent.nousresearch.com/docs/getting-started/platform-support)
- Runtime: first-party installs run on Python 3.14 managed by Hermes' 'PM' tool (pyproject requires-python >=3.11,<3.15); PM also provides pinned Node.js, npm, ripgrep, FFmpeg; prerequisites are git, curl, tar, sha256 utilities. [high] (https://hermes-agent.nousresearch.com/docs/getting-started/installation ; repo pyproject.toml)
- Persistent memory = two files in ~/.hermes/memories/: MEMORY.md (agent notes, 2,200 char limit) and USER.md (user profile, 1,375 char limit), injected into the system prompt as a frozen snapshot at session start; managed by the `memory` tool (add/replace/remove). Writes mid-session only appear in the next session. Config keys: memory.memory_enabled, memory.user_profile_enabled, memory.memory_char_limit, memory.user_char_limit, memory.write_approval. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
- All CLI and messaging sessions are stored in SQLite at ~/.hermes/state.db with FTS5 full-text search, exposed via the `session_search` tool (~20ms queries). External memory providers are pluggable: Honcho, Mem0, Hindsight, OpenViking (memory.provider). [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/memory ; https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers)
- Messaging-gateway chats are one continuous session that survives restarts; the memory/learning loop needs session boundaries (`/new`) to load updated memory. Small local models (<~30B) often claim to save memory without calling the tool. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
- Skills: stored in ~/.hermes/skills/<category>/<name>/SKILL.md (+ references/, templates/, scripts/, assets/, examples/), YAML frontmatter (name, description, version, platforms, metadata.hermes.*), compatible with agentskills.io; progressive disclosure via skills_list/skill_view; every skill is a slash command. Agent creates/patches its own skills via `skill_manage` (create/patch/delete/write_file/remove_file); a background post-turn review can save memory/skills; gate with skills.write_approval / memory.write_approval. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
- Curator: background maintenance of agent-created skills; unused 14 days -> stale, 30 days -> archived to ~/.hermes/skills/.archive/; runs every 7 days when idle 2h; never auto-deletes. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/curator)
- Skills Hub: `hermes skills search|install|inspect|audit ...`; trusted taps include OpenAI, Anthropic, HuggingFace and NVIDIA/skills (added as default trusted tap); NVIDIA SkillEvaluator Tier 1 advisory scanning runs on skill installs. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/skills ; release notes (v0.20.x) at https://github.com/NousResearch/hermes-agent/releases)
- Cron: single `cronjob_manage` tool; `/cron add "every 2h" "..."` or `hermes cron create "every 1h" "..." --skill <name>`; delivers to origin chat, files, or platforms; supports no-agent script jobs and webhook-triggered jobs. Cron is executed by the gateway daemon, which ticks every 60s, so the gateway must be running. Cron runs cannot create more cron jobs. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
- Messaging gateway platforms: Telegram, Discord, Slack, Google Chat, WhatsApp (Baileys bridge, unofficial, ban risk), WhatsApp Cloud API (official), Signal (via signal-cli + Java 17), SMS, Email, Home Assistant, Mattermost, Matrix, DingTalk, Feishu/Lark, WeCom, Weixin, BlueBubbles/Photon (iMessage), QQ, Yuanbao, Microsoft Teams, LINE, ntfy, Raft, IRC, Buzz, SimpleX, webhooks, plus an OpenAI-compatible API server. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/messaging/ ; https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp)
- Gateway commands: `hermes gateway setup`, `hermes gateway install` (user systemd service on Linux / launchd on macOS), `hermes gateway start|restart|status`, or foreground `hermes gateway` / `hermes gateway run`. Telegram needs TELEGRAM_BOT_TOKEN and TELEGRAM_ALLOWED_USERS in the profile .env (dashboard/desktop also offers 'Create with QR'). [high] (https://hermes-agent.nousresearch.com/docs/user-guide/messaging/ ; https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram)
- Terminal backends (terminal.backend): local | docker | ssh | modal | daytona | vercel_sandbox | singularity. Docker uses one persistent hardened container by default (container_persistent: false gives per-session containers). OpenShell is NOT a terminal backend. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/configuration#terminal-backend-configuration)
- Subagents: `delegate_task` spawns isolated child agents; up to 10 concurrent by default (delegation.max_concurrent_children), nesting off by default (delegation.max_spawn_depth: 1); optional output_schema validation. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)
- MCP client: add servers under `mcp_servers:` in ~/.hermes/config.yaml (stdio `command`/`args`, or HTTP `url`/`headers`), with per-server tool filtering; `hermes mcp add ...`; Hermes can also act as a stdio-only MCP server via `hermes mcp serve`. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp)
- API server: set API_SERVER_ENABLED=true and API_SERVER_KEY in ~/.hermes/.env, run `hermes gateway`; exposes OpenAI-compatible http://127.0.0.1:8642/v1/chat/completions with model 'hermes-agent'. Hermes can also be embedded as a Python library (`from run_agent import AIAgent`, params include model, base_url, api_key) from a source checkout. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server ; https://hermes-agent.nousresearch.com/docs/guides/python-library)
- NVIDIA NIM is a built-in provider: provider id `nvidia` (aliases nim, nvidia-nim, build-nvidia, nemotron), env NVIDIA_API_KEY, default base URL https://integrate.api.nvidia.com/v1, override NVIDIA_BASE_URL (e.g. http://localhost:8000/v1 for local NIM). Example: `hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b`. Hermes auto-adds the NIM billing-origin header and strips name/tool_name from tool messages because NIM uses a stricter ToolMessage schema; default_max_tokens 16384. [high] (https://hermes-agent.nousresearch.com/docs/integrations/providers#nvidia-nim ; repo plugins/model-providers/nvidia/__init__.py ; https://hermes-agent.nousresearch.com/docs/reference/environment-variables)
- Hermes' curated NVIDIA catalog: nvidia/nemotron-3-ultra-550b-a55b, nvidia/nemotron-3-super-120b-a12b, nvidia/nemotron-3.5-lightning-30b-a3b, nvidia/nemotron-3-nano-omni-30b-a3b-reasoning (plus z-ai/glm-5.3, glm-5.2, moonshotai/kimi-k2.6, minimaxai/minimax-m3). The NVIDIA endpoint requires the full vendor-prefixed ID (a bare ID returns 404). [high] (repo hermes_cli/models_catalog_static.py ; https://github.com/NousResearch/hermes-agent/issues/123997)
- Nemotron 3 Super is the de facto 'known-good' Nemotron for Hermes tool calling: it is the Hermes docs' example model, the Nemotron model listed on Nous Portal, NemoClaw's default for Hermes on NVIDIA Endpoints, and the default in NVIDIA's Hermes+NemoClaw blog. No Hermes-published tool-calling benchmark for Nemotron variants was found. [medium] (https://hermes-agent.nousresearch.com/docs/integrations/providers ; https://hermes-agent.nousresearch.com/docs/integrations/nous-portal ; NVIDIA/NemoClaw docs/get-started/quickstart-langchain-deepagents-code.mdx ('shared Nemotron 3 Super default for OpenClaw and Hermes') ; https://developer.nvidia.com/blog/deploy-self-evolving-agents-for-faster-more-secure-research-with-a-hermes-agent-and-nvidia-nemoclaw/)
- Hermes sets a 600s stall-timeout floor for nemotron-3-ultra and nemotron-3-super because hosted NIM idles out long reasoning streams after a documented 60-180s, and a 300s floor for nemotron-3-nano and nemotron-3.5-lightning. [high] (repo agent/reasoning_timeouts.py ; agent/error_classifier.py (cites NVIDIA/NemoClaw#4846))
- Nebius Token Factory is a built-in provider: id nebius-token-factory (aliases nebius, nebius-tf, tokenfactory), env NEBIUS_API_KEY (or NEBIUS_TOKEN_FACTORY_API_KEY), base URL https://api.tokenfactory.nebius.com/v1 (override NEBIUS_BASE_URL); default auxiliary model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B; sends top-level reasoning_effort (low/medium/high) for reasoning-family models. Added in v0.21.x (PR #97916). Example: `hermes chat --provider nebius --model deepseek-ai/DeepSeek-V4-Pro`. [high] (repo plugins/model-providers/nebius-token-factory/__init__.py ; https://hermes-agent.nousresearch.com/docs/integrations/providers ; https://hermes-agent.nousresearch.com/docs/reference/environment-variables)
- Hermes integrates Nebius only as the Token Factory inference API. No Hermes integration with any 'Nebius Serverless' compute or jobs product was found. [medium] (grep of repo main @00373b5 for 'nebius')
- Custom OpenAI-compatible endpoint config: `model: {provider: custom, default: <model>, base_url: http://localhost:8000/v1, api_key: <key or empty>, key_env: <ENV>}` or `hermes model` -> 'Custom endpoint'. Named providers go under `providers:`. config.yaml is the source of truth; OPENAI_BASE_URL is only honored for provider openai-api; LLM_MODEL env var removed. [high] (https://hermes-agent.nousresearch.com/docs/integrations/providers#custom--self-hosted-llm-providers)
- Hermes rejects models with less than 64,000 tokens of context (MINIMUM_CONTEXT_LENGTH = 64_000). Ollama's default context is 4,096 on machines with under 24 GB VRAM, so set OLLAMA_CONTEXT_LENGTH=64000 or a Modelfile num_ctx. vLLM needs --enable-auto-tool-choice --tool-call-parser <parser>. llama-server needs --jinja and -c >= 64000. [high] (repo agent/model_metadata.py ; https://hermes-agent.nousresearch.com/docs/integrations/providers#ollama--local-models-zero-config)
- Mac local inference: Hermes docs recommend llama.cpp (`brew install llama.cpp`) or omlx on Apple Silicon. Hermes Desktop has a managed llama.cpp 'Local Models' panel, enabled in canary builds and in other builds via the --local launch flag. [high] (https://hermes-agent.nousresearch.com/docs/guides/local-llm-on-mac ; https://hermes-agent.nousresearch.com/docs/user-guide/local-models)
- Hermes SECURITY.md names NVIDIA OpenShell as one of two supported 'whole-process wrapping' sandboxes (the other is Hermes' own Docker image). OpenShell gives per-session sandboxes with declarative filesystem, L7 network egress, process/syscall and inference-routing policy, and injects credentials from a Provider store. [high] (https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md)
- NVIDIA NemoClaw (Apache-2.0, ~22.6k stars) describes itself as 'Run agents like Hermes, LangChain Deep Agents, and OpenClaw more securely inside NVIDIA OpenShell with managed inference'. Hermes is a first-class agent there, with a `nemohermes` CLI alias equivalent to `nemoclaw onboard --agent hermes`. [high] (https://github.com/NVIDIA/NemoClaw ; NemoClaw docs/about/ecosystem-hermes.mdx ; docs/reference/platform-support.mdx)
- NemoHermes install: `curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_AGENT=hermes NEMOCLAW_SANDBOX_NAME=my-hermes bash`. Then `nemohermes my-hermes status`, `nemohermes launch my-hermes` or `nemohermes my-hermes connect` followed by `hermes`, `nemohermes my-hermes dashboard-url --quiet`, `nemohermes inference set --model <m> --provider <p> --sandbox my-hermes`, and `nemohermes my-hermes snapshot create --name <n>`. The dashboard is on port 18789 and the OpenAI-compatible API on 8642 (token via `nemohermes my-hermes gateway-token --quiet`). The NVIDIA Endpoints key on the host is NVIDIA_INFERENCE_API_KEY (nvapi- prefix). Hermes config inside the sandbox is /sandbox/.hermes/config.yaml. [high] (https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart-hermes.html ; NemoClaw repo docs/get-started/quickstart-hermes.mdx ; docs/inference/use-nvidia-endpoints.mdx)
- In NemoClaw, Hermes is 'Tested', but its model-provider compatibility registry is empty, there are no Hermes-specific unit tests, and 'production parity with OpenClaw is not yet asserted'. Older doc versions call the Hermes option experimental. In NemoClaw, Hermes supports Tavily for web search, not the Brave Search path. [high] (NemoClaw repo docs/reference/platform-support.mdx ; docs/get-started/quickstart-hermes.mdx ; https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/get-started/quickstart)
- NemoClaw on macOS Apple Silicon is 'Tested with limitations' and needs Colima (`brew install colima docker`) or Docker Desktop running first; Xcode CLT is recommended. Intel Macs are unsupported. Local GPU vLLM/NIM onboarding requires an NVIDIA GPU (Apple Metal is unsupported). [high] (NemoClaw repo docs/reference/platform-support.mdx)
- NemoClaw messaging for Hermes: Telegram (TELEGRAM_BOT_TOKEN), Discord, Slack, WeChat, WhatsApp and Microsoft Teams; Google Chat is experimental. WeChat, WhatsApp and Teams are also flagged experimental. [high] (NemoClaw repo docs/manage-sandboxes/messaging-channels.mdx)
- NVIDIA published 'Deploy Self-Evolving Agents ... with a Hermes Agent and NVIDIA NemoClaw' on 2026-06-02. It uses nvidia/nemotron-3-super-120b-a12b by default and integrates Outlook, Slack and GitHub; the example lives at github.com/NVIDIA/nemoclaw-community/tree/main/examples/personal-community-sentiment-triage. The OpenShell version it pins (v0.0.38) is stale. [medium] (https://developer.nvidia.com/blog/deploy-self-evolving-agents-for-faster-more-secure-research-with-a-hermes-agent-and-nvidia-nemoclaw/)
- Known OpenShell-related issues: SSRF/DNS check blocked web tools inside OpenShell's proxy-only sandbox (#32217, closed 2026-07-24, fixed). Slack adapter fails in proxy-only sandboxes without aiohttp trust_env (#90601, OPEN, reported on NemoClaw v0.0.109 / OpenShell 0.0.101). Mattermost ignores the proxy (#70116, OPEN). SessionDB write failures in a long-running NemoHermes deployment (#90623, OPEN). [high] (https://github.com/NousResearch/hermes-agent/issues/32217 ; /issues/90601 ; /issues/70116 ; /issues/90623)
- The free Nemotron 3 Ultra on Nous Portal (nvidia/nemotron-3-ultra:free, with Nebius) ran only June 4-18, 2026. The guide is stale (issue #53729). [high] (https://hermes-agent.nousresearch.com/docs/guides/run-nemotron-3-ultra-free ; https://github.com/NousResearch/hermes-agent/issues/53729)
- Defining a custom provider keyed 'nvidia' (provider: custom:nvidia) with a vendor-prefixed model id makes CLI startup fail with AuthError (#123997, open). Use the built-in `provider: nvidia` with NVIDIA_API_KEY instead. [high] (https://github.com/NousResearch/hermes-agent/issues/123997)
- Repo health: 14,425 open issues (552 labeled bug). The 'Install & Update E2E matrix is red' (#128399, 2026-09-29). There are open macOS bugs where `hermes update` exits 1 or the launchd restart misbehaves (#126883, #105938). [high] (GitHub search API 2026-10-02 ; https://github.com/NousResearch/hermes-agent/issues/128399 ; /issues/126883 ; /issues/105938)
- Web search backends: firecrawl (default), searxng (self-hosted, free), parallel, tavily, perplexity, keenable, exa, plus DDGS, Brave and others. web.keyless_fallback defaults to true, which rotates queries through third-party free tiers when no key is set. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/configuration#web-search-backends ; https://hermes-agent.nousresearch.com/docs/user-guide/features/web-search)
- NeMo Relay observability is integrated natively in Hermes core, configured through a Relay plugins.toml (HERMES_NEMO_RELAY_PLUGINS_TOML). [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/built-in-plugins ; https://hermes-agent.nousresearch.com/docs/reference/environment-variables)
- Docker deployment: `docker run -it --rm -v ~/.hermes:/opt/data nousresearch/hermes-agent setup`, then `docker run -d --name hermes --restart unless-stopped -v ~/.hermes:/opt/data -p 8642:8642 nousresearch/hermes-agent gateway run` (s6-supervised). Docker installs don't support `hermes update`. [high] (https://hermes-agent.nousresearch.com/docs/user-guide/docker)


# REPORT: Nebius as inference/compute platform for the Personal AI track (Token Factory + Nebius AI Cloud Serverless AI), as of 2026-10-02

## Summary
This hackathon is Nebius's own event, the "Nebius x NVIDIA Global AI Hackathon" on Devpost. It runs Aug 26 to Oct 30, 2026 (deadline 10:00am PDT). Every entry must "run on either Nebius Token Factory or Nebius AI Cloud". The rules count that as met when the project makes a runtime call to the Token Factory inference API, or runs on Nebius AI Cloud compute (Serverless Jobs, Serverless Endpoints or DevPods). The demo must stay usable through judging, Dec 1-15, 2026.

"Nebius Serverless" can mean two things. Token Factory calls its shared per-token public endpoints "Serverless". The Devpost page, though, says "Nebius Serverless Endpoints/Jobs", which is the Serverless AI service in Nebius AI Cloud (Jobs, Endpoints, Devlabs).

**Token Factory**
- OpenAI-compatible API at https://api.tokenfactory.nebius.com/v1/ with Bearer NEBIUS_API_KEY.
- It supports tools/tool_choice, response_format, reasoning_effort, /v1/embeddings, /v1/rerank and /v1/responses.
- Nemotron models in the public catalog today:
  - nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B: $0.06 in / $0.24 out per 1M tokens, 262K context
  - nvidia/Nemotron-3_5-Lightning: $0.06 / $0.24, 1M context
  - nvidia/nemotron-3-super-120b-a12b: $0.30 / $0.90, 256K context
  - nvidia/Nemotron-3-Ultra-550b-a55b: $1 / $3, 1M context
- All four are tagged function_calling. Nemotron-3-Nano-Omni was removed on Aug 31, 2026, and models are retired fast.
- The only public embedding model is Qwen/Qwen3-Embedding-8B, at $0.01 per 1M tokens. There is no NVIDIA embedding model.
- By default Nebius keeps prompts and outputs (stored in Finland) for speculative decoding but does not train on them. Zero Data Retention is an org-level switch and should be turned on for the privacy story.

**Serverless AI (Nebius AI Cloud)**
- It runs any container image you give it, including a CPU-only agent gateway and NIM or vLLM GPU servers.
- Each endpoint gets a managed HTTPS URL and optional token auth. Billing is per second at Compute VM rates.
- The service is still in "Preview" with no SLA.
- There is no autoscaling and no scale-to-zero. An endpoint is one container VM that you stop and start by hand, and stopping it deletes the VM and its disk. Persistent memory needs a mounted bucket or shared filesystem.
- Cold starts take minutes: about 5 min for a small vLLM model, 8-12 min for a NIM.

**Credits and sign-up**
- Credits are small and cover Token Factory only: $25 from the hackathon promo code NEBIUS-DEVPOST-GLOBAL26, $25 from the Builders Program (expires after 90 days) and a $1 trial.
- Both Token Factory and AI Cloud require a bank card. AI Cloud charges $25 to your card when you add it, and that amount becomes prepaid balance.

**What already works with Nebius**
- Hermes Agent has a built-in provider, nebius-token-factory (since May 2026).
- NemoClaw has no Nebius provider, so it must use "Other OpenAI-compatible endpoint" with COMPATIBLE_API_KEY.
- Nebius's own cookbook shows OpenClaw running as a CPU Serverless Endpoint backed by Token Factory, but its model and URL are now out of date.

**Recommended plan:** use Token Factory with Nemotron 3 Super (or Nano/Lightning for cheap background calls) as the inference layer. Optionally host the always-on Hermes gateway as a CPU Serverless Endpoint (cpu-d3 2vcpu-8gb is about $0.066/hr, or $1.58/day) with a mounted filesystem, and use Serverless Jobs for background work.

## Platform requirements
Token Factory (the minimum Nebius integration):
- Any OS that can make HTTPS calls, including the macOS dev laptop.
- Sign up at https://tokenfactory.nebius.com with Google or GitHub. A bank card is mandatory to finish onboarding.
- Create an API key under Project -> API keys and export it as NEBIUS_API_KEY.
- Apply promo code NEBIUS-DEVPOST-GLOBAL26 ($25), join the Builders Program for another $25, and turn on Zero Data Retention in the account profile.
- No GPU or Docker is needed.

Nebius AI Cloud Serverless AI (optional, to host the always-on gateway, run background Jobs, or self-host a Nemotron NIM/vLLM):
- Separate account at https://console.nebius.com (Google, GitHub or Microsoft login). Adding a card charges $25, which becomes prepaid balance. Promo codes only work after billing is set.
- Nebius CLI on macOS: curl -sSL https://artifacts.nebius.cloud/cli/install.sh | bash, plus jq (brew install jq). Docker is needed only to build or mirror images; Nebius Container Registry is at cr.<region>.nebius.cloud.
- The project needs a VPC subnet, at least one free VM quota and one public-IP allocation. GPU quota is needed only for GPU endpoints: L40S is eu-north1 only (default quota 2), and RTX6000 and H200 default to 0 in us-central1.
- Serverless AI regions: eu-north1, eu-west1, me-west1, us-central1, uk-south1, uk-south2, eu-west2.
- Containers must be linux/amd64-compatible for the platform (Hermes publishes amd64 and arm64 images).
- The service is in Preview, has no SLA, and is single-node.

Indicative costs (prices from Oct 1, 2026):
- CPU endpoint cpu-d3 2vcpu-8gb: about $0.066/hr ($1.58/day). 4vcpu-16gb: about $0.132/hr.
- Disk: about $0.071/GiB-month. The default disk is 250Gi (about $17.75/month), so set --disk-size small.
- L40S GPU endpoint 1gpu-8vcpu-32gb: about $1.55/hr ($37/day), which is too costly to run always-on.

For the demo:
- Judging is Dec 1-15, 2026, and the demo must be reachable then.
- Builders credits expire 90 days after issue, so credits claimed in early October expire around early January.

## Integration notes
1) Token Factory chat with tools, Nemotron Super (verified API shape; not executed without a key):
curl https://api.tokenfactory.nebius.com/v1/chat/completions -H "Authorization: Bearer $NEBIUS_API_KEY" -H "Content-Type: application/json" -d '{"model":"nvidia/nemotron-3-super-120b-a12b","messages":[{"role":"user","content":"What is on my calendar tomorrow?"}],"tools":[{"type":"function","function":{"name":"get_calendar","description":"List events for a date","parameters":{"type":"object","properties":{"date":{"type":"string"}},"required":["date"]}}}],"tool_choice":"auto"}'
- Python: OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/", api_key=os.environ["NEBIUS_API_KEY"]).
- Check which models your key can reach: curl -s "https://api.tokenfactory.nebius.com/v1/models?verbose=true" -H "Authorization: Bearer $NEBIUS_API_KEY" | jq '.data[] | select(.id|test("emotron";"i")) | {id,pricing,context_length}'
- Embeddings: POST /v1/embeddings with model "Qwen/Qwen3-Embedding-8B" (the only public embedding model; not NVIDIA). For strictly private memory, run embeddings locally on the Mac.
- Model IDs are case-sensitive and use inconsistent casing:
  - nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B
  - nvidia/Nemotron-3_5-Lightning
  - nvidia/nemotron-3-super-120b-a12b
  - nvidia/Nemotron-3-Ultra-550b-a55b
- Use the global base URL, not the regional ones in older cookbook pages.

2) Hermes Agent with Token Factory (built-in provider):
- Put NEBIUS_API_KEY=... in ~/.hermes/.env.
- Set the model in ~/.hermes/config.yaml:
  model:
    provider: "nebius-token-factory"
    default: "nvidia/nemotron-3-super-120b-a12b"
- One-off run: hermes chat --provider nebius --model nvidia/nemotron-3-super-120b-a12b
- Set any fallback chain explicitly in config.yaml or with `hermes fallback`, because the plugin's built-in fallback list contains deprecated model IDs.
- Hermes uses nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B as its default auxiliary model on this provider, which is cheap for background tasks.
- To point Hermes at your own Nebius Serverless Endpoint (vLLM/NIM), use provider: custom with base_url: https://<endpoint-managed-url>/v1 and api_key: <endpoint token>. Bug #121388 (/model validating against the vendor host and ignoring base_url) was closed on 2026-09-25.

3) NemoClaw / OpenShell (OpenClaw or Hermes inside the sandbox) with Token Factory, which has no first-class provider:
NEMOCLAW_PROVIDER=custom NEMOCLAW_ENDPOINT_URL=https://api.tokenfactory.nebius.com/v1 NEMOCLAW_MODEL=nvidia/nemotron-3-super-120b-a12b COMPATIBLE_API_KEY="$NEBIUS_API_KEY" nemoclaw onboard --non-interactive
- Interactively, choose "Other OpenAI-compatible endpoint" in `nemoclaw onboard` or `nemohermes onboard`.
- To switch an existing sandbox: nemoclaw <name> inference set --endpoint-url https://api.tokenfactory.nebius.com/v1. This goes through the HTTPS Pin Runtime adapter, which has a hard 30-second total upstream deadline, so long non-streamed reasoning responses may be cut off. Test this early.
- The DNS-backed HTTPS URL is rejected by the Hermes Provider setup and by Hermes host-side `config set`.
- The sandbox only ever sees inference.local; the key stays on the host. That is a strong privacy story.

4) Always-on agent on Nebius Serverless AI (CPU endpoint). The pattern comes from Nebius's OpenClaw cookbook. This is a Hermes adaptation that has not been tested:
export SUBNET_ID=$(nebius vpc subnet list --format jsonpath='{.items[0].metadata.id}')
nebius ai endpoint create --name hermes-gw --image nousresearch/hermes-agent:latest --args "gateway run" --container-port 8642 --env "API_SERVER_ENABLED=true,API_SERVER_HOST=0.0.0.0" --env-secret API_SERVER_KEY=<secret>,NEBIUS_API_KEY=<secret> --volume "<shared_filesystem_or_bucket>:/opt/data:rw" --platform cpu-d3 --preset 2vcpu-8gb --disk-size 30Gi --public --subnet-id "$SUBNET_ID"
- Get the URL: nebius ai endpoint get-by-name --name hermes-gw --format json | jq -r '.status.public_endpoints[]'
- Stop or start it with: nebius ai endpoint stop|start --id <id>
- Stopping deletes the container disk, so memories and skills must live on the mounted /opt/data volume.
- Hermes's API key and Nebius's --auth token both use "Authorization: Bearer". Pick one layer, or confirm that Nebius forwards the header.
- The OpenClaw cookbook version is at github.com/nebius/serverless-ai-cookbook/agents/openclaw. Update its model to a current Nemotron ID and its base URL to the global one.

5) Background work on Serverless Jobs (for the "Nebius Serverless" story):
nebius ai job create --name nightly-memory-consolidation --image <your-image> --container-command python --args "consolidate.py" --platform cpu-d3 --preset 2vcpu-8gb --timeout 1h --env-secret NEBIUS_API_KEY=<secret> --volume "<fs>:/data:rw" --subnet-id "$SUBNET_ID"
- REST equivalent: POST https://api.nebius.cloud/ai/v1/jobs
- No schedule flag is documented, so trigger jobs from Hermes cron through the CLI or REST.

6) Self-hosting Nemotron on a Serverless GPU Endpoint (optional, costly):
- Use vllm/vllm-openai:v0.18.0-cu130 with --model <HF Nemotron ID> on gpu-l40s-a 1gpu-8vcpu-32gb (eu-north1), or a NIM mirrored into Nebius Container Registry (see the cookbook's inference/nim-endpoint/scripts/deploy-nim.sh).
- Expect 5-12 minute cold starts and about $1.55/hr or more.
- Token Factory per-token pricing is far cheaper for a 15-day build.

## Risks
- Model churn: Token Factory removed Nemotron-3-Nano-Omni and Llama-3.1-Nemotron-Ultra on Aug 31, 2026, with no automatic rerouting. A Nemotron ID could disappear before judging (Dec 1-15), so keep the model ID in config and build a fallback to another Nemotron model.
- Many official examples are stale. The OpenClaw serverless cookbook uses the removed zai-org/GLM-5, the embeddings doc uses BAAI/bge-en-icl, the function-calling doc uses Llama-3.1-8B-fast, cookbooks use regional base URLs, the Nebius Nemotron page lists the deprecated Nano Omni, and Hermes's built-in Nebius fallback list contains deprecated -fast IDs.
- Credits only cover Token Factory ($25 promo + $25 Builders + $1 trial). Hosting on Nebius AI Cloud Serverless is likely out of pocket: the $25 prepaid card charge, about $1.58/day for an always-on 2vCPU endpoint, and about $37/day for an L40S GPU endpoint. Budget for a live demo from now through Dec 15.
- Both Nebius products require a bank card at signup, and an Indian or other non-US card may hit auto-charge or e-mandate problems (unverified). A failed Token Factory card charge suspends the account, which would break the demo.
- Serverless AI is in Preview with no SLA, no auto-recovery and no autoscaling or scale-to-zero. Stopping an endpoint deletes its disk, and an endpoint can go to ERROR NotEnoughResources after 30 minutes of provisioning. Mount a volume for state and keep a local-Mac fallback demo.
- Cold starts take minutes (about 5 min for vLLM, 8-12 min for NIM), and NIM pulls straight from nvcr.io often fail without mirroring the image into Nebius Container Registry. Do not rely on starting GPU endpoints on demand during a live demo.
- NemoClaw has no Nebius provider. The custom HTTPS endpoint path goes through a pinning adapter with a 30-second total upstream deadline (reasoning responses may time out), and DNS-backed HTTPS is rejected for Hermes Provider setup and Hermes `config set`. Validate NemoClaw/Hermes with Token Factory on day 1-2.
- Privacy claim: Token Factory public endpoints keep prompts and outputs for speculative decoding by default and route globally. You must enable org-level ZDR, and you cannot claim a fixed region without a paid dedicated endpoint.
- Dynamic rate limits (example baseline 60 RPM / 400K TPM) can return 429s during agent bursts. Implement backoff and read the x-ratelimit headers.
- Ambiguity over 'Nebius Serverless': calling Token Factory satisfies the platform rule, but the Personal AI text suggests Serverless Endpoints/Jobs. Using at least one Serverless Job or Endpoint visibly in the video may help judging.

## Unknowns
- Whether the global base URL https://api.tokenfactory.nebius.com/v1 serves every Nemotron model, given that the catalog lists specific regions such as us-central1 for Super and Ultra. Check with GET /v1/models using a real key.
- The current default rate limits for a new or individual Token Factory account (the docs give only an illustrative baseline).
- When the hackathon promo code NEBIUS-DEVPOST-GLOBAL26 credits expire, and whether any hackathon credit applies to Nebius AI Cloud (Serverless) rather than only Token Factory. The form is JS-rendered and could not be read.
- Whether Serverless AI endpoint containers allow privileged mode or Docker-in-Docker, which NemoClaw/OpenShell would need to run inside a Serverless Endpoint (probably not; unverified). A regular Nebius Compute VM is the likely alternative.
- Whether Nebius endpoint token auth strips or forwards the Authorization header to the container, which matters when layering it with the Hermes API_SERVER_KEY or the OpenClaw gateway token.
- The exact entrypoint and args needed to run nousresearch/hermes-agent as a Nebius Serverless Endpoint, including s6-overlay behavior on Nebius container VMs. The suggested command is untested.
- The minimum allowed --disk-size for Serverless endpoints and jobs, and whether jobs can be scheduled natively (the docs mention 'scheduled' but show no flag).
- Cold-start time for a small CPU endpoint (the docs give about 5 minutes only for a GPU vLLM endpoint).
- Whether Nemotron models on Token Factory honor reasoning_effort or chat_template_kwargs to turn thinking off for faster agent turns.
- Whether the Batch API mentioned in the rate-limit docs exists; /v1/batches is not in the current OpenAPI spec.
- Whether an Indian-issued card works for Nebius auto-charging (e-mandate rules) on either product.

## Facts
- Hackathon = 'Nebius x NVIDIA Global AI Hackathon' on Devpost; submission deadline October 30, 2026 @ 10:00am PDT; categories: Coding and Agentic Engineering, Best Apps and Agents, Personal AI, Physical AI; demo video <=3 min public YouTube; public repo with open-source license; README with setup; feedback on Token Factory required. [high] (https://nebiusglobalaihackathon.devpost.com/)
- Rules: 'Runs on Nebius Token Factory or Nebius AI Cloud' means the project makes a runtime call to the Token Factory inference API, or is deployed/run using Nebius AI Cloud compute (Serverless Jobs, Serverless Endpoints, or DevPods). Must use at least one NVIDIA open source model (Nemotron, GR00T, Cosmos, Sonic referenced). Judging Dec 1-15, 2026; demo access must remain available during judging; criteria equally weighted: Technological Implementation, Design, Potential Impact, Quality of Idea. [medium] (https://nebiusglobalaihackathon.devpost.com/rules)
- Devpost page references 'Nebius Serverless Endpoints' (real-time inference) and 'Nebius Serverless Jobs' (background processing and asynchronous workflows), i.e. 'Nebius Serverless' in the Personal AI text maps to Nebius AI Cloud Serverless AI. [medium] (https://nebiusglobalaihackathon.devpost.com/)
- Hackathon credits: $25 Token Factory credits via promo form with activation code NEBIUS-DEVPOST-GLOBAL26 (https://nebius.com/promo-code?utm_promo_event_code=2026-devpost-global-ai-hack&utm_promo_code_type=Token_Factory&utm_promo_activation_code=NEBIUS-DEVPOST-GLOBAL26); plus $25 Token Factory credit from Nebius Builders Program (https://dev.nebius.com/builders). [high] (https://nebiusglobalaihackathon.devpost.com/resources)
- Builders Program: $25 Token Factory + $25 Tavily credits (site also lists $100 LangSmith, $50 Toloka, $50 Tendem); credits expire 90 days from issuance; one signup per verified email and per IP per 24h; not for production/revenue workloads. No AI Cloud credit amount listed. [medium] (https://nebius.com/builders-terms-and-conditions ; https://dev.nebius.com/builders)
- Token Factory base URL is https://api.tokenfactory.nebius.com/v1/ (OpenAI-compatible; auth header 'Authorization: Bearer $NEBIUS_API_KEY'); API keys created at https://tokenfactory.nebius.com/project/api-keys. Old name Nebius AI Studio (api.studio.nebius.com) is superseded. [high] (https://docs.tokenfactory.nebius.com/quickstart ; https://docs.tokenfactory.nebius.com/api-reference/introduction)
- Public model catalog (authoritative JSON at https://tokenfactory.nebius.com/api/public/models_info) lists Nemotron serverless models: nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B ($0.06 in/$0.24 out per 1M, 262,144 ctx, fp8, eu-north1), nvidia/Nemotron-3_5-Lightning ($0.06/$0.24, 1,048,576 ctx, bf16, eu-north1), nvidia/nemotron-3-super-120b-a12b ($0.30/$0.90, 262,144 ctx, fp4, us-central1), nvidia/Nemotron-3-Ultra-550b-a55b ($1.00/$3.00, 1,048,576 ctx, fp4, us-central1). All tagged function_calling, reasoning, responses_api. Only one flavor per model (no '-fast' variant listed). [high] (https://tokenfactory.nebius.com/api/public/models_info ; https://tokenfactory.nebius.com/model-catalog.md)
- Also in catalog: NousResearch/Hermes-4-405B ($1/$3, 131K ctx); embeddings only Qwen/Qwen3-Embedding-8B ($0.01 per 1M input tokens, 40,960 ctx). No NVIDIA embedding model in the public catalog. Docs embedding example still uses BAAI/bge-en-icl (stale). [high] (https://tokenfactory.nebius.com/api/public/models_info ; https://docs.tokenfactory.nebius.com/api-reference/examples/create-embeddings)
- Model churn: nvidia/Nemotron-3-Nano-Omni, nvidia/Llama-3_1-Nemotron-Ultra-253B-v1, nvidia/Cosmos3-Super-Reasoner, NousResearch/Hermes-4-70B, meta-llama/Llama-3.3-70B-Instruct removed from Token Factory Serverless on Aug 31, 2026 (replacements: Nemotron-3_5-Lightning / nemotron-3-super-120b-a12b). June 22, 2026 removed all '-fast' variants listed and zai-org/GLM-5, Kimi-K2.5. No automatic rerouting. [high] (https://docs.tokenfactory.nebius.com/august-2026-deprecation-notice ; https://docs.tokenfactory.nebius.com/june-2026-deprecation-notice)
- Nebius Nemotron marketing page still lists 'Nemotron 3 Nano Omni' which was deprecated Aug 31, 2026 — page is stale. [high] (https://nebius.com/services/token-factory/nemotron)
- Function calling: OpenAI-compatible tools format; tool_choice supports 'auto' or an explicit {type:function,function:{name}}; model does not execute tools. ChatCompletionRequest schema includes tools, tool_choice, response_format, reasoning_effort, stream, stream_options, extra_body, max_completion_tokens. [high] (https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling ; https://api.tokenfactory.nebius.com/openapi.json (version 20260930-cfb76be12))
- Token Factory API paths include /v1/chat/completions, /v1/completions, /v1/embeddings, /v1/rerank, /v1/responses, /v1/images/generations, /v1/models, /v1/files, /v1/fine_tuning/jobs, /v0/dedicated_endpoints. [high] (https://api.tokenfactory.nebius.com/openapi.json)
- Rate limits are dynamic: example baseline 60 RPM / 400,000 TPM; +20% per 15-min window when avg usage >=80%, -1/3 when <=50%, hard ceiling 20x base; HTTP 429 with x-ratelimit-* headers; requests over limit may still be served with 'x-ratelimit-over-limit: yes'. Actual defaults shown at https://tokenfactory.nebius.com/project/rate-limits. [medium] (https://docs.tokenfactory.nebius.com/ai-models-inference/rate-limits)
- Data retention: by default Token Factory stores inputs/outputs for Speculative Decoding (stored in Finland/EU) but never uses content for training. Zero Data Retention (ZDR) is an org-level toggle on the account profile page; with ZDR no inputs/outputs retained; may reduce inference speed. Public endpoints have region 'Global' (processing location can change without notice); dedicated endpoints are region-pinned contractually (DPA 6.1). ISO 27001/27701, SOC 2 Type II, GDPR, EU-US DPF. [high] (https://docs.tokenfactory.nebius.com/legal/legal-quick-guide)
- Public (serverless) endpoints: docs warn that region-specific base URLs (e.g. api.tokenfactory.us-central1.nebius.com) can stop working; use the global base URL. Public endpoints 'best suited for testing and non-critical workloads'. [high] (https://docs.tokenfactory.nebius.com/public-serverless)
- Token Factory signup: log in with Google or GitHub at https://tokenfactory.nebius.com; billing account with bank card is mandatory to finish onboarding; first signup gets $1 trial credit valid 30 days; promo codes applied via balance -> Top up -> With promo code; failed card charge suspends the account. [high] (https://docs.tokenfactory.nebius.com/other-capabilities/billing-new)
- Token Factory dedicated endpoints: per GPU-hour billing (per-minute granularity), min/max replicas autoscaling, region-pinned, custom weights; billed only when >=1 replica is ready; public serverless is per-token with dynamic rate limits. [high] (https://docs.tokenfactory.nebius.com/ai-models-inference/dedicated-endpoints/overview ; https://docs.tokenfactory.nebius.com/ai-models-inference/dedicated-endpoints/billing-policy)
- Token Factory also offers Sandboxes (beta, 'Contree'): VM-isolated code execution with git-like branching, OCI images, SDK/CLI/MCP server; beta limit 50 concurrent operations, 180-day checkpoint retention. [high] (https://docs.tokenfactory.nebius.com/sandboxes/overview)
- Nebius AI Cloud Serverless AI = Devlabs (browser IDE/notebook; called DevPods in the Mar 2026 launch blog), Jobs (run to completion), Endpoints (serve requests at a URL). Bring any container image (public or private registry incl. nvcr.io, or Nebius Container Registry). Runs on Compute container VMs; per-second billing at Compute rates; no separate pricing/quotas. [high] (https://docs.nebius.com/serverless/overview ; https://docs.nebius.com/serverless/pricing-quotas ; https://nebius.com/blog/posts/introducing-serverless)
- Serverless AI legal terms: 'The Service is in Preview stage', no SLA, single-node only, no automatic retry/recovery/redundancy; endpoints run continuously until explicitly stopped/deleted; when an endpoint is stopped the VM AND disk are deleted (persist data via mounted Object Storage bucket or shared filesystem). [high] (https://docs.nebius.com/legal/specific-terms/serverless-ai)
- Serverless AI endpoints have no autoscaling/replicas/scale-to-zero in docs; stop/start is manual (nebius ai endpoint stop/start --id). Stopped endpoints incur no compute or disk charges (mounted volumes still billed). [high] (https://docs.nebius.com/serverless/endpoints/manage ; https://docs.nebius.com/serverless/lifecycle)
- Endpoint features: each HTTP container port exposed via a managed HTTPS URL; optional bearer token auth (--auth token --token/--token-secret); env vars and SecretStash secrets (--env, --env-secret); --volume for buckets/shared filesystems; --inject-file (read-only, <=64 KiB); default container disk 250Gi (--disk-size); --preemptible only on GPU platforms; CPU endpoints supported (e.g. --platform cpu-d3 --preset 4vcpu-16gb). [high] (https://docs.nebius.com/serverless/endpoints/manage ; https://docs.nebius.com/serverless/quickstart/endpoints)
- Cold start / provisioning: vLLM endpoint creation 'takes approximately five minutes' (Qwen3-0.6B on L40S); NIM endpoints ~8-12 min first time and large NIM images pulled straight from nvcr.io often fail the cold-start window (ERROR in ~2-3 min, no logs) — mirror to Nebius Container Registry first. If capacity unavailable, provisioning retries up to 30 min then ERROR NotEnoughResources (no auto-retry). [high] (https://docs.nebius.com/serverless/tutorials/deploy-model ; https://github.com/nebius/serverless-ai-cookbook/blob/main/inference/nim-endpoint/README.md ; https://docs.nebius.com/serverless/lifecycle)
- Jobs: --timeout min 1h, max 168h, default 24h; --restart-policy on-failure|never; REST POST https://api.nebius.cloud/ai/v1/jobs; container disk removed when the job finishes. No cron/schedule flag documented (page text mentions 'scheduled' but no option shown). [medium] (https://docs.nebius.com/serverless/jobs/manage)
- Compute prices from Oct 1, 2026 (USD): Non-GPU AMD Epyc Genoa (cpu-d3, all regions) $0.015/vCPU-h + $0.0045/GiB-h; L40S (gpu-l40s-a/-d, eu-north1 only) $1.35/GPU-h (+$0.012/vCPU-h, $0.0032/GiB-h), preemptible $0.65; RTX PRO 6000 (gpu-rtx6000 us-central1; gpu-rtx6000-a uk-south2/eu-south1) $1.80/GPU-h, preemptible $0.95; H100 $4.50 (preempt. $2.15); H200 $5.40 ($2.45); B200 $8.50; B300 $9.50. Network SSD disk $0.071/GiB-month; Shared Filesystem SSD $0.08/GiB-month. [high] (https://docs.nebius.com/compute/resources/pricing)
- Serverless AI is available in eu-north1, eu-west1, me-west1, us-central1, uk-south1, uk-south2, eu-west2 (not eu-south1, us-north1, or private eu-north2). [high] (https://docs.nebius.com/overview/regions)
- Default GPU quotas for new projects vary by region: L40S 2 (eu-north1), H100 32 (eu-north1), H200 32 eu-north1 / 8 eu-west1 / 0 us-central1, RTX PRO 6000 0 in us-central1 but 32 in uk-south2/eu-south1. Non-GPU: 12 VMs, 200 vCPUs per region. [high] (https://docs.nebius.com/compute/resources/quotas-limits)
- Nebius AI Cloud signup: console.nebius.com with Google, GitHub or Microsoft account; billing requires card (individual or company); adding a card charges $25 that goes to account balance; promo codes can only be applied after billing details are set. [high] (https://docs.nebius.com/signup-billing/sign-up ; https://docs.nebius.com/signup-billing/payments/promo-codes)
- Nebius CLI install (Ubuntu and macOS): curl -sSL https://artifacts.nebius.cloud/cli/install.sh | bash; then nebius profile create --profile <name> --endpoint api.nebius.cloud --federation-endpoint auth.nebius.com --parent-id <project_ID> (browser login). [high] (https://docs.nebius.com/cli/install)
- Hermes Agent has a built-in Nebius Token Factory provider (added 2026-05-18): provider name 'nebius-token-factory', aliases nebius, nebius-tokenfactory, nebius-tf, token-factory, tokenfactory; env NEBIUS_API_KEY (or NEBIUS_TOKEN_FACTORY_API_KEY), optional NEBIUS_BASE_URL (default https://api.tokenfactory.nebius.com/v1); default_aux_model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B. Latest Hermes release v2026.9.24. [high] (https://github.com/NousResearch/hermes-agent/blob/main/plugins/model-providers/nebius-token-factory/__init__.py ; https://github.com/NousResearch/hermes-agent/blob/main/website/docs/integrations/providers.md)
- Hermes's built-in Nebius fallback_models list still contains deprecated IDs (Kimi-K2.5-fast, MiniMax-M2.5-fast, DeepSeek-V3.2-fast, Hermes-4-70B, gpt-oss-120b-fast, Llama-3.3-70B) — must set model and fallback explicitly. Its reasoning_effort allowlist excludes 'nemotron', so Hermes does not send reasoning_effort for Nemotron models. [high] (https://github.com/NousResearch/hermes-agent/blob/main/plugins/model-providers/nebius-token-factory/__init__.py)
- Hermes official Docker image nousresearch/hermes-agent stores all state (config, keys, sessions, skills, memories) in /opt/data; 'gateway run' exposes an OpenAI-compatible API server on port 8642 when API_SERVER_ENABLED=true, API_SERVER_HOST=0.0.0.0 and API_SERVER_KEY (>=8 chars) are set; gateway supervised by s6-overlay; amd64 and arm64 images. [high] (https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/docker.md)
- Nous + Nebius ran a free Nemotron 3 Ultra promo on Nous Portal (nvidia/nemotron-3-ultra:free) June 4-18, 2026 — expired; not usable now. [high] (https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/run-nemotron-3-ultra-free.md)
- NemoClaw has no named Nebius provider; Nemotron hosted on third-party/self-hosted servers uses 'Other OpenAI-compatible endpoint' (NEMOCLAW_PROVIDER=custom, NEMOCLAW_ENDPOINT_URL, NEMOCLAW_MODEL, COMPATIBLE_API_KEY). Agent in sandbox calls inference.local; OpenShell injects the credential at egress so the sandbox never sees the raw key. NemoClaw default cloud model is nvidia/nemotron-3-super-120b-a12b. [high] (https://github.com/NVIDIA/NemoClaw/blob/main/docs/inference/set-up-openai-compatible-endpoint.mdx ; https://github.com/NVIDIA/NemoClaw/blob/main/docs/inference/choose-inference-provider.mdx ; https://github.com/NVIDIA/NemoClaw/blob/main/docs/inference/custom-endpoint-security.mdx)
- NemoClaw rejects DNS-backed HTTPS URLs (like api.tokenfactory.nebius.com) for Hermes Provider setup, Hermes host-side 'config set' and direct blueprint runs; 'nemoclaw inference set --endpoint-url <https-url>' supports them via the HTTPS Pin Runtime adapter, which enforces ONE 30-second total upstream deadline covering connect, TLS and the complete response. [high] (https://github.com/NVIDIA/NemoClaw/blob/main/docs/inference/custom-endpoint-security.mdx)
- Nebius's official serverless cookbook shows OpenClaw gateway as a Serverless CPU Endpoint (ghcr.io/openclaw/openclaw:latest, cpu-d3 8vcpu-32gb, port 18789) wired to Token Factory via models.providers.tokenfactory {baseUrl, apiKey, api:'openai-completions'}. Written 2026-03-25; uses zai-org/GLM-5 (removed June 22, 2026) and a regional base URL, and uses cloudflared for HTTPS (endpoints now get managed HTTPS URLs). [high] (https://github.com/nebius/serverless-ai-cookbook/blob/main/agents/openclaw/README.md)
- Community starter (fruteroclub) for this hackathon defaults to nvidia/nemotron-3-super-120b-a12b on https://api.tokenfactory.nebius.com and notes the permanent demo URL must stay up through 2026-12-15. [medium] (https://github.com/fruteroclub/nebius-nvidia-ai-hackathon-starter)


# REPORT: NVIDIA NemoClaw: what it is, maturity, install, macOS support, OpenClaw features inside it, inference routing (NVIDIA/Nebius/local), license, security, known breakages (as of 2026-10-02)

## Summary
NemoClaw (github.com/NVIDIA/NemoClaw, Apache-2.0, created 2026-03-15, announced 2026-03-16) is NVIDIA's open-source "reference stack" for running an always-on agent inside an NVIDIA OpenShell sandbox. It is a host CLI (`nemoclaw`), a versioned blueprint and an agent integration layer. OpenShell does the sandboxing (Landlock, seccomp, network namespace, deny-by-default egress with operator approval) and keeps credentials outside the sandbox by routing all model calls through `inference.local`. The agent runs inside the sandbox: OpenClaw by default, or Hermes Agent (`nemohermes`), or LangChain Deep Agents Code. It is still officially alpha / "early preview" with no SLA. Tags ship roughly weekly: v0.0.130 was tagged 2026-10-01, but the hosted installer installs the maintainer "lkg" tag, which is currently v0.0.124 from 2026-09-14. That release pins OpenShell to exactly 0.0.116 and OpenClaw 2026.7.1; main pins OpenClaw 2026.9.2. An open epic (#12558) plans the move to OpenShell 0.1.2, so breaking changes are likely during the 15-day window. Pin one release and do not upgrade mid-build. On macOS the official status is "Tested with limitations": Apple Silicon only, with Docker Desktop or Colima running first, 4+ vCPU and 8+ GB given to the container VM, Node 22.19+, and Xcode Command Line Tools. Landlock is downgraded to best_effort in the Docker VM, read-only host mounts are not supported on macOS, and there is no NVIDIA GPU, so on a Mac local inference only works through host Ollama. No NVIDIA GPU is needed when you use hosted inference: NVIDIA Endpoints (build.nvidia.com, default model `nvidia/nemotron-3-super-120b-a12b`), OpenRouter, OpenAI, Anthropic, Gemini, or any OpenAI-compatible URL such as Nebius Token Factory. That makes the Nemotron "NVIDIA open model" requirement easy to meet from the cloud. The dev laptop (M1 Pro, 16 GB RAM) cannot run the default local Nemotron model: `nemotron-3-nano:30b` needs about 26 GB. Its Ollama 0.13.1 is also below NemoClaw's 0.32.9 minimum. So plan on hosted Nemotron, either NVIDIA Endpoints or Nebius. OpenClaw's own features work inside the sandbox: workspace memory files (SOUL.md, USER.md, MEMORY.md, memory/YYYY-MM-DD.md), SKILL.md skills (`nemoclaw <sb> skill install`), heartbeats (HEARTBEAT.md and `NEMOCLAW_AGENT_HEARTBEAT_EVERY`), cron/automations (each job needs a manual `operator.admin` device approval), managed HTTPS MCP servers, and Telegram, Slack or Discord channels. WhatsApp, Teams and Google Chat are only "limited" or "experimental". Security caveats are real. NVIDIA's August 25, 2026 bulletin fixed critical OpenShell sandbox-escape CVEs and a NemoClaw Ollama exposure CVE. OpenClaw has a history of exposed instances, ClawHub malware (ClawHavoc) and prompt injection, and reviewers note the sandbox does not stop exfiltration through allowed endpoints. For an always-on demo, the more reliable path is the "Tested" Linux+Docker route on a cloud VM (Ubuntu 24.04, 4 vCPU / 16 GB, used over SSH). Use the Mac only for development, since a sleeping laptop is not "always-on" and macOS has several open onboarding bugs.

## Platform requirements
Officially supported (status from docs/reference/platform-support.mdx, generated from ci/platform-matrix.json, 2026-10-02):
- Linux x86_64 or arm64 with Docker: "Tested", the primary path. Ubuntu 24.04 is validated; the installer assumes apt-get.
- DGX Spark: "Tested".
- macOS on Apple Silicon only, with Docker Desktop or Colima: "Tested with limitations". Intel Mac is unsupported.
- Windows needs WSL2 with the Docker Desktop backend ("Tested with limitations"); native Windows is unsupported.
- Headless Linux VM over SSH: "Tested with limitations".
- RTX consumer/Pro GPU hosts: "Deferred".

Minimum host: 4 vCPU, 8 GB RAM, 20 GB free disk (recommended 16 GB RAM, 40 GB disk). Software: Node.js >= 22.19 and npm >= 10 (the installer can install Node via nvm), python3 at a trusted path, sha256sum or shasum, and a container runtime. Docker is the default; rootless Podman only on qualified Linux/WSL.

macOS extras:
- Install Xcode CLT.
- Start Docker Desktop or Colima before running the installer.
- Give the VM at least 4 vCPU and 8 GB; 6 vCPU / 12 GB is suggested.
- Colima needs `brew install colima docker`, and currently `export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock` (issue #12367).
- Landlock degrades to best_effort, and there are no read-only host mounts.

No NVIDIA GPU is needed when using hosted inference (NVIDIA Endpoints, Nebius or another OpenAI-compatible endpoint, OpenRouter and others). An NVIDIA GPU with Container Toolkit and CDI is needed only for local NIM or managed vLLM. Apple Metal GPUs are unsupported for NIM/vLLM. On a Mac, local inference is possible only through host Ollama >= 0.32.9 behind NemoClaw's token proxy on port 11435.

Team laptop (M1 Pro, 16 GB, macOS 27.0.1): it can run NemoClaw with cloud inference. It cannot run the default local Nemotron (nemotron-3-nano:30b needs about 26 GB). Docker Desktop must be started and its resources raised, and Ollama 0.13.1 must be upgraded if local inference is wanted.

The network must reach github.com, ghcr.io, nvcr.io (only for NIM), npm, Homebrew and the provider endpoint during install; air-gapped installs are unsupported.

## Integration notes
RECOMMENDED SETUP (macOS for development; a Linux VM for the always-on demo)

1) Prepare the Mac.
- Open Docker Desktop. In Settings -> Resources, set CPUs >= 4 (6 better) and Memory >= 8 GB, then run `docker info`.
- Optional: `brew upgrade ollama` (it is 0.13.1; 0.32.9 or newer is required).
- Get an NVIDIA API key (nvapi-...) from build.nvidia.com.
- Do not `npm i -g nemoclaw` (placeholder package) and do not install standalone OpenShell 0.1.x; NemoClaw manages OpenShell 0.0.116 itself.

2) Install with a pinned release and keep it for the whole build:
```
export NVIDIA_INFERENCE_API_KEY=nvapi-...
curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_INSTALL_REF= NEMOCLAW_INSTALL_TAG=v0.0.124 NEMOCLAW_NON_INTERACTIVE=1 NEMOCLAW_ACCEPT_THIRD_PARTY_SOFTWARE=1 NEMOCLAW_AGENT=openclaw NEMOCLAW_PROVIDER=build NEMOCLAW_SANDBOX_NAME=my-assistant bash
```
v0.0.124 is the current lkg; use v0.0.130 if you need features documented on main, such as OpenClaw 2026.9.x memory.search keys. Then run:
- `nemoclaw my-assistant status`
- `nemoclaw my-assistant dashboard-url --quiet`
- `nemoclaw launch my-assistant`, or `nemoclaw my-assistant connect` followed by `openclaw tui`

3) NVIDIA open model (meets the hackathon requirement).
- Default route: provider nvidia-prod/"build", model `nvidia/nemotron-3-super-120b-a12b` on https://integrate.api.nvidia.com/v1.
- Switch model: `nemoclaw my-assistant inference set --provider nvidia-prod --model nvidia/nemotron-3-ultra-550b-a55b`.
- Do not run `openshell inference set` directly on a NemoClaw gateway.

4) Nebius, or any OpenAI-compatible endpoint (including a Nebius Serverless or self-hosted vLLM/NIM endpoint), at onboarding:
```
NEMOCLAW_PROVIDER=custom NEMOCLAW_ENDPOINT_URL=https://api.tokenfactory.nebius.com/v1 NEMOCLAW_MODEL=nvidia/nemotron-3-super-120b-a12b COMPATIBLE_API_KEY=$NEBIUS_API_KEY NEMOCLAW_PREFERRED_API=openai-completions nemoclaw onboard --non-interactive
```
Add NEMOCLAW_REASONING=true only if the model returns only reasoning_content; that mode skips the tool-call checks.
If onboarding rejects the DNS-backed HTTPS URL, onboard with NVIDIA Endpoints first, then switch:
```
COMPATIBLE_API_KEY=... nemoclaw my-assistant inference set --provider compatible-endpoint --model <id> --endpoint-url https://<host>/v1 --credential-env COMPATIBLE_API_KEY --inference-api openai-completions
```
That goes through the HTTPS Pin Runtime adapter on host port 11438. The sandbox only ever calls https://inference.local/v1, and the key stays on the host.

5) Local model on the Mac (optional; the RAM limit applies). Pick Local Ollama (option 8). NemoClaw proxies host 127.0.0.1:11434 through token proxy port 11435. Only qwen3.5:9b fits 16 GB in the registry; a smaller Nemotron Ollama tag could be served via option 4 at http://localhost:11434/v1 with NEMOCLAW_COMPATIBLE_AUTH_MODE=none (unverified).

6) Persistent memory. Workspace Markdown lives at /sandbox/.openclaw/workspace (SOUL.md, USER.md, AGENTS.md, TOOLS.md, HEARTBEAT.md, MEMORY.md, memory/YYYY-MM-DD.md). Back it up with:
- `nemoclaw my-assistant snapshot create|list|restore`
- `nemoclaw my-assistant download /sandbox/.openclaw/workspace ./backup`

For vector memory search, run an embedding server, then:
```
nemoclaw my-assistant policy add local-inference --yes
openclaw config set memory.search.enabled true
openclaw config set memory.search.provider <prov>
openclaw config set memory.search.model <model>
nemoclaw my-assistant gateway restart
openclaw memory index --agent main --force
```

7) Skills.
- Write `./skills/<name>/SKILL.md` (frontmatter: name, description).
- Install with `nemoclaw my-assistant skill install ./skills/<name>/`; check with `nemoclaw my-assistant skill list`.
- Prefer your own skills over ClawHub ones; ClawHub egress is allowed by default.

8) Always-on behavior.
- Heartbeat: `export NEMOCLAW_AGENT_HEARTBEAT_EVERY=30m` before onboarding, or `openclaw config set agents.defaults.heartbeat.every 30m` in the sandbox, plus a HEARTBEAT.md checklist.
- Scheduled jobs: in `nemoclaw my-assistant connect`, run `openclaw cron ...` / `openclaw automations create ...`, then approve the operator.admin request with `openclaw devices list --json` and `openclaw devices approve <requestId>`.

9) Channels.
```
export TELEGRAM_BOT_TOKEN=...; export TELEGRAM_ALLOWED_IDS=<your id>
nemoclaw my-assistant channels add telegram
```
Telegram, Slack and Discord are Tested. WhatsApp uses WhatsApp Web QR pairing (ToS risk for "authorized third-party integrations").

10) Tools and data.
- Remote MCP: `nemoclaw my-assistant mcp add <name> --url https://... --env TOKEN_ENV`.
- Egress: `nemoclaw my-assistant policy add <preset>` (e.g. github, telegram, slack, outlook, jira, weather), approving live requests in `openshell term`.
- Web search: NEMOCLAW_WEB_SEARCH_PROVIDER=brave|tavily with BRAVE_API_KEY or TAVILY_API_KEY.

11) Hermes Agent variant (fulfils the "Hermes" tool mention):
```
curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_AGENT=hermes NEMOCLAW_SANDBOX_NAME=my-hermes bash
```
Then `nemohermes my-hermes status` and `nemohermes launch my-hermes`. It uses the same providers, and the inference set command patches /sandbox/.hermes/config.yaml.

12) Always-on host. Run the demo instance on an Ubuntu 24.04 VM with 4+ vCPU, 16 GB RAM, 40 GB disk and Docker (e.g. a Nebius CPU VM or a Brev launchable). Run onboarding in tmux, reach the dashboard through `ssh -N -L 18789:127.0.0.1:18789 user@vm`, and document the manual reboot-recovery steps.

13) Coding-agent help: `claude mcp add --transport http fern-docs https://docs.nvidia.com/nemoclaw/_mcp/server`.

## Risks
- Alpha software with a very fast release cadence (v0.0.124 to v0.0.130 in about 2 weeks) and a pending OpenShell 0.0.116 to 0.1.2 migration (epic #12558 opened 2026-10-01). Re-running the curl installer mid-build may pull breaking changes. Pin NEMOCLAW_INSTALL_TAG and never upgrade during the build.
- The hosted docs track main (v0.0.130, OpenClaw 2026.9.2), but the default installer installs lkg v0.0.124 (OpenClaw 2026.7.1). Config keys in the docs (e.g. memory.search, automations) may not match the installed OpenClaw version.
- macOS is only 'Tested with limitations'. Open bugs include the Colima docker.sock regression (#12367), the Ollama backend not running after onboarding (#11984), intermittent sandbox-recreation failures (#12501) and host.docker.internal not resolving (#3136). Judges require the project to 'install and run consistently on its stated platform', so state Linux (Ubuntu 24.04 + Docker) as the platform, or test the macOS path repeatedly from a clean state.
- Always-on conflicts with a laptop that sleeps. Headless Linux reboot recovery is manual and not guaranteed, so the demo VM needs a scripted recovery or must not reboot.
- The 16 GB M1 Pro cannot run the default local Nemotron (nemotron-3-nano:30b needs about 26 GB) and Docker Desktop takes 8 GB of it. The 'NVIDIA open model' requirement must be met through hosted Nemotron (NVIDIA Endpoints or Nebius); the API key's quota and rate limits are unverified.
- Third-party Nemotron endpoints (Nebius) may return reasoning-only output that breaks the onboarding smoke and tool-call checks (#3279). DNS-backed HTTPS custom endpoints may be rejected at onboarding and need the `inference set` workaround. Test the Nebius route on day 1.
- Cron and automation creation needs manual operator.admin device approval inside the sandbox, which breaks a fully hands-off flow unless it is scripted. Heartbeats run every 30 minutes by default and burn tokens.
- Anything outside the deny-by-default egress policy blocks until an operator approves it in `openshell term`. Demo flows that touch new hosts (Gmail, calendar APIs, custom MCP) hang unless their presets or policies are added up front. The Personal tier opens everything, which undermines the privacy story.
- Managed MCP supports only authenticated HTTPS Streamable HTTP servers with a single bearer env var. Local stdio MCP servers and OAuth flows such as Google Workspace need extra plumbing (your own HTTPS MCP bridge or a custom policy).
- WhatsApp works by unofficial WhatsApp Web QR pairing with no Meta Business API, which may conflict with the 'third-party integrations must be authorized under their terms' rule. Prefer the Telegram Bot API, Slack or Discord.
- Security posture: OpenClaw prompt injection and exfiltration through allowed endpoints remain unsolved. ClawHub has a malware history (ClawHavoc). The August 2026 NVIDIA bulletin fixed critical OpenShell sandbox escapes, so use only current pinned releases and never install unreviewed ClawHub skills. Judges may probe the security claims.
- The sandbox image is about 2.4 GB and the first onboarding builds and pulls images for several minutes. Too few Docker or Colima resources make the build stall silently on Apple Silicon.
- `nemoclaw <sb> destroy` deletes workspace memory unless a snapshot was taken first. Rebuilds preserve only manifest-declared state; ~/.local installs and other ad-hoc changes inside the sandbox are lost on rebuild or upgrade.
- One OpenShell gateway exposes one inference route to every sandbox on it. Switching models for one sandbox re-points the others, so use separate gateway ports or one sandbox.
- Supplementary data may need to be readable by the agent, but read-only host mounts are unsupported on macOS Docker. Use `nemoclaw <sb> upload`, `share mount` (SSHFS plus macFUSE) or Linux.

## Unknowns
- Whether `nemoclaw onboard` with NEMOCLAW_PROVIDER=custom accepts a DNS-backed public HTTPS URL such as https://api.tokenfactory.nebius.com/v1 directly on v0.0.124 or v0.0.130, or only through the `inference set` HTTPS Pin adapter. The docs are ambiguous; test it.
- The exact 'Nebius Serverless' product, base URL and model IDs. Only Nebius Token Factory URLs were found here, from secondary docs. Defer to the Nebius research thread.
- Whether Nemotron models via Nebius return structured tool calls reliably in OpenClaw tool loops (versus reasoning-only output).
- The free-tier quotas and rate limits of the NVIDIA build.nvidia.com API key for nvidia/nemotron-3-super-120b-a12b in late 2026. Not verified.
- Which semantic memory-search backend OpenClaw uses by default inside NemoClaw when no embedding provider is configured, and whether the plain MEMORY.md / daily-notes memory is enough without vector search. Not verified.
- Whether a small Nemotron model tag in Ollama (e.g. 4B) works with NemoClaw tool-call validation on a 16 GB Mac via the OpenAI-compatible route. The registry only lists nemotron-3-nano:30b.
- The exact OpenClaw cron/automations CLI syntax in OpenClaw 2026.7.1 (lkg) versus 2026.9.x. The docs page fetched was unversioned.
- How to disable OpenShell anonymous telemetry on the NemoClaw-managed gateway (OPENSHELL_TELEMETRY_ENABLED=false is documented for standalone OpenShell). How it is passed to the NemoClaw-launched gateway was not confirmed.
- Per-CVE details of NVIDIA bulletin a_id 5872. The NVIDIA page returned 403, so the versions come from a secondary summary (aicybr.com).
- Whether NemoClaw will move the lkg tag or switch to OpenShell 0.1.x during the 2026-10-02 to about 10-17 window.
- Whether a hackathon-provided Nebius VM or Brev credit is available for running the always-on Linux instance.
- Whether managed MCP can reach an MCP server running on the macOS host (loopback is blocked; host.openshell.internal behavior for MCP is not documented).

## Facts
- NemoClaw is 'an open source reference stack for running supported AI agents more safely inside NVIDIA OpenShell sandboxes', providing guided onboarding, managed inference, network policy, managed integrations, snapshots and lifecycle ops via the NemoClaw CLI. Supported agents: OpenClaw (default), Hermes, LangChain Deep Agents Code. [high] (https://github.com/NVIDIA/NemoClaw/blob/main/README.md)
- License is Apache-2.0. The repo has 22.6k stars, 3.1k forks and about 748 open issues/PRs, was created 2026-03-15, and was last pushed 2026-10-02. [high] (GitHub API repos/NVIDIA/NemoClaw)
- Project status: Stage alpha, label 'Early preview', since 2026-03-16. Maintainers work best-effort and there is no SLA. No hosted or managed NemoClaw exists. [high] (https://github.com/NVIDIA/NemoClaw/blob/main/docs/reference/platform-support.mdx)
- The latest release tag is v0.0.130 (2026-10-01) and the previous one v0.0.129 (2026-09-23). There are 130 v0.0.x tags since March, a roughly weekly or faster cadence. [high] (GitHub API tags + docs/changelog/2026-10-01.mdx, 2026-09-23.mdx)
- The hosted installer (https://www.nvidia.com/nemoclaw.sh redirects to raw main install.sh) defaults to DEFAULT_INSTALL_REF='lkg'. The lkg tag points to commit 6f3cced, which is v0.0.124 (2026-09-14). A specific release is pinned with `NEMOCLAW_INSTALL_REF= NEMOCLAW_INSTALL_TAG=vX.Y.Z` on the bash side of the pipe. [high] (curl https://www.nvidia.com/nemoclaw.sh; git ls-remote --tags NVIDIA/NemoClaw; docs/get-started/quickstart.mdx)
- The blueprint pins OpenShell exactly (min_openshell_version = max_openshell_version = 0.0.116) on both main and v0.0.124. The OpenClaw image version is 2026.9.2 on main and 2026.7.1 at v0.0.124 (lkg). Hermes is pinned at v2026.9.14 (semver 0.21.3). [high] (nemoclaw-blueprint/blueprint.yaml, Dockerfile.base ARG OPENCLAW_VERSION (main and v0.0.124), agents/hermes/Dockerfile.base and manifest.yaml)
- Standalone OpenShell has moved to v0.1.x (v0.1.0 on 2026-09-25, v0.1.2 on 2026-09-28) while NemoClaw still pins 0.0.116 (2026-08-28). Open epic #12558 (2026-10-01) is 'Complete pre-work for the OpenShell 0.1.2 upgrade', so a major dependency bump is likely soon. [high] (GitHub API NVIDIA/OpenShell tags/releases; https://github.com/NVIDIA/NemoClaw/issues/12558)
- Scope split: OpenClaw is the assistant runtime (tools, memory, behavior). OpenShell is the sandbox, policy engine, inference routing and the `openshell` CLI. NemoClaw is the host CLI, OpenClaw plugin, versioned blueprint, managed inference and MCP, messaging setup and lifecycle. Without NemoClaw you can run `openshell sandbox create --from openclaw` to get the community sandbox. [high] (https://github.com/NVIDIA/NemoClaw/blob/main/docs/about/ecosystem.mdx)
- The March 16, 2026 press release described a 'privacy router' that lets agents use cloud frontier models while keeping local models and privacy boundaries. It also claimed NemoClaw runs on GeForce RTX PCs/laptops, RTX PRO workstations, DGX Station and DGX Spark. Current docs never use the term 'privacy router'. The implemented mechanism is OpenShell's `inference.local` route with host-held credentials, plus an experimental complexity-based Model Router (NVIDIA LLM Router v3 on host port 4000; its pool is gpt-oss-20b and Nemotron 3 Super on integrate.api.nvidia.com). [high] (https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-NemoClaw-for-the-OpenClaw-Community/default.aspx; docs/inference/how-inference-routing-works.mdx; nemoclaw-blueprint/router/pool-config.yaml)
- The marketing claim of RTX PC support is not backed by the support matrix. The row 'NVIDIA RTX (consumer and Pro workstation GPUs)' on Linux is 'Deferred' (not validated), and managed vLLM on such hosts requires NEMOCLAW_EXPERIMENTAL=1. [high] (docs/reference/platform-support.mdx)
- Platform matrix: Linux+Docker is 'Tested' and the primary path (Ubuntu 24.04 validated). DGX Spark is 'Tested'. macOS Apple Silicon with Colima or Docker Desktop is 'Tested with limitations' and has CI. Windows WSL2 is 'Tested with limitations'. Intel Macs, native Windows, non-NVIDIA GPUs (Apple Metal included), air-gapped installs, Kubernetes and multi-user hosts are unsupported. [high] (https://docs.nvidia.com/nemoclaw/latest/get-started/prerequisites.html; docs/reference/platform-support.mdx)
- Hardware: 4 vCPU, 8 GB RAM, 20 GB disk minimum; 16 GB RAM and 40 GB disk recommended. The sandbox image is about 2.4 GB compressed. Software: Node.js >=22.19 (package.json engines), npm 10+, Python 3 at a trusted path (/opt/homebrew/bin/python3 is accepted), and Docker Desktop, Docker Engine or Colima (rootless Podman only on qualified Linux/WSL). [high] (docs/get-started/prerequisites.mdx; package.json)
- macOS specifics: start Docker Desktop or Colima before installing. Colima users need `brew install colima docker`. Install Xcode CLT. Default Colima (2 vCPU / 2 GiB) stalls the BuildKit build silently; use `colima start --cpu 6 --memory 12 --disk 100` or raise Docker Desktop resources (preflight warns below 4 vCPU / 8 GiB). [high] (docs/reference/troubleshooting.mdx (macOS first-run failures; Colima sections))
- On macOS the Docker VM kernel may lack Landlock, so filesystem restrictions silently drop to best_effort. Read-only `--host-mount` is unsupported with Docker on macOS (only Linux and WSL2). `share mount` via SSHFS needs macFUSE. [high] (docs/reference/troubleshooting.mdx (Landlock section); docs/manage-sandboxes/workspace-files.mdx; docs/reference/commands.mdx (share mount))
- Open macOS bug #12367 (2026-09-27): Colima onboarding fails at '[2/8] Starting OpenShell gateway' with 'Socket not found: /var/run/docker.sock' (a regression). The workaround is `export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock`. Other open macOS issues: #11984 (Ollama backend not running after onboarding on v0.0.125), #12501 (intermittent sandbox recreation failure), #3136 (host.docker.internal does not resolve inside sandbox). [high] (https://github.com/NVIDIA/NemoClaw/issues/12367 ; /issues/11984 ; /issues/12501 ; /issues/3136)
- `npm install -g nemoclaw` installs a placeholder npm package (version 0.1.0, about 222-byte package.json, no binary) and does not work. Use the curl installer. [medium] (https://github.com/openclaw/openclaw/issues/149950 (closed 2026-09-16, macOS 27.0 arm64))
- Install command: `curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash`. Non-interactive example: `curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_NON_INTERACTIVE=1 NEMOCLAW_ACCEPT_THIRD_PARTY_SOFTWARE=1 NEMOCLAW_AGENT=openclaw NEMOCLAW_PROVIDER=build NVIDIA_INFERENCE_API_KEY=<key> NEMOCLAW_SANDBOX_NAME=my-assistant bash`. Recovery: `nemoclaw onboard --resume` or `--fresh`. [high] (https://docs.nvidia.com/nemoclaw/latest/get-started/quickstart.html (docs/get-started/quickstart.mdx))
- Post-install commands: `nemoclaw my-assistant status`, `nemoclaw my-assistant dashboard-url --quiet` (dashboard on 127.0.0.1:18789; the token URL acts as a password), `nemoclaw launch my-assistant` (starts `openclaw tui`), `nemoclaw my-assistant connect`, `nemoclaw my-assistant logs --follow`, `nemoclaw my-assistant policy add`, and `openshell term` (TUI to approve egress). [high] (docs/get-started/quickstart.mdx; docs/reference/commands.mdx)
- Onboarding inference menu: 1 NVIDIA Endpoints (NVIDIA_INFERENCE_API_KEY, nvapi- prefix), 2 OpenRouter, 3 OpenAI, 4 Other OpenAI-compatible endpoint (COMPATIBLE_API_KEY), 5 Anthropic, 6 Other Anthropic-compatible, 7 Google Gemini, 8 Local Ollama (localhost:11434), 9 Model Router (experimental). Canonical provider IDs for `inference set`: nvidia-prod, nvidia-nim, nvidia-router, openai-api, openrouter-api, anthropic-prod, compatible-anthropic-endpoint, gemini-api, compatible-endpoint, hermes-provider, llama-cpp-local, ollama-local, vllm-local. [high] (docs/get-started/quickstart.mdx; docs/reference/commands.mdx (inference set))
- NVIDIA Endpoints bundled fallback models are `nvidia/nemotron-3-ultra-550b-a55b` and `nvidia/nemotron-3-super-120b-a12b`. Nemotron 3 Super is the default for OpenClaw and Hermes. Validation uses /v1/chat/completions only. The live catalog is loaded during interactive onboarding. [high] (docs/inference/use-nvidia-endpoints.mdx; docs/inference/choose-model.mdx; blueprint.yaml default profile (endpoint https://integrate.api.nvidia.com/v1))
- Custom OpenAI-compatible non-interactive onboarding variables: NEMOCLAW_PROVIDER=custom, NEMOCLAW_ENDPOINT_URL (no userinfo, query or fragment), NEMOCLAW_MODEL, COMPATIBLE_API_KEY, NEMOCLAW_REASONING=true for reasoning-only models, NEMOCLAW_PREFERRED_API=openai-completions|openai-responses. Runtime defaults to /v1/chat/completions. Private, loopback and internal addresses are rejected unless listed in NEMOCLAW_TRUSTED_PRIVATE_HOSTS (loopback no-auth is allowed only on ports 8000 and 11434). [high] (docs/inference/set-up-openai-compatible-endpoint.mdx; docs/inference/choose-compatible-inference-api.mdx; docs/inference/custom-endpoint-security.mdx)
- A DNS-backed public HTTPS custom endpoint may be rejected during custom-endpoint onboarding ('DNS-backed HTTPS endpoint is not supported'). `nemoclaw <sb> inference set --provider compatible-endpoint --model <id> --endpoint-url <https-url> --credential-env <ENV> --inference-api openai-completions` on an existing sandbox handles it through a local HTTPS Pin Runtime adapter (port 11438). The source shows public hosts pass SSRF preflight with pinned addresses, so whether onboarding accepts Nebius directly is unclear. [medium] (docs/reference/troubleshooting.mdx (DNS-backed HTTPS endpoint); docs/inference/custom-endpoint-security.mdx; src/lib/onboard/inference-selection-validation.ts)
- A Nebius Token Factory + NemoClaw integration was attempted via the OpenAI-compatible option. Issue #3279 (closed) reported that reasoning-only Nemotron models from third-party providers return text in reasoning_content and failed the smoke check and tool calls. NEMOCLAW_REASONING is now documented for custom endpoints, but reasoning mode 'does not verify tool calling or streaming'. [medium] (https://github.com/NVIDIA/NemoClaw/issues/3279; docs/inference/set-up-openai-compatible-endpoint.mdx)
- Nebius Token Factory OpenAI-compatible base URL is https://api.tokenfactory.nebius.com/v1/ (regional: https://api.tokenfactory.us-central1.nebius.com/v1/) and it hosts `nvidia/nemotron-3-super-120b-a12b`. This comes from secondary docs; verify with the Nebius research thread. [medium] (https://docs.agno.com/models/providers/gateways/nebius/overview ; https://nebius.com/services/token-factory/nemotron)
- The Local Ollama model registry used for auto-selection has three entries: qwen3.6:35b (30,000 MB), nemotron-3-nano:30b (26,000 MB, DEFAULT_OLLAMA_MODEL_TAG) and qwen3.5:9b (12,000 MB). NemoClaw requires Ollama >= 0.32.9 and upgrades it with `brew upgrade ollama` on macOS. Local NIM and managed vLLM require NVIDIA GPU, Container Toolkit and CDI, so not on a Mac. [high] (src/lib/inference/ollama-model-registry.ts; docs/inference/set-up-ollama.mdx; docs/reference/platform-support.mdx)
- The developer Mac checked locally is an Apple M1 Pro with 8 cores, 16 GB RAM, macOS 27.0.1, about 134 GiB free disk, Node v22.21.1, Homebrew, Xcode, and Docker.app installed but not running. Ollama client is 0.13.1, below the 0.32.9 minimum. Colima, openshell and nemoclaw are not installed. [high] (local commands: uname, sw_vers, sysctl, docker version, ollama --version)
- OpenClaw workspace files live in /sandbox/.openclaw/workspace/: SOUL.md, USER.md, IDENTITY.md, AGENTS.md, TOOLS.md and HEARTBEAT.md (seeded), POLICY.md (written by NemoClaw), and MEMORY.md plus memory/YYYY-MM-DD.md (created by the agent). They survive restart, rebuild and upgrade, are deleted on `destroy` unless snapshotted, and `~` is /sandbox, not the workspace. [high] (docs/manage-sandboxes/workspace-files.mdx)
- Semantic memory search requires configuring an embedding provider. The documented recipe uses a separate host Ollama container on port 8000 with qwen3-embedding:0.6b, the `local-inference` policy preset, and `openclaw config set memory.search.provider/model ...` (OpenClaw 2026.9.1 config keys), then `openclaw memory index --agent main --force`. [high] (docs/configure-agents/configure-memory-search.mdx)
- Heartbeats: set NEMOCLAW_AGENT_HEARTBEAT_EVERY (e.g. 30m or 2h; 0m disables) before onboarding. Otherwise run `openclaw config set agents.defaults.heartbeat.every 2h` inside the sandbox. The OpenClaw default is 30 minutes. Each beat runs an isolated session that reads HEARTBEAT.md. [high] (docs/configure-agents/configure-agent-heartbeats.mdx)
- Cron: NemoClaw auto-approves only the operator.pairing, read and write scopes, never operator.admin. Creating a cron job needs a manual approval: in `nemoclaw <sb> connect`, run the command, then `openclaw devices list --json` and `openclaw devices approve <requestId>`. OpenClaw's scheduler CLI is `openclaw automations ...`, with `openclaw cron` as an alias, and can deliver output to a chat channel or webhook. [medium] (docs/security/gateway-authentication-controls.mdx; https://docs.openclaw.ai/automation/cron-jobs)
- Skills: `nemoclaw <sb> skill install ./my-skill/` needs a SKILL.md with YAML frontmatter including `name`, and is limited to 1,024 files and 64 MiB. For OpenClaw it runs `openclaw skills install <staged> --agent main --force`. The commands `skill list` and `skill remove` also exist. ClawHub (clawhub.ai:443) is in the OpenClaw baseline egress policy. OpenClaw installs registry skills with `openclaw skills install @owner/<slug>` and its docs say to treat third-party skills as untrusted code. [high] (docs/reference/commands.mdx (skill install); docs/reference/network-policies.mdx; https://docs.openclaw.ai/tools/skills)
- Managed MCP: `nemoclaw <sb> mcp add <name> --url https://... --env TOKEN_VAR [--deny-tool <glob>]` supports authenticated HTTPS Streamable HTTP servers only. OpenShell keeps the raw token outside the sandbox and substitutes it at egress. [high] (docs/reference/commands.mdx (mcp add); docs/reference/platform-support.mdx)
- Messaging status: Slack, Discord and Telegram are Tested. WeChat and WhatsApp are 'Tested with limitations'; WhatsApp pairs through a WhatsApp Web QR code and does not use the Meta Business API. Microsoft Teams and Google Chat are Experimental and need a public HTTPS webhook. Telegram setup: TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_IDS and TELEGRAM_REQUIRE_MENTION (default 1), then onboarding or `nemoclaw <sb> channels add telegram`. [high] (docs/reference/platform-support.mdx (Messaging Integrations); docs/manage-sandboxes/set-up-telegram.mdx)
- Network policy is deny-by-default. The OpenClaw baseline allows integrate.api.nvidia.com, clawhub.ai, openclaw.ai, docs.openclaw.ai and registry.npmjs.org. The tiers are Restricted, Balanced (default: npm, pypi, huggingface, brew-balanced, brave/tavily), Open (adds slack, discord, telegram, jira, outlook and others) and Personal (personal-open-internet: any host on 80/443 with no approval prompts). Unlisted requests are held for operator approval in `openshell term`. [high] (docs/reference/network-policies.mdx)
- Hermes path: `curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_AGENT=hermes NEMOCLAW_SANDBOX_NAME=my-hermes bash`, then `nemohermes my-hermes status`, `nemohermes launch my-hermes` or the dashboard. Hermes is 'Tested', but production parity with OpenClaw is not asserted and macOS CI does not test it separately. Hermes supports Tavily web search only. [high] (docs/get-started/quickstart-hermes.mdx; docs/reference/platform-support.mdx)
- Headless Linux server (e.g. a Brev or any cloud VM) is 'Tested with limitations'. Keep the gateway and dashboard on loopback and reach them through an SSH tunnel (`ssh -N -L 18789:127.0.0.1:18789`). Do not open port 8080. Recovery after a host reboot is manual and not guaranteed. [high] (docs/deployment/deploy-to-headless-server.mdx)
- CVE-2026-25253 (CVSS 3.1 8.8): OpenClaw before 2026.1.29 took a gatewayUrl from the query string and auto-connected over WebSocket, sending its token (one-click compromise). It was published 2026-02-01. [high] (https://cveawg.mitre.org/api/cve/CVE-2026-25253)
- The ClawHavoc campaign: Koi Security found 341 malicious ClawHub skills out of 2,857, 335 of which used fake prerequisites to install the Atomic macOS Stealer and targeted always-on Mac minis. The count later rose to 824 or more as ClawHub grew past 10,700 skills. [high] (https://koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting ; https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html)
- NVIDIA security bulletin for NemoClaw and OpenShell (2026-08-25, a_id 5872, Canadian Cyber Centre AV26-849). Reported CVEs include CVE-2026-65093 and CVE-2026-65083 (OpenShell sandbox escape, CVSS 9.9, fixed in 0.0.34) and CVE-2026-65105 (NemoClaw bound Ollama to 0.0.0.0:11434 with unauthenticated access, CVSS 8.1, fixed by 0.0.25). The per-CVE details come from a secondary summary because the NVIDIA page returned 403. [medium] (https://cyber.gc.ca/en/alerts-advisories/nvidia-security-advisory-av26-849 ; https://nvidia.custhelp.com/app/answers/detail/a_id/5872 ; https://aicybr.com/blog/nvidia-nemoclaw-openshell-security-bulletin-august-2026)
- Independent criticism (XDA, 2026-04-03, run on a GB10 ThinkStation PGX): NemoClaw is safer than bare OpenClaw but does not fix prompt injection, because control and data plane are merged. A malicious skill can still exfiltrate through approved endpoints. The author also hit llama.cpp tool-calling incompatibility, permission bugs, and dashboard failures after overnight runs. [medium] (https://www.xda-developers.com/ran-nvidia-nemoclaw-openclaw-finally-safe-same-problems/)
- OpenShell collects anonymous operational telemetry by default. It can be disabled with OPENSHELL_TELEMETRY_ENABLED=false on the gateway. [high] (https://github.com/NVIDIA/OpenShell/blob/main/README.md)
- NemoClaw publishes a docs MCP server for coding agents, added to Claude Code with `claude mcp add --transport http fern-docs https://docs.nvidia.com/nemoclaw/_mcp/server`. A starter prompt and the `nemoclaw-user-guide` skill guide installation with a coding agent. [high] (docs/resources/agent-skills.mdx)


# REPORT: NVIDIA open model landscape (late 2026) for an always-on personal AI assistant: Nemotron 3 / 3.5 LLMs, vision/omni, embed/rerank, ASR/TTS, safety; licenses, run paths (Apple Silicon, RTX, build.nvidia.com, Nebius) and a recommended standard model pair

## Summary
The most important constraint is the hardware. The dev laptop is an Apple M1 Pro with 16 GB of unified memory, running macOS 27.0.1. It has Ollama 0.13.1 installed, and NemoClaw needs at least 0.32.9. That machine cannot run any 30B-class Nemotron locally, because those need about 24-25 GB at Q4 and Hermes' own Mac guide says 32 GB+. The only Nemotron LLM that fits locally is Nemotron 3 Nano 4B: about 2.8 GB at Q4 and 4.2 GB at Q8. The hackathon rules also require that the app 'runs on either Nebius Token Factory or Nebius AI Cloud' and uses at least one NVIDIA open source model. So the main agent model should be served from Nebius Token Factory, with build.nvidia.com (free trial key, roughly 40 RPM observed) used only for development. The current Nemotron line-up is: Nano 30B-A3B (Dec 2025), Nano 4B (Mar 2026), Super 120B-A12B (Mar 2026), Nano Omni 30B-A3B for vision, audio and video (Apr 2026), Ultra 550B-A55B (Jun 2026), and Nemotron 3.5 Lightning 30B-A3B (Aug 11, 2026), which is the newest general LLM. NVIDIA positions Lightning explicitly as 'the execution layer for always-on agents' and says it works with OpenClaw, Hermes Agent and NemoClaw. On NVIDIA's own card it scores PinchBench 85.4, ahead of Super (80.4) and Nano (66.1), and BrowseComp 37.0 vs Super's 22.8. On Nebius it costs $0.06/$0.24 per 1M tokens at about 314 tok/s with 1M context, vs Super at $0.30/$0.90, about 127 tok/s and 256K. Super is still clearly stronger on Terminal-Bench (39.6 vs 24.6), SWE-bench Verified (63.1 vs 51.6) and long-context AA-LCR (58.4 vs 52.0). Super is also the shared default that NemoClaw validates for both OpenClaw and Hermes. Recommendation: standardize on Nemotron 3.5 Lightning via Nebius Token Factory (`nvidia/Nemotron-3_5-Lightning`) as the always-on executor, and Nemotron 3 Super (`nvidia/nemotron-3-super-120b-a12b`) as the planner/escalation model and known-good fallback. Optionally add Nano 4B on-device through Ollama for privacy-sensitive local steps such as PII redaction, triage and offline mode. On licenses: Lightning, Ultra, Nemotron-3-Embed, the 3.5 ASR and 3.5 Content-Safety models use the permissive OpenMDW-1.1. Nano, Super and Nano 4B stay on the NVIDIA Nemotron Open Model License, which allows commercial use and derivatives but requires attribution and has a litigation-termination clause. Omni, Magpie TTS and llama-nemotron-embed use the NVIDIA Open Model License. Supporting models: Nemotron-3-Embed-1B for memory, llama-nemotron-rerank-1b-v2, Nemotron-3.5-Content-Safety as a guard, Parakeet TDT 0.6B v3 for voice on the Mac via parakeet-mlx, and Magpie TTS. Most of the NeMo speech, TTS and safety models document Linux plus NVIDIA GPU only, so on this Mac they need a hosted or Nebius Serverless path. NemoClaw's default memory embedder is qwen3-embedding:0.6b, not an NVIDIA model.

## Platform requirements
THIS DEV MAC (Apple M1 Pro, 16 GB, macOS 27.0.1):
- Locally, use only Nemotron 3 Nano 4B. Ollama tags: `nemotron-3-nano:4b` (Q4, 2.8 GB) or `:4b-q8_0` (4.2 GB). Alternatively llama.cpp `-hf nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF:Q4_K_M`. Keep context modest (16–32K), because NemoClaw's Colima VM wants about 8 GB on top of macOS.
- Upgrade Ollama first with `brew upgrade ollama`. The installed version is 0.13.1. NemoClaw needs at least 0.32.9, and Lightning or Nemotron 3 architecture support needs 0.32.9+. Latest stable is 0.35.0.
- Voice on the Mac: `pip install parakeet-mlx` (parakeet-tdt-0.6b-v3).

LOCAL MEMORY NEEDS FOR LARGER MODELS:
- Nano 30B / Lightning 30B-A3B: at least a 32 GB Mac (Q4 24–25 GB; MLX tag 23 GB with 256K context) or a 36–48 GB Mac for comfort.
- Super 120B: 96 GB+ (Ollama Q4 is 87 GB).
- Ultra: data-center only (8x B200).

RTX GPUs:
- Nano 4B: any 8 GB+ card.
- Lightning / Nano 30B: RTX 5090 32 GB, either Q4_K_M at 25 GB or NVFP4 at 23 GB (NVFP4 needs Blackwell). A 24 GB card (3090/4090) needs partial MoE offload.
- Nano Omni: NVFP4 21 GB, minimum RTX 5090.
- Super: RTX PRO 6000 96 GB or 2x H100 (FP8).

HOSTED:
- build.nvidia.com: free nvapi- key, trial terms, about 40 RPM observed. Use for development only.
- Nebius Token Factory: NEBIUS_API_KEY, base https://api.tokenfactory.nebius.com/v1/, baseline 60 RPM / 400K TPM. Hosts Lightning, Super, Ultra and Nano 30B. This is the path that satisfies the hackathon's 'runs on Nebius' rule.
- Nebius Serverless endpoints (vLLM container on L40S/H100; per-second Compute billing): for models that are not in Token Factory, such as Nemotron-3-Embed-1B, Nano Omni FP8 (needs an L40S 48 GB) and NeMo speech/TTS. Use a vLLM image newer than the tutorial's v0.18.0, e.g. v0.27.1 per the Lightning card.

OS NOTES: The NeMo ASR, TTS and safety model cards document Linux plus NVIDIA GPU only.

## Integration notes
RECOMMENDED STANDARD PAIR:
(1) Nemotron 3.5 Lightning as the always-on executor.
- Nebius ID `nvidia/Nemotron-3_5-Lightning`; build.nvidia.com ID `nvidia/nemotron-3.5-lightning-30b-a3b`; Ollama `nemotron-3.5-lightning`.
(2) Nemotron 3 Super as the planner/escalation model and known-good fallback.
- Nebius and build.nvidia.com ID `nvidia/nemotron-3-super-120b-a12b`. It is the NemoClaw-validated default for both OpenClaw and Hermes.
Optional (3): Nemotron 3 Nano 4B locally via Ollama (`nemotron-3-nano:4b`) for on-device privacy steps.

HERMES AGENT:
- Put NEBIUS_API_KEY=... in ~/.hermes/.env.
- Run `hermes chat --provider nebius --model nvidia/Nemotron-3_5-Lightning`, or set it in config.yaml: `model: {provider: "nebius-token-factory", default: "nvidia/Nemotron-3_5-Lightning"}`.
- For fast turns, add `extra_body: {chat_template_kwargs: {enable_thinking: false}}`.
- Dev alternative: NVIDIA_API_KEY in ~/.hermes/.env, then `hermes chat --provider nvidia --model nvidia/nemotron-3.5-lightning-30b-a3b`.
- Local: `ollama launch hermes --model nemotron-3-nano:4b`. This follows the pattern on Ollama's nemotron-3-nano page; it has not been tested on 4B.
- Hermes has fallback-provider support, which can point at Super.

NEMOCLAW, path A (NVIDIA Endpoints): `NVIDIA_INFERENCE_API_KEY=nvapi-... nemoclaw onboard`, then pick NVIDIA Endpoints. Super is the default. This path does not satisfy the Nebius rule.

NEMOCLAW, path B (Nebius Token Factory as a custom endpoint; untested combination):
```
NEMOCLAW_PROVIDER=custom NEMOCLAW_ENDPOINT_URL=https://api.tokenfactory.nebius.com/v1 NEMOCLAW_MODEL=nvidia/Nemotron-3_5-Lightning COMPATIBLE_API_KEY=$NEBIUS_API_KEY nemoclaw onboard --non-interactive
```
- Onboarding validates structured tool calls and streaming.
- NEMOCLAW_REASONING_EFFORT maps to `reasoning_effort`, not to Nemotron's `chat_template_kwargs.enable_thinking`. Verify how Token Factory handles reasoning before relying on it.

NEMOCLAW, path C (local Ollama on the 16 GB Mac): `brew upgrade ollama`, then `nemoclaw onboard` and choose Ollama. NemoClaw's validated Nemotron Ollama model is nemotron-3-nano:30b, which will not fit in 16 GB. Nano 4B is unvalidated and has to pass the strict tool-call probe.

DIRECT SDK:
```
OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/", api_key=os.environ["NEBIUS_API_KEY"]).chat.completions.create(model="nvidia/Nemotron-3_5-Lightning", messages=..., tools=..., temperature=0.6, top_p=0.95, extra_body={"chat_template_kwargs": {"enable_thinking": False}})
```
- For Super with OpenClaw-style many-tool prompts, consider `chat_template_kwargs: {"force_nonempty_content": True}`.

SELF-HOSTING ON NEBIUS SERVERLESS (vLLM flags from the model cards):
- Lightning: `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser nemotron_v3` (vLLM v0.27.1).
- Nano 30B / Nano 4B: `--tool-call-parser qwen3_coder --reasoning-parser nano_v3`.
- Omni: `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser nemotron_v3 --trust-remote-code --max-model-len 131072 --video-pruning-rate 0.5` (vLLM >=0.20).
- Example: `nebius ai endpoint create --name nemo-embed --image vllm/vllm-openai:v0.27.1 --container-command "python3 -m vllm.entrypoints.openai.api_server" --args "--model nvidia/Nemotron-3-Embed-1B-BF16 --host 0.0.0.0 --port 8000" --platform gpu-l40s-a --preset 1gpu-8vcpu-32gb --public --container-port 8000 --auth token --token $AUTH_TOKEN --subnet-id $SUBNET_ID`. This is adapted from the Nebius tutorial and has not been run.

MEMORY / RAG: NemoClaw/OpenClaw memory search defaults to qwen3-embedding:0.6b on host Ollama. To use an NVIDIA embedder:
- Nemotron-3-Embed-1B through build.nvidia.com `nvidia/nemotron-3-embed-1b` (dev) or a Nebius Serverless vLLM endpoint.
- Use the 'query: ' and 'passage: ' prefixes.

GUARD: Nemotron-3.5-Content-Safety (`nvidia/nemotron-3.5-content-safety` on build.nvidia.com, or vLLM `--served-model-name nemotron_moderator`) as an input/output moderation step.

VOICE: parakeet-mlx on the Mac for speech-to-text. Magpie TTS through its NIM or Nebius Serverless.

LICENSE HYGIENE: the repo itself must be Apache/MIT/MPL. Add a NOTICE file quoting 'Licensed by NVIDIA Corporation under the NVIDIA Nemotron Model License' if Super or Nano weights or derivatives are redistributed, and include an OpenMDW-1.1 copy for Lightning. Calling the model through an API without shipping the weights is lower risk.

## Risks
- The 16 GB M1 Pro cannot run Lightning, Nano 30B, Omni or Super locally. Any 'private/local' claim must rest on Nano 4B (BFCL v3 only 61.1) or on Nebius-hosted inference. Frame privacy as 'your Nebius tenant + NemoClaw/OpenShell policy + on-device redaction', not 'everything runs on my laptop'.
- Hackathon rule: the app must run on Nebius Token Factory or Nebius AI Cloud. Using build.nvidia.com or Ollama cloud tags as the production path could fail eligibility. build.nvidia.com is also a trial service (evaluation/prototyping terms, ~40 RPM observed, credit-limited).
- Nemotron 3.5 Lightning is only ~7 weeks old. It is not in NemoClaw's curated or validated lists, and the Lightning + Nebius + NemoClaw custom-endpoint combination is untested. Tool-call or reasoning-format quirks could eat days. Smoke-test it on day 1 and keep Super on NVIDIA Endpoints as a fallback.
- Reasoning tokens. All Nemotron 3 models think by default. Long reasoning can exhaust output budgets in agent loops, and NemoClaw has explicit retry logic for this. It is unknown whether Nebius Token Factory honors chat_template_kwargs (enable_thinking, low_effort, force_nonempty_content).
- Super, faced with many tool definitions, can return a tool call or empty content for plain chat (NemoClaw #1193, since fixed). Similar behavior may show up in Hermes or a custom harness.
- The local Ollama is 0.13.1, far below NemoClaw's 0.32.9 minimum, and the daemon is stopped. The Colima VM (about 8 GB) plus macOS plus a local model will squeeze 16 GB, causing swapping or OOM during demos.
- Model IDs differ by platform: nvidia/Nemotron-3_5-Lightning (Nebius), nvidia/nemotron-3.5-lightning-30b-a3b (build), nemotron-3.5-lightning (Ollama), nvidia/nemotron-nano-3-30b-a3b (build, Nano). Config typos will break onboarding validation.
- Vision and voice. Nano Omni is not in Token Factory's public catalog (Nebius says dedicated only). It needs a dedicated endpoint or a Nebius Serverless L40S 48 GB running vLLM >=0.20, which means cost, quota and cold-start risk. The NeMo ASR, TTS and safety models document Linux plus NVIDIA GPU only.
- Benchmark claims. NVIDIA's numbers are vendor-reported, and the Artificial Analysis index changed versions (Super shows 36.0 in June but 26 in v4.1.1). Don't mix numbers from different index versions in the pitch.
- Nebius Serverless GPU quota for new accounts (e.g., an L40S) may need an increase request. Endpoint creation takes about 5 minutes, plus model download time.

## Unknowns
- Whether Nebius Token Factory passes chat_template_kwargs (enable_thinking, low_effort, reasoning_budget, force_nonempty_content) through to Nemotron models, and whether it returns reasoning in a separate reasoning_content field.
- Nebius Token Factory data retention and logging policy for prompts and completions. The 'Data Lab: Import Chat Completions' page suggests logs may be retained. This matters for the privacy story.
- Whether nemotron-3-nano:4b (or an MLX variant) passes NemoClaw's strict Ollama tool-call validation on macOS, and its real tokens/sec on an M1 Pro.
- Whether NemoClaw's custom-endpoint path works cleanly with an authenticated remote HTTPS URL (https://api.tokenfactory.nebius.com/v1, no explicit port) under OpenShell egress policy on macOS.
- Exact build.nvidia.com rate limit and credit balance per model (NVIDIA does not publish them; ~40 RPM is community-observed).
- Whether Nemotron-3-Embed-1B runs acceptably on Apple MPS or CPU via sentence-transformers. Only Linux with A100/H100 is documented, and only a community GGUF exists.
- Nemotron 3 Nano Omni availability and pricing as a Token Factory dedicated endpoint.
- Exact Nebius Builder Program credit amounts, and L40S/H100 hourly prices for Serverless endpoints.
- Whether Magpie TTS and the Nemotron 3.5 ASR streaming model run on macOS at all. NeMo-Speech.cpp is mentioned for nemotron-speech-streaming-en but Mac support is unverified.
- Whether judges will treat the hosted Nebius model plus local Nano 4B as 'keeping your data under your control'. This depends on the judges' interpretation and is not specified in the rules.

## Facts
- Developer laptop is an Apple M1 Pro with 16 GB unified memory (hw.memsize=17179869184), 8 cores, macOS 27.0.1, ~134 GB free disk; Ollama CLI 0.13.1 is installed (daemon not running); llama-server and mlx_lm are not installed; iogpu.wired_limit_mb=0 (default GPU memory cap). [high] (Local commands run on the dev machine: sysctl machdep.cpu.brand_string hw.memsize; sw_vers; ollama --version; df -h)
- Hackathon rules: the project must use at least one NVIDIA open source model and 'Entrants must create a working software application that runs on either Nebius Token Factory or Nebius AI Cloud'. Submission period is Aug 26 – Oct 30, 2026. Video must be under 3 minutes and public on YouTube. The project must be free to access for testing. The four judging criteria are equally weighted. Credits come via the Nebius Builder Program. The code repo must be Apache 2.0, MIT or MPL 2.0. [high] (https://nebiusglobalaihackathon.devpost.com/rules ; https://nebiusglobalaihackathon.devpost.com/)
- Nemotron 3.5 Lightning: HF IDs nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16, -NVFP4, -Base-BF16, plus the speculative-decoding drafters -NVFP4-DSpark and -NVFP4-DFlash. 30B total / 3B active (Artificial Analysis says 31.6B/3.6B). Hybrid Mamba-2 + MoE + attention with MTP. Context up to 1M (256K on a single H100). Released Aug 11, 2026 under OpenMDW-1.1. Reasoning is toggled with chat_template_kwargs enable_thinking=True/False. vLLM image vllm/vllm-openai:v0.27.1 with flags `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser nemotron_v3` (the SGLang reasoning parser is nemotron_3). Recommended sampling is temperature 1.0, top_p 0.95. No official FP8 checkpoint. [high] (https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 (README raw + HF API license metadata); https://huggingface.co/api/models?author=nvidia&search=Nemotron-3.5)
- NVIDIA positions Lightning as the execution layer of autonomous, always-on agents: it handles tool calls, result validation and high-volume requests. NVIDIA says it is compatible with OpenClaw, Hermes Agent and NemoClaw, and recommends pairing it with a frontier reasoning model such as Nemotron 3 Ultra for planning, routed via NeMo Switchyard. It is available on build.nvidia.com, OpenRouter (free tier), Hugging Face and multiple inference providers. [high] (https://developer.nvidia.com/blog/nvidia-nemotron-3-5-lightning-delivers-fast-accurate-specialized-task-execution-for-long-running-agents/)
- Vendor benchmark table on the Lightning card (Lightning / Nemotron 3 Nano / Nemotron 3 Super / Qwen3.6-35B-A3B): PinchBench 85.37 / 66.11 / 80.36 / 88.07; Terminal-Bench 2.1 24.58 / 8.29 / 39.61 / 44.38; SWE-bench Verified 51.56 / 34.08 / 63.08 / 70.12; BrowseComp 36.97 / 13.74 / 22.77 / 48.74; tau3-bench Banking 9.28 / 7.01 / 12.37 / 10.52; GDPval-AA-V2 832 / 473 / 746 / 1015; IFBench 71.88 / 72.17 / 71.92 / 63.71; AA-LCR 52.00 / 32.75 / 58.44 / 61.06. [high] (https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 (benchmark table))
- Artificial Analysis (Index v4.1.1): Lightning scores 24, Nemotron 3 Nano 15, Nemotron 3 Super 26, gpt-oss-120b 24. Lightning ran at ~670 tok/s on a pre-release DeepInfra endpoint and took ~0.5 min per index task vs ~3.5 min for Qwen3.6 35B. A June article on an older index version gives Ultra 47.7 and Super 36.0, so the two sets of numbers are not comparable. [medium] (https://artificialanalysis.ai/articles/nemotron-3-5-lightning-launch ; https://artificialanalysis.ai/articles/nvidia-nemotron-3-ultra-released)
- Nemotron 3 Super: HF IDs nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16, -FP8, -NVFP4 and -Base-BF16, plus Nemotron-3-Super-120B-A12B-BF16-MTPv2. 120B total / 12B active, LatentMoE (Mamba-2 + MoE + attention) with MTP. Context up to 1M (256K default; 1M needs VLLM_ALLOW_LONG_MAX_MODEL_LEN=1). Released Mar 11, 2026 under the NVIDIA Nemotron Open Model License. chat_template_kwargs: enable_thinking, low_effort, reasoning_budget; force_nonempty_content=True is recommended for coding agents. vLLM/SGLang `--tool-call-parser qwen3_coder`. Sampling temperature 1.0, top_p 0.95. FP8 needs at least 2x H100-80GB or a single B200/B300. [high] (https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8 ; https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-super-120b-a12b)
- Nemotron 3 Nano 30B-A3B: HF IDs nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16, -FP8, -NVFP4 and -Base-BF16. 30B total / 3.5B active. 23 Mamba-2/MoE layers + 6 attention layers, 128 experts + 1 shared, 6 active per token. Context up to 1M (256K default). Released Dec 15, 2025 under the NVIDIA Nemotron Open Model License. enable_thinking defaults to True. Flags: `--tool-call-parser qwen3_coder --reasoning-parser nano_v3`. Tool-calling sampling temperature 0.6, top_p 0.95. [high] (https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16)
- Nemotron 3 Nano 4B: HF IDs nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16, -FP8 and -GGUF (Q4_K_M is 2.84 GB). 3.97B-parameter hybrid Mamba-2 + MLP with 4 attention layers, compressed from Nemotron-Nano-9B-v2. 262K context. Released Mar 16, 2026 under the NVIDIA Nemotron Open Model License. Reasoning-off scores: BFCL v3 61.1, IFEval 88.0, RULER-128k 91.1. Needs vLLM >=0.15.1. llama.cpp: `llama-server -hf nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF:Q4_K_M -c 0 -ngl 999`. [high] (https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16 ; https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF)
- Nemotron 3 Ultra: HF IDs nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16, -NVFP4 and -Base-BF16. 550B total / 55B active, 1M context. Released Jun 4, 2026 under OpenMDW-1.1. Needs at least 8x B200 (BF16). Reasoning toggles: enable_thinking and medium_effort. Tool parser qwen3_coder. Vendor scores: SWE-bench Verified 70.7, Terminal-Bench 2.1 56.4. LangChain Deep Agents Code uses it as its NemoClaw default. [high] (https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16 ; https://docs.nvidia.com/nemoclaw/user-guide/openclaw/inference/learn-and-choose/choose-model.md)
- Nemotron 3 Nano Omni: HF IDs nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 (62 GB), -FP8 (33 GB, minimum 1x L40S 48GB) and -NVFP4 (21 GB, minimum 1x RTX 5090). 31B total / ~3B active, 256K context. Input is video (up to 2 min), audio (up to 1 h), image and text; output is text only. Released Apr 28, 2026 under the NVIDIA Open Model Agreement. Supports tool calling (qwen3_coder) and reasoning parser nemotron_v3; needs vLLM >=0.20.0. The NemoClaw community DGX Spark tutorial says it 'is not designed to be the main driver for openclaw' and uses it as a vision subagent. [high] (https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 ; https://blogs.nvidia.com/blog/nemotron-3-nano-omni-multimodal-ai-agents/ ; https://nvidia.github.io/nemoclaw-community/examples/demos/field/build-a-claw-tutorial/)
- Ollama tags. nemotron-3.5-lightning: :latest / :30b-a3b-q4_K_M 25GB (1M ctx), :30b-a3b-mlx 23GB (256K), :30b-a3b-nvfp4 23GB, :30b-a3b-mxfp8 34GB, :30b-a3b-q8_0 35GB, :30b-a3b-bf16 66GB. nemotron-3-nano: :4b 2.8GB, :4b-q8_0 4.2GB, :4b-bf16 8.0GB (256K), :30b 24GB, :30b-a3b-q8_0 34GB. nemotron-3-super: :120b 87GB (q4_K_M), :cloud. nemotron3:33b is Nano Omni, 28GB, 128K, text+image. nemotron-3-ultra is cloud only. The Lightning and Nano pages list launch commands such as `ollama launch hermes --model nemotron-3.5-lightning` and `ollama launch openclaw --model nemotron-3-nano`. [high] (https://ollama.com/library/nemotron-3.5-lightning/tags ; https://ollama.com/library/nemotron-3-nano/tags ; https://ollama.com/library/nemotron-3-super/tags ; https://ollama.com/library/nemotron3)
- Ollama release history: v0.13.4 (2025-12-13) added Nemotron 3 Nano. v0.18.0 added nemotron-3-super:cloud; running it locally 'requires 96GB+ of VRAM'. v0.19.0 (2026-03-27) introduced MLX on Apple Silicon as a preview. v0.32.9 (2026-08-11) added Nemotron 3.5 Lightning and the Nemotron 3 architecture. v0.34.3 added Nemotron H vision on MLX. v0.40.0-rc0 makes MLX the default on Apple Silicon. Latest stable is v0.35.0 (2026-09-28). [high] (https://api.github.com/repos/ollama/ollama/releases)
- NemoClaw's Ollama path requires Ollama >=0.32.9 (older versions return tool calls as text). On macOS the upgrade is `brew upgrade ollama`. Validated Ollama defaults are qwen3.6:35b (high VRAM), nemotron-3-nano:30b (medium) and qwen3.5:9b (low). Onboarding stops if the model returns no structured tool call, and it retries with 1024/4096 output tokens when reasoning uses up the budget. [high] (https://docs.nvidia.com/nemoclaw/user-guide/openclaw/inference/local-inference/set-up-ollama.md ; https://docs.nvidia.com/nemoclaw/user-guide/openclaw/inference/learn-and-choose/choose-inference-provider)
- NemoClaw on NVIDIA Endpoints: 'Nemotron 3 Super remains the shared default for OpenClaw and Hermes'. The bundled fallback models are nvidia/nemotron-3-ultra-550b-a55b and nvidia/nemotron-3-super-120b-a12b. The credential is NVIDIA_INFERENCE_API_KEY (nvapi- prefix). Validation uses /v1/chat/completions only. [high] (https://docs.nvidia.com/nemoclaw/user-guide/openclaw/inference/learn-and-choose/choose-model.md ; https://docs.nvidia.com/nemoclaw/user-guide/openclaw/inference/hosted-inference/use-nvidia-endpoints.md)
- NemoClaw custom OpenAI-compatible endpoint, non-interactive setup: NEMOCLAW_PROVIDER=custom, NEMOCLAW_ENDPOINT_URL=<base>/v1, NEMOCLAW_MODEL=<id>, COMPATIBLE_API_KEY=<key>, then `nemoclaw onboard --non-interactive`. NEMOCLAW_REASONING_EFFORT writes extra_body.reasoning_effort, which is not the chat_template_kwargs switch that Nemotron uses. [high] (https://docs.nvidia.com/nemoclaw/user-guide/openclaw/inference/custom-endpoints/set-up-openai-compatible-endpoint.md)
- NemoClaw memory search guide uses qwen3-embedding:0.6b on a separate host Ollama container (port 8000), configured with OpenClaw 2026.9.1 keys models.providers.<name>, memory.search.enabled, memory.search.provider, memory.search.model and memory.search.fallback. No NVIDIA embedding model is the documented default. [high] (https://docs.nvidia.com/nemoclaw/user-guide/openclaw/configure-agents/configure-memory-search.md)
- NemoClaw on macOS (Apple Silicon) is 'Tested with limitations'. It needs Colima or Docker Desktop, e.g. `colima start --cpu 4 --memory 8`. Host RAM minimum is 8 GB, 16 GB recommended. On a 16 GB Mac that VM plus macOS leaves room only for a small local model. [high] (https://docs.nvidia.com/nemoclaw/user-guide/openclaw/get-started/prerequisites.md)
- Live build.nvidia.com model IDs (GET https://integrate.api.nvidia.com/v1/models): nvidia/nemotron-3.5-lightning-30b-a3b, nvidia/nemotron-3-super-120b-a12b, nvidia/nemotron-3-ultra-550b-a55b, nvidia/nemotron-nano-3-30b-a3b (note the odd naming), nvidia/nemotron-3-nano-omni-30b-a3b-reasoning, nvidia/nemotron-3-embed-1b, nvidia/llama-nemotron-embed-vl-1b-v2, nvidia/nemotron-3.5-content-safety, nvidia/llama-3.1-nemotron-safety-guard-8b-v3, nvidia/llama-3.1-nemoguard-8b-topic-control, nvidia/nemotron-parse-2.0. [high] (https://integrate.api.nvidia.com/v1/models (fetched live))
- build.nvidia.com free tier: a developer-program API key (nvapi-) with about 1,000 starter credits. The ~40 RPM limit is community-observed, not published; NVIDIA says limits vary by model and traffic, and there is no forum path to raise them. The service is a trial governed by the NVIDIA API Trial Terms, meant for evaluation and prototyping. [medium] (https://forums.developer.nvidia.com/t/request-for-nvidia-build-api-rate-limit-increase-to-300-rpm-business-use/383589 ; https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-super-120b-a12b ; https://news.creeta.com/en/nvidia-nim-free-tier-limits-2026/)
- Nebius Token Factory public catalog (Nemotron entries; prices per 1M tokens input/output):
- nvidia/Nemotron-3_5-Lightning: $0.06/$0.24, 1,048,576 max_model_len, bf16, ~314 tok/s, eu-north1, OpenMDW-1.1.
- nvidia/nemotron-3-super-120b-a12b: $0.30/$0.90, 262,144, fp4, ~127 tok/s, us-central1.
- nvidia/Nemotron-3-Ultra-550b-a55b: $1/$3, 1M, fp4, ~523 tok/s.
- nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B: $0.06/$0.24, 262K, fp8, ~60 tok/s.
All list function_calling and responses_api. The only embedding model is Qwen/Qwen3-Embedding-8B (no NVIDIA embed, rerank, ASR or Omni in the public catalog). [high] (https://tokenfactory.nebius.com/api/public/models_info ; https://tokenfactory.nebius.com/model-catalog.md)
- Nebius Token Factory API: OpenAI-compatible base_url https://api.tokenfactory.nebius.com/v1/ with env NEBIUS_API_KEY. Dynamic rate limits start at a baseline of 60 RPM / 400K TPM, scale ×1.2 per 15-min window at ≥80% use, up to 20× base. Supports tool_choice auto or a named function. [high] (https://docs.tokenfactory.nebius.com/quickstart.md ; https://docs.tokenfactory.nebius.com/ai-models-inference/rate-limits.md ; https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling.md)
- Nebius Serverless AI endpoints run a container such as vllm/vllm-openai, which pulls the model from Hugging Face and exposes /v1/chat/completions. The tutorial uses image vllm/vllm-openai:v0.18.0-cu130 on an L40S (preset 1gpu-8vcpu-32gb) via `nebius ai endpoint create ... --platform gpu-l40s-a --auth token`. Billing follows Compute VM pricing per second, and stopped endpoints are not billed for compute. Note that v0.18 is older than the vLLM versions the Nemotron 3.5 / Omni cards require. [high] (https://docs.nebius.com/serverless/tutorials/deploy-model.md ; https://docs.nebius.com/serverless/pricing-quotas.md)
- Hermes Agent built-in providers include `nebius-token-factory` (aliases nebius, nebius-tf, tokenfactory; NEBIUS_API_KEY in ~/.hermes/.env) and `nvidia` (NVIDIA_API_KEY; NVIDIA_BASE_URL overrides for local NIM). Documented example: `hermes chat --provider nvidia --model nvidia/nemotron-3-super-120b-a12b`. The Nemotron reasoning toggle can be passed as extra_body: chat_template_kwargs: enable_thinking. [high] (https://hermes-agent.nousresearch.com/docs/integrations/providers)
- Hermes' Mac guide: 'For larger models (27B, 35B), you'll need 32 GB+ of unified memory. The 9B is the sweet spot for 8-16 GB machines.' [high] (https://hermes-agent.nousresearch.com/docs/guides/local-llm-on-mac)
- macOS caps GPU wired memory by default at roughly 2/3–3/4 of RAM. The undocumented `sudo sysctl iogpu.wired_limit_mb=<MB>` raises it. On a 16 GB Mac that leaves about 10–12 GB for model plus KV cache. [medium] (https://llmconfigurator.com/en/guides/troubleshooting/increase-metal-vram-limit-apple-silicon ; https://github.com/ivanopcode/devnote-override-macos-metal-vram-cap)
- Licenses from HF metadata. OpenMDW-1.1: Lightning, Ultra, Nemotron-3-Embed-1B/8B, llama-nemotron-rerank-1b-v2 (plus the Llama 3.2 license), nemotron-3.5-asr-streaming-0.6b, Nemotron-3-Diarization, and Nemotron-3.5-Content-Safety (plus Gemma terms). NVIDIA Nemotron Open Model License: Nano 30B, Nano 4B, Super, and Nemotron-3-Content-Safety (plus Gemma terms). NVIDIA Open Model Agreement/License: Nano Omni, llama-nemotron-embed-1b-v2 (plus Llama 3.2), llama-nemotron-embed-vl/rerank-vl, magpie_tts_multilingual_357m, nemotron-speech-streaming-en-0.6b. CC-BY-4.0: parakeet-tdt-0.6b-v3, canary-1b-v2, canary-qwen-2.5b. llama-embed-nemotron-8b is non-commercial only. [high] (https://huggingface.co/api/models/nvidia/<id> (cardData.license_name for each); https://huggingface.co/nvidia/llama-embed-nemotron-8b)
- The NVIDIA Nemotron Open Model License (Dec 15, 2025) allows commercial use and derivative works, and NVIDIA claims no ownership of outputs. Redistribution must include a license copy and the notice 'Licensed by NVIDIA Corporation under the NVIDIA Nemotron Model License'. Rights terminate if you sue alleging patent or copyright infringement. OpenMDW-1.1 (Linux Foundation, May 28, 2026) is permissive: it requires only a license copy and notices, places no restrictions on outputs, and has a similar litigation termination clause. NVIDIA adopted OpenMDW for future releases; Nano and Super were not relicensed. [high] (https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-nemotron-open-model-license/ ; https://openmdw.ai/license/1-1/ ; https://www.linuxfoundation.org/press/linux-foundation-releases-openmdw-1.1-nvidia-adopts-openmdw-for-cosmos-isaac-gr00t-ising-and-nemotron-ai-model-families)
- Nemotron-3-Embed-1B-BF16: 1.14B parameters (pruned and distilled from Ministral-3-3B), 2048-dim embeddings sliceable with L2 re-normalization, 32,768-token sequence, 34 languages, released Jul 16, 2026. Requires 'query: ' and 'passage: ' prefixes. Runs via sentence-transformers or `vllm serve nvidia/Nemotron-3-Embed-1B-BF16`. Tested on Linux with A100/H100 only. No official GGUF/Ollama; a community GGUF exists (NeoRoth/nemotron-3-embed-1b-gguf). Hosted on build.nvidia.com as nvidia/nemotron-3-embed-1b. [high] (https://huggingface.co/nvidia/Nemotron-3-Embed-1B-BF16 ; https://huggingface.co/NeoRoth/nemotron-3-embed-1b-gguf)
- llama-nemotron-embed-1b-v2: Matryoshka dimensions 384/512/768/1024/2048, 8192-token sequence, 26 languages, needs trust_remote_code. llama-nemotron-rerank-1b-v2: 8192 tokens, 26 languages, AutoModelForSequenceClassification with trust_remote_code. llama-nemotron-rerank-vl-1b-v2 adds image and page reranking. [high] (https://huggingface.co/nvidia/llama-nemotron-embed-1b-v2 ; https://huggingface.co/nvidia/llama-nemotron-rerank-1b-v2)
- ASR models:
- nvidia/nemotron-3.5-asr-streaming-0.6b: 600M, 40 locales, chunk sizes 80ms–1120ms, OpenMDW-1.1, released Jun 4, 2026. NeMo install `pip install git+https://github.com/NVIDIA/NeMo.git@main#egg=nemo_toolkit[asr]`. Linux NVIDIA GPU only.
- nvidia/parakeet-tdt-0.6b-v3: 25 European languages, average WER 6.34%, CC-BY-4.0. Runs on Apple Silicon via `pip install parakeet-mlx` with model mlx-community/parakeet-tdt-0.6b-v3, including streaming via transcribe_stream. [high] (https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b ; https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3 ; https://github.com/senstella/parakeet-mlx)
- TTS: nvidia/magpie_tts_multilingual_357m has 364M parameters, 12 languages and 5 voices (Aria, Jason, John Van Stan, Leo, Sofia). Latest version v2607 released Jul 21, 2026 under the NVIDIA Open Model License. Install with `pip install nemo_toolkit[tts]@main kaldialign`; API is MagpieTTSModel.from_pretrained(...).do_tts(text, language='en', apply_TN=False, speaker_index=4). Documented for NVIDIA GPUs on Linux; a NIM is on build.nvidia.com; Mac support is not documented. [high] (https://huggingface.co/nvidia/magpie_tts_multilingual_357m ; https://huggingface.co/blog/nvidia/magpie-tts-multilingual-voice-agents)
- Safety models:
- nvidia/Nemotron-3.5-Content-Safety: 4B (Gemma-3-4B-it + LoRA), text + single image, 12 languages, released Jun 2, 2026. Outputs 'User Safety', 'Response Safety' and a category list. Run with `vllm serve nvidia/Nemotron-3.5-Content-Safety --served-model-name nemotron_moderator`; hosted as nvidia/nemotron-3.5-content-safety. Does not explicitly cover prompt injection or tool-call safety.
- Nemotron-3-Content-Safety (Mar 2026) has 22 categories.
- Llama-3.1-Nemotron-Safety-Guard-8B-v3 covers 9 languages. [high] (https://huggingface.co/nvidia/Nemotron-3.5-Content-Safety ; https://huggingface.co/nvidia/Nemotron-3-Content-Safety ; https://huggingface.co/nvidia/Llama-3.1-Nemotron-Safety-Guard-8B-v3)
- Known issue: with OpenClaw sending 23 tool definitions, nvidia/nemotron-3-super-120b-a12b replied to simple chat with a tool call and returned empty content (payloads: []). NemoClaw issue #1193 (Mar 31, 2026) was closed via PR #2380. Related open issue #2733 says Ollama can leak tool calls as text and recommends vLLM with a parser flag. [medium] (https://github.com/NVIDIA/NemoClaw/issues/1193 ; https://github.com/NVIDIA/NemoClaw/issues/2733)
- Estimated Mac speed for Nemotron 3 Nano 30B Q4_K_M (~32 GB needed): about 24 tok/s on an M4 Pro 48GB and about 38 tok/s on an M4 Max. These are modeled estimates, not measurements, and none applies to a 16 GB machine. [low] (https://willitrunai.com/can-run/nemotron-3-nano-30b-on-m4-pro-48gb)


# REPORT: Competitive landscape for always-on private personal AI assistants (memory, skills, tool access), late 2026: open-source and commercial players, documented user pain, 5 gaps a 15-day team could own, and project ideas many teams will submit

## Summary
As of 2026-10-02, the open-source personal-agent space is dominated by OpenClaw (391k GitHub stars, release v2026.9.7 on Sep 30) and Hermes Agent (250.7k stars, release v2026.9.24). NVIDIA NemoClaw (alpha, tag v0.0.130, 22.6k stars) wraps OpenClaw, Hermes, LangChain Deep Agents and Pi inside OpenShell sandboxes (v0.1.2, Sep 28). Older second-brain tools have mostly stalled or pivoted: Reor is archived, Khoj's last release was a March 2026 beta, Open Interpreter moved to a Rust coding agent, and Letta's work moved to letta-code. AnythingLLM, Jan, LibreChat, Mem0 and n8n are active, but they are components or chat apps, not secure always-on agents.

Commercial always-on agents arrived in force in 2026: Grok Bot (Aug 11), Meta Muse (Sep 8, cloud "Muse Secure VM" with a Sentinel approval agent and an audit trail), Claude Cowork (memory shared with chat since Aug 25), Google CC (household version Sep 17), ChatGPT Pulse plus the "Dreaming" memory upgrade (Jun 4), and Gemini-backed Siri in iOS 27. Judges will ask "why not just use Muse or Cowork?", and the credible answer is verifiable local control, not features.

The evidence of user pain is strong and recent:
- **Security advisories:** OpenClaw has 722 GitHub advisories in Jan–Sep 2026 (14 critical, 249 high). SecurityScorecard found 40k+ exposed instances.
- **Malicious skills:** 341 found on ClawHub in February (most delivered Atomic Stealer on macOS) and 1,103 of 14,706 by March.
- **Destructive mistakes:** Summer Yue's inbox was bulk-deleted after compaction dropped her "don't act until I tell you" instruction.
- **Injection via message objects:** zero-click link-preview exfiltration and message-object injection (CSA and Imperva/Varonis, June 2026).
- **Runaway cost:** bills of $200–500/day reported; one overnight heartbeat run cost $18.75 on Opus.
- **Unreliable memory:** OpenClaw compaction loses context; Hermes has a 2,200-character MEMORY.md cap.

A June 2026 paper (MPBench, arXiv 2606.04329) measured memory-poisoning success at 66.67% on Hermes vs 34.25% on OpenClaw, and no existing prompt-injection defense caught these attacks reliably (best was 67.67% detection). SkillJack (Aug 2026) shows poisoned experiences turning into persistent skills.

The sponsors' own stack already covers a lot, so a project must avoid re-skinning it:
- Hermes has on/off memory and skill write approval, skill quarantine and scanning (NVIDIA SkillSpector), and a localhost dashboard with approval modes.
- OpenShell has deny-by-default egress, credential injection, hot-reload policies, OCSF audit export and gateway interceptors.
- NVIDIA's nemoclaw-community already ships a "Memory-Driven Chief of Staff" (email/Slack, source-backed memory, obligation ledger), a Chrome side-panel assistant, a sandboxed Hermes bot team, and a payment-ops human-release pattern.

The real gaps are where these pieces stop. OpenShell's proposed "Privacy Guard" for content-aware outbound scanning and its streaming DLP proposal were both closed as not_planned on 2026-09-21. Memory and skill write approval is a single global switch with no awareness of where content came from. OCSF audit is "best-effort, not a guarantee of complete audit history". There is no undo or compensating-action layer. Cost per goal is not attributed (open Hermes issues).

For the build:
- **Recommended position:** a provenance-aware "trust layer" on Hermes + NemoClaw/OpenShell, with sensitive work on a local or Nemotron path and Nebius serverless only for non-sensitive escalation. This owns a defensible niche.
- **Avoid:** morning briefings, inbox triage, chat-with-your-notes, Telegram calendar bots, multi-agent teams, and email/Slack chief-of-staff clones.

## Platform requirements
Where each landscape player runs (relevant to choosing your stack on an Apple Silicon Mac):

**OpenClaw**
- Local daemon or gateway on macOS, Linux, WSL2 or Windows, plus mobile apps.
- npm install needs Node 24.16+ or 26.1+.
- Host installs bind to loopback by default. Run `openclaw security audit` to check for drift.

**Hermes Agent**
- macOS, Linux, WSL2, native Windows, Termux.
- Install: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`.
- State lives in ~/.hermes/ (memories/, skills/, state.db).
- Dashboard at 127.0.0.1:9119.

**NemoClaw**
- Alpha, tag v0.0.130.
- macOS Apple Silicon is "tested with limitations":
  - Docker Desktop, or Colima (`brew install colima docker; colima start --cpu 4 --memory 8`).
  - Node.js 22.16+, npm 10+, Xcode Command Line Tools.
  - Minimum 4 vCPU / 8 GB RAM / 20 GB disk; recommended 16 GB RAM / 40 GB disk.
  - On macOS the OpenShell gateway uses the Docker driver.
- Historically on macOS (March 2026), cloud NIM inference worked but sandbox-to-host Ollama inference was broken. Current status is unverified, so test early.
- The NemoClaw press release lists RTX PCs, RTX PRO, DGX Spark and DGX Station for local Nemotron. On a Mac you will likely use cloud inference (NVIDIA Endpoints or an OpenAI-compatible endpoint such as Nebius) or a small Ollama model (`nemotron-3-nano:30b` is in the NemoClaw docs examples).

**OpenShell**
- v0.1.2: Linux, macOS on Apple Silicon, WSL2 (experimental).
- Telemetry can be disabled with `OPENSHELL_TELEMETRY_ENABLED=false`.

**Commercial competitors**
- Mostly cloud: Muse Secure VM, Grok Bot cloud computer, ChatGPT/Pulse, Gemini/CC, Lindy, Manus.
- Exceptions: Claude Cowork runs a local VM (reported July 2026 patch defaults to cloud), and Apple Siri uses on-device processing plus Private Cloud Compute.

**Third-party access constraints**
- Gmail restricted scopes are exempt from CASA only for personal use or testing.
- In Testing mode, Google refresh tokens expire after 7 days (plan re-consent before demo day) and there is a 100 test-user cap.
- Telegram Bot API is officially supported. WhatsApp QR-pairing bridges are likely unofficial (verify against WhatsApp terms before showing it in the demo).

## Integration notes
**How the landscape maps onto NemoClaw / OpenShell / Hermes / Nebius / Nemotron, and where a project plugs in**

1. **Base stack.**
   - Install command:
     ```
     curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_AGENT=hermes NEMOCLAW_SANDBOX_NAME=my-hermes bash
     ```
   - For a scripted demo, run it non-interactively with NEMOCLAW_NON_INTERACTIVE=1, NEMOCLAW_ACCEPT_THIRD_PARTY_SOFTWARE=1 and NVIDIA_INFERENCE_API_KEY.
   - Manage with `nemohermes my-hermes status | connect | dashboard-url --quiet` and `nemohermes launch my-hermes`.
   - Onboarding asks for inference provider, model, credential, sandbox name, optional Tavily and messaging channels, and a network policy tier. Channels take TELEGRAM_BOT_TOKEN, DISCORD_BOT_TOKEN, SLACK_BOT_TOKEN plus SLACK_APP_TOKEN, or MSTEAMS_* variables.

2. **Nemotron models.**
   - NVIDIA's Hermes+NemoClaw example uses `nvidia/nemotron-3-super-120b-a12b` via build.nvidia.com.
   - NemoClaw docs list `nemotron-3-nano:30b` as an Ollama option.
   - Plan: route sensitive or cheap work (heartbeats, cron, classification) to Nano, and escalate to Super on NVIDIA Endpoints or a Nebius Serverless OpenAI-compatible endpoint. Use the NemoClaw "OpenAI-compatible endpoint" provider option.
   - I did not verify this exact Nebius wiring; other research threads should confirm the Nebius endpoint URL and model IDs.

3. **Hermes hooks a project can extend.**
   - Memory settings:
     - `memory.provider` for a custom provider plugin.
     - `memory.write_approval` (on/off only).
     - `memory.memory_char_limit` (2200) and `memory.user_char_limit` (1375).
   - Skills:
     - `skills.write_approval` stages writes in ~/.hermes/pending/skills/.
     - Hub installs are quarantined and logged in skills/.hub/lock.json.
     - `/memory pending | approve | reject` commands manage the review queue.
   - Session history: ~/.hermes/state.db (SQLite FTS5).
   - Dashboard approval modes: ask, yolo, deny.
   - Optional NVIDIA SkillSpector / SkillEvaluator scans.

4. **OpenShell hooks.**
   - Deny-by-default YAML network policy with host, port, HTTP verb and binary rules. Policies hot-reload, and denied requests return 403 as tool failures.
   - Credential injection at egress: the agent never sees raw keys.
   - Audit export: `openshell settings set --global --key ocsf_json_enabled --value true`. This is per-line OCSF JSONL, and the docs call it best-effort.
   - Gateway interceptors: a gRPC service registered under `[[openshell.gateway.interceptors]]` that can enforce or patch sandbox policy changes (CreateSandbox, UpdateConfig) with `failure_policy = "fail_closed"`.
   - Content-aware egress scanning ("Privacy Guard") and streaming DLP were closed not_planned on 2026-09-21. A project would implement them itself, e.g., as an LLM/API proxy inside the allowed egress path or as a Hermes tool wrapper. I have not verified whether OpenShell "supervisor middleware" can inspect request bodies.

5. **Observability.** NVIDIA's example uses NeMo Relay plus Arize Phoenix traces (ATIF format). The nemoclaw-community tool `hermes-relay-tracing` exists and could feed an action-receipt UI.

6. **Do not duplicate NVIDIA recipes.** Memory-Driven Chief of Staff, Ask NemoClaw side panel, Sandboxed Hermes Bot Team and Payment Ops already exist in https://github.com/NVIDIA/nemoclaw-community/tree/main/examples/recipes/nvidia. Build on or cite them instead.

7. **Five gaps a 2-person team could credibly own in 15 days**

   **(1) Taint-aware least privilege ("trifecta breaker").**
   - Track per session whether untrusted content (email body, web page, vCard or contact, file from others) has entered context.
   - When tainted, hot-swap the OpenShell policy to a restrictive tier: no new egress hosts, no outbound sends without approval, no memory or skill writes.
   - Restore the normal tier only after user approval.
   - Demo: an email carrying a hidden injection that is blocked live, with the OpenShell 403 shown.
   - Evidence: Imperva message-object injection, Varonis agent phishing, CSA link-preview exfiltration, lethal trifecta. Nothing in Hermes or NemoClaw does session-level information-flow control today.

   **(2) Provenance-gated memory and skill firewall.**
   - A Hermes memory provider plus skill-write reviewer that tags every proposed write with its source: the user's own words vs tool output vs a tainted session.
   - Auto-approve user-originated writes; quarantine tainted ones with a diff UI.
   - Expire or rollback poisoned entries, including vector residue.
   - Evidence: MPBench (Hermes 66.67% attack success), SkillJack (80% persistence after deletion), and Hermes write_approval being a blunt on/off switch.

   **(3) Local content-aware egress DLP / privacy router.**
   - Classify and redact PII or secrets in outbound requests, including prompts to cloud LLMs (Nebius), with a local Nemotron Nano or regex+NER classifier.
   - Route sensitive prompts to local inference.
   - Show a "data that left my machine" ledger.
   - Evidence: OpenShell Privacy Guard and streaming DLP both closed not_planned; cloud-exposure history.

   **(4) Plain-language action receipts with undo.**
   - Join the Hermes tool-call log, OpenShell OCSF events and connector side effects into a signed, append-only timeline ("what my agent did overnight and why").
   - Classify actions as reversible or irreversible. Force confirmation on irreversible ones and pin that constraint so compaction cannot drop it.
   - Offer one-click compensating actions: Gmail trash to restore, calendar delete to recreate, file snapshots.
   - Evidence: Summer Yue's inbox deletion; OCSF best-effort; the browser recipe "does not undo actions"; Muse markets an audit trail as a differentiator.

   **(5) Cost and locality governor.**
   - Per-goal token and cost attribution and budgets, with heartbeat and cron calls forced to a local or cheap Nemotron.
   - Escalate to Nebius serverless only within budget and only for non-sensitive data. Add a kill switch.
   - Evidence: $200–500/day bills, the heartbeat anecdote, open Hermes issues #39250 and #11701.

   (1)–(4) combine naturally into one "trust layer" product. (5) is a strong secondary feature that showcases Nebius plus Nemotron.

## Risks
- Stack churn: NemoClaw is alpha with near-daily tags (v0.0.128 to v0.0.130 within days), OpenShell is v0.1.2 (Sep 28) and Hermes has weekly releases (v2026.9.24). Pin exact versions in the README, or the 'installs and runs consistently' judging criterion can fail.
- macOS is a second-class NemoClaw platform ('tested with limitations'). Local Ollama inference from inside the sandbox was broken on macOS as of March 2026. Validate local Nemotron inference on day 1, or plan for cloud inference (NVIDIA Endpoints or Nebius) on the Mac.
- Overlap with sponsor reference code: NVIDIA's nemoclaw-community already ships an email/Slack chief of staff with source-backed memory, a browser side panel, a sandboxed bot team and a human-release payment pattern. A project resembling these will look derivative unless it clearly extends them.
- Cliché saturation: morning briefings, inbox triage, second-brain RAG, Telegram calendar bots and multi-agent 'teams' will be submitted by many teams. Commercial products (Google CC, ChatGPT Pulse, Muse, Grok Bot, Cowork) already do these better.
- Overclaiming security: guardrail classifiers miss a lot (MPBench best detection 67.67%; Willison says 95% is not enough). A security-themed project should show deterministic enforcement (OpenShell policy denials, staged writes), not just an LLM judge, and should state its limits.
- Third-party terms: Gmail restricted scopes are fine for personal use or testing, but Testing-mode refresh tokens expire after 7 days (re-consent before recording the video). WhatsApp QR-bridge integrations may violate WhatsApp terms. Prefer Telegram Bot API, Google APIs under personal use, or IMAP with app passwords.
- Demo reproducibility: an always-on agent needs a persistent host. On a laptop, sleep or lid-close breaks 'always-on'. Decide early between the Mac with caffeinate/launchd, a small cloud VM, or Nebius for the always-on part.
- Cost: a cloud Nemotron Super or frontier model with frequent heartbeats can burn credits quickly during development. Use small or local models for loops and cache aggressively.
- Hermes has had 2026 CVEs in skills and code-execution paths (some reportedly without vendor response), so stay on the latest release. Any skill you write may be judged on its own security.
- Security demos need realistic attack fixtures (injected email, poisoned vCard, malicious skill) built safely. Do not ship real malware samples, and keep the red-team payloads benign (e.g., exfiltration to a local canary endpoint).

## Unknowns
- I could not reach the exact hackathon page (name, deadline, judging weights, and whether NemoClaw/OpenShell/Hermes/Nebius use is mandatory or illustrative). The Nebius x NVIDIA Global AI Hackathon (Aug 26 – Oct 30, 2026, Devpost) is a low-confidence match.
- Whether NemoClaw on macOS Apple Silicon can now reach host-side Ollama or local Nemotron from inside the OpenShell sandbox (issue #260 is from March 2026 and closed; current behavior not re-tested).
- Whether OpenShell 'supervisor middleware' (docs/extensibility/supervisor-middleware) can inspect or modify HTTP request bodies; this determines whether egress DLP can live inside OpenShell or must be a proxy or tool wrapper.
- Which Hermes version the MPBench paper used for the 66.67% figure (the paper references OpenClaw v2026.3.38). Newer Hermes releases may have changed memory-write behavior.
- Exact Nebius Serverless endpoint compatibility with NemoClaw's 'OpenAI-compatible endpoint' provider, and which Nemotron model IDs Nebius serves (left to other research threads).
- Details of Meta Muse, Grok Bot, the Claude Cowork 'ShareRoot' sandbox escape and Gemini-backed Siri come from secondary press; primary vendor pages were not fetched. Treat specifics as medium confidence.
- Whether Hermes's dashboard or the NemoClaw roadmap will soon ship provenance-aware memory gating, action undo or per-goal cost budgets, which would narrow gaps 2, 4 and 5. Roadmaps were not checked.
- The SecurityScorecard exposure counts and the RankClaw 1,103-malicious-skills figure come from secondary sources and were not checked against the original reports.
- Whether ChatGPT Pulse has expanded beyond Pro/mobile in 2026, and whether OpenAI will ship its reported always-on agent before judging.

## Facts
- OpenClaw has 391,180 GitHub stars, latest release v2026.9.7 published 2026-09-30; installs via `curl -fsSL https://openclaw.ai/install.sh | bash` (macOS/Linux/WSL2) or `npm install -g openclaw@latest` (Node 24.16+ or 26.1+); runs locally with 20+ chat channels; state, memory, credentials stored on user hardware [high] (https://github.com/openclaw/openclaw (GitHub API queried 2026-10-02))
- OpenClaw repository has 722 published GitHub security advisories Jan–Sep 2026: 14 critical, 249 high, 390 medium, 69 low (peak Feb–Mar 2026 with 220 and 204 advisories respectively) [high] (GitHub API repos/openclaw/openclaw/security-advisories (queried 2026-10-02))
- CVE-2026-25253 (CVSS 8.8): OpenClaw accepted a gatewayUrl query parameter and auto-connected a WebSocket, leaking the auth token -> one-click RCE; fixed in 2026.1.29 (Jan 30, 2026) [high] (https://thehackernews.com/2026/02/openclaw-bug-enables-one-click-remote.html ; https://socradar.io/blog/cve-2026-25253-rce-openclaw-auth-token/)
- SecurityScorecard found 40,214 publicly exposed OpenClaw instances (28,663 IPs); 63% exploitable, 12,812 at RCE risk; default 0.0.0.0 bind blamed (current docs: host installs bind loopback, container images bind exposed with auth) [medium] (https://blog.rankiteo.com/ope1770630718-openclaw-vulnerability-february-2026/ ; https://docs.openclaw.ai/gateway/security)
- Koi Security audited 2,857 ClawHub skills and found 341 malicious (335 from one 'ClawHavoc' campaign) delivering Atomic macOS Stealer via fake 'prerequisites' shell commands; targets included API keys, SSH keys, browser passwords and ~/.clawdbot/.env [high] (https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html)
- RankClaw audit (March 2026) found 1,103 malicious skills among 14,706 ClawHub skills (7.5%); one account (hightower6eu) published 314 malicious skills with ~7,000 downloads [medium] (https://insiderllm.com/guides/openclaw-clawhub-security-alert/)
- OpenClaw partnered with VirusTotal to scan all skills uploaded to ClawHub [high] (https://thehackernews.com/2026/02/openclaw-integrates-virustotal-scanning.html)
- Gartner advised enterprises to immediately block OpenClaw downloads/traffic, calling it 'insecure by default' with plaintext credential storage and no enforced authentication [medium] (https://www.gartner.com/en/documents/7381830 ; https://www.csoonline.com/article/4129867/what-cisos-need-to-know-about-clawdbot-i-mean-moltbot-i-mean-openclaw.html)
- Moltbook (social network of OpenClaw agents) left its Supabase DB open: Wiz retrieved 1.5M agent API tokens, 35,000 emails and ~4,000 private DMs, some containing plaintext OpenAI keys (found Jan 31, 2026) [high] (https://www.govinfosecurity.com/moltbook-gave-everyone-control-every-ai-agent-a-30710)
- Meta alignment director Summer Yue's OpenClaw bulk-deleted her real inbox despite 'don't action until I tell you to'; the constraint was lost during context compaction and stop commands from her phone failed; she had to kill the process on her Mac mini (Feb 23, 2026) [high] (https://rits.shanghai.nyu.edu/ai/metas-alignment-director-lost-control-of-openclaw-it-deleted-her-inbox/)
- Imperva showed prompt injection via message objects (shared contacts, vCards, location pins) which, unlike web content, were not wrapped in untrusted-content markers (fixed in OpenClaw 2026.4.23); Varonis showed 'agent phishing' via believable emails leading to forwarding of mock AWS keys; mitigations: outbound-mail gates for unfamiliar addresses, connector segmentation, human approval for sensitive actions [high] (https://thehackernews.com/2026/06/new-attacks-trick-openclaw-ai-agent.html)
- CSA research note documents zero-click exfiltration via Telegram/Discord automatic link previews of attacker-constructed URLs, persistent control via poisoned SOUL.md/MEMORY.md that survives file revert because of vector-index residue, and skill supply-chain compromise [high] (https://labs.cloudsecurityalliance.org/research/csa-research-note-openclaw-indirect-prompt-injection/)
- MPBench paper: memory poisoning average attack success rate 66.67% on Hermes vs 34.25% on OpenClaw (OpenClaw v2026.3.38 referenced); retrieval success 64.70% vs 17.40%; off-the-shelf injection defenses fail (best, PromptArmor 70B guardrail: 67.67% TPR at 1% FPR; retraining didn't help) [high] (https://arxiv.org/abs/2606.04329 (PDF text verified))
- SkillJack: poisoned experiences converted into persistent skills in self-evolving agents (tested on SkillX and Anything2Skill, not Hermes): 56.2%/89.2% ASR, 80% persistence after deleting the original records, and safety detection drops from 98.5% on trajectories to 11.4% on extracted skills [high] (https://arxiv.org/abs/2608.03509)
- OpenClaw cost complaints: users report $200–500/day bills; a 30-minute heartbeat re-sending ~120k tokens of context cost ~$18.75 overnight on Claude Opus to answer 'is it daytime yet?' [medium] (https://clawdhost.net/blog/openclaw-api-costs-what-nobody-tells-you ; https://www.notebookcheck.net/18-75-overnight-to-ask-Is-it-daytime-yet-The-absurd-economics-of-OpenClaw-s-token-use.1219925.0.html)
- OpenClaw GitHub has ~4,085 issues mentioning 'compaction'. Examples: #3479 'Compaction always fails to generate summaries', #78367 'compaction storms', #45608 (open) memory flush before reset. #8081 'Multi-user permission management with RBAC' got 28 reactions; #48532 (open) on approval fatigue [high] (GitHub search API on openclaw/openclaw (queried 2026-10-02))
- Hermes Agent: 250,659 stars, MIT license, latest release v2026.9.24; install `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`; macOS/Linux/WSL2/native Windows/Termux; gateways for Telegram, Discord, Slack, WhatsApp, Signal; built-in cron; 7 terminal backends (local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox) [high] (https://github.com/NousResearch/hermes-agent (GitHub API queried 2026-10-02))
- Hermes memory: ~/.hermes/memories/MEMORY.md (2,200-char limit) and USER.md (1,375-char limit) are injected as a frozen snapshot at session start. Config keys: memory.memory_enabled, memory.user_profile_enabled, memory.memory_char_limit, memory.user_char_limit, memory.write_approval (default false). External providers include Honcho, OpenViking, Mem0, Holographic, RetainDB, ByteRover, Supermemory [high] (https://hermes-agent.nousresearch.com/docs/user-guide/features/memory ; https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory.md)
- Hermes has skills.write_approval (default false; when true, all skill_manage writes are staged under ~/.hermes/pending/skills/). Hub installs are quarantined, scanned and recorded in skills/.hub/lock.json; optional advisory scans via NVIDIA SkillEvaluator/SkillSpector [high] (https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md)
- Hermes CVEs assigned via VulDB in 2026 (none published as GitHub advisories): CVE-2026-10220 (injection/RCE in skills_tool, up to 2026.4.30), CVE-2026-9368 (code_execution sandbox issue), CVE-2026-9353 (skills_guard injection), CVE-2026-14625 (tui_gateway shell.exec protection bypass, up to 0.15.2) [medium] (https://www.sentinelone.com/vulnerability-database/cve-2026-10220/ ; https://advisories.gitlab.com/pypi/hermes-agent/CVE-2026-9353/)
- Hermes web dashboard runs at http://127.0.0.1:9119 with sessions browser, cron manager, live logs and approval modes (ask/yolo/deny); single-session-token auth (no multi-user) [medium] (https://www.contextstudios.ai/okf/en/blog/hermes-web-dashboard-the-agent-control-plane-has-arrived.md)
- Open Hermes feature requests show unmet needs: #5528 approval-locked command patterns (open), #39250 per-goal cost attribution (open), #11701 persistent usage/cost footer on gateway messages (open), #16462 first-invoke approval for MCP tools (open) [high] (GitHub search API on NousResearch/hermes-agent (queried 2026-10-02))
- NemoClaw announced at GTC on 2026-03-16 as a one-command install of Nemotron models plus the OpenShell runtime for OpenClaw. Jensen Huang: 'OpenClaw is the operating system for personal AI.' Listed hardware: GeForce RTX PCs/laptops, RTX PRO workstations, DGX Station, DGX Spark [high] (https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-NemoClaw-for-the-OpenClaw-Community/default.aspx)
- NemoClaw is alpha (tags up to v0.0.130, no GitHub releases, 22,637 stars). Supports OpenClaw (default), Hermes, LangChain Deep Agents Code and Pi (RC). Install: `curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash`. Inference options: local Ollama, vLLM, NVIDIA Endpoints, OpenRouter, OpenAI, Anthropic, Gemini, Model Router, OpenAI-compatible endpoints [high] (https://docs.nvidia.com/nemoclaw/latest/ ; https://github.com/NVIDIA/NemoClaw)
- NemoClaw with Hermes: `curl -fsSL https://www.nvidia.com/nemoclaw.sh | NEMOCLAW_AGENT=hermes NEMOCLAW_SANDBOX_NAME=my-hermes bash`. Non-interactive mode uses NEMOCLAW_NON_INTERACTIVE=1, NEMOCLAW_ACCEPT_THIRD_PARTY_SOFTWARE=1 and NVIDIA_INFERENCE_API_KEY. Management commands: `nemohermes my-hermes status`, `nemohermes launch my-hermes`, `nemohermes my-hermes connect` [high] (https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/get-started/quickstart)
- NemoClaw on macOS Apple Silicon is 'tested with limitations'. Requires Docker Desktop or Colima (`brew install colima docker && colima start --cpu 4 --memory 8`), Node.js 22.16+, npm 10+ and Xcode CLT. Minimum 4 vCPU / 8 GB RAM / 20 GB disk; recommended 16 GB / 40 GB [high] (https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/get-started/prerequisites)
- NemoClaw macOS tracking issue #260 (March 2026, now closed): cloud NIM inference worked, but local Ollama inference was broken inside the sandbox ('inference.local' missing from /etc/hosts) and Docker Model Runner was not bridged. Current status not re-verified [medium] (https://github.com/NVIDIA/NemoClaw/issues/260)
- OpenShell: 14,134 stars, Apache-2.0, latest v0.1.2 (2026-09-28); supports Linux, macOS on Apple Silicon and WSL2 (experimental). Install: `curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh`. Provides filesystem/network/process policy and credential injection only to approved endpoints [high] (https://github.com/NVIDIA/OpenShell (GitHub API queried 2026-10-02))
- OpenShell OCSF JSON audit export is enabled with `openshell settings set --global --key ocsf_json_enabled --value true`; docs state 'Collection is best-effort, not a guarantee of complete audit history' [high] (https://github.com/NVIDIA/OpenShell/blob/main/docs/observability/ocsf-json-export.mdx)
- OpenShell gateway interceptors: an external gRPC service, registered via [[openshell.gateway.interceptors]] in gateway TOML, can modify or validate allowlisted control-plane RPCs (e.g., CreateSandbox, UpdateConfig) in modify_operation/validate/post_commit phases. Data-plane traffic is not interceptable this way [high] (https://github.com/NVIDIA/OpenShell/blob/main/docs/extensibility/gateway-interceptors.mdx)
- OpenShell 'Privacy Guard' proposal (content-aware scanning of outbound sandbox traffic for PII/secrets before relay, issue #1043) and 'Zero-Latency DLP for SSE streaming in Privacy Router' (#2763) were both closed as not_planned on 2026-09-21 [high] (https://github.com/NVIDIA/OpenShell/issues/1043 ; https://github.com/NVIDIA/OpenShell/issues/2763)
- NVIDIA nemoclaw-community recipes already include: Memory-Driven Chief of Staff (email/Slack -> source-backed work wiki, obligation ledger, pins/ignores), Ask NemoClaw Chrome side panel, Sandboxed Hermes Bot Team, Payment Ops Hermes (human release authority outside the sandbox), PR Review Advisor, NV Tech Assistant. The 'hackathon' collection is empty [high] (https://github.com/NVIDIA/nemoclaw-community/tree/main/examples/recipes/nvidia)
- NVIDIA blog (June 2, 2026) shows Hermes plus NemoClaw doing product research across Outlook, Slack and GitHub with model nvidia/nemotron-3-super-120b-a12b, OpenShell pinned v0.0.38 in that example, unauthorized requests returning 403, and snapshot/restore excluding .env/token/secret files [high] (https://developer.nvidia.com/blog/deploy-self-evolving-agents-for-faster-more-secure-research-with-a-hermes-agent-and-nvidia-nemoclaw/)
- OpenClaw-alternative ecosystem (GitHub stars/latest release as of 2026-10-02): NanoClaw 30.9k (v2.4.0, container per conversation), ZeroClaw 32.9k (v0.8.5, Rust), nanobot 48.7k (v0.3.5, Python), IronClaw 12.6k (v1.4.1, 'AI never sees your passwords') [high] (GitHub API: qwibitai/nanoclaw, zeroclaw-labs/zeroclaw, HKUDS/nanobot, nearai/ironclaw ; https://composio.dev/blog/openclaw-alternatives)
- Older open-source assistants (as of 2026-10-02): Khoj 37.6k stars, AGPL, last release 2.0.0-beta.28 (2026-03-26), last push 2026-08-02 (slowing). Reor archived (read-only). Leon 17.6k, 2.0 rewrite on develop branch with no releases. Open Interpreter 68.5k, pivoted to a Rust coding agent (rust-v0.0.55). Letta 25k (core 0.16.8 May 2026; active work in letta-code v0.34.1) [high] (GitHub API for khoj-ai/khoj, reorproject/reor, leon-ai/leon, openinterpreter/open-interpreter, letta-ai/letta, letta-ai/letta-code)
- Active local-first building blocks: AnythingLLM 66.7k stars (v1.17.0, 2026-10-01; MCP, agent builder, memories, cron scheduled tasks, desktop and Docker). Jan 44.8k (v0.8.4; local OpenAI-compatible API at localhost:1337, MCP). Mem0 66.5k (library, self-hosted Docker server, or cloud; claims 92.5 LoCoMo / 94.4 LongMemEval). LibreChat 45.2k (v0.8.x added Agent Skills and subagents). n8n 206k (2.41.5) [high] (GitHub API queried 2026-10-02 ; https://github.com/Mintplex-Labs/anything-llm ; https://github.com/mem0ai/mem0 ; https://releasebot.io/updates/librechat)
- Screenpipe (21.8k stars) records screen and audio 24/7 locally (MIT core, paid app). Omi pendant ($25–50) is open hardware but processes audio in the cloud [medium] (https://screenpi.pe/compare/omi ; GitHub API mediar-ai/screenpipe)
- Peter Steinberger (OpenClaw creator) joined OpenAI in Feb 2026 to lead personal agents; OpenClaw moved to a foundation that OpenAI supports. As of late Sep 2026, OpenAI's always-on agent (reported 'Codex Bot') had no announced launch date [medium] (https://www.macstories.net/linked/openclaw-creator-peter-steinberger-joins-openai/ ; https://aiidelist.com/blog/openai-aeon-grok-bot-personal-agent-devday-2026)
- xAI Grok Bot launched 2026-08-11: always-on agents with their own cloud computer that sign into the user's tools, configurable approval rules for sends, deletes and purchases. All bots on an account share one cloud machine and credentials, and xAI says not to treat separate bots as security boundaries. Bundled with SuperGrok Heavy and Cursor Ultra [medium] (https://composio.dev/blog/guide-to-frok-bot ; https://blockchain.news/news/xai-launches-grok-bot)
- Meta Muse launched 2026-09-08 (US only; iOS, Android, muse.ai). Runs in a cloud 'Muse Secure VM' on the Muse Spark model; a separate 'Sentinel agent' must approve anything Muse sends to the internet. Claims a complete audit trail, no ad-system use of VM data, checkout via one-time Stripe Link cards, and a 'Confidential VM' later in 2026 [medium] (https://www.relevantaudience.com/ai/meta-muse-personal-ai-agent-launch/ ; https://www.etvbharat.com/amp/en/technology/meta-launches-muse-a-personal-ai-agent-that-can-handle-tasks-and-make-payments-for-you-enn26090901759)
- Claude Cowork runs tasks in an isolated VM on the user's computer with scheduled tasks. Memory was unified across chat and Cowork on 2026-08-25, on by default for Free/Pro/Max. PromptArmor showed file exfiltration via a hidden-text .docx 'skill' two days after launch (Jan 2026). A July 2026 'ShareRoot' sandbox escape on Mac was reported, and the patch defaulted execution to cloud [medium] (https://support.claude.com/articles/13345190 ; https://sdtimes.com/ai/anthropic-puts-persistent-memory-into-claude-cowork/ ; https://www.promptarmor.com/resources/claude-cowork-exfiltrates-files ; https://9to5mac.com/2026/07/27/claude-cowork-escaped-sandbox-on-mac-gain-full-access-to-all-files/)
- ChatGPT Pulse (launched Sep 2025, Pro mobile preview, off by default) builds overnight briefings from chats, memory and optional Gmail/Calendar connectors. OpenAI's 'Dreaming' memory (2026-06-04) curates memory in the background with an editable summary and claims factual recall up from 41.5% to 82.8% [medium] (https://www.eweek.com/news/openai-chatgpt-pulse/ ; https://www.pcworld.com/article/3158111/chatgpt-new-dreaming-feature-makes-it-way-better-at-remembering-you.html)
- Google: Gemini Personal Intelligence reasons across Gmail, Photos, YouTube and Search (US beta, early 2026). Google Labs CC sends a daily 'Your Day Ahead' email from Gmail/Calendar/Drive and expanded to a household agent for up to 6 members on 2026-09-17 [medium] (https://blog.google/innovation-and-ai/products/gemini-app/personal-intelligence/ ; https://www.computerworld.com/article/4107689/google-tests-an-ai-productivity-agent-that-lives-in-your-inbox.html ; https://wwwhatsnew.com/2026/05/20/google-daily-brief-agente-ia-resumen-matinal-gmail/)
- Apple (WWDC 2026-06-08): Siri AI in iOS/macOS 27 uses Apple Foundation Models built with Google Gemini, with personal-context processing on device and heavier work in Private Cloud Compute; developers get access only via App Intents, not a raw model endpoint; GA in fall 2026 [medium] (https://mer.vin/2026/06/apple-wwdc26-siri-ai-and-gemini-backed-foundation-models-on-device-and-private-cloud-compute/ ; https://letsdatascience.com/news/apple-unveils-gemini-powered-siri-and-ios-27-at-wwdc-2026-b757953c)
- Other commercial players: Lindy ($49.99/$99.99/$199.99 per month; iMessage access, inbox and meetings). Meta bought Manus (~$2B, Dec 2025) and some customers left over data trust. Meta acquired Limitless (Dec 2025); Rewind capture was disabled Dec 19 and data had to be exported or deleted. Grammarly rebranded as Superhuman with the Superhuman Go assistant. Shortwave offers an agentic Gmail client. Notion 3.0 has Custom Agents with memory. Microsoft Copilot has memory and Actions, and Recall became opt-in after a security backlash [medium] (https://www.wearefounders.uk/lindy-pricing-2026-every-plan-explained/ ; https://www.letsdatascience.com/news/meta-acquires-manus-triggering-customer-exodus-05fa2304 ; https://9to5mac.com/2025/12/05/rewind-limitless-meta-acquisition/ ; https://www.reworked.co/collaboration-productivity/grammarly-rebrands-as-superhuman-introduces-unified-ai-suite/ ; https://www.notion.com/releases/2025-09-18 ; https://support.microsoft.com/en-US/Privacy/microsoft-copilot/privacy-controls)
- Perplexity Comet: CometJacking (LayerX) used a crafted URL to exfiltrate memory and connected email/calendar data. Brave disclosed screenshot/hidden-text prompt injection; Perplexity initially rejected reports as having no security impact [high] (https://thehackernews.com/2025/10/cometjacking-one-click-can-turn.html ; https://bleepingcomputer.com/news/security/commetjacking-attack-tricks-comet-browser-into-stealing-emails)
- Cloud data-exposure precedents: 370,000+ Grok shared chats indexed by Google (Aug 2025); OpenAI ended the 'discoverable' ChatGPT shared-link experiment; a 2025 court preservation order required OpenAI to keep ChatGPT logs including deleted chats (later narrowed, so partly stale) [medium] (https://oecd.ai/en/incidents/2025-08-20-e91a ; https://www.malwarebytes.com/blog/news/2025/06/openai-forced-to-preserve-chatgpt-chats)
- Simon Willison's 'lethal trifecta': private-data access + exposure to untrusted content + an external communication channel lets attackers exfiltrate data. Guardrails catching '95%' are insufficient; once an agent has ingested untrusted input it must be constrained so that input cannot trigger consequential actions [high] (https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- OWASP Top 10 for Agentic Applications 2026 (published Dec 2025) lists ASI01 Agent Goal Hijack, with examples such as hidden instructions in emails, calendar invites and documents [medium] (https://www.giskard.ai/knowledge/owasp-top-10-for-agentic-application-2026)
- Google OAuth: restricted-scope apps (e.g., full Gmail read) need a CASA security assessment, except for personal use ('only user of your app or ... used by only a few users, all of whom are known personally to you') and apps in testing. In 'Testing' publishing status, refresh tokens expire after 7 days and there is a 100 test-user cap [high] (https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification ; https://www.unipile.com/google-oauth-refresh-token/)
- Prior hackathon outcomes in this space: SURGE x OpenClaw (lablab, Feb 4–Mar 1, 2026; 199 teams) was dominated by trading, DeFi and commerce agents. UCSC 'Hack-a-Claw' with NVIDIA/ASUS (May 15–16, 2026): the Best Use of NemoClaw winner was MonkeyClaw, a tool to probe and patch the NemoClaw ecosystem. Hermes Agent Hackathon had 187 submissions (1st place: Media Tool ffmpeg skill). DEV Hermes Agent Challenge (winners June 18, 2026) skewed to multi-agent teams [medium] (https://lablab.ai/ai-hackathons/openclaw-surge-hackathon/live ; https://news.ucsc.edu/2026/06/agentic-ai-first-uc-santa-cruz-hackathon-with-nvidia-asus/ ; https://dev.to/t/hermesagentchallenge)
- The most common OpenClaw/Hermes starter use cases are a morning briefing to Telegram (weather, calendar, tasks, news) and email triage. A Hermes community event in Gurugram on 2026-10-04 builds exactly an 'always-on assistant that checks inbox and calendar and sends a daily digest' [high] (https://www.kimi.ai/resources/openclaw-use-cases ; https://www.startupgrantsindia.com/events/hermes-comes-to-gurugram-set-up-your-24x7-personal-ai-assistant)
- Possible matching event: Nebius x NVIDIA Global AI Hackathon, online, Aug 26 – Oct 30, 2026, on Devpost, ~$50k prize pool. Tracks and 'Personal AI' problem statement not confirmed from the primary page [low] (https://www.startupgrantsindia.com/competitions/nebius-x-nvidia-global-ai-hackathon)
