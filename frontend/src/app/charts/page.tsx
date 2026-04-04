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
import { getYoutubeEngagement } from "@/lib/api";
import type { YoutubeEngagementResponse, YoutubeEngagementPoint } from "@/lib/api";

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

function EnrichedTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const d: YoutubeEngagementPoint = payload[0].payload;

  return (
    <div className="rounded-lg border border-slate-600 bg-slate-900/95 p-4 text-xs shadow-2xl max-w-xs">
      <div className="text-slate-200 font-semibold text-sm mb-3">{label}</div>

      {/* YouTube metrics */}
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

      {/* HN section */}
      {d.hn_item_count > 0 && (
        <div className="border-t border-slate-700 pt-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-orange-400 uppercase tracking-wider text-[10px] font-semibold">
              HackerNews · {d.hn_item_count} stories
            </span>
            <span className="text-orange-300 text-[10px]">{fmtNumber(d.hn_total_score)} pts total</span>
          </div>
          {d.hn_top_stories.map((s, i) => (
            <div key={i} className="flex gap-2 items-start">
              <span className="text-orange-500 font-bold shrink-0 w-8">{s.points}▲</span>
              <span className="text-slate-300 leading-tight">{s.title}</span>
            </div>
          ))}
        </div>
      )}
      {d.hn_item_count === 0 && (
        <div className="border-t border-slate-700 pt-2 text-slate-600 text-[10px]">
          No HN stories on this day
        </div>
      )}
    </div>
  );
}

