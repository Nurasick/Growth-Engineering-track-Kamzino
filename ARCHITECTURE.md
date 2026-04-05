# Architecture: Weekly Competitive Intelligence System
## HackNU 2026 · Growth Engineering Track

A weekly pipeline that scrapes 4 platforms, unifies and classifies the data, ranks posts by velocity, detects cross-platform narrative cascades, and generates an AI-written counter-playbook for competing products using Claude, Gemini, or OpenAI.

---

## Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SOURCES (public, no auth)                 │
│   Hacker News      X platform      YouTube      Reddit       │
└────────────┬───────────────┬──────────────┬────────────┬────┘
             │               │              │            │
             ▼               ▼              ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                  COLLECTION  (scrapers/)                     │
│  hn_scraper.py        reddit_scraper.py                      │
│  x_scraper.py /       youtube_scraper.py                     │
│  x_playwright_scraper.py                                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
                   data/raw/*.csv
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            NORMALIZATION  (normalize_sources.py)             │
│  • unified schema across all 4 platforms                     │
│  • canonical UTC timestamps                                  │
│  • per-platform engagement score (see Engagement Scoring)    │
│  • author metadata normalization                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
              data/processed/unified_posts.csv
                    (2,177 posts)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│            CLASSIFICATION  (spike_classifier.py)             │
│  • keyword-based, deterministic, < 1s on full dataset        │
│  • 5 spike types: breakthrough, tutorial, comparison,        │
│    personal, meme                                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
             data/processed/spike_classified.csv
                    (2,177 classified)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      ANALYSIS                                │
│                                                              │
│  growth_frontpage.py       → velocity ranking (HN gravity)   │
│  cascade_detector.py       → cross-platform narrative groups │
│  amplifier_watchlist.py    → creator / author scoring        │
└──────────┬────────────────┬────────────────────────────────┘
           │                │
           ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                      DELIVERY                                │
│  data/processed/growth_frontpage.csv   (1,962 ranked)        │
│  data/processed/spike_classified.csv                         │
│  data/processed/cascade_events.csv                           │
│  data/processed/virality_timeline.html (dashboard)           │
│  data/amplifier_watchlist.csv                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│           COUNTER-PLAYBOOK GENERATION                        │
│  generate_counter_playbook.py                                │
│  • reads processed CSVs, computes growth metrics             │
│  • builds structured context block (playbook_context.json)   │
│  • calls Claude / Gemini / OpenAI with a data-grounded prompt│
│  • writes COUNTER_PLAYBOOK_GENERATED.md                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Collection

Four scrapers, each writing a dated CSV to `data/raw/`:

| Scraper | Source | Output file |
|---|---|---|
| `hn_scraper.py` | Algolia HN API | `hn_items_YYYY-MM-DD.csv` |
| `reddit_scraper.py` | Reddit public JSON | `reddit_posts_YYYY-MM-DD.csv`, `reddit_comments_YYYY-MM-DD.csv` |
| `x_scraper.py` / `x_playwright_scraper.py` | X platform (Playwright + fxtwitter) | `x_case_raw.csv` |
| `youtube_scraper.py` | YouTube Data API v3 | `youtube_videos_YYYY-MM-DD.csv` |

All scrapers: retry ×3 with backoff, pagination handling, deduplication on ID. If today's file already exists, the pipeline skips the scraper and uses the cached file.

### Normalization

`normalize_sources.py` merges all raw files into one unified schema. Every row gets the same fields regardless of source platform. If today's file is missing, it falls back to the most recently dated file automatically.

**Engagement Scoring** — each platform uses a different native metric:

| Platform | `engagement_score` | Why |
|---|---|---|
| HN | raw points (upvotes) | community quality signal, absolute count |
| Reddit | raw upvote score | community quality signal, absolute count |
| X platform | (retweets + replies) / views × 100 | interaction rate %, normalizes for reach |
| YouTube | (likes + comments) / views × 100 | interaction rate %, normalizes for reach |

HN and Reddit scores are absolute — compare them with each other. X platform and YouTube scores are percentages — compare them with each other. Do not compare across groups.

### Classification

`spike_classifier.py` labels every post with one of 5 spike types using keyword matching:

| Spike type | Signal keywords (examples) |
|---|---|
| `breakthrough` | "new model", "just released", "claude 3/4", "funding", "research paper" |
| `tutorial` | "how to", "step by step", "guide", "workflow", "prompt" |
| `comparison` | "vs ", "versus", "better than", "switched from", "benchmark" |
| `personal` | "i built", "my experience", "changed my", "personal" |
| `meme` | "lol", "lmao", "😂", "bro ", "shitpost" |

Deterministic and free. Runs in under 1 second on the full dataset.

### Analysis

**`growth_frontpage.py`** — ranks all classified posts by velocity using the HN gravity formula:

```
velocity = normalized_score / (age_hours + 2) ^ 1.8
```

Scores are normalized per platform against a cap before ranking, so a 500-point HN post and a 5,000-upvote Reddit post are comparable. Output: `growth_frontpage.csv` (1,962 rows, sorted by velocity descending).

**`cascade_detector.py`** — groups posts across platforms that cover the same story within a sliding time window. Detects sequences like HN → X platform → Reddit where the same narrative propagates across surfaces. Output: `cascade_events.csv`, `cascade_report.txt`.

**`amplifier_watchlist.py`** — scores creators and authors by composite signal: views-to-follower ratio, posting velocity on topic, engagement rate. Surfaces breakout accounts regardless of follower count. Output: `amplifier_watchlist.csv`.

### Delivery

All outputs land in `data/processed/`:

| File | Contents |
|---|---|
| `growth_frontpage.csv` | All posts ranked by velocity, with spike type and age |
| `spike_classified.csv` | All posts with spike type labels |
| `cascade_events.csv` | Narrative cascades detected across platforms |
| `virality_timeline.html` | Self-contained HTML dashboard, no server needed |
| `amplifier_watchlist.csv` | Scored creator / author list |

### Counter-Playbook Generation

`analysis/generate_counter_playbook.py` is the only step that calls an external AI API.

**What it does:**
1. Reads `spike_classified.csv`, `growth_frontpage.csv`, `unified_posts.csv`, `amplifier_watchlist.csv`
2. Computes growth metrics: spike type distribution, per-platform engagement (median + percentiles), timing patterns (HN by UTC hour, Reddit by weekday), velocity decay by age bucket, top creator amplification ratios, title word lift
3. Saves the full context to `data/processed/playbook_context.json` (audit trail)
4. Builds a structured prompt with metric definitions and data-grounded instructions
5. Calls Claude, Gemini, or OpenAI (auto-detected from `.env`)
6. Writes `COUNTER_PLAYBOOK_GENERATED.md`

**Supported providers** (set in `.env`):

| Provider | Model | Key |
|---|---|---|
| Anthropic | claude-haiku-4-5 | `ANTHROPIC_API_KEY` |
| Google | gemini-2.5-flash | `GEMINI_API_KEY` |
| OpenAI | gpt-4o-mini | `OPENAI_API_KEY` |

Auto-detects whichever key is present. Override with `PLAYBOOK_AI_PROVIDER=anthropic|gemini|openai`.

---

## How to Run

```bash
# Full run — scrape all sources + full analysis + delivery
python pipeline.py

# Skip scrapers — re-analyze existing raw data
python pipeline.py --skip-scrape

# Fast demo mode — fewer pages, lower limits
python pipeline.py --demo

# Generate counter-playbook (requires processed data + one AI API key)
python analysis/generate_counter_playbook.py --product higgsfield
python analysis/generate_counter_playbook.py --product higgsfield --provider anthropic
```

---

## How X Platform Data Is Collected

Standard Python libraries for scraping X (twikit, twscrape, snscrape) all fail in 2025 with 403 responses due to `x-client-transaction-id` — a header generated client-side by Twitter's JavaScript using a proprietary algorithm. No Python implementation can reproduce it.

**Solution:** run a real Chromium browser via Playwright. The browser generates the header natively. We intercept XHR responses before they reach the page:

```python
async def handle_response(response: Response):
    if ("search/adaptive" in response.url or "SearchTimeline" in response.url) and response.status == 200:
        body = await response.json()
        response_queue.append(body)

page.on("response", handle_response)
await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
await asyncio.sleep(5)
```

Auth cookies (`auth_token`, `ct0`) are injected from a real logged-in session. No paid tier, no API contract.

**Historical data:** X search only returns ~7 days on the "Latest" tab. To collect 16 months (Jan 2025 → Apr 2026) we split queries into monthly date-bounded chunks — 64 searches total (4 queries × 16 months), each in Top mode to surface highest-engagement posts per period.

**fxtwitter enrichment:** Playwright captures tweet IDs and text but author data is often missing from GraphQL responses. Every tweet is enriched via `api.fxtwitter.com/i/status/{tweet_id}` — a public proxy returning structured JSON with author followers, views, likes, retweets, and bookmarks.

Result: **1,668 tweets across Jan 2025 → Apr 2026** at $0 cost.

---

## Error Recovery

- **Retry with backoff** — all scrapers retry 3 times (1s → 2s → 4s) before failing
- **Per-step graceful failure** — `pipeline.py` logs failure and continues to the next step; one broken scraper does not halt the run
- **Stale data fallback** — if today's raw file is missing, `normalize_sources.py` automatically uses the most recently dated file
- **Cached file skip** — if today's dated file already exists, the scraper is skipped entirely

---

## Known Tradeoffs

| Decision | Why | What we gave up |
|---|---|---|
| fxtwitter instead of official X API | Free, no auth, full engagement data | Rate-limited after ~100 requests/session; not suitable for real-time |
| Flat CSV instead of database | Zero setup, human-readable, git-diffable | No cross-query analytics, no timestamp index |
| Keyword classifier instead of LLM | Deterministic, free, < 1s on full dataset | Lower accuracy on ambiguous posts; LLM would cost $0.01–0.05/post |
| Weekly cron instead of streaming | Simple, sufficient for intelligence use case | Misses events between runs; real-time would need polling or webhooks |
| Instagram / LinkedIn / TikTok excluded | No public API without login | ~30% of Claude discourse not captured |
