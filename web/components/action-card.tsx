"use client";

// ActionCard (docs/03 §5): one Approval Gate action. Fields come from args_json, because that is
// exactly what will be sent; leftover [[KIND_n]] placeholders render as chips so R0 is visible.

import { AlertCircle, AlertTriangle, Loader2 } from "lucide-react";

import { ChipText } from "@/components/placeholder-chip";
import { Alert, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { fmtLocalTime } from "@/lib/format";
import {
  DELIVERY_UNKNOWN,
  RISK_REASON_UNRESOLVED_PLACEHOLDER,
  type Action,
  type FilesWriteArgs,
  type MailSendArgs,
} from "@/lib/types";

const STATUS_BADGE = {
  executed: { label: "Executed", variant: "success-outline" },
  rejected: { label: "Rejected", variant: "neutral" },
  failed: { label: "Failed", variant: "danger" },
  approved: { label: "Approved", variant: "neutral" },
  pending: { label: "Pending", variant: "neutral" },
} as const;

function parseArgs(action: Action): Partial<MailSendArgs & FilesWriteArgs> | null {
  try {
    const parsed: unknown = JSON.parse(action.args_json);
    return parsed && typeof parsed === "object" ? (parsed as Partial<MailSendArgs & FilesWriteArgs>) : null;
  } catch {
    return null;
  }
}

/** Monospace preview capped at ~12 lines; scrolls inside. */
function Preview({ text }: { text: string }) {
  return (
    <ScrollArea className="rounded-md border border-border bg-background [&>[data-slot=scroll-area-viewport]]:max-h-60">
      <pre className="p-3 font-mono text-[13px] leading-5 break-words whitespace-pre-wrap">
        <ChipText text={text} />
      </pre>
    </ScrollArea>
  );
}

export function isR0(action: Action): boolean {
  return action.risk_reasons.includes(RISK_REASON_UNRESOLVED_PLACEHOLDER);
}

interface ActionCardProps {
  action: Action;
  /** Which button is posting, if any; both are disabled while either posts. */
  posting?: "approve" | "reject" | null;
  onApprove?: () => void;
  onReject?: () => void;
}

export function ActionCard({ action, posting = null, onApprove, onReject }: ActionCardProps) {
  const args = parseArgs(action);
  const pending = action.status === "pending";
  const high = action.risk === "high";
  const r0 = isR0(action);
  const deliveryUnknown = action.status === "failed" && action.result === DELIVERY_UNKNOWN;
  const badge = STATUS_BADGE[action.status];

  const approve = (
    <Button className="flex-1 md:flex-none" onClick={onApprove} disabled={posting !== null || r0}>
      {posting === "approve" && <Loader2 className="animate-spin" aria-hidden />}
      Approve
    </Button>
  );

  return (
    <Card className="gap-3 px-4" aria-label={`action #${action.id}`}>
      <div className="flex items-center gap-2">
        <span className="font-mono text-sm font-medium">{action.tool}</span>
        <Badge variant={high ? "danger" : "success-outline"} className="ml-auto">
          {high ? "High risk" : "Low risk"}
        </Badge>
      </div>

      {args === null ? (
        <Preview text={action.args_json} />
      ) : action.tool === "mail_send" ? (
        <>
          <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
            <dt className="text-muted-foreground">To</dt>
            <dd className="min-w-0 font-mono text-xs leading-5 font-medium break-words">
              <ChipText text={(args.to ?? []).join(", ")} />
            </dd>
            <dt className="text-muted-foreground">Subject</dt>
            <dd className="min-w-0 break-words">
              <ChipText text={args.subject ?? ""} />
            </dd>
          </dl>
          {action.risk_reasons.length > 0 && <Reasons reasons={action.risk_reasons} high={high} />}
          <Preview text={args.body ?? ""} />
        </>
      ) : (
        <>
          <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
            <dt className="text-muted-foreground">Path</dt>
            <dd className="min-w-0 font-mono text-xs leading-5 font-medium break-words">
              <ChipText text={args.path ?? ""} />
            </dd>
          </dl>
          {action.risk_reasons.length > 0 && <Reasons reasons={action.risk_reasons} high={high} />}
          <Preview text={args.content ?? ""} />
        </>
      )}

      {!pending && action.result && action.status === "failed" && (
        <Alert variant={deliveryUnknown ? "warning" : "destructive"}>
          {deliveryUnknown ? <AlertTriangle aria-hidden /> : <AlertCircle aria-hidden />}
          <AlertTitle className="font-normal break-words">{action.result}</AlertTitle>
        </Alert>
      )}
      {!pending && action.result && action.status !== "failed" && (
        <p className="text-xs break-words text-muted-foreground">{action.result}</p>
      )}

      <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
        <span className="text-xs text-muted-foreground tabular-nums">
          <span className="font-mono font-medium">action #{action.id}</span> · {fmtLocalTime(action.created_at)}
        </span>
        {pending ? (
          <div className="flex w-full gap-2 md:ml-auto md:w-auto">
            <Button variant="outline" className="flex-1 md:flex-none" onClick={onReject} disabled={posting !== null}>
              {posting === "reject" && <Loader2 className="animate-spin" aria-hidden />}
              Reject
            </Button>
            {r0 ? (
              <Tooltip>
                <TooltipTrigger asChild>
                  <span tabIndex={0} className="flex flex-1 md:flex-none">
                    {approve}
                  </span>
                </TooltipTrigger>
                <TooltipContent>{RISK_REASON_UNRESOLVED_PLACEHOLDER}</TooltipContent>
              </Tooltip>
            ) : (
              approve
            )}
          </div>
        ) : (
          <div className="flex items-center gap-2 md:ml-auto">
            <Badge variant={badge.variant}>{badge.label}</Badge>
            {action.decided_at && (
              <span className="text-xs text-muted-foreground tabular-nums">{fmtLocalTime(action.decided_at)}</span>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

function Reasons({ reasons, high }: { reasons: string[]; high: boolean }) {
  // Low has no Alert (docs/03 §5); reasons only accompany High in practice.
  if (!high) return null;
  return (
    <Alert variant="destructive">
      <AlertCircle aria-hidden />
      <AlertTitle className="font-normal break-words">{reasons.join(" · ")}</AlertTitle>
    </Alert>
  );
}
