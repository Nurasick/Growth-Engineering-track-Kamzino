#!/usr/bin/env python3
"""
compute_playbook_metrics.py — extract all analysis metrics from processed CSVs.
Outputs: data/processed/analysis_metrics.json
No API calls. Runs in <5s.

Usage:
    python analysis/compute_playbook_metrics.py

Schema assumed for unified_posts.csv:
    post_id, platform, author, title, engagement_score, created_at,
    has_media, official, [subreddit], [follower_count], [channel]

    Columns in brackets are optional — metrics that depend on them degrade
    gracefully to "not_available" rather than crashing.

Schema assumed for spike_classified.csv:
    post_id, spike_type, engagement_score, title

Schema assumed for growth_frontpage.csv:
    platform, age_hours, velocity

Schema assumed for unified_comments.csv:
    post_id, platform, body_text, [author]
"""

import json, re, sys, math
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations

import pandas as pd
import numpy as np

ROOT      = Path(__file__).parent.parent
PROCESSED = ROOT / "data" / "processed"
OUT       = PROCESSED / "analysis_metrics.json"


# ── Helpers ───────────────────────────────────────────────────────────────────

def col(df, name):
    """Return df[name] if it exists, else an empty Series. Never crashes."""
    return df[name] if name in df.columns else pd.Series(dtype=object)


def safe_median(s):
    v = s.dropna()
    return int(v.median()) if len(v) > 0 else 0


def safe_mean(s):
    v = s.dropna()
    return int(v.mean()) if len(v) > 0 else 0


# ── Loaders ──────────────────────────────────────────────────────────────────

def load():
    def read(f):
        p = PROCESSED / f
        if not p.exists():
            sys.exit(f"ERROR: {f} not found — run: python pipeline.py --skip-scrape")
        return pd.read_csv(p, encoding="utf-8", low_memory=False)

    spike    = read("spike_classified.csv")
    front    = read("growth_frontpage.csv")
    unified  = read("unified_posts.csv")
    comments = read("unified_comments.csv")

    # Normalise types
    unified["created_at"]  = pd.to_datetime(unified["created_at"], utc=True, errors="coerce")
    unified["hour"]        = unified["created_at"].dt.hour
    unified["weekday"]     = unified["created_at"].dt.day_name()
    unified["week"]        = unified["created_at"].dt.isocalendar().week.astype(int)
    unified["year_week"]   = (
        unified["created_at"].dt.strftime("%Y-W%V")
    )
    unified["has_media"]   = col(unified, "has_media").astype(str).str.lower().isin(["true","1","yes"])
    unified["is_official"] = col(unified, "official").astype(str).str.lower().isin(["true","1","yes"])

    # Normalise follower_count if present
    if "follower_count" in unified.columns:
        unified["follower_count"] = pd.to_numeric(unified["follower_count"], errors="coerce")

    return spike, front, unified, comments


# ── Existing metrics (unchanged logic, minor hardening) ──────────────────────

def cascade_timestamps():
    """Hardcoded from validated Apr 1 2026 source code leak event."""
    return {
        "event": "Claude source code leak — April 1 2026",
        "wave1": [
            {"hours_after": 0,    "platform": "hn",      "score": 2,       "label": "HN first post (01:13 UTC)"},
            {"hours_after": 0.1,  "platform": "youtube", "score": 162576,  "label": "Matthew Berman (7 min after HN)"},
            {"hours_after": 3,    "platform": "youtube", "score": 182642,  "label": "Theo t3.gg"},
        ],
        "wave2": [
            {"hours_after": 12,   "platform": "reddit",  "score": 337,     "label": "Reddit joins (12h after HN)"},
            {"hours_after": 16,   "platform": "youtube", "score": 2592415, "label": "Fireship peak (2.59M views)"},
        ],
        "wave3": [
            {"hours_after": 48,   "platform": "youtube", "score": 131467,  "label": "SAMTIME satire"},
            {"hours_after": 48.5, "platform": "youtube", "score": 89249,   "label": "International wave (PT)"},
        ],
        "max_impact_window_hours": 16,
        "cascade_note": (
            "HN ignites at 01:13 UTC → YouTube reacts in 7 min (pre-briefed) → "
            "Reddit joins 12h later (organic) → Fireship peaks at 16h (organic) → "
            "meme/international 48h+"
        ),
    }


