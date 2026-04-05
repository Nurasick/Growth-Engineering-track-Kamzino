import os
import time
import json
from datetime import datetime, timezone

import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
API_KEY        = os.environ.get("YOUTUBE_API_KEY", "")
BASE_URL       = "https://www.googleapis.com/youtube/v3"
LOG_PATH       = os.path.join(os.path.dirname(__file__), "..", "..", "data", "errors.log")

SEARCH_QUERIES = [
    "Claude AI",
    "Anthropic Claude",
    "Claude vs ChatGPT",
    "Claude Sonnet",
    "Claude Opus",
    "Claude Code",
    "vibe coding Claude",
    "Anthropic AI",
    "switched to Claude",
    "Claude better than GPT",
    "Claude Code agent",
]

# High-signal channels — scraped directly regardless of keyword match
CHANNEL_IDS = [
    "UCsBjURrPoezykLs9EqgamOA",  # Fireship
    "UCnUYZLuoy1rq1aVMwx4aTzw",  # AI Explained
    "UCXZCJLpBC9Ex5k2XnQGFBgQ",  # Two Minute Papers
    "UC0RhatS1pyxInC00YKjjBqQ",  # Marques Brownlee (MKBHD)
    "UCVHkFZqq6tbjD7kqAEKhtAQ",  # Matthew Berman
    "UC-D2d5RDqXMQ0RuVUi_TWOQ",  # Wes Roth
]

RESULTS_PER_QUERY      = 50   # per search query
MAX_PER_QUERY          = 200  # pagination ceiling per query
MAX_COMMENTS_PER_VIDEO = 20
BATCH_SIZE             = 50   # videos.list accepts up to 50 IDs per call


# ---------------------------------------------------------------------------
# Error logging
# ---------------------------------------------------------------------------
def _log_error(error_type: str, context: str, exc: Exception) -> None:
    ts   = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] [YOUTUBE] [{error_type}] {context} — {exc}\n"
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())


# ---------------------------------------------------------------------------
# HTTP with retry + 429 backoff
# ---------------------------------------------------------------------------
def _get(endpoint: str, params: dict) -> dict | None:
    params["key"] = API_KEY
    url = f"{BASE_URL}/{endpoint}"
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=15)

            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", min(2 ** attempt, 60)))
                print(f"  [429] rate-limited — sleeping {wait}s")
                time.sleep(wait)
                continue

            if resp.status_code == 403:
                _log_error("QUOTA_EXCEEDED", endpoint, Exception(resp.text[:200]))
                return None

            resp.raise_for_status()
            return resp.json()

        except Exception as exc:
            wait = min(2 ** attempt, 60)
            if attempt < 2:
                print(f"  [retry {attempt+1}/3] {endpoint} — sleeping {wait}s ({exc})")
                time.sleep(wait)
            else:
                _log_error("MAX_RETRIES", endpoint, exc)
                return None

    return None


# ---------------------------------------------------------------------------
# Phase 1a — keyword search video IDs  (100 quota units per call)
# ---------------------------------------------------------------------------
def search_video_ids(
    query: str,
    max_results: int = MAX_PER_QUERY,
    days: int = 30,
    order: str = "relevance",
) -> list[str]:
    published_after = (
        datetime.now(timezone.utc) - pd.Timedelta(days=days)
    ).isoformat().replace("+00:00", "Z")

    ids: list[str] = []
    page_token = None

    while len(ids) < max_results:
        params = {
            "part":           "id",
            "q":              query,
            "type":           "video",
            "maxResults":     min(max_results - len(ids), 50),
            "publishedAfter": published_after,
            "order":          order,
        }
        if page_token:
            params["pageToken"] = page_token

        data = _get("search", params)
        if data is None:
            break

        for item in data.get("items", []):
            vid_id = item.get("id", {}).get("videoId")
            if vid_id:
                ids.append(vid_id)

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return ids


# ---------------------------------------------------------------------------
# Phase 1b — channel video IDs  (100 quota units per call)
# ---------------------------------------------------------------------------
def channel_video_ids(channel_id: str, days: int = 30, max_results: int = 50) -> list[str]:
    published_after = (
        datetime.now(timezone.utc) - pd.Timedelta(days=days)
    ).isoformat().replace("+00:00", "Z")

    ids: list[str] = []
    page_token = None

    while len(ids) < max_results:
        params = {
            "part":           "id",
            "channelId":      channel_id,
            "type":           "video",
            "maxResults":     min(max_results - len(ids), 50),
            "publishedAfter": published_after,
            "order":          "date",
        }
        if page_token:
            params["pageToken"] = page_token

        data = _get("search", params)
        if data is None:
            break

        for item in data.get("items", []):
            vid_id = item.get("id", {}).get("videoId")
            if vid_id:
                ids.append(vid_id)

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return ids


# ---------------------------------------------------------------------------
# Phase 2 — batch-fetch video stats  (1 quota unit per batch of ≤50)
# ---------------------------------------------------------------------------
def fetch_video_stats(video_ids: list[str]) -> list[dict]:
    records = []
    for i in range(0, len(video_ids), BATCH_SIZE):
        batch = video_ids[i : i + BATCH_SIZE]
        data = _get("videos", {
            "part": "snippet,statistics,contentDetails",
            "id":   ",".join(batch),
        })
        if data is None:
            continue

        for item in data.get("items", []):
            snippet  = item.get("snippet", {})
            stats    = item.get("statistics", {})
            details  = item.get("contentDetails", {})
            duration = _parse_duration(details.get("duration", ""))

            records.append({
                "video_id":       item["id"],
                "title":          snippet.get("title", ""),
                "description":    (snippet.get("description") or "")[:1000],
                "channel":        snippet.get("channelTitle", ""),
                "published_at":   snippet.get("publishedAt", ""),
                "view_count":     int(stats.get("viewCount",    0) or 0),
                "like_count":     int(stats.get("likeCount",    0) or 0),
                "comment_count":  int(stats.get("commentCount", 0) or 0),
                "duration_sec":   duration,
                "url":            f"https://www.youtube.com/watch?v={item['id']}",
            })

    return records


