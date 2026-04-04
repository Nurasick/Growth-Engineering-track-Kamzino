import type { Job } from "@/lib/api";
import { StatusBadge } from "./StatusBadge";

function ago(iso: string | null): string {
  if (!iso) return "";
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export function JobCard({ job }: { job: Job }) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-4 text-sm">
      <div className="flex items-center justify-between gap-4">
        <span className="font-medium text-slate-200 truncate">{job.label}</span>
        <div className="flex items-center gap-3 shrink-0">
          <span className="text-slate-500 text-xs">{ago(job.started_at)}</span>
          <StatusBadge status={job.status} />
        </div>
      </div>

      {job.output && (
        <pre className="mt-3 max-h-40 overflow-y-auto rounded bg-slate-900 p-3 text-xs text-slate-300 whitespace-pre-wrap">
          {job.output}
        </pre>
      )}

      {job.error && (
        <pre className="mt-3 max-h-24 overflow-y-auto rounded bg-red-950/50 p-3 text-xs text-red-300 whitespace-pre-wrap">
          {job.error}
        </pre>
      )}
    </div>
  );
}
