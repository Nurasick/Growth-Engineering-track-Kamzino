# Platform Notes

## Reddit (Public JSON API — not PRAW)
- **PRAW was dropped**: scraper uses `https://www.reddit.com/r/{sub}/search.json` directly with a custom User-Agent header. No client_id/secret needed.
- Rate limit: public API returns 429 with `Retry-After` header — scraper reads it. No fixed req/min documented but 0.5s delay between subreddits is sufficient in practice.
- Auth: none required for read-only public search
- Best subreddits: ClaudeAI, artificial, ChatGPT, MachineLearning, LocalLLaMA
- Comment fetch: uses `?depth=1&sort=top&limit=5` per post (1 request/post). No PRAW `replace_more` needed.
- Key fields confirmed present: controversiality, score, depth, upvote_ratio, total_awards_received
- `awards` field is NOT a list on the public API — use `total_awards_received` (int) instead
- `selftext` can be "[removed]" or empty string for deleted/link posts — truncate to 2000 chars
- Search endpoint: `/r/{sub}/search.json?q=Claude&sort=top&t=year&restrict_sr=true`

## YouTube (Data API v3)
- Quota: 10,000 units/day free
- Search costs 100 units, video detail costs 1 unit
- Strategy: search first (expensive), then batch detail lookups (cheap)
- Key engagement metric: comment_count / view_count

## Hacker News (Algolia API)
- No auth, no rate limit worth noting
- Base URL: https://hn.algolia.com/api/v1/search_by_date (use HTTPS — HTTP still works but redirects)
- Add 0.5s delay between pages to be polite
- Best signal: points + num_comments on stories mentioning Claude
- `numericFilters=created_at_i>1704067200` works cleanly for Jan 2024+ filtering
- Deduplication needed: queries "Claude AI" + "Anthropic" overlap — 1200 raw hits deduped to 1141 (~5% overlap)
- `_tags` array always present; first element is item type: `"story"` or `"comment"`
- `points` and `num_comments` are `null` on comments (not 0) — scraper coerces to 0 via `or 0`
- `story_text` is empty string for link posts (most HN stories); only populated for Ask/Show HN
- `comment_text` holds the comment body; `title` and `url` are null on comments
- Windows cp1251 terminal: avoid non-ASCII chars (`→`) in print statements — causes UnicodeEncodeError

## X / Twitter
- Free API v2: 500k tweet reads/month, 1 app/developer account
- snscrape broken on new X — use official API only
- Low priority: do after Reddit + YouTube + HN are working

## Platforms Skipped (document why)
- TikTok: no usable public API without login
- Instagram: heavily bot-protected
- LinkedIn: login-walled