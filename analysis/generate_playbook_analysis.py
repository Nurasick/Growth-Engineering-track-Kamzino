#!/usr/bin/env python3
"""
generate_playbook_analysis.py — AI-generated playbook analysis (Part 2).

Reads analysis_metrics.json (from compute_playbook_metrics.py) and sends it
to the Gemini API to produce a structured, data-backed PLAYBOOK_ANALYSIS_GENERATED.md.

Usage:
    python analysis/generate_playbook_analysis.py
    python analysis/generate_playbook_analysis.py --dry-run
"""

import os, json, sys, argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT         = Path(__file__).parent.parent
PROCESSED    = ROOT / "data" / "processed"
METRICS_FILE = PROCESSED / "analysis_metrics.json"
OUTPUT_MD    = ROOT / "PLAYBOOK_ANALYSIS_GENERATED.md"


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_prompt(metrics: dict) -> str:
    # Slim down the metrics: remove cumulative curve arrays (too large for prompt)
    slim = json.loads(json.dumps(metrics))  # deep copy
    for p_data in slim.get("pareto", {}).values():
        p_data.pop("cumulative_pct_posts", None)
        p_data.pop("cumulative_pct_engagement", None)
    # Keep only top 5 authors to save tokens
    ac = slim.get("author_concentration", {})
    ac["top_10_authors"] = ac.get("top_10_authors", [])[:5]
    # Keep only top 10 word lift entries
    wl = slim.get("word_lift", {})
    wl["top_lift_words"]    = wl.get("top_lift_words", [])[:10]
    wl["bottom_lift_words"] = wl.get("bottom_lift_words", [])[:5]

    data_block = json.dumps(slim, indent=2, ensure_ascii=False)

    total_posts  = metrics.get("spike_stats", {}).get("total_posts", "N/A")
    hn_top10     = metrics.get("pareto", {}).get("hn",      {}).get("top_10pct_share", "?")
    x_top10      = metrics.get("pareto", {}).get("x",       {}).get("top_10pct_share", "?")
    yt_top10     = metrics.get("pareto", {}).get("youtube", {}).get("top_10pct_share", "?")
    top5_share   = metrics.get("author_concentration", {}).get("top5_share_pct", "?")
    reddit_lift  = metrics.get("media_vs_text", {}).get("reddit", {}).get("lift_median", "?")
    x_lift       = metrics.get("media_vs_text", {}).get("x",      {}).get("lift_median", "?")

    return f"""You are a senior growth analyst writing a data-backed research report.
You have real scraped data from a competitive intelligence pipeline that analyzed how Claude (Anthropic's AI assistant) went viral across Hacker News, Reddit, YouTube, and X/Twitter.

Your job: write PLAYBOOK_ANALYSIS_GENERATED.md — a structured findings document (Part 2 of the HackNU 2026 Growth Engineering challenge).

STRICT RULES:
1. Every finding MUST include a specific number from the DATA BLOCK. No exceptions.
2. Use compact markdown. Do NOT pad table columns with spaces.
3. Each finding ends with a "**Growth Insight:**" paragraph explaining why this pattern matters.
4. Write like a data journalist: lead with the number, then explain the implication.
5. Only use statistics that appear in the DATA BLOCK — never invent figures.
6. Keep each finding section under 200 words. Be direct.

KEY NUMBERS TO HIGHLIGHT (cite these prominently):
- Total posts analyzed: {total_posts}
- HN: top 10% of posts = {hn_top10}% of all engagement
- X: top 10% of posts = {x_top10}% of all engagement
- YouTube: top 10% of posts = {yt_top10}% of all engagement
- Top 5 authors = {top5_share}% of total engagement (702 unique authors total)
- Reddit media posts: {reddit_lift}x median engagement vs text-only
- X media posts: {x_lift}x median engagement vs text-only

=== SCRAPED DATA (use these numbers only) ===
{data_block}
=== END DATA ===

Write the full document in this exact structure. Use compact markdown tables (no column padding):

# Claude's Viral Growth Playbook — Decoded
## HackNU 2026 · Growth Engineering Track · Part 2

> **Data provenance:** All findings derived from our scraped dataset: [total posts] posts across HN, Reddit, YouTube, X (April 2026). No external sources.

---

## Dataset Summary
[table: Platform | Posts | Coverage | Scraper method]

---

## Finding 1 — The 3-Wave Cascade Is Real
[Use the cascade timestamps from the data. Table: Time | Platform | Score | Event]
[Wave structure: wave1/wave2/wave3 from cascade data]
**Growth Insight:** [one paragraph on what this means for competing products]

---

## Finding 2 — Community Creators Outperform Official Channel by 30x
[Use youtube_ratio data. Table: Channel | Videos | Total Views | Avg/Video]
[Top 5 channels from youtube_ratio.top_channels]
**Growth Insight:** [why briefing creators > running official content]

---

## Finding 3 — Spike Type Volume vs Engagement Are Inverted
[Use spike_stats.by_type. Table: Spike Type | % of Posts | Avg Engagement | Median Engagement]
[Comment on the mean vs median gap for breakthrough posts]
**Growth Insight:** [what this means about content strategy]

---

## Finding 4 — Platform Timing Windows
[Use timing data. Two tables: HN top 5 UTC hours | Reddit by weekday avg score]
**Growth Insight:** [specific scheduling recommendation with the numbers]

---

## Finding 5 — Title Word Lift
[Use word_lift.top_lift_words. Table: Word | Lift | Interpretation]
[Include bottom_lift_words table too — what NOT to put in titles]
**Growth Insight:** [title formula for maximum reach]

---

## Finding 6 — Engagement Decay by Platform
[Use decay data. Table: Platform | Day 0 velocity | Day 1 | Day 3 | Day 6]
**Growth Insight:** [scheduling cadence based on decay curves]

---

## Finding 7 — The 10/80 Rule: Engagement is Pareto-Concentrated
[Use pareto data. Table: Platform | Posts | Top 10% share | Posts needed for 80% of engagement]
[This is a NEW finding not in prior analysis — make it prominent]
**Growth Insight:** [what this means — optimize for spikes, not average performance]

---

## Finding 8 — Author Concentration: Top 5 Accounts = {top5_share}% of Engagement
[Use author_concentration. Table: Author | Platform | Views | % of Total]
[Note: 702 unique authors, but {top5_share}% concentration]
[This is a NEW finding — the "organic" narrative partially masks how concentrated reach actually is]
**Growth Insight:** [implication — identify the 5 key accounts for any competing product]

---

## Finding 9 — Media Posts Drive 8–10x Higher Engagement
[Use media_vs_text. Table: Platform | Media Count | Text Count | Media Median | Text Median | Lift]
[This is a NEW finding]
**Growth Insight:** [specific recommendation: always attach media on Reddit and X]

---

## Finding 10 — Comment Sentiment Signals Spike Type
[Use comment_sentiment. Table: Spike Type | Positive % | Neutral % | Negative %]
[This is a NEW finding — 1,163 comments analyzed]
**Growth Insight:** [how to use sentiment as an early signal before engagement peaks]

---

## Limitations
- [4-5 honest bullets about data gaps and statistical caveats]

---

## Summary: Claude's Growth Playbook in 10 Rules
[10 one-sentence rules. Every sentence must contain at least one number from the data.]
"""


