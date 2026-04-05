"""
Charts router — aggregated analytics for frontend charts.
"""

import csv
import glob
import os
from collections import defaultdict
from fastapi import APIRouter, HTTPException

router = APIRouter()

DATA_RAW = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")


def _latest_csv(prefix: str) -> str | None:
    pattern = os.path.join(DATA_RAW, f"{prefix}_*.csv")
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None


def _load_hn_by_day() -> dict[str, list[dict]]:
    """Return HN stories grouped by day, sorted by points desc."""
    path = _latest_csv("hn_items")
    if not path:
        return {}

    by_day: dict[str, list[dict]] = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = (row.get("created_at") or "")[:10]
            if not date:
                continue
            try:
                points = int(row.get("points") or 0)
            except ValueError:
                points = 0
            by_day[date].append(
                {
                    "title": (row.get("title") or "").strip(),
                    "points": points,
                    "url": (row.get("url") or "").strip(),
                    "comments": int(row.get("num_comments") or 0),
                }
            )

    # sort each day's list by points descending
    for date in by_day:
        by_day[date].sort(key=lambda x: x["points"], reverse=True)

    return dict(by_day)


@router.get("/youtube-engagement")
def youtube_engagement():
    """
    Return YouTube engagement rate grouped by day, enriched with top HN stories
    for each day so the frontend can show what was happening on HackerNews.
    """
    yt_path = _latest_csv("youtube_videos")
    if not yt_path:
        raise HTTPException(status_code=404, detail="No YouTube CSV found")

    # ── YouTube buckets ──────────────────────────────────────────────────────
    buckets: dict[str, dict] = defaultdict(
        lambda: {"rates": [], "views": 0, "likes": 0, "comments": 0, "count": 0}
    )

    with open(yt_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                published = row.get("published_at", "")
                if not published or len(published) < 10:
                    continue
                period = published[:10]

                views = int(row.get("view_count") or 0)
                likes = int(row.get("like_count") or 0)
                comments = int(row.get("comment_count") or 0)

                if views <= 0:
                    continue

                rate = (likes + comments) / views * 100
                b = buckets[period]
                b["rates"].append(rate)
                b["views"] += views
                b["likes"] += likes
                b["comments"] += comments
                b["count"] += 1
            except (ValueError, KeyError):
                continue

    if not buckets:
        raise HTTPException(status_code=404, detail="No valid YouTube data found")

    # ── HN data ──────────────────────────────────────────────────────────────
    hn_by_day = _load_hn_by_day()

    # ── Assemble response ────────────────────────────────────────────────────
    data = []
    for period in sorted(buckets.keys()):
        b = buckets[period]
        rates_sorted = sorted(b["rates"])
        avg_rate = sum(b["rates"]) / len(b["rates"]) if b["rates"] else 0
        median_rate = rates_sorted[len(rates_sorted) // 2]

        day_hn = hn_by_day.get(period, [])
        top_hn = day_hn[:3]  # top 3 stories by points
        hn_total_score = sum(s["points"] for s in day_hn)

        data.append(
            {
                "period": period,
                "avg_engagement_rate": round(avg_rate, 3),
                "median_engagement_rate": round(median_rate, 3),
                "video_count": b["count"],
                "total_views": b["views"],
                "total_likes": b["likes"],
                "total_comments": b["comments"],
                # HN context
                "hn_item_count": len(day_hn),
                "hn_total_score": hn_total_score,
                "hn_top_stories": top_hn,
            }
        )

    all_rates = [r for b in buckets.values() for r in b["rates"]]
    summary = {
        "total_videos": sum(b["count"] for b in buckets.values()),
        "overall_avg_engagement_rate": round(
            sum(all_rates) / len(all_rates) if all_rates else 0, 3
        ),
        "date_range": f"{data[0]['period']} → {data[-1]['period']}" if data else "",
        "source_file": os.path.basename(yt_path),
    }

    return {"data": data, "summary": summary}


@router.get("/reddit-engagement")
def reddit_engagement():
    """
    Return Reddit engagement (avg score + comments) grouped by ISO week,
    enriched with top HN stories for that week.
    Reddit has no view count, so primary metric is avg upvote score per post.
    """
    reddit_path = _latest_csv("reddit_posts")
    if not reddit_path:
        raise HTTPException(status_code=404, detail="No Reddit CSV found")

    # ── Reddit buckets by ISO week ───────────────────────────────────────────
    from datetime import date as date_cls

    buckets: dict[str, dict] = defaultdict(
        lambda: {"scores": [], "comments": [], "eng": [], "total_score": 0, "total_comments": 0,
                 "count": 0, "top_posts": []}
    )

    with open(reddit_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                raw_date = (row.get("created_utc") or row.get("created_at") or "")[:10]
                if not raw_date or len(raw_date) < 10:
                    continue
                d = date_cls.fromisoformat(raw_date)
                iso = d.isocalendar()
                period = f"{iso[0]}-W{iso[1]:02d}"  # "2026-W14"

                score    = int(row.get("score") or 0)
                comments = int(row.get("num_comments") or 0)
                ratio    = float(row.get("upvote_ratio") or 0)

                # Weighted engagement: comments require writing = 3× upvote intent
                eng = score + (comments * 3)

                b = buckets[period]
                b["scores"].append(score)
                b["comments"].append(comments)
                b["eng"].append(eng)
                b["total_score"]    += score
                b["total_comments"] += comments
                b["count"]          += 1
                b["top_posts"].append({
                    "title":      (row.get("title") or "").strip(),
                    "score":      score,
                    "comments":   comments,
                    "engagement": eng,
                    "ratio":      ratio,
                    "url":        (row.get("url") or row.get("permalink") or "").strip(),
                    "subreddit":  (row.get("subreddit") or "").strip(),
                    "date":       raw_date,
                })
            except (ValueError, KeyError):
                continue

    if not buckets:
        raise HTTPException(status_code=404, detail="No valid Reddit data found")

    # ── HN data — aggregate by week ─────────────────────────────────────────
    hn_by_day = _load_hn_by_day()
    hn_by_week: dict[str, dict] = defaultdict(
        lambda: {"stories": [], "total_score": 0, "item_count": 0}
    )
    for day, stories in hn_by_day.items():
        try:
            d = date_cls.fromisoformat(day)
            iso = d.isocalendar()
            week = f"{iso[0]}-W{iso[1]:02d}"
        except ValueError:
            continue
        hw = hn_by_week[week]
        hw["stories"].extend(stories)
        hw["total_score"] += sum(s["points"] for s in stories)
        hw["item_count"]  += len(stories)

    for week in hn_by_week:
        hn_by_week[week]["stories"].sort(key=lambda x: x["points"], reverse=True)

    # ── Assemble response ────────────────────────────────────────────────────
    data = []
    for period in sorted(buckets.keys()):
        b = buckets[period]
        scores_sorted = sorted(b["scores"])
        eng_sorted    = sorted(b["eng"])
        avg_score     = sum(b["scores"]) / len(b["scores"]) if b["scores"] else 0
        median_score  = scores_sorted[len(scores_sorted) // 2]
        avg_comments  = sum(b["comments"]) / len(b["comments"]) if b["comments"] else 0
        avg_eng       = sum(b["eng"]) / len(b["eng"]) if b["eng"] else 0
        median_eng    = eng_sorted[len(eng_sorted) // 2]

        # Rank top posts by engagement (score + comments×3), not just score
        top_posts = sorted(b["top_posts"], key=lambda x: x["engagement"], reverse=True)[:3]

        hw = hn_by_week.get(period, {})
        data.append({
            "period":          period,
            "avg_score":       round(avg_score, 1),
            "median_score":    round(median_score, 1),
            "avg_engagement":  round(avg_eng, 1),
            "median_engagement": round(median_eng, 1),
            "avg_comments":    round(avg_comments, 1),
            "post_count":      b["count"],
            "total_score":     b["total_score"],
            "total_comments":  b["total_comments"],
            "top_posts":       top_posts,
            "hn_item_count":   hw.get("item_count", 0),
            "hn_total_score":  hw.get("total_score", 0),
            "hn_top_stories":  hw.get("stories", [])[:3],
        })

    all_scores = [s for b in buckets.values() for s in b["scores"]]
    all_eng    = [e for b in buckets.values() for e in b["eng"]]
    summary = {
        "total_posts":           sum(b["count"] for b in buckets.values()),
        "overall_avg_score":     round(sum(all_scores) / len(all_scores) if all_scores else 0, 1),
        "overall_avg_engagement": round(sum(all_eng) / len(all_eng) if all_eng else 0, 1),
        "date_range":            f"{data[0]['period']} → {data[-1]['period']}" if data else "",
        "source_file":           os.path.basename(reddit_path),
    }

    return {"data": data, "summary": summary}


@router.get("/x-engagement")
def x_engagement():
    """
    Return X/Twitter engagement (avg views) grouped by ISO week.
    Merges all x_playwright_*.csv and x_historical_*.csv files (deduped by tweet_id).
    """
    from datetime import datetime, date as date_cls

    x_files: list[str] = []
    for prefix in ("x_playwright", "x_historical", "x_case"):
        pattern = os.path.join(DATA_RAW, f"{prefix}*.csv")
        x_files.extend(glob.glob(pattern))

    if not x_files:
        raise HTTPException(status_code=404, detail="No X/Twitter CSV found")

    # Dedupe by tweet_id
    seen_ids: set[str] = set()
    rows_all: list[dict] = []

    for path in sorted(x_files):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = (row.get("tweet_id") or "").strip()
                if tid and tid in seen_ids:
                    continue
                if tid:
                    seen_ids.add(tid)
                rows_all.append(row)

    # Twitter date format: "Wed Jan 29 03:27:51 +0000 2025"
    _TW_FMT = "%a %b %d %H:%M:%S %z %Y"

    buckets: dict[str, dict] = defaultdict(
        lambda: {"views": [], "eng": [], "eng_rates": [], "likes": [], "retweets": [], "replies": [], "bookmarks": [], "count": 0, "top_tweets": []}
    )

    for row in rows_all:
        raw_date = (row.get("created_at") or "").strip()
        if not raw_date:
            continue
        period = None
        try:
            dt = datetime.strptime(raw_date, _TW_FMT)
            iso = dt.isocalendar()
            period = f"{iso[0]}-W{iso[1]:02d}"
        except ValueError:
            plain = raw_date[:10]
            if len(plain) >= 10:
                try:
                    d = date_cls.fromisoformat(plain)
                    iso = d.isocalendar()
                    period = f"{iso[0]}-W{iso[1]:02d}"
                except ValueError:
                    pass
        if period is None:
            continue

        try:
            views     = int(row.get("views") or 0)
            likes     = int(row.get("likes") or 0)
            retweets  = int(row.get("retweets") or 0)
            replies   = int(row.get("replies") or 0)
            bookmarks = int(row.get("bookmarks") or 0)
        except ValueError:
            continue

        # Weighted engagement: replies/RTs require more intent than likes
        eng = likes + (retweets * 2) + (replies * 2) + bookmarks
        eng_rate = (eng / views * 100) if views > 0 else 0

        b = buckets[period]
        b["views"].append(views)
        b["eng"].append(eng)
        b["likes"].append(likes)
        b["retweets"].append(retweets)
        b["replies"].append(replies)
        b["bookmarks"].append(bookmarks)
        if views > 0:
            b["eng_rates"].append(eng_rate)
        b["count"] += 1
        b["top_tweets"].append({
            "text":          (row.get("text") or "").strip()[:280],
            "author_handle": (row.get("author_handle") or "").strip(),
            "views":         views,
            "engagement":    eng,
            "eng_rate":      round(eng_rate, 3),
            "likes":         likes,
            "retweets":      retweets,
            "url":           (row.get("url") or "").strip(),
        })

    if not buckets:
        raise HTTPException(status_code=404, detail="No valid X/Twitter data found")

    data = []
    for period in sorted(buckets.keys()):
        b = buckets[period]
        eng_sorted   = sorted(b["eng"])
        avg_eng      = sum(b["eng"]) / len(b["eng"]) if b["eng"] else 0
        median_eng   = eng_sorted[len(eng_sorted) // 2]
        avg_eng_rate = sum(b["eng_rates"]) / len(b["eng_rates"]) if b["eng_rates"] else 0
        avg_views    = sum(b["views"]) / len(b["views"]) if b["views"] else 0
        # Sort top tweets by engagement score (not raw views)
        top_tweets   = sorted(b["top_tweets"], key=lambda x: x["engagement"], reverse=True)[:3]
        data.append({
            "period":           period,
            "avg_engagement":   round(avg_eng, 1),
            "median_engagement": round(median_eng, 1),
            "avg_engagement_rate": round(avg_eng_rate, 3),
            "avg_views":        round(avg_views, 0),
            "total_views":      sum(b["views"]),
            "total_likes":      sum(b["likes"]),
            "total_retweets":   sum(b["retweets"]),
            "tweet_count":      b["count"],
            "top_tweets":       top_tweets,
        })

    all_eng   = [v for b in buckets.values() for v in b["eng"]]
    all_rates = [v for b in buckets.values() for v in b["eng_rates"]]
    summary = {
        "total_tweets":          sum(b["count"] for b in buckets.values()),
        "overall_avg_engagement": round(sum(all_eng) / len(all_eng) if all_eng else 0, 1),
        "overall_avg_eng_rate":  round(sum(all_rates) / len(all_rates) if all_rates else 0, 3),
        "date_range":            f"{data[0]['period']} → {data[-1]['period']}" if data else "",
        "source_files":          [os.path.basename(p) for p in sorted(x_files)],
    }

    return {"data": data, "summary": summary}
