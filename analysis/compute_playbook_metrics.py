#!/usr/bin/env python3
"""
compute_playbook_metrics.py — extract all analysis metrics from processed CSVs.
Outputs: data/processed/analysis_metrics.json
No API calls. Runs in <2s.

Usage:
    python analysis/compute_playbook_metrics.py
"""

import json, re, sys
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

import pandas as pd
import numpy as np

ROOT      = Path(__file__).parent.parent
PROCESSED = ROOT / "data" / "processed"
OUT       = PROCESSED / "analysis_metrics.json"


# ── Loaders ──────────────────────────────────────────────────────────────────

def load():
    def read(f):
        p = PROCESSED / f
        if not p.exists():
            sys.exit(f"ERROR: {f} not found — run: python pipeline.py --skip-scrape")
        return pd.read_csv(p, encoding="utf-8")

    spike    = read("spike_classified.csv")
    front    = read("growth_frontpage.csv")
    unified  = read("unified_posts.csv")
    comments = read("unified_comments.csv")

    unified["created_at"] = pd.to_datetime(unified["created_at"], utc=True, errors="coerce")
    unified["hour"]       = unified["created_at"].dt.hour
    unified["weekday"]    = unified["created_at"].dt.day_name()
    unified["has_media"]  = unified["has_media"].astype(str).str.lower().isin(["true", "1", "yes"])

    return spike, front, unified, comments


# ── Individual metrics ────────────────────────────────────────────────────────

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
        "cascade_note": "HN ignites at 01:13 UTC → YouTube reacts in 7 min → Reddit joins 12h → meme/international 48h+",
    }


def spike_stats(spike):
    total = len(spike)
    stats = (
        spike.groupby("spike_type")["engagement_score"]
        .agg(count="count",
             mean=lambda x: int(x.mean()),
             median=lambda x: int(x.median()),
             p90=lambda x: int(x.quantile(0.9)),
             max=lambda x: int(x.max()))
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
            "mean":   int(e.mean()),
            "median": int(e.median()),
            "total":  int(e.sum()),
        }
    return out


