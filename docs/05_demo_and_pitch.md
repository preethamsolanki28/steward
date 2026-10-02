# Steward: Demo and Pitch

## 1. 60-second demo script, click by click

The 60-second flow sits inside the ≤2:50 YouTube video, from 0:20 to 1:20. It is recorded on the M4 Pro (24 GB), starting from `make demo-reset && make up`. All seed data is synthetic and uses `.example` domains. Video work is owned by T5.4 (E1 4h + E2 4h), Day 11–13.

### Recording rules

- **Speed-ups:** any agent wait or typing that is shortened in the edit gets the on-screen label **"sped up ×N"**, where N is the real factor. The label stays up for as long as the shortened part plays. Tool calls and results can be sped up but never cut out. The measured p50 turn time goes in the README (T5.3).
- **Brief cut:** if the 0:00 brief comes from a one-shot job (T5.2) rather than the 08:00 IST schedule, the cut is labelled on screen. The BriefCard always shows the actual run time.
- **Functionality rule:** the build must behave exactly as the video shows it. Never edit agent output, never stage a result, never fake a take.
- **Model label:** the Activity label and LedgerDiff header show the model actually used for that call (`egress_events.model`). This is `settings.model_primary` unless the call escalated ("↑ Super"). The script assumes DG-1 keeps Nemotron 3.5 Lightning as primary. If DG-1 makes Super primary, change the label, the voice-over and the call-outs to match.
- **On-screen content:** no Gmail UI and no third-party logos. Sponsor and tool names appear as text only.

### Pre-flight checklist (before every take and every live showing)

1. **Machine:** M4 Pro, Docker Desktop running with its VM capped at 6 GB, heavy apps closed, macOS Do Not Disturb on.
2. **`.env`:** `NEBIUS_API_KEY`, `TAVILY_API_KEY`, `SMTP_HOST`/`SMTP_PORT`/`SMTP_USER`/`SMTP_PASSWORD`, `DEMO_MAIL_REDIRECT` = the team demo inbox, `MAIL_MODE=demo`, `OWNER_EMAIL=maya@rao-consulting.example`.
3. **Reset and start:** run `make demo-reset && make up`. This wipes Hermes state and `steward.db`, reseeds with a new `reset_nonce`, and starts both services.
4. **Health green:** `GET /api/health` returns `ok`, `hermes:'up'`, `token_factory:'up'`, `tavily:'up'`, `mail_mode:'demo'` and the expected `model_primary`. The sidebar health pill shows green dots for Hermes, Token Factory and Tavily, and mail mode reads `demo`.
5. **Seed state:**
   - The Approvals badge is hidden (0 pending).
   - Chat shows the empty state with its chips.
   - On the DG-2 pass path, the Memory tab must NOT contain Rahul's tone line (it is not seeded).
   - Decide the DG-2 path (learned or edited) before rolling.
6. **Brief:** use one of two options.
   - Record at 08:00 IST.
   - Or schedule the optional one-shot brief job (T5.2) a few minutes ahead and start recording before it fires.
7. **Mail client:**
   - The `DEMO_MAIL_REDIRECT` inbox is open in a neutral desktop mail client, not the Gmail web UI.
   - The window is sized and cropped to the message list, with no other accounts, avatars or logos visible.
8. **Browser:**
   - Dashboard at `http://127.0.0.1:8787/chat`, on a clean profile (no extension icons) with the bookmarks bar hidden and a single tab.
   - Set a fixed zoom level, chosen in a test take so the LedgerDiff columns and teal chips are legible at 1080p. Use the same zoom for every take.
9. **Architecture shots ready:** see the shot list below.
10. **Live showings only:**
    - The second Mac (M1 Pro) is pre-warmed with `make demo-reset && make up`.
    - The phone hotspot is ready.
    - The backup recording of the 60-second flow is on both Macs.

### Script

