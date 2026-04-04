#!/usr/bin/env python3
"""
generate_charts_extended.py — 4 new PNG charts for the extended playbook analysis.
Follows same style as generate_charts.py (one clear insight per chart).
Outputs to data/charts/.

Charts produced:
  chart_pareto_curve.png     — 10% of posts = 78–80% of engagement
  chart_author_concentration.png — top 10 authors own 96% of views
  chart_media_vs_text.png    — media posts 8–10x higher engagement
  chart_comment_sentiment.png — sentiment breakdown by spike type
"""

import json, sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT      = Path(__file__).parent.parent
PROCESSED = ROOT / "data" / "processed"
CHARTS    = ROOT / "data" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

METRICS_FILE = PROCESSED / "analysis_metrics.json"

# ── Style (matches generate_charts.py) ───────────────────────────────────────
plt.rcParams.update({
    "font.family":        "sans-serif",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "figure.facecolor":   "white",
    "axes.facecolor":     "white",
    "font.size":          11,
})

PLATFORM_COLORS = {"hn": "#FF6600", "reddit": "#FF4500", "youtube": "#CC0000", "x": "#1DA1F2"}
SPIKE_COLORS    = {
    "breakthrough": "#4C72B0",
    "tutorial":     "#DD8452",
    "personal":     "#55A868",
    "meme":         "#C44E52",
    "comparison":   "#8172B2",
}
SENTIMENT_COLORS = {"positive": "#55A868", "neutral": "#AAAAAA", "negative": "#C44E52"}


def load_metrics() -> dict:
    if not METRICS_FILE.exists():
        sys.exit("ERROR: analysis_metrics.json not found — run compute_playbook_metrics.py first")
    return json.loads(METRICS_FILE.read_text(encoding="utf-8"))


# ── Chart 1: Pareto curve ─────────────────────────────────────────────────────
def chart_pareto_curve(metrics: dict):
    """Shows: top 10% of posts = 78–80% of engagement. One line per platform."""
    pareto = metrics["pareto"]
    fig, ax = plt.subplots(figsize=(8, 5))

    for platform, data in pareto.items():
        x = data["cumulative_pct_posts"]
        y = data["cumulative_pct_engagement"]
        color = PLATFORM_COLORS.get(platform, "#888888")
        top10 = data["top_10pct_share"]
        ax.plot(x, y, color=color, linewidth=2.5,
                label=f"{platform.upper()}  (top 10% = {top10}% of eng.)")

    # perfect equality line
    ax.plot([0, 100], [0, 100], "--", color="#CCCCCC", linewidth=1, label="Perfect equality")

    # shade the 10% mark
    ax.axvline(x=10, color="#CCCCCC", linestyle=":", linewidth=1)
    ax.text(10.5, 15, "10% of posts →", fontsize=9, color="#888888")

    ax.set_xlabel("Cumulative % of posts (sorted by engagement, highest first)")
    ax.set_ylabel("Cumulative % of total engagement")
    ax.set_title("Engagement is Pareto-concentrated:\nTop 10% of posts own 78–80% of all views",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(fontsize=9, frameon=False)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    plt.tight_layout()
    out = CHARTS / "chart_pareto_curve.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [chart] {out.name}")


# ── Chart 2: Author concentration ─────────────────────────────────────────────
def chart_author_concentration(metrics: dict):
    """Shows: top 5 authors = 96.5% of total engagement."""
    data     = metrics["author_concentration"]
    authors  = data["top_10_authors"]
    df       = pd.DataFrame(authors).head(10)

    # truncate long names
    df["label"] = df["author"].str[:22]
    df = df.sort_values("engagement_score")

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [PLATFORM_COLORS.get(p, "#888888") for p in df["platform"]]

    bars = ax.barh(df["label"], df["engagement_score"] / 1e6, color=colors, height=0.6)

    # annotate pct of total
    for bar, (_, row) in zip(bars, df.iterrows()):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f"{row['pct_of_total']}%", va="center", fontsize=9, color="#444444")

    # legend for platforms
    patches = [mpatches.Patch(color=v, label=k.upper()) for k, v in PLATFORM_COLORS.items()
               if k in df["platform"].values]
    ax.legend(handles=patches, fontsize=9, frameon=False, loc="lower right")

    top5_pct = data["top5_share_pct"]
    ax.set_xlabel("Total engagement (millions)")
    ax.set_title(f"Author concentration: top 5 accounts = {top5_pct}% of all engagement\n"
                 f"({data['total_unique_authors']} unique authors total)",
                 fontsize=12, fontweight="bold", pad=12)

    plt.tight_layout()
    out = CHARTS / "chart_author_concentration.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [chart] {out.name}")


