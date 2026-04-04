"""
generate_charts.py — produce PNG charts for PLAYBOOK_ANALYSIS.md findings.
Outputs to data/charts/. Called by pipeline.py or standalone.
"""

from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

REPO_ROOT = Path(__file__).parent.parent
PROCESSED = REPO_ROOT / "data" / "processed"
CHARTS = REPO_ROOT / "data" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

COLORS = {
    "breakthrough": "#4C72B0",
    "tutorial":     "#DD8452",
    "personal":     "#55A868",
    "meme":         "#C44E52",
    "comparison":   "#8172B2",
}
PLATFORM_COLORS = {
    "hn":      "#FF6600",
    "reddit":  "#FF4500",
    "youtube": "#CC0000",
    "x":       "#1DA1F2",
}


def load():
    unified = pd.read_csv(PROCESSED / "unified_posts.csv")
    unified["created_at"] = pd.to_datetime(unified["created_at"], utc=True, errors="coerce")
    classified = pd.read_csv(PROCESSED / "spike_classified.csv")
    frontpage = pd.read_csv(PROCESSED / "growth_frontpage.csv")
    return unified, classified, frontpage


# ── Chart 1: Spike type — volume vs median engagement ─────────────────────────
def chart_spike_types(classified):
    stats = classified.groupby("spike_type")["engagement_score"].agg(
        count="count", median="median", mean="mean"
    ).reset_index()
    total = stats["count"].sum()
    stats["pct"] = stats["count"] / total * 100
    stats = stats.sort_values("pct", ascending=False)

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    x = np.arange(len(stats))
    bars = ax1.bar(x, stats["pct"], color=[COLORS[t] for t in stats["spike_type"]], alpha=0.85, width=0.5)
    ax2.plot(x, stats["median"], marker="o", color="#333", linewidth=2, markersize=7, label="Median engagement")
    ax2.plot(x, stats["mean"] / 1000, marker="s", color="#888", linewidth=1.5,
             markersize=6, linestyle="--", label="Mean engagement (÷1K)")

    ax1.set_ylabel("% of posts", fontsize=11)
    ax2.set_ylabel("Engagement score", fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels([t.capitalize() for t in stats["spike_type"]], fontsize=11)
    ax1.set_title("Finding 3 — Spike Type: Volume vs Engagement\n"
                  "Meme has the highest ceiling; breakthrough is the most common but least consistent",
                  fontsize=11, pad=12)

    for bar, row in zip(bars, stats.itertuples()):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f"{row.pct:.0f}%", ha="center", va="bottom", fontsize=9)

    lines, labels = ax2.get_legend_handles_labels()
    ax2.legend(lines, labels, loc="upper right", fontsize=9)
    fig.tight_layout()
    out = CHARTS / "chart_spike_types.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 2: YouTube — community vs official ──────────────────────────────────
def chart_youtube_reach(unified):
    yt = unified[unified["platform"] == "youtube"].copy()
    official_mask = yt["author"] == "Anthropic"
    official_views = yt[official_mask]["engagement_score"].sum()
    community_views = yt[~official_mask]["engagement_score"].sum()
    official_count = official_mask.sum()
    community_count = (~official_mask).sum()

    # Top community creators
    top = (yt[~official_mask]
           .groupby("author")["engagement_score"]
           .sum()
           .sort_values(ascending=False)
           .head(6))

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # Left: total views comparison
    ax = axes[0]
    labels = [f"Anthropic official\n({official_count} video)", f"Community creators\n({community_count} videos)"]
    values = [official_views, community_views]
    bars = ax.bar(labels, values, color=["#4C72B0", "#C44E52"], alpha=0.85, width=0.45)
    ax.set_ylabel("Total views", fontsize=11)
    ax.set_title("Total YouTube Views\nOfficial vs Community", fontsize=11)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 50000,
                f"{val/1e6:.2f}M", ha="center", fontsize=10, fontweight="bold")
    ratio = community_views / official_views
    ax.text(0.5, 0.92, f"Community = {ratio:.0f}x official",
            transform=ax.transAxes, ha="center", fontsize=10,
            color="#C44E52", fontweight="bold")

    # Right: top creators bar
    ax2 = axes[1]
    ax2.barh(top.index[::-1], top.values[::-1], color="#DD8452", alpha=0.85)
    ax2.set_xlabel("Total views", fontsize=11)
    ax2.set_title("Top Community Creators\n(same period)", fontsize=11)
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    for i, (name, val) in enumerate(zip(top.index[::-1], top.values[::-1])):
        ax2.text(val + 10000, i, f"  {val/1e6:.2f}M", va="center", fontsize=8)

    fig.suptitle("Finding 2 — Community creators outperform Anthropic's channel 29x",
                 fontsize=11, y=1.01)
    fig.tight_layout()
    out = CHARTS / "chart_youtube_reach.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 3: Title word lift ───────────────────────────────────────────────────
