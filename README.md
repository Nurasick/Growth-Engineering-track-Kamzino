# Hack the Playbook: Claude's Viral Growth Machine
## HackNU 2026 · Growth Engineering Track

Competitive intelligence pipeline that reverse-engineers how Claude goes viral — then adapts the playbook for Higgsfield (AI video generation).

---

## Quick Start

**Data pipeline:**
```bash
pip install -r requirements.txt
cp .env.example .env          # add YOUTUBE_API_KEY=...
python pipeline.py --skip-scrape   # run on cached data (<30s)
python pipeline.py --demo          # live scrape, fast subset
python pipeline.py                 # full live scrape (~3 min)
```

**Backend API:**
```bash
cd backend && pip install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8000
# → http://localhost:8000/docs
```

**Frontend dashboard:**
```bash
cd frontend && npm install && npm run dev
# → http://localhost:3000
```

---

## What this does

A 9-step automated pipeline that runs every Monday morning:

1. Scrapes HN (90-day history), Reddit, X, and YouTube for Claude-related content
2. Auto-discovers and scores third-party amplifiers (self-expanding)
3. Normalizes all platforms into a unified schema
4. Classifies each post into one of 5 spike types (breakthrough/tutorial/meme/personal/comparison)
5. Ranks by velocity (HN gravity formula, cross-platform normalized)
6. Generates a virality timeline HTML dashboard
7. Alerts on posts with high velocity and age < 12h

**Backend** serves analytics via REST API. **Frontend** (Next.js) provides a live dashboard with velocity feed, spike breakdown, weekly trend chart, and top amplifier tracking.

---

## Repo Structure

```
pipeline.py              ← run this for data
backend/                 ← FastAPI backend (uvicorn, port 8000)
frontend/                ← Next.js dashboard (port 3000)
scrapers/                ← HN, Reddit, X, YouTube scrapers
analysis/                ← normalize, classify, rank, chart generation
data/raw/                ← date-stamped CSVs from scrapers (gitignored)
data/processed/          ← unified_posts.csv, spike_classified.csv (gitignored)
data/charts/             ← PNG charts for PLAYBOOK_ANALYSIS.md (gitignored)
PLAYBOOK_ANALYSIS.md     ← Part 2: 6 findings with charts
ARCHITECTURE.md          ← Part 3: pipeline design doc
COUNTER_PLAYBOOK.md      ← Part 4: Higgsfield distribution strategy
```

---

## Dataset (April 2026)

| Platform | Posts | Coverage |
|---|---|---|
| Hacker News | 1,884 | 90 days (Jan–Apr 2026) |
| Reddit | 125 | Last year, 5 subreddits |
| X / Twitter | 82 | Seed-based, known handles |
| YouTube | 86 | Last 2 weeks |
| **Classified** | **2,177** | Spike type + velocity scored |

---

## Key Findings (Part 2)

Full analysis with charts in [`PLAYBOOK_ANALYSIS.md`](PLAYBOOK_ANALYSIS.md). Summary:

1. **3-wave cascade is real** — HN fires at 01:13 UTC, YouTube reacts in 7 minutes, Reddit joins 12h later, meme/international at 48h+. Validated on the Apr 1 source code leak.
2. **Community creators = 29x official channel** — Fireship (2.59M views) beat Anthropic official (196K) by 13x on the same event.
3. **Meme content has the highest ceiling** (588K avg engagement). Personal stories are most consistent. Breakthrough is most common but median = 4 pts.
4. **Title framing**: "leaked" = 22x lift, "chatgpt" = 15x. "Anthropic" standalone = 0.35x (hurts).
5. **HN peaks 2–6pm ET** (not morning). Reddit peaks weekends (2.7x weekdays).
6. **Decay**: HN dead in 24h. Reddit half-life 3–4 days. YouTube retains velocity 6+ days.

---

## Deliverables

| Deliverable | File |
|---|---|
| Scrapers + pipeline | `pipeline.py`, `scrapers/`, `analysis/` |
| Backend API | `backend/` |
| Frontend dashboard | `frontend/` |
| Structured dataset | `data/processed/unified_posts.csv` (run pipeline first) |
| Playbook analysis + charts | `PLAYBOOK_ANALYSIS.md` |
| Architecture design doc | `ARCHITECTURE.md` |
| Higgsfield counter-playbook | `COUNTER_PLAYBOOK.md` |

---

## Known Limitations

- **X data is seed-based** — known handles only. Organic content from unknown accounts not captured.
- **Instagram, LinkedIn, TikTok excluded** — no public API without login.
- **HN includes off-topic posts** — Algolia search returns posts where "Claude"/"Anthropic" appears in comments, not just titles. Some noise in the dataset.
- **Velocity recency bias** — fresh posts with low engagement can temporarily outrank older high-engagement posts. Per-platform minimum thresholds not enforced.
- **Alerts require hourly scraping** — the alert system works correctly but with weekly batch scraping nothing is ever < 12h old at analysis time.
- **Backend job store is in-memory** — job history lost on server restart. Acceptable for demo.
- **Cascade timing from one event** — the 3-wave cascade was validated on the Apr 1 source code leak. Generalizing to all launch types requires more events.

---

## AI Tooling Disclosure

Per challenge rules: Claude (Anthropic) was used as a coding assistant throughout. Specifically:
- Scaffolding and debugging scraper code (all validated by running against live APIs and checking output CSVs)
- Drafting analysis docs and counter-playbook (all findings verified against actual scraped data — numbers match `data/processed/` outputs)
- Analysis methods (word lift, HN gravity, amplifier scoring) were designed and validated by us

The pipeline, dataset, and findings are real and reproducible via `pipeline.py --skip-scrape`.

---

## Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full design doc: ASCII diagram, automated vs human classification, tool recommendations (cron→Prefect, CSV→Postgres), cost estimates ($0/month now, ~$56/month at 10x), error recovery design, alert system.

---

## Counter-Playbook

See [`COUNTER_PLAYBOOK.md`](COUNTER_PLAYBOOK.md) for the Higgsfield distribution strategy: creator seeding, content format playbook, timing calendar, alert system, K-factor metrics, and $2,150 budget estimate for a 90-day launch window.

---

## Cron Setup

```bash
# runs every Monday at 8am
0 8 * * 1 cd /path/to/repo && python pipeline.py >> data/pipeline.log 2>&1
```
