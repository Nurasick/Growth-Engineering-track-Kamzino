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


def _latest_youtube_csv() -> str | None:
    pattern = os.path.join(DATA_RAW, "youtube_videos_*.csv")
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None


@router.get("/youtube-engagement")
def youtube_engagement():
    """
    Return YouTube engagement rate (likes + comments / views * 100) grouped by month.
    Engagement rate per video: (like_count + comment_count) / view_count * 100
    """
    path = _latest_youtube_csv()
    if not path:
        raise HTTPException(status_code=404, detail="No YouTube CSV found")

    # period -> {engagement_rates, total_views, total_likes, total_comments, count}
    buckets: dict[str, dict] = defaultdict(
        lambda: {"rates": [], "views": 0, "likes": 0, "comments": 0, "count": 0}
    )

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                published = row.get("published_at", "")
                if not published or len(published) < 10:
                    continue
                period = published[:10]  # "YYYY-MM-DD"

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

    data = []
    for period in sorted(buckets.keys()):
        b = buckets[period]
        avg_rate = sum(b["rates"]) / len(b["rates"]) if b["rates"] else 0
        data.append(
            {
                "period": period,
                "avg_engagement_rate": round(avg_rate, 3),
                "median_engagement_rate": round(
                    sorted(b["rates"])[len(b["rates"]) // 2], 3
                ),
                "video_count": b["count"],
                "total_views": b["views"],
                "total_likes": b["likes"],
                "total_comments": b["comments"],
            }
        )

    all_rates = [r for b in buckets.values() for r in b["rates"]]
    summary = {
        "total_videos": sum(b["count"] for b in buckets.values()),
        "overall_avg_engagement_rate": round(
            sum(all_rates) / len(all_rates) if all_rates else 0, 3
        ),
        "date_range": f"{data[0]['period']} → {data[-1]['period']}" if data else "",
        "source_file": os.path.basename(path),
    }

    return {"data": data, "summary": summary}
