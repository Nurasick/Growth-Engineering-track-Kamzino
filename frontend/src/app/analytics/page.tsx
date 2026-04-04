"use client";

import { useEffect, useState } from "react";
import {
  getAnalyticsSummary,
  getAnalyticsFeed,
  getAlerts,
} from "@/lib/api";
import type { AnalyticsSummary, FeedPost, Alert } from "@/lib/api";

const PLATFORM_COLORS: Record<string, string> = {
  hn:      "text-orange-400 bg-orange-950/40 border-orange-800",
  reddit:  "text-red-400   bg-red-950/40    border-red-800",
  youtube: "text-rose-400  bg-rose-950/40   border-rose-800",
  x:       "text-sky-400   bg-sky-950/40    border-sky-800",
};

const SPIKE_COLORS: Record<string, string> = {
  breakthrough: "text-blue-400   bg-blue-950/40",
  tutorial:     "text-amber-400  bg-amber-950/40",
  personal:     "text-green-400  bg-green-950/40",
  meme:         "text-pink-400   bg-pink-950/40",
  comparison:   "text-purple-400 bg-purple-950/40",
};

function PlatformBadge({ platform }: { platform: string }) {
  const cls = PLATFORM_COLORS[platform] ?? "text-slate-400 bg-slate-800 border-slate-700";
  return (
    <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-xs font-medium ${cls}`}>
      {platform.toUpperCase()}
    </span>
  );
}

function SpikeBadge({ type }: { type: string }) {
  const cls = SPIKE_COLORS[type] ?? "text-slate-400 bg-slate-800";
  return (
    <span className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs ${cls}`}>
      {type}
    </span>
  );
}

function VelocityBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 rounded-full bg-slate-700">
        <div
          className="h-1.5 rounded-full bg-violet-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs text-slate-400 tabular-nums">{value.toFixed(3)}</span>
    </div>
  );
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-4">
      <div className="text-xs text-slate-400 mb-1">{label}</div>
      <div className="text-2xl font-bold text-slate-100">{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [feed, setFeed] = useState<FeedPost[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [platformFilter, setPlatformFilter] = useState("all");
  const [spikeFilter, setSpikeFilter] = useState("all");

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getAnalyticsSummary(),
      getAnalyticsFeed({ limit: 50 }),
      getAlerts(0.05),
    ])
      .then(([s, f, a]) => {
        setSummary(s);
        setFeed(f.posts);
        setAlerts(a.alerts);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    getAnalyticsFeed({
      platform: platformFilter === "all" ? undefined : platformFilter,
      spike_type: spikeFilter === "all" ? undefined : spikeFilter,
      limit: 50,
    })
      .then((f) => setFeed(f.posts))
      .catch(() => {});
  }, [platformFilter, spikeFilter]);

  const maxVelocity = Math.max(...feed.map((p) => p.velocity), 0.001);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        Loading analytics…
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-800 bg-red-950/30 p-6 text-sm text-red-300">
        <strong>Error:</strong> {error}
        <p className="mt-2 text-red-400">Make sure the pipeline has been run at least once (Pipeline → Analysis Only).</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-slate-100">Analytics</h1>
        <p className="mt-1 text-sm text-slate-400">
          {summary?.total_posts.toLocaleString()} posts ·{" "}
          {summary?.date_range.from?.slice(0, 10)} → {summary?.date_range.to?.slice(0, 10)}
        </p>
      </div>

      {/* ── Alerts ── */}
      {alerts.length > 0 && (
        <div className="rounded-xl border border-amber-700 bg-amber-950/20 p-4 space-y-3">
          <h2 className="text-sm font-semibold text-amber-400 uppercase tracking-wider">
            ⚡ Breaking Now — {alerts.length} post{alerts.length !== 1 ? "s" : ""} with high velocity &lt; 12h old
          </h2>
          {alerts.map((a, i) => (
            <div key={i} className="flex items-start justify-between gap-4 text-sm">
              <div className="flex-1 min-w-0">
                <div className="text-slate-200 truncate font-medium">{a.title || "(no title)"}</div>
                <div className="flex items-center gap-2 mt-1">
                  <PlatformBadge platform={a.platform} />
                  <SpikeBadge type={a.spike_type} />
                  <span className="text-xs text-slate-500">{a.age_hours.toFixed(1)}h old</span>
                </div>
              </div>
              <div className="shrink-0 text-right">
                <div className="text-amber-400 font-bold tabular-nums">v={a.velocity.toFixed(3)}</div>
                {a.url && (
                  <a href={a.url} target="_blank" rel="noreferrer"
                     className="text-xs text-slate-500 hover:text-violet-400">↗ open</a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Stats row ── */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {summary?.platform_breakdown.map((p) => (
          <StatCard
            key={p.platform}
            label={p.platform.toUpperCase()}
            value={p.count.toLocaleString()}
            sub={`median ${p.median_engagement.toLocaleString()} eng`}
          />
        ))}
      </div>

      {/* ── Spike type breakdown ── */}
      {summary && (
        <div>
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
            Spike Type Breakdown
          </h2>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-5">
            {summary.spike_breakdown.map((s) => (
              <div key={s.spike_type}
                   className="rounded-lg border border-slate-700 bg-slate-800/50 p-3 cursor-pointer hover:border-violet-600 transition-colors"
                   onClick={() => setSpikeFilter(spikeFilter === s.spike_type ? "all" : s.spike_type)}>
                <div className="flex items-center justify-between mb-2">
                  <SpikeBadge type={s.spike_type} />
                  <span className="text-sm font-bold text-slate-200">{s.pct}%</span>
                </div>
                <div className="text-xs text-slate-400">{s.count} posts</div>
                <div className="text-xs text-slate-500 mt-1">
                  median {s.median_engagement.toLocaleString()}
                </div>
                <div className="text-xs text-slate-500">
                  avg {(s.mean_engagement / 1000).toFixed(0)}K
                </div>
              </div>
            ))}
          </div>
          {spikeFilter !== "all" && (
            <button onClick={() => setSpikeFilter("all")}
                    className="mt-2 text-xs text-violet-400 hover:text-violet-300">
              ✕ clear filter
            </button>
          )}
        </div>
      )}

      {/* ── Weekly trend ── */}
      {summary?.weekly_trend && summary.weekly_trend.weeks.length > 1 && (
        <div>
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
            Weekly Volume by Platform
          </h2>
          <div className="rounded-xl border border-slate-700 bg-slate-800/40 p-4 overflow-x-auto">
            <WeeklyChart trend={summary.weekly_trend} />
          </div>
        </div>
      )}

      {/* ── Top creators ── */}
      {summary && summary.top_creators.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
            Top Amplifiers
          </h2>
          <div className="space-y-1">
            {summary.top_creators.map((c, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800/40 px-4 py-2.5">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xs text-slate-500 w-5 tabular-nums">{i + 1}</span>
                  <span className="text-sm text-slate-200 font-medium truncate">{c.author}</span>
                  <PlatformBadge platform={c.platform} />
                </div>
                <div className="flex items-center gap-4 shrink-0">
                  <span className="text-xs text-slate-500">{c.posts} posts</span>
                  <span className="text-sm font-bold text-violet-300 tabular-nums">
                    {c.total_engagement >= 1_000_000
                      ? `${(c.total_engagement / 1_000_000).toFixed(1)}M`
                      : c.total_engagement >= 1000
                      ? `${(c.total_engagement / 1000).toFixed(0)}K`
                      : c.total_engagement.toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Velocity feed ── */}
      <div>
        <div className="flex flex-wrap items-center gap-3 mb-3">
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
            Velocity Feed
          </h2>
          <div className="flex gap-2 ml-auto flex-wrap">
            {["all", "hn", "reddit", "youtube", "x"].map((p) => (
              <button key={p}
                      onClick={() => setPlatformFilter(p)}
                      className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
                        platformFilter === p
                          ? "bg-violet-600 text-white"
                          : "border border-slate-600 text-slate-400 hover:border-slate-400"
                      }`}>
                {p === "all" ? "All" : p.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1">
          {feed.length === 0 && (
            <p className="text-sm text-slate-500">No posts match the current filter.</p>
          )}
          {feed.map((post, i) => (
            <div key={post.post_id || i}
                 className="flex items-start gap-3 rounded-lg border border-slate-700 bg-slate-800/40 px-4 py-3 hover:border-slate-600 transition-colors">
              <span className="text-xs text-slate-600 w-5 tabular-nums shrink-0 mt-0.5">{i + 1}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    {post.url ? (
                      <a href={post.url} target="_blank" rel="noreferrer"
                         className="text-sm text-slate-200 hover:text-violet-300 transition-colors line-clamp-2 font-medium">
                        {post.title || "(no title)"}
                      </a>
                    ) : (
                      <span className="text-sm text-slate-200 line-clamp-2 font-medium">
                        {post.title || "(no title)"}
                      </span>
                    )}
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      <PlatformBadge platform={post.platform} />
                      <SpikeBadge type={post.spike_type} />
                      {post.author && (
                        <span className="text-xs text-slate-500 truncate max-w-[140px]">
                          {post.author}
                        </span>
                      )}
                      {post.age_hours > 0 && (
                        <span className="text-xs text-slate-600">
                          {post.age_hours < 24
                            ? `${post.age_hours.toFixed(0)}h ago`
                            : `${(post.age_hours / 24).toFixed(0)}d ago`}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="shrink-0 text-right space-y-1">
                    <VelocityBar value={post.velocity} max={maxVelocity} />
                    <div className="text-xs text-slate-500 tabular-nums">
                      {post.engagement_score >= 1_000_000
                        ? `${(post.engagement_score / 1_000_000).toFixed(1)}M`
                        : post.engagement_score >= 1000
                        ? `${(post.engagement_score / 1000).toFixed(0)}K`
                        : post.engagement_score.toLocaleString()}{" "}
                      eng
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Simple inline bar chart for weekly trend ──────────────────────────────────
function WeeklyChart({ trend }: { trend: { weeks: string[]; series: Record<string, number[]> } }) {
  const COLORS: Record<string, string> = {
    hn: "#f97316", reddit: "#ef4444", youtube: "#dc2626", x: "#38bdf8",
  };

  const maxVal = Math.max(
    ...Object.values(trend.series).flatMap((arr) => arr),
    1
  );

  const recentWeeks = trend.weeks.slice(-12);
  const recentSeries = Object.fromEntries(
    Object.entries(trend.series).map(([p, vals]) => [p, vals.slice(-12)])
  );

  return (
    <div className="space-y-3">
      {/* Stacked bars */}
      <div className="flex items-end gap-1 h-24">
        {recentWeeks.map((week, wi) => {
          const total = Object.values(recentSeries).reduce((s, arr) => s + (arr[wi] ?? 0), 0);
          const pct = (total / maxVal) * 100;
          return (
            <div key={week} className="flex-1 flex flex-col justify-end group relative" title={week}>
              <div className="w-full rounded-sm overflow-hidden" style={{ height: `${Math.max(pct, 2)}%` }}>
                {Object.entries(recentSeries).map(([p, arr]) => {
                  const segPct = total > 0 ? ((arr[wi] ?? 0) / total) * 100 : 0;
                  return segPct > 0 ? (
                    <div key={p} style={{ height: `${segPct}%`, backgroundColor: COLORS[p] ?? "#6366f1", opacity: 0.8 }} />
                  ) : null;
                })}
              </div>
              {/* tooltip */}
              <div className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 hidden group-hover:block z-10 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200 whitespace-nowrap shadow-lg">
                {week.slice(0, 10)}: {total} posts
              </div>
            </div>
          );
        })}
      </div>
      {/* X axis labels */}
      <div className="flex gap-1 text-xs text-slate-600">
        {recentWeeks.map((w, i) => (
          <div key={w} className="flex-1 text-center truncate">
            {i === 0 || i === recentWeeks.length - 1 ? w.slice(5, 10) : ""}
          </div>
        ))}
      </div>
      {/* Legend */}
      <div className="flex gap-4">
        {Object.entries(COLORS).map(([p, c]) => (
          <div key={p} className="flex items-center gap-1.5">
            <div className="h-2 w-3 rounded-sm" style={{ backgroundColor: c }} />
            <span className="text-xs text-slate-400">{p.toUpperCase()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
