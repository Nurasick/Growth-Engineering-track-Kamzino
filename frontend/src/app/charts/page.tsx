"use client";

import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from "recharts";
import { getYoutubeEngagement, getRedditEngagement } from "@/lib/api";
import type {
  YoutubeEngagementResponse,
  YoutubeEngagementPoint,
  RedditEngagementResponse,
  RedditEngagementPoint,
} from "@/lib/api";

// ── helpers ───────────────────────────────────────────────────────────────────

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-4">
      <div className="text-xs text-slate-400 mb-1">{label}</div>
      <div className="text-2xl font-bold text-violet-300">{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

const fmtNumber = (n: number) =>
  n >= 1_000_000
    ? (n / 1_000_000).toFixed(1) + "M"
    : n >= 1_000
    ? (n / 1_000).toFixed(1) + "K"
    : String(n);

function SectionSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-6 w-48 rounded bg-slate-800 animate-pulse" />
      <div className="h-80 w-full rounded-xl bg-slate-800 animate-pulse" />
    </div>
  );
}

// ── YouTube tooltip ───────────────────────────────────────────────────────────

function YoutubeTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const d: YoutubeEngagementPoint = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-600 bg-slate-900/95 p-4 text-xs shadow-2xl max-w-xs">
      <div className="text-slate-200 font-semibold text-sm mb-3">{label}</div>
      <div className="mb-3 space-y-1">
        <div className="text-slate-500 uppercase tracking-wider text-[10px] mb-1">YouTube</div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-400">Avg engagement rate</span>
          <span className="text-violet-300 font-medium">{d.avg_engagement_rate.toFixed(3)}%</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-400">Median rate</span>
          <span className="text-cyan-400">{d.median_engagement_rate.toFixed(3)}%</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-400">Videos published</span>
          <span className="text-slate-300">{d.video_count}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-400">Total views</span>
          <span className="text-blue-400">{fmtNumber(d.total_views)}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-400">Likes · Comments</span>
          <span className="text-slate-400">{fmtNumber(d.total_likes)} · {fmtNumber(d.total_comments)}</span>
        </div>
      </div>
      <HnSection count={d.hn_item_count} total={d.hn_total_score} stories={d.hn_top_stories} />
    </div>
  );
}

// ── Reddit tooltip ────────────────────────────────────────────────────────────

function RedditTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const d: RedditEngagementPoint = payload[0].payload;
  return (
    <div className="rounded-lg border border-slate-600 bg-slate-900/95 p-4 text-xs shadow-2xl max-w-xs">
      <div className="text-slate-200 font-semibold text-sm mb-3">{label}</div>
      <div className="mb-3 space-y-1">
        <div className="text-slate-500 uppercase tracking-wider text-[10px] mb-1">Reddit</div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-400">Avg upvote score</span>
          <span className="text-orange-300 font-medium">{fmtNumber(d.avg_score)}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-400">Median score</span>
          <span className="text-amber-400">{fmtNumber(d.median_score)}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-400">Posts</span>
          <span className="text-slate-300">{d.post_count}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-400">Avg comments / post</span>
          <span className="text-slate-400">{d.avg_comments.toFixed(0)}</span>
        </div>
        {d.top_posts[0] && (
          <div className="pt-1 border-t border-slate-700 mt-1">
            <div className="text-slate-500 text-[10px] mb-0.5">Top post</div>
            <div className="text-slate-300 leading-tight">{d.top_posts[0].title}</div>
            <div className="text-orange-400 mt-0.5">{fmtNumber(d.top_posts[0].score)}▲</div>
          </div>
        )}
      </div>
      <HnSection count={d.hn_item_count} total={d.hn_total_score} stories={d.hn_top_stories} />
    </div>
  );
}

// ── shared HN tooltip section ─────────────────────────────────────────────────

