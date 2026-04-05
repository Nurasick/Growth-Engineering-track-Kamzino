#!/usr/bin/env python3
"""
Normalize all scraped sources into a unified schema.

Reads  → data/raw/  (x_case_raw.csv, reddit_posts_*.csv, hn_items_*.csv, youtube_*.csv)
Writes → data/processed/unified_posts.csv
         data/processed/unified_comments.csv
         data/processed/normalization_summary.json

Auto-detects today's dated files (e.g. hn_items_2026-04-04.csv).
Falls back to any existing dated file if today's isn't present.
"""

from __future__ import annotations

import ast
import csv
import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
import glob as _glob

REPO_ROOT      = Path(__file__).parent.parent
RAW_DIR        = REPO_ROOT / "data" / "raw"
PROCESSED_DIR  = REPO_ROOT / "data" / "processed"
TODAY          = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _latest(pattern: str) -> Path | None:
    """Find the most recently modified file matching a glob pattern in RAW_DIR."""
    matches = sorted(RAW_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def _find_input(today_name: str, fallback_pattern: str) -> Path | None:
    exact = RAW_DIR / today_name
    if exact.exists():
        return exact
    return _latest(fallback_pattern)


UNIFIED_POST_FIELDS = [
    "platform", "source_type", "source_file", "post_id", "root_post_id",
    "created_at", "author", "author_handle", "channel", "official",
    "title", "body_text", "url", "topic_query",
    "engagement_score", "comment_count", "secondary_metric", "secondary_metric_name",
    "raw_tags", "has_media", "outbound_links_json",
]

UNIFIED_COMMENT_FIELDS = [
    "platform", "source_type", "source_file", "comment_id", "post_id",
    "parent_id", "created_at", "author", "body_text", "score",
    "depth", "is_top_level", "channel", "official",
]


def parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool): return value
    if value is None: return None
    s = str(value).strip().lower()
    if s in {"true", "1", "yes"}: return True
    if s in {"false", "0", "no"}: return False
    return None


def parse_listish(value: str) -> list[str]:
    if not value: return []
    try:
        obj = ast.literal_eval(value)
        if isinstance(obj, list): return [str(x) for x in obj]
    except Exception:
        pass
    return [value]


def to_iso(value: str) -> str:
    if not value: return ""
    for parser in (
        lambda v: datetime.fromisoformat(v.replace("Z", "+00:00")),
        parsedate_to_datetime,
    ):
        try:
            dt = parser(value)
            if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except Exception:
            continue
    return value


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def normalize_x_posts(rows, source_file):
    out = []
    for row in rows:
        # Weighted engagement: replies and retweets require higher intent than likes
        # engagement_score = likes + (retweets × 2) + (replies × 2) + bookmarks
        # views is stored as secondary_metric (reach, not engagement)
        likes     = int(row.get("likes",     0) or 0)
        retweets  = int(row.get("retweets",  0) or 0)
        replies   = int(row.get("replies",   0) or 0)
        bookmarks = int(row.get("bookmarks", 0) or 0)
        views     = int(row.get("views",     0) or 0)
        eng = likes + (retweets * 2) + (replies * 2) + bookmarks
        # Fall back to views if no interaction data available (legacy seed tweets)
        if eng == 0 and views > 0:
            eng = views
        out.append({
            "platform": "x", "source_type": "post", "source_file": source_file,
            "post_id": row["tweet_id"], "root_post_id": row["tweet_id"],
            "created_at": to_iso(row["created_at"]),
            "author": row["author_name"], "author_handle": row["author_handle"],
            "channel": "official" if parse_bool(row.get("is_official")) else "third_party",
            "official": parse_bool(row.get("is_official")),
            "title": "", "body_text": row.get("text", ""),
            "url": row.get("url", ""), "topic_query": row.get("source_query", ""),
            "engagement_score": eng,
            "comment_count": row.get("replies", ""),
            "secondary_metric": views,
            "secondary_metric_name": "views",
            "raw_tags": row.get("source_query", ""),
            "has_media": parse_bool(row.get("has_media")),
            "outbound_links_json": json.dumps(parse_listish(row.get("outbound_links", "")), ensure_ascii=False),
        })
    return out


