"use client";

// Approvals (docs/03 §6.2): every side effect waits here. Pending oldest first, History newest
// first. Approve on a High card (or after a 409) goes through the confirm Dialog; R0 disables
// Approve; there is no retry anywhere, because an approval executes at most once.

import { useCallback, useEffect, useRef, useState } from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { ActionCard, isR0 } from "@/components/action-card";
import { useShellStatus } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api, errorDetail, type ApiResult } from "@/lib/api";
import { takeApprovalsTab } from "@/lib/nav-intent";
import type { Action, ActionConflictBody, ActionResponse, FilesWriteArgs } from "@/lib/types";
import { usePoll } from "@/lib/use-poll";

const HISTORY_POLL_MS = 3_000;
const CONFIRM_DETAILS = new Set(["High-risk action needs confirm_high", "Risk is now High; confirm to approve"]);

type Tab = "pending" | "history";
type Posting = { id: number; which: "approve" | "reject" } | null;

function conflictBody(result: Extract<ApiResult<unknown>, { ok: false }>): ActionConflictBody | null {
  const e = result.error;
  return e && typeof e === "object" && "action" in e ? (e as ActionConflictBody) : null;
}

function filePath(action: Action): string {
  try {
    return (JSON.parse(action.args_json) as FilesWriteArgs).path ?? "";
  } catch {
    return "";
  }
}

function CardSkeleton() {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-border bg-card p-4" aria-hidden>
      <div className="flex justify-between">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-5 w-16" />
      </div>
      <Skeleton className="h-4 w-2/3" />
      <Skeleton className="h-24 w-full" />
      <Skeleton className="h-9 w-1/2 self-end" />
    </div>
  );
}

export default function ApprovalsPage() {
  const { pending } = useShellStatus(); // the shell already polls ?status=pending every 3 s
  const all = usePoll(
    useCallback(() => api<Action[]>("GET", "/api/actions?status=all"), []),
    HISTORY_POLL_MS,
  );
  const [tab, setTab] = useState<Tab>("pending");
  const [posting, setPosting] = useState<Posting>(null);
  const [confirm, setConfirm] = useState<{ action: Action; reasons: string[] } | null>(null);
  const [confirmPosting, setConfirmPosting] = useState(false);
  const cancelRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    // An activity click on a decided action opens History (in-memory hand-off, no URL param).
    const requested = takeApprovalsTab();
    if (requested) setTab(requested);
  }, []);

  const refreshAll = useCallback(() => {
    void pending.refresh();
    void all.refresh();
  }, [pending, all]);

  async function approve(action: Action, confirmHigh: boolean) {
    if (confirmHigh) setConfirmPosting(true);
    else setPosting({ id: action.id, which: "approve" });
    const result = await api<ActionResponse>(
      "POST",
      `/api/actions/${action.id}/approve`,
      confirmHigh ? { confirm_high: true } : {},
    );
    setConfirmPosting(false);
    setPosting(null);

    if (result.ok) {
      setConfirm(null);
      const done = result.data.action;
      if (done.status === "executed") {
        toast.success(done.tool === "mail_send" ? "Sent" : `Written to ${filePath(done)}`);
      } else if (done.status === "failed") {
        toast.error(done.tool === "mail_send" ? "Not sent — see History" : "Not written — see History");
      }
      refreshAll();
      return;
    }
    if (result.status === 409) {
      const body = conflictBody(result);
      if (body && CONFIRM_DETAILS.has(body.detail)) {
        // Risk was recomputed at approve time: confirm against the server's current reasons.
        setConfirm({ action: body.action, reasons: body.action.risk_reasons });
      } else {
        setConfirm(null);
        // "unresolved placeholder" turns the card into R0 on refresh; the rest are toasted.
        if (body?.detail !== "unresolved placeholder") toast.error(errorDetail(result));
      }
      refreshAll();
      return;
    }
    setConfirm(null);
    if (result.status !== 0) toast.error(errorDetail(result)); // 404 "action not found", 4xx/5xx
    refreshAll();
  }

  function onApprove(action: Action) {
    if (isR0(action)) return;
    if (action.risk === "high") setConfirm({ action, reasons: action.risk_reasons });
    else void approve(action, false);
  }

  async function onReject(action: Action) {
    setPosting({ id: action.id, which: "reject" });
    const result = await api<ActionResponse>("POST", `/api/actions/${action.id}/reject`);
    setPosting(null);
    if (!result.ok && result.status !== 0) toast.error(errorDetail(result));
    refreshAll();
  }

  const pendingList = pending.error ? undefined : pending.data;
  const history = all.data?.filter((a) => a.status !== "pending");

  return (
    <div className="px-4 py-4 md:px-6">
      <div className="mx-auto flex max-w-[720px] flex-col gap-4">
        <h1 className="text-lg font-semibold">Approvals</h1>
        <Tabs value={tab} onValueChange={(v) => setTab(v as Tab)}>
          <TabsList>
            <TabsTrigger value="pending">
              Pending{pendingList && pendingList.length > 0 ? ` (${pendingList.length})` : ""}
            </TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
          </TabsList>

          <TabsContent value="pending" className="mt-4 flex flex-col gap-4">
            {pending.loading ? (
              <>
                <CardSkeleton />
                <CardSkeleton />
              </>
            ) : !pendingList || pendingList.length === 0 ? (
              pendingList && (
                <p className="text-sm text-muted-foreground">
                  Nothing waiting for you. Steward asks before it sends anything.
                </p>
              )
            ) : (
              pendingList.map((action) => (
                <ActionCard
                  key={action.id}
                  action={action}
                  posting={posting?.id === action.id ? posting.which : null}
                  onApprove={() => onApprove(action)}
                  onReject={() => void onReject(action)}
                />
              ))
            )}
          </TabsContent>

          <TabsContent value="history" className="mt-4 flex flex-col gap-4">
            {all.loading ? (
              <>
                <CardSkeleton />
                <CardSkeleton />
              </>
            ) : !history || history.length === 0 ? (
              history && <p className="text-sm text-muted-foreground">No decisions yet.</p>
            ) : (
              history.map((action) => <ActionCard key={action.id} action={action} />)
            )}
          </TabsContent>
        </Tabs>
      </div>

      <Dialog
        open={confirm !== null}
        onOpenChange={(open) => {
          if (!open && !confirmPosting) setConfirm(null);
        }}
      >
        <DialogContent
          onOpenAutoFocus={(e) => {
            e.preventDefault();
            cancelRef.current?.focus(); // Cancel has the default focus
          }}
        >
          <DialogHeader>
            <DialogTitle>Approve a High-risk action?</DialogTitle>
            <DialogDescription>
              {confirm ? `action #${confirm.action.id} · ${confirm.action.tool}` : ""}
            </DialogDescription>
          </DialogHeader>
          <ul className="flex flex-col gap-1 text-sm break-words">
            {confirm?.reasons.map((reason) => <li key={reason}>{reason}</li>)}
          </ul>
          <DialogFooter>
            <Button ref={cancelRef} variant="outline" onClick={() => setConfirm(null)} disabled={confirmPosting}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => confirm && void approve(confirm.action, true)}
              disabled={confirmPosting}
            >
              {confirmPosting && <Loader2 className="animate-spin" aria-hidden />}
              Approve anyway
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