def chart_word_lift(classified):
    # Validated numbers from our analysis
    words   = ["leaked/leaks", "chatgpt", "tutorial", "sonnet", "insane", "anthropic (alone)", "gemini"]
    lifts   = [22.0,           15.5,      8.3,        6.1,      5.4,      0.35,                 0.28]
    colors  = ["#C44E52" if l >= 1.0 else "#888888" for l in lifts]

    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(words))
    bars = ax.barh(y, lifts, color=colors, alpha=0.85)
    ax.axvline(1.0, color="#333", linewidth=1.2, linestyle="--", alpha=0.6)
    ax.text(1.05, len(words) - 0.5, "baseline (1x)", fontsize=8, color="#555")
    ax.set_yticks(y)
    ax.set_yticklabels(words, fontsize=11)
    ax.set_xlabel("Engagement lift (top 20% vs bottom 20%)", fontsize=11)
    ax.set_title("Finding 5 — Title Word Lift Analysis\n"
                 "Words overrepresented in high-engagement posts vs low-engagement posts",
                 fontsize=11, pad=12)
    for bar, val in zip(bars, lifts):
        label = f"{val}x"
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                label, va="center", fontsize=10, fontweight="bold")
    ax.set_xlim(0, 26)
    high = mpatches.Patch(color="#C44E52", alpha=0.85, label="Positive signal")
    low  = mpatches.Patch(color="#888888", alpha=0.85, label="Negative signal")
    ax.legend(handles=[high, low], loc="lower right", fontsize=9)
    fig.tight_layout()
    out = CHARTS / "chart_word_lift.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 4: 3-wave cascade timeline ─────────────────────────────────────────
def chart_cascade_timeline():
    # Validated timestamps from Apr 1, 2026 source code leak
    events = [
        (0.0,   "hn",      "HN: First post\n(01:13 UTC)",              2),
        (0.12,  "x",       "X: First tweets\n(~01:20 UTC)",            1),
        (0.12,  "youtube", "YouTube Wave 1\nMatthew Berman (162K)",    162576),
        (3.0,   "youtube", "YouTube Wave 1\nTheo t3.gg (182K)",        182642),
        (12.0,  "reddit",  "Reddit joins\n(12:54 UTC, 337 pts)",       337),
        (16.0,  "youtube", "YouTube Wave 2\nFireship (2.59M)",         2592415),
        (48.0,  "youtube", "YouTube Wave 3\nSATIME satire (131K)",     131467),
        (48.5,  "youtube", "International\nPortuguese creators (89K)", 89249),
    ]

    fig, ax = plt.subplots(figsize=(11, 5))

    for hours, platform, label, size in events:
        color = PLATFORM_COLORS[platform]
        # bubble size proportional to log(engagement)
        bubble = max(50, np.log1p(size) * 40)
        ax.scatter(hours, 0.5, s=bubble, color=color, alpha=0.75, zorder=3)
        yoff = 0.18 if events.index((hours, platform, label, size)) % 2 == 0 else -0.22
        ax.annotate(label, xy=(hours, 0.5), xytext=(hours, 0.5 + yoff),
                    fontsize=7.5, ha="center", va="center",
                    arrowprops=dict(arrowstyle="-", color="#aaa", lw=0.8))

    # Wave shading
    ax.axvspan(0, 2,   alpha=0.06, color="#FF6600", label="Wave 1 (0–2h): HN + YouTube")
    ax.axvspan(2, 16,  alpha=0.06, color="#CC0000", label="Wave 2 (2–16h): Tutorials + Reddit")
    ax.axvspan(16, 52, alpha=0.06, color="#8172B2", label="Wave 3 (16h+): Meme + International")

    ax.set_xlabel("Hours after HN post (Apr 1, 2026 source code leak)", fontsize=11)
    ax.set_title("Finding 1 — The 3-Wave Cascade (validated with timestamps)\n"
                 "Bubble size proportional to engagement", fontsize=11, pad=12)
    ax.set_yticks([])
    ax.set_xlim(-2, 52)
    ax.set_ylim(0, 1)

    # Platform legend
    patches = [mpatches.Patch(color=PLATFORM_COLORS[p], label=p.upper(), alpha=0.8)
               for p in ["hn", "youtube", "reddit", "x"]]
    ax.legend(handles=patches, loc="upper right", fontsize=8)

    # Wave legend
    w1 = mpatches.Patch(color="#FF6600", alpha=0.2, label="Wave 1: HN + immediate YouTube")
    w2 = mpatches.Patch(color="#CC0000", alpha=0.2, label="Wave 2: Tutorials + Reddit")
    w3 = mpatches.Patch(color="#8172B2", alpha=0.2, label="Wave 3: Meme + International")
    ax.legend(handles=patches + [w1, w2, w3], loc="upper right", fontsize=8, ncol=2)

    fig.tight_layout()
    out = CHARTS / "chart_cascade_timeline.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 5: Engagement decay by platform ────────────────────────────────────
