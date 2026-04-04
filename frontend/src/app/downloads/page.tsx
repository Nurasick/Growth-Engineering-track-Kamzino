"use client";

import { useEffect, useState } from "react";
import { listFiles, amplifierDownloadUrl } from "@/lib/api";
import type { FileInfo, FilesResponse } from "@/lib/api";

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileIcon(name: string): string {
  if (name.endsWith(".html")) return "🌐";
  if (name.endsWith(".json")) return "{}";
  return "📄";
}

function FileRow({
  file,
  downloadHref,
}: {
  file: FileInfo;
  downloadHref: string;
}) {
  return (
    <div className="flex items-center justify-between gap-4 px-4 py-3 rounded-lg border border-slate-700/60 bg-slate-800/40 hover:border-slate-600 transition-colors group">
      <div className="flex items-center gap-3 min-w-0">
        <span className="text-base shrink-0">{fileIcon(file.name)}</span>
        <span className="text-sm text-slate-200 font-mono truncate">{file.name}</span>
      </div>
      <div className="flex items-center gap-4 shrink-0">
        <span className="text-xs text-slate-500">{formatSize(file.size_bytes)}</span>
        <a
          href={downloadHref}
          download={file.name}
          className="flex items-center gap-1.5 rounded-md border border-slate-600 px-3 py-1 text-xs font-medium text-slate-300 hover:border-violet-500 hover:text-violet-300 transition-colors"
        >
          ↓ Download
        </a>
      </div>
    </div>
  );
}

type Tab = "processed" | "raw" | "other";

export default function DownloadsPage() {
  const [files, setFiles] = useState<FilesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("processed");

  const reload = () => {
    setLoading(true);
    setError(null);
    listFiles()
      .then(setFiles)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  };

  useEffect(reload, []);

  const tabs: { id: Tab; label: string; count: number | null }[] = [
    { id: "processed", label: "Processed", count: files?.processed.length ?? null },
    { id: "raw", label: "Raw", count: files?.raw.length ?? null },
    { id: "other", label: "Other", count: files ? files.amplifier.length : null },
  ];

  const currentFiles: { file: FileInfo; href: string }[] =
    !files
      ? []
      : tab === "raw"
      ? files.raw.map((f) => ({ file: f, href: `/api/downloads/raw/${encodeURIComponent(f.name)}` }))
      : tab === "processed"
      ? files.processed.map((f) => ({
          file: f,
          href: `/api/downloads/processed/${encodeURIComponent(f.name)}`,
        }))
      : files.amplifier.map((f) => ({
          file: f,
          href: amplifierDownloadUrl(),
        }));

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-100">Downloads</h1>
          <p className="mt-1 text-sm text-slate-400">
            Download raw scraper outputs and processed analysis files.
          </p>
        </div>
        <button
          onClick={reload}
          className="rounded-lg border border-slate-600 px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 hover:border-slate-400 transition-colors"
        >
          ↺ Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-800">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t.id
                ? "border-violet-500 text-violet-300"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {t.label}
            {t.count !== null && (
              <span className="ml-2 rounded-full bg-slate-700 px-1.5 py-0.5 text-xs text-slate-300">
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading && (
        <p className="text-sm text-slate-500 animate-pulse">Loading files…</p>
      )}

      {error && (
        <div className="rounded-lg border border-red-800 bg-red-950/30 px-4 py-3 text-sm text-red-300">
          {error}
          <br />
          <span className="text-xs text-red-400">Make sure the backend is running at localhost:8000</span>
        </div>
      )}

      {!loading && !error && currentFiles.length === 0 && (
        <div className="rounded-lg border border-slate-700 bg-slate-800/40 px-6 py-10 text-center">
          <p className="text-slate-400 text-sm">No files yet.</p>
          <p className="text-slate-500 text-xs mt-1">
            Run the pipeline or scrapers first to generate output files.
          </p>
        </div>
      )}

      {!loading && currentFiles.length > 0 && (
        <div className="space-y-2">
          {currentFiles.map(({ file, href }) => (
            <FileRow key={file.name} file={file} downloadHref={href} />
          ))}
        </div>
      )}

      {/* Amplifier quick download */}
      {tab === "other" && files && files.amplifier.length > 0 && (
        <div className="rounded-lg border border-violet-800/50 bg-violet-950/20 px-4 py-3">
          <p className="text-xs text-violet-300">
            <strong>amplifier_watchlist.csv</strong> — auto-scored X creator watchlist
          </p>
          <a
            href={amplifierDownloadUrl()}
            download="amplifier_watchlist.csv"
            className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-violet-700 px-3 py-1.5 text-xs font-medium text-white hover:bg-violet-600 transition-colors"
          >
            ↓ Download Amplifier Watchlist
          </a>
        </div>
      )}
    </div>
  );
}