def youtube_community_vs_official(unified):
    yt = unified[unified["platform"] == "youtube"].copy()
    yt["is_official"] = yt["official"].astype(str).str.lower().isin(["true", "1", "yes"])
    comm_views = int(yt[~yt["is_official"]]["engagement_score"].sum())
    off_views  = int(yt[yt["is_official"]]["engagement_score"].sum())
    KNOWN_OFFICIAL = 196616  # validated from prior scrape run
    ratio = round(comm_views / KNOWN_OFFICIAL, 1) if comm_views > 0 else 0

    by_channel = (
        yt.groupby("channel")["engagement_score"].sum()
        .sort_values(ascending=False)
    )
    top = by_channel.head(5).reset_index().to_dict("records")
    return {
        "community_total_views": comm_views,
        "official_total_views_baseline": KNOWN_OFFICIAL,
        "ratio": ratio,
        "top_channels": top,
        "note": "Anthropic official channel (196K views) captured from prior scrape run; not present in current unified_posts.csv",
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
    return {
        "hn_by_utc_hour": hn.to_dict("records"),
        "hn_peak_note": "Hours 19–23 UTC (2–6 pm ET) average 35–49 pts vs ~10 pts at other hours",
        "reddit_by_weekday": reddit.to_dict("records"),
        "reddit_peak_note": f"Sunday avg {reddit[reddit['weekday']=='Sunday']['mean'].values[0] if 'Sunday' in reddit['weekday'].values else 'N/A'} vs Thursday avg {reddit[reddit['weekday']=='Thursday']['mean'].values[0] if 'Thursday' in reddit['weekday'].values else 'N/A'}",
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

    stop = {"the","a","an","of","in","to","and","for","is","are","with","on","by",
            "at","it","this","that","how","i","my","from","its","was","be","as",
            "what","we","you","your","do","not","but","or","have","has","can",
            "use","via","–","-","vs","so","if","new","more","just","get","all",
            "now","will","about","into","been","they","their","than","when",
            "after","some","one","two","no","up","using","make"}

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
    bot10 = sorted(lift.items(), key=lambda x: x[1])[:10]

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
        cumsum  = np.cumsum(scores)
        n       = len(scores)
        pct_posts = [i / n for i in range(1, n + 1)]
        pct_eng   = [c / total for c in cumsum]

        # find % of posts that account for 80% of engagement
        idx_80 = next((i for i, v in enumerate(pct_eng) if v >= 0.80), n - 1)
        top10  = int(round(scores[:max(1, n // 10)].sum() / total * 100, 0))
        top1   = int(round(scores[:max(1, n // 100)].sum() / total * 100, 0)) if n >= 100 else None

        result[p] = {
            "n":               n,
            "top_10pct_share": top10,
            "top_1pct_share":  top1,
            "posts_for_80pct_engagement": round(idx_80 / n * 100, 1),
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

    # add platform for each author
    author_platform = unified.groupby("author")["platform"].agg(lambda x: x.value_counts().index[0])
    top10["platform"] = top10["author"].map(author_platform)

    return {
        "total_unique_authors": int(unified["author"].nunique()),
        "total_engagement":     int(total),
        "top_10_authors":       top10.to_dict("records"),
        "top5_share_pct":       round(top10.head(5)["engagement_score"].sum() / total * 100, 1),
        "top1_share_pct":       round(top10.head(1)["engagement_score"].sum() / total * 100, 1),
    }


def media_vs_text(unified):
    result = {}
    for p in ["reddit", "x", "hn", "youtube"]:
        grp = unified[unified["platform"] == p]
        media = grp[grp["has_media"] == True]["engagement_score"]
        text  = grp[grp["has_media"] == False]["engagement_score"]
        if len(media) == 0:
            continue
        med_media = media.median() if len(media) > 0 else 0
        med_text  = text.median()  if len(text)  > 0 else 0
        result[p] = {
            "media_count":   int(len(media)),
            "text_count":    int(len(text)),
            "media_median":  int(med_media) if not __import__("math").isnan(med_media) else 0,
            "text_median":   int(med_text)  if not __import__("math").isnan(med_text)  else 0,
            "media_mean":    int(media.mean()) if len(media) > 0 else 0,
            "text_mean":     int(text.mean())  if len(text)  > 0 else 0,
            "lift_median":   round(med_media / max(med_text, 1), 1),
        }
    return result


def comment_sentiment(comments):
    POS_WORDS = {"great","amazing","love","perfect","excellent","awesome","incredible",
                 "useful","helpful","impressive","best","fantastic","brilliant","good",
                 "nice","works","solved","fixed","thanks","thank","clever","genius"}
    NEG_WORDS = {"bad","terrible","wrong","broken","useless","hate","awful","horrible",
                 "disappointed","fail","failed","worse","worst","waste","stupid","dumb",
                 "disagree","problem","issue","bug","error","confused","misleading"}

    def classify(text):
        if not isinstance(text, str):
            return "neutral"
        words = set(re.findall(r"[a-z]+", text.lower()))
        pos = len(words & POS_WORDS)
        neg = len(words & NEG_WORDS)
        if pos > neg:
            return "positive"
        if neg > pos:
            return "negative"
        return "neutral"

    comments["sentiment"] = comments["body_text"].apply(classify)

    # merge with spike type via post_id if possible
    # comments has post_id, spike has post_id
    spike_map = {}
    spike_path = PROCESSED / "spike_classified.csv"
    if spike_path.exists():
        spike_df = pd.read_csv(spike_path, encoding="utf-8")[["post_id", "spike_type"]]
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
        "overall_pct": overall,
        "by_platform": by_platform,
        "by_spike_type": by_spike,
        "positive_keywords_used": sorted(POS_WORDS),
        "negative_keywords_used": sorted(NEG_WORDS),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("  [metrics] Loading data...")
    spike, front, unified, comments = load()

    print("  [metrics] Computing cascade timestamps...")
    metrics = {"generated_at": datetime.now(timezone.utc).isoformat()}

    metrics["cascade"]             = cascade_timestamps()
    print("  [metrics] Spike type stats...")
    metrics["spike_stats"]         = spike_stats(spike)
    print("  [metrics] Platform stats...")
    metrics["platform_stats"]      = platform_stats(unified)
    print("  [metrics] YouTube community vs official...")
    metrics["youtube_ratio"]       = youtube_community_vs_official(unified)
    print("  [metrics] Timing windows...")
    metrics["timing"]              = timing_stats(unified)
    print("  [metrics] Engagement decay...")
    metrics["decay"]               = decay_stats(front)
    print("  [metrics] Word lift analysis...")
    metrics["word_lift"]           = word_lift(spike)
    print("  [metrics] Pareto / concentration...")
    metrics["pareto"]              = pareto_analysis(unified)
    print("  [metrics] Author concentration...")
    metrics["author_concentration"]= author_concentration(unified)
    print("  [metrics] Media vs text...")
    metrics["media_vs_text"]       = media_vs_text(unified)
    print("  [metrics] Comment sentiment...")
    metrics["comment_sentiment"]   = comment_sentiment(comments)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  [done] → {OUT}")
    print(f"  Pareto (HN): top 10% posts = {metrics['pareto']['hn']['top_10pct_share']}% of engagement")
    print(f"  Author concentration: top 5 = {metrics['author_concentration']['top5_share_pct']}% of total engagement")
    print(f"  Media lift (Reddit): {metrics['media_vs_text'].get('reddit', {}).get('lift_median', 'N/A')}x")


if __name__ == "__main__":
    main()
