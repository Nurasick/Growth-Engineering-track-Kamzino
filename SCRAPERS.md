# Part 1 — Scraper Implementation Documentation
## HackNU 2026 · Growth Engineering Track

---

## Platform Selection Rationale

We needed to cover every surface where Claude goes viral, not just where it is officially discussed.

| Platform | Why it was chosen |
|---|---|
| **Hacker News** | Ground-zero for AI technical discourse. Claude posts spike here first — validated by the Apr 1 cascade timestamp (01:13 UTC). Algolia exposes a clean search API with `numericFilters` for date ranges. |
| **Reddit** | Community validation layer. r/ClaudeAI, r/artificial, r/ChatGPT, r/MachineLearning, r/LocalLLaMA cover the full spectrum from fans to critics to migration. The public JSON API (`/search.json`) works without login or OAuth. |
| **X / Twitter** | Real-time narrative spread and status signaling. Two scrapers: (1) fxtwitter enrichment for known-handle seed data, (2) Playwright for historical search. X has no public API since March 2023 for non-paying developers — required creative engineering. |
| **YouTube** | Explanation and creator amplification layer. Data API v3 provides structured video stats and comments. Community creator coverage outperformed official channels by 29× — this platform was non-optional. |

Platforms we explicitly excluded: Instagram (no public API without login), LinkedIn (same), TikTok (same). Documented limitation in README.

---

## Scraper Implementations

### 1. Hacker News — `scrapers/hn_scraper.py`

**Method:** Algolia HN Search API (`hn.algolia.com/api/v1/search_by_date`)

**How it works:**
- Queries: `["Claude AI", "Anthropic"]`
- Fetches both `story` and `comment` tags separately (comments often discuss Claude without it being in the title)
- `numericFilters=created_at_i>{unix_timestamp}` enforces the time window
- Paginated: configurable `--pages` flag, 100 hits per page max
- Deduplicates on `objectID` before writing

**Key flags:**
```bash
python scrapers/hn_scraper.py --days 90 --pages 10   # full 90-day run
python scrapers/hn_scraper.py --smoke                 # fetch 20 items, no file write
```

**What broke and how we handled it:**
- Off-topic results: Algolia returns posts where "Claude" appears in comments, not only titles. We kept all results and noted the noise in findings (power-law analysis still holds at n=3,779).
- Rate limiting: implemented exponential backoff (1s → 2s → 4s) with a 3-retry cap; 429 responses trigger `min(2^attempt, 60)` wait.
- Duplicate run protection: raises `FileExistsError` if today's file already exists; `--overwrite` flag bypasses this.

**Output schema:**
```
object_id, title, points, num_comments, author, created_at, url,
story_text (≤2000 chars), comment_text (≤1000 chars), tags, query
```

**Volume:** 3,779 items over 90 days (Jan–Apr 2026), ~2 queries × 2 tag types × 10 pages.

---

### 2. Reddit — `scrapers/reddit_scraper.py`

**Method:** Reddit public JSON API — no OAuth, no credentials required

**How it works:**
- Endpoint: `reddit.com/r/{subreddit}/search.json`
- Subreddits: `ClaudeAI, artificial, ChatGPT, MachineLearning, LocalLLaMA`
- Parameters: `sort=top`, `t=year`, `limit=100`, `restrict_sr=True`
- Per-post comment enrichment: 1 additional request per post to `reddit.com/r/{sub}/comments/{id}.json`, fetches top 5 comments (`depth=1`, `sort=top`)
- 0.5s delay between subreddits (not per-post — Reddit tolerates rapid per-post requests)

**What broke and how we handled it:**
- The public JSON API occasionally returns 429s with a `Retry-After` header; we respect that header directly instead of using a fixed backoff.
- Reddit soft-limits results to ~100 per search page. We accept this — going deeper on a single subreddit has diminishing value vs. cross-subreddit breadth.
- Deleted authors appear as `[deleted]` in the API; we pass this through as-is.

