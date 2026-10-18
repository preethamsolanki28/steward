# Steward: finish plan (from 2026-10-18)

## 1. Purpose

Steward is a private AI helper for freelancers. It remembers your clients, writes emails for you, and never sends anything without your OK. Before the AI sees anything, it swaps client names, emails, bank details and money amounts for labels like `[[PERSON_1]]`, and it shows you a receipt of exactly what the AI saw.

This plan replaces the remaining work in docs/04 from 2026-10-18. docs/04 stays as history. Goal: submit a working, simple, honest entry by **Fri Oct 23**. The hard deadline is Fri Oct 30, 10:00 AM PDT; Oct 24–30 is for emergencies only.

## 2. Where we are

**Done (main @ `7969a84`)**

| Area | State |
|---|---|
| Core features | Privacy Shield, receipt screen (LedgerDiff), Approval Gate (R0/R1/R3/overwrite), MCP tools, memory, morning brief with Tavily, sealed Docker network. All built and tested live. |
| Dashboard | 4 screens (Chat, Approvals, Ledger, Memory & Skills) with every loading, empty and error state; works at 375px. |
| Invoice chase | Fixed with `skills.auto_load: [invoice-chase]`: 10/10 runs read the email thread before drafting, each on a fresh reset (2026-10-04, p50 16.4 s). |
| Phishing (BEC) | Steward refuses the phishing request: 30/30 runs. The gate's lookalike check (R1) is proven by a CI test. |
| Demo brief shortcut | `STEWARD_DEMO=1` one-shot brief job built. |
| Checks | 420 backend tests green, web build green, CI workflow written (never run yet). |
| Install | Fresh clone + README steps worked on the M4 Pro (2026-10-04). |
| README | Draft on branch `t5-3-readme` (not merged; links still missing). |

**Not done**

GitHub repo and a green CI run, a real email delivery check (needs the demo mailbox password), install on the other Mac, a second reliability batch on another day, 3 clean dry runs of the demo, 2 clean smoke-test passes, the 5 freelancer conversations (T0.9), video, Devpost, `v1.0.0` tag.

**Known problems**

| # | Problem | Why it matters |
|---|---|---|
| P1 | After `make demo-reset`, the one-shot demo brief job is registered but **never runs**. 3/3 dry runs failed at the first beat. It worked on Oct 4 when Hermes was not restarted. | Blocks the 0:00 demo beat. The daily 08:00 brief may also be affected after a reset (NEVER-cut feature). |
| P2 | If steward-api restarts while Hermes is running a cron job (e.g. Docker auto-start, then `make up`), the run hangs for 600 s and ends "error". | Brief shows "error" by accident. |
| P3 | A retired model id returns a 4xx, and the proxy then stops instead of falling back (docs/02 §8 says it falls back). | If Nemotron Super is retired during judging (Dec 1–15), the app stops working for judges. |
| P4 | Hermes says "Noted – I'll remember" but rarely saves (1/12 on the release setup). | Demo uses the memory editor; README discloses it. |
| P5 | Docker Desktop VM is ~7.7 GiB; the rule is 6 GB. | Test on the 16 GB Mac may differ. |

## 3. Rules that still hold

- Everything in AGENTS.md still applies: fixed stack, **no new libraries without asking**, the Hermes boundary, secrets only in `.env`, synthetic `.example` data only.
- **NEVER cut or weaken:** Privacy Shield (aliases, `walk_strings`, leak check), internal network + toolset lockdown + tool allowlist, `/api` guards, the receipt screen, the `mail_send` gate with R0 and R1, invoice chase end to end, the morning brief with Tavily, cross-session memory, README, LICENSE, video, feedback.
- No fake or staged demo results. The video shows what the app really does.
- Judge-facing privacy text (README, Devpost, video) uses the approved wording from docs/00. UI words may be plainer, but **never claim more** (never "anonymous", "nothing leaves", "100% private", "every byte").
- Backend strings (API errors, risk reasons, activity text) stay as they are. The UI maps them to plain words, so backend tests and contracts don't change.

## 4. Simple UI plan

### 4.1 Plain-words rules

