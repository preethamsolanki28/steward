"use client";

// LedgerDiff (docs/03 §6.3; NEVER cut): the receipt for one outbound request. Left "On your Mac"
// is the re-identified view (computed on read, never stored); right is exactly what left the Mac,
// with placeholders as teal chips and blocked spans as red chips. By default only the last user
// turn, the tool traffic after it and the response are shown; "Show full payload" adds the rest.

import { useMemo, useState } from "react";

import { ChipText } from "@/components/placeholder-chip";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { fmtCost, fmtLatency, fmtLocalTime, stripTool } from "@/lib/format";
import type { LedgerDetail, LedgerRow } from "@/lib/types";
import { cn } from "@/lib/utils";

const ZDR = "ZDR: enabled in our Nebius org (account setting)";

type Json = Record<string, unknown>;

function parse(raw: string | null): unknown {
  if (raw === null) return null;
  try {
    return JSON.parse(raw) as unknown;
  } catch {
    return raw; // stored as plain text
  }
}

const isObj = (v: unknown): v is Json => typeof v === "object" && v !== null && !Array.isArray(v);

/** Message content may be a string, null, or OpenAI content parts. */
function text(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content.map((p) => (isObj(p) && typeof p.text === "string" ? p.text : "")).join("");
  }
  return content == null ? "" : JSON.stringify(content);
}

function prettyArgs(args: unknown): string {
  if (typeof args !== "string") return JSON.stringify(args, null, 2);
  try {
    return JSON.stringify(JSON.parse(args), null, 2);
  } catch {
    return args;
  }
}

function toolCallLines(calls: unknown): string[] {
  if (!Array.isArray(calls)) return [];
  return calls.map((c) => {
    const fn = isObj(c) && isObj(c.function) ? c.function : {};
    return `${stripTool(String(fn.name ?? "?"))} ${prettyArgs(fn.arguments)}`;
  });
}

/** OpenAI chat request → the last user message and everything after it. */
function llmRequestView(req: unknown): string {
  if (!isObj(req)) return text(req);
  if (typeof req.method === "string" && typeof req.path === "string" && !("messages" in req)) {
    return `${req.method} ${req.path}`; // a /v1 path Hermes probed (404, never forwarded)
  }
  if (typeof req.error === "string") return req.error;
  const messages = Array.isArray(req.messages) ? req.messages.filter(isObj) : [];
  const names = new Map<string, string>();
  for (const m of messages) {
    if (Array.isArray(m.tool_calls)) {
      for (const c of m.tool_calls) {
        if (isObj(c) && typeof c.id === "string" && isObj(c.function)) names.set(c.id, String(c.function.name ?? ""));
      }
    }
  }
  let start = -1;
  messages.forEach((m, i) => {
    if (m.role === "user") start = i;
  });
  const scope = start >= 0 ? messages.slice(start) : messages.slice(-3);
  const parts: string[] = [];
  for (const m of scope) {
    if (m.role === "tool") {
      const name = stripTool(names.get(String(m.tool_call_id ?? "")) ?? String(m.name ?? "tool"));
      parts.push(`tool ${name}: ${text(m.content)}`);
    } else {
      const body = text(m.content).trim();
      if (body) parts.push(`${String(m.role)}: ${body}`);
      parts.push(...toolCallLines(m.tool_calls));
    }
  }
  if (Array.isArray(req.steward_blocked_tools)) parts.push(`blocked tools: ${req.steward_blocked_tools.join(", ")}`);
  return parts.join("\n\n");
}

function llmResponseView(res: unknown): string {
  if (!isObj(res)) return text(res);
  if ("error" in res) return `error: ${typeof res.error === "string" ? res.error : JSON.stringify(res.error)}`;
  const choice = Array.isArray(res.choices) && isObj(res.choices[0]) ? res.choices[0] : null;
  const message = choice && isObj(choice.message) ? choice.message : null;
  if (!message) return JSON.stringify(res, null, 2);
  return [text(message.content).trim(), ...toolCallLines(message.tool_calls)].filter(Boolean).join("\n\n");
}

function webRequestView(req: unknown): string {
  return isObj(req) && typeof req.query === "string" ? `query: ${req.query}` : text(req);
}

function webResponseView(res: unknown): string {
  if (!Array.isArray(res)) return text(res);
  return res.map((r) => (isObj(r) ? `${String(r.title ?? "")} — ${String(r.url ?? "")}` : text(r))).join("\n");
}

function mailRequestView(req: unknown): string {
  if (!isObj(req)) return text(req);
  const to = Array.isArray(req.to) ? req.to.join(", ") : String(req.to ?? "");
  return `To: ${to}\nSubject: ${String(req.subject ?? "")}\n\n${String(req.body ?? "")}`;
}

