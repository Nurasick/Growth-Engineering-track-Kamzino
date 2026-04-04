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