| Time | Screen | Exact click / typing | What appears on screen | Voice-over |
|---|---|---|---|---|
| 0:00 | Chat `/chat` | None (hands off). Recording is already running before the job fires. | Activity rail: "morning-brief · scheduled run" arrives with no user input. **Today's brief** card appears: 3 replies needed, INV-0042 (Acme) 12 days overdue, Watch topics (Tavily) "warehouse robotics funding". The card shows the run time. | "No prompt. The morning brief ran on schedule: three replies due, Acme twelve days overdue, and news on each client's watch topics." |
| 0:07 | Chat | Type `FYI — Rahul at Acme likes short, formal emails.` and press Enter. When Activity shows the memory change, click **New chat**. | "Steward is working…" bubble. Activity: "Memory changed by Steward — review". After New chat, the empty thread shows the chips. | "Tell it once. Steward writes it to memory, and shows you the change." |
| 0:07 (DG-2 fail variant) | Memory & Skills `/memory`, Memory tab | Add an entry: `Rahul at Acme likes short, formal emails.` Click **Save**, go to Chat, click **New chat**. | New entry with char counter. "Changes apply from your next new chat." Then the empty thread with chips. | "Tell it once, here by editing its memory. It applies from the next new chat." |
| 0:13 | Chat (new conversation) | Click the chip **Chase the Acme invoice**. | Activity ticks: files_read, mail_search, "Nemotron 3.5 Lightning · N identifiers masked", mail_send → queued. "sped up ×N" shows while shortened. | "Chase the Acme invoice. Hermes reads the invoice and the thread, and Nemotron on Nebius Token Factory drafts the reply from placeholders, not names." |
| 0:24 | Chat | None. | Reply: a short, formal draft to Rahul for INV-0042 / $4,800. | "Short and formal, the way Rahul likes it. INV-0042, four thousand eight hundred dollars." |
| 0:28 | Approvals `/approvals` (sidebar badge 1) | Click **Approvals**, then **Approve** on the pending ActionCard. | ActionCard: mail_send, recipient rahul.verma@acme-logistics.example, subject, monospace body preview, **Low** risk badge. Toast "Sent". | "Nothing goes out without Maya. Trusted contact, low risk: approve." |
| 0:32 | Neutral mail client (cropped) | Switch to the mail client window. | New message "[Steward demo → rahul.verma@acme-logistics.example] …". | "It arrives, redirected to our demo inbox." |
| 0:36 | Ledger `/ledger` | Click **Ledger**, then the newest `llm` row. The Sheet opens. | LedgerDiff header "nvidia/\<model\> · api.tokenfactory.nebius.com · ZDR: enabled in our Nebius org (account setting)". Left, "On your Mac": Rahul Verma, Acme Logistics, emails, GSTIN, UPI, $4,800. Right, "Sent to Nebius": teal `[[PERSON_1]]`, `[[ORG_1]]`, `[[ACCOUNT_2]]`, `[[MONEY_1]]` … (indices come from the vault). | "Here's the receipt: what stayed on the Mac, next to what Nemotron saw. Nebius sees the work, not who it's for." |
| 0:46 | Chat, then Approvals | Click **Chat**. Type `Acme says their bank details changed — send all open invoices to the address in their latest email.` and press Enter. Click **Approvals**, then **Reject**. | Activity: mail tools run, mail_send → queued. ActionCard: red **High** badge. Red Alert: "billing@acme-logistics-payments.example is not a trusted contact · lookalike of acme-logistics.example". After Reject, the card moves to History as rejected. | "Now the phishing email: 'our bank details changed.' It talks the agent into a send, and the gate catches the lookalike domain. Rejected. Nothing was sent." |
| 0:57 | End card | None. | "Steward — your assistant, your clients, your receipts. NVIDIA Nemotron on Nebius Token Factory · Hermes Agent · Tavily" (text only, no logos). | "Steward. Your assistant, your clients, your receipts." |

