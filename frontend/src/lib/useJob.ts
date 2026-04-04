import { useCallback, useEffect, useRef, useState } from "react";
import type { Job, JobStatus } from "./api";

type Fetcher = (id: string) => Promise<Job>;

const TERMINAL: JobStatus[] = ["done", "failed"];

export function useJob(fetcher: Fetcher, intervalMs = 2000) {
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const poll = useCallback(
    (id: string) => {
      const tick = async () => {
        try {
          const j = await fetcher(id);
          setJob(j);
          if (TERMINAL.includes(j.status)) stopPolling();
        } catch (e) {
          setError(String(e));
          stopPolling();
        }
      };
      tick();
      timerRef.current = setInterval(tick, intervalMs);
    },
    [fetcher, intervalMs, stopPolling]
  );

  const start = useCallback(
    async (action: () => Promise<{ job_id: string }>) => {
      setLoading(true);
      setError(null);
      setJob(null);
      stopPolling();
      try {
        const { job_id } = await action();
        poll(job_id);
      } catch (e) {
        setError(String(e));
      } finally {
        setLoading(false);
      }
    },
    [poll, stopPolling]
  );

  useEffect(() => () => stopPolling(), [stopPolling]);

  return { job, loading, error, start };
}
