# HackNU 2026 — Progress Tracker
## Case: "Hack the Playbook: Claude's Viral Growth Machine"
## Competing product for Part 4: **Higgsfield** (AI video generation)

Last updated: 2026-04-04

---

## Scoring rubric (reminder)
| Criteria | Weight |
|---|---|
| Data extraction: working scrapers, clean data, edge case handling | 25% |
| Analytical depth: original insights from own data, not recycled takes | **30%** |
| Automation design: pipeline architecture, scalability, production awareness | 15% |
| Counter-playbook: actionable, specific, grounded in data | 20% |
| Communication: clear docs, explained tradeoffs, readable code | 10% |

---

## Part 1 — Scrape the Discourse
**Status: 80% ✅**

### Done
- [x] HN scraper — Algolia API, last 7 days, 1,141 items, retry logic, error logging
- [x] Reddit scraper — public JSON API, 5 subreddits, 125 posts + 584 comments
- [x] X/Twitter scraper — fxtwitter API, 82 tweets with full engagement (likes, views, retweets, bookmarks, author_followers), DDG+Bing+Brave discovery
- [x] YouTube scraper — Data API v3, 86 videos + 293 comments
- [x] Unified schema — all platforms normalized to same CSV structure (`data/processed/unified_posts.csv`)
- [x] Edge cases: rate limits, retries, deduplication, graceful failures, date-aware file detection

### Missing / Gaps
- [ ] Instagram — requires login, no public API. **Documented as limitation.**
- [ ] LinkedIn — requires login. **Documented as limitation.**
- [ ] TikTok — requires auth + unofficial API hacks. **Documented as limitation.**
- [ ] X coverage is seed-based (known handles), not exhaustive. Organic content from unknown accounts not captured.

### Deliverable status
- [x] Working scrapers + code (GitHub repo)
- [x] Structured dataset (CSV — `data/raw/`, `data/processed/`)

---

## Part 2 — Decode the Playbook
**Status: 75% ✅**

### Done (findings backed by data)
- [x] **5 spike types** classified across 855 posts (breakthrough 45%, tutorial 26%, personal 10%, meme 9%, comparison 7%)
- [x] **3-wave cascade validated** with timestamps from Apr 1 source code leak event: HN 01:13 → YouTube 01:20 → Reddit 12:54 → Meme wave 48h
- [x] **Community vs official reach**: community YouTube = 29x official Anthropic channel; X community ≈ official per tweet
- [x] **Engagement inversion**: meme highest avg (588K) but 9% of posts; breakthrough most common but median=4pts
- [x] **Timing patterns**: HN peaks 2–6pm ET, Reddit peaks weekends (Sunday avg 4,344 vs Thursday 1,625)
- [x] **Title word lift analysis**: "leaked" 22x lift, "chatgpt" 15x lift, "anthropic" alone 0.35x (hurts)
- [x] **Engagement decay**: HN dead in 24h, Reddit 3–4 days, YouTube retains velocity 6+ days
- [x] Written analysis: `PLAYBOOK_ANALYSIS.md`

### Missing / Gaps
- [ ] Visualizations for each finding (charts, not just tables) — jury expects data visualizations
- [ ] Cross-platform attribution: which HN post seeded which YouTube video? (manual analysis needed)
- [ ] Comparison finding needs more X data (only 1 comparison tweet in dataset)
- [ ] Statistical significance caveats need to be explicit in the doc

### Deliverable status
- [x] Playbook analysis with supporting data (`PLAYBOOK_ANALYSIS.md`)
- [ ] Data visualizations (charts) — needed for full score on 30% analytical depth criteria

---

## Part 3 — Build the Machine
**Status: 60% ✅**

### Done
- [x] **Working pipeline**: `pipeline.py` — end-to-end, runs in ~3 min, all 4 platforms
- [x] **Automated steps**: normalize → classify → rank → visualize → alert (fully automated)
- [x] **Amplifier watchlist**: self-expanding handle list, auto-scored weekly (Step 3.5)
- [x] **Alert design**: velocity > 0.5 AND age < 12h = flag human review
- [x] **Cron-ready**: `0 8 * * 1 python pipeline.py` — Monday morning schedule
- [x] **Error recovery**: retries on all HTTP calls, graceful skips, continues on step failure
- [x] **Data freshness**: date-stamped files, auto-detects today's vs cached

### Missing / **Required deliverables not yet done**
- [ ] **Architecture diagram** (required: "any visual format") — jury explicitly asks for this
- [ ] **Automation vs human review table** with written justification — not yet documented
- [ ] **Tool recommendations with justification** (why cron vs Airflow? why CSV vs DB?)
- [ ] **Cost estimate at current scale AND 10x scale** — not done
- [ ] **Monitoring design** — what happens if pipeline breaks silently?

### Deliverable status
- [x] Working prototype (bonus) — `pipeline.py`
- [ ] Architecture diagram (required)
- [ ] Written design doc covering: orchestration tools, error recovery, cost, monitoring

---

## Part 4 — Counter-Playbook for Higgsfield
**Status: 95% ✅**

### Context
- Higgsfield = AI video generation (competes with Sora, Runway, Pika)
- Audience: filmmakers, content creators, YouTubers — NOT developers
- Different from Claude's playbook: visual-first, TikTok/YouTube Shorts matter more than HN

### Done
- [x] Written counter-playbook: `COUNTER_PLAYBOOK.md`
- [x] Platform translation table (HN→ProductHunt, YouTube tech→YouTube VFX/film, Reddit ML→r/filmmakers)
- [x] Creator seeding strategy with named creator targets (Corridor Crew, Film Riot, Jake Bartlett, MattVidPro)
- [x] Content format playbook — all 5 spike types mapped to Higgsfield with data citations
- [x] Timing calendar (Week -2 → Week 3), grounded in decay and timing data
- [x] Alert system for competitor launches and virality spikes
- [x] Metrics: K-factor per creator, CAC by channel, virality coefficient, comparison win rate
- [x] Budget estimate: ~$2,150 for 90-day launch window

### Missing
- [ ] Nothing major. Could add TikTok-specific tactics or Instagram Reels playbook if time permits.

### Deliverable status
- [x] Counter-playbook / distribution plan (`COUNTER_PLAYBOOK.md`)

---

## Required deliverables checklist

| Deliverable | Format | Status |
|---|---|---|
| Working scrapers + code | GitHub repo | ✅ Done |
| Structured dataset | CSV | ✅ Done |
| Playbook analysis with supporting data | README or separate doc | ✅ `PLAYBOOK_ANALYSIS.md` |
| Automation architecture diagram | Any visual format | ✅ `ARCHITECTURE.md` |
| Counter-playbook / distribution plan | Written doc | ✅ `COUNTER_PLAYBOOK.md` |
| README (setup, assumptions, tradeoffs) | In repo | ⚠️ Needs writing |
| Video walkthrough (5–10 min) | Loom or screen recording | 🎁 Bonus |

---

## Priority order for remaining time

1. **README** (required, currently missing) — last required deliverable not yet done
2. **Part 2 visualizations** (the `virality_timeline.html` exists but needs charts for each finding)
3. **Video walkthrough** (bonus — record `pipeline.py` running live)
