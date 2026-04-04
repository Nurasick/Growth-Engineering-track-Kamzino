# HackNU 2026 — Progress Tracker
## Case: "Hack the Playbook: Claude's Viral Growth Machine"
## Competing product for Part 4: **Higgsfield** (AI video generation)

Last updated: 2026-04-04

---

## Scoring rubric
| Criteria | Weight | Our status |
|---|---|---|
| Data extraction: working scrapers, clean data, edge case handling | 25% | Strong |
| Analytical depth: original insights from own data, not recycled takes | **30%** | Strong |
| Automation design: pipeline architecture, scalability, production awareness | 15% | Strong |
| Counter-playbook: actionable, specific, grounded in data | 20% | Strong |
| Communication: clear docs, explained tradeoffs, readable code | 10% | Strong |

---

## Required deliverables checklist

| Deliverable | Format | Status |
|---|---|---|
| Working scrapers + code | GitHub repo | ✅ Done |
| Structured dataset | CSV | ✅ Done |
| Playbook analysis with supporting data | README or separate doc | ✅ `PLAYBOOK_ANALYSIS.md` + 6 charts |
| Automation architecture diagram | Any visual format | ✅ `ARCHITECTURE.md` |
| Counter-playbook / distribution plan | Written doc | ✅ `COUNTER_PLAYBOOK.md` |
| README (setup, assumptions, tradeoffs) | In repo | ✅ `README.md` |
| Video walkthrough (5–10 min) | Loom or screen recording | 🎁 Bonus — not done |

---

## Part 1 — Scrape the Discourse
**Status: 90% ✅**

### Done
- [x] HN scraper — Algolia API, `--days` flag (ran 90-day scrape: 3,779 items), retry + backoff
- [x] Reddit scraper — public JSON API, 5 subreddits, `t=year`, `limit=100`
- [x] X scraper — fxtwitter API, full engagement (likes, views, retweets, bookmarks, author_followers), self-expanding amplifier watchlist
- [x] YouTube scraper — Data API v3, 86 videos + 293 comments
- [x] Unified schema — all platforms normalized to same CSV structure
- [x] Amplifier watchlist — auto-scores X creators, feeds back into scraper
- [x] Edge cases: rate limits (429 backoff), retries (3x), deduplication, graceful failures

### Gaps (documented limitations)
- Instagram / LinkedIn / TikTok: no public API without login
- X is seed-based — organic content from unknown accounts not captured
- HN Algolia search includes off-topic posts where "Claude" appears in comments (not just titles)

---

## Part 2 — Decode the Playbook
**Status: 90% ✅**

### Done
- [x] 6 findings with data evidence in `PLAYBOOK_ANALYSIS.md`
- [x] 6 PNG charts generated from actual data (`data/charts/`) — embedded in analysis doc
- [x] 3-wave cascade validated with exact timestamps (Apr 1 source code leak natural experiment)
- [x] Community vs official YouTube quantified (29x, Fireship 13x single video)
- [x] Spike type breakdown (5 types, volume vs engagement inverted)
- [x] Title word lift analysis (leaked=22x, chatgpt=15x, anthropic=0.35x)
- [x] Timing patterns (HN 2–6pm ET, Reddit weekends 2.7x weekdays)
- [x] Engagement decay by platform (HN 24h, Reddit 3–4 days, YouTube 6+ days)
- [x] Statistical caveats documented (small n per timing bucket, cascade from one event)

### Known data quality issue
The 90-day HN expansion (1,884 posts) distorts platform-wide engagement numbers. Meme/personal median dropped because HN posts score 1–10 points while YouTube/Reddit memes score 100K+ views. Findings 3–5 in `PLAYBOOK_ANALYSIS.md` are stated from the original 855-post balanced dataset — more accurate for cross-platform comparisons.

---

## Part 3 — Build the Machine
**Status: 95% ✅**

### Done
- [x] Working pipeline: `pipeline.py` — 9 steps, end-to-end, ~3 min full run, <30s skip-scrape
- [x] FastAPI backend: `/analytics/summary`, `/feed`, `/alerts`, `/scrapers/*`, `/pipeline/*`, `/downloads/*`
- [x] Next.js frontend: Dashboard, Analytics page (velocity feed, spike breakdown, weekly trend, creators), Scrapers, Pipeline, Downloads
- [x] Velocity feed with platform + spike_type filters
- [x] Alert panel (velocity threshold, age < 12h)
- [x] Weekly trend chart (16-week window, stacked by platform)
- [x] `ARCHITECTURE.md`: full ASCII diagram, automated vs human table, tool recommendations, cost estimates ($0 now / $56/month at 10x), error recovery, alert design
- [x] Cron setup documented (`0 8 * * 1 python pipeline.py`)

### Known issues
- Velocity recency bias: fresh low-engagement posts can outrank older high-engagement ones. Per-platform minimum thresholds not enforced yet.
- Alerts always 0: works correctly but requires hourly scraping to catch breaking posts. Weekly batch = nothing is ever < 12h old.
- Backend job store is in-memory (lost on restart). Acceptable for demo; would use Redis/DB in prod.

---

## Part 4 — Counter-Playbook for Higgsfield
**Status: 95% ✅**

- [x] `COUNTER_PLAYBOOK.md` — 7 sections, all recommendations cite specific data findings
- [x] Platform translation (HN→ProductHunt, YouTube tech→YouTube VFX/film, Reddit ML→r/filmmakers)
- [x] Named creator targets: Corridor Crew, Film Riot, Jake Bartlett, MattVidPro, AI Explained
- [x] Content format playbook — all 5 spike types mapped with engagement data citations
- [x] Timing calendar (Week -2 → Week 3)
- [x] Alert system design (competitor launch response, virality spike monitoring)
- [x] Metrics: K-factor per creator, CAC by channel, virality coefficient (>15% target), comparison win rate
- [x] Budget: ~$2,150 for 90-day launch (Pro access for creators, $0 paid ads)

---

## Remaining (low priority)
- [ ] Per-platform minimum engagement thresholds in growth_frontpage.py (fixes velocity recency bias)
- [ ] HN title-only filtering to remove off-topic posts
- [ ] Video walkthrough (bonus — record `pipeline.py` + frontend running live)
