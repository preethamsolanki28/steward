// Display helpers shared by every screen (docs/03 §2, §5).

const MODEL_NAMES: Record<string, { long: string; short: string }> = {
  "nvidia/Nemotron-3_5-Lightning": { long: "Nemotron 3.5 Lightning", short: "Lightning" },
  "nvidia/nemotron-3-super-120b-a12b": { long: "Nemotron 3 Super", short: "Super" },
  "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B": { long: "Nemotron 3 Nano 30B", short: "Nano 30B" },
};

/** "Nemotron 3 Super" for a known ID, the raw ID otherwise, "—" for null. */
export function modelLong(id: string | null | undefined): string {
  if (!id) return "—";
  return MODEL_NAMES[id]?.long ?? id;
}

/** "Super" for a known ID, the raw ID otherwise, "—" for null. */
export function modelShort(id: string | null | undefined): string {
  if (!id) return "—";
  return MODEL_NAMES[id]?.short ?? id;
}

const IST = new Intl.DateTimeFormat("en-GB", {
  timeZone: "Asia/Kolkata",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

/** "08:00" in Asia/Kolkata. Works for UTC steward rows and +05:30 Hermes job times alike. */
export function fmtIST(iso: string): string {
  const ms = Date.parse(iso);
  return Number.isNaN(ms) ? "—" : IST.format(ms);
}

/** Local 24-hour "HH:mm" (or "HH:mm:ss"). */
export function fmtLocalTime(iso: string, seconds = false): string {
  const ms = Date.parse(iso);
  if (Number.isNaN(ms)) return "—";
  return new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: seconds ? "2-digit" : undefined,
    hour12: false,
  }).format(ms);
}

/** "9.4 s" */
export function fmtLatency(ms: number): string {
  return `${(ms / 1000).toFixed(1)} s`;
}

/** "$0.0021" */
export function fmtCost(usd: number): string {
  return `$${usd.toFixed(4)}`;
}

/** "mcp__steward__mail_send → queued" → "mail_send → queued" */
export function stripTool(s: string): string {
  return s.replace(/^mcp__steward__/, "");
}
