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

    return f"""You are a senior growth engineer writing a data-backed growth playbook — not a research summary.

A growth playbook has a specific job: a new team member should be able to read it on Monday
and know exactly what to do, in what order, for which platform, and who owns each action.
If someone reads this and doesn't know what to do next, the playbook has failed.

---

## STEP 1 — Detect the playbook type

Before writing anything, scan the data and classify which primary growth pattern this dataset
represents. Pick ONE of the following:

| Type | Pattern signature | Playbook shape |
|---|---|---|
| **Cascade** | Viral events dominate; content spreads in waves across platforms | Structure around timing windows and creator briefing |
| **Community-led** | Organic switching narratives, competitor subreddits outperform home turf | Structure around seeding channels and framing |
| **Creator-driven** | A handful of individual accounts generate most reach | Structure around identifying and activating key voices |
| **Event-reactive** | External events (controversy, scandal, competitor moves) generate biggest spikes | Structure around monitoring and rapid response |
| **Hybrid** | 2–3 of the above contribute significantly | Name the dominant + secondary type; structure reflects both |

State the detected type at the top of the document:
> **Playbook type:** [type] — [one sentence on what this means for the action plan]

---

## STEP 2 — Write the document

### Strict rules

1. Every finding MUST cite a specific number from the DATA BLOCK.
2. Each finding section must include ALL FIVE of: **stat → insight → owner → action → confidence**.
3. Use compact markdown tables (no column padding).
4. Write like a data journalist: lead with the number, then explain it.
5. Never invent figures. Only use statistics from the DATA BLOCK.
6. Keep each finding under 200 words.
7. The summary and action stack go AT THE TOP, before the findings.

---

## DOCUMENT STRUCTURE

# [Product]'s Viral Growth Playbook — Decoded

> **Playbook type:** [detected type from Step 1]
> **Data provenance:** All findings derived from [N] posts scraped across [platforms], [date range].

---

## TL;DR — 10 Rules (read this first)

[10 one-sentence rules. Every sentence must contain at least one number from the data.
Each rule must name an owner in parentheses: (Growth), (Content), (Comms), (Engineering).]

---

## Prioritized Action Stack

The 5 highest-leverage plays, ranked by (estimated impact) × (execution speed).
For each play, include: what to do, when, who owns it, and what "done" looks like.

| # | Play | Impact | Effort | Owner | Done when |
|---|---|---|---|---|---|
| 1 | ... | High | Low | Growth | ... |
| 2 | ... | High | Med | Content | ... |
...

---

## Launch Day Protocol

Hour-by-hour checklist for the first 48h of any major launch or event.
Synthesizes findings on cascade timing, creator briefing, and platform decay.

| Window | Action | Owner | Platform |
|---|---|---|---|
| T-72h | Brief [creator names] with embargo assets | Growth | YouTube/X |
| T-0h | Post on [platform] at [exact time UTC] | Content | HN |
| T+2h | ... | | |
...

---

## Dataset Summary

[table: Platform | Posts | Coverage | Scraper method]

---

## Finding 1 — [Title]

[Stat from data. Table if available.]

**Growth Insight:** [What it means, specifically.]
**Owner:** [Growth / Content / Comms / Engineering]
**Action:** [One concrete action sentence.]
**Confidence:** [High (n>500) / Medium (n=25–500) / Directional (n<25 or single event)]

---

[Repeat for all findings. Required findings, in order:]

## Finding 1 — The Power Law Is the Whole Game
## Finding 2 — The 3-Wave Cascade (Timestamped)
## Finding 3 — Spike Type Volume vs Engagement Inverted
## Finding 4 — Platform Timing Windows
## Finding 5 — Title Word Lift (what to say and what kills reach)
## Finding 6 — Engagement Decay by Platform
## Finding 7 — The 10/80 Rule: Engagement Is Pareto-Concentrated
## Finding 8 — Author Concentration: Top 5 Accounts = {top5_share}% of Engagement
## Finding 9 — Media Posts Drive 8–10x Higher Engagement
## Finding 10 — Comment Sentiment as an Early Signal

---

## Limitations

[Inline with each finding above — but also list here globally:]
- [4–5 honest bullets, each with the affected finding number]

---

## KEY NUMBERS TO HIGHLIGHT (cite these prominently)

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
