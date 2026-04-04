"use client";

import { useEffect, useState } from "react";
import { runPipeline, getPipelineJob, listPipelineJobs } from "@/lib/api";
import type { Job } from "@/lib/api";
import { useJob } from "@/lib/useJob";
import { JobCard } from "@/components/JobCard";

const STEPS = [
  { id: "normalize", label: "Normalize", description: "Merge all raw sources → unified_posts.csv",       icon: "01" },
  { id: "classify",  label: "Classify",  description: "Label spike types (breakthrough, tutorial, meme…)", icon: "02" },
  { id: "rank",      label: "Rank",      description: "Velocity ranking with HN gravity formula",          icon: "03" },
  { id: "visualize", label: "Visualize", description: "Generate virality_timeline.html dashboard",         icon: "04" },
];

function StepButton({ step }: { step: (typeof STEPS)[number] }) {
  const { job, loading, error, start } = useJob(getPipelineJob);
  const busy = loading || job?.status === "running" || job?.status === "pending";

  return (
    <div className="rounded border border-[#242424] bg-[#141414] p-4 space-y-3">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-mono text-[#CAFF33]/50 w-6">{step.icon}</span>
          <div>
            <div className="text-sm font-medium text-white">{step.label}</div>
            <div className="text-xs text-white/40">{step.description}</div>
          </div>
        </div>
        <button
          onClick={() => start(() => runPipeline(step.id))}
          disabled={busy}
          className="shrink-0 rounded border border-[#333] px-3 py-1.5 text-xs font-medium text-white/60 hover:border-[#CAFF33] hover:text-[#CAFF33] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          {busy ? "Running…" : "Run"}
        </button>
      </div>
      {error && <p className="text-xs text-red-400 rounded bg-red-950/20 border border-red-900/30 px-3 py-2">{error}</p>}
      {job && <JobCard job={job} />}
    </div>
  );
}

function PipelineMainButton({ label, description, action, accent }: {
  label: string;
  description: string;
  action: () => Promise<{ job_id: string }>;
  accent?: boolean;
}) {
  const { job, loading, error, start } = useJob(getPipelineJob);
  const busy = loading || job?.status === "running" || job?.status === "pending";

  return (
    <div className="rounded border border-[#242424] bg-[#141414] p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-base font-semibold text-white mb-1">{label}</div>
          <p className="text-sm text-white/40">{description}</p>
        </div>
        <button
          onClick={() => start(action)}
          disabled={busy}
          className={`shrink-0 rounded px-5 py-2.5 text-xs font-bold uppercase tracking-wide transition-colors disabled:opacity-30 disabled:cursor-not-allowed ${
            accent
              ? "bg-[#CAFF33] text-black hover:bg-[#b3e020]"
              : "border border-[#333] text-white/60 hover:border-[#CAFF33] hover:text-[#CAFF33]"
          }`}
        >
          {busy ? "Running…" : "▶ Run"}
        </button>
      </div>
      {error && <p className="text-xs text-red-400 rounded bg-red-950/20 border border-red-900/30 px-3 py-2">{error}</p>}
      {job && <JobCard job={job} />}
    </div>
  );
}

export default function PipelinePage() {
  const [demo, setDemo] = useState(false);
  const [allJobs, setAllJobs] = useState<Job[]>([]);

  useEffect(() => {
    listPipelineJobs().then((jobs) => setAllJobs(jobs.slice(0, 20))).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Pipeline</h1>
        <p className="mt-1 text-sm text-white/40">
          Run the full pipeline or trigger individual analysis steps.
        </p>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-3 mb-1">
          <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest">Full Run</h2>
          <label className="flex items-center gap-2 text-xs text-white/40 cursor-pointer ml-auto">
            <input
              type="checkbox"
              checked={demo}
              onChange={(e) => setDemo(e.target.checked)}
              className="accent-[#CAFF33]"
            />
            Demo mode (faster, fewer pages)
          </label>
        </div>
        <PipelineMainButton
          label="Full Pipeline"
          description="Scrape all sources + normalize + classify + rank + visualize"
          action={() => runPipeline("run", demo ? { demo: "true" } : undefined)}
          accent
        />
        <PipelineMainButton
          label="Analysis Only"
          description="Skip scrapers, re-analyze existing data in data/raw/"
          action={() => runPipeline("analyze")}
        />
      </div>

      <div>
        <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest mb-3">Individual Steps</h2>
        <div className="space-y-2">
          {STEPS.map((s) => <StepButton key={s.id} step={s} />)}
        </div>
      </div>

      {allJobs.length > 0 && (
        <div>
          <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest mb-3">Job History</h2>
          <div className="space-y-2">
            {allJobs.map((j) => <JobCard key={j.id} job={j} />)}
          </div>
        </div>
      )}
    </div>
  );
}