function mailResponseView(res: unknown): string {
  return isObj(res) && typeof res.result === "string" ? res.result : text(res);
}

function defaultView(channel: LedgerRow["channel"], raw: string | null, part: "request" | "response"): string | null {
  if (raw === null) return null;
  const v = parse(raw);
  if (channel === "web") return part === "request" ? webRequestView(v) : webResponseView(v);
  if (channel === "mail") return part === "request" ? mailRequestView(v) : mailResponseView(v);
  return part === "request" ? llmRequestView(v) : llmResponseView(v);
}

function fullView(raw: string | null): string | null {
  if (raw === null) return null;
  const v = parse(raw);
  return typeof v === "string" ? v : JSON.stringify(v, null, 2);
}

export function diffHeader(row: LedgerRow): string {
  return row.channel === "llm" ? `${row.model ?? "—"} · ${row.destination} · ${ZDR}` : row.destination;
}

export function diffMeta(row: LedgerRow): string {
  const latency = row.status === "blocked" ? "—" : fmtLatency(row.latency_ms);
  return [
    fmtLocalTime(row.ts, true),
    `${row.entities_masked} identifiers masked`,
    latency,
    fmtCost(row.cost_usd),
    row.status,
  ].join(" · ");
}

function rightLabel(row: LedgerRow): string {
  if (row.status === "blocked") return "Not sent — blocked";
  if (row.channel === "web") return "Sent in clear to Tavily — Tavily's own retention applies";
  if (row.channel === "mail") return "Sent by email";
  return "Sent to Nebius";
}

function Body({ value, chips, full }: { value: string | null; chips: boolean; full: boolean }) {
  const pre = (
    <pre className="font-mono text-[13px] leading-5 whitespace-pre-wrap [overflow-wrap:anywhere]">
      {value === null || value === "" ? (
        <span className="text-muted-foreground">—</span>
      ) : chips ? (
        <ChipText text={value} />
      ) : (
        value
      )}
    </pre>
  );
  return full ? <ScrollArea className="[&>[data-slot=scroll-area-viewport]]:max-h-[60vh]">{pre}</ScrollArea> : pre;
}

function Column({
  label,
  labelClass,
  request,
  response,
  showResponse,
  chips,
  full,
}: {
  label: string;
  labelClass?: string;
  request: string | null;
  response: string | null;
  showResponse: boolean;
  chips: boolean;
  full: boolean;
}) {
  return (
    <section className="flex min-w-0 flex-col gap-2">
      <h3 className={cn("text-sm font-semibold", labelClass)}>{label}</h3>
      <p className="text-xs tracking-wide text-muted-foreground uppercase">Request</p>
      <Body value={request} chips={chips} full={full} />
      {showResponse && (
        <>
          <Separator className="my-1" />
          <p className="text-xs tracking-wide text-muted-foreground uppercase">Response</p>
          <Body value={response} chips={chips} full={full} />
        </>
      )}
    </section>
  );
}

export function LedgerDiffSkeleton() {
  return (
    <div className="grid gap-6 md:grid-cols-2" aria-label="Loading request">
      {[0, 1].map((i) => (
        <div key={i} className="flex flex-col gap-2">
          <Skeleton className="h-5 w-28" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-11/12" />
          <Skeleton className="h-4 w-4/5" />
          <Skeleton className="h-4 w-full" />
        </div>
      ))}
    </div>
  );
}

export function LedgerDiff({ detail }: { detail: LedgerDetail }) {
  const [full, setFull] = useState(false);
  const blocked = detail.status === "blocked";

  const views = useMemo(() => {
    const pick = (raw: string | null, part: "request" | "response") =>
      full ? fullView(raw) : defaultView(detail.channel, raw, part);
    return {
      localReq: pick(detail.request_local, "request"),
      localRes: pick(detail.response_local, "response"),
      sentReq: pick(detail.request_redacted, "request"),
      sentRes: pick(detail.response_redacted, "response"),
    };
  }, [detail, full]);

  return (
    <div className="flex flex-col gap-4">
      <div className="grid gap-6 md:grid-cols-2">
        <Column
          label="On your Mac"
          request={views.localReq}
          response={views.localRes}
          showResponse={!blocked}
          chips={false}
          full={full}
        />
        <Column
          label={rightLabel(detail)}
          labelClass={blocked ? "text-destructive" : undefined}
          request={views.sentReq}
          response={views.sentRes}
          showResponse={!blocked}
          chips
          full={full}
        />
      </div>
      <div>
        <Button variant="link" className="h-auto min-h-11 px-0 md:min-h-0" onClick={() => setFull((f) => !f)}>
          {full ? "Hide full payload" : "Show full payload"}
        </Button>
      </div>
    </div>
  );
}
