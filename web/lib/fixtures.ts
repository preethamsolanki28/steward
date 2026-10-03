// Mock mode (T0.8): seed-like fixture responses for every endpoint in docs/02 §6, so UI work never
// waits on the API. Values mirror seed/ (docs/03 §11). Every docs/03 §8-10 state has a scenario.
//
// How it is switched on (no env var): open any page with `?fixtures` (= "seed") or
// `?fixtures=<scenario>`, optionally `&slow=<ms>` to see loading states. The choice is kept in
// sessionStorage so in-app navigation keeps it; `?fixtures=off` turns mock mode off again.
// lib/api.ts (T4.1) routes requests through fixtureFetch() when getFixtureConfig() is non-null.

import {
  CHAT_ERROR_MODEL_UNAVAILABLE,
  CHAT_ERROR_STILL_WORKING,
  DELIVERY_UNKNOWN,
  MEMORY_ENTRY_DELIMITER,
  MEMORY_LIMIT,
  RISK_REASON_UNRESOLVED_PLACEHOLDER,
  USER_LIMIT,
  ZDR_NOTE,
  type Action,
  type ActivityItem,
  type BriefLatestResponse,
  type Contact,
  type ConversationDetail,
  type ConversationSummary,
  type HealthResponse,
  type LedgerDetail,
  type LedgerRow,
  type LedgerStatsResponse,
  type MemoryResponse,
  type SettingsResponse,
  type Skill,
} from "./types";

export const FIXTURE_SCENARIOS = [
  "seed", // populated, after the docs/05 demo flow
  "empty", // fresh make demo-reset: empty Chat/Approvals/Ledger/BriefCard, seeded USER.md
  "hermes_down",
  "tf_down",
  "tf_no_key",
  "tavily_down", // brief without "Watch topics", tavily dot no_key
  "model_unavailable", // POST /api/chat -> 502
  "chat_timeout", // POST /api/chat -> 504
  "r0", // pending action with an unresolved placeholder
  "approve_409", // approve -> 409 (risk recomputed to High)
  "memory_empty",
  "memory_over_limit", // PUT /api/memory -> 400
  "network_error", // every request throws, like `make down`
  "brief_late", // brief ran late (Mac asleep at 08:00 IST)
] as const;

export type FixtureScenario = (typeof FIXTURE_SCENARIOS)[number];

export interface FixtureConfig {
  scenario: FixtureScenario;
  slowMs: number;
}

const STORAGE_KEY = "steward.fixtures";

function isScenario(value: string): value is FixtureScenario {
  return (FIXTURE_SCENARIOS as readonly string[]).includes(value);
}

/** Returns the active mock-mode config, or null when mock mode is off (always null on the server). */
export function getFixtureConfig(): FixtureConfig | null {
  if (typeof window === "undefined") return null;
  const params = new URLSearchParams(window.location.search);
  const fromUrl = params.get("fixtures");
  if (fromUrl === "off") {
    window.sessionStorage.removeItem(STORAGE_KEY);
    return null;
  }
  if (fromUrl !== null) {
    const scenario = fromUrl === "" ? "seed" : fromUrl;
    const slowMs = Number(params.get("slow") ?? 0) || 0;
    if (isScenario(scenario)) {
      window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ scenario, slowMs }));
      return { scenario, slowMs };
    }
  }
  const stored = window.sessionStorage.getItem(STORAGE_KEY);
  if (!stored) return null;
  try {
    const parsed = JSON.parse(stored) as FixtureConfig;
    return isScenario(parsed.scenario) ? parsed : null;
  } catch {
    return null;
  }
}

// --- time helpers (fixtures always look current) ---------------------------------------------

const NOW = Date.now();
const minutesAgo = (m: number) => new Date(NOW - m * 60_000).toISOString();
/** Today's (or tomorrow's) hh:mm in Asia/Kolkata (UTC+05:30) as an ISO string. */
function istToday(hour: number, minute: number, dayOffset = 0): string {
  const istNow = new Date(NOW + 330 * 60_000);
  const utcMs =
    Date.UTC(istNow.getUTCFullYear(), istNow.getUTCMonth(), istNow.getUTCDate() + dayOffset, hour, minute) -
    330 * 60_000;
  return new Date(utcMs).toISOString();
}

// --- seed-consistent values -------------------------------------------------------------------

const LIGHTNING = "nvidia/Nemotron-3_5-Lightning";
const SUPER = "nvidia/nemotron-3-super-120b-a12b";
const NANO = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B";
const TF_HOST = "api.tokenfactory.nebius.com";

