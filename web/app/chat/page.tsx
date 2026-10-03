"use client";

// Chat (docs/03 §6.1): conversation list | thread (BriefCard pinned on top, messages, composer) |
// Activity rail. The rail is inline at >=1280px and a right Sheet below; the list is inline at
// >=1024px and a left Sheet below.

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { Activity, AlertCircle, Clock, Loader2, MessagesSquare } from "lucide-react";
import { toast } from "sonner";

import { ActivityRail } from "@/components/activity-rail";
import { currentHealth, useShellStatus } from "@/components/app-shell";
import { BriefCard } from "@/components/brief-card";
import { ConversationList } from "@/components/conversation-list";
import { ChipText } from "@/components/placeholder-chip";
import { SafeText } from "@/components/safe-text";
import { Alert, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { api, errorDetail } from "@/lib/api";
import {
  CHAT_ERROR_MODEL_UNAVAILABLE,
  CHAT_ERROR_STILL_WORKING,
  type BriefLatestResponse,
  type ChatErrorBody,
  type ChatResponse,
  type ConversationDetail,
  type ConversationSummary,
  type HealthResponse,
  type Message,
} from "@/lib/types";
import { useActivity } from "@/lib/use-activity";
import { usePoll } from "@/lib/use-poll";

const CHIPS = ["Chase the Acme invoice", "What needs my reply today?", "Run my morning brief"];
const MAX_MESSAGE = 20_000; // POST /api/chat accepts 1..20000 chars
const RUNNING_HINT_MS = 5 * 60_000;

/** One banner at a time: Hermes first, then Token Factory. Tavily never pauses chat. */
function bannerCopy(h: HealthResponse | undefined): string | null {
  if (!h) return null;
  if (h.hermes === "down") return "Hermes is down — chat is paused until it's back.";
  if (h.token_factory === "down") return "Token Factory is unreachable — chat is paused until it's back.";
  if (h.token_factory === "no_key") return "No Token Factory key (NEBIUS_API_KEY) — chat is paused.";
  return null;
}

type ErrorCard = { kind: "model" | "timeout"; text: string };

export default function ChatPage() {
  const banner = bannerCopy(currentHealth(useShellStatus().health));
  const paused = banner !== null;

  // --- conversations, brief, activity -----------------------------------------------------------
  const convs = usePoll(
    useCallback(() => api<ConversationSummary[]>("GET", "/api/conversations"), []),
    null,
  );
  const brief = usePoll(
    useCallback(() => api<BriefLatestResponse>("GET", "/api/briefs/latest"), []),
    null,
  );
  const [briefOpen, setBriefOpen] = useState(true);
  const [briefRunning, setBriefRunning] = useState(false);
  const briefRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Expanded by default at >=768px, collapsed below.
    if (!window.matchMedia("(min-width: 768px)").matches) setBriefOpen(false);
  }, []);

  useEffect(() => {
    if (!briefRunning) return;
    const t = setTimeout(() => setBriefRunning(false), RUNNING_HINT_MS);
    return () => clearTimeout(t);
  }, [briefRunning]);

  const activity = useActivity((fresh, initial) => {
    if (initial) return; // the brief loads on mount anyway
    if (fresh.some((a) => a.kind === "skill_run")) {
      // skill_run is written in the same transaction as the brief, so the brief is there now.
      setBriefRunning(false);
      void brief.refresh();
    } else if (fresh.some((a) => a.kind === "tool_call" && a.summary === "mcp__steward__brief_save")) {
      setTimeout(() => void brief.refresh(), 1_000);
    }
  });

  const showBrief = useCallback(() => {
    setBriefOpen(true);
    briefRef.current?.scrollIntoView({ block: "start" });
  }, []);

  // --- thread -----------------------------------------------------------------------------------
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [threadLoading, setThreadLoading] = useState(false);
  const [turn, setTurn] = useState<string | null>(null); // the message in flight
  const [card, setCard] = useState<ErrorCard | null>(null);
  const [draft, setDraft] = useState("");
  const [convSheet, setConvSheet] = useState(false);
  const [railSheet, setRailSheet] = useState(false);
  const view = useRef(0); // bumped on every selection change; late responses for an old view are dropped
  const threadEnd = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    threadEnd.current?.scrollIntoView({ block: "end" });
  }, [messages.length, turn, card, threadLoading]);

  async function selectConversation(id: number) {
    setConvSheet(false);
    if (id === selectedId) return;
    const token = ++view.current;
    setSelectedId(id);
    setMessages([]);
    setCard(null);
    setThreadLoading(true);
    const result = await api<ConversationDetail>("GET", `/api/conversations/${id}`);
    if (token !== view.current) return;
    setThreadLoading(false);
    if (result.ok) {
      setMessages(result.data.messages);
    } else if (result.status === 404) {
      setSelectedId(null);
      void convs.refresh();
      toast.error(errorDetail(result));
    } else if (result.status !== 0) {
      toast.error(errorDetail(result));
    }
  }

  function newChat() {
    setConvSheet(false);
    view.current++;
    setSelectedId(null);
    setMessages([]);
    setCard(null);
    setThreadLoading(false);
    void convs.refresh();
  }

  async function send(text: string, fromComposer: boolean) {
    const message = text.trim();
    if (!message || turn !== null || paused) return;
    const token = view.current;
    const conversationId = selectedId;
    setCard(null);
    setMessages((m) => [...m, { id: -Date.now(), role: "user", content: message, created_at: new Date().toISOString() }]);
    setTurn(message);
    if (fromComposer) setDraft("");

    const result = await api<ChatResponse>(
      "POST",
      "/api/chat",
      conversationId === null ? { message } : { conversation_id: conversationId, message },
    );
    setTurn(null);
    const sameView = token === view.current;
    void activity.refresh();

    if (result.ok) {
      if (sameView) {
        setSelectedId(result.data.conversation_id);
        setMessages((m) => [
          ...m,
          { id: result.data.message_id, role: "assistant", content: result.data.reply, created_at: new Date().toISOString() },
        ]);
      }
      void convs.refresh();
      return;
    }
    if (result.status === 502 || result.status === 504) {
      // The user message was stored; adopt its conversation so Retry stays in it.
      const body = result.error && typeof result.error === "object" ? (result.error as ChatErrorBody) : null;
      if (sameView) {
        if (typeof body?.conversation_id === "number") setSelectedId(body.conversation_id);
        setCard({ kind: result.status === 502 ? "model" : "timeout", text: message });
      }
      void convs.refresh();
    } else if (result.status === 404) {
      // Stale conversation (e.g. after make demo-reset).
      if (sameView) {
        view.current++;
        setSelectedId(null);
        setMessages([]);
      }
      void convs.refresh();
      toast.error(errorDetail(result));
    } else if (result.status !== 0) {
      toast.error(errorDetail(result)); // status 0 (network) is already toasted
    }
  }

  const composerDisabled = turn !== null || paused;
  const emptyThread = !threadLoading && messages.length === 0 && turn === null && card === null;

  const list = (
    <ConversationList
      conversations={convs.data}
      loading={convs.loading}
      selectedId={selectedId}
      onSelect={(id) => void selectConversation(id)}
      onNewChat={newChat}
    />
  );
  const rail = (onNavigate?: () => void) => (
    <ActivityRail items={activity.items} loading={activity.loading} onShowBrief={showBrief} onNavigate={onNavigate} />
  );

  return (
    <div className="flex h-[calc(100dvh-3rem)] min-w-0 md:h-dvh">
      <aside className="hidden w-64 shrink-0 border-r border-border bg-card lg:block">{list}</aside>

      <section className="flex min-w-0 flex-1 flex-col">
        <div className="flex min-h-14 items-center gap-2 border-b border-border bg-card px-4 py-2 md:px-6">
          <h1 className="text-lg font-semibold max-md:sr-only">Chat</h1>
          <div className="ml-auto flex gap-2">
            <Button variant="outline" className="lg:hidden" onClick={() => setConvSheet(true)}>
              <MessagesSquare aria-hidden />
              Conversations
            </Button>
            <Button variant="outline" className="xl:hidden" onClick={() => setRailSheet(true)}>
              <Activity aria-hidden />
              Activity
            </Button>
          </div>
        </div>

        <div className="flex flex-col gap-3 px-4 pt-4 md:px-6">
          {banner && (
            <Alert variant="destructive">
              <AlertCircle aria-hidden />
              <AlertTitle>{banner}</AlertTitle>
            </Alert>
          )}
          <BriefCard
            ref={briefRef}
            data={brief.data}
            loading={brief.loading}
            skillRuns={activity.skillRuns}
            open={briefOpen}
            onOpenChange={setBriefOpen}
            running={briefRunning}
            onRunStarted={() => setBriefRunning(true)}
            disabled={paused}
          />
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4 md:px-6" aria-live="polite">
          {threadLoading ? (
            <div className="flex flex-col gap-4" aria-label="Loading conversation">
              <Skeleton className="ml-auto h-10 w-1/2" />
              <Skeleton className="h-16 w-3/4" />
              <Skeleton className="ml-auto h-10 w-2/5" />
            </div>
          ) : emptyThread ? (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
              <p className="text-sm text-muted-foreground">Ask Steward to chase an invoice or check what needs a reply</p>
              <div className="flex flex-wrap justify-center gap-2">
                {CHIPS.map((chip) => (
                  <Button key={chip} variant="outline" disabled={composerDisabled} onClick={() => void send(chip, false)}>
                    {chip}
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {messages.map((m) =>
                m.role === "user" ? (
                  <div key={m.id} className="flex justify-end">
                    <Card className="max-w-[85%] gap-0 px-3 py-2 break-words whitespace-pre-wrap">
                      <ChipText text={m.content} />
                    </Card>
                  </div>
                ) : (
                  <div key={m.id} className="max-w-[85%]">
                    <SafeText text={m.content} />
                  </div>
                ),
              )}
              {turn !== null && (
                <div className="w-fit rounded-xl border border-border bg-card px-3 py-2 text-sm text-muted-foreground">
                  Steward is working…
                </div>
              )}
              {card?.kind === "model" && (
                <Card className="max-w-[85%] gap-2 border-l-4 border-l-destructive px-4">
                  <p className="flex items-center gap-2 font-medium text-destructive">
                    <AlertCircle className="size-4 shrink-0" aria-hidden />
                    {CHAT_ERROR_MODEL_UNAVAILABLE}
                  </p>
                  <div className="flex flex-wrap items-center gap-3">
                    <Button variant="outline" disabled={composerDisabled} onClick={() => void send(card.text, false)}>
                      Retry
                    </Button>
                    <span className="text-xs text-muted-foreground">Check Approvals before retrying</span>
                  </div>
                </Card>
              )}
              {card?.kind === "timeout" && (
                <Card className="max-w-[85%] gap-2 border-warning px-4">
                  <p className="flex items-center gap-2 font-medium">
                    <Clock className="size-4 shrink-0 text-warning" aria-hidden />
                    {CHAT_ERROR_STILL_WORKING}
                  </p>
                </Card>
              )}
            </div>
          )}
          <div ref={threadEnd} />
        </div>

        <form
          className="flex items-end gap-2 border-t border-border bg-card px-4 py-3 md:px-6"
          onSubmit={(e) => {
            e.preventDefault();
            void send(draft, true);
          }}
        >
          <Textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                e.preventDefault();
                void send(draft, true);
              }
            }}
            placeholder="Message Steward…"
            aria-label="Message Steward"
            maxLength={MAX_MESSAGE}
            rows={1}
            disabled={composerDisabled}
            className="max-h-40 min-h-11 resize-none md:min-h-9"
          />
          <Button type="submit" disabled={composerDisabled || !draft.trim()}>
            {turn !== null && <Loader2 className="animate-spin" aria-hidden />}
            Send
          </Button>
        </form>
      </section>

      <aside className="hidden w-80 shrink-0 border-l border-border bg-card xl:block">{rail()}</aside>

      <Sheet open={convSheet} onOpenChange={setConvSheet}>
        <SheetContent side="left" className="w-72 gap-0 p-0">
          <SheetTitle className="px-4 pt-4 text-base font-semibold">Conversations</SheetTitle>
          {list}
        </SheetContent>
      </Sheet>
      <Sheet open={railSheet} onOpenChange={setRailSheet}>
        <SheetContent side="right" className="w-80 gap-0 p-0">
          <SheetTitle className="sr-only">Activity</SheetTitle>
          {rail(() => setRailSheet(false))}
        </SheetContent>
      </Sheet>
    </div>
  );
}
