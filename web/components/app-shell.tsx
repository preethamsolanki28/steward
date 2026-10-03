"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { createContext, useCallback, useContext, useState } from "react";
import { Brain, Menu, MessageSquare, ScrollText, ShieldCheck, type LucideIcon } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { api } from "@/lib/api";
import type { Action, HealthResponse, UpDownNoKey } from "@/lib/types";
import { usePoll, type PollState } from "@/lib/use-poll";
import { cn } from "@/lib/utils";

// --- shared status: one health poll and one pending poll for the whole app (docs/03 §6.0) ------

const HEALTH_POLL_MS = 10_000;
const PENDING_POLL_MS = 3_000;

interface ShellStatus {
  health: PollState<HealthResponse>;
  pending: PollState<Action[]>;
}

const ShellStatusContext = createContext<ShellStatus | null>(null);

/** Health and pending actions, shared by the shell, the Chat banner, Approvals and the System tab. */
export function useShellStatus(): ShellStatus {
  const status = useContext(ShellStatusContext);
  if (!status) throw new Error("useShellStatus must be used inside AppShell");
  return status;
}

/** The latest health, or undefined before the first response and after a failed poll
 *  (grey dots rather than stale green). */
export function currentHealth(health: PollState<HealthResponse>): HealthResponse | undefined {
  return health.error ? undefined : health.data;
}

/** The pending count, or undefined until the first response and after a failed poll. */
function pendingCount(pending: PollState<Action[]>): number | undefined {
  return pending.error ? undefined : pending.data?.length;
}

// --- nav ----------------------------------------------------------------------------------------

type NavItem = { href: string; label: string; icon: LucideIcon };

const NAV: NavItem[] = [
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/approvals", label: "Approvals", icon: ShieldCheck },
  { href: "/ledger", label: "Ledger", icon: ScrollText },
  { href: "/memory", label: "Memory & Skills", icon: Brain },
];

function isActive(pathname: string, href: string) {
  return pathname === href || pathname.startsWith(`${href}/`);
}

function NavLinks({ pathname, onNavigate }: { pathname: string; onNavigate?: () => void }) {
  const count = pendingCount(useShellStatus().pending);
  return (
    <nav aria-label="Main" className="flex flex-col gap-1">
      {NAV.map(({ href, label, icon: Icon }) => {
        const active = isActive(pathname, href);
        const showCount = href === "/approvals" && count !== undefined && count > 0;
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex min-h-11 items-center gap-3 border-l-2 px-3 text-sm md:min-h-9",
              active
                ? "border-primary font-medium text-primary"
                : "border-transparent text-foreground hover:bg-background",
            )}
          >
            <Icon className="size-4" aria-hidden />
            <span className="flex-1">{label}</span>
            {showCount && (
              <Badge variant="count" aria-label={`${count} pending`}>
                {count}
              </Badge>
            )}
          </Link>
        );
      })}
    </nav>
  );
}

// --- health pill (docs/03 §6.0) -------------------------------------------------------------------

const DOT: Record<UpDownNoKey, string> = { up: "bg-success", down: "bg-destructive", no_key: "bg-warning" };
const WORD: Record<UpDownNoKey, string> = { up: "up", down: "down", no_key: "no key" };

function HealthPill() {
  const h = currentHealth(useShellStatus().health);
  const connectors: Array<[string, UpDownNoKey | undefined]> = [
    ["Hermes", h?.hermes],
    ["Token Factory", h?.token_factory],
    ["Tavily", h?.tavily],
  ];
  const words = h
    ? [
        ...connectors.map(([name, s]) => `${name}: ${WORD[s ?? "down"]}`),
        `mail: ${h.mail_mode}`,
        `model: ${h.model_primary}`,
      ].join(" · ")
    : "Checking connectors…";

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Link
          href="/memory?tab=system"
          aria-label={`Connector status. ${words}`}
          className="flex flex-col gap-1.5 rounded-md text-xs text-muted-foreground outline-none hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50"
        >
          {connectors.map(([name, s]) => (
            <span key={name} className="flex items-center gap-2">
              <span className={cn("size-2 shrink-0 rounded-full", s ? DOT[s] : "bg-border")} aria-hidden />
              <span>{name}</span>
            </span>
          ))}
          <span className="pl-4">mail: {h?.mail_mode ?? "—"}</span>
        </Link>
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-72">
        {words}
      </TooltipContent>
    </Tooltip>
  );
}

// --- shell --------------------------------------------------------------------------------------

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const title = NAV.find(({ href }) => isActive(pathname, href))?.label ?? "Steward";

  const health = usePoll(
    useCallback(() => api<HealthResponse>("GET", "/api/health"), []),
    HEALTH_POLL_MS,
  );
  const pending = usePoll(
    useCallback(() => api<Action[]>("GET", "/api/actions?status=pending"), []),
    PENDING_POLL_MS,
  );
  const count = pendingCount(pending);

  return (
    <ShellStatusContext.Provider value={{ health, pending }}>
      <div className="flex min-h-dvh bg-background">
        {/* >=768px: left sidebar, sticky so the nav and health pill stay put while a screen scrolls */}
        <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-card md:sticky md:top-0 md:flex md:h-dvh">
          <div className="px-4 py-4 text-base font-semibold">Steward</div>
          <div className="flex-1 overflow-y-auto px-2">
            <NavLinks pathname={pathname} />
          </div>
          <Separator />
          <div className="p-4">
            <HealthPill />
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          {/* <768px: top bar with the same nav in a left Sheet */}
          <header className="flex h-12 items-center gap-2 border-b border-border bg-card px-2 md:hidden">
            <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
              <SheetTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="relative size-11"
                  aria-label={count ? `Open menu (${count} pending)` : "Open menu"}
                >
                  <Menu className="size-5" aria-hidden />
                  {count !== undefined && count > 0 && (
                    <Badge
                      variant="count"
                      className="absolute top-1 right-0.5 h-4 min-w-4 px-1 text-[10px]"
                      aria-hidden
                    >
                      {count}
                    </Badge>
                  )}
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-72 gap-0 p-0">
                <SheetTitle className="px-4 py-4 text-base font-semibold">Steward</SheetTitle>
                <div className="flex-1 px-2">
                  <NavLinks pathname={pathname} onNavigate={() => setMenuOpen(false)} />
                </div>
                <Separator />
                <div className="p-4">
                  <HealthPill />
                </div>
              </SheetContent>
            </Sheet>
            <span className="text-base font-semibold">Steward</span>
            <span className="ml-auto pr-2 text-sm text-muted-foreground">{title}</span>
          </header>

          <main className="min-w-0 flex-1">{children}</main>
        </div>
      </div>
    </ShellStatusContext.Provider>
  );
}