const RAHUL_DRAFT = {
  to: ["rahul.verma@acme-logistics.example"],
  subject: "INV-0042: payment reminder",
  body:
    "Dear Rahul,\n\nThis is a reminder that INV-0042 for $4,800 (integration sprint 3) was due 12 days ago. " +
    "Could you confirm when the payment will be made?\n\nBest, Maya",
};

const BEC_SEND = {
  to: ["billing@acme-logistics-payments.example"],
  subject: "Open invoices",
  body: "Hello,\n\nAs requested, please find the open invoices below: INV-0042, INV-0043, INV-0045, INV-0046.\n\nBest, Maya",
};

function contacts(): Contact[] {
  const created = minutesAgo(600);
  const seed: Array<[string, string, string | null, 0 | 1]> = [
    ["Rahul Verma", "rahul.verma@acme-logistics.example", "Acme Logistics", 1],
    ["Dr. Anita Shah", "anita.shah@brightleaf-clinics.example", "Brightleaf Clinics", 1],
    ["Li Wei", "li.wei@kestrel-robotics.example", "Kestrel Robotics", 1],
    ["Tom Becker", "tom.becker@juniper-co.example", "Juniper & Co", 1],
    ["Sara Khan", "sara.khan@orbitra-foods.example", "Orbitra Foods", 1],
    ["Maya Rao", "maya@rao-consulting.example", null, 0],
    ["Priya Nair", "priya.nair@nair-ca.example", null, 0],
    ["Karan Joshi", "karan.joshi@workloft-blr.example", null, 0],
  ];
  const rows: Contact[] = seed.map(([name, email, org, trusted], i) => ({
    id: i + 1,
    name,
    email,
    org,
    trusted,
    source: "seed",
    created_at: created,
  }));
  rows.push({
    id: 9,
    name: "Vikram Sethi",
    email: "billing@acme-logistics-payments.example",
    org: null,
    trusted: 0,
    source: "mail",
    created_at: minutesAgo(30),
  });
  return rows;
}

function health(scenario: FixtureScenario): HealthResponse {
  return {
    ok: true,
    hermes: scenario === "hermes_down" ? "down" : "up",
    token_factory: scenario === "tf_down" ? "down" : scenario === "tf_no_key" ? "no_key" : "up",
    tavily: scenario === "tavily_down" ? "no_key" : "up",
    mail_mode: "demo",
    model_primary: SUPER,
  };
}

const BRIEF_MD_HEAD =
  "# Today's brief\n\n## 3 replies needed\n" +
  "- **Li Wei** (Kestrel Robotics): which slot works for the pilot demo call\n" +
  "- **Dr. Anita Shah** (Brightleaf Clinics): consent checkbox on the intake form\n" +
  "- **Sara Khan** (Orbitra Foods): quote for a Q4 reporting add-on\n\n" +
  "## Overdue invoices\n- **INV-0042** (Acme): $4,800, 12 days overdue\n";
const BRIEF_MD_WATCH =
  "\n## Watch topics (Tavily)\n" +
  "- **warehouse robotics funding**: fixture result, not real news (https://example.com/fixture-1)\n" +
  "- **India clinic regulation**: fixture result, not real news (https://example.com/fixture-2)\n";

function briefLatest(scenario: FixtureScenario): BriefLatestResponse {
  if (scenario === "empty") {
    return { brief: null, job: { last_run_at: null, last_status: null, next_run_at: istToday(8, 0, 1) } };
  }
  const late = scenario === "brief_late";
  const ranAt = late ? istToday(9, 47) : istToday(8, 0);
  return {
    brief: {
      id: 1,
      created_at: ranAt,
      content_md: BRIEF_MD_HEAD + (scenario === "tavily_down" ? "" : BRIEF_MD_WATCH),
    },
    job: { last_run_at: ranAt, last_status: "ok", next_run_at: istToday(8, 0, 1) },
  };
}

function conversations(scenario: FixtureScenario): ConversationSummary[] {
  if (scenario === "empty") return [];
  return [
    { id: 2, title: "Chase the Acme invoice", updated_at: minutesAgo(12) },
    { id: 1, title: "FYI — Rahul at Acme likes short, formal emails.", updated_at: minutesAgo(15) },
  ];
}

