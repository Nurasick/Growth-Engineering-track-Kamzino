#!/usr/bin/env python3
"""
Hybrid LLM Spike Classifier

Confidence-based routing — the same pattern used in production ML pipelines:
  - Keyword classifier confidence >= 0.60 → keep label (fast, free, deterministic)
  - Keyword classifier confidence <  0.60 → send to Claude Haiku (accurate, $0.01/post)

This is how real systems avoid paying for LLM calls on easy cases while getting
accuracy where the rules genuinely can't decide. A post titled "How I use Claude
for therapy" is ambiguous between tutorial/personal — Haiku handles it. A post
titled "Anthropic releases Claude 4" is clearly breakthrough — keyword wins.

Reads:  data/processed/spike_classified.csv  (keyword classifier output)
Writes: data/processed/spike_classified_llm.csv  (hybrid output)
        data/processed/llm_classifier_report.txt  (comparison summary)

Requires: ANTHROPIC_API_KEY in .env
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

REPO_ROOT      = Path(__file__).parent.parent
PROCESSED_DIR  = REPO_ROOT / "data" / "processed"
INPUT_CSV      = PROCESSED_DIR / "spike_classified.csv"
OUTPUT_CSV     = PROCESSED_DIR / "spike_classified_llm.csv"
REPORT_TXT     = PROCESSED_DIR / "llm_classifier_report.txt"

# Load .env
_env = REPO_ROOT / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CONFIDENCE_THRESHOLD = 0.60   # below this → send to LLM
SPIKE_TYPES = ["breakthrough", "tutorial", "comparison", "personal", "meme"]
MAX_LLM_CALLS = 100           # safety cap — don't burn the key on a full run


def call_haiku(title: str, body: str, platform: str) -> Optional[dict]:
    """
    Call Claude claude-haiku-4-5 to classify a post.
    Returns dict with spike_type, confidence, reason — or None on failure.
    """
    try:
        import urllib.request
        import urllib.error

        text = f"Platform: {platform}\nTitle: {title[:200]}\nBody: {body[:300]}"
        prompt = f"""Classify this social media post about Claude AI into exactly one spike type.

Spike types:
- breakthrough: official announcements, releases, research papers, funding news
- tutorial: how-to guides, workflows, tips, demos, walkthroughs
- comparison: Claude vs other models, switching stories, benchmarks
- personal: personal stories, testimonials, emotional experiences, saved my job
- meme: humor, viral/funny content, jokes, irreverent takes

Post:
{text}

