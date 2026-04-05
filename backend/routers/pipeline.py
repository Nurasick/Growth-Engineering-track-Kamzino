"""
POST /pipeline/run          — full pipeline (scrape + analyze)
POST /pipeline/analyze      — analysis only (skip-scrape)
POST /pipeline/normalize    — step 5: normalize sources
POST /pipeline/classify     — step 6: spike classifier
POST /pipeline/rank         — step 7: velocity ranking
POST /pipeline/visualize    — step 8: virality timeline HTML
GET  /pipeline/jobs         — list pipeline jobs
GET  /pipeline/jobs/{id}    — job status
"""

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

from jobs import get_job, list_jobs
from runner import run_command, run_script

router = APIRouter()

REPO_ROOT    = Path(__file__).parent.parent.parent
ANALYSIS_DIR = REPO_ROOT / "analysis"
PYTHON       = sys.executable


@router.post("/run")
def run_full(demo: bool = False):
    args = [PYTHON, str(REPO_ROOT / "pipeline.py")]
    if demo:
        args.append("--demo")
    from runner import run_command
    job_id = run_command(args, "Full pipeline")
    return {"job_id": job_id}


@router.post("/analyze")
def run_analyze():
    job_id = run_command(
        [PYTHON, str(REPO_ROOT / "pipeline.py"), "--skip-scrape"],
        "Analysis only (skip-scrape)",
    )
    return {"job_id": job_id}


@router.post("/normalize")
def run_normalize():
    job_id = run_script(ANALYSIS_DIR / "normalize_sources.py", [], "Normalize sources")
    return {"job_id": job_id}


@router.post("/classify")
def run_classify():
    job_id = run_script(ANALYSIS_DIR / "spike_classifier.py", [], "Spike classifier")
    return {"job_id": job_id}


@router.post("/rank")
def run_rank():
    job_id = run_script(ANALYSIS_DIR / "growth_frontpage.py", [], "Velocity ranking")
    return {"job_id": job_id}


@router.post("/visualize")
def run_visualize():
    job_id = run_script(ANALYSIS_DIR / "virality_timeline.py", [], "Virality timeline")
    return {"job_id": job_id}


@router.post("/playbook-metrics")
def run_playbook_metrics():
    job_id = run_script(ANALYSIS_DIR / "compute_playbook_metrics.py", [], "Compute playbook metrics")
    return {"job_id": job_id}


@router.post("/playbook-analysis")
def run_playbook_analysis():
    job_id = run_script(ANALYSIS_DIR / "generate_playbook_analysis.py", [], "Generate playbook analysis")
    return {"job_id": job_id}


@router.post("/counter-playbook")
def run_counter_playbook():
    job_id = run_script(ANALYSIS_DIR / "generate_counter_playbook.py", [], "Generate counter playbook")
    return {"job_id": job_id}


@router.get("/jobs")
def get_jobs():
    return list_jobs()


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