- Write for a 9-year-old: short, common words. One idea per sentence.
- Labels are 1–4 words. Messages are one short sentence, plus "what to do next" when something fails.
- Don't use: ledger, egress, payload, placeholder, pseudonymize, shield, model, token, risk, approve, reject, execute, schedule, cron, skill, MCP, latency, endpoint.
- Technical names (model id, Token Factory, tool names) appear only in small print or behind **Show details**.
- Same thing, same word, on every screen.
- Every status keeps an icon or a word, not only a color.

### 4.2 Menu (same 4 pages, new names)

| Old | New | What it's for (shown as a small line under the page title) |
|---|---|---|
| Chat | **Chat** | Talk to Steward. |
| Approvals | **Needs your OK** | Emails and files wait here until you say yes. |
| Ledger | **What the AI saw** | A receipt for everything sent to the AI or the web. |
| Memory & Skills | **Memory** | What Steward knows about you, and what it can do. |

Memory tabs: **What Steward knows** · **Jobs it can do** · **Status**.

### 4.3 Word changes, screen by screen

"(B)" means the text comes from the backend and the UI shows the new words instead (backend unchanged).

**Side bar (status)**

| Old | New |
|---|---|
| Hermes / Token Factory / Tavily | Assistant / AI / Web search |
| up / down / no key | Working / Not working / No key |
| mail: demo | Email: practice inbox |

**Chat**

| Old | New |
|---|---|
| Today's brief | Today's summary |
| Ran by schedule at 08:00 IST | Made automatically at 8:00 am (India time) |
| Ran at HH:mm IST | Made at HH:mm (India time) |
| Run now / Running… | Make it now / Making it… |
| Your first brief arrives at 08:00 IST — or run it now. | Your first summary comes at 8:00 am (India time). Or tap "Make it now". |
| Ask Steward to chase an invoice or check what needs a reply | Ask Steward for help. Try one: |
| Chips: Chase the Acme invoice / What needs my reply today? / Run my morning brief | **Keep "Chase the Acme invoice" exactly** (it is the tested prompt; changing it needs a new 10-run test). "What needs my reply today?" stays. "Run my morning brief" → "Make my morning summary". |
| Message Steward… | Type a message… |
| Steward is working… | Steward is working on it… |
| Conversations / New chat | Past chats / New chat |
| Activity | Steps |
| Hermes is down — chat is paused until it's back. | The assistant isn't running. Chat is paused. |
| Token Factory is unreachable — chat is paused… | Can't reach the AI right now. Chat is paused. |
| No Token Factory key (NEBIUS_API_KEY) — chat is paused. | The AI key is missing (NEBIUS_API_KEY). Chat is paused. |
| Model unavailable — this turn did not complete (B) | The AI didn't answer. Check "Needs your OK", then try again. |
| Retry | Try again |
| Still working — check Approvals and Activity (B) | This is taking a long time. Check "Needs your OK" and Steps. |
| Can't reach Steward — is `make up` running? | Can't reach Steward. Is it running? (`make up`) |

**Steps list (activity) (B)**

| Old | New |
|---|---|
| files_list / files_read | Looked at files / Read a file |
| contacts_lookup | Checked contacts |
| mail_search / mail_read | Searched email / Read an email |
| mail_send / mail_send → queued | Wrote an email / Email waiting for your OK |
| files_write → queued | File waiting for your OK |
| web_search / Tavily search | Searched the web |
| brief_save | Saved the summary |
| Nemotron 3 Super · N identifiers masked | Asked the AI · hid N private details |
| Blocked: identifier would have left the Mac | Stopped: private details were about to be sent |
| Memory changed by Steward — review | Steward changed its memory — see what changed |
| morning-brief · scheduled run / run now / (demo one-shot) | Morning summary (automatic) / (you asked) / (demo, started early) |
| action #N approved / rejected | You said yes / You said no |
| mail_send → sent (demo mailbox only) | Email sent (practice inbox) |
| mail_send → delivery unknown / failed | Not sure if it was sent / Couldn't send |
| files_write → written | File saved |

**Needs your OK**

