"""
Growth Intelligence — FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import scrapers, pipeline, downloads

app = FastAPI(title="Growth Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrapers.router, prefix="/scrapers", tags=["scrapers"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(downloads.router, prefix="/downloads", tags=["downloads"])


@app.get("/health")
def health():
    return {"status": "ok"}