# ---------------------------------------------------------------------------
# Phase 3 — comments  (1 quota unit per request)
# ---------------------------------------------------------------------------
def fetch_comments(video_id: str, max_comments: int = MAX_COMMENTS_PER_VIDEO) -> list[dict]:
    data = _get("commentThreads", {
        "part":       "snippet",
        "videoId":    video_id,
        "maxResults": min(max_comments, 100),
        "order":      "relevance",
        "textFormat": "plainText",
    })
    if data is None:
        return []

    records = []
    for item in data.get("items", []):
        try:
            top = item["snippet"]["topLevelComment"]["snippet"]
        except (KeyError, TypeError) as exc:
            _log_error("PARSE_ERROR", f"comment in {video_id}", exc)
            continue

        records.append({
            "comment_id":   item["id"],
            "video_id":     video_id,
            "author":       top.get("authorDisplayName", ""),
            "body":         (top.get("textDisplay") or "")[:1000],
            "like_count":   int(top.get("likeCount", 0) or 0),
            "published_at": top.get("publishedAt", ""),
        })

    return records


# ---------------------------------------------------------------------------
# Duration helper  PT#H#M#S → seconds
# ---------------------------------------------------------------------------
def _parse_duration(duration: str) -> int:
    import re
    if not duration:
        return 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


# ---------------------------------------------------------------------------
# CSV upsert — merge new records into existing file, dedup on id_col
# ---------------------------------------------------------------------------
def upsert_csv(new_records: list[dict], filepath: str, id_col: str) -> int:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    new_df = pd.DataFrame(new_records)
    if os.path.exists(filepath):
        existing = pd.read_csv(filepath, dtype=str)
        existing = existing[~existing[id_col].isin(new_df[id_col].astype(str))]
        merged = pd.concat([existing, new_df], ignore_index=True)
    else:
        merged = new_df
    merged.to_csv(filepath, index=False, encoding="utf-8")
    return len(merged)


# ---------------------------------------------------------------------------
# Main — keyword queries + channel scraping, upserts date-stamped CSVs
# ---------------------------------------------------------------------------
def main(
    queries: list[str] = SEARCH_QUERIES,
    channel_ids: list[str] = CHANNEL_IDS,
    limit: int = MAX_PER_QUERY,
    days: int = 30,
    order: str = "relevance",
) -> None:
    today         = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw_dir       = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
    videos_path   = os.path.join(raw_dir, f"youtube_videos_{today}.csv")
    comments_path = os.path.join(raw_dir, f"youtube_comments_{today}.csv")

    seen_ids: set[str] = set()
    all_video_ids: list[str] = []

    def _add(ids: list[str]) -> None:
        for vid_id in ids:
            if vid_id not in seen_ids:
                seen_ids.add(vid_id)
                all_video_ids.append(vid_id)

    # Phase 1a: keyword search
    for query in queries:
        ids = search_video_ids(query, max_results=limit, days=days, order=order)
        _add(ids)
        print(f"Query '{query}' → {len(ids)} results · {len(all_video_ids)} unique total")

    # Phase 1b: channel scraping
    for ch_id in channel_ids:
        ids = channel_video_ids(ch_id, days=days, max_results=50)
        _add(ids)
        print(f"Channel {ch_id} → {len(ids)} results · {len(all_video_ids)} unique total")

    # Phase 2: batch-fetch stats
    all_videos = fetch_video_stats(all_video_ids)

    # Phase 3: fetch comments for each video
    all_comments: list[dict] = []
    for video in all_videos:
        comments = fetch_comments(video["video_id"])
        all_comments.extend(comments)

    total_videos   = upsert_csv(all_videos,   videos_path,   id_col="video_id")
    total_comments = upsert_csv(all_comments, comments_path, id_col="comment_id")
    print(f"\nUpserted {len(all_videos)} videos   → {total_videos} total in {videos_path}")
    print(f"Upserted {len(all_comments)} comments → {total_comments} total in {comments_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",   type=int, default=30,         help="How many days back to fetch (default 30)")
    parser.add_argument("--limit",  type=int, default=MAX_PER_QUERY, help="Max results per query (default 200)")
    parser.add_argument("--order",  type=str, default="relevance", choices=["relevance", "viewCount", "date"], help="Search order (default relevance)")
    parser.add_argument("--no-channels", action="store_true",     help="Skip channel scraping")
    parser.add_argument("--smoke",  action="store_true",          help="Smoke test — fetch 5 videos, no file write")
    args = parser.parse_args()

    if args.smoke:
        videos   = fetch_video_stats(search_video_ids("Claude AI", max_results=5, days=args.days))
        comments = fetch_comments(videos[0]["video_id"]) if videos else []
        print(f"\n--- Smoke test ---\nVideos: {len(videos)}  Comments: {len(comments)}")
        if videos:
            print(json.dumps(videos[0], indent=2, default=str))
    else:
        channels = [] if args.no_channels else CHANNEL_IDS
        main(days=args.days, limit=args.limit, order=args.order, channel_ids=channels)
