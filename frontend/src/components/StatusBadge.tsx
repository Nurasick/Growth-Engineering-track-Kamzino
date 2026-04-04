import type { JobStatus } from "@/lib/api";

const styles: Record<JobStatus, string> = {
  pending: "bg-slate-700 text-slate-300",
  running: "bg-amber-500/20 text-amber-300 animate-pulse",
  done: "bg-green-500/20 text-green-400",
  failed: "bg-red-500/20 text-red-400",
};

const labels: Record<JobStatus, string> = {
  pending: "Pending",
  running: "Running…",
  done: "Done",
  failed: "Failed",
};

export function StatusBadge({ status }: { status: JobStatus }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status]}`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          status === "running"
            ? "bg-amber-400"
            : status === "done"
            ? "bg-green-400"
            : status === "failed"
            ? "bg-red-400"
            : "bg-slate-400"
        }`}
      />
      {labels[status]}
    </span>
  );
}