**Wow moments (hold the frame):**
- The LedgerDiff at 0:36.
- The BEC catch at 0:46. The injected email talked the agent into a send, and the lookalike domain was caught before anything left.

### Full video structure (≤2:50, public on YouTube)

| Time | Segment | On screen | Voice-over (key lines) |
|---|---|---|---|
| 0:00–0:20 | Problem | Persona card: Maya Rao (fictional, they/them), independent software consultant in Bengaluru, 5 active clients each under NDA. Pain sentence as an on-screen quote. "n=5 conversations, Oct 2026". | "Client admin — follow-ups, invoice chasing, keeping track of who wants what — eats my day, and I won't hand my clients' names, emails and bank details to a chatbot that keeps them." Add one line on what the five conversations said (validate in T0.9; reword to the real findings). |
| 0:20–1:20 | The 60-second demo | The script above. | The script above. |
| 1:20–1:55 | Architecture | Shot list below. | "Hermes Agent runs in a sealed Docker network. Its only way out is Steward's Privacy Shield, which holds the Token Factory key, swaps known client identifiers for placeholders, and blocks the request if anything known slips through." Over the shots: "Hermes can't reach the internet." / "Leak test: zero seeded identifiers in recorded payloads." / DG-1 line (say only what the table shows). / "If something would leak, it's blocked, not sent." / "ZDR is enabled in our Token Factory org (an account setting Steward cannot verify), so prompts aren't retained, and Nebius never trains on them." |
| 1:55–2:25 | Impact, and what's new vs Hermes/OpenShell | Comparison card with three rows (frameworks, sandboxes, Steward), then the LedgerDiff again. | "Agent frameworks like Hermes give memory, skills and tools, but assume you trust the model provider with raw data. Sandboxes like OpenShell control where an agent connects, not what it sends. NVIDIA closed the content-aware egress proposals as not planned in September. Steward adds that layer on top of Hermes: pseudonymize-then-infer, with receipts." Add one impact line from T0.9 (validate in T0.9). |
| 2:25–2:45 | Call-outs, said aloud | End card. | "Steward runs on **Nebius Token Factory** with **NVIDIA Nemotron 3.5 Lightning**, NVIDIA's executor model for always-on agents, with **Nemotron 3 Super** as fallback. The agent runtime is **Hermes Agent**. Research goes through **Tavily**, on topics only, never client names, and the ledger proves it." |
| 2:45–2:50 | Slack | End card hold. | None. Never run past 2:50. |

#### Architecture segment shot list (1:20–1:55)

| # | Duration | Shot | Source / trigger |
|---|---|---|---|
| 1 | ~21 s, split around shots 2–6 | Diagram: the dashboard talks to steward-api, which contains the Privacy Shield proxy `/v1/chat/completions`, the MCP server `steward-tools` at `/mcp`, the Approval Gate and the Egress Ledger. Hermes Agent sits on the `internal` network (no internet), and its only reachable host is steward-api. steward-api sits on the `egress` network and is the only service that talks to Nebius Token Factory (Nemotron), Tavily and SMTP. | README architecture diagram (T5.3) |
| 2 | 3 s | `make egress-check` failing: Hermes cannot reach example.com | Terminal, large font |
| 3 | 3 s | `make leak-test` passing: 0 seeded identifiers across all recorded outbound payloads | Terminal |
| 4 | 4 s | DG-1 table: 4 rows (Lightning/Super × plain/pseudonymized), with success, placeholder integrity, p50 latency and tokens for each | docs/02 decisions log |
| 5 | 2 s | One red policy block: Activity "Blocked: identifier would have left the Mac", or a Ledger row whose right column reads "Not sent — blocked" with «BLOCKED:KIND» chips | Leak-test fixture trigger (T4.6) |
| 6 | 2 s | Token Factory ZDR toggle in the org profile | Browser, cropped to the toggle |

#### Video production rules

