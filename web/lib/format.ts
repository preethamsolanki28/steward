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

const IST_PARTS = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Asia/Kolkata",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

/** The IST calendar day ("2026-10-03") and minutes since IST midnight, or null if unparseable. */
export function istParts(iso: string): { day: string; minutes: number } | null {
  const ms = Date.parse(iso);
  if (Number.isNaN(ms)) return null;
  const p = Object.fromEntries(IST_PARTS.formatToParts(ms).map(({ type, value }) => [type, value]));
  return { day: `${p.year}-${p.month}-${p.day}`, minutes: Number(p.hour) * 60 + Number(p.minute) };
}

/** "3 Oct" in Asia/Kolkata. */
export function fmtISTDate(iso: string): string {
  const ms = Date.parse(iso);
  if (Number.isNaN(ms)) return "—";
  return new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", day: "numeric", month: "short" }).format(ms);
}

/** Local "HH:mm" today, otherwise the local date ("3 Oct"). */
export function fmtLocalShort(iso: string): string {
  const ms = Date.parse(iso);
  if (Number.isNaN(ms)) return "—";
  const d = new Date(ms);
  if (d.toDateString() === new Date().toDateString()) return fmtLocalTime(iso);
  return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short" }).format(ms);
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
