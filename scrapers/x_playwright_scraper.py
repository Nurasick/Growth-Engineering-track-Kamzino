#!/usr/bin/env python3
"""
X / Twitter scraper using Playwright (real Chromium browser).

Bypasses x-client-transaction-id by running a real browser — the browser
generates the header natively. We intercept the search API JSON responses.

Setup (.env):
  X_AUTH_TOKEN=<value of auth_token cookie from x.com>
  X_CT0=<value of ct0 cookie from x.com>

Usage:
  python scrapers/x_playwright_scraper.py                      # Claude queries
  python scrapers/x_playwright_scraper.py --product higgsfield
  python scrapers/x_playwright_scraper.py --queries "Claude Code" "vibe coding"
  python scrapers/x_playwright_scraper.py --headless false      # watch the browser
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import sys
import time
from pathlib import Path

# Load .env
_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

try:
    from playwright.async_api import async_playwright, Response
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright && python -m playwright install chromium", file=sys.stderr)
    sys.exit(1)

_REPO_ROOT = Path(__file__).parent.parent
_RAW_DIR   = _REPO_ROOT / "data" / "raw"

PRODUCT_QUERIES = {
    "claude": [
        "Claude Code",
        "vibe coding Claude",
        "Claude Code agent",
        "switched to Claude",
        "Claude vs ChatGPT",
        "Anthropic Claude",
        "Claude Sonnet",
        "Claude Opus",
        "from:AnthropicAI",
        "#ClaudeCode",
    ],
    "higgsfield": [
        "Higgsfield AI",
        "Higgsfield video",
        "Higgsfield vs Runway",
        "@Higgsfield_ai",
        "Higgsfield Cinema",
        "#Higgsfield",
    ],
}

PRODUCT_OUTPUT = {
    "claude":     "x_playwright_claude.csv",
    "higgsfield": "x_playwright_higgsfield.csv",
}

OFFICIAL_HANDLES = {
    "claude":     {"anthropicai", "claudeai"},
    "higgsfield": {"higgsfield_ai"},
}


def _extract_tweets_from_response(data: dict, query: str, official_handles: set[str]) -> list[dict]:
    """Parse tweets from Twitter's internal search/adaptive.json or GraphQL response."""
    rows: list[dict] = []

    # adaptive.json format
    global_tweets = data.get("globalObjects", {}).get("tweets", {})
    global_users  = data.get("globalObjects", {}).get("users",  {})
    if global_tweets:
        for tid, t in global_tweets.items():
            uid  = str(t.get("user_id_str") or t.get("user_id", ""))
            u    = global_users.get(uid, {})
            handle = (u.get("screen_name") or "").lower()
            views  = int((t.get("ext", {}) or {}).get("views", {}).get("count") or 0)
            likes  = int(t.get("favorite_count") or 0)
            rows.append({
                "platform":         "x",
                "tweet_id":         str(tid),
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
            })
        return rows

    # GraphQL SearchTimeline format
    try:
        instructions = (
            data.get("data", {})
                .get("search_by_raw_query", {})
                .get("search_timeline", {})
                .get("timeline", {})
                .get("instructions", [])
        )
        for instr in instructions:
            entries = instr.get("entries", []) or instr.get("moduleItems", [])
            for entry in entries:
                result = (
                    entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {})
                    or entry.get("item", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {})
                )
                if not result:
                    continue
                core    = result.get("core", {}).get("user_results", {}).get("result", {})
                legacy  = result.get("legacy", {}) or {}
                u_leg   = core.get("legacy", {}) or {}
                tid     = str(result.get("rest_id") or legacy.get("id_str") or "")
                handle  = (u_leg.get("screen_name") or "").lower()
                views   = int(result.get("views", {}).get("count") or 0)
                likes   = int(legacy.get("favorite_count") or 0)
                if not tid:
                    continue
                rows.append({
                    "platform":         "x",
                    "tweet_id":         tid,
                    "author_handle":    u_leg.get("screen_name", ""),
                    "author_name":      u_leg.get("name", ""),
                    "text":             (legacy.get("full_text") or "").replace("\n", " "),
                    "created_at":       legacy.get("created_at", ""),
                    "url":              f"https://x.com/{u_leg.get('screen_name','i')}/status/{tid}",
                    "is_official":      handle in official_handles,
                    "source_query":     query,
                    "has_media":        bool(legacy.get("extended_entities", {}).get("media")),
                    "likes":            likes,
                    "retweets":         int(legacy.get("retweet_count") or 0),
                    "replies":          int(legacy.get("reply_count") or 0),
                    "views":            views,
                    "bookmarks":        int(legacy.get("bookmark_count") or 0),
                    "author_followers": int(u_leg.get("followers_count") or 0),
                    "engagement_score": views if views > 0 else likes,
                })
    except Exception:
        pass

    return rows