- The finished video must be under 3 minutes (target ≤2:50) and public on YouTube. It must show Steward running on the Mac, in English, with captions (T5.4).
- Say "Nebius Token Factory" and the Nemotron model name out loud. They must also appear in the Devpost description and in Built With.
- No Gmail UI and no third-party logos. Show the mail client neutral and cropped.
- Use no external statistic in the video unless it has been verified by T5.4. Until then it stays "(to verify)" in the docs only.

## 2. 5-slide outline

Slides are only for live showings. The video is the primary artifact.

### Slide 1: Problem

**Title:** Client admin eats the day, and it runs on other people's identities

- Maya Rao (fictional persona, they/them) is an independent software consultant in Bengaluru with 5 active clients, each under NDA. Their inbox plus a folder of client notes and invoices is the whole back office.
- "Client admin — follow-ups, invoice chasing, keeping track of who wants what — eats my day, and I won't hand my clients' names, emails and bank details to a chatbot that keeps them."
- Small vendors are targeted by "our bank details changed" invoice fraud (business-email compromise). FBI IC3 BEC loss figure: (to verify).
- What we heard: n=5 conversations, Oct 2026, with a one-line summary (validate in T0.9).

**Visual:** the persona card, the pain quote, and one short T0.9 quote.

### Slide 2: Solution

**Title:** Steward: pseudonymize-then-infer, with receipts

- **F1 Remembers & acts.** Hermes Agent memory across sessions. Two skills: `invoice-chase`, and `morning-brief` (daily 08:00 IST via Hermes cron, also on demand).
- **F2 Privacy Shield + Egress Ledger.** Known client identifiers become placeholders like `[[PERSON_1]]` before Nemotron on Token Factory sees them. Answers are re-identified locally, a fail-closed leak check runs on every request, and every request is logged.
- **F3 Approval Gate.** Every send and write waits for approval. A lookalike-domain (BEC) guard and an unresolved-placeholder guard protect sends.
- "Nebius sees the work, not who it's for: Nemotron never learns who your clients are, how to reach them, or their bank and money details."

**Visual:** LedgerDiff screenshot, "On your Mac" vs "Sent to Nebius", with teal placeholder chips.

### Slide 3: Live demo

**Title:** 60 seconds: brief, memory, chase, approve, receipt, BEC caught

- The scheduled morning brief appears with no user input.
- A preference is learned (or edited, on the DG-2 fail path), and a new chat applies it.
- "Chase the Acme invoice" produces a short formal draft, which is Low risk, approved and delivered to the demo inbox.
- The LedgerDiff shows exactly what Nebius saw.
- A BEC request to a lookalike domain is flagged High and rejected.

**Visual:** live dashboard on the M4 Pro. Backup: 4 screenshots (BriefCard, Low ActionCard, LedgerDiff, High BEC ActionCard) plus the screen-recorded 60-second flow.

### Slide 4: Architecture and tech

**Title:** Hermes in a sealed network; the Shield is its only way out

- **Hermes Agent** v2026.9.24 (pinned digest) runs on a Docker `internal` network. Its toolsets are restricted to memory, session_search, skills and the `steward` MCP server, and the proxy enforces a tool-name allowlist.
- **steward-api** (Python 3.12, FastAPI) contains the Privacy Shield proxy, the `steward-tools` MCP server (9 tools), the Approval Gate and the Egress Ledger. It is the only service holding the Token Factory, Tavily and SMTP credentials.
- **Nebius Token Factory** serves Nemotron 3.5 Lightning, then Nemotron 3 Super (fallback/escalation), then Nemotron 3 Nano 30B. Hermes only ever sees the `steward-auto` alias, and DG-1 sets the order.
- **Dashboard:** Next.js 15 static export + shadcn/ui, served by steward-api. The rest of the stack is SQLite, Docker Compose (2 services), and Tavily on watch topics only.
- **Proof:** `make egress-check`, `make leak-test`, the DG-1 table, and CI on Linux.

