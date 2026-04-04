#!/usr/bin/env python3
"""
Classify posts into 5 spike types:
  1. comparison   - Claude vs other models
  2. tutorial     - how-to, guides, tips
  3. breakthrough - official releases, announcements
  4. meme         - viral/humor content
  5. personal     - personal stories, testimonials

Reads  → data/processed/unified_posts.csv
Writes → data/processed/spike_classified.csv
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path

REPO_ROOT     = Path(__file__).parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
INPUT_CSV     = PROCESSED_DIR / "unified_posts.csv"
OUTPUT_CSV    = PROCESSED_DIR / "spike_classified.csv"

SIGNALS: dict[str, list[str]] = {
    "comparison": [
        "vs ", " vs.", "versus", "compared to", "better than", "worse than",
        "switched from", "switch from", "moved from", "leaving", "left chatgpt",
        "chatgpt vs", "gpt-4 vs", "gemini vs", "copilot vs", "claude vs",
        "vs claude", "vs chatgpt", "vs gpt", "vs gemini", "which is better",
        "beats", "outperforms", "benchmark", "score", "wins", "loses to",
        "prefer claude", "prefer chatgpt", "why i use", "why i switched",
        "best ai", "top ai", "best model", "why claude", "prefer over",
    ],
    "tutorial": [
        "how to", "how i", "step by step", "guide to", "tutorial",
        "tips for", "tips on", "workflow", "prompt", "prompting",
        "getting started", "beginners guide", "learn", "course",
        "cheat sheet", "cheatsheet", "template", "technique",
        "trick", "hack ", "setup", "configure", "install",
        "walk through", "walkthrough", "demo", "example",
        "use case", "use cases", "best practices", "101",
    ],
    "breakthrough": [
        "anthropic announce", "anthropic release", "anthropic launch",
        "new model", "new version", "new feature", "just released",
        "just launched", "now available", "introducing", "announcing",
        "claude 3", "claude 4", "opus", "sonnet", "haiku",
        "api update", "system prompt", "context window",
        "research paper", "paper shows", "study finds",
        "breakthrough", "milestone", "first ever", "record",
        "raises", "funding", "series", "valuation",
        "acquired", "acquisition", "partnership",
        "safety", "alignment", "responsible ai",
        "[news]", "[announcement]", "press release",
    ],
    "meme": [
        "lol", "lmao", "lmfao", "😂", "💀", "🤣", "😭",
        "bro ", "bruh", "ngl ", "tbh", "imo ", "imo,",
        "when the", "me when", "nobody:", "not me",
        "can't believe", "imagine", "surreal",
        "unhinged", "cooked", "based", "mid ", "ratio",
        "actually insane", "actually crazy", "wild",
        "shitpost", "meme", "joke", "parody",
        "ai slop", "vibes", "no way", "bro really",
        "the ai said", "it literally",
    ],
    "personal": [
        "my dad", "my mom", "my wife", "my husband", "my son", "my daughter",
        "my family", "my child", "my kid", "my friend",
        "diagnosed", "diagnosis", "cancer", "disease", "illness", "doctor",
        "saved my", "saved me", "changed my life", "helped me",
        "personal experience", "my story", "my journey",
        "i was", "i am", "i've been", "i used to",
        "mental health", "therapy", "depression", "anxiety",
        "job loss", "fired", "laid off", "unemployed",
        "grateful", "thankful", "life changing", "amazing experience",
        "honest review", "my honest", "sharing my",
    ],
}

PLATFORM_PRIORS: dict[str, dict[str, float]] = {
    "comparison":   {"youtube": 0.3, "reddit": 0.2, "x": 0.1},
    "tutorial":     {"youtube": 0.4, "reddit": 0.2, "hn": 0.1},
    "breakthrough": {"hn": 0.4, "x": 0.2, "reddit": 0.1},
    "meme":         {"x": 0.4, "reddit": 0.2},
    "personal":     {"reddit": 0.3, "hn": 0.2, "x": 0.1},
}

OFFICIAL_BOOST = {"breakthrough": 0.5, "comparison": -0.1}


@dataclass
class ClassifiedPost:
    post_id: str
    platform: str
    title: str
    spike_type: str
    confidence: float
    scores_json: str
    created_at: str
    author: str
    url: str
    engagement_score: str


def classify_post(row: dict) -> ClassifiedPost:
    title    = row.get("title") or ""
    body     = row.get("body_text") or ""
    platform = (row.get("platform") or "").lower()
    is_official = str(row.get("official") or "").lower() in {"true", "1", "yes"}

    combined = f"{title} {body}".lower()
    scores: dict[str, float] = {
        st: sum(1 for kw in kws if kw in combined)
        for st, kws in SIGNALS.items()
    }

    for st, priors in PLATFORM_PRIORS.items():
        scores[st] += priors.get(platform, 0.0)
    if is_official:
        for st, boost in OFFICIAL_BOOST.items():
            scores[st] += boost

    total     = sum(scores.values()) or 1.0
    spike     = max(scores, key=lambda k: scores[k])
    confidence = round(scores[spike] / total, 3)

    return ClassifiedPost(
        post_id=row.get("post_id") or row.get("id") or row.get("object_id") or "",
        platform=platform,
        title=title[:120],
        spike_type=spike,
        confidence=confidence,
        scores_json=json.dumps({k: round(v, 2) for k, v in scores.items()}),
        created_at=row.get("created_at") or row.get("created_utc") or "",
        author=row.get("author") or row.get("author_handle") or "",
        url=row.get("url") or "",
        engagement_score=str(row.get("engagement_score") or row.get("score") or ""),
    )


def main() -> None:
    if not INPUT_CSV.exists():
        print(f"[error] {INPUT_CSV} not found — run normalize_sources.py first", file=sys.stderr)
        raise SystemExit(1)

    with INPUT_CSV.open(encoding="utf-8", newline="") as f:
        all_rows = list(csv.DictReader(f))

    print(f"[classify] {len(all_rows)} input rows", file=sys.stderr)
    results = [classify_post(row) for row in all_rows]

    type_counts = Counter(r.spike_type for r in results)
    print("\n=== Spike Type Distribution ===")
    for spike_type, count in type_counts.most_common():
        print(f"  {spike_type:<15} {count:>5}  ({count/len(results)*100:.1f}%)")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(r) for r in results)

    print(f"\n[done] {len(results)} rows → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