function HnSection({ count, total, stories }: { count: number; total: number; stories: any[] }) {
  if (count === 0) {
    return <div className="border-t border-slate-700 pt-2 text-slate-600 text-[10px]">No HN stories</div>;
  }
  return (
    <div className="border-t border-slate-700 pt-3 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-orange-400 uppercase tracking-wider text-[10px] font-semibold">
          HackerNews · {count} stories
        </span>
        <span className="text-orange-300 text-[10px]">{fmtNumber(total)} pts</span>
      </div>
      {stories.map((s, i) => (
        <div key={i} className="flex gap-2 items-start">
          <span className="text-orange-500 font-bold shrink-0 w-8">{s.points}▲</span>
          <span className="text-slate-300 leading-tight">{s.title}</span>
        </div>
      ))}
    </div>
  );
}

// ── shared HN stories panel ───────────────────────────────────────────────────

function HnStoriesPanel({ data }: { data: Array<{ period: string; hn_item_count: number; hn_total_score: number; hn_top_stories: any[] }> }) {
  const withHn = [...data].reverse().filter(r => r.hn_item_count > 0);
  if (withHn.length === 0) return null;
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/60 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-700 flex items-center gap-2">
        <span className="text-orange-400 font-bold text-sm">Y</span>
        <h3 className="text-sm font-medium text-slate-300">Top HackerNews Stories by Period</h3>
        <span className="text-xs text-slate-500 ml-auto">stories mentioning Claude / Anthropic</span>
      </div>
      <div className="divide-y divide-slate-800">
        {withHn.map((row) => (
          <div key={row.period} className="px-6 py-4">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-xs font-medium text-slate-300 w-24 shrink-0">{row.period}</span>
              <span className="text-xs text-orange-400 ml-auto">
                {row.hn_item_count} stories · {fmtNumber(row.hn_total_score)} pts
              </span>
            </div>
            <div className="space-y-1.5">
              {row.hn_top_stories.map((s: any, i: number) => (
                <div key={i} className="flex gap-3 items-start text-xs">
                  <span className="text-orange-500 font-bold w-12 shrink-0 tabular-nums">{s.points}▲</span>
                  {s.url ? (
                    <a href={s.url} target="_blank" rel="noopener noreferrer"
                      className="text-slate-300 hover:text-violet-300 transition-colors leading-tight">
                      {s.title}
                    </a>
                  ) : (
                    <span className="text-slate-300 leading-tight">{s.title}</span>
                  )}
                  {s.comments > 0 && <span className="text-slate-600 shrink-0">{s.comments}c</span>}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── YouTube section ───────────────────────────────────────────────────────────

function YoutubeSection({ data }: { data: YoutubeEngagementResponse }) {
  const { summary, data: chartData } = data;
  const avgRate = summary.overall_avg_engagement_rate;

  return (
    <div className="space-y-6">
      {/* formula */}
      <div className="rounded-xl border border-violet-800/50 bg-violet-900/10 p-4">
        <div className="text-xs font-semibold text-violet-400 uppercase tracking-wider mb-2">
          How YouTube engagement rate is calculated
        </div>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm font-mono">
          <span className="text-slate-200">Engagement Rate</span>
          <span className="text-slate-500">=</span>
          <span className="text-violet-300">(Likes + Comments)</span>
          <span className="text-slate-500">÷</span>
          <span className="text-blue-300">Views</span>
          <span className="text-slate-500">×</span>
          <span className="text-slate-200">100</span>
        </div>
        <p className="mt-2 text-xs text-slate-400 leading-relaxed">
          Each video&apos;s rate is computed individually, then averaged across all videos published that day.
          Measures quality of engagement (how interactive the audience was), not raw reach.
        </p>
        <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
          <span><span className="text-violet-300 font-medium">Likes</span> — direct positive reactions</span>
          <span><span className="text-blue-300 font-medium">Comments</span> — deeper interactions</span>
          <span><span className="text-slate-300 font-medium">Views</span> — total watch events (denominator)</span>
        </div>
      </div>

      {/* stat cards */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Videos" value={fmtNumber(summary.total_videos)} />
        <StatCard label="Overall Avg Engagement" value={`${avgRate.toFixed(2)}%`} sub="(likes + comments) / views" />
        <StatCard label="Date Range" value={chartData[0]?.period ?? "—"} sub={`→ ${chartData[chartData.length - 1]?.period ?? "—"}`} />
        <StatCard label="Days Tracked" value={String(chartData.length)} sub="days of data" />
      </div>

      {/* chart */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-6">
        <h3 className="text-sm font-medium text-slate-300 mb-1">
          Engagement Rate vs HackerNews Activity · by Day
        </h3>
        <p className="text-xs text-slate-500 mb-1">
          Dashed line = overall avg ({avgRate.toFixed(2)}%). Hover for HN stories that day.
        </p>
        <div className="flex flex-wrap gap-4 mb-5 text-xs text-slate-500">
          <span><span className="inline-block w-3 h-0.5 bg-violet-400 mr-1 align-middle" />Avg engagement rate (left)</span>
          <span><span className="inline-block w-3 h-0.5 bg-cyan-500 mr-1 align-middle" style={{borderTop:'2px dashed'}} />Median rate (left)</span>
          <span><span className="inline-block w-3 h-2 bg-orange-500/50 mr-1 align-middle rounded-sm" />HN total score (right)</span>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={chartData} margin={{ top: 4, right: 56, bottom: 4, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="period" tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={{ stroke: "#475569" }} />
            <YAxis yAxisId="rate" tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} width={48} />
            <YAxis yAxisId="hn" orientation="right" tick={{ fill: "#f97316", fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={fmtNumber} width={48} />
            <Tooltip content={<YoutubeTooltip />} />
            <ReferenceLine yAxisId="rate" y={avgRate} stroke="#7c3aed" strokeDasharray="6 3"
              label={{ value: `avg ${avgRate.toFixed(2)}%`, fill: "#a78bfa", fontSize: 10, position: "insideTopRight" }} />
            <Bar yAxisId="hn" dataKey="hn_total_score" name="HN Score" fill="#f97316" fillOpacity={0.25} radius={[3, 3, 0, 0]} />
            <Line yAxisId="rate" type="monotone" dataKey="avg_engagement_rate" name="Avg Rate (%)" stroke="#8b5cf6" strokeWidth={2.5} dot={{ fill: "#8b5cf6", r: 4 }} activeDot={{ r: 6 }} />
            <Line yAxisId="rate" type="monotone" dataKey="median_engagement_rate" name="Median Rate (%)" stroke="#06b6d4" strokeWidth={1.5} strokeDasharray="4 2" dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* HN stories */}
      <HnStoriesPanel data={chartData} />

      {/* table */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700">
          <h3 className="text-sm font-medium text-slate-300">Daily Breakdown</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-700">
                {["Day", "Videos", "Avg Eng. Rate", "Median Rate", "Total Views", "HN Stories", "HN Score"].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left text-slate-400 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...chartData].reverse().map(row => (
                <tr key={row.period} className="border-b border-slate-800 hover:bg-slate-700/30 transition-colors">
                  <td className="px-4 py-2.5 text-slate-300 font-medium">{row.period}</td>
                  <td className="px-4 py-2.5 text-slate-400">{row.video_count}</td>
                  <td className="px-4 py-2.5 text-violet-300">{row.avg_engagement_rate.toFixed(3)}%</td>
                  <td className="px-4 py-2.5 text-cyan-400">{row.median_engagement_rate.toFixed(3)}%</td>
                  <td className="px-4 py-2.5 text-blue-400">{fmtNumber(row.total_views)}</td>
                  <td className="px-4 py-2.5 text-orange-400">{row.hn_item_count}</td>
                  <td className="px-4 py-2.5 text-orange-300">{fmtNumber(row.hn_total_score)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ── Reddit section ────────────────────────────────────────────────────────────

function RedditSection({ data }: { data: RedditEngagementResponse }) {
  const { summary, data: chartData } = data;
  const avgScore = summary.overall_avg_score;

  return (
    <div className="space-y-6">
      {/* formula */}
      <div className="rounded-xl border border-orange-800/40 bg-orange-900/10 p-4">
        <div className="text-xs font-semibold text-orange-400 uppercase tracking-wider mb-2">
          How Reddit engagement is measured
        </div>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm font-mono">
          <span className="text-slate-200">Avg Score</span>
          <span className="text-slate-500">=</span>
          <span className="text-orange-300">Σ Upvotes per post</span>
          <span className="text-slate-500">÷</span>
          <span className="text-slate-200">Posts that week</span>
        </div>
        <p className="mt-2 text-xs text-slate-400 leading-relaxed">
          Reddit has no view count, so the primary signal is the upvote score — how much the community
          endorsed a post. Grouped by ISO week since posts span a full year.
        </p>
        <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
          <span><span className="text-orange-300 font-medium">Score</span> — net upvotes (upvotes − downvotes)</span>
          <span><span className="text-amber-300 font-medium">Comments</span> — discussion depth per post</span>
          <span><span className="text-slate-300 font-medium">Upvote ratio</span> — % of votes that were upvotes</span>
        </div>
      </div>

      {/* stat cards */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Posts" value={fmtNumber(summary.total_posts)} />
        <StatCard label="Overall Avg Score" value={fmtNumber(avgScore)} sub="avg upvotes per post" />
        <StatCard label="Date Range" value={chartData[0]?.period ?? "—"} sub={`→ ${chartData[chartData.length - 1]?.period ?? "—"}`} />
        <StatCard label="Weeks Tracked" value={String(chartData.length)} sub="ISO weeks of data" />
      </div>

      {/* chart */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-6">
        <h3 className="text-sm font-medium text-slate-300 mb-1">
          Avg Upvote Score vs HackerNews Activity · by Week
        </h3>
        <p className="text-xs text-slate-500 mb-1">
          Dashed line = overall avg score ({fmtNumber(avgScore)}). Hover for top posts and HN stories that week.
        </p>
        <div className="flex flex-wrap gap-4 mb-5 text-xs text-slate-500">
          <span><span className="inline-block w-3 h-0.5 bg-orange-400 mr-1 align-middle" />Avg score (left)</span>
          <span><span className="inline-block w-3 h-0.5 bg-amber-500 mr-1 align-middle" />Median score (left)</span>
          <span><span className="inline-block w-3 h-2 bg-orange-500/50 mr-1 align-middle rounded-sm" />HN total score (right)</span>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={chartData} margin={{ top: 4, right: 56, bottom: 16, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="period"
              tick={{ fill: "#94a3b8", fontSize: 10, textAnchor: "end" }}
              tickLine={false}
              axisLine={{ stroke: "#475569" }}
              interval={3}
              angle={-40}
              height={48}
              tickFormatter={(v: string) => {
                // "2025-W14" → "W14 '25"
                const m = v.match(/^(\d{4})-W(\d+)$/);
                return m ? `W${m[2]} '${m[1].slice(2)}` : v;
              }}
            />
            <YAxis yAxisId="score" tick={{ fill: "#94a3b8", fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={fmtNumber} width={52} />
            <YAxis yAxisId="hn" orientation="right" tick={{ fill: "#f97316", fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={fmtNumber} width={48} />
            <Tooltip content={<RedditTooltip />} />
            <ReferenceLine yAxisId="score" y={avgScore} stroke="#f97316" strokeDasharray="6 3"
              label={{ value: `avg ${fmtNumber(avgScore)}`, fill: "#fb923c", fontSize: 10, position: "insideTopRight" }} />
            <Bar yAxisId="hn" dataKey="hn_total_score" name="HN Score" fill="#f97316" fillOpacity={0.25} radius={[3, 3, 0, 0]} />
            <Line yAxisId="score" type="monotone" dataKey="avg_score" name="Avg Score" stroke="#f97316" strokeWidth={2.5} dot={{ fill: "#f97316", r: 4 }} activeDot={{ r: 6 }} />
            <Line yAxisId="score" type="monotone" dataKey="median_score" name="Median Score" stroke="#f59e0b" strokeWidth={1.5} strokeDasharray="4 2" dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* HN stories */}
      <HnStoriesPanel data={chartData} />

      {/* top posts per week */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700 flex items-center gap-2">
          <span className="text-orange-500 font-bold text-sm">↑</span>
          <h3 className="text-sm font-medium text-slate-300">Top Reddit Posts by Week</h3>
        </div>
        <div className="divide-y divide-slate-800">
          {[...chartData].reverse().filter(r => r.top_posts.length > 0).map(row => (
            <div key={row.period} className="px-6 py-4">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-xs font-medium text-slate-300 w-24 shrink-0">{row.period}</span>
                <span className="text-xs text-orange-300">{fmtNumber(row.avg_score)} avg score</span>
                <span className="text-xs text-slate-500 ml-auto">{row.post_count} posts</span>
              </div>
              <div className="space-y-1.5">
                {row.top_posts.map((p, i) => (
                  <div key={i} className="flex gap-3 items-start text-xs">
                    <span className="text-orange-500 font-bold w-14 shrink-0 tabular-nums">{fmtNumber(p.score)}▲</span>
                    {p.url ? (
                      <a href={p.url} target="_blank" rel="noopener noreferrer"
                        className="text-slate-300 hover:text-orange-300 transition-colors leading-tight">
                        {p.title}
                      </a>
                    ) : (
                      <span className="text-slate-300 leading-tight">{p.title}</span>
                    )}
                    <span className="text-slate-600 shrink-0">{p.comments}c</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* table */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700">
          <h3 className="text-sm font-medium text-slate-300">Weekly Breakdown</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-700">
                {["Week", "Posts", "Avg Score", "Median Score", "Avg Comments", "HN Stories", "HN Score"].map(h => (
                  <th key={h} className="px-4 py-2.5 text-left text-slate-400 font-medium whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...chartData].reverse().map(row => (
                <tr key={row.period} className="border-b border-slate-800 hover:bg-slate-700/30 transition-colors">
                  <td className="px-4 py-2.5 text-slate-300 font-medium">{row.period}</td>
                  <td className="px-4 py-2.5 text-slate-400">{row.post_count}</td>
                  <td className="px-4 py-2.5 text-orange-300">{fmtNumber(row.avg_score)}</td>
                  <td className="px-4 py-2.5 text-amber-400">{fmtNumber(row.median_score)}</td>
                  <td className="px-4 py-2.5 text-slate-400">{row.avg_comments.toFixed(0)}</td>
                  <td className="px-4 py-2.5 text-orange-400">{row.hn_item_count}</td>
                  <td className="px-4 py-2.5 text-orange-300">{fmtNumber(row.hn_total_score)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ── page ──────────────────────────────────────────────────────────────────────

export default function ChartsPage() {
  const [ytData, setYtData] = useState<YoutubeEngagementResponse | null>(null);
  const [rdData, setRdData] = useState<RedditEngagementResponse | null>(null);
  const [ytError, setYtError] = useState<string | null>(null);
  const [rdError, setRdError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"youtube" | "reddit">("youtube");

  useEffect(() => {
    getYoutubeEngagement().then(setYtData).catch(e => setYtError(e.message ?? "Failed"));
    getRedditEngagement().then(setRdData).catch(e => setRdError(e.message ?? "Failed"));
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-slate-100">Engagement Analytics</h1>
        <p className="mt-1 text-sm text-slate-400">
          YouTube &amp; Reddit engagement over time, correlated with HackerNews activity
        </p>
      </div>

      {/* Tab switcher */}
      <div className="flex gap-1 rounded-lg border border-slate-700 bg-slate-800/60 p-1 w-fit">
        {(["youtube", "reddit"] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-md px-5 py-1.5 text-sm font-medium transition-colors capitalize ${
              activeTab === tab
                ? "bg-violet-600 text-white"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab === "youtube" ? "YouTube" : "Reddit"}
          </button>
        ))}
      </div>

      {/* YouTube tab */}
      {activeTab === "youtube" && (
        ytError
          ? <div className="rounded-xl border border-red-800 bg-red-900/20 p-6 text-red-400 text-sm">{ytError}</div>
          : ytData
          ? <YoutubeSection data={ytData} />
          : <SectionSkeleton />
      )}

      {/* Reddit tab */}
      {activeTab === "reddit" && (
        rdError
          ? <div className="rounded-xl border border-red-800 bg-red-900/20 p-6 text-red-400 text-sm">{rdError}</div>
          : rdData
          ? <RedditSection data={rdData} />
          : <SectionSkeleton />
      )}
    </div>
  );
}
