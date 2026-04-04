#!/usr/bin/env python3
"""
Claude Virality Timeline — generates self-contained HTML dashboard.

Reads  → data/processed/spike_classified.csv
Writes → data/processed/virality_timeline.html
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT     = Path(__file__).parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
INPUT_CSV     = PROCESSED_DIR / "spike_classified.csv"
OUTPUT_HTML   = PROCESSED_DIR / "virality_timeline.html"

KEY_EVENTS = [
    ("2025-02", "Claude Code<br>launches"),
    ("2025-09", "Sonnet 4.5<br>'thing to beat'"),
    ("2025-11", "China hacking<br>story"),
    ("2026-01", "Boris setup<br>post viral"),
    ("2026-02", "Non-English<br>creators pile in"),
    ("2026-03", "Source code<br>leak + OpenClaw"),
]

COLORS = {
    "breakthrough": "#e63946", "tutorial": "#457b9d",
    "comparison": "#f4a261",   "personal": "#2a9d8f", "meme": "#e9c46a",
}
SPIKE_LABELS = {
    "breakthrough": "Breakthrough ⚡", "tutorial": "Tutorial 📖",
    "comparison": "Comparison ⚔️",    "personal": "Personal 💬", "meme": "Meme 😂",
}
PLATFORM_SCORE_CAP = {"hn": 1000, "reddit": 10000, "youtube": 200000, "x": 50000}


def main() -> None:
    if not INPUT_CSV.exists():
        print(f"[error] {INPUT_CSV} not found — run spike_classifier.py first")
        raise SystemExit(1)

    with INPUT_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Build monthly aggregates
    week_data   = defaultdict(lambda: defaultdict(float))
    week_counts = defaultdict(int)

    for r in rows:
        ca = r.get("created_at", "")
        try:
            dt = datetime.fromisoformat(ca.replace("Z", "+00:00"))
        except Exception:
            continue
        if dt.year < 2025:
            continue

        ym    = dt.strftime("%Y-%m")
        spike = r.get("spike_type", "breakthrough")
        eng   = float(r.get("engagement_score") or 0)
        plat  = r.get("platform", "")
        cap   = PLATFORM_SCORE_CAP.get(plat, 1000)
        norm  = min(eng / cap * 100, 100)

        week_data[ym][spike] += norm
        week_counts[ym] += 1

    months      = sorted(week_data.keys())
    spike_types = ["breakthrough", "tutorial", "comparison", "personal", "meme"]
    datasets    = [{
        "label": SPIKE_LABELS[st],
        "data":  [round(week_data[m].get(st, 0), 1) for m in months],
        "backgroundColor": COLORS[st], "borderColor": COLORS[st],
        "borderWidth": 1, "stack": "stack0",
    } for st in spike_types]

    annotations = {}
    for i, (month, label) in enumerate(KEY_EVENTS):
        if month in months:
            idx = months.index(month)
            annotations[f"event{i}"] = {
                "type": "line", "xMin": idx, "xMax": idx,
                "borderColor": "rgba(0,0,0,0.5)", "borderWidth": 1.5, "borderDash": [4, 4],
                "label": {"display": True, "content": label, "position": "start",
                           "backgroundColor": "rgba(0,0,0,0.75)", "color": "#fff",
                           "font": {"size": 10}, "padding": 4},
            }

    chart_config = {
        "type": "bar",
        "data": {"labels": months, "datasets": datasets},
        "options": {
            "responsive": True, "maintainAspectRatio": False,
            "plugins": {
                "legend": {"position": "top"},
                "title": {"display": True,
                           "text": "Claude Virality Timeline — Engagement by Spike Type",
                           "font": {"size": 16, "weight": "bold"}, "padding": {"bottom": 20}},
                "annotation": {"annotations": annotations},
                "tooltip": {"mode": "index", "intersect": False},
            },
            "scales": {
                "x": {"stacked": True, "title": {"display": True, "text": "Month"},
                       "ticks": {"maxRotation": 45}},
                "y": {"stacked": True, "beginAtZero": True,
                       "title": {"display": True, "text": "Normalized Engagement (cross-platform)"}},
            },
            "interaction": {"mode": "index", "intersect": False},
        },
    }

    # Top posts table
    top_posts = []
    for r in rows:
        ca = r.get("created_at", "")
        try:
            dt = datetime.fromisoformat(ca.replace("Z", "+00:00"))
        except Exception:
            continue
        if dt.year < 2025:
            continue
        eng = float(r.get("engagement_score") or 0)
        if eng < 500:
            continue
        top_posts.append({
            "date": dt.strftime("%Y-%m-%d"), "platform": r.get("platform", ""),
            "spike": r.get("spike_type", ""), "title": r.get("title", "")[:90], "score": int(eng),
        })

    top_posts.sort(key=lambda x: x["score"], reverse=True)
    table_rows = ""
    for p in top_posts[:20]:
        emoji = {"breakthrough": "⚡", "tutorial": "📖", "comparison": "⚔️",
                 "personal": "💬", "meme": "😂"}.get(p["spike"], "•")
        color = COLORS.get(p["spike"], "#888")
        table_rows += f"""
        <tr>
          <td>{p['date']}</td>
          <td><span class="plat plat-{p['platform']}">{p['platform'].upper()}</span></td>
          <td><span style="color:{color}">{emoji} {p['spike']}</span></td>
          <td>{p['title']}</td>
          <td style="text-align:right;font-weight:bold">{p['score']:,}</td>
        </tr>"""

    # Stats
    total       = len(rows)
    type_counts = defaultdict(int)
    for r in rows:
        type_counts[r.get("spike_type", "breakthrough")] += 1

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Virality Intelligence — HackNU 2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; padding: 24px; }}
  h1 {{ font-size: 1.6rem; font-weight: 700; margin-bottom: 4px; color: #fff; }}
  .subtitle {{ color: #888; font-size: 0.9rem; margin-bottom: 24px; }}
  .card {{ background: #1a1d27; border-radius: 12px; padding: 24px; margin-bottom: 24px; border: 1px solid #2a2d3a; }}
  .chart-wrap {{ height: 420px; position: relative; }}
  .stats-row {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 24px; }}
  .stat {{ background: #1a1d27; border-radius: 8px; padding: 16px; border: 1px solid #2a2d3a; text-align: center; }}
  .stat-emoji {{ font-size: 1.5rem; }}
  .stat-label {{ font-size: 0.75rem; color: #888; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .stat-val {{ font-size: 1.4rem; font-weight: 700; color: #fff; margin-top: 2px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th {{ text-align: left; padding: 10px 12px; border-bottom: 2px solid #2a2d3a; color: #888; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #1f2232; vertical-align: middle; }}
  tr:hover td {{ background: #1f2232; }}
  .plat {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }}
  .plat-hn {{ background: #ff6600; color: #fff; }}
  .plat-reddit {{ background: #ff4500; color: #fff; }}
  .plat-youtube {{ background: #ff0000; color: #fff; }}
  .plat-x {{ background: #1d9bf0; color: #fff; }}
  .pipeline {{ display: flex; align-items: center; gap: 0; margin: 12px 0; flex-wrap: wrap; }}
  .pipe-step {{ background: #252836; border: 1px solid #3a3d4a; border-radius: 8px; padding: 12px 16px; font-size: 0.85rem; }}
  .pipe-step .name {{ font-weight: 700; color: #fff; }}
  .pipe-step .desc {{ color: #888; font-size: 0.75rem; margin-top: 2px; }}
  .pipe-arrow {{ color: #3a3d4a; font-size: 1.2rem; padding: 0 8px; }}
  .alert-box {{ background: #2d1b1b; border: 1px solid #e63946; border-radius: 8px; padding: 16px; margin-top: 12px; }}
  .alert-title {{ color: #e63946; font-weight: 700; margin-bottom: 8px; }}
  h2 {{ font-size: 1.1rem; font-weight: 700; color: #fff; margin-bottom: 16px; }}
</style>
</head>
<body>
<h1>Claude Virality Intelligence Dashboard</h1>
<p class="subtitle">HackNU 2026 · Growth Engineering Track · {total} posts · 4 platforms · auto-generated</p>

<div class="stats-row">
  <div class="stat"><div class="stat-emoji">⚡</div><div class="stat-label">Breakthrough</div><div class="stat-val">{type_counts['breakthrough']*100//total if total else 0}%</div></div>
  <div class="stat"><div class="stat-emoji">📖</div><div class="stat-label">Tutorial</div><div class="stat-val">{type_counts['tutorial']*100//total if total else 0}%</div></div>
  <div class="stat"><div class="stat-emoji">⚔️</div><div class="stat-label">Comparison</div><div class="stat-val">{type_counts['comparison']*100//total if total else 0}%</div></div>
  <div class="stat"><div class="stat-emoji">💬</div><div class="stat-label">Personal</div><div class="stat-val">{type_counts['personal']*100//total if total else 0}%</div></div>
  <div class="stat"><div class="stat-emoji">😂</div><div class="stat-label">Meme</div><div class="stat-val">{type_counts['meme']*100//total if total else 0}%</div></div>
</div>

<div class="card">
  <div class="chart-wrap"><canvas id="timelineChart"></canvas></div>
</div>

<div class="card">
  <h2>🔄 Automated Pipeline</h2>
  <div class="pipeline">
    <div class="pipe-step"><div class="name">🕷️ Scrapers</div><div class="desc">X · Reddit · YouTube · HN<br>public APIs + fxtwitter</div></div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step"><div class="name">🎯 Amplifier Watchlist</div><div class="desc">auto-score creators<br>self-expanding weekly</div></div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step"><div class="name">🗄️ Unified Dataset</div><div class="desc">{total} posts normalized<br>deduped across platforms</div></div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step"><div class="name">🏷️ Spike Classifier</div><div class="desc">5 types: breakthrough<br>tutorial · comparison · personal · meme</div></div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step"><div class="name">📊 Velocity Ranker</div><div class="desc">HN gravity formula<br>cross-platform normalized</div></div>
    <div class="pipe-arrow">→</div>
    <div class="pipe-step"><div class="name">🚨 Alert Layer</div><div class="desc">velocity &gt; 1.0 AND age &lt; 6h<br>→ flag human review</div></div>
  </div>
  <div class="alert-box">
    <div class="alert-title">🚨 Alert Signal Design</div>
    Flag when: <strong>velocity &gt; 1.0</strong> (HN gravity) AND <strong>age &lt; 6h</strong> AND spike_type ∈ {{personal, meme}} = organic content gaining momentum. Runs every Monday 08:00 UTC via cron.
  </div>
</div>

<div class="card">
  <h2>📈 Top Viral Posts (by raw engagement)</h2>
  <table>
    <thead><tr><th>Date</th><th>Platform</th><th>Type</th><th>Title</th><th>Score</th></tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
</div>

<div class="card">
  <h2>🎯 The 3-Wave Cascade</h2>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:8px">
    <div class="pipe-step"><div class="name">Wave 1 · Day 0–7</div><div class="desc">⚡ Breakthrough<br>HN + X<br>Engineers &amp; press pick up</div></div>
    <div class="pipe-step"><div class="name">Wave 2 · Day 7–21</div><div class="desc">📖 Tutorial + ⚔️ Comparison<br>YouTube<br>Creator economy activates</div></div>
    <div class="pipe-step"><div class="name">Wave 3 · Day 21+</div><div class="desc">💬 Personal + 😂 Meme<br>Reddit<br>Cultural lock-in</div></div>
  </div>
</div>

<script>
Chart.register(window['chartjs-plugin-annotation']);
new Chart(document.getElementById('timelineChart').getContext('2d'), {json.dumps(chart_config, indent=2)});
</script>
</body>
</html>"""

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"[done] → {OUTPUT_HTML}")
    print(f"        Open: xdg-open {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
