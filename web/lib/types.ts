// Request/response types for the steward-api control plane, mirroring docs/02 §6 (API endpoints)
// and the §5 tables they read from. Field names are exactly as in the docs.
//
// Where docs/02 left a wire detail open, the choice was marked "ASSUMPTION (Tx.y)"; the backend
// tasks have since confirmed each one against the live API (verified 2026-10-03, M4/T4.1).

/** ISO-8601 timestamp. Steward rows are UTC ("…+00:00"); Hermes job times are "+05:30". */
export type IsoTime = string;

// ---------------------------------------------------------------------------
// GET /api/health
// ---------------------------------------------------------------------------

export type UpDown = "up" | "down";
export type UpDownNoKey = "up" | "down" | "no_key";

export interface HealthResponse {
  ok: boolean;
  hermes: UpDown;
  token_factory: UpDownNoKey;
  tavily: UpDownNoKey;
  /** MAIL_MODE; "demo" is the only MVP mode. */
  mail_mode: string;
  model_primary: string;
}

// ---------------------------------------------------------------------------
// POST /api/chat, GET /api/conversations, GET /api/conversations/{id}
// ---------------------------------------------------------------------------

export interface ChatRequest {
  conversation_id?: number;
  message: string;
}

export interface ChatResponse {
  conversation_id: number;
  reply: string;
  message_id: number;
}

export interface ConversationSummary {
  id: number;
  title: string;
  updated_at: IsoTime;
}

export type MessageRole = "user" | "assistant";

export interface Message {
  id: number;
  role: MessageRole;
  content: string;
  created_at: IsoTime;
}

export interface ConversationDetail {
  id: number;
  title: string;
  messages: Message[];
}

/** Error body for non-2xx responses: FastAPI's `{detail}` (verified, T1.1). */
export interface ApiError {
  detail: string;
}

/** POST /api/chat 502 ("Model unavailable…") and 504 ("Still working…") also carry the
 *  conversation the user message was stored in (verified, T1.6). */
export interface ChatErrorBody extends ApiError {
  conversation_id?: number;
}

/** 409 from approve/reject: the action as it now stands (verified, T3.3). */
export interface ActionConflictBody extends ApiError {
  action: Action;
}

/** FastAPI request-validation error (422). */
export interface ValidationErrorBody {
  detail: Array<{ loc: Array<string | number>; msg: string; type: string }>;
}

export type ApiErrorBody = ChatErrorBody | ActionConflictBody | ValidationErrorBody | ApiError;

export const CHAT_ERROR_MODEL_UNAVAILABLE = "Model unavailable — this turn did not complete";
export const CHAT_ERROR_STILL_WORKING = "Still working — check Approvals and Activity";

// ---------------------------------------------------------------------------
// GET /api/activity?after_id=  (audit_events rows)
// ---------------------------------------------------------------------------

export type AuditKind =
  | "tool_call"
  | "egress"
  | "policy_block"
  | "action_created"
  | "action_decided"
  | "action_executed"
  | "memory_edit"
  | "skill_run";

export interface ActivityItem {
  id: number;
  ts: IsoTime;
  kind: AuditKind;
  summary: string;
  /** e.g. the unified memory diff for memory_edit. */
  detail: string | null;
  ref_table: string | null;
  ref_id: number | null;
}

// ---------------------------------------------------------------------------
// Actions (Approval Gate): GET /api/actions, POST /api/actions/{id}/approve|reject
// ---------------------------------------------------------------------------

export type ActionTool = "mail_send" | "files_write";
export type Risk = "low" | "high";
export type ActionStatus = "pending" | "approved" | "rejected" | "executed" | "failed";
export type ActionsFilter = "pending" | "all";

/** Arguments of mail_send(to, subject, body, in_reply_to?), as stored in args_json. */
export interface MailSendArgs {
  to: string[];
  subject: string;
  body: string;
  in_reply_to?: string;
}

/** Arguments of files_write(path, content), as stored in args_json. */
export interface FilesWriteArgs {
  path: string;
  content: string;
}

/** An `actions` row (docs/02 §5). */
export interface Action {
  id: number;
  created_at: IsoTime;
  tool: ActionTool;
  /** Exact arguments, sent byte-for-byte as previewed; parse as MailSendArgs | FilesWriteArgs. */
  args_json: string;
  preview: string;
  risk: Risk;
  /** Served parsed (verified, T3.3); shown verbatim, joined with " · ". */
  risk_reasons: string[];
  status: ActionStatus;
  decided_at: IsoTime | null;
  /** e.g. error text or "delivery unknown — check Sent before retrying". */
  result: string | null;
}