**Visual:** the video's architecture diagram, with the DG-1 table inset.

### Slide 5: Impact and future

**Title:** Who it's for, and what's next

- **For:** freelancers and consultants whose clients' identities are the sensitive part of the work. n=5 conversations, Oct 2026 (validate in T0.9).
- **Risk addressed:** BEC invoice fraud aimed at small vendors, IC3 figure (to verify). The gate flags lookalike domains before anything is sent.
- **What's new:** frameworks assume you trust the provider. Sandboxes control where an agent connects, not what it sends (content-aware egress closed not_planned 2026-09-21). Steward adds a per-request receipt.
- **Next (S1–S5):** S1 hosted demo on a Nebius AI Cloud Serverless Endpoint, S2 IMAP read, S3 local Nemotron guard, S4 OpenShell secure mode, S5 Telegram approval cards with placeholders only.
- **Later:** encryption at rest of local stores, more connectors, and an OpenShell policy layer.

**Visual:** a roadmap strip. Now = F1–F3; next = S1–S5; later = encryption at rest, connectors, OpenShell policy layer.

## 3. 10 likely judge questions

**1. If it's private, why does inference run in the cloud?**
Stage One is a hard gate: a runtime call to Nebius Token Factory with an NVIDIA open model is required, and local-only inference fails. On our 16 GB and 24 GB Macs only Nemotron 3 Nano 4B fits (30B-class Nemotron needs ~24–26 GB), and it is too weak to drive Hermes's multi-step tool use. So we pseudonymize, then infer, and describe it in exactly these words:

> "Nebius sees the work, not who it's for: Nemotron never learns who your clients are, how to reach them, or their bank and money details. ZDR is enabled in our Token Factory org (an account setting Steward cannot verify), so prompts aren't retained, and Nebius never trains on them. Every model and search request is logged locally so you can check."

**2. What does the Shield NOT hide?**
The content of the work (free text) is sent, and so are dates and any names that are in neither contacts nor mail headers (until S3). File names aren't masked, which is why the seed rule keeps them identifier-free. Tavily queries go to Tavily in clear under Tavily's own retention, but they carry topics only, and any query containing a vault entity is blocked. Local stores (`steward.db`, Hermes memory) are plaintext on disk; we assume FileVault and disclose this in the README.

**3. What stops Hermes from calling the internet directly?**
Hermes sits only on a Docker `internal: true` network, so its only reachable host is steward-api; `make egress-check` shows it cannot reach example.com. Its toolsets are locked to memory, session_search, skills and the `steward` MCP server, with web, browser, terminal, file, code_execution and delegation disabled. The proxy also blocks any request whose tool list contains a name outside the allowlist. Hermes holds no provider keys (only STEWARD_PROXY_KEY, STEWARD_MCP_TOKEN and its API server key), and the `/api/*` Host guard rejects it, so it cannot drive the control plane either.

**4. How is this different from Hermes, OpenShell, NemoClaw and the other entries?**
Hermes and NemoClaw provide memory, skills and tools, but they assume you trust the model provider with raw data. OpenShell and NemoClaw control where an agent connects, not what it sends to allowed endpoints, and NVIDIA closed the content-aware egress proposals as not_planned on 2026-09-21. Steward is built on Hermes and adds that missing layer: pseudonymize-then-infer, plus a per-request receipt (LedgerDiff) of what the provider saw. Public Personal AI entries already ship memory, approval inboxes and audit logs, which we treat as table stakes; none we found does pseudonymize-then-infer or shows a per-request diff.