**Output schema:**
Posts file: `post_id, title, selftext, score, upvote_ratio, num_comments, created_utc, subreddit, url, permalink, author, post_awards_count`
Comments file: `comment_id, post_id, body, score, controversiality, depth, author, created_utc, parent_id, is_top_level`

**Volume:** 125 posts + 584 comments across 5 subreddits. Additional 45 posts + 130 comments collected for Higgsfield competitor analysis (r/aivideo, r/filmmakers, r/videography).

---

### 3. X / Twitter — `scrapers/x_scraper.py` (fxtwitter enrichment)

**Method:** FxTwitter public API (`api.fxtwitter.com/status/{tweet_id}`) — no auth required

**The problem:** X shut down free API access in March 2023. The v2 free tier gives 500k reads/month and excludes engagement metrics. We needed full engagement data (likes, retweets, replies, bookmarks, views).

**How it works:**
- Seed phase: known handles (`AnthropicAI`, `ClaudeAI`, `bcherny`, `sama`, `swyx`, `karpathy`, etc.) are crawled via RSS/Nitter and Google dorks (`site:x.com "Claude Code"`, etc.) to collect tweet URLs.
- Enrichment phase: for each tweet URL, hits FxTwitter to get the full structured payload including engagement metrics.
- FxTwitter is a public tweet embed proxy that resolves the full tweet object including counts.

**Engagement formula (decided during project):**
```python
eng = likes + (retweets * 2) + (replies * 2) + bookmarks
# views stored separately as reach metric
```

**What broke:**
- Google dorks return inconsistent results (bot detection, caching). We accepted the seed-based limitation and documented it: the dataset covers known handles, not organic unknown-account content.
- Some tweets return 404 on FxTwitter (deleted/protected). Skipped silently.

**Output schema:**
`tweet_id, author, content, created_at, likes, retweets, replies, bookmarks, views, url, is_official`

**Volume:** 82 seed tweets with full engagement metrics.

---

### 4. X / Twitter — `scrapers/x_playwright_scraper.py` (Playwright browser)

**Method:** Real Chromium browser via Playwright — intercepts X's internal search API responses

**Why Playwright was necessary:**

X's internal search API (`api.twitter.com/2/search/adaptive.json`) requires `x-client-transaction-id` — a request-specific signed header generated by X's JavaScript client. It cannot be replicated with a plain HTTP client: the value changes per-request and is computed by obfuscated JS.

Playwright runs a real Chromium browser, which generates this header natively as part of the browser's normal operation. We intercept the JSON responses that the browser receives — not the HTML page itself.

**How it works:**
1. Browser launches with stored cookies (`X_AUTH_TOKEN`, `X_CT0` from `.env`) — requires a logged-in X session.
2. Navigates to `x.com/search?q={query}&src=typed_query&f=live`.
3. Intercepts responses matching `adaptive.json` or `SearchTimeline`.
4. Parses tweet objects from the nested `data.search_by_raw_query.search_timeline` structure.
5. After parsing a page, scrolls down to load more tweets. Repeats until the date limit or max-tweets limit is hit.
6. FxTwitter enrichment pass: for tweets missing engagement data, fires a secondary API call.

**Historical run:**
```bash
python scrapers/x_playwright_scraper.py --since 2025-01-01 --until 2026-04-01
# → 1,668 historical tweets, Jan 2025 → Apr 2026
```

**What broke and how we handled it:**
- X's response schema changed mid-project. The tweet object path shifted from `legacy` to `core.user_results.result.legacy`. Added multiple field-path fallbacks.
- Some search result pages return promoted tweets with no real tweet data. These are filtered by checking for an `id_str` field.
- Playwright can lose the browser context on long runs. Added `--max-tweets` cap and a `time.sleep(1)` between scroll batches to reduce detection.
- `x-client-transaction-id` issue: fully bypassed by the browser approach — the browser generates it, we never need to reproduce it.

**Setup:**
```bash
pip install playwright
python -m playwright install chromium
# Add to .env:
# X_AUTH_TOKEN=<auth_token cookie value>
# X_CT0=<ct0 cookie value>
```

