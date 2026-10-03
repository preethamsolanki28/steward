"use client";

// Memory & Skills (docs/03 §6.4): Memory (the per-entry editor, the DG-2 demo path), Skills, and a
// read-only System tab. ?tab=memory|skills|system selects a tab (the health pill links to system).

import { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { currentHealth, useShellStatus } from "@/components/app-shell";
import { MemoryEntries } from "@/components/memory-entries";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api, errorDetail } from "@/lib/api";
import { fmtIST } from "@/lib/format";
import {
  MEMORY_LIMIT,
  USER_LIMIT,
  type BriefLatestResponse,
  type Contact,
  type MemoryResponse,
  type OkResponse,
  type SettingsResponse,
  type Skill,
  type UpDownNoKey,
} from "@/lib/types";
import { usePoll } from "@/lib/use-poll";
import { cn } from "@/lib/utils";

const TABS = ["memory", "skills", "system"] as const;
type Tab = (typeof TABS)[number];
const SYSTEM_POLL_MS = 10_000;
const RUN_POLL_MS = 10_000;
const RUNNING_HINT_MS = 5 * 60_000;

// --- Memory -----------------------------------------------------------------------------------

function MemoryTab() {
  const mem = usePoll(
    useCallback(() => api<MemoryResponse>("GET", "/api/memory"), []),
    null, // no polling: it would clobber edits
  );
  if (mem.loading || !mem.data) {
    return (
      <div className="flex flex-col gap-6" aria-label="Loading memory">
        {[0, 1].map((i) => (
          <div key={i} className="flex flex-col gap-3">
            <Skeleton className="h-5 w-24" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        ))}
      </div>
    );
  }
  const { user, memory } = mem.data;
  const refresh = () => void mem.refresh();
  return (
    <div className="flex flex-col gap-8">
      {/* Remounting on new server entries resets the draft after a save. */}
      <MemoryEntries
        key={`user:${JSON.stringify(user.entries)}`}
        title="USER.md"
        file="user"
        limit={USER_LIMIT}
        entries={user.entries}
        onSaved={refresh}
      />
      <MemoryEntries
        key={`memory:${JSON.stringify(memory.entries)}`}
        title="MEMORY.md"
        file="memory"
        limit={MEMORY_LIMIT}
        entries={memory.entries}
        onSaved={refresh}
      />
      <p className="text-sm text-muted-foreground">Changes apply from your next new chat</p>
    </div>
  );
}

// --- Skills -----------------------------------------------------------------------------------

