// PlaceholderChip (docs/03 §5): a teal chip always means "this is what the provider saw instead
// of the real value"; a red chip marks a span the Shield blocked. Placeholders are shown exactly
// as stored, never renumbered. Neutralized inbound syntax (⟦…⟧) stays plain text.

import { Fragment } from "react";

import { cn } from "@/lib/utils";

const PLACEHOLDER = /^\[\[[A-Z]+_\d+\]\]$/;
const BLOCKED = /^«BLOCKED:[A-Z]+»$/;
const TOKENS = /(\[\[[A-Z]+_\d+\]\]|«BLOCKED:[A-Z]+»)/g;

export function PlaceholderChip({ value, variant = "placeholder" }: { value: string; variant?: "placeholder" | "blocked" }) {
  return (
    <span
      className={cn(
        "rounded px-1 font-mono text-xs font-medium whitespace-nowrap",
        variant === "blocked"
          ? "bg-chip-blocked text-chip-blocked-foreground"
          : "bg-chip-placeholder text-chip-placeholder-foreground",
      )}
    >
      {value}
    </span>
  );
}

/** Plain text with every `[[KIND_n]]` and `«BLOCKED:KIND»` rendered as a chip. */
export function ChipText({ text }: { text: string }) {
  const parts = text.split(TOKENS);
  return (
    <>
      {parts.map((part, i) => {
        if (i % 2 === 1 && PLACEHOLDER.test(part)) return <PlaceholderChip key={i} value={part} />;
        if (i % 2 === 1 && BLOCKED.test(part)) return <PlaceholderChip key={i} value={part} variant="blocked" />;
        return <Fragment key={i}>{part}</Fragment>;
      })}
    </>
  );
}
