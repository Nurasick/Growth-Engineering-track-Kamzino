import type { JobStatus } from "@/lib/api";

const styles: Record<JobStatus, string> = {
  pending: "bg-white/5 text-white/40",
  running: "bg-[#CAFF33]/10 text-[#CAFF33] animate-pulse",
  done:    "bg-[#CAFF33]/15 text-[#CAFF33]",
  failed:  "bg-red-500/15 text-red-400",
};

const labels: Record<JobStatus, string> = {
  pending: "Pending",
  running: "Running…",
  done:    "Done",
  failed:  "Failed",
};

const dots: Record<JobStatus, string> = {
  pending: "bg-white/30",
  running: "bg-[#CAFF33]",
  done:    "bg-[#CAFF33]",
  failed:  "bg-red-400",
};

export function StatusBadge({ status }: { status: JobStatus }) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-xs font-medium tracking-wide ${styles[status]}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${dots[status]}`} />
      {labels[status]}
    </span>
  );
}
