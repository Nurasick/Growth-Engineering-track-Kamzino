"""
GET /analytics/summary   — top posts, spike breakdown, platform stats, creators, weekly trend
GET /analytics/feed      — velocity-ranked posts (paginated)
GET /analytics/alerts    — posts with velocity > threshold, age < 12h
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

REPO_ROOT     = Path(__file__).parent.parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"


def _load() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load spike_classified and growth_frontpage. Raise 503 if not ready."""
    classified_path = PROCESSED_DIR / "spike_classified.csv"
    frontpage_path  = PROCESSED_DIR / "growth_frontpage.csv"

    if not classified_path.exists() or not frontpage_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Processed data not found. Run the pipeline first (pipeline/analyze)."
        )

    classified = pd.read_csv(classified_path)
    classified["created_at"] = pd.to_datetime(classified["created_at"], utc=True, errors="coerce")

    frontpage  = pd.read_csv(frontpage_path)
    return classified, frontpage


@router.get("/summary")
def summary():
    """Full analytics summary: spike breakdown, platform stats, top creators, weekly trend."""
    classified, frontpage = _load()

    now = datetime.now(timezone.utc)

    # ── Spike type breakdown ────────────────────────────────────────────────
    spike_stats = (
        classified.groupby("spike_type")["engagement_score"]
        .agg(count="count", mean="mean", median="median")
        .reset_index()
    )
    total_posts = len(classified)
    spike_breakdown = [
        {
            "spike_type":  row["spike_type"],
            "count":       int(row["count"]),
            "pct":         round(row["count"] / total_posts * 100, 1),
            "mean_engagement":   round(row["mean"]),
            "median_engagement": round(row["median"]),
        }
        for _, row in spike_stats.sort_values("count", ascending=False).iterrows()
    ]

    # ── Platform breakdown ──────────────────────────────────────────────────
    platform_stats = (
        classified.groupby("platform")["engagement_score"]
        .agg(count="count", mean="mean", median="median")
        .reset_index()
    )
    platform_breakdown = [
        {
            "platform":          row["platform"],
            "count":             int(row["count"]),
            "mean_engagement":   round(row["mean"]),
            "median_engagement": round(row["median"]),
        }
        for _, row in platform_stats.sort_values("count", ascending=False).iterrows()
    ]

    # ── Weekly trend (posts per week per platform) ──────────────────────────
    dated = classified.dropna(subset=["created_at"]).copy()
    dated["week"] = dated["created_at"].dt.to_period("W").dt.start_time.dt.strftime("%Y-%m-%d")
    weekly = (
        dated.groupby(["week", "platform"])
        .size()
        .reset_index(name="count")
        .sort_values("week")
    )
    # Pivot for frontend convenience
    weeks   = sorted(weekly["week"].unique())
    platforms = sorted(weekly["platform"].unique())
    weekly_pivot = {
        "weeks": weeks,
        "series": {
            p: [
                int(weekly[(weekly["week"] == w) & (weekly["platform"] == p)]["count"].sum())
                for w in weeks
            ]
            for p in platforms
        },
    }

    # ── Top creators (by total engagement) ─────────────────────────────────
    top_creators = (
        classified[classified["author"].notna() & (classified["author"] != "")]
        .groupby(["author", "platform"])
        .agg(posts=("engagement_score", "count"), total_engagement=("engagement_score", "sum"))
        .reset_index()
        .sort_values("total_engagement", ascending=False)
        .head(10)
    )
    creators_list = [
        {
            "author":           row["author"],
            "platform":         row["platform"],
            "posts":            int(row["posts"]),
            "total_engagement": int(row["total_engagement"]),
        }
        for _, row in top_creators.iterrows()
    ]

    # ── Dataset stats ───────────────────────────────────────────────────────
    date_min = classified["created_at"].min()
    date_max = classified["created_at"].max()

    return {
        "total_posts":        total_posts,
        "date_range": {
            "from": date_min.isoformat() if pd.notna(date_min) else None,
            "to":   date_max.isoformat() if pd.notna(date_max) else None,
        },
        "spike_breakdown":    spike_breakdown,
        "platform_breakdown": platform_breakdown,
        "weekly_trend":       weekly_pivot,
        "top_creators":       creators_list,
    }