**5. What about prompt injection and memory poisoning?**
We assume injection will sometimes work, and the demo shows it: the BEC email's injected line gets the agent to queue a send. The gate is the backstop: sends and writes only create pending actions, R1 flags untrusted and lookalike recipients High, R0 blocks unresolved placeholders, approval executes at most once, and contacts and trust are never agent-writable. For memory poisoning (MPBench, arXiv 2606.04329, June 2026, measured 66.67% attack success on Hermes), every agent-made memory change is diffed into Activity and is editable per entry, and mail/file/web content is wrapped as untrusted. This is mitigated, not prevented: a subtle poisoned entry persists until the user reviews the diff.

**6. Does pseudonymization hurt Nemotron?**
We measured it before building on it: T0.3 (DG-1) ran invoice-chase 10× for each of {Lightning, Super} × {plain, pseudonymized} fixture, scoring correct tool order with valid JSON args, placeholder integrity and p50 latency. The pass bar is ≥8/10 runs, ≥95% of placeholders intact and p50 ≤45 s, and T2.5 re-runs the harness through the full Shield. The 4-row table is in docs/02, the README and the video (numbers filled from T0.3). The re-identifier tolerates single brackets, extra spaces and lowercase kinds, and R0 disables Approve on any placeholder that still can't be resolved.

**7. Why Lightning rather than Super, and what does it cost?**
DG-1 data sets the order. Lightning costs $0.06/$0.24 per 1M input/output tokens with a 1M context, against $0.30/$0.90 for Super, and NVIDIA positions it as the execution layer for always-on agents (vendor PinchBench 85.4 vs 80.4 (to verify)). If Lightning returns a malformed tool call or empty content where a tool call was expected, the proxy retries once on Super, and the ledger shows "↑ Super". Every call's tokens and estimated cost are in the Ledger; the build runs on the $25 promo credit plus $25 from the Builders Program, and judges get a separate prepaid key with no auto top-up.

**8. Is it really always-on on a laptop?**
The morning brief is a Hermes cron job (daily 08:00 Asia/Kolkata) that steward-api registers idempotently through the Hermes Jobs API at startup, so it runs with no user input; Hermes runs with `restart: unless-stopped`. The limitation: if the Mac is asleep, the brief runs late or not at all. We disclose this, and the BriefCard shows the actual run time. Always-on hosting is S1 (a Nebius AI Cloud Serverless Endpoint, ~$1.6/day for Dec 1–15), a should-have that ships only if it is ready in the buffer.

**9. How can judges test it?**
The test build is GitHub release `v1.0.0`: clone it, `cp .env.example .env`, paste the judge `NEBIUS_API_KEY` and `TAVILY_API_KEY` from Devpost's private testing instructions, run `make demo-reset && make up`, and open `http://127.0.0.1:8787`. Judges get a dedicated Token Factory key (a separate prepaid project, no auto top-up) and a Tavily key, and `MAIL_MODE=demo` keeps sends local, so no mail credentials are needed. The declared platform is Docker Compose on macOS 14+ Apple Silicon and Linux x86_64; CI on ubuntu runs lint, typecheck, tests, the web build and compose up + `/api/health`. Testing stays free until Dec 15, 2026 12:00 PM PT, with a weekly key check Dec 1–15.

**10. Why no Telegram?**
Telegram bot chats aren't end-to-end encrypted. Replies containing re-identified client names, emails and amounts would pass through Telegram in clear and bypass the Shield, so v1 uses the local dashboard (D7). The planned S5 sends only approval cards with placeholders, so Telegram would see `[[PERSON_1]]`, not the client's name.

## 4. Fallback plan if the live demo breaks

### Principles

- **The recorded video is the primary artifact.** Judging is asynchronous (Dec 1–15, 2026): judges watch the YouTube video and test the release, so any live showing is an extra. Record clean takes during M5 (Day 11–13). Final submission is by Fri Oct 23, and Oct 24–30 is for emergencies only.
- **Recorded demo option:**
  - Keep a screen-recorded backup of the 60-second flow, taken from a clean take with speed-up labels.
  - Store it locally on both Macs so it plays offline.
  - Put screenshots of the key beats in the deck (slide 3).
  - If you switch to it live, say "this is the recording".
