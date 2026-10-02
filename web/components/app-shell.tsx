"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Brain, Menu, MessageSquare, ScrollText, ShieldCheck, type LucideIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

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
  return (
    <nav aria-label="Main" className="flex flex-col gap-1">
      {NAV.map(({ href, label, icon: Icon }) => {
        const active = isActive(pathname, href);
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
            {/* Approvals pending-count Badge: hidden until /api/actions?status=pending responds (T4.1). */}
          </Link>
        );
      })}
    </nav>
  );
}

// Health pill, first-load state (docs/03 §8): grey dots until /api/health responds (wired in T4.1).
function HealthPill() {
  const connectors = ["Hermes", "Token Factory", "Tavily"];
  return (
    <div className="flex flex-col gap-1.5 text-xs text-muted-foreground" aria-label="Connector status">
      {connectors.map((name) => (
        <div key={name} className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-border" aria-hidden />
          <span>{name}</span>
        </div>
      ))}
      <div className="pl-4">mail: —</div>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const title = NAV.find(({ href }) => isActive(pathname, href))?.label ?? "Steward";

  return (
    <div className="flex min-h-dvh bg-background">
      {/* >=768px: left sidebar */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-card md:flex">
        <div className="px-4 py-4 text-base font-semibold">Steward</div>
        <div className="flex-1 px-2">
          <NavLinks pathname={pathname} />
        </div>
        <Separator />
        <div className="p-4">
          <HealthPill />
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        {/* <768px: top bar with the same nav in a left Sheet */}
        <header className="flex items-center gap-2 border-b border-border bg-card px-2 md:hidden">
          <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="size-11" aria-label="Open menu">
                <Menu className="size-5" aria-hidden />
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
  );
}