| Old | New |
|---|---|
| Pending (N) / History | Waiting (N) / Done |
| mail_send / files_write | Email / Save a file |
| Low risk / High risk | Looks OK / Be careful |
| X is not a trusted contact (B) | X is not in your trusted contacts |
| lookalike of Y (B) | Looks like Y, but it's a different address |
| unresolved placeholder (B) | A hidden name wasn't filled back in |
| more than 3 recipients (B) | Goes to more than 3 people |
| overwrites existing file (B) | Replaces a file that already exists |
| local part mentions trusted org (B) | The part before @ copies a client's name |
| Approve / Reject | Yes, send it (Yes, save it for files) / No |
| Executed / Rejected / Failed | Sent (Saved) / You said no / Didn't work |
| delivery unknown — check Sent before retrying (B) | We're not sure it was sent. Check your Sent folder before trying again. |
| Approve a High-risk action? / Approve anyway / Cancel | Are you sure? / Yes, send anyway / Go back |
| Nothing waiting for you. Steward asks before it sends anything. | Nothing waiting. Steward always asks before sending. |
| No decisions yet. | Nothing done yet. |
| Toasts: Sent / Written to path / Not sent — see History | Sent / Saved (path) / Didn't send. See Done. |

**What the AI saw**

| Old | New |
|---|---|
| Calls today / Identifiers masked / Est. cost / Blocked; "today (IST)" | AI requests / Private details hidden / Cost (about) / Stopped; "today" |
| Time / Channel / Destination / Model / Masked / Latency / Status | Time / Sent to / Address / AI / Hidden / Took / Result |
| llm / web / mail | AI / Web / Email |
| ok / error / blocked | OK / Failed / Stopped |
| On your Mac / Sent to Nebius | What you see (on your Mac) / What the AI saw |
| Sent in clear to Tavily — Tavily's own retention applies | Sent to Tavily web search as written (Tavily's own rules apply) |
| Not sent — blocked | Not sent — stopped |
| REQUEST / RESPONSE | Asked / Answer |
| Show full payload | Show everything |
| New one-line key above the columns | "The AI only saw labels like [[PERSON_1]], not the real details." |
| Header "… · ZDR: enabled in our Nebius org (account setting)" | Keep the model id + host on the header; plain line under it: "Zero data retention is on in our Nebius account. Steward can't check this." |
| Nothing has been sent to an AI or search provider yet. | Nothing sent to the AI yet. |

**Memory**

| Old | New |
|---|---|
| USER.md / MEMORY.md | About you / Other notes |
| N / 1,375 | Space used: N of 1,375 |
| Add entry / Delete entry / Save | Add a note / Delete / Save |
| Changes apply from your next new chat | Changes start in your next new chat. |
| Steward doesn't know anything about you yet. Tell it in chat or add an entry. | Steward doesn't know anything about you yet. Add a note. |
| Skills tab cards (raw SKILL.md text) | "Remind a client to pay": finds the unpaid invoice, reads the latest email, writes a reminder for you to check. Start it in Chat. / "Morning summary": every day at 8:00 am (India time), lists emails to answer, unpaid invoices and news on your topics. [Make it now] |
| Daily 08:00 IST / Last run | Every day at 8:00 am (India time) / Last made |
| System tab rows: Connectors / Model chain / Reasoning effort / Privacy Shield On / ZDR / Trusted contacts | Is everything working? / AI: NVIDIA Nemotron 3 Super on Nebius Token Factory (backup: Nemotron 3.5 Lightning) / (under Show details) / Hide private details: On / the plain ZDR line above / People Steward can email: "Only these people are trusted. Steward can't change this list." |

### 4.4 Layout changes

- **Add a small "Start here" card on an empty chat** (can be closed): "1. Ask in Chat. 2. Say yes in Needs your OK. 3. See the receipt in What the AI saw." Default: yes.
- Every page gets the one-line "What it's for" under its title (from 4.2).
- Tool names, model ids and raw JSON go behind **Show details**. The receipt screen keeps "Show everything".
- Keep the stats tiles, with the plain words above.

### 4.5 What stays technical, and why

- "NVIDIA Nemotron" and "Nebius Token Factory" stay visible on the Status tab and the receipt header. The hackathon needs them on screen and said aloud in the video.
- Model id, host and the approved privacy wording stay in the README, Devpost and the receipt header.

## 5. Other changes from now on

