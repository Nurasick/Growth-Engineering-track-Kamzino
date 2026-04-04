"""
Simple in-memory job tracker for background scraper/pipeline runs.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Literal

JobStatus = Literal["pending", "running", "done", "failed"]

_jobs: Dict[str, dict] = {}


def create_job(label: str) -> str:
    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {
        "id": job_id,
        "label": label,
        "status": "pending",
        "started_at": None,
        "finished_at": None,
        "output": "",
        "error": "",
    }
    return job_id


def update_job(job_id: str, **kwargs):
    if job_id in _jobs:
        _jobs[job_id].update(kwargs)


def get_job(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def list_jobs() -> list[dict]:
    return sorted(_jobs.values(), key=lambda j: j["started_at"] or "", reverse=True)
