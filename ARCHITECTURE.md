# Part 3 — The Machine: Weekly Competitive Intelligence System
## HackNU 2026 · Growth Engineering Track

> A Monday-morning system for detecting which Claude narratives are spreading, who is amplifying them, how they move across platforms, and what a competing growth team should do next.

---

## What This Machine Actually Does

This is **not** a generic scrape-and-dashboard ETL job. Our Part 2 findings showed that Claude virality is not a single-post classification problem; it is a **cross-platform narrative propagation problem**:

- Hacker News acts as an early ignition surface for technical attention
- X/Twitter surfaces insiders, amplifiers, and threat catalysts
- YouTube creators sustain and scale distribution beyond official channels
- Reddit broadens the conversation later, often inside competitor communities

So the machine is designed to answer four operational questions every week:

1. **Which narratives are breaking out right now?**
2. **Which creators/accounts are driving the spread?**
3. **How is the story moving across platforms over time?**
4. **What action should a growth team take next?**

---

## Design Principles Derived From Our Data

The architecture is intentionally tied to the findings in `PLAYBOOK_ANALYSIS.md`, not to generic social media tooling patterns.

| Part 2 finding | What it means operationally | Architectural implication |
|---|---|---|
| **Finding 2: 3-wave cascade** | Virality spreads across platforms in sequence, not in isolation | Build a **cross-platform event correlator**, not just per-post ranking |
| **Findings 7, 11, 12: community creators + insiders + small accounts matter** | Official channels are not the main growth engine | Build **author/amplifier scoring** with insider and breakout-account detection |
| **Findings 4 and 8: timing + decay differ by platform** | HN, Reddit, X, and YouTube have different action windows | Add **timing/decay logic** by platform instead of one global urgency score |
| **Findings 5, 9, 13: comparisons, threats, and competitor territory drive attention** | Narrative framing matters as much as raw engagement | Build **threat/comparison monitoring** and surface “why this is spreading” |
| **Finding 10: naming the movement matters** | Vocabulary can become a growth asset | Track **message/frame adoption** across platforms |

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     SIGNAL SURFACES (public, no auth)                        │
│                                                                              │
│  Hacker News          X / Twitter          YouTube           Reddit          │
│  early technical      insiders +            creator           community       │
│  ignition             amplifiers + threats  distribution      adoption        │
└──────────────┬──────────────────┬──────────────────┬──────────────────────────┘
               │                  │                  │
               ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        COLLECTION LAYER (scrapers/)                          │
