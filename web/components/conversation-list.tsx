"use client";

import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { fmtLocalShort } from "@/lib/format";
import type { ConversationSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ConversationListProps {
  conversations: ConversationSummary[] | undefined;
  loading: boolean;
  selectedId: number | null;
  onSelect: (id: number) => void;
  onNewChat: () => void;
}

export function ConversationList({ conversations, loading, selectedId, onSelect, onNewChat }: ConversationListProps) {
  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="p-4">
        <Button variant="outline" className="w-full justify-start" onClick={onNewChat}>
          <Plus aria-hidden />
          New chat
        </Button>
      </div>
      <nav aria-label="Conversations" className="min-h-0 flex-1 overflow-y-auto px-2 pb-4">
        {loading ? (
          <div className="flex flex-col gap-3 px-2" aria-label="Loading conversations">
            {Array.from({ length: 5 }, (_, i) => (
              <Skeleton key={i} className="h-9 w-full" />
            ))}
          </div>
        ) : !conversations || conversations.length === 0 ? (
          <p className="px-2 text-sm text-muted-foreground">No conversations yet.</p>
        ) : (
          <ul className="flex flex-col gap-0.5">
            {conversations.map((c) => {
              const selected = c.id === selectedId;
              return (
                <li key={c.id}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        type="button"
                        onClick={() => onSelect(c.id)}
                        aria-current={selected ? "true" : undefined}
                        className={cn(
                          "flex min-h-11 w-full flex-col justify-center rounded-md px-2 py-1.5 text-left hover:bg-background focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none md:min-h-0",
                          selected && "bg-background font-medium",
                        )}
                      >
                        <span className="w-full truncate text-sm">{c.title}</span>
                        <span className="text-xs text-muted-foreground tabular-nums">{fmtLocalShort(c.updated_at)}</span>
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="right" className="max-w-72">
                      {c.title}
                    </TooltipContent>
                  </Tooltip>
                </li>
              );
            })}
          </ul>
        )}
      </nav>
    </div>
  );
}