export default function ChartsPage() {
  const [data, setData] = useState<YoutubeEngagementResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getYoutubeEngagement()
      .then(setData)
      .catch((e) => setError(e.message ?? "Failed to load data"));
  }, []);

  if (error) {
    return (
      <div className="rounded-xl border border-red-800 bg-red-900/20 p-6 text-red-400 text-sm">
        {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-8">
        <div>
          <div className="h-7 w-48 rounded bg-slate-800 animate-pulse mb-2" />
          <div className="h-4 w-72 rounded bg-slate-800 animate-pulse" />
        </div>
        <div className="h-80 w-full rounded-xl bg-slate-800 animate-pulse" />
      </div>
    );
  }

  const { summary } = data;
  const chartData = data.data;
  const avgRate = summary.overall_avg_engagement_rate;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-slate-100">YouTube Analytics</h1>
        <p className="mt-1 text-sm text-slate-400">
          Engagement rate over time · {summary.date_range} · {summary.source_file}
        </p>
      </div>

      {/* Formula callout */}
      <div className="rounded-xl border border-violet-800/50 bg-violet-900/10 p-4">
        <div className="text-xs font-semibold text-violet-400 uppercase tracking-wider mb-2">
          How engagement rate is calculated
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
          Each video&apos;s rate is computed individually from raw YouTube counts, then averaged across all
          videos published on that day. A higher rate means the audience that watched a video was more
          likely to interact with it — it measures quality of engagement, not raw reach.
        </p>
        <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">
          <span><span className="text-violet-300 font-medium">Likes</span> — direct positive reactions from viewers</span>
          <span><span className="text-blue-300 font-medium">Comments</span> — deeper interactions requiring effort</span>
          <span><span className="text-slate-300 font-medium">Views</span> — total watch events (denominator / reach)</span>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Videos" value={fmtNumber(summary.total_videos)} />
        <StatCard
          label="Overall Avg Engagement"
          value={`${summary.overall_avg_engagement_rate.toFixed(2)}%`}
          sub="(likes + comments) / views"
        />
        <StatCard
          label="Date Range"
          value={data.data[0]?.period ?? "—"}
          sub={`→ ${data.data[data.data.length - 1]?.period ?? "—"}`}
        />
        <StatCard
          label="Days Tracked"
          value={String(chartData.length)}
          sub="days of data"
        />
      </div>

      {/* Main combined chart */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-6">
        <h2 className="text-sm font-medium text-slate-300 mb-1">
          YouTube Engagement Rate vs HackerNews Activity
        </h2>
        <p className="text-xs text-slate-500 mb-1">
          Dashed reference line = overall avg engagement ({avgRate.toFixed(2)}%).
          Hover a day to see the top HN stories that may have driven interest.
        </p>
        <div className="flex flex-wrap gap-4 mb-5 text-xs text-slate-500">
          <span><span className="inline-block w-3 h-0.5 bg-violet-400 mr-1 align-middle" />Avg engagement rate (left axis)</span>
          <span><span className="inline-block w-3 h-0.5 bg-cyan-500 mr-1 align-middle border-dashed" />Median rate (left axis)</span>
          <span><span className="inline-block w-3 h-2 bg-orange-500/50 mr-1 align-middle rounded-sm" />HN total score (right axis)</span>
        </div>
        <ResponsiveContainer width="100%" height={340}>
          <ComposedChart data={chartData} margin={{ top: 4, right: 56, bottom: 4, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="period"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#475569" }}
            />
            {/* Left axis: engagement rate */}
            <YAxis
              yAxisId="rate"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `${v}%`}
              width={48}
            />
            {/* Right axis: HN score */}
            <YAxis
              yAxisId="hn"
              orientation="right"
              tick={{ fill: "#f97316", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={fmtNumber}
              width={48}
            />
            <Tooltip content={<EnrichedTooltip />} />
            <ReferenceLine
              yAxisId="rate"
              y={avgRate}
              stroke="#7c3aed"
              strokeDasharray="6 3"
              label={{
                value: `avg ${avgRate.toFixed(2)}%`,
                fill: "#a78bfa",
                fontSize: 10,
                position: "insideTopRight",
              }}
            />
            {/* HN score bars behind the lines */}
            <Bar
              yAxisId="hn"
              dataKey="hn_total_score"
              name="HN Total Score"
              fill="#f97316"
              fillOpacity={0.25}
              radius={[3, 3, 0, 0]}
            />
            <Line
              yAxisId="rate"
              type="monotone"
              dataKey="avg_engagement_rate"
              name="Avg Engagement Rate (%)"
              stroke="#8b5cf6"
              strokeWidth={2.5}
              dot={{ fill: "#8b5cf6", r: 4, strokeWidth: 0 }}
              activeDot={{ r: 6 }}
            />
            <Line
              yAxisId="rate"
              type="monotone"
              dataKey="median_engagement_rate"
              name="Median Engagement Rate (%)"
              stroke="#06b6d4"
              strokeWidth={1.5}
              strokeDasharray="4 2"
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* HN stories per day */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700 flex items-center gap-2">
          <span className="text-orange-400 font-bold">Y</span>
          <h2 className="text-sm font-medium text-slate-300">Top HackerNews Stories by Day</h2>
          <span className="text-xs text-slate-500 ml-auto">stories mentioning Claude / Anthropic</span>
        </div>
        <div className="divide-y divide-slate-800">
          {[...chartData].reverse().map((row) => (
            <div key={row.period} className="px-6 py-4">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-xs font-medium text-slate-300 w-24 shrink-0">{row.period}</span>
                <span className="text-xs text-violet-300">{row.avg_engagement_rate.toFixed(3)}% eng.</span>
                {row.hn_total_score > 0 && (
                  <span className="text-xs text-orange-400 ml-auto">
                    {row.hn_item_count} stories · {fmtNumber(row.hn_total_score)} pts
                  </span>
                )}
              </div>
              {row.hn_top_stories.length > 0 ? (
                <div className="space-y-1.5 pl-0">
                  {row.hn_top_stories.map((s, i) => (
                    <div key={i} className="flex gap-3 items-start text-xs">
                      <span className="text-orange-500 font-bold w-12 shrink-0 tabular-nums">
                        {s.points}▲
                      </span>
                      {s.url ? (
                        <a
                          href={s.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-slate-300 hover:text-violet-300 transition-colors leading-tight"
                        >
                          {s.title}
                        </a>
                      ) : (
                        <span className="text-slate-300 leading-tight">{s.title}</span>
                      )}
                      {s.comments > 0 && (
                        <span className="text-slate-600 shrink-0">{s.comments}c</span>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-600 pl-0">No HN stories recorded</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Data table */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700">
          <h2 className="text-sm font-medium text-slate-300">Daily Breakdown</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-700">
                {["Day", "Videos", "Avg Eng. Rate", "Median Rate", "Total Views", "HN Stories", "HN Score"].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left text-slate-400 font-medium whitespace-nowrap">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...chartData].reverse().map((row) => (
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
