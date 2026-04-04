#!/usr/bin/env python3
"""
Cross-Platform Cascade Detector

Detects when the same narrative spreads across multiple platforms within a time window.
This is what competitive intelligence tools call "story clustering" or "cascade detection."

Unlike per-post velocity ranking, this answers: which NARRATIVES are propagating,
not just which individual posts are popular.

Based on Finding 2: HN fires at 01:13 UTC → YouTube at 01:20 (+7min) → Reddit at 12:54 (+12h).
The goal is to detect this pattern automatically, in real time.

Reads:  data/processed/unified_posts.csv
Writes: data/processed/cascade_events.csv
        data/processed/cascade_report.txt (Slack-ready briefing)
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

REPO_ROOT      = Path(__file__).parent.parent
PROCESSED_DIR  = REPO_ROOT / "data" / "processed"
INPUT_CSV      = PROCESSED_DIR / "unified_posts.csv"
OUTPUT_CSV     = PROCESSED_DIR / "cascade_events.csv"
OUTPUT_REPORT  = PROCESSED_DIR / "cascade_report.txt"

# -------------------------------------------------------------------
# Topic vocabulary: curated named entities + event terms grouped by theme.
# This is how real social listening tools work — not NLP, not ML,
# but a maintained vocabulary of terms that matter for this domain.
# Each theme maps to a set of keywords that signal the same narrative.
# -------------------------------------------------------------------
TOPICS: dict[str, list[str]] = {
    "source_leak":         ["leak", "leaked", "source code", "github dump", "unauthorized", "breach"],
    "pentagon_ban":        ["pentagon", "department of defense", "dod", "government ban", "banned", "blocked", "federal"],
    "competitor_grok":     ["grok", "xai", "elon musk ai", "grok-3", "grok-2"],
    "competitor_gemini":   ["gemini", "google ai", "bard", "google deepmind"],
    "competitor_gpt":      ["gpt-5", "gpt-4o", "openai", "chatgpt", "o3", "o4"],
    "competitor_cursor":   ["cursor", "copilot", "github copilot", "codeium"],
    "competitor_video":    ["runway", "sora", "pika", "kling", "vidu", "hailuo", "luma dream"],
    "vibe_coding":         ["vibe coding", "vibe-coding", "vibecoding", "vibe code"],
    "claude_code":         ["claude code", "computer use", "coding agent", "claude agent"],
    "claude_release":      ["claude 4", "claude 3.7", "claude opus", "claude sonnet", "claude haiku", "new model"],
    "anthropic_news":      ["anthropic", "series", "funding", "valuation", "raises", "acquired", "partnership"],
    "ai_safety":           ["alignment", "safety", "responsible ai", "rlhf", "constitutional ai"],
    "comparison_frame":    ["vs ", "versus", "better than", "beats", "switched", "prefer", "which is better"],
    "viral_framing":       ["leaked", "insane", "crazy", "wild", "actually", "no way", "unhinged", "surreal"],
    "creator_content":     ["tutorial", "workflow", "how i", "my setup", "tips", "guide"],
    "personal_story":      ["saved my", "changed my life", "helped me", "my experience", "honest review"],
}

# How much weight to give title vs body text when extracting topics.
# Title is what spreads — body adds context.
TITLE_WEIGHT = 3
BODY_WEIGHT  = 1

# Cascade detection parameters
CASCADE_WINDOW_HOURS  = 6    # max hours between first and last platform for a cascade
CASCADE_MIN_PLATFORMS = 2    # minimum distinct platforms to count as a cascade
CASCADE_MIN_POSTS     = 3    # minimum total posts in a cascade cluster
TOPIC_OVERLAP_MIN     = 1    # minimum shared topics to consider posts "about the same story"

# Platform display order by typical cascade sequence (from Finding 2)
PLATFORM_ORDER = {"hn": 0, "x": 1, "youtube": 2, "reddit": 3}


# -------------------------------------------------------------------
# Data structures
# -------------------------------------------------------------------

@dataclass
class Post:
    post_id:          str
    platform:         str
    title:            str
    body_text:        str
    created_at:       datetime
    engagement_score: float
    author:           str
    url:              str
    topics:           frozenset  # extracted topic tags


@dataclass
class CascadeEvent:
    event_id:         str
    cascade_type:     str         # FAST_CASCADE (< 6h spread) | SUSTAINED (ongoing narrative)
    dominant_topics:  list[str]
    platforms:        list[str]   # in time order
    platform_times:   dict        # platform → first_seen ISO string
    window_hours:     float
    total_posts:      int
    peak_engagement:  float
    peak_post_title:  str
    first_seen:       str         # ISO
    last_seen:        str         # ISO
    hours_since_peak: float
    status:           str         # ACTIVE / EMERGING / DECAYING / HISTORICAL
    action:           str         # recommended growth team action


# -------------------------------------------------------------------
# Parsing
# -------------------------------------------------------------------

def _parse_dt(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            dt = datetime.strptime(raw, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def _safe_float(val: str) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def extract_topics(title: str, body: str) -> frozenset:
    """Extract topic tags from a post using the curated vocabulary."""
    combined = (title.lower() + " ") * TITLE_WEIGHT + (body.lower() + " ") * BODY_WEIGHT
    found = set()
    for topic, keywords in TOPICS.items():
        if any(kw in combined for kw in keywords):
            found.add(topic)
    return frozenset(found)


def load_posts(path: Path) -> list[Post]:
    posts = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            dt = _parse_dt(row.get("created_at") or "")
            if dt is None:
                continue
            title    = row.get("title") or ""
            body     = row.get("body_text") or ""
            platform = (row.get("platform") or "").lower().strip()
            if not platform:
                continue
            topics = extract_topics(title, body)
            if not topics:
                continue  # no signal — skip
            posts.append(Post(
                post_id          = row.get("post_id") or "",
                platform         = platform,
                title            = title[:120],
                body_text        = body[:300],
                created_at       = dt,
                engagement_score = _safe_float(row.get("engagement_score") or "0"),
                author           = row.get("author") or row.get("author_handle") or "",
                url              = row.get("url") or "",
                topics           = topics,
            ))
    return posts


# -------------------------------------------------------------------
# Cascade detection
# -------------------------------------------------------------------

def jaccard(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def find_cascades(posts: list[Post]) -> list[CascadeEvent]:
    """
    Algorithm:
    1. Sort posts by timestamp.
    2. Slide a 6-hour window. Within each window, group posts by topic overlap
       (shared topics >= TOPIC_OVERLAP_MIN).
    3. Merge overlapping groups that share the same dominant topics.
    4. Keep groups with 2+ platforms and 3+ posts.
    5. Score and classify each cascade.
    """
    now = datetime.now(timezone.utc)
    posts_sorted = sorted(posts, key=lambda p: p.created_at)

    # Step 1: build topic-keyed clusters using a sliding window
    # Each cluster is a list of posts that share a dominant topic set
    clusters: dict[frozenset, list[Post]] = defaultdict(list)

    for i, post in enumerate(posts_sorted):
        window_end = post.created_at + timedelta(hours=CASCADE_WINDOW_HOURS)
        # find all posts within window that overlap in topics
        for j in range(i + 1, len(posts_sorted)):
            other = posts_sorted[j]
            if other.created_at > window_end:
                break
            shared = post.topics & other.topics
            if len(shared) >= TOPIC_OVERLAP_MIN:
                key = frozenset(shared)
                clusters[key].append(post)
                clusters[key].append(other)

    # Deduplicate within clusters
    deduped: dict[frozenset, list[Post]] = {}
    for key, members in clusters.items():
        seen_ids = set()
        unique = []
        for p in members:
            if p.post_id not in seen_ids:
                seen_ids.add(p.post_id)
                unique.append(p)
        deduped[key] = unique

    # Step 2: filter to cascades (2+ platforms, 3+ posts)
    cascade_events = []
    seen_keys: set[frozenset] = set()

    for key, members in sorted(deduped.items(), key=lambda x: len(x[1]), reverse=True):
        platforms = set(p.platform for p in members)
        if len(platforms) < CASCADE_MIN_PLATFORMS:
            continue
        if len(members) < CASCADE_MIN_POSTS:
            continue

        # Avoid reporting the same cluster under multiple keys
        post_ids = frozenset(p.post_id for p in members)
        if post_ids in seen_keys:
            continue
        seen_keys.add(post_ids)

        # Sort members by time
        members_sorted = sorted(members, key=lambda p: p.created_at)
        first = members_sorted[0]
        last  = members_sorted[-1]
        window_h = (last.created_at - first.created_at).total_seconds() / 3600

        # Platform timeline
        platform_first_seen: dict[str, datetime] = {}
        for p in members_sorted:
            if p.platform not in platform_first_seen:
                platform_first_seen[p.platform] = p.created_at

        platforms_ordered = sorted(
            platform_first_seen.keys(),
            key=lambda pl: platform_first_seen[pl]
        )

        # Peak engagement post
        peak = max(members, key=lambda p: p.engagement_score)
        total_engagement = sum(p.engagement_score for p in members)
        hours_since_peak = (now - peak.created_at).total_seconds() / 3600

        # Status classification
        # Distinguish fast cascades (same-day spread) from sustained narratives (ongoing story)
        if window_h <= CASCADE_WINDOW_HOURS:
            cascade_type = "FAST_CASCADE"    # story spread across platforms in < 6h — real cascade
        else:
            cascade_type = "SUSTAINED"       # same narrative kept appearing over days/weeks

        if hours_since_peak < 6:
            status = "ACTIVE"
        elif hours_since_peak < 24:
            status = "EMERGING"
        elif hours_since_peak < 72:
            status = "DECAYING"
        else:
            status = "HISTORICAL"

        # Action recommendation
        if status == "ACTIVE":
            action = "Brief Tier 1 creator NOW — window closes in < 4h"
        elif status == "EMERGING":
            action = "Amplify via official channels; comparison content ready"
        elif status == "DECAYING":
            action = "Monitor — window passed; archive for next launch brief"
        else:
            action = "Archive as historical pattern evidence"

        dominant = sorted(key, key=lambda t: sum(1 for p in members if t in p.topics), reverse=True)[:3]

        cascade_events.append(CascadeEvent(
            event_id        = f"cascade_{first.created_at.strftime('%Y%m%d_%H%M')}_{list(key)[0][:12]}",
            cascade_type    = "FAST_CASCADE" if window_h <= CASCADE_WINDOW_HOURS else "SUSTAINED",
            dominant_topics = dominant,
            platforms       = platforms_ordered,
            platform_times  = {pl: platform_first_seen[pl].strftime("%Y-%m-%dT%H:%M UTC") for pl in platforms_ordered},
            window_hours    = round(window_h, 1),
            total_posts     = len(members),
            peak_engagement = peak.engagement_score,
            peak_post_title = peak.title,
            first_seen      = first.created_at.strftime("%Y-%m-%dT%H:%M UTC"),
            last_seen       = last.created_at.strftime("%Y-%m-%dT%H:%M UTC"),
            hours_since_peak= round(hours_since_peak, 1),
            status          = status,
            action          = action,
        ))

    # Sort: active first, then by post count
    status_order = {"ACTIVE": 0, "EMERGING": 1, "DECAYING": 2, "HISTORICAL": 3}
    cascade_events.sort(key=lambda c: (status_order.get(c.status, 9), -c.total_posts))

    return cascade_events


# -------------------------------------------------------------------
# Output formatting
# -------------------------------------------------------------------

def write_csv(events: list[CascadeEvent], path: Path) -> None:
    if not events:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for e in events:
        d = asdict(e)
        d["dominant_topics"]  = ", ".join(e.dominant_topics)
        d["platforms"]        = " → ".join(e.platforms)
        d["platform_times"]   = json.dumps(e.platform_times)
        rows.append(d)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _format_event(e: CascadeEvent, lines: list[str]) -> None:
    status_icon = {"ACTIVE": "🔴", "EMERGING": "🟡", "DECAYING": "🟠", "HISTORICAL": "⚫"}.get(e.status, "⚪")
    lines.append("")
    lines.append(f"{status_icon} {e.status} | {', '.join(e.dominant_topics)}")
    lines.append(f"   First seen:   {e.first_seen}")

    pl_timeline = []
    prev_time = None
    for pl in e.platforms:
        t_str = e.platform_times[pl]
        if prev_time:
            t_dt    = datetime.strptime(t_str, "%Y-%m-%dT%H:%M UTC").replace(tzinfo=timezone.utc)
            prev_dt = datetime.strptime(prev_time, "%Y-%m-%dT%H:%M UTC").replace(tzinfo=timezone.utc)
            delta_h = (t_dt - prev_dt).total_seconds() / 3600
            delta_str = f"+{int(delta_h * 60)}min" if delta_h < 1 else f"+{delta_h:.1f}h"
            pl_timeline.append(f"{pl.upper()} ({delta_str})")
        else:
            pl_timeline.append(f"{pl.upper()} (origin)")
        prev_time = t_str

    lines.append(f"   Spread:       {' → '.join(pl_timeline)}")
    lines.append(f"   Posts:        {e.total_posts} across {len(e.platforms)} platforms")
    lines.append(f"   Peak:         {e.peak_engagement:,.0f} pts — \"{e.peak_post_title[:65]}\"")
    lines.append(f"   ACTION:       {e.action}")


def write_report(events: list[CascadeEvent], path: Path, total_posts: int) -> str:
    """Slack-ready briefing — what a growth manager reads Monday morning."""
    now = datetime.now(timezone.utc)
    fast      = [e for e in events if e.cascade_type == "FAST_CASCADE"]
    sustained = [e for e in events if e.cascade_type == "SUSTAINED"]

    lines = [
        "=" * 70,
        "CLAUDE GROWTH INTELLIGENCE — CASCADE REPORT",
        f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Posts analyzed: {total_posts:,} | Cascades: {len(events)} "
        f"({len(fast)} fast, {len(sustained)} sustained)",
        "=" * 70,
    ]

    if fast:
        lines.append("\n── FAST CASCADES (same story spread cross-platform in < 6h) ──")
        lines.append("   Real-time alerts fire on these. Act within 4h.")
        for e in fast:
            _format_event(e, lines)

    if sustained:
        lines.append("\n── SUSTAINED NARRATIVES (ongoing cross-platform story threads) ──")
        lines.append("   Stories that keep appearing across platforms over days/weeks.")
        for e in sustained[:15]:
            _format_event(e, lines)

    lines.append("")
    lines.append("=" * 70)
    report = "\n".join(lines)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return report


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> None:
    if not INPUT_CSV.exists():
        print(f"[error] {INPUT_CSV} not found — run normalize_sources.py first", file=sys.stderr)
        raise SystemExit(1)

    print(f"[cascade] loading posts from {INPUT_CSV.name} ...", file=sys.stderr)
    posts = load_posts(INPUT_CSV)
    print(f"[cascade] {len(posts):,} posts with topic signal (of {sum(1 for _ in open(INPUT_CSV)) - 1:,} total)", file=sys.stderr)

    if not posts:
        print("[cascade] no posts with topic signal — check input file", file=sys.stderr)
        raise SystemExit(1)

    print(f"[cascade] detecting cascades (window={CASCADE_WINDOW_HOURS}h, min_platforms={CASCADE_MIN_PLATFORMS}) ...", file=sys.stderr)
    events = find_cascades(posts)
    print(f"[cascade] {len(events)} cascade events detected", file=sys.stderr)

    if events:
        write_csv(events, OUTPUT_CSV)
        report = write_report(events, OUTPUT_REPORT, len(posts))
        print(report)
        print(f"\n[cascade] → {OUTPUT_CSV}", file=sys.stderr)
        print(f"[cascade] → {OUTPUT_REPORT}", file=sys.stderr)
    else:
        print("[cascade] no cascades detected — try lowering CASCADE_MIN_POSTS or CASCADE_MIN_PLATFORMS", file=sys.stderr)


if __name__ == "__main__":
    main()
