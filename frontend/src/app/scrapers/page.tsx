"use client";

import { useEffect, useState } from "react";
import { runScraper, getScraperJob, listScraperJobs } from "@/lib/api";
import type { Job } from "@/lib/api";
import { useJob } from "@/lib/useJob";
import { JobCard } from "@/components/JobCard";

const SCRAPERS = [
  {
    id: "hn" as const,
    name: "Hacker News",
    icon: "🟠",
    description: "Algolia API · stories & comments · last 7 days",
    outputHint: "hn_items_YYYY-MM-DD.csv",
  },
  {
    id: "reddit" as const,
    name: "Reddit",
    icon: "🔴",
    description: "Public JSON API · 5 subreddits",
    outputHint: "reddit_posts_YYYY-MM-DD.csv",
  },
  {
    id: "x" as const,
    name: "X / Twitter",
    icon: "🐦",
    description: "fxtwitter + DDG/Bing/Brave discovery",
    outputHint: "x_case_raw.csv",
  },
  {
    id: "youtube" as const,
    name: "YouTube",
    icon: "▶️",
    description: "Data API v3 · requires YOUTUBE_API_KEY",
    outputHint: "youtube_videos_YYYY-MM-DD.csv",
  },
];

function ScraperCard({ scraper }: { scraper: (typeof SCRAPERS)[number] }) {
  const { job, loading, error, start } = useJob(getScraperJob);

  const handleRun = () =>
    start(() => runScraper(scraper.id).then((r) => ({ job_id: r.job_id })));

  const busy = loading || job?.status === "running" || job?.status === "pending";

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{scraper.icon}</span>
            <span className="font-semibold text-slate-100">{scraper.name}</span>
          </div>
          <p className="text-xs text-slate-400">{scraper.description}</p>
          <p className="text-xs text-slate-600 mt-1 font-mono">→ {scraper.outputHint}</p>
        </div>

        <button
          onClick={handleRun}
          disabled={busy}
          className="shrink-0 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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

export default function ScrapersPage() {
  const [allJobs, setAllJobs] = useState<Job[]>([]);

  useEffect(() => {
    listScraperJobs()
      .then((jobs) => setAllJobs(jobs.slice(0, 20)))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-100">Scrapers</h1>
        <p className="mt-1 text-sm text-slate-400">
          Trigger individual platform scrapers. Each run saves a raw CSV to{" "}
          <span className="font-mono text-slate-300">data/raw/</span>.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {SCRAPERS.map((s) => (
          <ScraperCard key={s.id} scraper={s} />
        ))}
      </div>

      {allJobs.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
            All Scraper Jobs
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