function conversationDetail(id: number): ConversationDetail | null {
  if (id === 1) {
    return {
      id: 1,
      title: "FYI — Rahul at Acme likes short, formal emails.",
      messages: [
        { id: 1, role: "user", content: "FYI — Rahul at Acme likes short, formal emails.", created_at: minutesAgo(16) },
        { id: 2, role: "assistant", content: "Noted. I've saved that to memory for future emails to Rahul.", created_at: minutesAgo(15) },
      ],
    };
  }
  if (id === 2) {
    return {
      id: 2,
      title: "Chase the Acme invoice",
      messages: [
        { id: 3, role: "user", content: "Chase the Acme invoice", created_at: minutesAgo(13) },
        {
          id: 4,
          role: "assistant",
          content:
            "INV-0042 to Acme Logistics ($4,800) is 12 days overdue. I've drafted a short reminder to Rahul " +
            "and queued it for your approval as action #1.\n\n" +
            `**To:** ${RAHUL_DRAFT.to[0]}\n**Subject:** ${RAHUL_DRAFT.subject}\n\n${RAHUL_DRAFT.body}`,
          created_at: minutesAgo(12),
        },
      ],
    };
  }
  return null;
}

const MEMORY_DIFF =
  "--- MEMORY.md\n+++ MEMORY.md\n@@ -3 +3,3 @@\n Maya works Monday to Friday, 10:00 to 18:00 IST, and prefers to handle client email in the morning.\n+§\n+Rahul at Acme Logistics prefers short, formal emails.";

function activity(scenario: FixtureScenario): ActivityItem[] {
  if (scenario === "empty") return [];
  const a = (
    id: number,
    m: number,
    kind: ActivityItem["kind"],
    summary: string,
    ref_table: string | null = null,
    ref_id: number | null = null,
    detail: string | null = null,
  ): ActivityItem => ({ id, ts: minutesAgo(m), kind, summary, detail, ref_table, ref_id });
  return [
    a(1, 300, "tool_call", "mcp_steward_mail_search"),
    a(2, 299, "tool_call", "mcp_steward_files_list"),
    a(3, 299, "egress", "Tavily search", "egress_events", 3),
    a(4, 298, "tool_call", "mcp_steward_brief_save"),
    a(5, 298, "skill_run", "morning-brief · scheduled run", "briefs", 1),
    a(6, 16, "memory_edit", "Memory changed by Steward", null, null, MEMORY_DIFF),
    a(7, 13, "tool_call", "mcp_steward_files_read"),
    a(8, 13, "tool_call", "mcp_steward_mail_search"),
    a(9, 12, "egress", "Nemotron 3.5 Lightning · 7 identifiers masked", "egress_events", 1),
    a(10, 12, "action_created", "mail_send → queued", "actions", 1),
    a(11, 8, "action_created", "mail_send → queued", "actions", 2),
    a(12, 5, "policy_block", "Blocked: identifier would have left the Mac", "egress_events", 5),
  ];
}

function actions(scenario: FixtureScenario): Action[] {
  if (scenario === "empty") return [];
  const act = (
    id: number,
    m: number,
    args: object,
    risk: Action["risk"],
    risk_reasons: string[],
    status: Action["status"],
    result: string | null = null,
  ): Action => ({
    id,
    created_at: minutesAgo(m),
    tool: "mail_send",
    args_json: JSON.stringify(args),
    preview: JSON.stringify(args, null, 2),
    risk,
    risk_reasons,
    status,
    decided_at: status === "pending" ? null : minutesAgo(m - 2),
    result,
  });
  const rows: Action[] = [
    act(1, 12, RAHUL_DRAFT, "low", [], "pending"),
    act(
      2,
      8,
      BEC_SEND,
      "high",
      ["billing@acme-logistics-payments.example is not a trusted contact", "lookalike of acme-logistics.example"],
      "pending",
    ),
    act(3, 400, { to: ["li.wei@kestrel-robotics.example"], subject: "Pilot demo slot", body: "Hi Li,\n\nThursday at 11 am IST works.\n\nBest, Maya" }, "low", [], "executed"),
    act(4, 380, BEC_SEND, "high", ["billing@acme-logistics-payments.example is not a trusted contact", "lookalike of acme-logistics.example"], "rejected"),
    act(5, 360, { to: ["sara.khan@orbitra-foods.example"], subject: "Q4 reporting quote", body: "Hi Sara,\n\nQuote attached.\n\nBest, Maya" }, "low", [], "failed", "SMTP error: 535 authentication failed"),
    // ASSUMPTION (T3.3): an SMTP timeout ends as status 'failed' with the delivery-unknown result.
    act(6, 340, { to: ["tom.becker@juniper-co.example"], subject: "Thanks", body: "Hi Tom,\n\nThanks for the quick payment.\n\nBest, Maya" }, "low", [], "failed", DELIVERY_UNKNOWN),
  ];
  if (scenario === "r0") {
    rows.unshift(
      act(
        7,
        2,
        { to: ["rahul.verma@acme-logistics.example"], subject: "INV-0042", body: "Dear [[PERSON_1]],\n\nA reminder about INV-0042 for [[MONEY_1]].\n\nBest, Maya" },
        "high",
        [RISK_REASON_UNRESOLVED_PLACEHOLDER],
        "pending",
      ),
    );
  }
  return rows;
}

