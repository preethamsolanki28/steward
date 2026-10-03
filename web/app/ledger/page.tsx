"use client";

// Ledger (docs/03 §6.3): every request sent to an AI or search provider, newest first. A row opens
// its LedgerDiff in a right Sheet; /ledger?id=<id> deep-links to it (Activity links here).

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { diffHeader, diffMeta, LedgerDiff, LedgerDiffSkeleton } from "@/components/ledger-diff";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { api, errorDetail } from "@/lib/api";
import { fmtCost, fmtLatency, fmtLocalTime, modelShort } from "@/lib/format";
import type { LedgerDetail, LedgerRow, LedgerStatsResponse } from "@/lib/types";
import { usePoll } from "@/lib/use-poll";
import { cn } from "@/lib/utils";

const LEDGER_POLL_MS = 5_000;

function StatTile({ label, value, danger }: { label: string; value: string | undefined; danger?: boolean }) {
  return (
    <Card className="gap-1 px-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      {value === undefined ? (
        <Skeleton className="h-8 w-16" />
      ) : (
        <p className={cn("text-2xl font-semibold tabular-nums", danger && "text-destructive")}>{value}</p>
      )}
      <p className="text-xs text-muted-foreground">today (IST)</p>
    </Card>
  );
}

function Status({ status }: { status: LedgerRow["status"] }) {
  if (status === "blocked") return <Badge variant="blocked">blocked</Badge>;
  if (status === "error") {
    return (
      <span className="inline-flex items-center gap-1.5">
        <span className="size-2 rounded-full bg-warning" aria-hidden />
        error
      </span>
    );
  }
  return <span className="text-muted-foreground">ok</span>;
}

function Model({ row }: { row: LedgerRow }) {
  if (row.channel !== "llm" || row.model === null) return <span className="text-muted-foreground">—</span>;
  if (!row.escalated_from) return <>{modelShort(row.model)}</>;
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Badge variant="neutral" className="font-mono" tabIndex={0}>
          ↑ {modelShort(row.model)}
        </Badge>
      </TooltipTrigger>
      <TooltipContent>Escalated from {row.escalated_from}</TooltipContent>
    </Tooltip>
  );
}

function LedgerScreen() {
  const router = useRouter();
  const params = useSearchParams();
  const idParam = params.get("id");
  const openId = idParam && /^\d+$/.test(idParam) ? Number(idParam) : null;

  const rows = usePoll(
    useCallback(() => api<LedgerRow[]>("GET", "/api/ledger?limit=50"), []),
    LEDGER_POLL_MS,
  );
  const stats = usePoll(
    useCallback(() => api<LedgerStatsResponse>("GET", "/api/ledger/stats"), []),
    LEDGER_POLL_MS,
  );

  const [detail, setDetail] = useState<LedgerDetail | null>(null);
  const loadToken = useRef(0);

  const close = useCallback(() => router.replace("/ledger", { scroll: false }), [router]);
  const open = (id: number) => router.replace(`/ledger?id=${id}`, { scroll: false });

  useEffect(() => {
    // The Sheet follows ?id=, so a deep link opens a row even if it is not in the latest 50.
    const token = ++loadToken.current;
    setDetail(null);
    if (openId === null) return;
    void api<LedgerDetail>("GET", `/api/ledger/${openId}`).then((result) => {
      if (token !== loadToken.current) return;
      if (result.ok) {
        setDetail(result.data);
      } else {
        if (result.status !== 0) toast.error(errorDetail(result));
        close();
      }
    });
  }, [openId, close]);

  const today = stats.error ? undefined : stats.data?.today;
  const list = rows.data;

  return (
    <div className="flex flex-col gap-4 px-4 py-4 md:px-6">
      <h1 className="text-lg font-semibold">Ledger</h1>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <StatTile label="Calls today" value={today && String(today.calls)} />
        <StatTile label="Identifiers masked" value={today && String(today.entities_masked)} />
        <StatTile label="Est. cost" value={today && fmtCost(today.cost_usd)} />
        <StatTile label="Blocked" value={today && String(today.blocked)} danger={(today?.blocked ?? 0) > 0} />
      </div>

      {rows.loading ? (
        <div className="flex flex-col gap-2" aria-label="Loading ledger">
          {Array.from({ length: 8 }, (_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
      ) : list && list.length === 0 ? (
        <p className="text-sm text-muted-foreground">Nothing has been sent to an AI or search provider yet.</p>
      ) : list ? (
        <div className="rounded-xl border border-border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Channel</TableHead>
                <TableHead className="hidden md:table-cell">Destination</TableHead>
                <TableHead className="hidden md:table-cell">Model</TableHead>
                <TableHead className="text-right">Masked</TableHead>
                <TableHead className="hidden text-right md:table-cell">Latency</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {list.map((row) => (
                <TableRow
                  key={row.id}
                  role="button"
                  tabIndex={0}
                  aria-label={`Ledger row ${row.id}: ${row.channel} to ${row.destination}, ${row.status}`}
                  onClick={() => open(row.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      open(row.id);
                    }
                  }}
                  className={cn(
                    "h-11 cursor-pointer hover:bg-background focus-visible:bg-background focus-visible:outline-none md:h-auto",
                    row.id === openId && "bg-background",
                  )}
                >
                  <TableCell className="tabular-nums">{fmtLocalTime(row.ts, true)}</TableCell>
                  <TableCell>
                    <Badge variant="neutral" className="font-mono">
                      {row.channel}
                    </Badge>
                  </TableCell>
                  <TableCell className="hidden font-mono text-xs md:table-cell">{row.destination}</TableCell>
                  <TableCell className="hidden md:table-cell">
                    <Model row={row} />
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{row.entities_masked}</TableCell>
                  <TableCell className="hidden text-right tabular-nums md:table-cell">
                    {row.status === "blocked" ? "—" : fmtLatency(row.latency_ms)}
                  </TableCell>
                  <TableCell>
                    <Status status={row.status} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : null}

      <Sheet open={openId !== null} onOpenChange={(o) => !o && close()}>
        <SheetContent side="right" className="gap-0 data-[side=right]:w-full data-[side=right]:sm:max-w-4xl">
          <SheetHeader className="pr-12">
            <SheetTitle className="font-mono text-sm leading-5 font-medium break-words">
              {detail ? diffHeader(detail) : <Skeleton className="h-5 w-3/4" />}
            </SheetTitle>
            <SheetDescription className="text-xs tabular-nums">
              {detail ? diffMeta(detail) : "Loading…"}
            </SheetDescription>
          </SheetHeader>
          <div className="min-h-0 flex-1 overflow-y-auto px-4 pb-4">
            {detail ? <LedgerDiff key={detail.id} detail={detail} /> : <LedgerDiffSkeleton />}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}

export default function LedgerPage() {
  return (
    <Suspense>
      <LedgerScreen />
    </Suspense>
  );
}