function SkillsTab() {
  const hermesDown = currentHealth(useShellStatus().health)?.hermes === "down";
  const skills = usePoll(
    useCallback(() => api<Skill[]>("GET", "/api/skills"), []),
    null,
  );
  const [running, setRunning] = useState<string | null | false>(false); // last_run_at when started
  const brief = usePoll(
    useCallback(() => api<BriefLatestResponse>("GET", "/api/briefs/latest"), []),
    running === false ? null : RUN_POLL_MS,
  );
  const [posting, setPosting] = useState(false);
  const job = brief.data?.job ?? null;

  useEffect(() => {
    // The run finished when the job's last_run_at moves on.
    if (running !== false && job && job.last_run_at !== running) setRunning(false);
  }, [running, job]);
  useEffect(() => {
    if (running === false) return;
    const t = setTimeout(() => setRunning(false), RUNNING_HINT_MS);
    return () => clearTimeout(t);
  }, [running]);

  async function runNow() {
    setPosting(true);
    const result = await api<OkResponse>("POST", "/api/skills/morning-brief/run");
    setPosting(false);
    if (result.ok) setRunning(job?.last_run_at ?? null);
    else if (result.status !== 0) toast.error(errorDetail(result));
  }

  if (skills.loading || !skills.data) {
    return (
      <div className="grid gap-4 md:grid-cols-2" aria-label="Loading skills">
        {[0, 1].map((i) => (
          <Card key={i} className="gap-3 px-4">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid items-start gap-4 md:grid-cols-2">
      {skills.data.map((skill) => (
        <Card key={skill.name} className="gap-3 px-4">
          <h2 className="font-mono text-base font-semibold">{skill.name}</h2>
          <p className="text-sm">{skill.description}</p>
          {skill.runnable ? (
            <>
              <div className="flex flex-col gap-0.5 text-sm">
                <span>Daily 08:00 IST</span>
                <span className="text-muted-foreground tabular-nums">
                  Last run:{" "}
                  {job?.last_run_at
                    ? `${fmtIST(job.last_run_at)} IST${job.last_status ? ` · ${job.last_status}` : ""}`
                    : "—"}
                  {running !== false && " · Running…"}
                </span>
              </div>
              <div className="flex justify-end">
                <Button variant="outline" onClick={() => void runNow()} disabled={posting || hermesDown}>
                  {posting && <Loader2 className="animate-spin" aria-hidden />}
                  Run now
                </Button>
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Start it from Chat</p>
          )}
        </Card>
      ))}
    </div>
  );
}

// --- System (read-only) -------------------------------------------------------------------------

const DOT: Record<UpDownNoKey, string> = { up: "bg-success", down: "bg-destructive", no_key: "bg-warning" };
const WORD: Record<UpDownNoKey, string> = { up: "up", down: "down", no_key: "no key" };

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <>
      <dt className="text-sm text-muted-foreground md:pt-0.5">{label}</dt>
      <dd className="min-w-0 text-sm">{children}</dd>
    </>
  );
}

function SystemTab() {
  const h = currentHealth(useShellStatus().health);
  const settings = usePoll(
    useCallback(() => api<SettingsResponse>("GET", "/api/settings"), []),
    SYSTEM_POLL_MS,
  );
  const contacts = usePoll(
    useCallback(() => api<Contact[]>("GET", "/api/contacts"), []),
    SYSTEM_POLL_MS,
  );
  const s = settings.data;
  const retrying = <span className="text-muted-foreground">Couldn&apos;t load — retrying</span>;
  const pending = <Skeleton className="h-4 w-48" />;

  const connectors: Array<[string, UpDownNoKey | undefined]> = [
    ["Hermes", h?.hermes],
    ["Token Factory", h?.token_factory],
    ["Tavily", h?.tavily],
  ];
  const trusted = contacts.data?.filter((c) => c.trusted === 1);

  return (
    <dl className="grid grid-cols-1 gap-x-6 gap-y-2 md:grid-cols-[10rem_1fr] md:gap-y-5">
      <Row label="Connectors">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
          {connectors.map(([name, st]) => (
            <span key={name} className="inline-flex items-center gap-2">
              <span className={cn("size-2 rounded-full", st ? DOT[st] : "bg-border")} aria-hidden />
              {name}
              <span className="sr-only">: {st ? WORD[st] : "unknown"}</span>
            </span>
          ))}
          <span className="text-muted-foreground">mail: {h?.mail_mode ?? "—"}</span>
        </div>
      </Row>
      <Row label="Model chain">
        {s ? (
          <span className="font-mono text-xs font-medium break-words">
            {s.model_primary} → {s.model_fallback}
          </span>
        ) : settings.error ? retrying : pending}
      </Row>
      <Row label="Reasoning effort">{s ? s.reasoning_effort : settings.error ? retrying : pending}</Row>
      <Row label="Privacy Shield">
        {s ? (
          <span className="inline-flex items-center gap-2">
            <Switch checked={s.shield === "on"} disabled aria-readonly aria-label="Privacy Shield" />
            {s.shield === "on" ? "On" : s.shield}
          </span>
        ) : settings.error ? retrying : pending}
      </Row>
      <Row label="ZDR">{s ? s.zdr_note : settings.error ? retrying : pending}</Row>
      <Row label="Trusted contacts">
        <div className="flex flex-col gap-3">
          <p>Only these contacts are trusted. Steward cannot change this list.</p>
          {trusted ? (
            <div className="rounded-xl border border-border bg-card">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Org</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {trusted.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>{c.name ?? "—"}</TableCell>
                      <TableCell className="font-mono text-xs break-words">{c.email}</TableCell>
                      <TableCell>{c.org ?? "—"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : contacts.error ? (
            retrying
          ) : (
            <div className="flex flex-col gap-2">
              {Array.from({ length: 5 }, (_, i) => (
                <Skeleton key={i} className="h-6 w-full" />
              ))}
            </div>
          )}
        </div>
      </Row>
    </dl>
  );
}

// --- page -------------------------------------------------------------------------------------

function MemoryScreen() {
  const router = useRouter();
  const params = useSearchParams();
  const requested = params.get("tab");
  const tab: Tab = (TABS as readonly string[]).includes(requested ?? "") ? (requested as Tab) : "memory";

  return (
    <div className="px-4 py-4 md:px-6">
      <div className="mx-auto flex max-w-4xl flex-col gap-4">
        <h1 className="text-lg font-semibold">Memory &amp; Skills</h1>
        <Tabs value={tab} onValueChange={(v) => router.replace(`/memory?tab=${v}`, { scroll: false })}>
          <TabsList>
            <TabsTrigger value="memory">Memory</TabsTrigger>
            <TabsTrigger value="skills">Skills</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
          </TabsList>
          <TabsContent value="memory" className="mt-4">
            <MemoryTab />
          </TabsContent>
          <TabsContent value="skills" className="mt-4">
            <SkillsTab />
          </TabsContent>
          <TabsContent value="system" className="mt-4">
            <SystemTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default function MemoryPage() {
  return (
    <Suspense>
      <MemoryScreen />
    </Suspense>
  );
}
