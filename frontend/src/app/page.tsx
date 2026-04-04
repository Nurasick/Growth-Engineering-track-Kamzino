"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { checkHealth, listFiles, listScraperJobs, listPipelineJobs } from "@/lib/api";
import type { Job, FilesResponse } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";

export default function DashboardPage() {
  const [health, setHealth] = useState<boolean | null>(null);
  const [files, setFiles] = useState<FilesResponse | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    checkHealth().then((r) => setHealth(r?.status === "ok"));
    listFiles().then(setFiles).catch(() => {});
    Promise.all([listScraperJobs(), listPipelineJobs()])
      .then(([s, p]) => setJobs([...s, ...p].sort((a, b) => (b.started_at ?? "").localeCompare(a.started_at ?? ""))))
      .catch(() => {});
  }, []);

  const totalFiles = files
    ? files.raw.length + files.processed.length + files.amplifier.length
    : null;

  const recentJobs = jobs.slice(0, 5);

  const statCards = [
    {
      label: "Backend",
      value: health === null ? "…" : health ? "Online" : "Offline",
      color: health === null ? "text-slate-400" : health ? "text-green-400" : "text-red-400",
      dot: health === null ? "bg-slate-500" : health ? "bg-green-400 animate-pulse" : "bg-red-500",
    },
    {
      label: "Raw files",
      value: files ? String(files.raw.length) : "…",
      color: "text-violet-300",
      dot: null,
    },
    {
      label: "Processed files",
      value: files ? String(files.processed.length) : "…",
      color: "text-violet-300",
      dot: null,
    },
    {
      label: "Total files",
      value: totalFiles !== null ? String(totalFiles) : "…",
      color: "text-slate-200",
      dot: null,
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-100">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-400">
          Growth Intelligence · HackNU 2026 · 4 platforms
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {statCards.map((s) => (
          <div key={s.label} className="rounded-xl border border-slate-700 bg-slate-800/60 p-4">
            <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
              {s.dot && <span className={`h-2 w-2 rounded-full ${s.dot}`} />}
              {s.label}
            </div>
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
          Quick Actions
        </h2>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/pipeline"
            className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-500 transition-colors"
          >
            ▶ Run Full Pipeline
          </Link>
          <Link
            href="/scrapers"
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 hover:border-slate-400 hover:text-slate-100 transition-colors"
          >
            Run Scrapers
          </Link>
          <Link
            href="/downloads"
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 hover:border-slate-400 hover:text-slate-100 transition-colors"
          >
            Download CSVs
          </Link>
        </div>
      </div>

      {/* Recent jobs */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
            Recent Jobs
          </h2>
          <Link href="/scrapers" className="text-xs text-violet-400 hover:text-violet-300">
            View all →
          </Link>
        </div>

        {recentJobs.length === 0 ? (
          <p className="text-sm text-slate-500">No jobs yet — run a scraper or the pipeline.</p>
        ) : (
          <div className="space-y-2">
            {recentJobs.map((j) => (
              <div
                key={j.id}
                className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-3"
              >
                <span className="text-sm text-slate-300 truncate mr-4">{j.label}</span>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs text-slate-500">{j.id}</span>
                  <StatusBadge status={j.status} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Available processed files preview */}
      {files && files.processed.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
              Processed Files
            </h2>
            <Link href="/downloads" className="text-xs text-violet-400 hover:text-violet-300">
              Download all →
            </Link>
          </div>
          <div className="flex flex-wrap gap-2">
            {files.processed.map((f) => (
              <a
                key={f.name}
                href={`/api/downloads/processed/${encodeURIComponent(f.name)}`}
                download={f.name}
                className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800/60 px-3 py-2 text-xs text-slate-300 hover:border-violet-600 hover:text-violet-300 transition-colors"
              >
                <span>↓</span>
                <span>{f.name}</span>
                <span className="text-slate-500">{(f.size_bytes / 1024).toFixed(1)} KB</span>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
