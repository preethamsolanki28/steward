// The one way the dashboard talks to steward-api (docs/02 §6). Same-origin relative URLs only:
// CORS is off and the Host guard accepts 127.0.0.1:8787 / localhost:8787 (docs/02 §8).
// In mock mode (lib/fixtures.ts) the request is answered by fixtureFetch() instead of fetch().

import { toast } from "sonner";

import { fixtureFetch, getFixtureConfig } from "./fixtures";
import type { ApiErrorBody } from "./types";

export type ApiResult<T> =
  | { ok: true; status: number; data: T }
  /** status 0 = network error (already toasted). error is the parsed body, raw text, or null. */
  | { ok: false; status: number; error: ApiErrorBody | string | null };

export type Method = "GET" | "POST" | "PUT";

export const NETWORK_ERROR_TOAST = "Can't reach Steward — is `make up` running?";

function networkError<T>(): ApiResult<T> {
  // A fixed id dedupes the toast, so a poll loop never stacks them.
  toast.error(NETWORK_ERROR_TOAST, { id: "network" });
  return { ok: false, status: 0, error: null };
}

/** Error bodies are usually `{detail}` JSON, but an unknown path returns the static 404 page. */
async function readBody(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

export async function api<T>(method: Method, path: string, body?: unknown): Promise<ApiResult<T>> {
  const config = getFixtureConfig();
  let status: number;
  let parsed: unknown;
  try {
    if (config) {
      const res = await fixtureFetch(method, path, body, config);
      status = res.status;
      // Round-trip through JSON like a real response, so mock state is never shared by reference.
      parsed = res.body === undefined ? null : (JSON.parse(JSON.stringify(res.body)) as unknown);
    } else {
      // Mutating routes need X-Steward-Client (docs/02 §8); a JSON body needs its Content-Type,
      // or FastAPI rejects it with 422.
      const headers: Record<string, string> = { "X-Steward-Client": "web" };
      if (body !== undefined) headers["Content-Type"] = "application/json";
      const res = await fetch(path, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
        cache: "no-store",
      });
      status = res.status;
      parsed = await readBody(res);
    }
  } catch {
    return networkError<T>();
  }
  if (status >= 200 && status < 300) return { ok: true, status, data: parsed as T };
  return { ok: false, status, error: parsed as ApiErrorBody | string | null };
}

/** A human-readable message for a failed result: the API's `detail` when it is a string. */
export function errorDetail(result: { status: number; error: ApiErrorBody | string | null }): string {
  const { error, status } = result;
  if (error && typeof error === "object" && typeof error.detail === "string") return error.detail;
  if (error && typeof error === "object" && Array.isArray(error.detail)) {
    return error.detail.map((d) => d.msg).join("; ") || `HTTP ${status}`;
  }
  return status === 0 ? NETWORK_ERROR_TOAST : `HTTP ${status}`;
}
