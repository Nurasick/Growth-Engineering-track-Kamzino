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
    icon: "HN",
    description: "Algolia API · stories & comments · last 7 days",
    outputHint: "hn_items_YYYY-MM-DD.csv",
  },
  {
    id: "reddit" as const,
    name: "Reddit",
    icon: "RD",
    description: "Public JSON API · 5 subreddits",
    outputHint: "reddit_posts_YYYY-MM-DD.csv",
  },
  {
    id: "x" as const,
    name: "X / Twitter",
    icon: "X",
    description: "fxtwitter + DDG/Bing/Brave discovery",
    outputHint: "x_case_raw.csv",
  },
  {
    id: "youtube" as const,
    name: "YouTube",
    icon: "YT",
    description: "Data API v3 · requires YOUTUBE_API_KEY",
    outputHint: "youtube_videos_YYYY-MM-DD.csv",
  },
];

function ScraperCard({ scraper }: { scraper: (typeof SCRAPERS)[number] }) {
  const { job, loading, error, start } = useJob(getScraperJob);
  const handleRun = () => start(() => runScraper(scraper.id).then((r) => ({ job_id: r.job_id })));
  const busy = loading || job?.status === "running" || job?.status === "pending";

  return (
    <div className="rounded border border-[#242424] bg-[#141414] p-5 space-y-4 hover:border-[#2e2e2e] transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <span className="rounded bg-[#CAFF33]/10 border border-[#CAFF33]/30 px-2 py-0.5 text-xs font-bold text-[#CAFF33] font-mono">
              {scraper.icon}
            </span>
            <span className="font-semibold text-white">{scraper.name}</span>
          </div>
          <p className="text-xs text-white/40">{scraper.description}</p>
          <p className="text-xs text-white/20 mt-1 font-mono">→ {scraper.outputHint}</p>
        </div>
        <button
          onClick={handleRun}
          disabled={busy}
          className="shrink-0 rounded bg-[#CAFF33] px-4 py-2 text-xs font-bold uppercase tracking-wide text-black hover:bg-[#b3e020] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          {busy ? "Running…" : "Run"}
        </button>
      </div>
      {error && <p className="text-xs text-red-400 rounded bg-red-950/20 border border-red-900/30 px-3 py-2">{error}</p>}
      {job && <JobCard job={job} />}
    </div>
  );
}

export default function ScrapersPage() {
  const [allJobs, setAllJobs] = useState<Job[]>([]);

  useEffect(() => {
    listScraperJobs().then((jobs) => setAllJobs(jobs.slice(0, 20))).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Scrapers</h1>
        <p className="mt-1 text-sm text-white/40">
          Trigger individual platform scrapers. Each run saves a raw CSV to{" "}
          <span className="font-mono text-white/60">data/raw/</span>.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {SCRAPERS.map((s) => <ScraperCard key={s.id} scraper={s} />)}
      </div>

      {allJobs.length > 0 && (
        <div>
          <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest mb-3">
            All Scraper Jobs
          </h2>
          <div className="space-y-2">
            {allJobs.map((j) => <JobCard key={j.id} job={j} />)}
          </div>
        </div>
      )}
    </div>
  );
}