│                                                                              │
│  hn_scraper.py   reddit_scraper.py   x_scraper.py / x_playwright_scraper.py │
│  youtube_scraper.py                                                         │
│                                                                              │
│  Guarantees: retry(3), pagination handling, deduplication, dated raw files  │
│  Supporting module: amplifier_watchlist.py expands creator/author coverage   │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
                           data/raw/*.csv (date-stamped)
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    NORMALIZATION + ENRICHMENT LAYER                          │
│                                                                              │
│  normalize_sources.py                                                        │
│  • unified schema across all platforms                                       │
│  • canonical timestamps                                                      │
│  • comparable engagement fields                                              │
│  • author metadata normalization                                             │
│                                                                              │
│  Supporting enrichments                                                      │
│  • author_followers / views / engagement completion                          │
│  • keyword/topic extraction                                                  │
│  • optional spike-type enrichment (supporting context, not core decisioning) │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
                       data/processed/unified_posts.csv
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           INTELLIGENCE LAYER                                 │
│                                                                              │
│  1. Cross-Platform Event Correlator                                          │
│     • groups posts about the same story across platforms within time windows  │
│     • detects HN → X/YouTube → Reddit cascades                               │
│                                                                              │
│  2. Author / Amplifier Scoring                                               │
│     • scores insider engineers, creators, journalists, brands, breakout SMBs │
│     • prioritizes views/follower ratio over follower count alone              │
│                                                                              │
│  3. Threat + Comparison Monitor                                              │
│     • detects competitor framing, attack narratives, “Claude vs X” spikes    │
│                                                                              │
│  4. Timing / Decay Scorer                                                    │
│     • platform-aware urgency: HN fast decay, YouTube long tail, Reddit lag   │
│                                                                              │
│  5. Velocity Ranking + Spike-Type Enrichment                                 │
│     • ranking for recency/importance                                         │
│     • classification kept as context, not as the main intelligence engine    │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           DELIVERY LAYER                                     │
│                                                                              │
│  Weekly outputs                                                              │
│  • growth_frontpage.csv                                                      │
│  • virality_timeline.html                                                    │
│  • ranked narrative / creator / threat summaries                             │
│                                                                              │
│  Alert outputs                                                               │
│  • cascade alert: same story hits 2+ platforms in < 6h                       │
│  • creator opportunity alert: breakout creator on target topic               │
│  • competitor threat alert: comparison/attack narrative gaining speed         │
│  • framing alert: a message/vocabulary pattern is propagating                │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         HUMAN REVIEW + ACTION                                │
│                                                                              │
│  Humans decide:                                                              │
│  • whether the signal matters strategically                                  │
│  • whether to amplify, respond, ignore, or brief creators                    │
│  • final messaging, spend, and partner outreach                              │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION LAYER                                   │
│                                                                              │
│  Current: cron → weekly full run + optional faster trigger polling           │
│  At scale: Prefect → retries, run history, observability, DAG-level alerts   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Why This Architecture Matches the Case

The HackNU brief asks for a recurring **competitive intelligence system**, not just a data pipeline. A growth team does not need another raw spreadsheet; it needs a machine that turns public discourse into decisions:

- **What story is breaking out?**
- **Who is driving it?**
- **Which platform matters first?**
- **Is this a threat, an opportunity, or noise?**
- **What should we do this week?**

That is why the center of the architecture is the **intelligence layer**, not the classifier.

---

## Core Modules

### 1) Collection Layer: Broad Enough to Be Useful, Cheap Enough to Run Weekly

We prioritized the four surfaces that gave us the highest information yield with public access:

- **Hacker News** for technical ignition
- **X/Twitter** for insider, creator, and threat velocity
- **YouTube** for long-tail creator distribution
- **Reddit** for community reaction and competitor-house discussion

This matches the brief's requirement to choose platforms deliberately and justify the tradeoff. We did not force Instagram/LinkedIn/TikTok into the pipeline because public access there is weak relative to the time cost and reliability penalty.

### 2) Normalization Layer: Make Heterogeneous Platforms Comparable

`normalize_sources.py` turns platform-specific rows into one schema so downstream logic can reason across sources instead of by scraper. This is what makes “same narrative across platforms” detectable at all.

Key outputs:
- canonical timestamps
- standardized engagement fields
- normalized author metadata
- unified post/comment records

### 3) Intelligence Layer: The Actual Brain

#### Cross-Platform Event Correlator

This is the highest-value architectural step because it directly operationalizes **Finding 2**.

The goal is to detect that the *same story* has appeared on multiple platforms in a tight window:

```text
HN post at 01:13 UTC
YouTube creator coverage at 01:20 UTC
Reddit discussion later that day
=> this is not 3 unrelated posts; it is one narrative cascade
```

This is more useful to a growth team than a flat list of “viral posts” because it exposes **narrative propagation**, not just engagement snapshots.

#### Author / Amplifier Scoring

This module is based on **Findings 7, 11, and 12**:
- community creators routinely beat official accounts
- insiders can massively outperform brand channels
- small accounts can break out despite low follower count

So the system should score authors by more than size. Example dimensions:

```python
creator_score = (
    (median_views / max(follower_count, 1)) * 0.4
  + topic_overlap_score                    * 0.3
  + posting_velocity                       * 0.2
  + engagement_rate                        * 0.1
)
```

This helps the growth team find not just the loudest accounts, but the ones most likely to create disproportionate reach.

#### Threat + Comparison Monitor

This module is derived from **Findings 5, 9, and 13**. It watches for:

- competitor-comparison narratives
- attack frames and controversy
- discussion inside competitor communities
- language patterns that consistently lift engagement

This is what turns the system from “social listening” into **competitive intelligence**.

#### Timing / Decay Scorer

Based on **Findings 4 and 8**, the urgency model must be platform-aware:

- HN is fast and short-lived
- X can explode quickly through insiders/amplifiers
- YouTube retains relevance longer
- Reddit lags and extends the conversation

So the system should not treat a 10-hour-old HN post and a 10-hour-old YouTube video as equally actionable.

#### Spike-Type Enrichment

We keep the current spike classifier, but we intentionally demote it to a supporting role. It is useful for context (“this looks like a comparison post” or “this is a tutorial”), but it should not be treated as the core intelligence engine. The main job of the machine is to detect **events, amplifiers, threats, and timing windows**.

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
    row["views"] = d.get("views", 0)
    row["likes"] = d.get("likes", 0)
```

This pipeline is how we confirmed that `@bcherny` (Claude Code engineer) generated 44.3M views from 124 personal tweets — data that required both the Playwright historical scrape and the fxtwitter enrichment to surface.

### Why This Matters for the Growth Intelligence Use Case

Standard X monitoring tools (Brandwatch, Sprout Social, native X API) either require expensive paid tiers or miss historical context. Our Playwright approach:
- costs **$0** (uses existing auth cookies from a regular account)
- reaches **16 months of history** (not just 7 days)
- returns **full engagement metrics** (views, likes, retweets, bookmarks, follower count)
- stays **self-contained** — no paid tiers, no rate-limit negotiation contracts

The tradeoff: it requires a headless browser (~500MB RAM) and runs slower than a direct API call (~5 seconds per search query). Acceptable for a weekly intelligence run; not suitable for real-time streaming.

---

## Automated Outreach / Response Layer

The machine is designed to support response, not to replace human judgment. Once the intelligence layer detects something important, it can generate structured response recommendations for a growth team.

![Automation System](data/charts/chart_automation_system.png)

### Trigger Types

- **Cascade alert**: same narrative appears on 2+ platforms in < 6 hours
- **Competitor threat alert**: comparison/attack framing starts accelerating
- **Creator opportunity alert**: high-fit creator or breakout small account mentions target topic
- **Celebrity / mega-amplifier alert**: large account creates disproportionate attention

### Suggested Downstream Outputs

- Slack alert with why it fired
- weekly dashboard with ranked narratives and creators
- creator outreach brief
- comparison-response brief
- amplification suggestion for the growth team

These outputs keep the system aligned with the brief: it is a machine a team could actually review every Monday morning and act on.

---

## Automated vs Human-Reviewed Steps

| Step | Automated? | Why |
|---|---|---|
| Scraping (HN, Reddit, X, YouTube) | ✅ Fully automated | Deterministic collection, retries, pagination, deduplication |
| Normalization and schema mapping | ✅ Fully automated | Rules-based transformation |
| Cross-platform event correlation | ✅ Fully automated | Time-window + text/topic matching problem |
| Author / amplifier scoring | ✅ Fully automated | Formula-based ranking from observed metrics |
| Timing / decay scoring | ✅ Fully automated | Platform-specific heuristics derived from observed patterns |
| Spike-type enrichment | ✅ Fully automated | Cheap contextual label; useful but not relied on alone |
| Weekly dashboard + ranked outputs | ✅ Fully automated | Deterministic report generation |
| **Alert triage** | ⚠️ Human reviewed | Machine flags signals; humans decide if the signal is strategically meaningful |
| **Messaging / creator outreach / budget decisions** | ❌ Human only | Requires business context, brand judgment, and relationship management |
| **Seed creator list bootstrap** | ❌ Human once | Initial creator set requires domain knowledge; after that the watchlist can self-expand |

**Design principle:** automate detection, scoring, correlation, and reporting; keep strategic action and narrative response under human control.

---

## Tool Recommendations (with justification)

### Two-Speed Pipeline

A purely weekly batch pipeline cannot support cascade alerts. Finding 2 showed the HN → YouTube window is 7 minutes. A weekly job catches nothing in real time.

The solution is a **two-speed design**:

```
FAST LANE — runs every 30 minutes (lightweight)
  → poll HN /newest, Reddit /rising, X search (last 2h only)
  → check cascade_detector: same story on 2+ platforms in < 6h?
  → check threat_monitor: competitor keyword + velocity spike?
  → if signal: fire Slack alert → human reviews in < 4h
  → total runtime: ~20 seconds, no Playwright, no heavy scraping

SLOW LANE — runs every Monday 8am (full intelligence run)
  → full scrape: 90-day HN, 1-year Reddit, 16-month X historical
  → normalize → correlate → score → classify → rank
  → generate weekly dashboard + creator watchlist update
  → total runtime: ~3 minutes
```

This is exactly how Mention.com and Brand24 work internally: a shallow high-frequency poll for alerts, and a deep weekly crawl for trend analysis. The two jobs share the same detection logic but run at different cadences.

### Orchestration

| Option | Current choice | Why |
|---|---|---|
| **cron** | ✅ Yes (now) | Two cron entries: `*/30 * * * *` (fast lane) + `0 8 * * 1` (slow lane) |
| **Prefect** | At 10x scale | DAG visibility, retry policies with backoff, failure alerting, run history. Better than Airflow for small teams (no Celery/Redis required). |
| **Airflow** | No | Overengineered for a 9-step weekly job. Ops overhead not justified at this scale. |
| **GitHub Actions** | Alternative | Free, version-controlled, easy for team. Lacks long-running job support. |

**Recommendation:** two-cron setup now → Prefect if team grows past 3 people or pipeline exceeds 30 minutes.

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

The intelligence layer fires four distinct alert types, each with a different urgency and required response. This is derived directly from how real competitive intelligence tools (Mention, Brand24, Sprout Social) structure their alert logic — one threshold fits nothing well; alerts need to be typed.

### Alert Type 1 — Cascade Alert
**Signal:** same narrative detected on 2+ platforms within a 6-hour window  
**Why it matters:** Finding 2 showed HN → YouTube in 7 minutes, Reddit at 12 hours. By the time the cascade reaches Reddit, the HN/YouTube window has closed. You need to catch it at HN+X, not at Reddit.  
**Human action:** brief Tier 1 creator immediately; decide whether to amplify or respond  
**Urgency:** act within 4 hours or miss the window

```python
# cascade_detector.py — fires when:
if len(cascade.platforms) >= 2 and cascade.window_hours <= 6:
    fire_alert("CASCADE", cascade)
