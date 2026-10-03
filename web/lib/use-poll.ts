"use client";

// Client-side polling (docs/02 §3): setTimeout chaining so requests never overlap, the same
// interval after an error, paused while the tab is hidden, and `loading` only until the first
// result so later refreshes update in place instead of flashing skeletons (docs/03 §8).

import { useCallback, useEffect, useRef, useState } from "react";

import type { ApiResult } from "./api";

export interface PollState<T> {
  data: T | undefined;
  /** The last failed result; cleared by the next success. */
  error: Extract<ApiResult<T>, { ok: false }> | undefined;
  /** True only before the first result (success or failure). */
  loading: boolean;
  /** Fetch now (after a mutation, or on an activity trigger). Resolves when the result is applied. */
  refresh: () => Promise<void>;
}

export interface PollOptions {
  /** false = don't fetch at all (default true). */
  enabled?: boolean;
  /** Skip timer ticks while document.hidden and fetch on return (default true). */
  pauseWhenHidden?: boolean;
}

export function usePoll<T>(
  fetcher: () => Promise<ApiResult<T>>,
  intervalMs: number | null,
  { enabled = true, pauseWhenHidden = true }: PollOptions = {},
): PollState<T> {
  const [data, setData] = useState<T | undefined>(undefined);
  const [error, setError] = useState<PollState<T>["error"]>(undefined);
  const [loading, setLoading] = useState(true);

  // The latest fetcher, so callers can pass inline closures without restarting the loop.
  const fetcherRef = useRef(fetcher);
  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const inFlight = useRef<Promise<void> | null>(null);
  const generation = useRef(0); // bumped on unmount/restart; stale responses are dropped
  const mounted = useRef(false);

  const run = useCallback(async (): Promise<void> => {
    if (inFlight.current) return inFlight.current; // never overlap
    const gen = generation.current;
    const p = (async () => {
      const result = await fetcherRef.current();
      if (gen !== generation.current || !mounted.current) return;
      if (result.ok) {
        setData(result.data);
        setError(undefined);
      } else {
        setError(result);
      }
      setLoading(false);
    })();
    inFlight.current = p;
    try {
      await p;
    } finally {
      if (inFlight.current === p) inFlight.current = null;
    }
  }, []);

  useEffect(() => {
    mounted.current = true;
    if (!enabled) return;
    const gen = ++generation.current;
    inFlight.current = null;

    const schedule = () => {
      if (intervalMs === null || gen !== generation.current) return;
      timer.current = setTimeout(tick, intervalMs);
    };
    const tick = async () => {
      if (pauseWhenHidden && document.hidden) return; // resumed by visibilitychange
      await run();
      schedule();
    };
    const onVisible = () => {
      if (document.hidden || gen !== generation.current) return;
      clearTimeout(timer.current);
      void tick();
    };

    void tick();
    if (pauseWhenHidden) document.addEventListener("visibilitychange", onVisible);
    return () => {
      generation.current++;
      clearTimeout(timer.current);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [enabled, intervalMs, pauseWhenHidden, run]);

  useEffect(
    () => () => {
      mounted.current = false;
    },
    [],
  );

  const refresh = useCallback(() => run(), [run]);
  return { data, error, loading, refresh };
}
