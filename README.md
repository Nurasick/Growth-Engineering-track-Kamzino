# Hack the Playbook: Claude's Viral Growth Machine
## HackNU 2026 · Growth Engineering Track

Reverse-engineered how Claude goes viral across 4 platforms — 6,400+ posts, 16 months of X history, 13 data-backed findings — then built a distribution playbook for Higgsfield.

---

## Three findings you can only get from actually scraping the data

**1. The small account 415x anomaly.**
@MangoLassC has 6,800 followers. One Claude demo tweet: 2.85M views. That's a 415x views-to-follower ratio — more than Anthropic's entire official account for the same period. Full distribution in [Finding 12](PLAYBOOK_ANALYSIS.md#finding-12-small-accounts-go-massive--415x-ratio).

**2. Claude performs better in enemy territory.**
r/ChatGPT mean score for Claude content: 5,770. r/ClaudeAI mean: 4,593. Claude gets 25% more engagement on a competitor's home turf. [Finding 13](PLAYBOOK_ANALYSIS.md#finding-13-reddit-competitor-territory--37x-engagement-gap).

**3. The cascade has exact timestamps.**
HN post: 01:13 UTC Apr 1. First YouTube video: 01:20 (7 minutes later). Reddit: 12:54 (12h later). Meme/international: 48h+. Not a theory — timestamped across 4 platforms from the source code leak event. [Finding 2](PLAYBOOK_ANALYSIS.md#finding-2-the-3-wave-cascade--timestamped).

---

## Deliverables

| Deliverable | File | Status |
|---|---|---|
| Working scrapers | `scrapers/` | ✅ |
| Structured dataset (6,400+ posts) | `data/raw/*.csv` | ✅ |
| Playbook analysis — 13 findings, 12 charts | [`PLAYBOOK_ANALYSIS.md`](PLAYBOOK_ANALYSIS.md) | ✅ |
| Automation architecture diagram | [`ARCHITECTURE.md`](ARCHITECTURE.md) | ✅ |
| Higgsfield counter-playbook | [`COUNTER_PLAYBOOK.md`](COUNTER_PLAYBOOK.md) | ✅ |
| Live dashboard (FastAPI + Next.js) | `backend/`, `frontend/` | ✅ |
| Progress tracker | [`PROGRESS.md`](PROGRESS.md) | ✅ |

---

## One-command run

```bash
pip install -r requirements.txt
python pipeline.py --skip-scrape   # <30s, uses committed data
```

Outputs: `data/processed/unified_posts.csv`, `spike_classified.csv`, `growth_frontpage.csv`, `virality_timeline.html`

Full live scrape (requires `YOUTUBE_API_KEY` in `.env`):
```bash
cp .env.example .env   # add your key
python pipeline.py     # ~3 min, live scrape
```

---

## Dataset

| Platform | Posts | Coverage |
|---|---|---|
| Hacker News | 3,779 | 90 days, Jan–Apr 2026 |
| Reddit | 125 posts + 584 comments | 1 year, 5 subreddits |
| X fxtwitter (seed) | 82 | Known handles, full engagement |
| X Playwright (live) | 384 | Last 48h, 10 queries |
| X Playwright (historical) | **1,668** | Jan 2025 → Apr 2026, enriched via fxtwitter |
| YouTube | 86 videos + 293 comments | Last 2 weeks |
| Higgsfield Reddit | 45 posts + 130 comments | r/aivideo, r/filmmakers, r/videography |
| **Total** | **~6,400** | Multi-platform, unified schema |

The X historical dataset (1,668 tweets) required a Playwright browser scraper — see [Architecture.md §Playwright Story](ARCHITECTURE.md) for why and how.

---

## Key Findings Summary

Full analysis with 12 charts in [`PLAYBOOK_ANALYSIS.md`](PLAYBOOK_ANALYSIS.md).

| # | Finding | Key number |
|---|---|---|
| 1 | Power law — HN is winner-take-all | 88% of posts get ≤5 pts (n=3,779) |
| 2 | 3-wave cascade — timestamped | HN → YouTube in 7 min, Reddit at 12h |
| 3 | Spike type ceiling vs floor inverted | Meme 588K avg, competitor framing 381 median |
| 4 | HN timing — counterintuitive | 22:00 UTC = 4x baseline; not morning |
| 5 | Title word lift | "department" 36x, "war" 25x, "leaked" 22x |
| 6 | Pentagon saga — controversy cluster | 253 posts, 51.9 avg pts (8x baseline), App Store #1 |
| 7 | Community YouTube = 29x official | Fireship 2.59M vs Anthropic 196K same event |
| 8 | Engagement decay by platform | HN dead in 24h; YouTube retains 6+ days |
| 9 | Threat catalyst outsizes any launch | @elonmusk Grok Code: 27.3M views |
| 10 | Naming the movement | "vibe coding" Feb 2025 → 74M total views, Bolt v2 56.1M |
| 11 | Inside engineer vs official accounts | @bcherny 44.3M (124 tweets) vs @AnthropicAI 7.2M |
| 12 | Small accounts go massive — 415x ratio | @MangoLassC 6.8K followers → 2.85M views |
| 13 | Reddit competitor territory | r/ChatGPT mean 5,770 vs r/ClaudeAI 4,593 |

---

## Repo Structure

```
pipeline.py              ← MAIN ENTRYPOINT
scrapers/
  hn_scraper.py          ← Algolia API, --days 90
  reddit_scraper.py      ← public JSON API, 5 subreddits
  x_scraper.py           ← fxtwitter API, full engagement
  x_playwright_scraper.py← Playwright browser, 16-month historical
  youtube_scraper.py     ← Data API v3
analysis/
  normalize_sources.py   ← unified schema
  spike_classifier.py    ← 5 spike types
  growth_frontpage.py    ← HN gravity velocity ranking
  generate_charts.py     ← 12 PNG charts
  virality_timeline.py   ← HTML dashboard
  amplifier_watchlist.py ← auto-scores X creators
backend/                 ← FastAPI (port 8000), /docs for API reference
frontend/                ← Next.js dashboard (port 3000)
data/raw/                ← 14 date-stamped CSVs (committed)
data/processed/          ← pipeline outputs (gitignored, regenerated by pipeline)
data/charts/             ← 12 PNG charts (gitignored, regenerated by generate_charts.py)
PLAYBOOK_ANALYSIS.md     ← Part 2: 13 findings with charts
ARCHITECTURE.md          ← Part 3: pipeline design, Playwright story, outreach system
COUNTER_PLAYBOOK.md      ← Part 4: Higgsfield distribution strategy
```

---

## Running the full stack

**Backend API:**
```bash
cd backend && pip install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8000
# API docs → http://localhost:8000/docs
```

**Frontend dashboard:**
```bash
cd frontend && npm install && npm run dev
# Dashboard → http://localhost:3000
```

---

## Known Limitations

- **X historical data uses Playwright** — requires a logged-in X session. The scraper automates a real browser; no credentials are stored in the repo. See [ARCHITECTURE.md §Playwright Story](ARCHITECTURE.md) for the full explanation. The resulting dataset (1,668 tweets) is committed to `data/raw/` and does not need to be re-scraped.
- **Instagram, LinkedIn, TikTok excluded** — no public API without login. Documented gap.
- **HN includes off-topic posts** — Algolia returns posts where "Claude" appears in comments, not titles only. Some noise in the dataset; statistical caveats noted per finding.
- **Velocity recency bias** — fresh posts can temporarily outrank older high-engagement posts. Per-platform minimum thresholds not enforced (documented tradeoff).
- **Alerts require hourly scraping** — alert system logic is correct but weekly batch scraping means nothing is ever < 12h old at analysis time.
- **Backend job store is in-memory** — job history lost on server restart. Acceptable for demo; Redis/Postgres path documented in ARCHITECTURE.md.
- **X Playwright scraper: one event validation** — cascade timing verified on Apr 1 source code leak. Generalizing requires more events.

---

## AI Usage Disclosure

Per challenge rules: Claude (Anthropic) was used as a coding and writing assistant throughout this project. Specifically:

- **Scraper scaffolding**: initial code structure generated with Claude, then debugged and validated by running against live APIs and inspecting output CSVs directly
- **Analysis logic**: HN gravity formula, word-lift calculation, amplifier scoring formula — designed and validated by us; Claude helped implement and debug
- **Document drafts**: PLAYBOOK_ANALYSIS.md, COUNTER_PLAYBOOK.md, ARCHITECTURE.md — drafted with Claude assistance, all findings and numbers verified against actual `data/raw/` and `data/processed/` files before including
- **What we validated ourselves**: every number in PLAYBOOK_ANALYSIS.md was cross-checked against raw CSV output; findings that didn't hold up under inspection were revised or removed

The pipeline is fully reproducible: `python pipeline.py --skip-scrape` regenerates all processed outputs from the committed raw data in under 30 seconds.

---

## Cron Setup

```bash
# runs every Monday at 8am
0 8 * * 1 cd /path/to/repo && python pipeline.py >> data/pipeline.log 2>&1
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full automation design including the creator outreach system and upgrade path to Prefect + Postgres.
