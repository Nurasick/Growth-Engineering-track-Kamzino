const BASE =
  typeof window === "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
    : "";  // use Next.js rewrite proxy on client

export type JobStatus = "pending" | "running" | "done" | "failed";

export interface Job {
  id: string;
  label: string;
  status: JobStatus;
  started_at: string | null;
  finished_at: string | null;
  output: string;
  error: string;
}

export interface FileInfo {
  name: string;
  size_bytes: number;
  location: string;
}

export interface FilesResponse {
  raw: FileInfo[];
  processed: FileInfo[];
  amplifier: FileInfo[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(text);
  }
  return res.json() as Promise<T>;
}

// ── scrapers ──────────────────────────────────────────────────────────────────

export const runScraper = (
  source: "hn" | "reddit" | "x" | "youtube",
  params?: Record<string, string>
) => {
  const url = new URL(`${window.location.origin}/api/scrapers/${source}`);
  if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  return request<{ job_id: string; scraper: string }>(
    `/api/scrapers/${source}${params ? "?" + new URLSearchParams(params) : ""}`,
    { method: "POST" }
  );
};

export const getScraperJob = (id: string) =>
  request<Job>(`/api/scrapers/jobs/${id}`);

export const listScraperJobs = () =>
  request<Job[]>("/api/scrapers/jobs");

// ── pipeline ──────────────────────────────────────────────────────────────────

export const runPipeline = (step: string, params?: Record<string, string>) =>
  request<{ job_id: string }>(
    `/api/pipeline/${step}${params ? "?" + new URLSearchParams(params) : ""}`,
    { method: "POST" }
  );

export const getPipelineJob = (id: string) =>
  request<Job>(`/api/pipeline/jobs/${id}`);

export const listPipelineJobs = () =>
  request<Job[]>("/api/pipeline/jobs");

// ── downloads ─────────────────────────────────────────────────────────────────

export const listFiles = () => request<FilesResponse>("/api/downloads/files");

export const downloadUrl = (bucket: "raw" | "processed", filename: string) =>
  `${BASE}/api/downloads/${bucket}/${encodeURIComponent(filename)}`;

export const amplifierDownloadUrl = () => `${BASE}/api/downloads/amplifier`;

// ── health ────────────────────────────────────────────────────────────────────

export const checkHealth = () =>
  request<{ status: string }>("/api/health").catch(() => null);
