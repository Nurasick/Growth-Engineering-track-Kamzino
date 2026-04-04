# HackNU 2026 — Progress Tracker
## Case: "Hack the Playbook: Claude's Viral Growth Machine"
## Competing product for Part 4: **Higgsfield** (AI video generation)

Last updated: 2026-04-05

---

## Scoring rubric

| Criteria | Weight | Our status |
|---|---|---|
| Data extraction: working scrapers, clean data, edge case handling | 25% | **Strong** |
| Analytical depth: original insights from own data, not recycled takes | **30%** | **Strong** |
| Automation design: pipeline architecture, scalability, production awareness | 15% | **Strong** |
| Counter-playbook: actionable, specific, grounded in data | 20% | **Strong** |
| Communication: clear docs, explained tradeoffs, readable code | 10% | **Strong** |

---

## Required deliverables checklist

| Deliverable | Format | Status |
|---|---|---|
| Working scrapers + code | GitHub repo | ✅ Done |
| Structured dataset | CSV | ✅ Done — 6,100+ posts across 4 platforms |
| Playbook analysis with supporting data | `PLAYBOOK_ANALYSIS.md` | ✅ 13 findings, 12 charts |
| Automation architecture diagram | `ARCHITECTURE.md` + chart | ✅ Full pipeline + outreach system diagram |
| Counter-playbook / distribution plan | `COUNTER_PLAYBOOK.md` | ✅ 11 sections, all data-backed |
| README (setup, assumptions, tradeoffs) | `README.md` | ✅ Done |
| Video walkthrough (5–10 min) | Loom or screen recording | Bonus — not done |

---

## Part 1 — Scrape the Discourse
**Status: ✅ Complete**

### Done
- [x] HN scraper — Algolia API, `--days 90` flag → 3,779 items
- [x] Reddit scraper — public JSON API, 5 subreddits, `t=year`, `limit=100` → 125 posts + 584 comments
- [x] X scraper (fxtwitter) — full engagement (likes, views, retweets, bookmarks, author_followers) → 82 seed tweets
- [x] YouTube scraper — Data API v3 → 86 videos + 293 comments
- [x] **X scraper (Playwright)** — real Chromium browser, bypasses x-client-transaction-id anti-bot header
  - Live feed: 384 tweets (last 48h)
  - Historical: **1,668 tweets, Jan 2025 → Apr 2026** (64 searches = 4 queries × 16 monthly chunks)
  - Enriched via fxtwitter API for full author + engagement data
- [x] Unified schema — all platforms normalized to same CSV structure
- [x] Amplifier watchlist — auto-scores X creators, self-expanding
- [x] Edge cases: rate limits (429 backoff), retries (3x), deduplication, graceful failures
- [x] Higgsfield-specific scrape — 45 Reddit posts + 130 comments across r/aivideo, r/filmmakers, r/videography

### Gaps (documented)
- Instagram / LinkedIn / TikTok: no public API without login — documented limitation
- X seed-based initially; Playwright historical scraper addressed this for 16-month coverage
- HN Algolia search returns posts where "Claude" appears in comments, not just titles

---

## Part 2 — Decode the Playbook
**Status: ✅ Complete**

### Done
- [x] **13 findings** with data evidence in `PLAYBOOK_ANALYSIS.md` — all from own scraped data
- [x] **12 PNG charts** generated from actual data (`data/charts/`) — embedded in analysis doc
- [x] Finding 1: Power law — 88% of HN posts get ≤5 pts (n=3,779)
- [x] Finding 2: 3-wave cascade — timestamped on Apr 1 source code leak, all 4 platforms
- [x] Finding 3: Spike type volume vs engagement inverted — meme ceiling (588K avg), personal most consistent
- [x] Finding 4: Timing — HN 22:00 UTC = 4x baseline, Reddit Sunday = 2.7x Thursday
- [x] Finding 5: Title word lift — "department" 36x, "war" 25x, "leaked" 22x, "chatgpt" 15x
- [x] Finding 6: Pentagon saga cluster — 8x avg HN score, drove Claude to App Store #1
- [x] Finding 7: Community YouTube 29x official — Fireship 13x on single event
- [x] Finding 8: Engagement decay — HN dead in 24h, YouTube retains 6+ days
- [x] Finding 9: Threat catalyst — @elonmusk Grok Code 27.3M views vs all Claude launches combined
- [x] Finding 10: Naming the movement — @karpathy "vibe coding" Feb 2025 → 74M total views, Bolt v2 56.1M
- [x] Finding 11: Inside engineer — @bcherny 44.3M views (124 tweets) vs @AnthropicAI + @claudeai 7.2M combined
- [x] Finding 12: Small accounts go massive — @MangoLassC 6.8K followers → 2.85M views (415x ratio)
- [x] Finding 13: Reddit competitor territory — r/ChatGPT mean 5,770 vs r/ClaudeAI 4,593 for Claude content
- [x] Statistical caveats documented throughout