# ── Chart 3: Media vs text engagement ────────────────────────────────────────
def chart_media_vs_text(metrics: dict):
    """Shows: media posts 8x (Reddit) and 9.7x (X) higher median engagement."""
    data = metrics["media_vs_text"]
    # only platforms with meaningful media counts
    platforms = {p: v for p, v in data.items() if v["media_count"] >= 5}

    if not platforms:
        print("  [chart] Skipping media_vs_text — insufficient media posts")
        return

    labels   = list(platforms.keys())
    media_m  = [platforms[p]["media_median"] for p in labels]
    text_m   = [platforms[p]["text_median"]  for p in labels]
    lifts    = [platforms[p]["lift_median"]   for p in labels]

    x  = np.arange(len(labels))
    w  = 0.35
    fig, ax = plt.subplots(figsize=(7, 4.5))

    b1 = ax.bar(x - w/2, text_m,  w, label="Text only",   color="#AAAAAA")
    b2 = ax.bar(x + w/2, media_m, w, label="With media",  color="#4C72B0")

    # lift annotation
    for i, (lift, xi) in enumerate(zip(lifts, x)):
        ymax = max(media_m[i], text_m[i])
        ax.text(xi, ymax * 1.05, f"{lift}x lift", ha="center", fontsize=10,
                fontweight="bold", color="#4C72B0")

    ax.set_xticks(x)
    ax.set_xticklabels([p.upper() for p in labels])
    ax.set_ylabel("Median engagement score")
    ax.set_title("Media posts drive 8–10x higher median engagement\n(Reddit and X)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(frameon=False)

    plt.tight_layout()
    out = CHARTS / "chart_media_vs_text.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [chart] {out.name}")


# ── Chart 4: Comment sentiment by spike type ──────────────────────────────────
def chart_comment_sentiment(metrics: dict):
    """Shows sentiment distribution (positive/neutral/negative) per spike type."""
    rows = metrics["comment_sentiment"]["by_spike_type"]
    if not rows:
        print("  [chart] Skipping comment_sentiment — no spike-linked comment data")
        return

    df = pd.DataFrame(rows).set_index("spike_type")
    # ensure all three columns exist
    for col in ["positive", "neutral", "negative"]:
        if col not in df.columns:
            df[col] = 0.0

    df = df[["positive", "neutral", "negative"]]
    order = ["breakthrough", "tutorial", "personal", "meme", "comparison"]
    df = df.reindex([r for r in order if r in df.index])

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bottom = np.zeros(len(df))

    for col in ["positive", "neutral", "negative"]:
        vals = df[col].values
        bars = ax.bar(df.index, vals, bottom=bottom,
                      color=SENTIMENT_COLORS[col], label=col.capitalize(), width=0.55)
        for bar, val, bot in zip(bars, vals, bottom):
            if val > 8:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bot + val / 2, f"{val:.0f}%",
                        ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        bottom += vals

    overall = metrics["comment_sentiment"]["overall_pct"]
    pos_pct = overall.get("positive", 0)
    ax.set_ylabel("% of comments")
    ax.set_title(f"Comment sentiment by spike type\n"
                 f"Overall: {pos_pct:.0f}% positive across {metrics['comment_sentiment']['total_comments_analyzed']} comments",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_xticklabels(df.index, rotation=15, ha="right")
    ax.legend(frameon=False, loc="upper right")
    ax.set_ylim(0, 110)

    plt.tight_layout()
    out = CHARTS / "chart_comment_sentiment.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [chart] {out.name}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("  [charts-ext] Loading metrics...")
    metrics = load_metrics()

    chart_pareto_curve(metrics)
    chart_author_concentration(metrics)
    chart_media_vs_text(metrics)
    chart_comment_sentiment(metrics)

    print(f"\n  [done] 4 charts → {CHARTS}/")


if __name__ == "__main__":
    main()