def normalize_reddit_posts(rows, source_file):
    out = []
    for row in rows:
        body = (row.get("title", "") + "\n\n" + row.get("selftext", "")).strip()
        # Weighted engagement: comments require writing = 3× the intent of an upvote
        # engagement_score = score + (num_comments × 3)
        # upvote_ratio stored as secondary_metric for filtering
        score    = int(row.get("score", 0) or 0)
        comments = int(row.get("num_comments", 0) or 0)
        eng      = score + (comments * 3)
        out.append({
            "platform": "reddit", "source_type": "post", "source_file": source_file,
            "post_id": row["post_id"], "root_post_id": row["post_id"],
            "created_at": to_iso(row["created_utc"]),
            "author": row.get("author", ""), "author_handle": row.get("author", ""),
            "channel": row.get("subreddit", ""), "official": False,
            "title": row.get("title", ""), "body_text": body,
            "url": row.get("permalink") or row.get("url", ""),
            "topic_query": row.get("subreddit", ""),
            "engagement_score": eng,
            "comment_count": comments,
            "secondary_metric": row.get("upvote_ratio", ""),
            "secondary_metric_name": "upvote_ratio",
            "raw_tags": row.get("subreddit", ""),
            "has_media": bool(row.get("url", "").startswith("https://i.redd.it/")),
            "outbound_links_json": json.dumps([row.get("url", "")] if row.get("url") else [], ensure_ascii=False),
        })
    return out


def normalize_reddit_comments(rows, source_file):
    out = []
    for row in rows:
        out.append({
            "platform": "reddit", "source_type": "comment", "source_file": source_file,
            "comment_id": row["comment_id"], "post_id": row["post_id"],
            "parent_id": row.get("parent_id", ""),
            "created_at": to_iso(row["created_utc"]),
            "author": row.get("author", ""), "body_text": row.get("body", ""),
            "score": row.get("score", ""), "depth": row.get("depth", ""),
            "is_top_level": parse_bool(row.get("is_top_level")),
            "channel": "", "official": False,
        })
    return out


def normalize_hn_items(rows, source_file):
    posts, comments = [], []
    for row in rows:
        created_at = to_iso(row.get("created_at", ""))
        tags = row.get("tags", "")
        if "comment_" in tags or row.get("comment_text"):
            comments.append({
                "platform": "hn", "source_type": "comment", "source_file": source_file,
                "comment_id": row.get("object_id", ""), "post_id": row.get("object_id", ""),
                "parent_id": "", "created_at": created_at,
                "author": row.get("author", ""),
                "body_text": row.get("comment_text") or row.get("story_text") or row.get("title", ""),
                "score": row.get("points", ""), "depth": "", "is_top_level": "",
                "channel": "Hacker News", "official": False,
            })
        else:
            body = (row.get("title", "") + "\n\n" + (row.get("story_text") or "")).strip()
            posts.append({
                "platform": "hn", "source_type": "post", "source_file": source_file,
                "post_id": row.get("object_id", ""), "root_post_id": row.get("object_id", ""),
                "created_at": created_at,
                "author": row.get("author", ""), "author_handle": row.get("author", ""),
                "channel": "Hacker News", "official": False,
                "title": row.get("title", ""), "body_text": body,
                "url": row.get("url", ""), "topic_query": row.get("query", ""),
                "engagement_score": row.get("points", ""),
                "comment_count": row.get("num_comments", ""),
                "secondary_metric": "", "secondary_metric_name": "",
                "raw_tags": tags, "has_media": False,
                "outbound_links_json": json.dumps([row.get("url", "")] if row.get("url") else [], ensure_ascii=False),
            })
    return posts, comments


