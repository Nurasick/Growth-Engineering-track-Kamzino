"""
POST /scrapers/{source}  — trigger individual scrapers
GET  /scrapers/jobs      — list all scraper jobs
GET  /scrapers/jobs/{id} — get job status
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from jobs import get_job, list_jobs
from runner import run_script

router = APIRouter()

REPO_ROOT    = Path(__file__).parent.parent.parent
SCRAPERS_DIR = REPO_ROOT / "scrapers"


@router.post("/hn")
def run_hn():
    job_id = run_script(SCRAPERS_DIR / "hn_scraper.py", ["--overwrite"], "HN scraper")
    return {"job_id": job_id, "scraper": "hn"}


@router.post("/reddit")
def run_reddit():
    # Reddit scraper has no --overwrite flag; delete today's files before re-running
    import datetime, glob, os
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    raw_dir = REPO_ROOT / "data" / "raw"
    for pattern in [f"reddit_posts_{today}.csv", f"reddit_comments_{today}.csv"]:
        for f in glob.glob(str(raw_dir / pattern)):
            os.remove(f)
    job_id = run_script(SCRAPERS_DIR / "reddit_scraper.py", [], "Reddit scraper")
    return {"job_id": job_id, "scraper": "reddit"}


@router.post("/x")
def run_x(pages: int = 2, limit_per_query: int = 20):
    args = ["--pages", str(pages), "--limit-per-query", str(limit_per_query), "--verbose"]
    job_id = run_script(SCRAPERS_DIR / "x_scraper.py", args, "X scraper")
    return {"job_id": job_id, "scraper": "x"}


@router.post("/youtube")
def run_youtube():
    import datetime, glob, os
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    raw_dir = REPO_ROOT / "data" / "raw"
    for pattern in [f"youtube_videos_{today}.csv", f"youtube_comments_{today}.csv"]:
        for f in glob.glob(str(raw_dir / pattern)):
            os.remove(f)
    job_id = run_script(SCRAPERS_DIR / "youtube_scraper.py", [], "YouTube scraper")
    return {"job_id": job_id, "scraper": "youtube"}


@router.get("/jobs")
def get_jobs():
    return list_jobs()


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
