// The in-house renderer for briefs and assistant replies (docs/03 §5). It understands `#`/`##`
// headings, `-` bullets, `**bold**` and bare http(s) links, and builds React nodes only: the brief
// contains untrusted web snippets, so there is no dangerouslySetInnerHTML and no Markdown library.
// Anything else (including literal `<billing@…>`) is shown as text.

import type { ReactNode } from "react";

import { ChipText } from "@/components/placeholder-chip";

// A URL never ends in punctuation that belongs to the sentence: "(https://x.example)." keeps ")."
const URL_RE = /(https?:\/\/[^\s<>()"']*[^\s<>()"'.,;:!?])/g;
const BOLD_RE = /(\*\*[^*]+\*\*)/g;

function linkify(text: string, key: string): ReactNode[] {
  return text.split(URL_RE).map((part, i) =>
    i % 2 === 1 ? (
      <a
        key={`${key}-${i}`}
        href={part}
        target="_blank"
        rel="noopener noreferrer"
        className="break-all text-primary underline-offset-4 hover:text-primary-hover hover:underline"
      >
        {part}
      </a>
    ) : (
      <ChipText key={`${key}-${i}`} text={part} />
    ),
  );
}

function inline(text: string, key: string): ReactNode[] {
  return text.split(BOLD_RE).map((part, i) =>
    i % 2 === 1 ? (
      <strong key={`${key}-b${i}`} className="font-semibold">
        {linkify(part.slice(2, -2), `${key}-b${i}`)}
      </strong>
    ) : (
      linkify(part, `${key}-t${i}`)
    ),
  );
}

type Block =
  | { type: "h1" | "h2"; text: string }
  | { type: "ul"; items: string[] }
  | { type: "p"; lines: string[] };

function parse(source: string): Block[] {
  const blocks: Block[] = [];
  for (const raw of source.replace(/\r\n?/g, "\n").split("\n")) {
    const line = raw.trimEnd();
    const last = blocks[blocks.length - 1];
    if (!line.trim()) {
      blocks.push({ type: "p", lines: [] }); // paragraph break
    } else if (/^#\s+/.test(line)) {
      blocks.push({ type: "h1", text: line.replace(/^#\s+/, "") });
    } else if (/^##+\s+/.test(line)) {
      blocks.push({ type: "h2", text: line.replace(/^##+\s+/, "") });
    } else if (/^\s*[-*]\s+/.test(line)) {
      const item = line.replace(/^\s*[-*]\s+/, "");
      if (last?.type === "ul") last.items.push(item);
      else blocks.push({ type: "ul", items: [item] });
    } else if (last?.type === "p") {
      last.lines.push(line);
    } else {
      blocks.push({ type: "p", lines: [line] });
    }
  }
  return blocks.filter((b) => b.type !== "p" || b.lines.length > 0);
}

export function SafeText({ text, className }: { text: string; className?: string }) {
  return (
    <div className={className ?? "flex flex-col gap-2 text-sm break-words"}>
      {parse(text).map((block, i) => {
        const key = `k${i}`;
        switch (block.type) {
          case "h1":
            return (
              <p key={key} className="text-base font-semibold">
                {inline(block.text, key)}
              </p>
            );
          case "h2":
            return (
              <p key={key} className="pt-1 text-sm font-semibold">
                {inline(block.text, key)}
              </p>
            );
          case "ul":
            return (
              <ul key={key} className="flex list-disc flex-col gap-1 pl-5">
                {block.items.map((item, j) => (
                  <li key={j}>{inline(item, `${key}-${j}`)}</li>
                ))}
              </ul>
            );
          case "p":
            return (
              <p key={key}>
                {block.lines.map((line, j) => (
                  <span key={j}>
                    {j > 0 && <br />}
                    {inline(line, `${key}-${j}`)}
                  </span>
                ))}
              </p>
            );
        }
      })}
    </div>
  );
}