async def scrape_query(
    page,
    query: str,
    max_results: int,
    official_handles: set[str],
    verbose: bool,
    since: str | None = None,   # YYYY-MM-DD
    until: str | None = None,   # YYYY-MM-DD
    top_mode: bool = False,     # True = Top tweets (good for historical), False = Latest
) -> list[dict]:
    collected: list[dict] = []
    seen_ids: set[str] = set()
    response_queue: list[dict] = []

    # Build full query string with optional date filters
    full_query = query
    if since:
        full_query += f" since:{since}"
    if until:
        full_query += f" until:{until}"

    async def handle_response(response: Response):
        url = response.url
        if ("search/adaptive" in url or "SearchTimeline" in url) and response.status == 200:
            try:
                body = await response.json()
                response_queue.append(body)
            except Exception:
                pass

    page.on("response", handle_response)

    # Top mode = no &f=live, best for historical. Latest mode = &f=live, best for real-time.
    tab_param = "" if top_mode else "&f=live"
    encoded   = full_query.replace(' ', '%20').replace(':', '%3A')
    search_url = f"https://x.com/search?q={encoded}&src=typed_query{tab_param}"
    if verbose:
        print(f"  [browser] {search_url}", file=sys.stderr)
    await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(5)  # let XHR responses arrive

    # Process intercepted responses
    for body in response_queue:
        for row in _extract_tweets_from_response(body, query, official_handles):
            if row["tweet_id"] not in seen_ids:
                seen_ids.add(row["tweet_id"])
                collected.append(row)
    response_queue.clear()

    # Scroll to load more
    scrolls = 0
    while len(collected) < max_results and scrolls < 8:
        await page.evaluate("window.scrollBy(0, 2000)")
        await asyncio.sleep(2)
        for body in response_queue:
            for row in _extract_tweets_from_response(body, query, official_handles):
                if row["tweet_id"] not in seen_ids:
                    seen_ids.add(row["tweet_id"])
                    collected.append(row)
        response_queue.clear()
        scrolls += 1
        if verbose:
            print(f"  [scroll {scrolls}] {len(collected)} tweets so far", file=sys.stderr)

    page.remove_listener("response", handle_response)
    return collected


def _monthly_chunks(since: str, until: str) -> list[tuple[str, str]]:
    """Split a date range into monthly (since, until) pairs."""
    from datetime import date, timedelta
    import calendar
    start = date.fromisoformat(since)
    end   = date.fromisoformat(until)
    chunks = []
    cur = start
    while cur < end:
        last_day = calendar.monthrange(cur.year, cur.month)[1]
        next_month = date(cur.year, cur.month, last_day) + timedelta(days=1)
        chunk_end = min(next_month, end)
        chunks.append((cur.isoformat(), chunk_end.isoformat()))
        cur = next_month
    return chunks


