"use client";

// MemoryEntries (docs/03 §5): one editor per Hermes memory file. The counter mirrors the server
// exactly: entries are stripped, blanks dropped, joined with "\n§\n" and counted in code points.

import { useState } from "react";
import { Loader2, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { api, errorDetail } from "@/lib/api";
import { MEMORY_ENTRY_DELIMITER, type MemoryFileName, type OkResponse } from "@/lib/types";
import { cn } from "@/lib/utils";

const DELIMITER_LINE_ERROR = "An entry cannot contain a line that is only §";
const EMPTY_COPY = "Steward doesn't know anything about you yet. Tell it in chat or add an entry.";

const normalize = (entries: string[]) => entries.map((e) => e.trim()).filter(Boolean);
const count = (entries: string[]) => [...normalize(entries).join(MEMORY_ENTRY_DELIMITER)].length;

interface MemoryEntriesProps {
  title: string; // "USER.md" / "MEMORY.md"
  file: MemoryFileName;
  limit: number;
  /** The entries as last loaded from the server (remount the component to reset the draft). */
  entries: string[];
  onSaved: () => void;
}

export function MemoryEntries({ title, file, limit, entries, onSaved }: MemoryEntriesProps) {
  const [draft, setDraft] = useState<string[]>(entries);
  const [saving, setSaving] = useState(false);

  const chars = count(draft);
  const over = chars > limit;
  const delimiterLine = draft.some((e) => e.split("\n").some((line) => line.trim() === "§"));
  const changed = JSON.stringify(normalize(draft)) !== JSON.stringify(normalize(entries));

  async function save() {
    setSaving(true);
    const result = await api<OkResponse>("PUT", "/api/memory", { file, entries: draft });
    setSaving(false);
    if (result.ok) {
      toast.success("Memory saved");
      onSaved();
    } else if (result.status !== 0) {
      toast.error(errorDetail(result)); // e.g. "Memory not saved — over the limit (N > L)"; edits are kept
    }
  }

  return (
    <section className="flex flex-col gap-3" aria-label={title}>
      <div className="flex items-baseline justify-between gap-3">
        <h2 className="text-base font-semibold">{title}</h2>
        <span className={cn("text-xs tabular-nums", over ? "font-medium text-destructive" : "text-muted-foreground")}>
          {chars.toLocaleString("en-US")} / {limit.toLocaleString("en-US")}
        </span>
      </div>

      {draft.length === 0 && <p className="text-sm text-muted-foreground">{EMPTY_COPY}</p>}
      {draft.map((entry, i) => (
        <div key={i} className="flex items-start gap-2">
          <Textarea
            value={entry}
            onChange={(e) => setDraft((d) => d.map((x, j) => (j === i ? e.target.value : x)))}
            aria-label={`${title} entry ${i + 1}`}
            className="min-h-16 bg-card"
          />
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                aria-label="Delete entry"
                onClick={() => setDraft((d) => d.filter((_, j) => j !== i))}
              >
                <Trash2 aria-hidden />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Delete entry</TooltipContent>
          </Tooltip>
        </div>
      ))}
      {delimiterLine && <p className="text-xs text-destructive">{DELIMITER_LINE_ERROR}</p>}

      <div className="flex items-center justify-between gap-2">
        <Button variant="outline" onClick={() => setDraft((d) => [...d, ""])}>
          <Plus aria-hidden />
          Add entry
        </Button>
        <Button onClick={() => void save()} disabled={saving || !changed || over || delimiterLine}>
          {saving && <Loader2 className="animate-spin" aria-hidden />}
          Save
        </Button>
      </div>
    </section>
  );
}