# ── Gemini API ────────────────────────────────────────────────────────────────

def call_gemini(prompt: str) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("ERROR: google-genai not installed. Run: pip install google-genai")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY not set in .env")

    import re
    client = genai.Client(api_key=api_key)
    print("  [api] Calling Gemini models/gemini-2.5-flash...")

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=8192,
        ),
    )
    text = response.text or ""
    # Collapse excessive whitespace padding from table alignment
    text = re.sub(r" {10,}", "  ", text)
    return text


# ── Output ────────────────────────────────────────────────────────────────────

def write_output(content: str, metrics: dict) -> Path:
    now   = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = metrics.get("spike_stats", {}).get("total_posts", "?")
    plat  = metrics.get("platform_stats", {})
    plat_str = ", ".join(f"{p}: {v['count']}" for p, v in plat.items())

    header = f"""<!-- Generated: {now} -->
<!-- Model: gemini/models/gemini-2.5-flash -->
<!-- Source data: {total} classified posts — {plat_str} -->
<!-- Audit trail: data/processed/analysis_metrics.json -->

"""
    OUTPUT_MD.write_text(header + content, encoding="utf-8")
    return OUTPUT_MD


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate AI playbook analysis from scraped data")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build prompt but skip API call")
    args = parser.parse_args()

    # Load .env
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    # Load metrics
    if not METRICS_FILE.exists():
        sys.exit("ERROR: analysis_metrics.json not found — run compute_playbook_metrics.py first")

    print("  [analysis] Loading metrics...")
    metrics = json.loads(METRICS_FILE.read_text(encoding="utf-8"))

    # Build prompt
    prompt = build_prompt(metrics)
    print(f"  [analysis] Prompt built ({len(prompt):,} chars)")

    if args.dry_run:
        dry = PROCESSED / "analysis_prompt_dry_run.txt"
        dry.write_text(prompt, encoding="utf-8")
        print(f"  [dry-run] Saved → {dry}")
        return

    # Call API
    content = call_gemini(prompt)

    # Write output
    out = write_output(content, metrics)
    lines = content.count("\n")
    nums  = len(__import__("re").findall(r"\b\d[\d,.]+\b", content))
    print(f"\n  [done] {out.name}  ({lines} lines, {nums} data citations)")


if __name__ == "__main__":
    main()
