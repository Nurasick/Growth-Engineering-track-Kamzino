#!/usr/bin/env python3
"""
X / Twitter scraper — direct internal API using browser cookies.
No paid API, no broken twikit transaction middleware.
Uses auth_token + ct0 cookies exported from your browser.

Setup (.env):
  X_AUTH_TOKEN=<value of auth_token cookie from x.com>
  X_CT0=<value of ct0 cookie from x.com>

Usage:
  python scrapers/x_twikit_scraper.py                    # Claude queries
  python scrapers/x_twikit_scraper.py --product higgsfield
  python scrapers/x_twikit_scraper.py --queries "Claude Code" "vibe coding" --max 500
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import requests

# Load .env
_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

_REPO_ROOT = Path(__file__).parent.parent
_RAW_DIR   = _REPO_ROOT / "data" / "raw"

# Twitter's internal bearer token (public, hardcoded in the web app JS)
_BEARER = (
    "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
    "%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
)

PRODUCT_QUERIES = {
    "claude": [
        "Claude Code",
        "vibe coding Claude",
        "Anthropic Claude Code",
        "Claude Code agent",
        "switched to Claude",
        "Claude vs ChatGPT",
        "Claude better than GPT",
        "Anthropic announcement",
        "Claude Sonnet 2025",
        "Claude Opus",
        "from:AnthropicAI",
        "from:ClaudeAI",
        "#ClaudeCode",
    ],
    "higgsfield": [
        "Higgsfield AI",
        "Higgsfield video",
        "Higgsfield vs Runway",
        "Higgsfield vs Sora",
        "@Higgsfield_ai",
        "Higgsfield Cinema Studio",
        "#Higgsfield",
        "higgsfield.ai",
    ],
}

PRODUCT_OUTPUT = {
    "claude":     "x_twikit_claude.csv",
    "higgsfield": "x_twikit_higgsfield.csv",
}

OFFICIAL_HANDLES = {
    "claude":     {"anthropicai", "claudeai"},
    "higgsfield": {"higgsfield_ai"},
}


def _make_session(auth_token: str, ct0: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Authorization":          f"Bearer {_BEARER}",
        "X-Csrf-Token":           ct0,
        "X-Twitter-Auth-Type":    "OAuth2Session",
        "X-Twitter-Active-User":  "yes",
        "X-Twitter-Client-Language": "en",
        "Referer":                "https://x.com/",
        "Origin":                 "https://x.com",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        ),
    })
    s.cookies.set("auth_token", auth_token, domain=".x.com")
    s.cookies.set("ct0",        ct0,        domain=".x.com")
    return s


def _search_page(
    session: requests.Session,
    query: str,
    cursor: str | None,
    product: str = "Latest",
) -> tuple[list[dict], str | None]:
    """
    Call the adaptive search JSON endpoint.
    Returns (tweets, next_cursor).
    """
    params: dict = {
        "q":                     query,
        "tweet_mode":            "extended",
        "include_entities":      "true",
        "include_reply_count":   "1",
        "include_user_entities": "true",
        "count":                 "20",
        "result_filter":         "tweet" if product == "Latest" else "",
        "src":                   "typed_query",
        "f":                     "live" if product == "Latest" else "",
    }
    if cursor:
        params["cursor"] = cursor

    resp = session.get(
        "https://twitter.com/i/api/2/search/adaptive.json",
        params=params,
        timeout=20,
    )
    if resp.status_code == 429:
        print("  [rate-limit] sleeping 60s", file=sys.stderr)
        time.sleep(60)
        return [], None
    if resp.status_code != 200:
        print(f"  [warn] HTTP {resp.status_code} for {query!r}", file=sys.stderr)
        return [], None

    data     = resp.json()
    timeline = data.get("timeline", {})
    instrs   = timeline.get("instructions", [])

    tweets: list[dict] = []
    next_cursor: str | None = None

    tweet_lookup = data.get("globalObjects", {}).get("tweets", {})
    user_lookup  = data.get("globalObjects", {}).get("users",  {})

    for instr in instrs:
        for entry in instr.get("addEntries", {}).get("entries", []):
            eid = entry.get("entryId", "")
            content = entry.get("content", {})

            # Cursor entry
            op = content.get("operation", {})
            if op.get("cursor", {}).get("cursorType") == "Bottom":
                next_cursor = op["cursor"].get("value")
                continue

            # Tweet entry
            item = content.get("item", {})
            tweet_id = (
                item.get("content", {}).get("tweet", {}).get("id")
                or (eid.split("-")[1] if eid.startswith("tweet-") else None)
            )
            if tweet_id and tweet_id in tweet_lookup:
                t = tweet_lookup[tweet_id]
                uid = str(t.get("user_id_str") or t.get("user_id", ""))
                u = user_lookup.get(uid, {})
                tweets.append({"tweet": t, "user": u})

    return tweets, next_cursor


def _parse_tweet(raw: dict, query: str, official_handles: set[str]) -> dict:
    t = raw["tweet"]
    u = raw["user"]
    handle = (u.get("screen_name") or "").lower()
    tid    = str(t.get("id_str") or t.get("id") or "")
    views  = int((t.get("ext", {}) or {}).get("views", {}).get("count") or 0)
    likes  = int(t.get("favorite_count") or 0)
    return {
        "platform":         "x",
        "tweet_id":         tid,
        "author_handle":    u.get("screen_name", ""),
        "author_name":      u.get("name", ""),
        "text":             (t.get("full_text") or t.get("text") or "").replace("\n", " "),
        "created_at":       t.get("created_at", ""),
        "url":              f"https://x.com/{u.get('screen_name','i')}/status/{tid}",
        "is_official":      handle in official_handles,
        "source_query":     query,
        "has_media":        bool(t.get("extended_entities", {}).get("media")),
        "likes":            likes,
        "retweets":         int(t.get("retweet_count") or 0),
        "replies":          int(t.get("reply_count") or 0),
        "views":            views,
        "bookmarks":        int(t.get("bookmark_count") or 0),
        "author_followers": int(u.get("followers_count") or 0),
        "engagement_score": views if views > 0 else likes,
    }


def fetch_query(
    session: requests.Session,
    query: str,
    max_results: int,
    official_handles: set[str],
    verbose: bool,
) -> list[dict]:
    rows: list[dict] = []
    seen: set[str]   = set()

    for product in ("Latest", "Top"):
        cursor: str | None = None
        pages = 0
        while len(rows) < max_results and pages < 10:
            raw_tweets, cursor = _search_page(session, query, cursor, product)
            if not raw_tweets:
                break
            for raw in raw_tweets:
                tid = str(raw["tweet"].get("id_str") or "")
                if tid and tid not in seen:
                    seen.add(tid)
                    rows.append(_parse_tweet(raw, query, official_handles))
            pages += 1
            if verbose:
                print(f"  [fetch] {query!r} [{product}] page={pages} total={len(rows)}", file=sys.stderr)
            if not cursor:
                break
            time.sleep(1.0)

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape X via internal API (cookie auth)")
    parser.add_argument("--product", default="claude", choices=list(PRODUCT_QUERIES.keys()))
    parser.add_argument("--queries", nargs="*", help="Override default queries")
    parser.add_argument("--max",     type=int, default=200, help="Max tweets per query (default 200)")
    parser.add_argument("--output",  default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    auth_token = os.environ.get("X_AUTH_TOKEN", "")
    ct0        = os.environ.get("X_CT0", "")

    if not auth_token or not ct0:
        print(
            "ERROR: X_AUTH_TOKEN and X_CT0 must be set in .env\n"
            "Steps:\n"
            "  1. Open x.com in your browser (logged in)\n"
            "  2. DevTools → Application → Cookies → https://x.com\n"
            "  3. Copy 'auth_token' and 'ct0' values\n"
            "  4. Add to .env:\n"
            "       X_AUTH_TOKEN=<value>\n"
            "       X_CT0=<value>\n",
            file=sys.stderr,
        )
        return 1

    session     = _make_session(auth_token, ct0)
    queries     = args.queries or PRODUCT_QUERIES[args.product]
    official    = OFFICIAL_HANDLES.get(args.product, set())
    output_path = Path(args.output) if args.output else _RAW_DIR / PRODUCT_OUTPUT[args.product]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    seen_ids: set[str]   = set()

    for q in queries:
        print(f"  searching: {q!r}", file=sys.stderr)
        rows = fetch_query(session, q, args.max, official, args.verbose)
        for row in rows:
            if row["tweet_id"] not in seen_ids:
                seen_ids.add(row["tweet_id"])
                all_rows.append(row)
        time.sleep(2)

    if not all_rows:
        print("No tweets collected — cookies may be expired or account rate-limited.", file=sys.stderr)
        return 0

    fieldnames = list(all_rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(json.dumps({
        "product":          args.product,
        "queries_run":      len(queries),
        "tweets_collected": len(all_rows),
        "output":           str(output_path),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