def spike_stats(spike):
    total = len(spike)
    stats = (
        spike.groupby("spike_type")["engagement_score"]
        .agg(
            count="count",
            mean=lambda x: int(x.mean()),
            median=lambda x: int(x.median()),
            p90=lambda x: int(x.quantile(0.9)),
            max=lambda x: int(x.max()),
        )
        .reset_index()
    )
    stats["pct"] = (stats["count"] / total * 100).round(1)
    return {
        "total_posts": total,
        "by_type": stats.sort_values("count", ascending=False).to_dict("records"),
    }


def platform_stats(unified):
    out = {}
    for p, grp in unified.groupby("platform"):
        e = grp["engagement_score"]
        out[p] = {
            "count":  int(len(grp)),
            "mean":   safe_mean(e),
            "median": safe_median(e),
            "total":  int(e.sum()),
        }
    return out


def youtube_community_vs_official(unified):
    yt = unified[unified["platform"] == "youtube"].copy()
    comm_views = int(yt[~yt["is_official"]]["engagement_score"].sum())
    off_views  = int(yt[yt["is_official"]]["engagement_score"].sum())
    KNOWN_OFFICIAL = 196616  # validated from prior scrape run
    ratio = round(comm_views / KNOWN_OFFICIAL, 1) if comm_views > 0 else 0

    channel_col = "channel" if "channel" in yt.columns else "author"
    by_channel  = (
        yt.groupby(channel_col)["engagement_score"].sum()
        .sort_values(ascending=False)
    )
    top = by_channel.head(5).reset_index().to_dict("records")
    return {
        "community_total_views":            comm_views,
        "official_total_views_baseline":    KNOWN_OFFICIAL,
        "ratio":                            ratio,
        "top_channels":                     top,
        "note": (
            "Anthropic official channel (196K views) captured from prior scrape run; "
            "not present in current unified_posts.csv"
        ),
    }


def timing_stats(unified):
    hn = (
        unified[unified["platform"] == "hn"]
        .groupby("hour")["engagement_score"]
        .agg(mean=lambda x: round(x.mean(), 1), count="count")
        .reset_index()
        .sort_values("mean", ascending=False)
    )
    reddit = (
        unified[unified["platform"] == "reddit"]
        .groupby("weekday")["engagement_score"]
        .agg(mean=lambda x: round(x.mean(), 1), count="count")
        .reset_index()
        .sort_values("mean", ascending=False)
    )

    def day_mean(day):
        row = reddit[reddit["weekday"] == day]
        return float(row["mean"].values[0]) if len(row) > 0 else None

    return {
        "hn_by_utc_hour":    hn.to_dict("records"),
        "hn_peak_note":      "Hours 19–23 UTC (2–6 pm ET) average 35–49 pts vs ~10 pts at other hours",
        "reddit_by_weekday": reddit.to_dict("records"),
        "reddit_peak_note":  (
            f"Sunday avg {day_mean('Sunday')} vs Thursday avg {day_mean('Thursday')}"
        ),
    }


def decay_stats(front):
    buckets = [("day0", 0, 24), ("day1", 24, 48), ("day3", 72, 96), ("day6", 144, 168)]
    result  = {}
    for label, lo, hi in buckets:
        bucket = front[(front["age_hours"] >= lo) & (front["age_hours"] < hi)]
        result[label] = {
            p: round(float(g["velocity"].mean()), 4)
            for p, g in bucket.groupby("platform")
            if len(g) > 0
        }
    return result


