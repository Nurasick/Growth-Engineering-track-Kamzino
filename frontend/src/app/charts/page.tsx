"use client";

import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine,
} from "recharts";
import { getYoutubeEngagement } from "@/lib/api";
import type { YoutubeEngagementResponse } from "@/lib/api";

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

  // overall avg line for reference
  const avgRate = summary.overall_avg_engagement_rate;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
      <div className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-xs space-y-1 shadow-xl">
        <div className="text-slate-300 font-semibold mb-1">{label}</div>
        <div className="text-violet-300">Avg rate: {d.avg_engagement_rate.toFixed(3)}%</div>
        <div className="text-slate-400">Median rate: {d.median_engagement_rate.toFixed(3)}%</div>
        <div className="text-slate-400">Videos: {d.video_count}</div>
        <div className="text-slate-400">Views: {fmtNumber(d.total_views)}</div>
        <div className="text-slate-400">
          Likes: {fmtNumber(d.total_likes)} · Comments: {fmtNumber(d.total_comments)}
        </div>
      </div>
    );
  };

  const BarTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
      <div className="rounded-lg border border-slate-700 bg-slate-900 p-3 text-xs space-y-1 shadow-xl">
        <div className="text-slate-300 font-semibold mb-1">{label}</div>
        <div className="text-blue-300">Views: {fmtNumber(d.total_views)}</div>
        <div className="text-slate-400">Videos: {d.video_count}</div>
      </div>
    );
  };

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
        <StatCard
          label="Total Videos"
          value={fmtNumber(summary.total_videos)}
        />
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

      {/* Engagement Rate Line Chart */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-6">
        <h2 className="text-sm font-medium text-slate-300 mb-1">
          Avg Engagement Rate by Day
        </h2>
        <p className="text-xs text-slate-500 mb-5">
          Engagement rate = (likes + comments) / views × 100. Dashed line = overall average ({avgRate.toFixed(2)}%).
        </p>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData} margin={{ top: 4, right: 24, bottom: 4, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="period"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#475569" }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `${v}%`}
              width={48}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 12, color: "#94a3b8", paddingTop: 8 }}
            />
            <ReferenceLine
              y={avgRate}
              stroke="#7c3aed"
              strokeDasharray="6 3"
              label={{ value: `avg ${avgRate.toFixed(2)}%`, fill: "#a78bfa", fontSize: 10, position: "insideTopRight" }}
            />
            <Line
              type="monotone"
              dataKey="avg_engagement_rate"
              name="Avg Engagement Rate (%)"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={{ fill: "#8b5cf6", r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line
              type="monotone"
              dataKey="median_engagement_rate"
              name="Median Engagement Rate (%)"
              stroke="#06b6d4"
              strokeWidth={1.5}
              strokeDasharray="4 2"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Video Count Bar Chart */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-6">
        <h2 className="text-sm font-medium text-slate-300 mb-1">
          Video Volume &amp; Total Views by Day
        </h2>
        <p className="text-xs text-slate-500 mb-5">
          Bar = total views (left axis). Line = number of videos published (right axis).
        </p>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={chartData} margin={{ top: 4, right: 48, bottom: 4, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="period"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "#475569" }}
              interval="preserveStartEnd"
            />
            <YAxis
              yAxisId="views"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={fmtNumber}
              width={52}
            />
            <YAxis
              yAxisId="count"
              orientation="right"
              tick={{ fill: "#94a3b8", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={36}
            />
            <Tooltip content={<BarTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 12, color: "#94a3b8", paddingTop: 8 }}
            />
            <Bar
              yAxisId="views"
              dataKey="total_views"
              name="Total Views"
              fill="#3b82f6"
              fillOpacity={0.7}
              radius={[3, 3, 0, 0]}
            />
            <Line
              yAxisId="count"
              type="monotone"
              dataKey="video_count"
              name="Videos Published"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={{ fill: "#f59e0b", r: 3 }}
            />
          </BarChart>
        </ResponsiveContainer>
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
                {["Month", "Videos", "Avg Eng. Rate", "Median Eng. Rate", "Total Views", "Likes", "Comments"].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-2.5 text-left text-slate-400 font-medium whitespace-nowrap"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...chartData].reverse().map((row) => (
                <tr
                  key={row.period}
                  className="border-b border-slate-800 hover:bg-slate-700/30 transition-colors"
                >
                  <td className="px-4 py-2.5 text-slate-300 font-medium">{row.period}</td>
                  <td className="px-4 py-2.5 text-slate-400">{row.video_count}</td>
                  <td className="px-4 py-2.5 text-violet-300">{row.avg_engagement_rate.toFixed(3)}%</td>
                  <td className="px-4 py-2.5 text-cyan-400">{row.median_engagement_rate.toFixed(3)}%</td>
                  <td className="px-4 py-2.5 text-blue-400">{fmtNumber(row.total_views)}</td>
                  <td className="px-4 py-2.5 text-slate-400">{fmtNumber(row.total_likes)}</td>
                  <td className="px-4 py-2.5 text-slate-400">{fmtNumber(row.total_comments)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
