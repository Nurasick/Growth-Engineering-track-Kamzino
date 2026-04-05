"use client";

import { useEffect, useState } from "react";
import { getAnalyticsSummary, getAnalyticsFeed, getAlerts } from "@/lib/api";
import type { AnalyticsSummary, FeedPost, Alert } from "@/lib/api";

const PLATFORM_COLORS: Record<string, string> = {
  hn:      "text-orange-400 bg-orange-950/30 border-orange-900/50",
  reddit:  "text-red-400   bg-red-950/30    border-red-900/50",
  youtube: "text-rose-400  bg-rose-950/30   border-rose-900/50",
  x:       "text-sky-400   bg-sky-950/30    border-sky-900/50",
};

const SPIKE_COLORS: Record<string, string> = {
  breakthrough: "text-[#CAFF33]  bg-[#CAFF33]/5",
  tutorial:     "text-amber-400  bg-amber-950/30",
  personal:     "text-blue-400   bg-blue-950/30",
  meme:         "text-pink-400   bg-pink-950/30",
  comparison:   "text-purple-400 bg-purple-950/30",
};

function PlatformBadge({ platform }: { platform: string }) {
  const cls = PLATFORM_COLORS[platform] ?? "text-white/40 bg-white/5 border-white/10";
  return (
    <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-xs font-bold font-mono ${cls}`}>
      {platform.toUpperCase()}
    </span>
  );
}

function SpikeBadge({ type }: { type: string }) {
  const cls = SPIKE_COLORS[type] ?? "text-white/40 bg-white/5";
  return (
    <span className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs ${cls}`}>{type}</span>
  );
}

function VelocityBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="h-1 w-20 rounded-full bg-[#242424]">
        <div className="h-1 rounded-full bg-[#CAFF33]" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-white/30 tabular-nums">{value.toFixed(3)}</span>
    </div>
  );
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded border border-[#242424] bg-[#141414] p-4">
      <div className="text-xs text-white/30 mb-1 uppercase tracking-wider">{label}</div>
      <div className="text-2xl font-bold text-white">{value}</div>
      {sub && <div className="text-xs text-white/25 mt-0.5">{sub}</div>}
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
    Promise.all([getAnalyticsSummary(), getAnalyticsFeed({ limit: 50 }), getAlerts(0.05)])
      .then(([s, f, a]) => { setSummary(s); setFeed(f.posts); setAlerts(a.alerts); })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    getAnalyticsFeed({
      platform: platformFilter === "all" ? undefined : platformFilter,
      spike_type: spikeFilter === "all" ? undefined : spikeFilter,
      limit: 50,
    }).then((f) => setFeed(f.posts)).catch(() => {});
  }, [platformFilter, spikeFilter]);

  const maxVelocity = Math.max(...feed.map((p) => p.velocity), 0.001);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-white/30 text-sm">Loading analytics…</div>;
  }

  if (error) {
    return (
      <div className="rounded border border-red-900/40 bg-red-950/20 p-6 text-sm text-red-400">
        <strong>Error:</strong> {error}
        <p className="mt-2 text-red-400/60 text-xs">Make sure the pipeline has been run at least once.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Analytics</h1>
        <p className="mt-1 text-sm text-white/40">
          {summary?.total_posts.toLocaleString()} posts ·{" "}
          {summary?.date_range.from?.slice(0, 10)} → {summary?.date_range.to?.slice(0, 10)}
        </p>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="rounded border border-[#CAFF33]/30 bg-[#CAFF33]/5 p-4 space-y-3">
          <h2 className="text-xs font-bold text-[#CAFF33] uppercase tracking-widest">
            ⚡ Breaking Now — {alerts.length} post{alerts.length !== 1 ? "s" : ""} with high velocity &lt; 12h old
          </h2>
          {alerts.map((a, i) => (
            <div key={i} className="flex items-start justify-between gap-4 text-sm">
              <div className="flex-1 min-w-0">
                <div className="text-white/80 truncate font-medium">{a.title || "(no title)"}</div>
                <div className="flex items-center gap-2 mt-1">
                  <PlatformBadge platform={a.platform} />
                  <SpikeBadge type={a.spike_type} />
                  <span className="text-xs text-white/25">{a.age_hours.toFixed(1)}h old</span>
                </div>
              </div>
              <div className="shrink-0 text-right">
                <div className="text-[#CAFF33] font-bold tabular-nums text-sm">v={a.velocity.toFixed(3)}</div>
                {a.url && (
                  <a href={a.url} target="_blank" rel="noreferrer"
                     className="text-xs text-white/25 hover:text-[#CAFF33]">↗ open</a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {summary?.platform_breakdown.map((p) => (
          <StatCard
            key={p.platform}
            label={p.platform.toUpperCase()}
            value={p.count.toLocaleString()}
            sub={`median ${p.median_engagement.toLocaleString()} eng`}
          />
        ))}
      </div>

      {/* Spike breakdown */}
      {summary && (
        <div>
          <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest mb-3">Spike Type Breakdown</h2>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-5">
            {summary.spike_breakdown.map((s) => (
              <div
                key={s.spike_type}
                className={`rounded border bg-[#141414] p-3 cursor-pointer transition-colors ${
                  spikeFilter === s.spike_type ? "border-[#CAFF33]" : "border-[#242424] hover:border-[#2e2e2e]"
                }`}
                onClick={() => setSpikeFilter(spikeFilter === s.spike_type ? "all" : s.spike_type)}
              >
                <div className="flex items-center justify-between mb-2">
                  <SpikeBadge type={s.spike_type} />
                  <span className="text-sm font-bold text-white">{s.pct}%</span>
                </div>
                <div className="text-xs text-white/40">{s.count} posts</div>
                <div className="text-xs text-white/25 mt-1">median {s.median_engagement.toLocaleString()}</div>
                <div className="text-xs text-white/25">avg {(s.mean_engagement / 1000).toFixed(0)}K</div>
              </div>
            ))}
          </div>
          {spikeFilter !== "all" && (
            <button onClick={() => setSpikeFilter("all")} className="mt-2 text-xs text-[#CAFF33]/60 hover:text-[#CAFF33]">
              ✕ clear filter
            </button>
          )}
        </div>
      )}

      {/* Weekly trend */}
      {summary?.weekly_trend && summary.weekly_trend.weeks.length > 1 && (
        <div>
          <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest mb-3">Weekly Volume by Platform</h2>
          <div className="rounded border border-[#242424] bg-[#141414] p-4 overflow-x-auto">
            <WeeklyChart trend={summary.weekly_trend} />
          </div>
        </div>
      )}

      {/* Top creators */}
      {summary && summary.top_creators.length > 0 && (
        <div>
          <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest mb-3">Top Amplifiers</h2>
          <div className="space-y-1">
            {summary.top_creators.map((c, i) => (
              <div key={i} className="flex items-center justify-between rounded border border-[#242424] bg-[#141414] px-4 py-2.5">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xs text-white/20 w-5 tabular-nums">{i + 1}</span>
                  <span className="text-sm text-white/70 font-medium truncate">{c.author}</span>
                  <PlatformBadge platform={c.platform} />
                </div>
                <div className="flex items-center gap-4 shrink-0">
                  <span className="text-xs text-white/25">{c.posts} posts</span>
                  <span className="text-sm font-bold text-[#CAFF33] tabular-nums">
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

      {/* Velocity feed */}
      <div>
        <div className="flex flex-wrap items-center gap-3 mb-3">
          <h2 className="text-xs font-medium text-white/30 uppercase tracking-widest">Velocity Feed</h2>
          <div className="flex gap-1.5 ml-auto flex-wrap">
            {["all", "hn", "reddit", "youtube", "x"].map((p) => (
              <button
                key={p}
                onClick={() => setPlatformFilter(p)}
                className={`rounded px-2.5 py-1 text-xs font-medium uppercase tracking-wide transition-colors ${
                  platformFilter === p
                    ? "bg-[#CAFF33] text-black"
                    : "border border-[#333] text-white/40 hover:border-[#CAFF33] hover:text-[#CAFF33]"
                }`}
              >
                {p === "all" ? "All" : p.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-1">
          {feed.length === 0 && <p className="text-sm text-white/20">No posts match the current filter.</p>}
          {feed.map((post, i) => (
            <div
              key={post.post_id || i}
              className="flex items-start gap-3 rounded border border-[#242424] bg-[#141414] px-4 py-3 hover:border-[#2e2e2e] transition-colors"
            >
              <span className="text-xs text-white/20 w-5 tabular-nums shrink-0 mt-0.5">{i + 1}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    {/* Show tweet body for X (no title), title for everything else */}
                    {post.url ? (
                      <a href={post.url} target="_blank" rel="noreferrer"
                         className="text-sm text-white/70 hover:text-[#CAFF33] transition-colors line-clamp-2 font-medium">
                        {post.title || post.body_text || "(no content)"}
                      </a>
                    ) : (
                      <span className="text-sm text-white/70 line-clamp-2 font-medium">
                        {post.title || post.body_text || "(no content)"}
                      </span>
                    )}
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      <PlatformBadge platform={post.platform} />
                      <SpikeBadge type={post.spike_type} />
                      {post.author && <span className="text-xs text-white/25 truncate max-w-[140px]">{post.author}</span>}
                      {post.age_hours > 0 && (
                        <span className="text-xs text-white/20">
                          {post.age_hours < 24 ? `${post.age_hours.toFixed(0)}h ago` : `${(post.age_hours / 24).toFixed(0)}d ago`}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="shrink-0 text-right space-y-1">
                    <VelocityBar value={post.velocity} max={maxVelocity} />
                    <div className="text-xs text-white/25 tabular-nums">
                      {post.engagement_score >= 1_000_000
                        ? `${(post.engagement_score / 1_000_000).toFixed(1)}M`
                        : post.engagement_score >= 1000
                        ? `${(post.engagement_score / 1000).toFixed(0)}K`
                        : post.engagement_score.toLocaleString()}
                      {" "}{post.platform === "x" ? "views" : post.platform === "youtube" ? "views" : "pts"}
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

function WeeklyChart({ trend }: { trend: { weeks: string[]; series: Record<string, number[]> } }) {
  const COLORS: Record<string, string> = {
    hn: "#f97316", reddit: "#ef4444", youtube: "#dc2626", x: "#38bdf8",
  };
  const maxVal = Math.max(...Object.values(trend.series).flatMap((arr) => arr), 1);
  const recentWeeks = trend.weeks.slice(-12);
  const recentSeries = Object.fromEntries(
    Object.entries(trend.series).map(([p, vals]) => [p, vals.slice(-12)])
  );

  return (
    <div className="space-y-3">
      <div className="flex items-stretch gap-1 h-24">
        {recentWeeks.map((week, wi) => {
          const breakdown = Object.fromEntries(
            Object.entries(recentSeries).map(([platform, arr]) => [platform, arr[wi] ?? 0])
          );
          const total = Object.values(breakdown).reduce((sum, value) => sum + value, 0);
          const pct = (total / maxVal) * 100;
          return (
            <div key={week} className="flex-1 flex flex-col justify-end group relative h-full" title={week}>
              <div className="w-full rounded-sm overflow-hidden" style={{ height: `${Math.max(pct, 2)}%` }}>
                {Object.entries(recentSeries).map(([p, arr]) => {
                  const segPct = total > 0 ? ((arr[wi] ?? 0) / total) * 100 : 0;
                  return segPct > 0 ? (
                    <div key={p} style={{ height: `${segPct}%`, backgroundColor: COLORS[p] ?? "#CAFF33", opacity: 0.7 }} />
                  ) : null;
                })}
              </div>
              <div className="pointer-events-none absolute left-1/2 top-1 z-10 hidden min-w-[148px] -translate-x-1/2 rounded border border-[#222] bg-[#0d0d0d] px-2 py-1.5 text-[11px] text-white/80 shadow-lg group-hover:block">
                <div className="font-medium text-white/90">{week.slice(0, 10)}</div>
                <div className="mb-1 text-white/50">{total} posts</div>
                <div className="space-y-0.5">
                  {Object.entries(breakdown).map(([platform, count]) => (
                    <div key={platform} className="flex items-center justify-between gap-3">
                      <span style={{ color: COLORS[platform] ?? "#CAFF33" }}>{platform.toUpperCase()}</span>
                      <span className="tabular-nums text-white/70">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="flex gap-1 text-xs text-white/20">
        {recentWeeks.map((w, i) => (
          <div key={w} className="flex-1 text-center truncate">
            {i === 0 || i === recentWeeks.length - 1 ? w.slice(5, 10) : ""}
          </div>
        ))}
      </div>
      <div className="flex gap-4">
        {Object.entries(COLORS).map(([p, c]) => (
          <div key={p} className="flex items-center gap-1.5">
            <div className="h-2 w-3 rounded-sm" style={{ backgroundColor: c }} />
            <span className="text-xs text-white/40">{p.toUpperCase()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