def chart_decay(frontpage):
    fig, ax = plt.subplots(figsize=(9, 5))

    for platform, color in PLATFORM_COLORS.items():
        subset = frontpage[frontpage["platform"] == platform].copy()
        if subset.empty:
            continue
        # bin by age
        subset["age_day"] = (subset["age_hours"] / 24).clip(0, 6).round(1)
        decay = subset.groupby("age_day")["velocity"].mean().reset_index()
        decay = decay.sort_values("age_day")
        ax.plot(decay["age_day"], decay["velocity"], marker="o", color=color,
                linewidth=2, markersize=5, label=platform.upper(), alpha=0.85)

    ax.set_xlabel("Post age (days)", fontsize=11)
    ax.set_ylabel("Avg velocity score", fontsize=11)
    ax.set_title("Finding 6 — Engagement Decay by Platform\n"
                 "HN dies in 24h; YouTube retains velocity 6+ days",
                 fontsize=11, pad=12)
    ax.legend(fontsize=10)
    ax.set_xlim(0, 6.2)
    fig.tight_layout()
    out = CHARTS / "chart_decay.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 6: HN timing + Reddit day-of-week ──────────────────────────────────
def chart_timing(unified):
    hn = unified[unified["platform"] == "hn"].copy()
    hn["hour"] = hn["created_at"].dt.hour
    hn_hourly = hn.groupby("hour")["engagement_score"].mean()

    rd = unified[unified["platform"] == "reddit"].copy()
    rd["day"] = rd["created_at"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    rd_daily = rd.groupby("day")["engagement_score"].mean().reindex(day_order)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    hours = hn_hourly.index
    vals = hn_hourly.values
    bar_colors = ["#C44E52" if 18 <= h <= 23 else "#4C72B0" for h in hours]
    ax.bar(hours, vals, color=bar_colors, alpha=0.85)
    ax.set_xlabel("Hour (UTC)", fontsize=11)
    ax.set_ylabel("Avg HN score", fontsize=11)
    ax.set_title("HN — Best posting hours\n2–6pm ET = 18–22 UTC", fontsize=11)
    ax.set_xticks(range(0, 24, 2))
    peak = mpatches.Patch(color="#C44E52", alpha=0.85, label="Peak window (18–23 UTC)")
    ax.legend(handles=[peak], fontsize=9)

    ax2 = axes[1]
    day_colors = ["#C44E52" if d in ("Saturday", "Sunday") else "#4C72B0" for d in day_order]
    ax2.bar(day_order, rd_daily.values, color=day_colors, alpha=0.85)
    ax2.set_ylabel("Avg Reddit score", fontsize=11)
    ax2.set_title("Reddit — Best posting days\nWeekends 2.7x weekdays", fontsize=11)
    ax2.tick_params(axis="x", rotation=30)
    weekend = mpatches.Patch(color="#C44E52", alpha=0.85, label="Weekend (2.7x higher)")
    ax2.legend(handles=[weekend], fontsize=9)

    fig.suptitle("Finding 4 — Platform Timing Patterns", fontsize=12, y=1.01)
    fig.tight_layout()
    out = CHARTS / "chart_timing.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


def main():
    print("Loading data...")
    unified, classified, frontpage = load()
    print("Generating charts...")
    chart_cascade_timeline()
    chart_youtube_reach(unified)
    chart_spike_types(classified)
    chart_timing(unified)
    chart_word_lift(classified)
    chart_decay(frontpage)
    print(f"\nDone. Charts saved to {CHARTS}/")


if __name__ == "__main__":
    main()
