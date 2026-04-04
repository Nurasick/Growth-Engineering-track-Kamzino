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
