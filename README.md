# Hack the Playbook: Claude's Viral Growth Machine
## HackNU 2026 · Growth Engineering Track

Competitive intelligence pipeline that reverse-engineers how Claude goes viral — then adapts the playbook for Higgsfield (AI video generation).

---

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env        # add YOUTUBE_API_KEY=...
python pipeline.py --skip-scrape   # run on cached data (<30s)
python pipeline.py --demo          # live scrape, fast subset
python pipeline.py                 # full live scrape (~3 min)
```

Output: `data/processed/virality_timeline.html` — open in browser.

---

## What this does

A 9-step automated pipeline that runs every Monday morning:

1. Scrapes HN, Reddit, X, and YouTube for Claude-related content
2. Auto-discovers and scores third-party amplifiers (self-expanding)
3. Normalizes all platforms into a unified schema
4. Classifies each post into one of 5 spike types
5. Ranks by velocity (HN gravity formula)
6. Generates a virality timeline dashboard
7. Alerts on posts with high velocity and age < 12h

No API keys required except YouTube (free tier: 10K units/day, our run uses ~600).

---

## Repo Structure

```
pipeline.py              ← run this
scrapers/
  hn_scraper.py          ← Algolia API, no auth
  reddit_scraper.py      ← public JSON API, no auth
  x_scraper.py           ← fxtwitter API, no auth
  youtube_scraper.py     ← YouTube Data API v3 (needs .env)
analysis/
  amplifier_watchlist.py ← auto-scores X creators, self-expanding
  normalize_sources.py   ← unified schema, date-aware fallback
  spike_classifier.py    ← keyword + platform prior classifier
  growth_frontpage.py    ← velocity ranking
  virality_timeline.py   ← Chart.js HTML dashboard
data/raw/                ← date-stamped CSVs from scrapers
data/processed/          ← unified_posts.csv, spike_classified.csv,
                            growth_frontpage.csv, virality_timeline.html
data/amplifier_watchlist.csv  ← auto-generated, feeds x_scraper.py
.env                     ← YOUTUBE_API_KEY=... (gitignored)
```

---

## Dataset (April 2026 run)

| Platform | Posts | Notes |
|---|---|---|
| Hacker News | 562 | Algolia API, last 7 days |
| Reddit | 125 posts + 584 comments | 5 subreddits |
| X / Twitter | 82 tweets | fxtwitter, full engagement metrics |
| YouTube | 86 videos + 293 comments | Data API v3 |
| **Unified** | **855 classified, 692 velocity-ranked** | |

---

## Key Findings (Part 2)

Full analysis in [`PLAYBOOK_ANALYSIS.md`](PLAYBOOK_ANALYSIS.md). Summary:

1. **3-wave cascade is real** — HN fires at 01:13 UTC, YouTube reacts in 7 minutes, Reddit joins 12h later, meme/international wave at 48h+. Validated on the Apr 1 source code leak.
2. **Community creators = 29x official channel** — Fireship (2.59M views) beat Anthropic official (196K) by 13x on the same event.
3. **Meme content has the highest ceiling** (588K avg engagement) but only 9% of posts. Breakthrough is most common (45%) but median = 4 pts.
4. **Title framing matters**: "leaked" = 22x engagement lift, "chatgpt" = 15x. "Anthropic" standalone = 0.35x (hurts).
5. **HN peaks 2–6pm ET**, not morning. Reddit peaks weekends (Sunday 2.7x Thursday).
6. **Engagement decay**: HN dead in 24h. Reddit half-life 3–4 days. YouTube retains velocity 6+ days.

---

## Deliverables

| Deliverable | File |
|---|---|
| Scrapers + working pipeline | `pipeline.py`, `scrapers/`, `analysis/` |
| Structured dataset | `data/processed/unified_posts.csv` |
| Playbook analysis (Part 2) | `PLAYBOOK_ANALYSIS.md` |
| Architecture diagram + design doc (Part 3) | `ARCHITECTURE.md` |
| Higgsfield counter-playbook (Part 4) | `COUNTER_PLAYBOOK.md` |

---

## Known Limitations

- **X data is seed-based** — we scrape known handles + auto-discovered amplifiers. Organic content from unknown accounts is not captured.
- **Instagram, LinkedIn, TikTok excluded** — no public API without login. ~30% of Claude discourse surface area is missing.
- **X rate limit** — fxtwitter caps at ~100 requests/session. Not suitable for real-time monitoring; sufficient for weekly intelligence runs.
- **HN data is last-7-days only** — Algolia API filter. Historical patterns before the scrape window are not captured.
- **Small n per timing bucket** — timing findings (HN peaks 2–6pm ET, Reddit peaks weekends) are directionally consistent but not statistically significant at the bucket level.
- **Cascade timing validated on one event** — the Apr 1 source code leak. Generalization to all launch types requires more events.

---

## Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full design doc including:
- Architecture diagram (all layers: collection → transform → delivery → orchestration)
- Automated vs human-review classification for each step
- Tool recommendations (cron → Prefect, CSV → Postgres) with justification
- Cost estimates: $0/month now, ~$56/month at 10x scale
- Error recovery design

---

## Cron Setup

```bash
# runs every Monday at 8am
0 8 * * 1 cd /path/to/repo && python pipeline.py >> data/pipeline.log 2>&1
```

---

## Counter-Playbook (Part 4)

See [`COUNTER_PLAYBOOK.md`](COUNTER_PLAYBOOK.md) for the full Higgsfield distribution strategy, including creator seeding targets, content format playbook, timing calendar, alert system, and metrics.