function ledgerRows(scenario: FixtureScenario): LedgerRow[] {
  if (scenario === "empty") return [];
  const r = (
    id: number,
    m: number,
    channel: LedgerRow["channel"],
    destination: string,
    model: string | null,
    escalated_from: string | null,
    entities_masked: number,
    latency_ms: number,
    cost_usd: number,
    status: LedgerRow["status"],
  ): LedgerRow => ({ id, ts: minutesAgo(m), channel, destination, model, escalated_from, entities_masked, latency_ms, cost_usd, status });
  return [
    r(6, 4, "llm", TF_HOST, NANO, null, 3, 60_400, 0, "error"),
    r(5, 5, "llm", TF_HOST, SUPER, null, 0, 0, 0, "blocked"),
    r(4, 7, "mail", "smtp.gmail.com", null, null, 0, 1_850, 0, "ok"),
    r(2, 12, "llm", TF_HOST, LIGHTNING, SUPER, 7, 21_300, 0.0071, "ok"),
    r(1, 12, "llm", TF_HOST, SUPER, null, 7, 9_800, 0.0013, "ok"),
    r(3, 299, "web", "api.tavily.com", null, null, 0, 1_240, 0, "ok"),
  ];
}

const LOCAL_REQ = {
  model: SUPER,
  messages: [
    { role: "system", content: "<Hermes system prompt with the memory snapshot and skills index>" },
    { role: "user", content: "Chase the Acme invoice" },
    {
      role: "tool",
      tool_call_id: "call_1",
      content:
        '<untrusted source="file">INV-0042 · Bill to: Acme Logistics, attn. Rahul Verma (CFO) · rahul.verma@acme-logistics.example · GSTIN: 29AAAPR4242M1ZD · UPI: mayarao@examplebank · Total due: $4,800</untrusted>',
    },
  ],
};
const SENT_REQ = {
  model: SUPER,
  messages: [
    { role: "system", content: "<Hermes system prompt with the memory snapshot and skills index>" },
    { role: "user", content: "Chase the [[ORG_1]] invoice" },
    {
      role: "tool",
      tool_call_id: "call_1",
      content:
        '<untrusted source="file">INV-0042 · Bill to: [[ORG_1]], attn. [[PERSON_1]] (CFO) · [[EMAIL_1]] · GSTIN: [[ACCOUNT_1]] · UPI: [[ACCOUNT_2]] · Total due: [[MONEY_1]]</untrusted>',
    },
  ],
};
const toolCallResponse = (to: string, subject: string, body: string) => ({
  choices: [
    {
      message: {
        role: "assistant",
        content: null,
        tool_calls: [
          { id: "call_2", type: "function", function: { name: "mcp_steward_mail_send", arguments: JSON.stringify({ to: [to], subject, body }) } },
        ],
      },
    },
  ],
});
const pretty = (v: unknown) => JSON.stringify(v, null, 2);