| Change | Why | Effort | Risk | Decision |
|---|---|---|---|---|
| Fix P1 (demo brief job never runs after reset) | Blocks the demo; may affect 08:00 | 2–6 h | Unknown cause | **DO first** |
| Overnight 08:00 check | Prove the daily brief really runs by itself after a reset | 0.5 h + one night | — | **DO** |
| Model fallback on "model not found" 4xx (P3) | Keeps the judge build working if Super is retired Dec 1–15 | 2 h + tests | Low; only allowlisted Nemotron ids, still through the Shield | **DO** (record in docs/02) |
| P2 note: after Docker restarts, run `make demo-reset` before a demo | Avoids the hung "error" brief | 0.5 h (docs) | — | **DO** |
| Plain-English README (same words as the UI) | Judges read it first | 2 h | — | **DO** |
| T0.9: 5 short freelancer conversations | Our weakest score is Impact; real quotes help | 2–3 h (E2 + you) | Needs real people | **DO** |
| Docker VM to 6 GB | Matches the declared setup | 5 min (you) | — | **DO** |
| Drop the redundant `skill_view` call (SKILL.md description tidy) | Saves about one AI round per chase | 1 h + a new 10-run test | Could change the tested behaviour | **DON'T** (before submission) |
| Read a real inbox (IMAP, read-only) | Would raise Impact | 1.5–2 days | High; cut item S2 | **ASK USER** (default: no) |
| Hosted demo, Telegram, model switching | — | Days | High | **DON'T** |

## 6. Task list

| ID | Task | Owner | Day | Done when |
|---|---|---|---|---|
| N0 | Approve this plan; create the empty public GitHub repo `steward`; give the demo mailbox App Password + `DEMO_MAIL_REDIRECT`; set the Docker VM to 6 GB; book the 5 freelancer calls | **USER** | Oct 18–19 | Repo URL and `.env` values exist (never in git) |
| N1 | Find and fix P1. Steps: start the stack; `STEWARD_DEMO=1 make demo-reset`; watch the Jobs API (GET only) for 6 min; compare with `docker compose restart hermes` (no reset) and with a test one-shot "in 1m"; read Hermes container logs and the read-only source copy. Fix only inside the boundary (config, Jobs API use, registration timing, compose/Makefile order). Any fix that deletes extra Hermes files needs the user's OK first. Fallback if not fixed by Oct 20: the video uses "Make it now", labelled "(you asked)", never called automatic. | E1 | Oct 19 | Demo brief appears by itself within 5 min after `STEWARD_DEMO=1 make demo-reset`, 3/3 times; or the fallback is recorded in docs/02 §12 |
| N2 | Overnight check: leave the stack running after a reset; at 08:00 India time the brief appears with "(automatic)" | E1 | Night of Oct 19 → Oct 20 | Brief + "Morning summary (automatic)" seen at 08:0x |
| N3 | Model fallback on "model not found" 4xx, with tests; update docs/02 §8 + §12 | E1 | Oct 19 | Tests green; a fake retired id falls back to Lightning, and the receipt shows the model used |
| N4 | Plain-words UI (section 4): menu names, word tables, backend-string mapping in one place (`web/lib/words.ts`), "Start here" card, Show details. Update fixtures and tests; screenshots at desktop + 375px; no console errors; 44 px tap targets | E2 | Oct 19–20 | All 4 screens use the new words; `make typecheck`, web build and the fixture checks pass; no old jargon left (grep list in 4.1) |
| N5 | Update docs to the new words: docs/03 copy tables, docs/05 script + voice-over, docs/04 §7 smoke checklist wording, README (plain English; fill measured results; merge `t5-3-readme`), AGENTS.md + .claude/CLAUDE.md point to this plan | E2 | Oct 20 | No doc names an old label |
| N6 | Push to GitHub (MIT LICENSE first commit already); CI runs green on the pushed commit; add the CI badge + repo URL to the README | E1 + USER | Oct 20 | Green Actions run on the main commit, URL recorded |
| N7 | Second reliability batch: 10 chase runs, each after its own reset, on a new calendar day (same harness, same pass rules as docs/02 §12) | E1 | Oct 20 | ≥ 8/10 strict (cumulative ≥ 17/20) |
| N8 | Real email check: with `DEMO_MAIL_REDIRECT` + SMTP set, approve one chase; exactly one email with "[Steward demo → rahul.verma@acme-logistics.example]" arrives; a second approve does nothing | E1 + USER | Oct 21 | Seen in the inbox; one `mail` row in the receipt list |
| N9 | Install on the other Mac (M1 Pro) using only the README | **USER** + E1 | Oct 21 | `make demo-reset && make up` works; health all green; README fixed for any gap |
| N10 | 3 clean dry runs of the full demo (with the new words) | E1 + E2 | Oct 21 | 3/3 in a row, no console errors |
| N11 | 2 clean smoke passes in a row (docs/04 §7, new words) | E1 + E2 | Oct 21–22 | Both passes fully green; any failure → fix and restart at pass 1 |
| N12 | T0.9: 5 conversations, a 5-line summary in docs/00; use one real quote in the video | E2 + **USER** | Oct 19–21 | Summary committed; "(validate in T0.9)" tags removed where now true |
| N13 | Video ≤ 2:50 on the M4 Pro: script from docs/05 with the new words; labelled "sped up ×N"; captions; say "Nebius Token Factory" and "NVIDIA Nemotron" aloud; public YouTube | E1 + E2 | Oct 22 | Public link works; length ≤ 2:50 |
| N14 | Devpost: description, Built With (names Nebius Token Factory + NVIDIA Nemotron), Personal AI track, feedback (from docs/feedback_log.md), private judge testing steps with a **separate prepaid judge key** (never in the repo) | E2 + **USER** | Oct 22 | Every field filled; draft saved |
| N15 | Tag `v1.0.0` (only after N6 green + N11 passed), put the leak-test output in the README, submit Devpost | E1 + **USER** | Oct 23 | Submitted; tag visible on GitHub |
| N16 | Weekly judge-key check Dec 1–15 (`curl /v1/models` with the judge key) | E1 | Dec 1–15 | Calendar reminder set |