async def run(
    product: str,
    queries: list[str],
    max_per_query: int,
    output_path: Path,
    headless: bool,
    verbose: bool,
    since: str | None = None,
    until: str | None = None,
    historical: bool = False,   # chunk by month, Top mode
) -> int:
    auth_token = os.environ.get("X_AUTH_TOKEN", "")
    ct0        = os.environ.get("X_CT0", "")

    if not auth_token or not ct0:
        print("ERROR: X_AUTH_TOKEN and X_CT0 must be set in .env", file=sys.stderr)
        return 1

    official = OFFICIAL_HANDLES.get(product, set())
    all_rows: list[dict] = []
    seen_ids: set[str] = set()

    # Build list of (query, since, until, top_mode) jobs
    jobs: list[tuple[str, str | None, str | None, bool]] = []
    if historical and since:
        end = until or "2026-04-05"
        chunks = _monthly_chunks(since, end)
        print(f"  [historical] {len(chunks)} months × {len(queries)} queries = {len(chunks)*len(queries)} searches", file=sys.stderr)
        for q in queries:
            for chunk_since, chunk_until in chunks:
                jobs.append((q, chunk_since, chunk_until, True))
    else:
        for q in queries:
            jobs.append((q, since, until, since is not None))  # top_mode if date-filtered

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )
        await context.add_cookies([
            {"name": "auth_token", "value": auth_token, "domain": ".x.com", "path": "/"},
            {"name": "ct0",        "value": ct0,        "domain": ".x.com", "path": "/"},
        ])
        page = await context.new_page()

        for i, (q, s, u, top_mode) in enumerate(jobs):
            label = f"{q!r}"
            if s: label += f" [{s}→{u}]"
            print(f"  [{i+1}/{len(jobs)}] {label}", file=sys.stderr)
            try:
                rows = await scrape_query(page, q, max_per_query, official, verbose,
                                          since=s, until=u, top_mode=top_mode)
            except Exception as exc:
                print(f"  [warn] failed: {exc}", file=sys.stderr)
                rows = []
            for row in rows:
                if row["tweet_id"] not in seen_ids:
                    seen_ids.add(row["tweet_id"])
                    all_rows.append(row)
            print(f"  → {len(rows)} new (total: {len(all_rows)})", file=sys.stderr)
            if all_rows:
                _write_csv(output_path, all_rows)
            await asyncio.sleep(2)

        await browser.close()

    if not all_rows:
        print("No tweets collected.", file=sys.stderr)
        return 0

    _write_csv(output_path, all_rows)
    print(json.dumps({
        "product": product, "jobs": len(jobs),
        "tweets_collected": len(all_rows), "output": str(output_path),
    }))
    return 0


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape X with real Chromium (Playwright)")
    parser.add_argument("--product",     default="claude", choices=list(PRODUCT_QUERIES.keys()))
    parser.add_argument("--queries",     nargs="*", help="Override queries")
    parser.add_argument("--max",         type=int, default=50, help="Max tweets per query/chunk")
    parser.add_argument("--output",      default=None)
    parser.add_argument("--since",       default=None, help="Start date YYYY-MM-DD")
    parser.add_argument("--until",       default=None, help="End date YYYY-MM-DD")
    parser.add_argument("--historical",  action="store_true",
                        help="Auto-chunk by month from --since to today, Top mode (best for history)")
    parser.add_argument("--headless",    default="true", choices=["true", "false"])
    parser.add_argument("--verbose",     action="store_true")
    args = parser.parse_args()

    queries     = args.queries or PRODUCT_QUERIES[args.product]
    output_path = Path(args.output) if args.output else _RAW_DIR / PRODUCT_OUTPUT[args.product]
    headless    = args.headless.lower() == "true"

    return asyncio.run(run(
        product=args.product,
        queries=queries,
        max_per_query=args.max,
        output_path=output_path,
        headless=headless,
        verbose=args.verbose,
        since=args.since,
        until=args.until,
        historical=args.historical,
    ))


if __name__ == "__main__":
    raise SystemExit(main())
