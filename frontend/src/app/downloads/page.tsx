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
  if (name.endsWith(".html")) return "HTM";
  if (name.endsWith(".json")) return "JSN";
  return "CSV";
}

function FileRow({ file, downloadHref }: { file: FileInfo; downloadHref: string }) {
  return (
    <div className="flex items-center justify-between gap-4 px-4 py-3 rounded border border-[#242424] bg-[#141414] hover:border-[#2e2e2e] transition-colors group">
      <div className="flex items-center gap-3 min-w-0">
        <span className="text-[10px] font-mono font-bold text-[#CAFF33]/50 bg-[#CAFF33]/5 border border-[#CAFF33]/10 rounded px-1 py-0.5 shrink-0">
          {fileIcon(file.name)}
        </span>
        <span className="text-sm text-white/70 font-mono truncate">{file.name}</span>
      </div>
      <div className="flex items-center gap-4 shrink-0">
        <span className="text-xs text-white/25">{formatSize(file.size_bytes)}</span>
        <a
          href={downloadHref}
          download={file.name}
          className="flex items-center gap-1.5 rounded border border-[#333] px-3 py-1 text-xs font-medium text-white/50 hover:border-[#CAFF33] hover:text-[#CAFF33] transition-colors"
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
    listFiles().then(setFiles).catch((e) => setError(String(e))).finally(() => setLoading(false));
  };

  useEffect(reload, []);

  const tabs: { id: Tab; label: string; count: number | null }[] = [
    { id: "processed", label: "Processed", count: files?.processed.length ?? null },
    { id: "raw",       label: "Raw",       count: files?.raw.length ?? null },
    { id: "other",     label: "Other",     count: files ? files.amplifier.length : null },
  ];

  const currentFiles: { file: FileInfo; href: string }[] =
    !files ? [] :
    tab === "raw"       ? files.raw.map(f => ({ file: f, href: `/api/downloads/raw/${encodeURIComponent(f.name)}` })) :
    tab === "processed" ? files.processed.map(f => ({ file: f, href: `/api/downloads/processed/${encodeURIComponent(f.name)}` })) :
    files.amplifier.map(f => ({ file: f, href: amplifierDownloadUrl() }));

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Downloads</h1>
          <p className="mt-1 text-sm text-white/40">
            Download raw scraper outputs and processed analysis files.
          </p>
        </div>
        <button
          onClick={reload}
          className="rounded border border-[#333] px-3 py-1.5 text-xs text-white/40 hover:text-[#CAFF33] hover:border-[#CAFF33] transition-colors"
        >
          ↺ Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-0 border-b border-[#242424]">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-xs font-medium uppercase tracking-wider border-b-2 transition-colors ${
              tab === t.id
                ? "border-[#CAFF33] text-[#CAFF33]"
                : "border-transparent text-white/30 hover:text-white/60"
            }`}
          >
            {t.label}
            {t.count !== null && (
              <span className="ml-2 rounded bg-[#242424] px-1.5 py-0.5 text-xs text-white/40">
                {t.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {loading && <p className="text-sm text-white/20 animate-pulse">Loading files…</p>}

      {error && (
        <div className="rounded border border-red-900/40 bg-red-950/20 px-4 py-3 text-sm text-red-400">
          {error}
          <br />
          <span className="text-xs text-red-400/60">Make sure the backend is running at localhost:8000</span>
        </div>
      )}

      {!loading && !error && currentFiles.length === 0 && (
        <div className="rounded border border-[#242424] bg-[#141414] px-6 py-10 text-center">
          <p className="text-white/30 text-sm">No files yet.</p>
          <p className="text-white/20 text-xs mt-1">Run the pipeline or scrapers first.</p>
        </div>
      )}

      {!loading && currentFiles.length > 0 && (
        <div className="space-y-1.5">
          {currentFiles.map(({ file, href }) => <FileRow key={file.name} file={file} downloadHref={href} />)}
        </div>
      )}

      {tab === "other" && files && files.amplifier.length > 0 && (
        <div className="rounded border border-[#CAFF33]/20 bg-[#CAFF33]/5 px-4 py-3">
          <p className="text-xs text-[#CAFF33]/80 font-mono">
            amplifier_watchlist.csv — auto-scored X creator watchlist
          </p>
          <a
            href={amplifierDownloadUrl()}
            download="amplifier_watchlist.csv"
            className="mt-2 inline-flex items-center gap-1.5 rounded bg-[#CAFF33] px-3 py-1.5 text-xs font-bold uppercase tracking-wide text-black hover:bg-[#b3e020] transition-colors"
          >
            ↓ Download Amplifier Watchlist
          </a>
        </div>
      )}
    </div>
  );
}
