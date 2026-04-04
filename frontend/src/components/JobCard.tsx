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
    <div className="rounded border border-[#222] bg-[#141414] p-4 text-sm">
      <div className="flex items-center justify-between gap-4">
        <span className="font-medium text-white/80 truncate">{job.label}</span>
        <div className="flex items-center gap-3 shrink-0">
          <span className="text-white/25 text-xs">{ago(job.started_at)}</span>
          <StatusBadge status={job.status} />
        </div>
      </div>

      {job.output && (
        <pre className="mt-3 max-h-40 overflow-y-auto rounded bg-[#0d0d0d] border border-[#1e1e1e] p-3 text-xs text-[#CAFF33]/70 whitespace-pre-wrap font-mono">
          {job.output}
        </pre>
      )}

      {job.error && (
        <pre className="mt-3 max-h-24 overflow-y-auto rounded bg-red-950/20 border border-red-900/40 p-3 text-xs text-red-400 whitespace-pre-wrap font-mono">
          {job.error}
        </pre>
      )}
    </div>
  );
}
