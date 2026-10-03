"use client";

// BriefCard (docs/03 §5): today's morning brief, pinned at the top of the Chat thread.

import { forwardRef, useState } from "react";
import { ChevronDown, ChevronUp, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { SafeText } from "@/components/safe-text";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { api, errorDetail } from "@/lib/api";
import { fmtIST, fmtISTDate, istParts } from "@/lib/format";
import type { Brief, BriefJob, BriefLatestResponse, OkResponse } from "@/lib/types";

const SCHEDULED_SUMMARY = "morning-brief · scheduled run";

/**
 * "Ran by schedule at 08:00 IST" only when the brief's skill_run row says it was the scheduled
 * run AND the brief was saved between 08:00 and 08:15 IST; otherwise the actual time (the newer of
 * job.last_run_at and brief.created_at), with the date when it isn't today, plus a non-ok status.
 */
export function runLabel(brief: Brief, job: BriefJob | null, skillRunSummary: string | undefined): string {
  const created = istParts(brief.created_at);
  const scheduled =
    skillRunSummary === SCHEDULED_SUMMARY && created !== null && created.minutes >= 480 && created.minutes <= 495;
  let label: string;
  if (scheduled) {
    label = "Ran by schedule at 08:00 IST";
  } else {
    let t = brief.created_at;
    if (job?.last_run_at && Date.parse(job.last_run_at) > Date.parse(t)) t = job.last_run_at;
    const day = istParts(t)?.day;
    const today = istParts(new Date().toISOString())?.day;
    label = `Ran at ${fmtIST(t)} IST${day && day !== today ? `, ${fmtISTDate(t)}` : ""}`;
  }
  if (job?.last_status && job.last_status !== "ok") label += ` · ${job.last_status}`;
  return label;
}

/** A leading "# Today's brief" repeats the card title, so it is not rendered twice. */
function body(contentMd: string): string {
  return contentMd.replace(/^\s*#\s+Today['’]s brief\s*\n/i, "");
}

interface BriefCardProps {
  data: BriefLatestResponse | undefined;
  loading: boolean;
  skillRuns: ReadonlyMap<number, string>;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** A Run now was accepted and its skill_run activity has not arrived yet. */
  running: boolean;
  onRunStarted: () => void;
  /** The health banner is showing. */
  disabled: boolean;
}

export const BriefCard = forwardRef<HTMLDivElement, BriefCardProps>(function BriefCard(
  { data, loading, skillRuns, open, onOpenChange, running, onRunStarted, disabled },
  ref,
) {
  const [posting, setPosting] = useState(false);

  async function runNow() {
    setPosting(true);
    const result = await api<OkResponse>("POST", "/api/skills/morning-brief/run");
    setPosting(false);
    if (result.ok) onRunStarted();
    else if (result.status !== 0) toast.error(errorDetail(result)); // status 0 is already toasted
  }

  if (loading) {
    return (
      <Card ref={ref} className="gap-3 px-4" aria-busy="true" aria-label="Loading today's brief">
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-11/12" />
        <Skeleton className="h-4 w-3/4" />
      </Card>
    );
  }

  const brief = data?.brief ?? null;
  const job = data?.job ?? null;
  const runButton = (
    <Button variant="outline" onClick={runNow} disabled={posting || disabled}>
      {posting && <Loader2 className="animate-spin" aria-hidden />}
      Run now
    </Button>
  );

  return (
    <Card ref={ref} className="gap-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2 px-4">
        <div className="min-w-0 flex-1">
          <h2 className="text-base font-semibold">Today&apos;s brief</h2>
          {brief && (
            <p className="text-xs text-muted-foreground">
              {runLabel(brief, job, skillRuns.get(brief.id))}
              {running && " · Running…"}
            </p>
          )}
          {!brief && running && <p className="text-xs text-muted-foreground">Running…</p>}
        </div>
        {runButton}
        {brief && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onOpenChange(!open)}
                aria-expanded={open}
                aria-label={open ? "Collapse brief" : "Expand brief"}
              >
                {open ? <ChevronUp aria-hidden /> : <ChevronDown aria-hidden />}
              </Button>
            </TooltipTrigger>
            <TooltipContent>{open ? "Collapse" : "Expand"}</TooltipContent>
          </Tooltip>
        )}
      </div>
      {!brief && (
        <p className="px-4 text-sm text-muted-foreground">Your first brief arrives at 08:00 IST — or run it now.</p>
      )}
      {brief && open && (
        <div className="max-h-[40dvh] overflow-y-auto px-4">
          <SafeText text={body(brief.content_md)} />
        </div>
      )}
    </Card>
  );
});