function ledgerDetail(row: LedgerRow): LedgerDetail {
  const base = { ...row, entity_kinds: {} };
  switch (row.channel) {
    case "web":
      return { ...base, request_redacted: pretty({ query: "warehouse robotics funding", max_results: 5 }), response_redacted: pretty({ results: [{ title: "Fixture result", url: "https://example.com/fixture-1" }] }), request_local: pretty({ query: "warehouse robotics funding", max_results: 5 }), response_local: pretty({ results: [{ title: "Fixture result", url: "https://example.com/fixture-1" }] }) };
    case "mail":
      return { ...base, request_redacted: pretty({ to: RAHUL_DRAFT.to, subject: `[Steward demo → ${RAHUL_DRAFT.to[0]}] ${RAHUL_DRAFT.subject}` }), response_redacted: null, request_local: pretty({ to: RAHUL_DRAFT.to, subject: `[Steward demo → ${RAHUL_DRAFT.to[0]}] ${RAHUL_DRAFT.subject}` }), response_local: null };
    default:
      break;
  }
  if (row.status === "blocked") {
    const blocked = pretty({ model: SUPER, messages: [{ role: "user", content: "Use token «BLOCKED:SECRET» to call the tools" }] });
    return { ...base, request_redacted: blocked, response_redacted: null, request_local: blocked, response_local: null };
  }
  return {
    ...base,
    entity_kinds: { ORG: 2, PERSON: 1, EMAIL: 1, ACCOUNT: 2, MONEY: 1 },
    request_redacted: pretty(SENT_REQ),
    response_redacted: row.status === "error" ? null : pretty(toolCallResponse("[[EMAIL_1]]", "INV-0042: payment reminder", "Dear [[PERSON_1]],\n\nThis is a reminder that INV-0042 for [[MONEY_1]] was due 12 days ago.\n\nBest, Maya")),
    request_local: pretty(LOCAL_REQ),
    response_local: row.status === "error" ? null : pretty(toolCallResponse(RAHUL_DRAFT.to[0], RAHUL_DRAFT.subject, RAHUL_DRAFT.body)),
  };
}

function ledgerStats(scenario: FixtureScenario): LedgerStatsResponse {
  const rows = ledgerRows(scenario);
  return {
    today: {
      calls: rows.length,
      entities_masked: rows.reduce((n, r) => n + r.entities_masked, 0),
      tokens: scenario === "empty" ? 0 : 61_420,
      cost_usd: rows.reduce((n, r) => n + r.cost_usd, 0),
      blocked: rows.filter((r) => r.status === "blocked").length,
    },
  };
}

const charCount = (entries: string[]) => [...entries.join(MEMORY_ENTRY_DELIMITER)].length;

function memory(scenario: FixtureScenario): MemoryResponse {
  const user = scenario === "memory_empty" ? [] : ["Maya prefers concise, friendly emails and signs off 'Best, Maya'"];
  const mem =
    scenario === "memory_empty"
      ? []
      : [
          "Invoices are in the workspace under invoices/, one file per invoice (invoices/INV-00NN.md). Payment terms are net 30, and a payment reminder goes out only after the due date has passed.",
          "Maya works Monday to Friday, 10:00 to 18:00 IST, and prefers to handle client email in the morning.",
          ...(scenario === "empty" ? [] : ["Rahul at Acme Logistics prefers short, formal emails."]),
        ];
  return {
    memory: { entries: mem, chars: charCount(mem), limit: MEMORY_LIMIT },
    user: { entries: user, chars: charCount(user), limit: USER_LIMIT },
  };
}

const SKILLS: Skill[] = [
  { name: "invoice-chase", description: "Find the overdue invoice and the latest thread, draft a reminder in the tone the client prefers, then queue mail_send for approval.", runnable: false },
  { name: "morning-brief", description: "Daily 08:00 IST: client mail needing replies, overdue invoices, and a Tavily search on each client's watch topics (never client names).", runnable: true },
];

function settings(): SettingsResponse {
  // reasoning_effort is set by DG-1; "low" is only the docs' example value.
  return { model_primary: SUPER, model_fallback: LIGHTNING, reasoning_effort: "low", mail_mode: "demo", shield: "on", zdr_note: ZDR_NOTE };
}

// --- request router ---------------------------------------------------------------------------

export interface FixtureResponse {
  status: number;
  body: unknown;
}

/** Thrown in the network_error scenario, like fetch() failing when steward-api is down. */
export class FixtureNetworkError extends TypeError {
  constructor() {
    super("Failed to fetch (fixture network_error)");
  }
}

// Mutable per-page-load state so approve/reject/PUT behave like the real API in mock mode.
const state: { scenario?: FixtureScenario; actions?: Action[]; memory?: MemoryResponse } = {};

function store(scenario: FixtureScenario) {
  if (state.scenario !== scenario) {
    state.scenario = scenario;
    state.actions = actions(scenario);
    state.memory = memory(scenario);
  }
  return state as Required<typeof state>;
}

const ok = (body: unknown): FixtureResponse => ({ status: 200, body });
const err = (status: number, detail: string): FixtureResponse => ({ status, body: { detail } });