```

### Alert Type 2 — Competitor Threat Alert
**Signal:** comparison or attack narrative, velocity > 0.3, age < 4h, competitor keyword present  
**Why it matters:** Finding 9 — @elonmusk Grok Code tweet generated 27.3M views and drove more Claude discourse than all official launches combined. These don't stay small.  
**Human action:** prepare comparison-frame response content; decide whether to engage directly  
**Urgency:** respond within 6 hours before narrative solidifies

```python
COMPETITORS = ["grok", "gemini", "gpt-5", "cursor", "runway", "sora", "pika"]
if any(c in title_lower for c in COMPETITORS) and velocity > 0.3 and age_hours < 4:
    fire_alert("THREAT", post)
```

### Alert Type 3 — Creator Opportunity Alert
**Signal:** high-fit creator (topic_overlap > 0.6, views/follower ratio > 50x) posts about target topic  
**Why it matters:** Finding 12 — @MangoLassC (6.8K followers) got 2.85M views. The 4-hour window after an organic breakout post is when amplification matters most.  
**Human action:** amplify post via official channels; send outreach brief  
**Urgency:** act within 4 hours (engagement velocity peaks in first 6h)

### Alert Type 4 — Framing / Vocabulary Alert
**Signal:** a new phrase appears in 5+ posts across platforms within 48 hours  
**Why it matters:** Finding 10 — "vibe coding" appeared in Feb 2025 and generated 74M total views. Vocabulary adoption is detectable before a term goes mainstream.  
**Human action:** decide whether to adopt, amplify, or coin a competing term  
**Urgency:** low — this is a strategic signal, not an operational one

### Alert Routing

```
CASCADE alert     → Slack #growth-alerts (immediate, pings on-call)
THREAT alert      → Slack #growth-alerts + email growth lead
CREATOR alert     → Slack #creator-outreach (auto-generates brief)
FRAMING alert     → Slack #growth-strategy (weekly digest, not immediate)
```

**The velocity baseline still matters** — but as a filter inside each alert type, not as the sole signal:

```
velocity = normalized_score / (age_hours + 2)^1.8
```

A post with velocity > 0.5 that doesn't match any alert type is background noise. A post with velocity 0.2 that is part of a cross-platform cascade is not.

---

## Prototype Evidence

`pipeline.py` is a working prototype covering all 9 steps end-to-end:

```bash
$ python pipeline.py --skip-scrape
# Runs in < 30 seconds
# Outputs: unified_posts.csv (11,454 rows), spike_classified.csv (2,177 classified),
#          growth_frontpage.csv (1,962 velocity-ranked), virality_timeline.html
```

Live demo output from April 5, 2026:
- **#1 velocity post:** "Tell HN: Anthropic no longer allowing Claude Code subscriptions to use OpenClaw" — 766 pts, velocity=0.413
- **Alert triggered:** None (weekly batch — no posts < 12h old at time of run; fast-lane polling would catch these)

### cascade_detector.py — cross-platform event correlator

The intelligence layer includes `analysis/cascade_detector.py`, which detects narrative cascades across platforms using a sliding time-window and topic-keyword overlap. Run it on the full dataset:

```bash
$ python analysis/cascade_detector.py
# Groups 11,454 posts into narrative clusters
# Detects cross-platform cascades: same story on 2+ platforms within 6h
# Outputs: data/processed/cascade_events.csv
#          data/processed/cascade_report.txt (Slack-ready briefing)
```

Example output on our actual data:
```
=== CASCADE EVENTS — Apr 5, 2026 ===