**Output schema:**
`tweet_id, author, content, created_at, likes, retweets, replies, bookmarks, views, url, query, is_official, followers_count`

**Volume:** 384 tweets from last 48h (live run) + 1,668 historical tweets (Jan 2025 → Apr 2026).

---

### 5. YouTube — `scrapers/youtube_scraper.py`

**Method:** YouTube Data API v3 — requires `YOUTUBE_API_KEY` in `.env`

**How it works:**
Three-phase design to minimize quota usage (API cost: 100 units/search, 1 unit/batch stats, 1 unit/comment page):

1. **Phase 1 — search (`search.list`):** queries `["Claude AI", "Anthropic Claude", "Claude vs GPT", "Claude Sonnet", "Anthropic"]`, collects video IDs. Returns only `id` part to save quota (no snippet).
2. **Phase 2 — batch stats (`videos.list`):** fetches `snippet + statistics + contentDetails` for batches of 50 video IDs. Single API call per 50 videos.
3. **Phase 3 — comments (`commentThreads.list`):** top 20 comments per video, `order=relevance`, `textFormat=plainText`.

Deduplicates video IDs across queries before hitting Phase 2.

**What broke and how we handled it:**
- Quota exhaustion (HTTP 403): logged to `errors.log`, skips remaining videos for that run rather than crashing. Subsequent batch runs fill the gaps.
- Some videos have comments disabled → Phase 3 returns 403 for that video ID. Caught and skipped.
- `publishedAfter` filter uses a dynamic 7-day window from run time; for the committed dataset we used a 14-day window.

**Output schema:**
Videos: `video_id, title, description (≤1000 chars), channel, published_at, view_count, like_count, comment_count, duration_sec, url`
Comments: `comment_id, video_id, author, body (≤1000 chars), like_count, published_at`

**Volume:** 86 videos + 293 comments over last 2 weeks.

---

## Unified Output Schema

All scrapers write date-stamped CSVs to `data/raw/`. The normalization step (`analysis/normalize_sources.py`) converts them to a unified schema:

| Field | Description |
|---|---|
| `post_id` | Platform-native ID |
| `title` | Post/tweet/video title or first 280 chars of content |
| `platform` | `hn`, `reddit`, `x`, `youtube` |
| `author` | Username |
| `created_at` | ISO 8601 UTC timestamp |
| `engagement_score` | Platform-weighted: HN `points`, Reddit `score + comments×3`, X `likes + RT×2 + replies×2 + bookmarks`, YouTube `views` |
| `secondary_metric` | Secondary signal: HN `num_comments`, Reddit `score`, X `views` (reach), YouTube `like_count` |
| `url` | Canonical post URL |
| `raw_text` | Content preview (≤500 chars) |
| `subreddit` | Reddit only |
| `spike_type` | Set by classifier: `breakthrough`, `tutorial`, `comparison`, `personal`, `meme` |
| `velocity` | Set by ranker: HN gravity formula score |

---

## Error Handling Architecture

All scrapers share the same error pattern:

```
_log_error(error_type, context, exc)
    → writes to data/errors.log with [PLATFORM] tag

_get(url, params)
    → 3 retries with exponential backoff (1s, 2s, 4s, max 60s)
    → 429 → respect Retry-After or backoff
    → returns None on failure (caller skips, pipeline continues)
```

No scraper raises an exception to the pipeline. Partial failures produce partial outputs; the pipeline logs what it got and continues.

---

## Reproducing the Dataset

The committed raw data in `data/raw/` does not need to be re-scraped. Run:

```bash
python pipeline.py --skip-scrape   # uses committed data, <30s
```

To re-scrape from scratch (requires `YOUTUBE_API_KEY` and X cookies):
```bash
cp .env.example .env   # fill in YOUTUBE_API_KEY, X_AUTH_TOKEN, X_CT0
python pipeline.py     # full live scrape, ~3 min
```