def normalize_youtube_videos(rows, source_file):
    out = []
    for row in rows:
        out.append({
            "platform": "youtube", "source_type": "post", "source_file": source_file,
            "post_id": row.get("video_id", ""), "root_post_id": row.get("video_id", ""),
            "created_at": to_iso(row.get("published_at", "")),
            "author": row.get("channel", ""), "author_handle": row.get("channel", ""),
            "channel": row.get("channel", ""), "official": False,
            "title": row.get("title", ""),
            "body_text": (row.get("title", "") + "\n\n" + row.get("description", "")).strip(),
            "url": row.get("url", ""), "topic_query": "",
            "engagement_score": row.get("view_count", ""),
            "comment_count": row.get("comment_count", ""),
            "secondary_metric": row.get("like_count", ""),
            "secondary_metric_name": "like_count",
            "raw_tags": "", "has_media": True,
            "outbound_links_json": json.dumps([row.get("url", "")] if row.get("url") else [], ensure_ascii=False),
        })
    return out


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main(prefix: str = "") -> int:
    """
    prefix: product prefix for raw filenames (e.g. "higgsfield").
    Empty string = default Claude dataset.
    """
    posts:    list[dict] = []
    comments: list[dict] = []
    loaded = []
    p = f"{prefix}_" if prefix else ""

    # X posts
    x_path = RAW_DIR / f"{p}x_case_raw.csv" if prefix else RAW_DIR / "x_case_raw.csv"
    if x_path.exists():
        rows = read_csv(x_path)
        posts.extend(normalize_x_posts(rows, x_path.name))
        loaded.append(f"X: {len(rows)}")

    # Reddit posts
    rp = _find_input(f"{p}reddit_posts_{TODAY}.csv", f"{p}reddit_posts_*.csv")
    if rp:
        rows = read_csv(rp)
        posts.extend(normalize_reddit_posts(rows, rp.name))
        loaded.append(f"Reddit posts: {len(rows)}")

    # Reddit comments
    rc = _find_input(f"{p}reddit_comments_{TODAY}.csv", f"{p}reddit_comments_*.csv")
    if rc:
        rows = read_csv(rc)
        comments.extend(normalize_reddit_comments(rows, rc.name))
        loaded.append(f"Reddit comments: {len(rows)}")

    # HN — prefer wider historical file if available
    hn_wide = _latest(f"{p}hn_items_*d_*.csv") if not prefix else _latest(f"{p}hn_items_*.csv")
    hn = hn_wide if hn_wide else _find_input(f"{p}hn_items_{TODAY}.csv", f"{p}hn_items_*.csv")
    if hn:
        rows = read_csv(hn)
        hn_posts, hn_comments = normalize_hn_items(rows, hn.name)
        posts.extend(hn_posts)
        comments.extend(hn_comments)
        loaded.append(f"HN: {len(rows)}")

    # YouTube videos
    yt = _find_input(f"{p}youtube_videos_{TODAY}.csv", f"{p}youtube_videos_*.csv")
    if not yt and not prefix:
        yt = _find_input("youtube_posts.csv", "youtube_posts.csv")
    if yt:
        rows = read_csv(yt)
        posts.extend(normalize_youtube_videos(rows, yt.name))
        loaded.append(f"YouTube: {len(rows)}")

    out_posts    = PROCESSED_DIR / "unified_posts.csv"
    out_comments = PROCESSED_DIR / "unified_comments.csv"
    out_summary  = PROCESSED_DIR / "normalization_summary.json"

    write_csv(out_posts, UNIFIED_POST_FIELDS, posts)
    write_csv(out_comments, UNIFIED_COMMENT_FIELDS, comments)

    summary = {
        "posts_total": len(posts), "comments_total": len(comments),
        "sources_loaded": loaded,
        "posts_by_platform": {
            p: sum(1 for r in posts if r["platform"] == p)
            for p in ["x", "reddit", "youtube", "hn"]
        },
    }
    out_summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", type=str, default="", help="Product prefix for raw filenames (e.g. higgsfield)")
    args = parser.parse_args()
    raise SystemExit(main(prefix=args.prefix))
