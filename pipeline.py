#!/usr/bin/env python3
"""
Unified Growth Intelligence Pipeline — HackNU 2026

Run this once to collect all data, classify, rank, and generate the dashboard.
Designed to run every Monday morning as a cron job.

Usage:
  python pipeline.py               # full run (scrape + analyze)
  python pipeline.py --skip-scrape # skip scrapers, re-analyze existing data
  python pipeline.py --demo        # fast demo mode (fewer pages, lower limits)

Steps:
  1. HN       — Algolia API, last 7 days
  2. Reddit   — public JSON, 5 subreddits
  3. X        — fxtwitter + DDG/Bing/Brave discovery
  4. YouTube  — Data API v3 (skipped if no YOUTUBE_API_KEY)
  3.5 Amplifier watchlist — auto-score X creators, expand handle list
  5. Normalize — merge all into unified_posts.csv
  6. Classify  — spike_classifier.py (5 types)
  7. Rank      — growth_frontpage.py (HN gravity velocity)
  8. Visualize — virality_timeline.html
  9. Alert     — surface hot posts right now
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT     = Path(__file__).parent
RAW_DIR       = REPO_ROOT / "data" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
SCRAPERS_DIR  = REPO_ROOT / "scrapers"
ANALYSIS_DIR  = REPO_ROOT / "analysis"
PYTHON        = sys.executable
TODAY         = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def log(msg: str, icon: str = "→") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] {icon}  {msg}")


def run(cmd: list[str], label: str, cwd: Path | None = None) -> bool:
    log(label, "🔄")
    result = subprocess.run(cmd, cwd=str(cwd or REPO_ROOT))
    if result.returncode != 0:
        log(f"FAILED (exit {result.returncode}) — continuing", "⚠️")
        return False
    log("Done", "✅")
    return True


def run_python(script: Path, args: list[str], label: str) -> bool:
    return run([PYTHON, str(script)] + args, label)


def check_alerts() -> None:
    fp = PROCESSED_DIR / "growth_frontpage.csv"
    if not fp.exists():
        return
    now    = datetime.now(timezone.utc)
    alerts = []
    with fp.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                vel = float(row.get("velocity", 0))
                age = float(row.get("age_hours", 999))
            except Exception:
                continue
            if vel > 0.5 and age < 12:
                alerts.append(row)

    if alerts:
        print()
        print("  🚨 ACTIVE ALERTS — Something is happening RIGHT NOW:")
        for a in sorted(alerts, key=lambda x: float(x.get("velocity", 0)), reverse=True)[:5]:
            emoji = {"breakthrough": "⚡", "tutorial": "📖", "comparison": "⚔️",
                     "personal": "💬", "meme": "😂"}.get(a.get("spike_type", ""), "•")
            print(f"     {emoji} [{a.get('platform','?').upper()}] {a.get('title','')[:70]}")
            print(f"          score={a.get('raw_score','')}  age={float(a.get('age_hours',0)):.1f}h  velocity={float(a.get('velocity',0)):.3f}")
    else:
        log("No active alerts", "✅")


def print_summary() -> None:
    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║          GROWTH INTELLIGENCE — PIPELINE RESULTS         ║")
    print("  ╠══════════════════════════════════════════════════════════╣")
    raw_files = [
        (RAW_DIR / "x_case_raw.csv",                      "X/Twitter posts"),
        (RAW_DIR / f"reddit_posts_{TODAY}.csv",            "Reddit posts"),
        (RAW_DIR / f"reddit_comments_{TODAY}.csv",         "Reddit comments"),
        (RAW_DIR / f"hn_items_{TODAY}.csv",                "HN items"),
        (RAW_DIR / f"youtube_videos_{TODAY}.csv",          "YouTube videos"),
    ]
    print("  ║  RAW DATA:                                               ║")
    for p, label in raw_files:
        if p.exists():
            count = sum(1 for _ in p.open()) - 1
            print(f"  ║    ✅  {label:<28} {count:>6} rows        ║")
        else:
            # Try any matching file for today's dated ones
            pattern = p.name.replace(TODAY, "*")
            matches = list(RAW_DIR.glob(pattern)) if "*" in pattern else []
            if matches:
                count = sum(1 for _ in matches[0].open()) - 1
                print(f"  ║    ✅  {label:<28} {count:>6} rows        ║")
            else:
                print(f"  ║    ⏭️   {label:<28} {'—':>6}              ║")

    print("  ║                                                          ║")
    print("  ║  PROCESSED:                                              ║")
    for p, label in [
        (PROCESSED_DIR / "unified_posts.csv",    "Unified dataset"),
        (PROCESSED_DIR / "spike_classified.csv", "Classified posts"),
        (PROCESSED_DIR / "growth_frontpage.csv", "Velocity ranked"),
    ]:
        if p.exists():
            count = sum(1 for _ in p.open()) - 1
            print(f"  ║    ✅  {label:<28} {count:>6} rows        ║")

    print("  ║                                                          ║")
    print("  ║  OUTPUT:                                                 ║")
    print("  ║    📊  data/processed/virality_timeline.html             ║")
    print("  ║    📋  data/processed/growth_frontpage.csv               ║")
    print("  ║    🗂️   data/processed/spike_classified.csv              ║")
    print("  ║    🎯  data/amplifier_watchlist.csv                      ║")
    print("  ╚══════════════════════════════════════════════════════════╝")


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified Growth Intelligence Pipeline")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip scrapers, re-analyze existing data")
    parser.add_argument("--demo",        action="store_true", help="Fast demo mode")
    args = parser.parse_args()

    # Ensure output dirs exist
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║     CLAUDE GROWTH INTELLIGENCE — UNIFIED PIPELINE       ║")
    print("  ║     HackNU 2026 · 4 platforms · live + historical       ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"  Date:  {TODAY}")
    print(f"  Mode:  {'demo (fast)' if args.demo else 'full'}{' [skip-scrape]' if args.skip_scrape else ''}")
    print()

    # ── STEP 1: HN ────────────────────────────────────────────────────────────
    if not args.skip_scrape:
        print("  ── STEP 1: HN (Algolia API · last 7 days) ──────────────────")
        hn_out = RAW_DIR / f"hn_items_{TODAY}.csv"
        if hn_out.exists():
            log(f"HN cached ({sum(1 for _ in hn_out.open())-1} items)", "⏭️")
        else:
            run_python(SCRAPERS_DIR / "hn_scraper.py", [], "HN scraper")

    # ── STEP 2: Reddit ────────────────────────────────────────────────────────
    if not args.skip_scrape:
        print()
        print("  ── STEP 2: Reddit (public API · 5 subreddits) ───────────────")
        reddit_out = RAW_DIR / f"reddit_posts_{TODAY}.csv"
        if reddit_out.exists():
            log(f"Reddit cached ({sum(1 for _ in reddit_out.open())-1} posts)", "⏭️")
        else:
            run_python(SCRAPERS_DIR / "reddit_scraper.py", [], "Reddit scraper")

    # ── STEP 3: X ─────────────────────────────────────────────────────────────
    if not args.skip_scrape:
        print()
        print("  ── STEP 3: X/Twitter (fxtwitter · public) ───────────────────")
        x_out = RAW_DIR / "x_case_raw.csv"
        if x_out.exists():
            count = sum(1 for _ in x_out.open()) - 1
            log(f"X cached ({count} tweets)", "⏭️")
        else:
            x_args = ["--pages", "1", "--limit-per-query", "10", "--verbose"] if args.demo else ["--pages", "2", "--limit-per-query", "20", "--verbose"]
            run_python(SCRAPERS_DIR / "x_scraper.py", x_args, "X scraper (fxtwitter + DDG/Bing/Brave)")

    # ── STEP 3.5: Amplifier Watchlist ────────────────────────────────────────
    print()
    print("  ── STEP 3.5: Amplifier watchlist (auto-score creators) ──────")
    run_python(ANALYSIS_DIR / "amplifier_watchlist.py", [], "Amplifier scorer → data/amplifier_watchlist.csv")

    # ── STEP 4: YouTube ───────────────────────────────────────────────────────
    if not args.skip_scrape:
        print()
        print("  ── STEP 4: YouTube (Data API v3) ────────────────────────────")
        yt_key = os.environ.get("YOUTUBE_API_KEY", "")
        yt_out = RAW_DIR / f"youtube_videos_{TODAY}.csv"
        if not yt_key:
            log("No YOUTUBE_API_KEY — skipping", "⏭️")
        elif yt_out.exists():
            log("YouTube cached", "⏭️")
        else:
            run_python(SCRAPERS_DIR / "youtube_scraper.py", [], "YouTube scraper (Data API v3)")

    # ── STEP 5: Normalize ─────────────────────────────────────────────────────
    print()
    print("  ── STEP 5: Normalize → data/processed/unified_posts.csv ────")
    run_python(ANALYSIS_DIR / "normalize_sources.py", [], "Normalize all sources → unified_posts.csv")

    # ── STEP 6: Classify ──────────────────────────────────────────────────────
    print()
    print("  ── STEP 6: Classify spike types ─────────────────────────────")
    run_python(ANALYSIS_DIR / "spike_classifier.py", [], "Spike classifier (5 types)")

    # ── STEP 7: Rank ──────────────────────────────────────────────────────────
    print()
    print("  ── STEP 7: Velocity ranking (HN gravity) ────────────────────")
    run_python(ANALYSIS_DIR / "growth_frontpage.py", [], "Growth front page")

    # ── STEP 8: Visualize ─────────────────────────────────────────────────────
    print()
    print("  ── STEP 8: Generate dashboard ───────────────────────────────")
    run_python(ANALYSIS_DIR / "virality_timeline.py", [], "Virality timeline HTML")

    # ── STEP 9: Alerts ────────────────────────────────────────────────────────
    print()
    print("  ── STEP 9: Alert check ──────────────────────────────────────")
    check_alerts()

    print_summary()
    print()
    html_path = PROCESSED_DIR / "virality_timeline.html"
    print(f"  Open dashboard:  xdg-open {html_path}")
    print(f"  Schedule (cron): 0 8 * * 1 cd {REPO_ROOT} && python pipeline.py")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