export async function fixtureFetch(
  method: string,
  url: string,
  body: unknown,
  config: FixtureConfig,
): Promise<FixtureResponse> {
  if (config.slowMs > 0) await new Promise((resolve) => setTimeout(resolve, config.slowMs));
  const { scenario } = config;
  if (scenario === "network_error") throw new FixtureNetworkError();
  const s = store(scenario);
  const { pathname, searchParams } = new URL(url, "http://127.0.0.1:8787");
  const m = method.toUpperCase();
  const id = (re: RegExp) => Number(pathname.match(re)?.[1]);

  if (m === "GET" && pathname === "/api/health") return ok(health(scenario));
  if (m === "POST" && pathname === "/api/chat") {
    if (scenario === "model_unavailable") return err(502, CHAT_ERROR_MODEL_UNAVAILABLE);
    if (scenario === "chat_timeout") return err(504, CHAT_ERROR_STILL_WORKING);
    const req = body as { conversation_id?: number; message?: string };
    return ok({ conversation_id: req.conversation_id ?? 3, reply: `Fixture reply to: ${req.message ?? ""}`, message_id: 99 });
  }
  if (m === "GET" && pathname === "/api/conversations") return ok(conversations(scenario));
  if (m === "GET" && /^\/api\/conversations\/\d+$/.test(pathname)) {
    const detail = conversationDetail(id(/(\d+)$/));
    return detail ? ok(detail) : err(404, "Not Found");
  }
  if (m === "GET" && pathname === "/api/activity") {
    const after = Number(searchParams.get("after_id") ?? 0) || 0;
    return ok(activity(scenario).filter((a) => a.id > after));
  }
  if (m === "GET" && pathname === "/api/actions") {
    const all = searchParams.get("status") === "all";
    return ok(all ? s.actions : s.actions.filter((a) => a.status === "pending"));
  }
  const decide = pathname.match(/^\/api\/actions\/(\d+)\/(approve|reject)$/);
  if (m === "POST" && decide) {
    const action = s.actions.find((a) => a.id === Number(decide[1]));
    if (!action) return err(404, "Not Found");
    if (action.status !== "pending") return err(409, "Action already decided");
    if (decide[2] === "reject") {
      Object.assign(action, { status: "rejected", decided_at: new Date().toISOString() });
      return ok({ action });
    }
    const confirm = (body as { confirm_high?: boolean } | undefined)?.confirm_high === true;
    if (action.risk_reasons.includes(RISK_REASON_UNRESOLVED_PLACEHOLDER)) return err(409, RISK_REASON_UNRESOLVED_PLACEHOLDER);
    if (scenario === "approve_409" && !confirm) {
      Object.assign(action, { risk: "high", risk_reasons: ["overwrites existing file"] });
      return err(409, "Risk is now High; confirm to approve");
    }
    if (action.risk === "high" && !confirm) return err(409, "High-risk action needs confirm_high");
    Object.assign(action, { status: "executed", decided_at: new Date().toISOString(), result: null });
    return ok({ action });
  }
  if (m === "GET" && pathname === "/api/ledger/stats") return ok(ledgerStats(scenario));
  if (m === "GET" && pathname === "/api/ledger") {
    const channel = searchParams.get("channel");
    const limit = Number(searchParams.get("limit") ?? 50) || 50;
    return ok(ledgerRows(scenario).filter((r) => !channel || r.channel === channel).slice(0, limit));
  }
  if (m === "GET" && /^\/api\/ledger\/\d+$/.test(pathname)) {
    const row = ledgerRows(scenario).find((r) => r.id === id(/(\d+)$/));
    return row ? ok(ledgerDetail(row)) : err(404, "Not Found");
  }
  if (m === "GET" && pathname === "/api/memory") return ok(s.memory);
  if (m === "PUT" && pathname === "/api/memory") {
    const req = body as { file: "memory" | "user"; entries: string[] };
    const limit = req.file === "memory" ? MEMORY_LIMIT : USER_LIMIT;
    if (scenario === "memory_over_limit" || charCount(req.entries) > limit) return err(400, "Memory not saved — over the limit");
    s.memory[req.file] = { ...s.memory[req.file], entries: req.entries, chars: charCount(req.entries) } as never;
    return ok({ ok: true });
  }
  if (m === "GET" && pathname === "/api/skills") return ok(SKILLS);
  if (m === "POST" && pathname === "/api/skills/morning-brief/run") return ok({ ok: true });
  if (m === "GET" && pathname === "/api/briefs/latest") return ok(briefLatest(scenario));
  if (m === "GET" && pathname === "/api/contacts") return ok(contacts());
  if (m === "GET" && pathname === "/api/settings") return ok(settings());
  return err(404, "Not Found");
}