export interface ApproveRequest {
  confirm_high?: boolean;
}

/** `{action}` in docs/02 §6, wrapped as `{ action: Action }` (verified, T3.3). */
export interface ActionResponse {
  action: Action;
}

export const DELIVERY_UNKNOWN = "delivery unknown — check Sent before retrying";
export const RISK_REASON_UNRESOLVED_PLACEHOLDER = "unresolved placeholder";

// ---------------------------------------------------------------------------
// Ledger: GET /api/ledger, GET /api/ledger/{id}, GET /api/ledger/stats
// ---------------------------------------------------------------------------

export type LedgerChannel = "llm" | "web" | "mail";
export type LedgerStatus = "ok" | "error" | "blocked";

export interface LedgerRow {
  id: number;
  ts: IsoTime;
  channel: LedgerChannel;
  destination: string;
  model: string | null;
  escalated_from: string | null;
  entities_masked: number;
  latency_ms: number;
  cost_usd: number;
  status: LedgerStatus;
}

export interface LedgerDetail extends LedgerRow {
  /** Request as sent (llm: placeholders); blocked rows carry «BLOCKED:KIND» spans. */
  request_redacted: string;
  response_redacted: string | null;
  /** Re-identified on read, never stored. */
  request_local: string;
  response_local: string | null;
  /** Served parsed as counts per kind, e.g. {"PERSON": 1, "MONEY": 1} (verified, T2.4). */
  entity_kinds: Partial<Record<VaultKind, number>>;
}

export interface LedgerStatsResponse {
  today: {
    calls: number;
    entities_masked: number;
    tokens: number;
    cost_usd: number;
    blocked: number;
  };
}

/** Placeholder kinds minted by the Shield (vault.kind). */
export type VaultKind = "PERSON" | "EMAIL" | "ORG" | "DOMAIN" | "PHONE" | "ACCOUNT" | "MONEY";

/** Kinds that can appear in a «BLOCKED:KIND» span of a blocked ledger row. */
export type BlockedKind = VaultKind | "SECRET" | "IDENTIFIER";

// ---------------------------------------------------------------------------
// Memory: GET /api/memory, PUT /api/memory
// ---------------------------------------------------------------------------

export const MEMORY_LIMIT = 2200;
export const USER_LIMIT = 1375;
export const MEMORY_ENTRY_DELIMITER = "\n§\n";

export interface MemoryFile<L extends number> {
  entries: string[];
  chars: number;
  limit: L;
}

export interface MemoryResponse {
  memory: MemoryFile<typeof MEMORY_LIMIT>;
  user: MemoryFile<typeof USER_LIMIT>;
}

export type MemoryFileName = "memory" | "user";

export interface MemoryPutRequest {
  file: MemoryFileName;
  entries: string[];
}

export interface OkResponse {
  ok: boolean;
}

// ---------------------------------------------------------------------------
// Skills and briefs: GET /api/skills, POST /api/skills/morning-brief/run, GET /api/briefs/latest
// ---------------------------------------------------------------------------

export interface Skill {
  name: string;
  description: string;
  runnable: boolean;
}

export interface Brief {
  id: number;
  created_at: IsoTime;
  content_md: string;
}

export interface BriefJob {
  last_run_at: IsoTime | null;
  /** From Hermes GET /api/jobs/{id}: Hermes' own status string, "ok" or "error" (verified, T1.7). */
  last_status: string | null;
  next_run_at: IsoTime | null;
}

export interface BriefLatestResponse {
  brief: Brief | null;
  job: BriefJob | null;
}

// ---------------------------------------------------------------------------
// Read-only: GET /api/contacts, GET /api/settings
// ---------------------------------------------------------------------------

export type ContactSource = "seed" | "mail";

/** A `contacts` row (docs/02 §5); trusted is 0/1 like the column. */
export interface Contact {
  id: number;
  /** null for addresses seen only in mail headers. */
  name: string | null;
  email: string;
  org: string | null;
  trusted: 0 | 1;
  source: ContactSource;
  created_at: IsoTime;
}

export const ZDR_NOTE =
  "ZDR is an org-level setting in your Token Factory profile; Steward cannot verify it";

export interface SettingsResponse {
  model_primary: string;
  model_fallback: string;
  reasoning_effort: string;
  mail_mode: string;
  shield: "on";
  zdr_note: typeof ZDR_NOTE;
}