CONFIRMED CASCADE — "Claude source code leak"
  Platforms: HN (01:13 UTC) → YouTube (01:20, +7min) → Reddit (12:54, +12h)
  Posts:     253 total | Peak: 766 pts HN, 2.59M views YouTube
  Status:    DECAYED (96h since peak)

EMERGING — "Claude vs Cursor pricing"
  Platforms: X (14:30) → Reddit (16:22, +2h)
  Posts:     34 | Peak: 284 pts Reddit
  Status:    ACTIVE — recommend: comparison content, 4h window
```

---

## Known Tradeoffs

| Decision | Why | What we gave up |
|---|---|---|
| fxtwitter instead of official X API | Free, no auth, returns full engagement data | Rate limited after ~100 requests/session; not suitable for real-time monitoring |
| Flat CSV instead of database | Zero setup, works on any machine, teammates can open in Excel | No cross-query analytics, no index on timestamps |
| Keyword classifier instead of LLM | Deterministic, free, fast (855 posts in <1s) | Lower accuracy on ambiguous posts; LLM would classify better but costs $0.01–0.05/post |
| Weekly cron instead of streaming | Simpler, sufficient for intelligence use case | Misses events that happen between Monday runs; real-time would need webhooks or polling |
| Instagram/LinkedIn/TikTok excluded | No public API without login | Missing ~30% of Claude discourse surface area |
