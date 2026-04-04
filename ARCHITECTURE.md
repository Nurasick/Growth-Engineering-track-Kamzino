# Part 3 — The Machine: Automated Intelligence Pipeline
## HackNU 2026 · Growth Engineering Track

> A competitive intelligence system that a growth team checks every Monday morning.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES (public, no auth)                      │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  HN      │  │  Reddit  │  │  X/Twitter   │  │  YouTube             │   │
│  │ Algolia  │  │ JSON API │  │  fxtwitter   │  │  Data API v3         │   │
│  │ (free)   │  │  (free)  │  │  (free)      │  │  (free tier: 10K/day)│   │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘  └──────────┬───────────┘   │
└───────│─────────────│───────────────│──────────────────────│───────────────┘
        │             │               │                      │
        ▼             ▼               ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     COLLECTION LAYER  (scrapers/)                           │
│                                                                             │
│  hn_scraper.py     reddit_scraper.py  x_scraper.py    youtube_scraper.py   │
│  • retry(3)        • retry(3)         • fxtwitter API  • batch fetch        │
│  • last 7 days     • 5 subreddits     • DDG+Bing+Brave • engagement metrics │
│  • dedup on ID     • posts+comments   • engagement     • comments           │
│                                       • amplifier list                      │
│                         ↓                                                   │
│              [Step 3.5] amplifier_watchlist.py                              │
│              Score every author → auto-expand handle list                   │
│              (self-expanding: no human needed after bootstrap)              │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼  data/raw/*.csv  (date-stamped)
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TRANSFORM LAYER  (analysis/)                            │
│                                                                             │
│  normalize_sources.py                                                       │
│  • unified schema across all platforms                                      │
│  • ISO timestamp normalization                                              │
│  • engagement score normalization (platform-aware)                          │
│         ↓  data/processed/unified_posts.csv                                 │
│                                                                             │
│  spike_classifier.py                                                        │
│  • keyword signals + platform priors                                        │
│  • 5 types: breakthrough / tutorial / comparison / personal / meme          │
│  • confidence score per post                                                │
│         ↓  data/processed/spike_classified.csv                              │
│                                                                             │
│  growth_frontpage.py                                                        │
│  • HN gravity formula: score / (age_hours + 2)^1.8                         │
│  • normalized cross-platform (HN cap 1K, Reddit 10K, YouTube 200K)         │
│  • deduplication by title+platform                                          │
│         ↓  data/processed/growth_frontpage.csv                              │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DELIVERY LAYER                                          │
│                                                                             │
│  virality_timeline.py  →  data/processed/virality_timeline.html            │
│  • Chart.js stacked bar by month                                            │
│  • 5 spike types colored                                                    │
│  • key event annotations                                                    │
│  • top 20 posts table                                                       │
│                                                                             │
│  Alert check (in pipeline.py)                                               │
│  • velocity > 0.5 AND age_hours < 12                                        │
│  • prints to stdout (→ Slack webhook at prod scale)                         │
│                            ↓                                                │
│                   ┌────────────────┐                                        │
│                   │  HUMAN REVIEW  │  ← only triggered by alert signal     │
│                   └────────────────┘                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                               ↑
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION LAYER                                     │
│                                                                             │
│  Current:  cron  →  0 8 * * 1  python pipeline.py                          │
│  At scale: Prefect (see tool justification below)                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## How We Actually Got X Data: The Playwright Story

This is the most technically interesting part of the data collection — and the reason most competitive intelligence tools have incomplete X/Twitter data.

### The Problem: x-client-transaction-id

Every Python library for scraping Twitter — twikit, twscrape, snscrape, direct requests — fails in 2025 with a 403 Forbidden response. The reason is a header called `x-client-transaction-id`.

Twitter introduced this header as an anti-bot measure. The value is generated client-side using a proprietary algorithm that:
1. Takes the current URL, request method, and a rotating key stored in Twitter's JavaScript bundle
2. Runs a binary XOR/interpolation operation across the key bytes
3. Produces a token that Twitter's servers validate server-side

The problem: this algorithm runs in JavaScript inside the browser. No Python implementation exists. When `twikit` tries to generate the token server-side:

```
ClientTransaction.__init__: KeyError: 'Couldn't get KEY_BYTE indices'
```

The library fails because it can't reproduce the browser's cryptographic environment. Direct `requests` to `twitter.com/i/api/2/search/adaptive.json` returns 403 immediately — the header is missing.

### The Solution: Real Browser, Intercepted Responses

Instead of reverse-engineering the header, we run a real Chromium browser via Playwright. The browser generates `x-client-transaction-id` natively, as part of normal JavaScript execution. We intercept the XHR responses before they reach the page:

```python
async def handle_response(response: Response):
    url = response.url
    # Twitter's internal search API — contains the full tweet JSON
    if ("search/adaptive" in url or "SearchTimeline" in url) and response.status == 200:
        body = await response.json()
        response_queue.append(body)

page.on("response", handle_response)

# domcontentloaded, NOT networkidle — X constantly pings analytics, never goes idle
await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
await asyncio.sleep(5)  # let XHR responses arrive
```

We inject auth cookies (`auth_token`, `ct0`) from a real logged-in session. The browser navigates to `x.com/search?q=...`, generates all required headers automatically, and we intercept the JSON responses that Twitter sends back — without ever needing to parse the HTML or reverse-engineer the auth.

### Historical Data: Monthly Date Chunks

Twitter's search only returns ~7 days of results on the "Latest" tab. To collect 16 months of data (Jan 2025 → Apr 2026), we used date filters and split into monthly chunks:

```python
def _monthly_chunks(since: str, until: str) -> list[tuple[str, str]]:
    """64 searches = 4 queries × 16 months"""
    ...

# Each search uses Top mode (no &f=live) — surfaces highest-engagement 
# tweets from the period, not just the most recent
tab_param = "" if top_mode else "&f=live"
encoded = full_query.replace(' ', '%20').replace(':', '%3A')
search_url = f"https://x.com/search?q={encoded}&src=typed_query{tab_param}"
```

Result: **1,668 tweets across Jan 2025 → Apr 2026**, enriched with author data and engagement metrics via fxtwitter API.

### fxtwitter Enrichment

The Playwright scraper captures tweet IDs and text, but author data is often missing from GraphQL responses. We enrich every tweet via `api.fxtwitter.com/i/status/{tweet_id}` — a public proxy that returns structured JSON including `author.screen_name`, `author.followers`, `likes`, `retweets`, `views`, and `bookmarks`.

```python
r = session.get(f"https://api.fxtwitter.com/i/status/{tid}", timeout=8)
if r.status_code == 200:
    d = r.json().get("tweet", {})
    row["author_followers"] = d.get("author", {}).get("followers", 0)
    row["views"]    = d.get("views", 0)
    row["likes"]    = d.get("likes", 0)
```

This pipeline is how we confirmed that `@bcherny` (Claude Code engineer) generated 44.3M views from 124 personal tweets — data that required both the Playwright historical scrape and the fxtwitter enrichment to surface.

### Why This Matters for the Growth Intelligence Use Case

Standard X monitoring tools (Brandwatch, Sprout Social, native X API) either require expensive paid tiers or miss historical context. Our Playwright approach:
- Costs **$0** (uses existing auth cookies from a regular account)
- Reaches **16 months of history** (not just 7 days)
- Returns **full engagement metrics** (views, likes, retweets, bookmarks, follower count)
- Is **self-contained** — no API keys, no paid tiers, no rate limit negotiation

The tradeoff: it requires a headless browser (~500MB RAM) and runs slower than a direct API call (~5 seconds per search query). Acceptable for a weekly intelligence run; not suitable for real-time streaming.

---

## Automated Outreach System

The growth intelligence pipeline now extends beyond monitoring into automated outreach — knowing not just what's happening, but who to contact and what to say.

![Automation System](data/charts/chart_automation_system.png)

### Three New Layers

**Trigger Engine (runs every 30 min)**
Detects three signal types:
- Competitor launch: velocity > 0.3, age < 4h, competitor keyword → fire comparison brief
- Virality spike: velocity > 0.5, age < 6h, Higgsfield mention → fire amplification brief
- Celebrity use: author_followers > 1M, mentions Higgsfield → fire quote-tweet brief

**Brief Generator (fires on trigger)**
Auto-populates a content brief from:
- Creator watchlist (scored weekly by views/follower ratio × topic overlap × posting velocity)
- Playbook rules engine (comparison frame for competitor trigger, scandal-adjacent for celebrity, personal story for organic spike)
- Platform priority sequence (X same day → YouTube 24h → Reddit weekend)
- UTM-tagged Pro access link per creator

**Delivery**
- Slack webhook: brief lands in team channel, human approves and sends in 15 minutes
- Weekly dashboard: virality_timeline.html, velocity feed, spike breakdown
- Creator K-factor report: signups per UTM link at 72h — which creator to double down on

### Creator Scoring Formula

```python
creator_score = (
    (median_views / follower_count) * 0.4   # the key signal — @MangoLassC got 415x ratio
  + (posts_per_week)                * 0.2   # posting velocity (fast reactors matter)
  + (topic_overlap_score)           * 0.3   # covers AI video / filmmaking
  + (engagement_rate)               * 0.1   # likes+comments / views
)
```

This formula is derived from our data finding that follower count is not the constraint — 8.1% of non-mega-account tweets in our dataset crossed 100K views. @MangoLassC (6.8K followers) got 2.85M views (415x multiplier) on a genuine reaction tweet. The views/follower ratio predicts breakout potential better than raw follower count.

---

## Automated vs Human-Reviewed Steps

| Step | Automated? | Justification |
|---|---|---|
| Scraping (HN, Reddit, X, YouTube) | ✅ Fully automated | Deterministic HTTP calls, error handling built in, no judgment needed |
| Amplifier scoring | ✅ Fully automated | Formula-based (ER × amplification × log(frequency)), no edge cases requiring human input |
| Normalization | ✅ Fully automated | Rules-based schema mapping, platform-specific parsers |
| Spike classification | ✅ Fully automated | Keyword signals + platform priors. Confidence score surfaces low-confidence posts |
| Velocity ranking | ✅ Fully automated | Pure math (HN gravity formula) |
| Dashboard generation | ✅ Fully automated | Deterministic from ranked data |
| **Alert triage** | ⚠️ Human triggered | System flags; human decides if it's real signal or noise. Context matters: is "leaked" a drama post or a genuine security issue? Algorithm can't distinguish. |
| **Counter-playbook execution** | ❌ Human only | Creator outreach, timing decisions, budget allocation require business judgment |
| **Amplifier bootstrap list** | ❌ Human once | Initial 5–10 seed handles require domain knowledge. After bootstrap, system self-expands. |

**Design principle:** Automate everything that is deterministic or formula-based. Require humans only where context, judgment, or business decisions are needed.

---

## Tool Recommendations (with justification)

### Orchestration

| Option | Current choice | Why |
|---|---|---|
| **cron** | ✅ Yes (now) | Zero infrastructure, sufficient for weekly cadence, no dependencies |
| **Prefect** | At 10x scale | DAG visibility, retry policies with backoff, failure alerting, run history. Better than Airflow for small teams (no Celery/Redis required). |
| **Airflow** | No | Overengineered for a 9-step weekly job. Ops overhead not justified at this scale. |
| **GitHub Actions** | Alternative | Free, version-controlled, easy for team. Lacks long-running job support. |

**Recommendation:** cron now → Prefect if team grows past 3 people or pipeline exceeds 30 minutes.

### Storage

| Option | Current | Why |
|---|---|---|
| **Flat CSV** | ✅ Yes (now) | Zero setup, human-readable, git-diffable, sufficient for 5K rows |
| **SQLite** | At 50K rows | Single-file DB, no server, cross-query support (GROUP BY, JOIN across platforms) |
| **Postgres** | At 10x scale | Index on `created_at`, `platform`, `spike_type`. Full-text search on titles. |

### Alerting

| Option | Current | Why |
|---|---|---|
| **stdout** | ✅ Yes (now) | Sufficient for hackathon/demo |
| **Slack webhook** | Production | One-line addition to `check_alerts()`. Zero cost. Delivers to team channel. |
| **PagerDuty** | Overkill | For on-call systems, not a weekly intelligence report |

---

## Error Recovery Design

Every scraper implements:
1. **Retry with exponential backoff** (3 attempts, 1→2→4s waits)
2. **Per-step graceful failure** — `pipeline.py` logs failure and continues to next step. One broken scraper doesn't halt the whole run.
3. **Cached data fallback** — if today's file doesn't exist, `normalize_sources.py` finds the most recently dated file automatically. Stale data is better than no data.
4. **Error log** — `data/errors.log` captures all failed requests with timestamp, source, and exception.

```python
# What happens when Reddit is down on Monday morning:
Step 2 (Reddit): FAILED (exit 1) — continuing     ⚠️
Step 3 (X):      Done                             ✅
Step 5 (Normalize): uses last week's reddit_posts_*.csv automatically
# Growth team gets report with week-old Reddit data, clearly labelled.
```

---

## Data Freshness Policy

| Data | Max staleness | How enforced |
|---|---|---|
| HN, Reddit | 7 days | Scrapers filter `created_at > 7 days ago` at source |
| X (Twitter) | No filter (historical seed) | Bootstrap URLs cover multiple years; discovery queries return recent results |
| YouTube | 7 days | `publishedAfter` filter in API call |
| Velocity ranking | Recalculated every run | `age_hours` computed at runtime from `datetime.now()` |

---

## Cost Estimates

### Current scale (weekly, ~5K posts/run)

| Component | Cost |
|---|---|
| HN (Algolia API) | $0 — unlimited free |
| Reddit (public JSON) | $0 — no auth required |
| X (fxtwitter) | $0 — public proxy API |
| YouTube (Data API v3) | $0 — 10,000 units/day free; our run uses ~600 units |
| Compute (local) | $0 — runs in ~3 minutes on any laptop |
| **Total** | **$0/month** |

### 10x scale (~50K posts/run, daily cadence)

| Component | Cost |
|---|---|
| YouTube API (10x queries) | ~$50/month (quota top-up) |
| VPS for cron (e.g. DigitalOcean 1GB) | $6/month |
| Storage (Postgres, ~500MB) | $0 — fits on same VPS |
| Slack alerting | $0 — webhook is free |
| **Total** | **~$56/month** |

At 100x scale (500K posts, multiple competitors monitored): ~$200–400/month (YouTube quota, larger VPS, S3 for CSV archival).

---

## Alert Design

**Signal:** `velocity > 0.5 AND age_hours < 12`

This means: a post is gaining momentum right now, not just popular historically.

```
velocity = normalized_score / (age_hours + 2)^1.8

A post scoring velocity > 0.5 with age < 12h means:
  - It has already accumulated significant engagement
  - It's still in its growth window
  - Something is happening RIGHT NOW
```

**Alert categories by spike type:**

| Spike type + high velocity | What it means | Human action |
|---|---|---|
| `breakthrough` | Product launch or announcement gaining traction | Check if it's a Claude release; prepare response content |
| `personal` | Organic user story going viral | Amplify via official channels while it's hot |
| `meme` | Something funny/controversial spreading | Monitor; decide if it needs a response |
| `comparison` | Claude vs competitor framing spreading | Check sentiment; engage if inaccurate |
| `tutorial` | Tutorial going viral | Share it officially; low urgency |

**Production implementation (one additional line in `pipeline.py`):**
```python
import requests
requests.post(SLACK_WEBHOOK_URL, json={"text": f"🚨 {spike_type}: {title} | velocity={velocity}"})
```

---

## Prototype Evidence

`pipeline.py` is a working prototype covering all 9 steps end-to-end:

```bash
$ python pipeline.py --skip-scrape
# Runs in < 30 seconds
# Outputs: unified_posts.csv (5,083 rows), spike_classified.csv (855 rows),
#          growth_frontpage.csv (692 ranked posts), virality_timeline.html
```

Live demo output from April 4, 2026:
- **#1 velocity post:** "Tell HN: Anthropic no longer allowing Claude Code subscriptions to use OpenClaw" — 766 pts, 16h old, velocity=0.413
- **Alert triggered:** None (no post met velocity > 0.5 AND age < 12h at time of run)

---

## Known Tradeoffs

| Decision | Why | What we gave up |
|---|---|---|
| fxtwitter instead of official X API | Free, no auth, returns full engagement data | Rate limited after ~100 requests/session; not suitable for real-time monitoring |
| Flat CSV instead of database | Zero setup, works on any machine, teammates can open in Excel | No cross-query analytics, no index on timestamps |
| Keyword classifier instead of LLM | Deterministic, free, fast (855 posts in <1s) | Lower accuracy on ambiguous posts; LLM would classify better but costs $0.01–0.05/post |
| Weekly cron instead of streaming | Simpler, sufficient for intelligence use case | Misses events that happen between Monday runs; real-time would need webhooks or polling |
| Instagram/LinkedIn/TikTok excluded | No public API without login | Missing ~30% of Claude discourse surface area |
