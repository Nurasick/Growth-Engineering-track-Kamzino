# HackNU 2026 — Growth Engineering Track

## Project Goal
Reverse-engineer Claude's viral growth playbook. Build scrapers → clean data → 
analyze patterns → design automation pipeline → write counter-playbook.

## Repo Structure
- /scrapers       — reddit_scraper.py, youtube_scraper.py, hn_scraper.py
- /data/raw       — timestamped raw outputs (never overwrite, always append date)
- /data/clean     — processed master dataset
- /analysis       — eda.py, charts/ folder (plotly HTML)
- /pipeline       — scheduler.py, run_history.jsonl
- /docs           — architecture.md, platform-notes.md, task-tracker.md, counter-playbook.md
- /.claude        — agents/, commands/

## Tech Stack
- Python 3.11, praw, google-api-python-client, requests, pandas, plotly
- Orchestration: APScheduler (lightweight, no infra needed for hackathon)
- Visualization: plotly (saves as HTML, shareable without Jupyter)
- Remove: yt-dlp (wrong tool — that's video download, not metadata), tweepy (X API too restricted)

## Non-Negotiables
- All credentials via .env + python-dotenv, never hardcoded
- Every scraper logs failures to /data/errors.log with ISO timestamp
- Rate limit handling: exponential backoff, max 3 retries, then log and continue
- Outputs: /data/raw/[platform]_YYYY-MM-DD.csv on every run
- Before coding anything: output implementation plan, wait for approval

## Commands to Run This Project
- Install deps: pip install -r requirements.txt
- Run Reddit scraper: python scrapers/reddit_scraper.py
- Run YouTube scraper: python scrapers/youtube_scraper.py
- Run HN scraper: python scrapers/hn_scraper.py
- Run full pipeline: python pipeline/scheduler.py
- Generate charts: python analysis/eda.py

## What Claude Should Never Do
- Never use login-based scraping
- Never overwrite existing raw data files
- Never skip error handling to save lines of code
- Never use synchronous sleep without logging why