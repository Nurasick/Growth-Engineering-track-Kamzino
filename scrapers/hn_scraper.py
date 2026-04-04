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
BASE_URL  = "https://hn.algolia.com/api/v1/search_by_date"
LOG_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "errors.log")
QUERIES   = ["Claude AI", "Anthropic"]


# ---------------------------------------------------------------------------
# Error logging
# ---------------------------------------------------------------------------
def _log_error(error_type, context, exc):
    ts   = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] [HN] [{error_type}] {context} — {exc}\n"
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())


# ---------------------------------------------------------------------------
# HTTP with retry + exponential backoff
# ---------------------------------------------------------------------------
def _get(url, params=None):
    last_exc = None
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=15)

            if resp.status_code == 429:
                wait = min(2 ** attempt, 60)
                print(f"  [429] rate-limited — sleeping {wait}s")
                time.sleep(wait)
                continue

            if resp.status_code != 200:
                wait = min(2 ** attempt, 60)
                print(f"  [HTTP {resp.status_code}] — sleeping {wait}s")
                time.sleep(wait)
                continue

            return resp.json()

        except Exception as exc:
            last_exc = exc
            wait = min(2 ** attempt, 60)
            if attempt < 2:
                print(f"  [retry {attempt+1}/3] {url} — sleeping {wait}s ({exc})")
                time.sleep(wait)
            else:
                _log_error("MAX_RETRIES", url, exc)
                return None

    if last_exc is not None:
        _log_error("MAX_RETRIES", url, last_exc)
    return None


# ---------------------------------------------------------------------------
# Item fetching — paginates search_by_date for one query + tag type
# ---------------------------------------------------------------------------
def fetch_items(query, tags, pages=3, hits_per_page=100, days=7):
    records = []
    since = int(datetime.now(timezone.utc).timestamp()) - (days * 24 * 60 * 60)

    for page_num in range(pages):
        params = {
            "query":          query,
            "tags":           tags,
            "numericFilters": f"created_at_i>{since}",
            "hitsPerPage":    hits_per_page,
            "page":           page_num,
        }

        data = _get(BASE_URL, params=params)

        if data is None:
            _log_error(
                "FETCH_FAILED",
                f"query={query!r} tags={tags!r} page={page_num}",
                Exception("_get returned None"),
            )
            time.sleep(0.5)
            continue

        hits = data.get("hits", [])
        print(f"  Page {page_num+1}: fetched {len(hits)} items")

        for hit in hits:
            records.append({
                "object_id":    hit.get("objectID", ""),
                "title":        hit.get("title") or "",
                "points":       hit.get("points") or 0,
                "num_comments": hit.get("num_comments") or 0,
                "author":       hit.get("author") or "",
                "created_at":   hit.get("created_at") or "",
                "url":          hit.get("url") or "",
                "story_text":   (hit.get("story_text") or "")[:2000],
                "comment_text": (hit.get("comment_text") or "")[:1000],
                "tags":         "|".join(hit.get("_tags") or []),
                "query":        query,
            })

        time.sleep(0.5)

    return records


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------
def save_to_csv(records, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    pd.DataFrame(records).to_csv(filepath, index=False, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main — both queries, stories + comments, deduped on object_id
# ---------------------------------------------------------------------------
def main(queries=QUERIES, pages=3, days=7, overwrite=False):
    today    = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    suffix   = f"_{days}d" if days != 7 else ""
    filepath = os.path.join(
        os.path.dirname(__file__), "..", "data", "raw", f"hn_items{suffix}_{today}.csv"
    )

    if os.path.exists(filepath) and not overwrite:
        raise FileExistsError(
            f"Output file for {today} already exists: {filepath}\n"
            "Pass overwrite=True or use --overwrite flag to re-run."
        )

    all_records = []

    for query in queries:
        print(f"\nFetching stories  — query: {query!r} (last {days} days)")
        all_records.extend(fetch_items(query, tags="story", pages=pages, days=days))

        print(f"\nFetching comments — query: {query!r} (last {days} days)")
        all_records.extend(fetch_items(query, tags="comment", pages=pages, days=days))

    # Deduplicate on object_id — keep first occurrence
    seen    = set()
    deduped = []
    for rec in all_records:
        if rec["object_id"] not in seen:
            seen.add(rec["object_id"])
            deduped.append(rec)

    save_to_csv(deduped, filepath)
    print(f"\nSaved {len(deduped)} items -> {filepath}")


# ---------------------------------------------------------------------------
# Smoke test — 1 page, 20 hits, stories only, does NOT write a file
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",      type=int, default=7,     help="How many days back to fetch (default 7)")
    parser.add_argument("--pages",     type=int, default=3,     help="Pages per query (default 3)")
    parser.add_argument("--overwrite", action="store_true",     help="Overwrite existing output file")
    parser.add_argument("--smoke",     action="store_true",     help="Smoke test only — don't write file")
    args = parser.parse_args()

    if args.smoke:
        print("Running smoke test: fetch_items('Claude AI', tags='story', pages=1, hits_per_page=20)")
        results = fetch_items("Claude AI", tags="story", pages=1, hits_per_page=20)
        print(f"\nRow count: {len(results)}")
        if results:
            print("\nFirst row:")
            print(json.dumps(results[0], indent=2, default=str))
    else:
        main(pages=args.pages, days=args.days, overwrite=args.overwrite)