#!/usr/bin/env python3
"""
Growth Front Page — HN-style velocity ranking across all platforms.

HN gravity formula: score / (age_hours + 2)^1.8
Adapted for cross-platform normalized engagement scores.

Reads  → data/processed/spike_classified.csv
Writes → data/processed/growth_frontpage.csv
         stdout: ranked front page
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT     = Path(__file__).parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
INPUT_CSV     = PROCESSED_DIR / "spike_classified.csv"
OUTPUT_CSV    = PROCESSED_DIR / "growth_frontpage.csv"

GRAVITY = 1.8
PLATFORM_SCORE_CAP = {"hn": 1000, "reddit": 10000, "youtube": 200000, "x": 50000}
SPIKE_EMOJI  = {"breakthrough": "⚡", "tutorial": "📖", "comparison": "⚔️", "personal": "💬", "meme": "😂"}
PLATFORM_LABEL = {"hn": "HN", "reddit": "Reddit", "youtube": "YouTube", "x": "X"}


def normalize_score(score: float, platform: str) -> float:
    return min(score / PLATFORM_SCORE_CAP.get(platform, 1000) * 100, 100)


def hn_rank(norm: float, age_hours: float) -> float:
    return norm / ((age_hours + 2) ** GRAVITY)


def age_hours_from(created_at: str, now: datetime) -> float | None:
    if not created_at:
        return None
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return max((now - dt).total_seconds() / 3600, 0.01)
    except Exception:
        return None


def classify_simple(r: dict) -> str:
    if r.get("spike_type") and r["spike_type"] not in ("", "unknown"):
        return r["spike_type"]
    text = (r.get("title", "") + " " + r.get("body_text", "")).lower()
    if any(k in text for k in ["vs ", "versus", "compared", "better than"]):
        return "comparison"
    if any(k in text for k in ["how to", "tutorial", "guide", "tips"]):
        return "tutorial"
    if any(k in text for k in ["announce", "release", "launch", "new model"]):
        return "breakthrough"
    if any(k in text for k in ["lol", "lmao", "😂", "meme", "bro "]):
        return "meme"
    if any(k in text for k in ["my ", "i was", "helped me", "my story"]):
        return "personal"
    return "breakthrough"


def main() -> None:
    if not INPUT_CSV.exists():
        print(f"[error] {INPUT_CSV} not found — run spike_classifier.py first")
        raise SystemExit(1)

    now = datetime.now(timezone.utc)

    with INPUT_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Deduplicate by title+platform
    seen: set[tuple] = set()
    deduped = []
    for r in rows:
        key = (r.get("platform", ""), r.get("title", "")[:60])
        if key not in seen and r.get("title"):
            seen.add(key)
            deduped.append(r)

    scored = []
    for r in deduped:
        platform  = (r.get("platform") or "hn").lower()
        raw_score = float(r.get("engagement_score") or r.get("score") or r.get("points") or 0)
        created   = r.get("created_at") or ""
        hours     = age_hours_from(created, now)
        if hours is None or hours > 24 * 90:
            continue
        norm     = normalize_score(raw_score, platform)
        velocity = hn_rank(norm, hours)
        spike    = classify_simple(r)

        scored.append({
            "rank": 0, "velocity": round(velocity, 4), "raw_score": int(raw_score),
            "age_hours": round(hours, 1), "platform": platform, "spike_type": spike,
            "title": r.get("title", "")[:100],
            "author": r.get("author") or r.get("author_handle") or "",
            "url": r.get("url") or "",
            "comments": r.get("comment_count") or "",
        })

    scored.sort(key=lambda x: x["velocity"], reverse=True)
    for i, item in enumerate(scored, 1):
        item["rank"] = i

    # Print front page
    print("=" * 80)
    print(f"  GROWTH FRONT PAGE  |  {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("  Ranked by engagement velocity (HN gravity, cross-platform normalized)")
    print("=" * 80)
    for item in scored[:30]:
        emoji = SPIKE_EMOJI.get(item["spike_type"], "•")
        plat  = PLATFORM_LABEL.get(item["platform"], item["platform"].upper())
        print(f"  {item['rank']:>2}. {emoji} [{plat}]  {item['title']}")
        print(f"       {item['raw_score']:,} pts · {item['age_hours']:.0f}h · v={item['velocity']:.3f} · {item['spike_type']}")
        print()

    # Spike mix
    mix = Counter(item["spike_type"] for item in scored[:30])
    print("-" * 80)
    print("  SPIKE MIX (top 30):")
    for st, count in mix.most_common():
        print(f"    {SPIKE_EMOJI.get(st,'•')} {st:<15} {'█'*count} ({count})")

    # Alert signals
    alerts = [i for i in scored if i["velocity"] > 1.0 and i["age_hours"] < 6]
    print()
    print("  ALERTS (velocity > 1.0 AND age < 6h):")
    if alerts:
        for a in alerts[:5]:
            print(f"    [{a['platform'].upper()}] {a['title'][:70]}")
            print(f"          {a['raw_score']:,} pts in {a['age_hours']:.1f}h — SOMETHING IS HAPPENING")
    else:
        print("    None right now.")

    # Write CSV
    if scored:
        OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(scored[0].keys()))
            writer.writeheader()
            writer.writerows(scored)
        print(f"\n  Full list → {OUTPUT_CSV}  ({len(scored)} posts)")
    print("=" * 80)


if __name__ == "__main__":
    main()
