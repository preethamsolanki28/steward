"use client";

// ActivityRail (docs/03 §5): one row per audit_events item, newest at the bottom. Summaries are
// rendered exactly as steward-api wrote them (the model label is never recomputed); only the
// mcp__steward__ prefix is stripped from tool names.

import { useLayoutEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Brain,
  CalendarClock,
  Send,
  ShieldAlert,
  ShieldCheck,
  Wrench,
  type LucideIcon,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { fmtLocalTime, stripTool } from "@/lib/format";
import { requestApprovalsTab } from "@/lib/nav-intent";
import type { ActivityItem } from "@/lib/types";
import { cn } from "@/lib/utils";

const ICON: Record<ActivityItem["kind"], LucideIcon> = {
  tool_call: Wrench,
  egress: Send,
  memory_edit: Brain,
  action_created: ShieldCheck,
  action_decided: ShieldCheck,
  action_executed: ShieldCheck,
  policy_block: ShieldAlert,
  skill_run: CalendarClock,
};

const BLOCK_COPY = "Blocked: identifier would have left the Mac";
const NEAR_BOTTOM_PX = 48;

/** Unified diff with + green, - red and the ---/+++/@@ headers muted. */
function MemoryDiff({ diff }: { diff: string }) {
  return (
    <pre className="font-mono text-[13px] leading-5 break-words whitespace-pre-wrap">
      {diff.split("\n").map((line, i) => (
        <div
          key={i}
          className={cn(
            /^(\+\+\+|---|@@)/.test(line)
              ? "text-muted-foreground"
              : line.startsWith("+")
                ? "text-success"
                : line.startsWith("-")
                  ? "text-destructive"
                  : undefined,
          )}
        >
          {line || " "}
        </div>
      ))}
    </pre>
  );
}

interface ActivityRailProps {
  items: ActivityItem[];
  loading: boolean;
  /** skill_run click: expand and scroll to the BriefCard. */
  onShowBrief: () => void;
  /** Called before navigating or opening the brief (closes the rail's Sheet on small screens). */
  onNavigate?: () => void;
}

export function ActivityRail({ items, loading, onShowBrief, onNavigate }: ActivityRailProps) {
  const router = useRouter();
  const scroller = useRef<HTMLDivElement>(null);
  const stick = useRef(true); // follow new rows only while the user is at the bottom
  const [diff, setDiff] = useState<string | null>(null);

  useLayoutEffect(() => {
    const el = scroller.current;
    if (el && stick.current) el.scrollTop = el.scrollHeight;
  }, [items.length, loading]);

  function go(href: string) {
    onNavigate?.();
    router.push(href);
  }

  function onClick(item: ActivityItem): (() => void) | undefined {
    switch (item.kind) {
      case "egress":
        return item.ref_id !== null ? () => go(`/ledger?id=${item.ref_id}`) : undefined;
      case "policy_block":
        return item.ref_table === "egress_events" && item.ref_id !== null
          ? () => go(`/ledger?id=${item.ref_id}`)
          : undefined;
      case "action_created":
        return () => {
          requestApprovalsTab("pending");
          go("/approvals");
        };
      case "action_decided":
      case "action_executed":
        return () => {
          requestApprovalsTab("history");
          go("/approvals");
        };
      case "skill_run":
        return () => {
          onNavigate?.();
          onShowBrief();
        };
      default:
        return undefined;
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-col">
      <h2 className="px-4 pt-4 pb-2 text-base font-semibold">Activity</h2>
      <div
        ref={scroller}
        onScroll={(e) => {
          const el = e.currentTarget;
          stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < NEAR_BOTTOM_PX;
        }}
        className="min-h-0 flex-1 overflow-y-auto px-2 pb-4"
        aria-live="polite"
        aria-busy={loading}
      >
        {loading ? (
          <div className="flex flex-col gap-3 px-2 pt-1" aria-label="Loading activity">
            {Array.from({ length: 4 }, (_, i) => (
              <Skeleton key={i} className="h-5 w-full" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <p className="px-2 text-sm text-muted-foreground">No activity yet.</p>
        ) : (
          <ol className="flex flex-col">
            {items.map((item) => {
              const Icon = ICON[item.kind];
              const blocked = item.kind === "policy_block";
              const tool = item.kind === "tool_call";
              const text = tool ? stripTool(item.summary) : blocked ? BLOCK_COPY : item.summary;
              const click = onClick(item);
              const content = (
                <>
                  <Icon
                    className={cn("mt-0.5 size-4 shrink-0", blocked ? "text-destructive" : "text-muted-foreground")}
                    aria-hidden
                  />
                  <span
                    className={cn(
                      "min-w-0 flex-1 break-words",
                      tool && "font-mono text-xs leading-5 text-muted-foreground",
                      blocked && "font-medium text-destructive",
                    )}
                  >
                    {text}
                    {item.kind === "memory_edit" && (
                      <>
                        {" — "}
                        <Button
                          variant="link"
                          className="h-auto min-h-0 p-0 text-sm md:h-auto"
                          onClick={() => setDiff(item.detail ?? "")}
                        >
                          review
                        </Button>
                      </>
                    )}
                  </span>
                  <time dateTime={item.ts} className="shrink-0 text-xs leading-5 text-muted-foreground tabular-nums">
                    {fmtLocalTime(item.ts, true)}
                  </time>
                </>
              );
              const row = "flex w-full items-start gap-2 rounded-md px-2 py-1.5 text-left text-sm";
              return (
                <li key={item.id}>
                  {click ? (
                    <button
                      type="button"
                      onClick={click}
                      className={cn(
                        row,
                        "min-h-11 hover:bg-background focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none md:min-h-0",
                      )}
                    >
                      {content}
                    </button>
                  ) : (
                    <div className={row}>{content}</div>
                  )}
                </li>
              );
            })}
          </ol>
        )}
      </div>

      <Sheet open={diff !== null} onOpenChange={(o) => !o && setDiff(null)}>
        <SheetContent side="right" className="w-full gap-0 sm:max-w-lg">
          <SheetHeader>
            <SheetTitle>Memory changed by Steward</SheetTitle>
            <SheetDescription>What Steward changed in its memory, as a diff.</SheetDescription>
          </SheetHeader>
          <div className="min-h-0 flex-1 overflow-y-auto px-4">
            <MemoryDiff diff={diff ?? ""} />
          </div>
          <div className="border-t border-border p-4">
            <Button
              variant="outline"
              onClick={() => {
                setDiff(null);
                go("/memory");
              }}
            >
              Open Memory
            </Button>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
