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

export const runPlaybookMetrics = () =>
  request<{ job_id: string }>("/api/pipeline/playbook-metrics", { method: "POST" });

export const runPlaybookAnalysis = () =>
  request<{ job_id: string }>("/api/pipeline/playbook-analysis", { method: "POST" });

export const runCounterPlaybook = () =>
  request<{ job_id: string }>("/api/pipeline/counter-playbook", { method: "POST" });

// ── downloads ─────────────────────────────────────────────────────────────────

export const listFiles = () => request<FilesResponse>("/api/downloads/files");

export const downloadUrl = (bucket: "raw" | "processed", filename: string) =>
  `${BASE}/api/downloads/${bucket}/${encodeURIComponent(filename)}`;

export const amplifierDownloadUrl = () => `${BASE}/api/downloads/amplifier`;

// ── charts ────────────────────────────────────────────────────────────────────

export interface HnStory {
  title: string;
  points: number;
  url: string;
  comments: number;
}

export interface YoutubeEngagementPoint {
  period: string;
  avg_engagement_rate: number;
  median_engagement_rate: number;
  video_count: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  hn_item_count: number;
  hn_total_score: number;
  hn_top_stories: HnStory[];
}

export interface YoutubeEngagementResponse {
  data: YoutubeEngagementPoint[];
  summary: {
    total_videos: number;
    overall_avg_engagement_rate: number;
    date_range: string;
    source_file: string;
  };
}

export const getYoutubeEngagement = () =>
  request<YoutubeEngagementResponse>("/api/charts/youtube-engagement");

export interface RedditPost {
  title: string;
  score: number;
  comments: number;
  ratio: number;
  url: string;
  subreddit: string;
  date: string;
}

export interface RedditEngagementPoint {
  period: string;
  avg_score: number;
  median_score: number;
  avg_comments: number;
  post_count: number;
  total_score: number;
  total_comments: number;
  top_posts: RedditPost[];
  hn_item_count: number;
  hn_total_score: number;
  hn_top_stories: HnStory[];
}

export interface RedditEngagementResponse {
  data: RedditEngagementPoint[];
  summary: {
    total_posts: number;
    overall_avg_score: number;
    date_range: string;
    source_file: string;
  };
}

export const getRedditEngagement = () =>
  request<RedditEngagementResponse>("/api/charts/reddit-engagement");

// ── analytics ─────────────────────────────────────────────────────────────────

export interface SpikeStat {
  spike_type: string;
  count: number;
  pct: number;
  mean_engagement: number;
  median_engagement: number;
}

export interface PlatformStat {
  platform: string;
  count: number;
  mean_engagement: number;
  median_engagement: number;
}

export interface Creator {
  author: string;
  platform: string;
  posts: number;
  total_engagement: number;
}

export interface WeeklyTrend {
  weeks: string[];
  series: Record<string, number[]>;
}

export interface AnalyticsSummary {
  total_posts: number;
  date_range: { from: string | null; to: string | null };
  spike_breakdown: SpikeStat[];
  platform_breakdown: PlatformStat[];
  weekly_trend: WeeklyTrend;
  top_creators: Creator[];
}

export interface FeedPost {
  post_id: string;
  title: string;
  body_text: string;
  platform: string;
  author: string;
  url: string;
  spike_type: string;
  confidence: number;
  engagement_score: number;
  velocity: number;
  age_hours: number;
  created_at: string | null;
}

export interface Alert {
  title: string;
  platform: string;
  author: string;
  velocity: number;
  age_hours: number;
  spike_type: string;
  url: string;
}

export const getAnalyticsSummary = () =>
  request<AnalyticsSummary>("/api/analytics/summary");

export const getAnalyticsFeed = (params?: { platform?: string; spike_type?: string; limit?: number }) => {
  const qs = params ? "?" + new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined).map(([k, v]) => [k, String(v)]))
  ) : "";
  return request<{ total: number; posts: FeedPost[] }>(`/api/analytics/feed${qs}`);
};

export const getAlerts = (threshold?: number) =>
  request<{ count: number; threshold: number; alerts: Alert[] }>(
    `/api/analytics/alerts${threshold !== undefined ? `?velocity_threshold=${threshold}` : ""}`
  );

// ── health ────────────────────────────────────────────────────────────────────

export const checkHealth = () =>
  request<{ status: string }>("/api/health").catch(() => null);