@router.get("/feed")
def feed(
    limit: int = Query(default=50, le=200),
    platform: str = Query(default="all"),
    spike_type: str = Query(default="all"),
):
    """Velocity-ranked post feed. Filter by platform or spike_type."""
    classified, frontpage = _load()

    # Merge velocity from frontpage into classified
    velocity_map = frontpage.set_index(
        frontpage.apply(lambda r: f"{r.get('platform','')}_{r.get('title','')}", axis=1)
    )["velocity"].to_dict() if "velocity" in frontpage.columns else {}

    df = classified.copy()
    if "velocity" not in df.columns:
        fp_cols = ["title", "platform", "velocity", "rank", "age_hours"]
        available = [c for c in fp_cols if c in frontpage.columns]
        df = df.merge(
            frontpage[available].drop_duplicates(subset=["title", "platform"]),
            on=["title", "platform"],
            how="left",
        )

    if platform != "all":
        df = df[df["platform"] == platform]
    if spike_type != "all":
        df = df[df["spike_type"] == spike_type]

    sort_col = "velocity" if "velocity" in df.columns else "engagement_score"
    df = df.sort_values(sort_col, ascending=False).head(limit)

    posts = []
    for _, row in df.iterrows():
        posts.append({
            "post_id":        str(row.get("post_id", "")),
            "title":          str(row.get("title", "")) if pd.notna(row.get("title")) else "",
            "platform":       str(row.get("platform", "")),
            "author":         str(row.get("author", "")) if pd.notna(row.get("author")) else "",
            "url":            str(row.get("url", "")) if pd.notna(row.get("url")) else "",
            "spike_type":     str(row.get("spike_type", "")),
            "confidence":     float(row.get("confidence", 0)),
            "engagement_score": int(row.get("engagement_score", 0)),
            "velocity":       round(float(row.get("velocity", 0)), 4) if pd.notna(row.get("velocity")) else 0,
            "age_hours":      round(float(row.get("age_hours", 0)), 1) if pd.notna(row.get("age_hours")) else 0,
            "created_at":     row["created_at"].isoformat() if pd.notna(row.get("created_at")) else None,
        })

    return {"total": len(posts), "posts": posts}


@router.get("/alerts")
def alerts(velocity_threshold: float = Query(default=0.1)):
    """Posts with high velocity and age < 12h — breaking out right now."""
    classified, frontpage = _load()

    if "velocity" not in frontpage.columns or "age_hours" not in frontpage.columns:
        return {"alerts": [], "message": "velocity data not available — run rank step first"}

    hot = frontpage[
        (frontpage["velocity"] >= velocity_threshold) &
        (frontpage["age_hours"] < 12)
    ].copy()

    # Join spike type
    if "spike_type" in frontpage.columns:
        pass
    elif "title" in hot.columns and "title" in classified.columns:
        hot = hot.merge(
            classified[["title", "platform", "spike_type"]].drop_duplicates(),
            on=["title", "platform"],
            how="left",
        )

    hot = hot.sort_values("velocity", ascending=False)

    return {
        "count": len(hot),
        "threshold": velocity_threshold,
        "alerts": [
            {
                "title":      str(row.get("title", "")),
                "platform":   str(row.get("platform", "")),
                "author":     str(row.get("author", "")) if pd.notna(row.get("author")) else "",
                "velocity":   round(float(row["velocity"]), 4),
                "age_hours":  round(float(row["age_hours"]), 1),
                "spike_type": str(row.get("spike_type", "unknown")),
                "url":        str(row.get("url", "")) if pd.notna(row.get("url")) else "",
            }
            for _, row in hot.iterrows()
        ],
    }