## 7. Schedule

| Day | E1 | E2 | You |
|---|---|---|---|
| Sun Oct 18 | — | — | N0: approve plan, repo, mailbox password, Docker 6 GB, book calls |
| Mon Oct 19 | N1 scheduler fix, N3 fallback, start N2 overnight | N4 UI words (part 1), N12 calls | Join calls |
| Tue Oct 20 | Check N2 at 08:00, N6 push + CI, N7 batch | N4 (part 2), N5 docs + README | — |
| Wed Oct 21 | N8 email check, N10 dry runs, N11 pass 1 | N10, N11, N12 summary | N9 other Mac |
| Thu Oct 22 | N11 pass 2, N13 video | N13 edit + captions, N14 Devpost | Review video |
| Fri Oct 23 | N15 tag + submit | Final checks | Press submit |
| Oct 24–30 | Emergency only | | |

If a day slips: move N12, then the "Start here" card, then the Memory/Status wording down the list. Never skip N1/N2, N6, N8, N11, N13, N14 or N15.

## 8. Decisions for you (default in bold)

1. New menu names: **Chat / Needs your OK / What the AI saw / Memory**.
2. Keep the chip text "Chase the Acme invoice" as it is (tested prompt): **yes**.
3. "Start here" card on an empty chat: **yes**.
4. Model fallback on "model not found": **yes**.
5. If P1 needs deleting extra Hermes files to fix: **no**; use "Make it now" in the video, labelled honestly.
6. Real inbox reading (IMAP): **no** (not before Oct 23).
7. Who owns the Devpost account and records the voice-over: **you decide**.

## 9. Cut order if time runs out

1. "Start here" card.
2. Plain words on the Memory "Jobs it can do" and "Status" tabs (keep the menu names).
3. Stats-tile wording.
4. T0.9 (keep the "(validate in T0.9)" tags instead).

The NEVER-cut list in section 3 does not change.

## 10. Final release checklist

- [ ] `make lint typecheck test` green; web build green
- [ ] CI green on GitHub for the tagged commit
- [ ] Brief runs by itself (N1/N2) or the honest fallback is recorded
- [ ] Invoice chase ≥ 17/20 across two days; phishing still refused
- [ ] One real email delivered, exactly once (N8)
- [ ] 3/3 dry runs and 2 smoke passes in a row
- [ ] README: plain words, MIT visible, setup in 5 commands, measured results, leak-test output, links
- [ ] YouTube: public, ≤ 2:50, captions, says Nebius Token Factory + NVIDIA Nemotron
- [ ] Devpost: all fields, Built With, track, feedback, judge key in private instructions only
- [ ] `v1.0.0` tag on GitHub; no commits after Oct 30, 10:00 AM PDT
