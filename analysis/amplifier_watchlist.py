#!/usr/bin/env python3
"""
Amplifier Watchlist — auto-discovers high-leverage X/Twitter accounts from scraped data.

Pipeline role (Step 3.5): runs after x_scraper.py, feeds handles back into next X scrape.

Scoring formula:
  engagement_rate     = likes / views          (audience quality signal)
  amplification_mult  = views / followers      (reach leverage)
  frequency_bonus     = log(1 + tweet_count)   (consistency)
  composite_score     = ER * amp_mult * frequency_bonus

Automation: FULLY AUTOMATED after initial bootstrap seed list.
  Reads  → data/raw/x_case_raw.csv
  Writes → data/amplifier_watchlist.csv  (consumed by x_scraper.py on next run)
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT     = Path(__file__).parent.parent
RAW_DIR       = REPO_ROOT / "data" / "raw"
INPUT_CSV     = RAW_DIR / "x_case_raw.csv"
WATCHLIST_CSV = REPO_ROOT / "data" / "amplifier_watchlist.csv"

OFFICIAL_HANDLES = {"anthropicai", "claudeai"}

# Thresholds — viral tweets naturally have 0.1-0.5% ER (views is huge denominator)
MIN_ENGAGEMENT_RATE    = 0.001  # 0.1% — filters pure spam/bots
MIN_AMPLIFICATION_MULT = 0.1    # views >= 10% of follower count
MIN_FOLLOWERS          = 500
MIN_VIEWS_TOTAL        = 5_000

BOOTSTRAP_HANDLES = [
    "AnthropicAI", "ClaudeAI", "sama", "karpathy", "swyx", "goodside",
    "simonw", "amasad", "ilyasut", "ycombinator", "notthreadguy",
    "aakashgupta", "trq212", "kimmonismus",
]


def score_author(stats: dict) -> float:
    views, likes, followers, tweets = (
        stats["total_views"], stats["total_likes"],
        stats["followers"], stats["tweet_count"],
    )
    if views == 0 or followers == 0:
        return 0.0
    return (likes / views) * (views / followers) * math.log1p(tweets)


def _tier(score: float, followers: int) -> str:
    if score > 1.0:   return "tier1_high_leverage"
    if score > 0.2:   return "tier2_solid"
    if followers > 100_000: return "tier3_reach"
    return "tier4_niche"


def build_watchlist(input_path: Path = INPUT_CSV) -> list[dict]:
    if not input_path.exists():
        print(f"  [skip] {input_path} not found")
        return []

    authors: dict[str, dict] = defaultdict(lambda: {
        "total_views": 0, "total_likes": 0, "total_retweets": 0,
        "followers": 0, "tweet_count": 0, "author_name": "", "sample_tweet": "",
    })

    with input_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            handle = (row.get("author_handle") or "").strip().lower()
            if not handle or handle in OFFICIAL_HANDLES:
                continue
            d = authors[handle]
            d["total_views"]    += int(row.get("views", 0) or 0)
            d["total_likes"]    += int(row.get("likes", 0) or 0)
            d["total_retweets"] += int(row.get("retweets", 0) or 0)
            d["tweet_count"]    += 1
            d["followers"] = max(d["followers"], int(row.get("author_followers", 0) or 0))
            d["author_name"] = row.get("author_name", "") or d["author_name"]
            if not d["sample_tweet"]:
                d["sample_tweet"] = (row.get("text") or "")[:80]

    candidates = []
    for handle, stats in authors.items():
        views, likes, followers = stats["total_views"], stats["total_likes"], stats["followers"]
        if followers < MIN_FOLLOWERS or views < MIN_VIEWS_TOTAL:
            continue
        er   = likes / views if views > 0 else 0
        mult = views / followers if followers > 0 else 0
        if er < MIN_ENGAGEMENT_RATE or mult < MIN_AMPLIFICATION_MULT:
            continue
        composite = score_author(stats)
        candidates.append({
            "handle":             handle,
            "author_name":        stats["author_name"],
            "followers":          followers,
            "tweet_count":        stats["tweet_count"],
            "total_views":        views,
            "total_likes":        likes,
            "total_retweets":     stats["total_retweets"],
            "engagement_rate":    round(er, 4),
            "amplification_mult": round(mult, 2),
            "composite_score":    round(composite, 4),
            "tier":               _tier(composite, followers),
            "sample_tweet":       stats["sample_tweet"],
            "added_at":           datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "source":             "auto_scored",
        })

    scored_handles = {c["handle"] for c in candidates}
    for h in BOOTSTRAP_HANDLES:
        if h.lower() not in scored_handles and h.lower() not in OFFICIAL_HANDLES:
            candidates.append({
                "handle": h.lower(), "author_name": h,
                "followers": 0, "tweet_count": 0, "total_views": 0,
                "total_likes": 0, "total_retweets": 0,
                "engagement_rate": 0, "amplification_mult": 0,
                "composite_score": 0, "tier": "bootstrap",
                "sample_tweet": "",
                "added_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "source": "manual_bootstrap",
            })

    return sorted(candidates, key=lambda x: x["composite_score"], reverse=True)


def save_watchlist(rows: list[dict], path: Path = WATCHLIST_CSV) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    print(f"  [amplifier] scoring authors from {INPUT_CSV.name}")
    rows = build_watchlist()
    save_watchlist(rows)
    auto  = sum(1 for r in rows if r["source"] == "auto_scored")
    boot  = sum(1 for r in rows if r["source"] == "manual_bootstrap")
    print(f"  [amplifier] {auto} auto-scored + {boot} bootstrap = {len(rows)} handles → {WATCHLIST_CSV.name}")
    if rows and rows[0]["source"] == "auto_scored":
        top = rows[0]
        print(f"  [amplifier] top: @{top['handle']}  score={top['composite_score']}  "
              f"amp={top['amplification_mult']}x  ER={top['engagement_rate']:.1%}")


if __name__ == "__main__":
    main()