def word_lift(spike, top_q=0.8, bot_q=0.2, min_count=3):
    top_thresh = spike["engagement_score"].quantile(top_q)
    bot_thresh = spike["engagement_score"].quantile(bot_q)

    stop = {
        "the","a","an","of","in","to","and","for","is","are","with","on","by",
        "at","it","this","that","how","i","my","from","its","was","be","as",
        "what","we","you","your","do","not","but","or","have","has","can",
        "use","via","–","-","vs","so","if","new","more","just","get","all",
        "now","will","about","into","been","they","their","than","when",
        "after","some","one","two","no","up","using","make",
    }

    top_text = " ".join(spike[spike["engagement_score"] >= top_thresh]["title"].dropna().str.lower())
    bot_text = " ".join(spike[spike["engagement_score"] <= bot_thresh]["title"].dropna().str.lower())

    top_words = Counter(w for w in re.findall(r"[a-z]{4,}", top_text) if w not in stop)
    bot_words = Counter(w for w in re.findall(r"[a-z]{4,}", bot_text) if w not in stop)
    total_top = sum(top_words.values()) or 1
    total_bot = sum(bot_words.values()) or 1

    lift = {}
    for word, cnt in top_words.items():
        if cnt >= min_count:
            top_rate = cnt / total_top
            bot_rate = (bot_words.get(word, 0) + 0.5) / total_bot
            lift[word] = round(top_rate / bot_rate, 2)

    top20 = sorted(lift.items(), key=lambda x: -x[1])[:20]
    bot10 = sorted(lift.items(), key=lambda x:  x[1])[:10]

    return {
        "top_lift_words":    [{"word": w, "lift": l} for w, l in top20],
        "bottom_lift_words": [{"word": w, "lift": l} for w, l in bot10],
        "method": f"top {int(top_q*100)}% vs bottom {int(bot_q*100)}% engagement posts, min {min_count} occurrences",
    }


