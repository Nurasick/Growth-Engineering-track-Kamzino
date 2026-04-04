import os
import time
import json
from datetime import datetime, timezone

import requests
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL   = "https://www.reddit.com"
HEADERS    = {"User-Agent": "hacknu-growth-scraper/1.0"}
LOG_PATH   = os.path.join(os.path.dirname(__file__), "..", "data", "errors.log")
SUBREDDITS = ["ClaudeAI", "artificial", "ChatGPT", "MachineLearning", "LocalLLaMA"]


# ---------------------------------------------------------------------------
# Error logging
# ---------------------------------------------------------------------------
def _log_error(error_type: str, context: str, exc: Exception) -> None:
    ts   = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] [REDDIT] [{error_type}] {context} — {exc}\n"
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())


# ---------------------------------------------------------------------------
# HTTP with retry + 429 backoff
# ---------------------------------------------------------------------------
def _get(url: str, params: dict = None) -> dict | None:
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)

            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", min(2 ** attempt, 60)))
                print(f"  [429] rate-limited — sleeping {wait}s")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            return resp.json()

        except Exception as exc:
            wait = min(2 ** attempt, 60)
            if attempt < 2:
                print(f"  [retry {attempt+1}/3] {url} — sleeping {wait}s ({exc})")
                time.sleep(wait)
            else:
                _log_error("MAX_RETRIES", url, exc)
                return None

    return None


# ---------------------------------------------------------------------------
# Comment scraping — 1 request per post, top 5 comments, no sleep
# ---------------------------------------------------------------------------
def scrape_comments(subreddit: str, post_id: str, max_comments: int = 5) -> list[dict]:
    url  = f"{BASE_URL}/r/{subreddit}/comments/{post_id}.json"
    data = _get(url, params={"limit": max_comments, "depth": 1, "sort": "top"})
    if data is None:
        return []

    try:
        comment_listing = data[1]["data"]["children"]
    except (IndexError, KeyError, TypeError) as exc:
        _log_error("PARSE_ERROR", f"comments for {post_id}", exc)
        return []

    records = []
    for child in comment_listing:
        if child.get("kind") != "t1":
            continue
        c = child["data"]
        records.append({
            "comment_id":       c.get("id", ""),
            "post_id":          post_id,
            "body":             (c.get("body") or "")[:1000],
            "score":            c.get("score", 0),
            "controversiality": c.get("controversiality", 0),
            "depth":            c.get("depth", 0),
            "author":           c.get("author") or "[deleted]",
            "created_utc":      datetime.fromtimestamp(
                                    c.get("created_utc", 0), tz=timezone.utc
                                ).isoformat(),
            "parent_id":        c.get("parent_id", ""),
            "is_top_level":     (c.get("parent_id", "")).startswith("t3_"),
        })
        if len(records) >= max_comments:
            break

    return records


# ---------------------------------------------------------------------------
# Subreddit scraping — 1 search request + 1 comment request per post
# 0.5s delay only between subreddits (called from main/smoke test)
# ---------------------------------------------------------------------------
def scrape_subreddit(
    subreddit: str,
    query: str = "Claude",
    limit: int = 25,
) -> tuple[list[dict], list[dict]]:
    # Single search request — Reddit caps at 100 per page, we want 25
    url  = f"{BASE_URL}/r/{subreddit}/search.json"
    data = _get(url, params={
        "q":          query,
        "sort":       "top",
        "t":          "year",
        "limit":      min(limit, 100),
        "restrict_sr": True,
    })

    posts    = []
    comments = []

    if data is None:
        return posts, comments

    try:
        children = data["data"]["children"]
    except (KeyError, TypeError) as exc:
        _log_error("PARSE_ERROR", f"posts r/{subreddit}", exc)
        return posts, comments

    for child in children[:limit]:
        p = child["data"]
        post_id = p.get("id", "")

        posts.append({
            "post_id":           post_id,
            "title":             p.get("title", ""),
            "selftext":          (p.get("selftext") or "")[:2000],
            "score":             p.get("score", 0),
            "upvote_ratio":      p.get("upvote_ratio", 0.0),
            "num_comments":      p.get("num_comments", 0),
            "created_utc":       datetime.fromtimestamp(
                                     p.get("created_utc", 0), tz=timezone.utc
                                 ).isoformat(),
            "subreddit":         p.get("subreddit", subreddit),
            "url":               p.get("url", ""),
            "permalink":         BASE_URL + p.get("permalink", ""),
            "author":            p.get("author") or "[deleted]",
            "post_awards_count": p.get("total_awards_received", 0),
        })

        # 1 comment request per post, no sleep — Reddit allows this fine
        post_comments = scrape_comments(subreddit, post_id, max_comments=5)
        comments.extend(post_comments)

    print(f"Fetched {len(posts)} posts, {len(comments)} comments from r/{subreddit}")
    return posts, comments


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------
def save_to_csv(records: list[dict], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    pd.DataFrame(records).to_csv(filepath, index=False, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main — all 5 subreddits, 0.5s delay between them
# ---------------------------------------------------------------------------
def main(subreddits: list[str] = SUBREDDITS, limit: int = 100) -> None:
    today         = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    raw_dir       = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    posts_path    = os.path.join(raw_dir, f"reddit_posts_{today}.csv")
    comments_path = os.path.join(raw_dir, f"reddit_comments_{today}.csv")

    if os.path.exists(posts_path) or os.path.exists(comments_path):
        raise FileExistsError(
            f"Output files for {today} already exist. "
            "Delete them manually if you want to re-run today."
        )

    all_posts, all_comments = [], []

    for i, sub in enumerate(subreddits):
        posts, comments = scrape_subreddit(sub, limit=limit)
        all_posts.extend(posts)
        all_comments.extend(comments)
        if i < len(subreddits) - 1:
            time.sleep(0.5)

    save_to_csv(all_posts,    posts_path)
    save_to_csv(all_comments, comments_path)
    print(f"\nSaved {len(all_posts)} posts    → {posts_path}")
    print(f"Saved {len(all_comments)} comments → {comments_path}")


# ---------------------------------------------------------------------------
# Smoke test — limit=5, r/ClaudeAI only
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    posts, comments = scrape_subreddit("ClaudeAI", limit=5)

    df_posts    = pd.DataFrame(posts)
    df_comments = pd.DataFrame(comments)

    print(f"\n--- Smoke test results ---")
    print(f"Posts rows:    {len(df_posts)}")
    print(f"Comments rows: {len(df_comments)}")

    if not df_posts.empty:
        print("\nFirst post:")
        print(json.dumps(df_posts.iloc[0].to_dict(), indent=2, default=str))

    if not df_comments.empty:
        print("\nFirst comment:")
        print(json.dumps(df_comments.iloc[0].to_dict(), indent=2, default=str))