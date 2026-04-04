"""
GET /downloads/files          — list all available CSV/HTML files
GET /downloads/raw/{filename} — download a file from data/raw/
GET /downloads/processed/{filename} — download a file from data/processed/
GET /downloads/amplifier      — download amplifier_watchlist.csv
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

REPO_ROOT      = Path(__file__).parent.parent.parent
RAW_DIR        = REPO_ROOT / "data" / "raw"
PROCESSED_DIR  = REPO_ROOT / "data" / "processed"
DATA_DIR       = REPO_ROOT / "data"

ALLOWED_EXTENSIONS = {".csv", ".html", ".json"}


def _safe_path(directory: Path, filename: str) -> Path:
    """Resolve and validate that the path stays within the expected directory."""
    resolved = (directory / filename).resolve()
    if not str(resolved).startswith(str(directory.resolve())):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if resolved.suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return resolved


@router.get("/files")
def list_files():
    """List all downloadable files grouped by location."""
    def _list(directory: Path, label: str):
        if not directory.exists():
            return []
        return [
            {"name": f.name, "size_bytes": f.stat().st_size, "location": label}
            for f in sorted(directory.iterdir())
            if f.is_file() and f.suffix in ALLOWED_EXTENSIONS
        ]

    return {
        "raw": _list(RAW_DIR, "raw"),
        "processed": _list(PROCESSED_DIR, "processed"),
        "amplifier": _list(DATA_DIR, "data") ,
    }


@router.get("/raw/{filename}")
def download_raw(filename: str):
    path = _safe_path(RAW_DIR, filename)
    return FileResponse(
        path=str(path),
        media_type="text/csv",
        filename=filename,
    )


@router.get("/processed/{filename}")
def download_processed(filename: str):
    path = _safe_path(PROCESSED_DIR, filename)
    media_type = "text/html" if path.suffix == ".html" else "text/csv"
    return FileResponse(
        path=str(path),
        media_type=media_type,
        filename=filename,
    )


@router.get("/amplifier")
def download_amplifier():
    path = DATA_DIR / "amplifier_watchlist.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="amplifier_watchlist.csv not found — run the pipeline first")
    return FileResponse(
        path=str(path),
        media_type="text/csv",
        filename="amplifier_watchlist.csv",
    )