### New charts (generated Apr 5)
- [x] `chart_hn_power_law.png` — score distribution + trigger type breakdown
- [x] `chart_pentagon_controversy.png` — 6-week controversy timeline with HN scores
- [x] `chart_x_content_categories.png` — total views vs median floor by content type
- [x] `chart_monthly_x_views.png` — 16-month X view distribution with event annotations
- [x] `chart_inside_engineer.png` — @bcherny vs official accounts comparison
- [x] `chart_reddit_subreddits.png` — subreddit performance comparison

---

## Part 3 — Build the Machine
**Status: ✅ Complete**

### Done
- [x] Working pipeline: `pipeline.py` — 9 steps, end-to-end, ~3 min full run, <30s skip-scrape
- [x] FastAPI backend: `/analytics/summary`, `/feed`, `/alerts`, `/scrapers/*`, `/pipeline/*`, `/downloads/*`
- [x] Next.js frontend: Dashboard, Analytics, Scrapers, Pipeline, Downloads pages
- [x] `ARCHITECTURE.md` — full ASCII pipeline diagram, automated vs human table, tool justifications, cost estimates ($0 now / $56/month at 10x), error recovery, alert design
- [x] **Playwright story documented** — explains x-client-transaction-id problem, Chromium solution, fxtwitter enrichment, why this matters for the intelligence use case
- [x] **Automated outreach system designed and documented** — trigger engine, brief generator, creator scoring formula, delivery via Slack
- [x] **`chart_automation_system.png`** — full visual diagram of the extended pipeline
- [x] Cron setup documented (`0 8 * * 1 python pipeline.py`)

### Known issues (documented tradeoffs)
- Velocity recency bias: fresh low-engagement posts can outrank older high-engagement ones
- Alerts always 0 in batch mode: requires hourly scraping for real-time alerts
- Backend job store is in-memory (Redis/DB at prod scale)

---

## Part 4 — Counter-Playbook for Higgsfield
**Status: ✅ Complete**

### Done
- [x] `COUNTER_PLAYBOOK.md` — 11 sections, all recommendations cite specific data findings
- [x] Section 0: Higgsfield pipeline data (0 HN posts, r/aivideo dominant, r/videography hostile)
- [x] Section 1: Platform translation with validation from Higgsfield scrape data
- [x] Section 2: Celebrity signal activation — Madonna, Snoop Dogg, Will Smith, Elon Musk organic use
- [x] Section 3: Creator strategy — 3 tiers, inside engineer play, @bcherny data backing
- [x] Section 4: **TikTok and Instagram specific playbook** — 35K TikTok vs 846K Instagram gap identified; Dequine (241K TikTok), Yenlik (230K Instagram) ambassador activation
- [x] Section 5: Content format decisions — table of all formats with median views, when to use/avoid
- [x] Section 6: **Automated outreach system** — creator scoring formula, trigger detection code, auto-brief template, outreach email template
- [x] Section 7: Threat catalyst response playbook
- [x] Section 8: Naming the movement play — "vibe filmmaking", Yenlik activation path
- [x] Section 9: Alert system with specific thresholds
- [x] Section 10: Metrics (K-factor, TikTok follower velocity, comparison win rate, virality coefficient)
- [x] Section 11: Budget (~$2,400–$2,600 for 90-day window)
- [x] Growth engineering case references: Vercel, Linear, Figma, Superhuman, Notion, Drift, HubSpot

### Growth engineering frameworks cited
- **Inside engineer play**: documented at Vercel (Guillermo Rauch, Lee Robinson), Linear (Karri Saarinen), Figma (Dylan Field)
- **Creator pre-briefing**: Vercel explicitly pre-briefs Theo (t3.gg), Fireship before Next.js releases — documented by Theo publicly
- **Competitor territory seeding**: Superhuman seeded Gmail power-user communities; Notion seeded r/productivity not r/Notion
- **Movement naming**: "Growth hacking" (Sean Ellis → HubSpot), "Jobs to be done" (Christensen → Intercom), "Product-led growth" (OpenView → Notion/Figma/Slack)
- **Trigger-based outreach**: Drift (monitored Intercom pricing), HubSpot (Salesforce timing), Notion (Evernote migration guide)

---

## Key data stats (final)

| Platform | Posts | Coverage |
|---|---|---|
| Hacker News | 3,779 | 90 days, Jan–Apr 2026 |
| Reddit | 125 posts + 584 comments | 1 year, 5 subreddits |
| X fxtwitter (seed) | 82 | Known handles, full engagement |
| X Playwright (live) | 384 | Last 48h, 10 queries |
| X Playwright (historical) | **1,668** | Jan 2025 → Apr 2026, enriched |
| YouTube | 86 videos + 293 comments | Last 2 weeks |
| Higgsfield Reddit | 45 posts + 130 comments | r/aivideo, r/filmmakers, r/videography |
| **Total** | **~6,400** | Multi-platform, unified schema |

---

## Remaining (low priority / bonus)
- [ ] Per-platform minimum engagement thresholds in growth_frontpage.py (fixes velocity recency bias)
- [ ] HN title-only filtering to remove off-topic posts
- [ ] Video walkthrough (bonus — record `pipeline.py` + frontend running live)
- [ ] Build actual creator watchlist scraper for YouTube/TikTok (currently designed, not implemented)