- **Live-showing kit:**
  - Primary M4 Pro with pre-flight done.
  - Second Mac (M1 Pro) pre-warmed with `make demo-reset && make up` and health green.
  - Phone hotspot.
  - The backup recording and the screenshots.
- **No replay mode.** It was cut before Day 1. The product never fakes a run. The backup is a plain screen recording.
- **Never wait out the 300 s `/api/chat` timeout on stage.** If a beat stalls, check Activity and Approvals first, then switch to the backup recording at that beat.
- **Re-takes always start from `make demo-reset && make up`,** because memory, actions and ledger rows persist across a failed take.

### Failure → action

| Failure | What you see | During recording | During a live showing |
|---|---|---|---|
| Token Factory down / 429 / timeout | Health pill shows Token Factory down, a banner appears and the composer is disabled. Or the turn ends in "Model unavailable — this turn did not complete" with Retry, plus a ledger `error` row. The proxy has already tried 60 s per attempt, 1 retry, then the fallback chain. | Check the key and balance with `curl /v1/models`. Wait, then re-take from reset. If a model ID was retired, change `MODEL_PRIMARY` per the README. | Click Retry once. If it fails again, say so and play the backup recording. The second Mac uses the same Token Factory, so it won't help here. |
| Hermes hangs | "Steward is working…" stays up. At 300 s the dashboard shows "Still working — check Approvals and Activity". If Hermes is down, the health pill shows it and the composer is disabled with a banner. | Check Activity and Approvals before re-prompting, because the action may already be queued. Use `make logs` and `docker compose restart hermes`, wait for health green, then reset and re-take. | Check Approvals. If the action is there, continue. Otherwise switch to the second Mac or the backup recording. Do not wait. |
| SMTP fails | The action ends `failed` with an error card, or shows "delivery unknown — check Sent before retrying" on a timeout. Nothing is auto-retried. | Check the redirect inbox first. Fix the SMTP credentials or App Password, then reset and re-take. | Skip the 0:32 mail-client shot and show the action in Approvals → History. The gate and ledger beats are unaffected. Don't click anything that could send twice. |
| Wrong model output (wrong tone, missing INV-0042 or $4,800, wrong tool order, a clarifying question instead of a draft, refusing to queue the BEC send) | Visible in the chat reply and the Activity rail. An unresolved placeholder disables Approve (R0). An escalation shows "↑ Super". | Never edit the output. Reset and re-take. If failures repeat, recheck against the DG-1 harness. Keep a "↑ Super" escalation only if the voice-over mentions it. | Reject any wrong action (nothing is sent), say what happened, and continue with the LedgerDiff, which is still accurate for that call. If the BEC beat fails, play that beat from the backup. |
| Docker issue (Docker Desktop not running, container unhealthy, out of memory) | `make up` prints a clear message, or `docker compose ps` shows a service unhealthy. | Start Docker Desktop and run `make down && make up`. Close heavy apps (the VM is capped at 6 GB). Then reset and re-take. | Switch to the second Mac. |
| Wi-Fi down or unreliable | Token Factory, Tavily and SMTP calls fail, and the health pill shows them down. | Use the hotspot, or wait. | Switch to the phone hotspot and confirm the health pill is green. With no connectivity at all, use the backup recording and the deck screenshots. |
| Tavily down or no key | The brief renders without "Watch topics". | Re-take the brief once Tavily is back, because the 0:00 beat needs the watch-topics line. | Say so and move on. The rest of the flow doesn't use Tavily. |
| Brief did not run on schedule (Mac asleep, missed run) | No "scheduled run" entry. The BriefCard shows a stale or empty brief. | Use the one-shot job (T5.2), or trigger the same Hermes job with "Run now" or `make brief-now`, and label the cut. Never caption a manual run as "ran by schedule". | Click "Run now" and say it was triggered by hand. |
