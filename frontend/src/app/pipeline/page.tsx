"use client";

import { useEffect, useState } from "react";
import { runPipeline, getPipelineJob, listPipelineJobs } from "@/lib/api";
import type { Job } from "@/lib/api";
import { useJob } from "@/lib/useJob";
import { JobCard } from "@/components/JobCard";

const STEPS = [
  {
    id: "normalize",
    label: "Normalize",
    description: "Merge all raw sources → unified_posts.csv",
    icon: "🔀",
  },
  {
    id: "classify",
    label: "Classify",
    description: "Label spike types (breakthrough, tutorial, meme…)",
    icon: "🏷️",
  },
  {
    id: "rank",
    label: "Rank",
    description: "Velocity ranking with HN gravity formula",
    icon: "📈",
  },
  {
    id: "visualize",
    label: "Visualize",
    description: "Generate virality_timeline.html dashboard",
    icon: "📊",
  },
];

function StepButton({
  step,
}: {
  step: (typeof STEPS)[number];
}) {
  const { job, loading, error, start } = useJob(getPipelineJob);
  const busy = loading || job?.status === "running" || job?.status === "pending";

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-4 space-y-3">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-xl">{step.icon}</span>
          <div>
            <div className="text-sm font-medium text-slate-200">{step.label}</div>
            <div className="text-xs text-slate-400">{step.description}</div>
          </div>
        </div>
        <button
          onClick={() => start(() => runPipeline(step.id))}
          disabled={busy}
          className="shrink-0 rounded-md border border-slate-600 px-3 py-1.5 text-xs font-medium text-slate-300 hover:border-violet-500 hover:text-violet-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {busy ? "Running…" : "Run"}
        </button>
      </div>

      {error && (
        <p className="text-xs text-red-400 rounded bg-red-950/40 px-3 py-2">{error}</p>
      )}
      {job && <JobCard job={job} />}
    </div>
  );
}

function PipelineMainButton({
  label,
  description,
  action,
  accent,
}: {
  label: string;
  description: string;
  action: () => Promise<{ job_id: string }>;
  accent?: boolean;
}) {
  const { job, loading, error, start } = useJob(getPipelineJob);
  const busy = loading || job?.status === "running" || job?.status === "pending";

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-base font-semibold text-slate-100 mb-1">{label}</div>
          <p className="text-sm text-slate-400">{description}</p>
        </div>
        <button
          onClick={() => start(action)}
          disabled={busy}
          className={`shrink-0 rounded-lg px-5 py-2.5 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
            accent
              ? "bg-violet-600 text-white hover:bg-violet-500"
              : "border border-slate-600 text-slate-300 hover:border-slate-400 hover:text-slate-100"
          }`}
        >
          {busy ? "Running…" : "▶ Run"}
        </button>
      </div>

      {error && (
        <p className="text-xs text-red-400 rounded bg-red-950/40 px-3 py-2">{error}</p>
      )}
      {job && <JobCard job={job} />}
    </div>
  );
}

export default function PipelinePage() {
  const [demo, setDemo] = useState(false);
  const [allJobs, setAllJobs] = useState<Job[]>([]);

  useEffect(() => {
    listPipelineJobs()
      .then((jobs) => setAllJobs(jobs.slice(0, 20)))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-100">Pipeline</h1>
        <p className="mt-1 text-sm text-slate-400">
          Run the full pipeline or trigger individual analysis steps.
        </p>
      </div>

      {/* Main pipeline buttons */}
      <div className="space-y-3">
        <div className="flex items-center gap-3 mb-1">
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
            Full Run
          </h2>
          <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer ml-auto">
            <input
              type="checkbox"
              checked={demo}
              onChange={(e) => setDemo(e.target.checked)}
              className="accent-violet-500"
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

      {/* Individual steps */}
      <div>
        <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
          Individual Steps
        </h2>
        <div className="space-y-2">
          {STEPS.map((s) => (
            <StepButton key={s.id} step={s} />
          ))}
        </div>
      </div>

      {/* Job history */}
      {allJobs.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
            Job History
          </h2>
          <div className="space-y-2">
            {allJobs.map((j) => (
              <JobCard key={j.id} job={j} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
