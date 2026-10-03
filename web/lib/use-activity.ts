"use client";

// The Activity feed (docs/03 §6.1): the first GET /api/activity has no cursor, then after_id is the
// last id seen. Polled every 1.5 s while the page is visible, idle or not, so a scheduled brief
// shows up with no input. The API has no limit, so only the newest MAX_ITEMS rows are kept.

import { useCallback, useEffect, useRef, useState } from "react";

import { api } from "./api";
import type { ActivityItem } from "./types";
import { usePoll } from "./use-poll";

export const ACTIVITY_POLL_MS = 1_500;
const MAX_ITEMS = 200;

/** `onNew(items, initial)`: called with each batch of new rows; `initial` is the first load. */
export function useActivity(onNew?: (items: ActivityItem[], initial: boolean) => void) {
  const cursor = useRef(0);
  const first = useRef(true);
  const [items, setItems] = useState<ActivityItem[]>([]);
  // skill_run summary by brief id, kept apart from the capped list (the BriefCard label needs it).
  const [skillRuns, setSkillRuns] = useState<ReadonlyMap<number, string>>(new Map());

  const onNewRef = useRef(onNew);
  useEffect(() => {
    onNewRef.current = onNew;
  });

  const fetcher = useCallback(async () => {
    const result = await api<ActivityItem[]>("GET", `/api/activity?after_id=${cursor.current}`);
    if (result.ok) {
      // Filter at arrival time, so an overlapping response can never add a row twice.
      const fresh = result.data.filter((a) => a.id > cursor.current);
      if (fresh.length > 0) {
        cursor.current = fresh[fresh.length - 1].id;
        setItems((prev) => [...prev, ...fresh].slice(-MAX_ITEMS));
        const runs = fresh.filter((a) => a.kind === "skill_run" && a.ref_id !== null);
        if (runs.length > 0) {
          setSkillRuns((prev) => {
            const next = new Map(prev);
            for (const r of runs) next.set(r.ref_id as number, r.summary);
            return next;
          });
        }
      }
      const initial = first.current;
      first.current = false;
      onNewRef.current?.(fresh, initial);
    }
    return result;
  }, []);

  const { loading, refresh } = usePoll(fetcher, ACTIVITY_POLL_MS);
  return { items, skillRuns, loading, refresh };
}
