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

  const totalFiles = files ? files.raw.length + files.processed.length + files.amplifier.length : null;
  const recentJobs = jobs.slice(0, 5);

  const statCards = [
    {
      label: "Backend",
      value: health === null ? "…" : health ? "Online" : "Offline",
      color: health === null ? "text-white/30" : health ? "text-[#CAFF33]" : "text-red-400",
      dot: health === null ? "bg-white/20" : health ? "bg-[#CAFF33] animate-pulse" : "bg-red-500",
    },
    { label: "Raw files",       value: files ? String(files.raw.length)       : "…", color: "text-[#CAFF33]", dot: null },
    { label: "Processed files", value: files ? String(files.processed.length) : "…", color: "text-[#CAFF33]", dot: null },
    { label: "Total files",     value: totalFiles !== null ? String(totalFiles) : "…", color: "text-white",     dot: null },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-white/40">
          Growth Intelligence · HackNU 2026 · 4 platforms
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {statCards.map((s) => (
          <div key={s.label} className="rounded border border-[#242424] bg-[#141414] p-4">
            <div className="flex items-center gap-2 text-xs text-white/30 mb-1 uppercase tracking-wider">
              {s.dot && <span className={`h-2 w-2 rounded-full ${s.dot}`} />}
              {s.label}
            </div>
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest mb-3">
          Quick Actions
        </h2>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/pipeline"
            className="rounded bg-[#CAFF33] px-4 py-2 text-xs font-bold tracking-wide uppercase text-black hover:bg-[#b3e020] transition-colors"
          >
            ▶ Run Full Pipeline
          </Link>
          <Link
            href="/scrapers"
            className="rounded border border-[#333] px-4 py-2 text-xs font-medium text-white/60 hover:border-[#CAFF33] hover:text-[#CAFF33] transition-colors"
          >
            Run Scrapers
          </Link>
          <Link
            href="/downloads"
            className="rounded border border-[#333] px-4 py-2 text-xs font-medium text-white/60 hover:border-[#CAFF33] hover:text-[#CAFF33] transition-colors"
          >
            Download CSVs
          </Link>
        </div>
      </div>

      {/* Recent jobs */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest">
            Recent Jobs
          </h2>
          <Link href="/scrapers" className="text-xs text-[#CAFF33]/70 hover:text-[#CAFF33]">
            View all →
          </Link>
        </div>

        {recentJobs.length === 0 ? (
          <p className="text-sm text-white/20">No jobs yet — run a scraper or the pipeline.</p>
        ) : (
          <div className="space-y-1.5">
            {recentJobs.map((j) => (
              <div
                key={j.id}
                className="flex items-center justify-between rounded border border-[#242424] bg-[#141414] px-4 py-3"
              >
                <span className="text-sm text-white/70 truncate mr-4">{j.label}</span>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs text-white/20">{j.id}</span>
                  <StatusBadge status={j.status} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Processed files */}
      {files && files.processed.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest">
              Processed Files
            </h2>
            <Link href="/downloads" className="text-xs text-[#CAFF33]/70 hover:text-[#CAFF33]">
              Download all →
            </Link>
          </div>
          <div className="flex flex-wrap gap-2">
            {files.processed.map((f) => (
              <a
                key={f.name}
                href={`/api/downloads/processed/${encodeURIComponent(f.name)}`}
                download={f.name}
                className="flex items-center gap-2 rounded border border-[#222] bg-[#141414] px-3 py-2 text-xs text-white/50 hover:border-[#CAFF33] hover:text-[#CAFF33] transition-colors"
              >
                <span>↓</span>
                <span className="font-mono">{f.name}</span>
                <span className="text-white/20">{(f.size_bytes / 1024).toFixed(1)} KB</span>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
