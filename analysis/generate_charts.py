"""
generate_charts.py — produce PNG charts for PLAYBOOK_ANALYSIS.md findings.
Design principle: one clear insight per chart, readable in 3 seconds.
Outputs to data/charts/.
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
CHARTS    = REPO_ROOT / "data" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

GREY   = "#CCCCCC"
BLUE   = "#4C72B0"
RED    = "#C44E52"
ORANGE = "#DD8452"
GREEN  = "#55A868"
PURPLE = "#8172B2"

PLATFORM_COLORS = {"hn": "#FF6600", "reddit": "#FF4500", "youtube": "#CC0000", "x": "#1DA1F2"}
SPIKE_COLORS    = {"breakthrough": BLUE, "tutorial": ORANGE, "personal": GREEN, "meme": RED, "comparison": PURPLE}


def load():
    unified    = pd.read_csv(PROCESSED / "unified_posts.csv")
    unified["created_at"] = pd.to_datetime(unified["created_at"], utc=True, errors="coerce")
    classified = pd.read_csv(PROCESSED / "spike_classified.csv")
    frontpage  = pd.read_csv(PROCESSED / "growth_frontpage.csv")
    return unified, classified, frontpage


# ── Chart 1: 3-wave cascade — clean vertical timeline ─────────────────────────
def chart_cascade_timeline():
    """One clear message: Fireship hits 16h after HN. The window is 0–16h."""
    events = [
        (0,    "hn",      "HN first post\n(01:13 UTC)",           2),
        (0.1,  "x",       "X reacts",                             5000),
        (0.1,  "youtube", "Matthew Berman\n162K views",           162576),
        (3,    "youtube", "Theo t3.gg\n182K views",               182642),
        (12,   "reddit",  "Reddit joins\n337 pts",                337),
        (16,   "youtube", "Fireship\n2.59M views ◀ peak",         2592415),
        (48,   "youtube", "SAMTIME satire\n131K views",           131467),
        (48.5, "youtube", "International wave\n89K views",        89249),
    ]

    fig, ax = plt.subplots(figsize=(11, 4))

    # Wave backgrounds
    ax.axvspan(0,  2,  color="#FFF3E0", zorder=0)
    ax.axvspan(2,  16, color="#FCE4EC", zorder=0)
    ax.axvspan(16, 52, color="#F3E5F5", zorder=0)

    wave_labels = [
        (1,    "Wave 1\n0–2h\nHN + YouTube",    "#E65100"),
        (9,    "Wave 2\n2–16h\nTutorials + Reddit", "#B71C1C"),
        (34,   "Wave 3\n16h+\nMeme + International", "#6A1B9A"),
    ]
    for x, label, color in wave_labels:
        ax.text(x, 0.93, label, transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=8, color=color, alpha=0.7)

    for hours, platform, label, size in events:
        color = PLATFORM_COLORS[platform]
        r = max(8, np.log1p(size) * 5)
        y = 0.5
        ax.scatter(hours, y, s=r**2, color=color, alpha=0.7, zorder=3, linewidths=0)

        # alternate labels above/below
        idx = [e[0] for e in events].index(hours)
        ytext = 0.78 if idx % 2 == 0 else 0.22
        ax.annotate(label, xy=(hours, y), xytext=(hours, ytext),
                    fontsize=7.5, ha="center", va="center", color="#333",
                    arrowprops=dict(arrowstyle="-", color="#bbb", lw=0.8))

    # Highlight the key insight
    ax.axvline(16, color=RED, linewidth=1.5, linestyle="--", alpha=0.6, zorder=2)

    ax.set_xlabel("Hours after first HN post  (Apr 1, 2026 — Claude Code source leak)", fontsize=10)
    ax.set_yticks([])
    ax.set_xlim(-1, 52)
    ax.set_ylim(0, 1)
    ax.set_title("Finding 1 — The 3-Wave Cascade\n"
                 "Maximum impact window is 0–16 hours. After Fireship posts, the moment is made.",
                 fontsize=11, pad=10)

    patches = [mpatches.Patch(color=PLATFORM_COLORS[p], label=p.upper(), alpha=0.8)
               for p in ["hn", "youtube", "reddit", "x"]]
    ax.legend(handles=patches, loc="upper right", fontsize=8, framealpha=0.8)

    fig.tight_layout()
    out = CHARTS / "chart_cascade_timeline.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 2: YouTube — one bar comparison, annotated ─────────────────────────
def chart_youtube_reach(unified):
    """One clear message: community = 29x official."""
    yt = unified[unified["platform"] == "youtube"].copy()
    official_views   = yt[yt["author"] == "Anthropic"]["engagement_score"].sum()
    community_views  = yt[yt["author"] != "Anthropic"]["engagement_score"].sum()
    fireship_views   = yt[yt["author"] == "Fireship"]["engagement_score"].sum()

    fig, ax = plt.subplots(figsize=(7, 4.5))

    bars = ax.bar(
        ["Anthropic official\n(1 video)", "Community creators\n(85 videos)"],
        [official_views, community_views],
        color=[GREY, RED], width=0.5, alpha=0.9
    )

    # Annotate values
    for bar, val in zip(bars, [official_views, community_views]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 30000,
                f"{val/1e6:.2f}M views", ha="center", fontsize=11, fontweight="bold")

    # Fireship callout
    ax.annotate(
        f"Fireship alone: {fireship_views/1e6:.2f}M\n(one video, same event)",
        xy=(1, fireship_views), xytext=(0.62, fireship_views + 800000),
        fontsize=9, color=RED,
        arrowprops=dict(arrowstyle="->", color=RED, lw=1.2)
    )

    # 29x label
    ax.text(0.5, 0.88,  "Community = 29×  official", transform=ax.transAxes,
            ha="center", fontsize=13, fontweight="bold", color=RED)

    ax.set_ylabel("Total YouTube views", fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
    ax.set_title("Finding 2 — Seed creators, not your own channel.\n"
                 "Community outperformed Anthropic 29× on the same event.",
                 fontsize=11, pad=10)
    ax.set_ylim(0, community_views * 1.25)

    fig.tight_layout()
    out = CHARTS / "chart_youtube_reach.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 3: Spike types — scatter (% of posts vs median engagement) ──────────
def chart_spike_types(classified):
    """One clear message: meme is rare but has a massive ceiling. Personal is most reliable."""
    stats = classified.groupby("spike_type")["engagement_score"].agg(
        count="count", median="median", mean="mean"
    ).reset_index()
    total = stats["count"].sum()
    stats["pct"] = stats["count"] / total * 100

    fig, ax = plt.subplots(figsize=(8, 5))

    for _, row in stats.iterrows():
        color = SPIKE_COLORS[row["spike_type"]]
        size  = max(80, row["mean"] / 3000)   # bubble = mean engagement
        ax.scatter(row["pct"], row["median"], s=size, color=color, alpha=0.75,
                   zorder=3, linewidths=0)
        # label offset to avoid overlap
        offsets = {
            "breakthrough": (-3.5,  80),
            "tutorial":     ( 0.5,  80),
            "personal":     ( 0.5, -120),
            "meme":         ( 0.5,  80),
            "comparison":   ( 0.5, -120),
        }
        dx, dy = offsets.get(row["spike_type"], (0.5, 60))
        ax.annotate(
            f"{row['spike_type'].capitalize()}\n{row['pct']:.0f}% of posts\nmedian={int(row['median']):,}",
            xy=(row["pct"], row["median"]),
            xytext=(row["pct"] + dx, row["median"] + dy),
            fontsize=8.5, color=color, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=color, lw=0.8, alpha=0.5)
        )

    ax.set_xlabel("% of all posts  →  more common", fontsize=10)
    ax.set_ylabel("Median engagement  →  more reliable", fontsize=10)
    ax.set_title("Finding 3 — Not all content types are equal\n"
                 "Bubble size = mean engagement (ceiling).  Personal is most consistent; Meme has highest upside.",
                 fontsize=11, pad=10)

    # Quadrant hint
    ax.axhline(100, color=GREY, linewidth=0.8, linestyle="--", zorder=0)
    ax.text(40, 110, "reliable floor", fontsize=7.5, color="#aaa")

    fig.tight_layout()
    out = CHARTS / "chart_spike_types.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 4: Timing — HN hours + Reddit days, side by side ───────────────────
def chart_timing(unified):
    """One clear message: HN 2–6pm ET, Reddit weekends. Counterintuitive."""
    hn = unified[unified["platform"] == "hn"].copy()
    hn["hour"] = hn["created_at"].dt.hour
    hn_hourly = hn.groupby("hour")["engagement_score"].mean().reindex(range(24), fill_value=0)

    rd = unified[unified["platform"] == "reddit"].copy()
    rd["day"] = rd["created_at"].dt.day_name()
    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    rd["day_short"] = rd["created_at"].dt.strftime("%a")
    rd_daily = rd.groupby("day_short")["engagement_score"].mean().reindex(day_order, fill_value=0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # HN
    peak_hours = [h for h in range(24) if 18 <= h <= 23]
    colors_hn  = [RED if h in peak_hours else GREY for h in range(24)]
    ax1.bar(range(24), hn_hourly.values, color=colors_hn, alpha=0.85)
    ax1.set_xticks([0, 6, 12, 18, 23])
    ax1.set_xticklabels(["0", "6", "12", "18\n(2pm ET)", "23\n(6pm ET)"], fontsize=9)
    ax1.set_xlabel("Hour (UTC)", fontsize=10)
    ax1.set_ylabel("Avg HN score", fontsize=10)
    ax1.set_title("HN peaks 2–6pm ET\n(not morning — counterintuitive)", fontsize=11)
    # annotate peak
    peak_val = hn_hourly[22]
    ax1.annotate(f"Peak: {peak_val:.0f} pts\n(22:00 UTC)", xy=(22, peak_val),
                 xytext=(15, peak_val * 0.85), fontsize=9, color=RED, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=RED, lw=1))

    # Reddit
    colors_rd = [RED if d in ("Sat", "Sun") else GREY for d in day_order]
    bars = ax2.bar(day_order, rd_daily.values, color=colors_rd, alpha=0.85)
    ax2.set_ylabel("Avg Reddit score", fontsize=10)
    ax2.set_title("Reddit peaks on weekends\n(Sunday = 2.7× Thursday)", fontsize=11)
    for bar, day, val in zip(bars, day_order, rd_daily.values):
        if day in ("Sat", "Sun"):
            ax2.text(bar.get_x() + bar.get_width() / 2, val + 50,
                     f"{val:.0f}", ha="center", fontsize=9, fontweight="bold", color=RED)

    fig.suptitle("Finding 4 — Timing matters. Post at the right moment.", fontsize=12, y=1.02)
    fig.tight_layout()
    out = CHARTS / "chart_timing.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 5: Word lift — clean horizontal bars ───────────────────────────────
def chart_word_lift():
    """One clear message: lead with drama/comparison, never with brand name."""
    data = [
        ("leaked / leaks",    22.0,  True),
        ("chatgpt",           15.5,  True),
        ("tutorial",           8.3,  True),
        ("sonnet",             6.1,  True),
        ("insane",             5.4,  True),
        ("anthropic (alone)",  0.35, False),
        ("gemini",             0.28, False),
    ]
    labels = [d[0] for d in data]
    lifts  = [d[1] for d in data]
    colors = [GREEN if d[2] else RED for d in data]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    y = np.arange(len(labels))
    ax.barh(y, lifts, color=colors, alpha=0.85, height=0.55)
    ax.axvline(1.0, color="#999", linewidth=1.2, linestyle="--")
    ax.text(1.1, len(labels) - 0.3, "neutral (1×)", fontsize=8, color="#999")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel("Engagement lift  (top 20% posts vs bottom 20%)", fontsize=10)
    ax.set_title('Finding 5 — Title framing drives 22× more engagement\n'
                 '"leaked" and "chatgpt" win. "anthropic" alone hurts.',
                 fontsize=11, pad=10)

    for i, (val, pos) in enumerate(zip(lifts, [d[2] for d in data])):
        color = GREEN if pos else RED
        label = f"{val}×"
        ax.text(val + 0.3, i, label, va="center", fontsize=10, fontweight="bold", color=color)

    ax.set_xlim(0, 26)
    good = mpatches.Patch(color=GREEN, alpha=0.85, label="Use this framing")
    bad  = mpatches.Patch(color=RED,   alpha=0.85, label="Avoid this framing")
    ax.legend(handles=[good, bad], loc="lower right", fontsize=9)

    fig.tight_layout()
    out = CHARTS / "chart_word_lift.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.name}")


# ── Chart 6: Decay — clean line chart ────────────────────────────────────────
def chart_decay(frontpage):
    """One clear message: HN dies in 24h. YouTube holds for 6+ days."""
    fig, ax = plt.subplots(figsize=(8, 4.5))

    for platform, color in PLATFORM_COLORS.items():
        subset = frontpage[frontpage["platform"] == platform].copy()
        if subset.empty:
            continue
        subset["age_day"] = (subset["age_hours"] / 24).clip(0, 7).round(1)
        decay = subset.groupby("age_day")["velocity"].mean().reset_index().sort_values("age_day")
        lw = 2.5 if platform in ("hn", "youtube") else 1.5
        ax.plot(decay["age_day"], decay["velocity"], marker="o", color=color,
                linewidth=lw, markersize=4, label=platform.upper(), alpha=0.9)

    ax.set_xlabel("Post age (days)", fontsize=10)
    ax.set_ylabel("Average velocity score", fontsize=10)
    ax.set_title("Finding 6 — Engagement Decay by Platform\n"
                 "HN is dead after 24h. YouTube holds velocity for 6+ days. Plan your response window accordingly.",
                 fontsize=11, pad=10)

    # Annotations
    ax.axvline(1, color="#ccc", linewidth=1, linestyle=":")
    ax.text(1.05, ax.get_ylim()[1] * 0.95, "24h mark", fontsize=8, color="#aaa")

    ax.legend(fontsize=10)
    ax.set_xlim(0, 7)
    fig.tight_layout()
    out = CHARTS / "chart_decay.png"
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
    chart_word_lift()
    chart_decay(frontpage)
    print(f"\nDone. Charts saved to {CHARTS}/")


if __name__ == "__main__":
    main()
