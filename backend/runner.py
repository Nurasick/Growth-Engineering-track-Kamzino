"""
Utility to run a subprocess and stream stdout/stderr into a job record.
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from jobs import create_job, update_job

REPO_ROOT = Path(__file__).parent.parent
PYTHON = sys.executable


def run_script(script_path: Path, args: list[str], label: str) -> str:
    """Run a Python script as a background subprocess, returns job_id."""
    job_id = create_job(label)

    def _run():
        update_job(job_id, status="running", started_at=datetime.now(timezone.utc).isoformat())
        try:
            result = subprocess.run(
                [PYTHON, str(script_path)] + args,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            update_job(
                job_id,
                status="done" if result.returncode == 0 else "failed",
                output=result.stdout[-4000:],
                error=result.stderr[-2000:],
                finished_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as exc:
            update_job(
                job_id,
                status="failed",
                error=str(exc),
                finished_at=datetime.now(timezone.utc).isoformat(),
            )

    import threading
    threading.Thread(target=_run, daemon=True).start()
    return job_id


def run_command(cmd: list[str], label: str) -> str:
    """Run an arbitrary command as a background subprocess, returns job_id."""
    job_id = create_job(label)

    def _run():
        update_job(job_id, status="running", started_at=datetime.now(timezone.utc).isoformat())
        try:
            result = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            update_job(
                job_id,
                status="done" if result.returncode == 0 else "failed",
                output=result.stdout[-4000:],
                error=result.stderr[-2000:],
                finished_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as exc:
            update_job(
                job_id,
                status="failed",
                error=str(exc),
                finished_at=datetime.now(timezone.utc).isoformat(),
            )

    import threading
    threading.Thread(target=_run, daemon=True).start()
    return job_id
