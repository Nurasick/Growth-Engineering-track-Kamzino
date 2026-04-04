# Backend — Growth Intelligence API

FastAPI backend that wraps the scrapers and analysis pipeline, and serves CSV downloads.

## Requirements

- Python 3.10+

## Setup

```bash
cd backend
pip install -r requirements.txt
```

## Start

```bash
uvicorn main:app --reload --port 8000
```

Must be run from inside the `backend/` folder so imports resolve correctly.

## Environment variables

The backend inherits the root `.env` file automatically (loaded by the pipeline scripts). Copy it from the example if you haven't already:

```bash
cp ../.env.example ../.env
# then fill in YOUTUBE_API_KEY if you want YouTube scraping
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/scrapers/hn` | Run HN scraper |
| `POST` | `/scrapers/reddit` | Run Reddit scraper |
| `POST` | `/scrapers/x` | Run X/Twitter scraper |
| `POST` | `/scrapers/youtube` | Run YouTube scraper |
| `GET` | `/scrapers/jobs` | List all scraper jobs |
| `GET` | `/scrapers/jobs/{id}` | Get scraper job status |
| `POST` | `/pipeline/run` | Run full pipeline (`?demo=true` for fast mode) |
| `POST` | `/pipeline/analyze` | Re-analyze existing data (skip scrapers) |
| `POST` | `/pipeline/normalize` | Step 5: normalize sources |
| `POST` | `/pipeline/classify` | Step 6: classify spike types |
| `POST` | `/pipeline/rank` | Step 7: velocity ranking |
| `POST` | `/pipeline/visualize` | Step 8: generate HTML dashboard |
| `GET` | `/pipeline/jobs` | List all pipeline jobs |
| `GET` | `/pipeline/jobs/{id}` | Get pipeline job status |
| `GET` | `/downloads/files` | List all downloadable files |
| `GET` | `/downloads/raw/{filename}` | Download a raw CSV |
| `GET` | `/downloads/processed/{filename}` | Download a processed CSV |
| `GET` | `/downloads/amplifier` | Download amplifier_watchlist.csv |

Interactive API docs available at `http://localhost:8000/docs` once running.

## Job lifecycle

Scraper and pipeline runs execute in background threads. Every `POST` returns a `job_id` immediately:

```json
{ "job_id": "a1b2c3d4" }
```

Poll `GET /scrapers/jobs/{id}` or `GET /pipeline/jobs/{id}` until `status` is `"done"` or `"failed"`.