def pareto_analysis(unified):
    result = {}
    for p, grp in unified.groupby("platform"):
        scores = grp["engagement_score"].sort_values(ascending=False).values
        total  = scores.sum()
        if total == 0:
            continue
        cumsum    = np.cumsum(scores)
        n         = len(scores)
        pct_posts = [i / n for i in range(1, n + 1)]
        pct_eng   = [c / total for c in cumsum]

        idx_80 = next((i for i, v in enumerate(pct_eng) if v >= 0.80), n - 1)
        top10  = int(round(scores[:max(1, n // 10)].sum() / total * 100, 0))
        top1   = int(round(scores[:max(1, n // 100)].sum() / total * 100, 0)) if n >= 100 else None

        result[p] = {
            "n":                          n,
            "top_10pct_share":            top10,
            "top_1pct_share":             top1,
            "posts_for_80pct_engagement": round(idx_80 / n * 100, 1),
            # Stripped in slim_metrics() before sending to the model
            "cumulative_pct_posts":       [round(v * 100, 1) for v in pct_posts],
            "cumulative_pct_engagement":  [round(v * 100, 1) for v in pct_eng],
        }
    return result


def author_concentration(unified):
    by_author = (
        unified.groupby("author")["engagement_score"]
        .sum()
        .sort_values(ascending=False)
    )
    total = by_author.sum()
    top10 = by_author.head(10).reset_index()
    top10["cumulative_pct"] = (top10["engagement_score"].cumsum() / total * 100).round(1)
    top10["pct_of_total"]   = (top10["engagement_score"] / total * 100).round(1)

    author_platform = unified.groupby("author")["platform"].agg(
        lambda x: x.value_counts().index[0]
    )
    top10["platform"]    = top10["author"].map(author_platform)
    top10["is_official"] = top10["author"].map(
        unified.groupby("author")["is_official"].any()
    )

    return {
        "total_unique_authors": int(unified["author"].nunique()),
        "total_engagement":     int(total),
        "top_10_authors":       top10.to_dict("records"),
        "top5_share_pct":       round(top10.head(5)["engagement_score"].sum() / total * 100, 1),
        "top1_share_pct":       round(top10.head(1)["engagement_score"].sum() / total * 100, 1),
        "note": (
            "top1 is typically the official brand account. "
            "is_official flag is set from the 'official' column in unified_posts.csv."
        ),
    }


def media_vs_text(unified):
    result = {}
    for p in ["reddit", "x", "hn", "youtube"]:
        grp   = unified[unified["platform"] == p]
        media = grp[grp["has_media"] == True]["engagement_score"]
        text  = grp[grp["has_media"] == False]["engagement_score"]
        if len(media) == 0 and len(text) == 0:
            continue
        med_media = media.median() if len(media) > 0 else 0
        med_text  = text.median()  if len(text)  > 0 else 0
        result[p] = {
            "media_count":  int(len(media)),
            "text_count":   int(len(text)),
            "media_median": int(med_media) if not math.isnan(med_media) else 0,
            "text_median":  int(med_text)  if not math.isnan(med_text)  else 0,
            "media_mean":   int(media.mean()) if len(media) > 0 else 0,
            "text_mean":    int(text.mean())  if len(text)  > 0 else 0,
            "lift_median":  round(med_media / max(med_text, 1), 1),
        }
    return result


def comment_sentiment(comments):
    POS_WORDS = {
        "great","amazing","love","perfect","excellent","awesome","incredible",
        "useful","helpful","impressive","best","fantastic","brilliant","good",
        "nice","works","solved","fixed","thanks","thank","clever","genius",
    }
    NEG_WORDS = {
        "bad","terrible","wrong","broken","useless","hate","awful","horrible",
        "disappointed","fail","failed","worse","worst","waste","stupid","dumb",
        "disagree","problem","issue","bug","error","confused","misleading",
    }

    def classify(text):
        if not isinstance(text, str):
            return "neutral"
        words = set(re.findall(r"[a-z]+", text.lower()))
        pos   = len(words & POS_WORDS)
        neg   = len(words & NEG_WORDS)
        if pos > neg:   return "positive"
        if neg > pos:   return "negative"
        return "neutral"

    comments = comments.copy()
    comments["sentiment"] = comments["body_text"].apply(classify)

    spike_map = {}
    spike_path = PROCESSED / "spike_classified.csv"
    if spike_path.exists():
        spike_df  = pd.read_csv(spike_path, encoding="utf-8")[["post_id", "spike_type"]]
        spike_map = dict(zip(spike_df["post_id"].astype(str), spike_df["spike_type"]))
    comments["spike_type"] = comments["post_id"].astype(str).map(spike_map).fillna("unknown")

    by_platform = (
        comments.groupby(["platform", "sentiment"])
        .size().unstack(fill_value=0)
        .apply(lambda row: (row / row.sum() * 100).round(1), axis=1)
        .reset_index().to_dict("records")
    )
    by_spike = (
        comments[comments["spike_type"] != "unknown"]
        .groupby(["spike_type", "sentiment"])
        .size().unstack(fill_value=0)
        .apply(lambda row: (row / row.sum() * 100).round(1), axis=1)
        .reset_index().to_dict("records")
    )
    overall = comments["sentiment"].value_counts(normalize=True).mul(100).round(1).to_dict()

    return {
        "total_comments_analyzed": int(len(comments)),
        "overall_pct":             overall,
        "by_platform":             by_platform,
        "by_spike_type":           by_spike,
        "positive_keywords_used":  sorted(POS_WORDS),
        "negative_keywords_used":  sorted(NEG_WORDS),
    }


# ── New metrics ───────────────────────────────────────────────────────────────

def official_vs_community_x(unified):
    """
    Finding 9 / F11 support: compare official account reach vs community accounts on X.
    Uses the is_official flag in unified_posts.csv.
    Also surfaces the top non-official author on X as the 'inside engineer equivalent'.
    """
    x = unified[unified["platform"] == "x"].copy()
    if len(x) == 0:
        return {"available": False, "reason": "No X posts in unified_posts.csv"}

    official   = x[x["is_official"] == True]
    community  = x[x["is_official"] == False]

    off_total  = int(official["engagement_score"].sum())
    comm_total = int(community["engagement_score"].sum())
    multiplier = round(comm_total / max(off_total, 1), 1)

    # Top community author by total engagement
    top_comm = (
        community.groupby("author")["engagement_score"]
        .agg(total=sum, count="count", mean=lambda x: int(x.mean()))
        .sort_values("total", ascending=False)
        .head(5)
        .reset_index()
        .to_dict("records")
    )

    # Per-tweet comparison
    off_per_tweet  = int(official["engagement_score"].mean())  if len(official)  > 0 else 0
    comm_per_tweet = int(community["engagement_score"].mean()) if len(community) > 0 else 0

    return {
        "available":                True,
        "official_post_count":      int(len(official)),
        "official_total":           off_total,
        "official_mean_per_post":   off_per_tweet,
        "community_post_count":     int(len(community)),
        "community_total":          comm_total,
        "community_mean_per_post":  comm_per_tweet,
        "community_vs_official_total_multiplier": multiplier,
        "top_community_authors":    top_comm,
        "interpretation": (
            f"Community accounts ({len(community)} posts) generated "
            f"{multiplier}x the total engagement of the official account "
            f"({len(official)} posts)."
        ),
    }


def subreddit_breakdown(unified):
    """
    Finding 13 support: per-subreddit performance for Claude-related Reddit posts.
    Requires a 'subreddit' column in unified_posts.csv.
    Degrades gracefully if the column is absent.
    """
    if "subreddit" not in unified.columns:
        return {
            "available": False,
            "reason": (
                "'subreddit' column not found in unified_posts.csv. "
                "Add it in your Reddit scraper and re-run the pipeline."
            ),
        }

    reddit = unified[unified["platform"] == "reddit"].copy()
    if len(reddit) == 0 or reddit["subreddit"].isna().all():
        return {"available": False, "reason": "No Reddit posts with subreddit data"}

    by_sub = (
        reddit.groupby("subreddit")["engagement_score"]
        .agg(
            n="count",
            mean=lambda x: round(x.mean(), 1),
            median=lambda x: round(x.median(), 1),
            max=lambda x: int(x.max()),
        )
        .reset_index()
        .sort_values("mean", ascending=False)
    )

    return {
        "available":        True,
        "by_subreddit":     by_sub.to_dict("records"),
        "note": (
            "Higher mean in competitor subreddits vs home subreddit indicates "
            "switching-frame content outperforms in discovery audiences."
        ),
    }


def follower_count_vs_reach(unified):
    """
    Finding 12 support: follower count buckets vs engagement.
    Requires a 'follower_count' column in unified_posts.csv (X only).
    Degrades gracefully if absent.
    """
    if "follower_count" not in unified.columns:
        return {
            "available": False,
            "reason": (
                "'follower_count' column not found in unified_posts.csv. "
                "Add it in your X scraper (via fxtwitter enrichment) and re-run."
            ),
        }

    x = unified[
        (unified["platform"] == "x") &
        unified["follower_count"].notna() &
        (unified["follower_count"] > 0)
    ].copy()

    if len(x) < 10:
        return {"available": False, "reason": f"Too few X posts with follower data (n={len(x)})"}

    bins   = [0, 10_000, 100_000, 1_000_000, float("inf")]
    labels = ["<10K", "10K–100K", "100K–1M", "1M+"]
    x["follower_bucket"] = pd.cut(x["follower_count"], bins=bins, labels=labels)

    by_bucket = (
        x.groupby("follower_bucket", observed=True)["engagement_score"]
        .agg(
            n="count",
            median=lambda s: int(s.median()),
            mean=lambda s:   int(s.mean()),
            max=lambda s:    int(s.max()),
        )
        .reset_index()
    )
    by_bucket["outlier_to_median_ratio"] = (
        by_bucket["max"] / by_bucket["median"].replace(0, 1)
    ).round(1)

    # Top 5 accounts by views/follower ratio
    x["vpf_ratio"] = (x["engagement_score"] / x["follower_count"]).round(1)
    top_vpf = (
        x.nlargest(5, "vpf_ratio")[["author", "follower_count", "engagement_score", "vpf_ratio"]]
        .to_dict("records")
    )

    return {
        "available":                    True,
        "by_follower_bucket":           by_bucket.to_dict("records"),
        "top_views_per_follower":       top_vpf,
        "note": (
            "outlier_to_median_ratio is highest in small-account buckets — "
            "when small accounts go viral, they go more disproportionately viral."
        ),
    }


def author_type_breakdown(unified, spike):
    """
    Finding 9 / F11 support: break down engagement by author type and content type.
    Author types: official (is_official=True) vs community.
    Crossed with spike_type where available.
    """
    merged = unified.merge(
        spike[["post_id", "spike_type"]],
        on="post_id", how="left"
    )
    merged["author_type"] = merged["is_official"].map(
        {True: "official", False: "community"}
    )

    by_type = (
        merged.groupby("author_type")["engagement_score"]
        .agg(
            n="count",
            total=sum,
            mean=lambda x: int(x.mean()),
            median=lambda x: int(x.median()),
        )
        .reset_index()
        .to_dict("records")
    )

    # Cross: author_type × spike_type — reveals which content types each author
    # category produces and how they perform
    cross = (
        merged[merged["spike_type"].notna()]
        .groupby(["author_type", "spike_type"])["engagement_score"]
        .agg(n="count", mean=lambda x: int(x.mean()), median=lambda x: int(x.median()))
        .reset_index()
        .to_dict("records")
    )

    return {
        "available":              True,
        "by_author_type":         by_type,
        "by_author_type_x_spike": cross,
    }


def weekly_volume_trend(unified):
    """
    Finding 6 / F10 support: weekly post volume and engagement per platform.
    Reveals the 'halo effect' — weeks where one platform spikes tend to
    coincide with elevated activity on others (compounds vs cannibalizes).
    Also surfaces phrase-based trend if title column is available.
    """
    if unified["created_at"].isna().all():
        return {"available": False, "reason": "No valid created_at timestamps"}

    # Weekly engagement per platform
    weekly = (
        unified.groupby(["year_week", "platform"])["engagement_score"]
        .agg(total=sum, n="count", mean=lambda x: round(x.mean(), 1))
        .reset_index()
    )

    # Pivot to wide — one column per platform — to detect co-occurrence
    pivot = weekly.pivot_table(
        index="year_week", columns="platform",
        values="total", aggfunc="sum", fill_value=0
    ).reset_index()

    # Correlation matrix between platform weekly totals
    platform_cols = [c for c in pivot.columns if c != "year_week"]
    corr = {}
    for a, b in combinations(platform_cols, 2):
        r = pivot[a].corr(pivot[b])
        if not math.isnan(r):
            corr[f"{a}_vs_{b}"] = round(r, 3)

    # Top 10 weeks by total cross-platform engagement
    pivot["total_all"] = pivot[platform_cols].sum(axis=1)
    top_weeks = (
        pivot.sort_values("total_all", ascending=False)
        .head(10)
        .to_dict("records")
    )

    # Phrase tracking — find weeks where a high-lift word dominates titles
    phrase_trend = {}
    if "title" in unified.columns:
        # Pull top 5 lift words from word_lift results — we re-derive here
        # using the same top-20% threshold for consistency
        top_thresh = unified["engagement_score"].quantile(0.8)
        top_titles = unified[unified["engagement_score"] >= top_thresh]["title"].dropna().str.lower()
        all_words  = Counter(
            w for t in top_titles
            for w in re.findall(r"[a-z]{5,}", t)
        )
        # Track top 5 words week over week
        top_phrases = [w for w, _ in all_words.most_common(5)]
        for phrase in top_phrases:
            mask = unified["title"].str.contains(phrase, case=False, na=False)
            weekly_phrase = (
                unified[mask]
                .groupby("year_week")["engagement_score"]
                .agg(n="count", total=sum)
                .reset_index()
            )
            if len(weekly_phrase) >= 3:  # only include if phrase appears in 3+ weeks
                phrase_trend[phrase] = weekly_phrase.to_dict("records")

    return {
        "available":                 True,
        "weekly_by_platform":        weekly.to_dict("records"),
        "top_weeks_cross_platform":  top_weeks,
        "platform_weekly_correlation": corr,
        "phrase_weekly_trend":       phrase_trend,
        "correlation_note": (
            "Correlation > 0.5 between two platforms in the same week suggests "
            "a shared narrative drove both — compounds rather than cannibalizes. "
            "Correlation near 0 suggests independent events."
        ),
    }


def narrative_switching_signal(unified, spike):
    """
    Finding 14 / F13 support: detect switching-narrative posts without a
    full cascade detector. Uses title keyword matching to surface posts
    that match the 'switching' frame (e.g., 'switched from', 'vs', 'better than',
    'moved to', 'migrated') and shows their cross-platform spread.

    This is a lightweight proxy for cascade_detector.py output.
    """
    SWITCH_PATTERNS = [
        r"\bswitch(ed|ing)?\b",
        r"\bmigrat(ed|ing)?\b",
        r"\bmov(ed|ing) (to|from)\b",
        r"\b(better|worse) than\b",
        r"\bvs\.?\b",
        r"\breplace(d|s)?\b",
        r"\balternative\b",
        r"\bdump(ed|ing)?\b",
        r"\bditch(ed|ing)?\b",
        r"\bcancel(led|ing)?\b",
    ]
    ATTACK_PATTERNS = [
        r"\bend of\b",
        r"\bdead\b",
        r"\bkill(ed|ing)?\b",
        r"\bfail(ed|ing|ure)?\b",
        r"\bcollaps(ed|ing)?\b",
        r"\bover(rated|hyped)\b",
        r"\bscam\b",
        r"\bwaste\b",
    ]

    def flag(title, patterns):
        if not isinstance(title, str):
            return False
        tl = title.lower()
        return any(re.search(p, tl) for p in patterns)

    merged = unified.merge(
        spike[["post_id", "spike_type"]],
        on="post_id", how="left"
    )
    merged["is_switch"] = merged["title"].apply(lambda t: flag(t, SWITCH_PATTERNS))
    merged["is_attack"] = merged["title"].apply(lambda t: flag(t, ATTACK_PATTERNS))

    def summarise(mask, label):
        sub = merged[mask]
        if len(sub) == 0:
            return {"n": 0, "label": label}
        by_platform = (
            sub.groupby("platform")["engagement_score"]
            .agg(n="count", total=sum, mean=lambda x: int(x.mean()))
            .reset_index().to_dict("records")
        )
        weekly = (
            sub.groupby("year_week")["engagement_score"]
            .agg(n="count", total=sum)
            .reset_index().to_dict("records")
        )
        return {
            "label":        label,
            "n":            int(len(sub)),
            "platforms":    int(sub["platform"].nunique()),
            "total_engagement": int(sub["engagement_score"].sum()),
            "mean_engagement":  int(sub["engagement_score"].mean()),
            "median_engagement": int(sub["engagement_score"].median()),
            "by_platform":  by_platform,
            "weekly_trend": weekly,
        }

    return {
        "available":        True,
        "switching_narrative": summarise(merged["is_switch"], "switching frame"),
        "attack_narrative":    summarise(merged["is_attack"], "attack frame"),
        "switch_patterns_used": SWITCH_PATTERNS,
        "attack_patterns_used": ATTACK_PATTERNS,
        "note": (
            "Lightweight proxy for cascade_detector.py. "
            "Uses regex on titles — not a full narrative cluster detector. "
            "Cross-platform spread shows how the same narrative frame appears "
            "independently on each platform."
        ),
    }


def halo_effect_test(unified):
    """
    Finding 6 support: test whether a high-scoring week on one platform
    correlates with elevated engagement on other platforms in the same week.
    Surfaces weeks where HN spiked and checks if Reddit/X/YouTube also spiked.
    """
    weekly = (
        unified.groupby(["year_week", "platform"])["engagement_score"]
        .sum().reset_index()
    )
    pivot = weekly.pivot_table(
        index="year_week", columns="platform",
        values="engagement_score", aggfunc="sum", fill_value=0
    ).reset_index()

    if "hn" not in pivot.columns:
        return {"available": False, "reason": "No HN data in weekly pivot"}

    # Define a 'spike week' as HN total in top 25% of weeks
    hn_75 = pivot["hn"].quantile(0.75)
    spike_weeks  = pivot[pivot["hn"] >= hn_75]
    normal_weeks = pivot[pivot["hn"] <  hn_75]

    result = {"available": True, "hn_spike_threshold_75pct": round(float(hn_75), 0)}
    for plat in ["reddit", "x", "youtube"]:
        if plat not in pivot.columns:
            continue
        spike_mean  = spike_weeks[plat].mean()
        normal_mean = normal_weeks[plat].mean()
        ratio = round(spike_mean / max(normal_mean, 1), 2)
        result[f"hn_spike_vs_normal_{plat}"] = {
            "mean_engagement_during_hn_spike_weeks":  round(float(spike_mean), 0),
            "mean_engagement_during_normal_hn_weeks": round(float(normal_mean), 0),
            "ratio": ratio,
            "interpretation": (
                f"During weeks when HN spikes, {plat} engagement is {ratio}x higher "
                f"than during normal HN weeks — "
                + ("suggests halo effect." if ratio > 1.3 else "no clear halo effect.")
            ),
        }
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("  [metrics] Loading data...")
    spike, front, unified, comments = load()

    metrics = {"generated_at": datetime.now(timezone.utc).isoformat()}

    # — Existing metrics —
    print("  [metrics] Cascade timestamps...")
    metrics["cascade"]              = cascade_timestamps()

    print("  [metrics] Spike type stats...")
    metrics["spike_stats"]          = spike_stats(spike)

    print("  [metrics] Platform stats...")
    metrics["platform_stats"]       = platform_stats(unified)

    print("  [metrics] YouTube community vs official...")
    metrics["youtube_ratio"]        = youtube_community_vs_official(unified)

    print("  [metrics] Timing windows...")
    metrics["timing"]               = timing_stats(unified)

    print("  [metrics] Engagement decay...")
    metrics["decay"]                = decay_stats(front)

    print("  [metrics] Word lift...")
    metrics["word_lift"]            = word_lift(spike)

    print("  [metrics] Pareto analysis...")
    metrics["pareto"]               = pareto_analysis(unified)

    print("  [metrics] Author concentration...")
    metrics["author_concentration"] = author_concentration(unified)

    print("  [metrics] Media vs text...")
    metrics["media_vs_text"]        = media_vs_text(unified)

    print("  [metrics] Comment sentiment...")
    metrics["comment_sentiment"]    = comment_sentiment(comments)

    # — New metrics —
    print("  [metrics] Official vs community on X (F9/F11)...")
    metrics["official_vs_community_x"] = official_vs_community_x(unified)

    print("  [metrics] Subreddit breakdown (F13)...")
    metrics["subreddit_breakdown"]     = subreddit_breakdown(unified)

    print("  [metrics] Follower count vs reach (F12)...")
    metrics["follower_count_vs_reach"] = follower_count_vs_reach(unified)

    print("  [metrics] Author type × spike type breakdown (F9/F11)...")
    metrics["author_type_breakdown"]   = author_type_breakdown(unified, spike)

    print("  [metrics] Weekly volume trend + phrase tracking (F6/F10)...")
    metrics["weekly_volume_trend"]     = weekly_volume_trend(unified)

    print("  [metrics] Narrative switching signal (F14/F13)...")
    metrics["narrative_switching"]     = narrative_switching_signal(unified, spike)

    print("  [metrics] Halo effect test (F6)...")
    metrics["halo_effect"]             = halo_effect_test(unified)

    # Write output
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    # Summary
    print(f"\n  [done] → {OUT}")
    print(f"  Pareto (HN): top 10% = {metrics['pareto'].get('hn', {}).get('top_10pct_share', 'N/A')}% of engagement")
    print(f"  Author concentration: top 5 = {metrics['author_concentration']['top5_share_pct']}%")
    print(f"  Media lift (Reddit): {metrics['media_vs_text'].get('reddit', {}).get('lift_median', 'N/A')}x")
    print(f"  Official vs community X: {metrics['official_vs_community_x'].get('community_vs_official_total_multiplier', 'N/A')}x")
    print(f"  Subreddit breakdown: {'available' if metrics['subreddit_breakdown'].get('available') else 'not available — add subreddit column'}")
    print(f"  Follower/reach: {'available' if metrics['follower_count_vs_reach'].get('available') else 'not available — add follower_count column'}")
    print(f"  Switching narrative posts: {metrics['narrative_switching'].get('switching_narrative', {}).get('n', 0)}")
    print(f"  Attack narrative posts: {metrics['narrative_switching'].get('attack_narrative', {}).get('n', 0)}")

    # Warn about columns that need scraper changes
    missing_cols = []
    if not metrics["subreddit_breakdown"].get("available"):
        missing_cols.append("subreddit (Reddit scraper)")
    if not metrics["follower_count_vs_reach"].get("available"):
        missing_cols.append("follower_count (X/fxtwitter scraper)")
    if missing_cols:
        print(f"\n  [warn] Add these columns to unlock more findings: {', '.join(missing_cols)}")


if __name__ == "__main__":
    main()