Respond with JSON only, no explanation outside the JSON:
{{"spike_type": "<one of the 5 types>", "confidence": <0.0-1.0>, "reason": "<one sentence>"}}"""

        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 100,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            text_out = data["content"][0]["text"].strip()
            # strip markdown code fences if present
            if text_out.startswith("```"):
                text_out = text_out.split("```")[1]
                if text_out.startswith("json"):
                    text_out = text_out[4:]
            result = json.loads(text_out)
            if result.get("spike_type") not in SPIKE_TYPES:
                result["spike_type"] = "breakthrough"
            result["confidence"] = max(0.0, min(1.0, float(result.get("confidence", 0.5))))
            return result

    except Exception as e:
        print(f"  [llm] API error: {e}", file=sys.stderr)
        return None


def main() -> None:
    if not ANTHROPIC_API_KEY:
        print("[llm_classifier] No ANTHROPIC_API_KEY — set it in .env", file=sys.stderr)
        raise SystemExit(1)

    if not INPUT_CSV.exists():
        print(f"[llm_classifier] {INPUT_CSV} not found — run spike_classifier.py first", file=sys.stderr)
        raise SystemExit(1)

    with INPUT_CSV.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    print(f"[llm_classifier] {len(rows)} posts loaded", file=sys.stderr)

    # Separate high-confidence (keyword wins) from low-confidence (LLM needed)
    high_conf = [r for r in rows if float(r.get("confidence") or 0) >= CONFIDENCE_THRESHOLD]
    low_conf  = [r for r in rows if float(r.get("confidence") or 0) <  CONFIDENCE_THRESHOLD]

    print(f"[llm_classifier] routing: {len(high_conf)} keyword ({CONFIDENCE_THRESHOLD:.0%}+ conf) "
          f"| {len(low_conf)} → LLM (capped at {MAX_LLM_CALLS})", file=sys.stderr)

    llm_sample = low_conf[:MAX_LLM_CALLS]
    llm_pass   = 0
    llm_fail   = 0
    disagreements = []

    output_rows = []

    # High-confidence posts — keyword label stands
    for r in high_conf:
        output_rows.append({
            **r,
            "llm_spike_type":  "",
            "llm_confidence":  "",
            "llm_reason":      "",
            "classifier_used": "keyword",
        })

    # Low-confidence posts — call Haiku
    for i, r in enumerate(llm_sample):
        if i % 10 == 0:
            print(f"  [llm] {i}/{len(llm_sample)} ...", file=sys.stderr)

        result = call_haiku(
            title    = r.get("title") or "",
            body     = "",   # spike_classified.csv doesn't carry body — title is enough
            platform = r.get("platform") or "",
        )

        if result:
            llm_pass += 1
            keyword_label = r.get("spike_type", "")
            llm_label     = result["spike_type"]
            if keyword_label != llm_label:
                disagreements.append({
                    "title":           (r.get("title") or "")[:80],
                    "platform":        r.get("platform"),
                    "keyword_label":   keyword_label,
                    "keyword_conf":    r.get("confidence"),
                    "llm_label":       llm_label,
                    "llm_conf":        result["confidence"],
                    "llm_reason":      result["reason"],
                })
            output_rows.append({
                **r,
                "llm_spike_type":  llm_label,
                "llm_confidence":  result["confidence"],
                "llm_reason":      result["reason"],
                "classifier_used": "llm",
            })
        else:
            llm_fail += 1
            # Fallback: keep keyword label
            output_rows.append({
                **r,
                "llm_spike_type":  "",
                "llm_confidence":  "",
                "llm_reason":      "api_error",
                "classifier_used": "keyword_fallback",
            })

        time.sleep(0.1)  # gentle rate limiting

    # Low-confidence posts beyond the LLM cap — keep keyword label
    for r in low_conf[MAX_LLM_CALLS:]:
        output_rows.append({
            **r,
            "llm_spike_type":  "",
            "llm_confidence":  "",
            "llm_reason":      "beyond_cap",
            "classifier_used": "keyword",
        })

    # Write output CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) + ["llm_spike_type", "llm_confidence", "llm_reason", "classifier_used"]
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    # Write comparison report
    disagree_pct = len(disagreements) / max(llm_pass, 1) * 100
    lines = [
        "=" * 70,
        "HYBRID CLASSIFIER REPORT",
        f"Total posts: {len(rows)} | Keyword: {len(high_conf)} | LLM: {llm_pass} | LLM errors: {llm_fail}",
        f"Disagreements (keyword vs LLM): {len(disagreements)} / {llm_pass} = {disagree_pct:.1f}%",
        "=" * 70,
        "",
        "What the keyword classifier gets wrong (LLM disagrees):",
        "",
    ]
    for d in disagreements[:20]:
        lines.append(f"  [{d['platform'].upper()}] \"{d['title']}\"")
        lines.append(f"    keyword → {d['keyword_label']} ({float(d['keyword_conf']):.2f} conf)")
        lines.append(f"    LLM     → {d['llm_label']} ({d['llm_conf']:.2f} conf): {d['llm_reason']}")
        lines.append("")

    lines += [
        "=" * 70,
        "Routing logic:",
        f"  >= {CONFIDENCE_THRESHOLD:.0%} confidence → keyword label (fast, free, deterministic)",
        f"  <  {CONFIDENCE_THRESHOLD:.0%} confidence → Claude Haiku (accurate, ~$0.001/post)",
        "  Cost this run: ~$" + f"{llm_pass * 0.001:.3f} (Haiku input+output at 200 tokens avg)",
        "=" * 70,
    ]

    report = "\n".join(lines)
    REPORT_TXT.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n[llm_classifier] → {OUTPUT_CSV}", file=sys.stderr)
    print(f"[llm_classifier] → {REPORT_TXT}", file=sys.stderr)


if __name__ == "__main__":
    main()
