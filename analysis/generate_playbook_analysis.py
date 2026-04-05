#!/usr/bin/env python3
"""
generate_playbook_analysis.py — AI-generated playbook analysis (Part 2).

Reads analysis_metrics.json (from compute_playbook_metrics.py) and calls the
Gemini API in TWO passes to produce PLAYBOOK_ANALYSIS_GENERATED.md.

  Pass 1 — Causality + skeleton:
    Detects playbook type, writes the cross-platform causality analysis,
    TL;DR rules, action stack, launch protocol, and dataset summary.
    Output is short enough to always complete within token limits.

  Pass 2 — Findings + strategic playbooks:
    Receives Pass 1 output as context, then writes all 14 findings and
    the three strategic playbooks (A/B/C).
    Token budget is used entirely for content, not for repeated setup.

Why two passes?
  The full document is ~7,000–9,000 words. At 8,192 max_output_tokens the
  model was reliably truncating before finishing the strategic playbooks.
  Splitting the work means each pass has its own token budget and neither
  runs out before completing its section.

Usage:
    python analysis/generate_playbook_analysis.py
    python analysis/generate_playbook_analysis.py --dry-run
    python analysis/generate_playbook_analysis.py --pass1-only
"""

import os, json, sys, time, argparse, re
from pathlib import Path
from datetime import datetime, timezone

ROOT         = Path(__file__).parent.parent
PROCESSED    = ROOT / "data" / "processed"
METRICS_FILE = PROCESSED / "analysis_metrics.json"
OUTPUT_MD    = ROOT / "PLAYBOOK_ANALYSIS_GENERATED.md"

# Sections that MUST appear in the final document. Used to detect truncation.
REQUIRED_SECTIONS = [
    "## TL;DR",
    "## Prioritized Action Stack",
    "## Launch Day Protocol",
    "## Cross-Platform Causality",
    "## Finding 1",
    "## Finding 7",
    "## Finding 14",
    "### Playbook A",
    "### Playbook B",
    "### Playbook C",
    "## Limitations",
]


# ── Data preparation ──────────────────────────────────────────────────────────

def slim_metrics(metrics: dict) -> dict:
    """
    Remove fields that bloat the prompt without adding analytical value.
    All slimming happens here — the prompts themselves never touch raw metrics.
    """
    import copy
    m = copy.deepcopy(metrics)

    # Drop cumulative curve arrays (large, not useful in prose)
    for p_data in m.get("pareto", {}).values():
        p_data.pop("cumulative_pct_posts", None)
        p_data.pop("cumulative_pct_engagement", None)

    # Keep only top 5 authors (the long tail adds no strategic signal)
    ac = m.get("author_concentration", {})
    ac["top_10_authors"] = ac.get("top_10_authors", [])[:5]

    # Keep top 10 + bottom 5 word lift entries (enough to see the pattern)
    wl = m.get("word_lift", {})
    wl["top_lift_words"]    = wl.get("top_lift_words",    [])[:10]
    wl["bottom_lift_words"] = wl.get("bottom_lift_words", [])[:5]

    return m


# ── Prompt builders ───────────────────────────────────────────────────────────

# The system role is the same for both passes — defined once here.
SYSTEM_ROLE = """You are a senior growth engineer at a competing AI company.
You have been given a scraped intelligence dataset on how a product went viral
across Hacker News, Reddit, YouTube, and X/Twitter.

Your job: write sections of PLAYBOOK_ANALYSIS.md — a strategic playbook a new
growth engineer can act on immediately. This is not a research summary. Every
section must end with a concrete action, an owner, and a confidence level.

STRICT RULES — apply to every word you write:
1. Every number must come from the DATA BLOCK. Do not invent figures.
   Do not use knowledge from your training data. If a number is not in
   the DATA BLOCK, write "not available in dataset" and move on.
2. Actions must be specific. Name the trigger condition, the threshold,
   the timing, and the framing. Vague verbs like "monitor", "consider",
   and "leverage" are banned unless followed by a concrete specification.
3. Confidence levels must cite sample size: High (n>500 multi-platform),
   Medium (n=25–500), Directional (n<25 or single event).
4. Cross-platform links are mandatory in every finding. If none exist,
   write "Platform-isolated: no cross-platform signal in this data."
5. No image references. No charts. Tables and prose only.
6. When data does not support a causal claim, write
   "the data suggests but does not confirm" — never assert causality as fact.
"""


def build_pass1_prompt(data_block: str) -> str:
    """
    Pass 1: playbook type detection + cross-platform causality analysis +
    document skeleton (TL;DR, action stack, launch protocol, dataset summary).

    Kept deliberately short so the model always completes within token limits.
    Pass 2 receives this output as context.
    """
    return f"""{SYSTEM_ROLE}

---

# YOUR TASK — PASS 1 OF 2

Write the FIRST HALF of the playbook. Pass 2 will write the findings and
strategic playbooks. Your output in this pass becomes the context for Pass 2.

Produce these sections IN ORDER. Do not skip any.

---

## SECTION 1 — Playbook type (2 sentences max)

Read the DATA BLOCK. Classify the dominant growth pattern:

| Type | Signature |
|---|---|
| Cascade | Events spread in waves across platforms in <48h |
| Community-led | Organic switching narratives; competitor communities outperform home community |
| Creator-driven | A small number of individual accounts generate disproportionate reach |
| Event-reactive | External controversies and competitor moves produce the biggest spikes |
| Hybrid | Multiple patterns — name dominant + secondary |

Output format (one line at the very top):
> **Playbook type:** [type] — [one sentence on what this means for strategy]

---

## SECTION 2 — TL;DR — 10 Rules (read this first)

10 one-sentence rules derived from the data. Every rule must:
- Contain at least one specific number from the DATA BLOCK
- Name the platform it applies to
- Name an owner in parentheses: (Growth), (Content), (Comms), (Engineering), (Leadership)

---

## SECTION 3 — Prioritized Action Stack

The 5 highest-leverage plays right now, ranked by impact × execution speed.

| # | Play | Why now | Impact | Effort | Owner | Done when |
|---|---|---|---|---|---|---|

Every "Why now" cell must reference a finding number (e.g., "F2 — cascade window").
Every "Done when" cell must be a concrete, verifiable state.

---

## SECTION 4 — Launch Day Protocol (48h window)

Hour-by-hour checklist. Every row references a finding number in the last column.

| Window | Action | Platform | Owner | Finding |
|---|---|---|---|---|
| T-72h | | | | |
| T-0h | | | | |
...through T+48h

---

## SECTION 5 — Dataset Summary

| Platform | Posts | Coverage | Method |
|---|---|---|---|

---

## SECTION 6 — Cross-Platform Causality Analysis

This is the analytical core. Answer each question using specific numbers from
the DATA BLOCK. If data is missing for a question, say so explicitly.

**A. Does HN ignition reliably pull Reddit?**
Look at HN→Reddit lag across all cascade narratives. What is the range of lags?
Is lag shorter for scandal/leak vs opinion/narrative content? Is there a HN score
threshold above which Reddit activation appears near-certain?

**B. Does HN ignition pull YouTube — and through which pathway?**
Distinguish two pathways:
1. Pre-briefed creators (lag <2h — parallel to HN, not caused by it)
2. Organic YouTube reaction (lag 10h+ — likely caused by HN traction)
When should a growth team rely on briefing vs wait for organic cascade?

**C. Is Reddit always downstream of HN?**
Do all cascade narratives in the data originate on HN? Does any start on Reddit?
Strategic implication: if Reddit is always downstream, it is an amplifier not an
ignition source — how does this change where you invest effort?

**D. Does HN score determine organic cascade reach?**
Argue for or against: "HN score is the social proof signal that tells organic
YouTube creators whether a story is worth covering." Use data from the cascade
timing table to support your argument.

**E. Do simultaneous narratives compound or cannibalize reach?**
Look at periods where multiple narratives overlap in the monthly view data.
Does total reach compound, or does one narrative crowd out the other?
Strategic implication for launch timing.

**F. Cascade speed synthesis table**

Build this table from all cascade narratives in the DATA BLOCK:

| Narrative | HN→Reddit lag | HN→X lag | HN→YouTube lag | Platforms | Speed |
|---|---|---|---|---|---|

Then answer: does scandal cascade faster than opinion content? Should fast and
slow cascades have different response playbooks?

---

=== DATA BLOCK ===
{data_block}
=== END DATA BLOCK ===
"""


def build_pass2_prompt(data_block: str, pass1_output: str) -> str:
    """
    Pass 2: all 14 findings + three strategic playbooks + limitations table.

    Receives Pass 1 output as context so it can reference findings and numbers
    already established, without re-reading the setup instructions.
    """
    return f"""{SYSTEM_ROLE}

---

# YOUR TASK — PASS 2 OF 2

Pass 1 has already been written. It contains the playbook type, TL;DR,
action stack, launch protocol, dataset summary, and cross-platform causality
analysis. You do NOT rewrite those sections.

Your job: write the SECOND HALF — all 14 findings and the three strategic
playbooks — then append a limitations table.

The Pass 1 output is provided below as context. Reference it where relevant
(e.g., "as established in the causality analysis...").

---

## PASS 1 OUTPUT (context — do not rewrite)

{pass1_output}

---

## YOUR OUTPUT — write each of the following sections in order

---

### Finding structure (apply to every finding)

```
## Finding N — [Title]

**Claim:** [one sentence]

[data table or evidence list — DATA BLOCK numbers only]

**Cross-platform link:** [lag, direction, and whether it is causal or correlational.
If platform-isolated, state that explicitly.]

**Growth Insight:** [what the pattern means]

**Strategy:**
1. [specific tactic with trigger, threshold, timing, framing]
2. [specific tactic]
3. [optional third tactic]

**Owner:** [role]
**Confidence:** [High/Medium/Directional — cite n]
```

---

### Finding 1 — The Power Law Is the Whole Game
Show the score/engagement distribution. The key insight: a tiny fraction of posts
generate nearly all reach, and those top-tier posts are the same ones that triggered
cross-platform cascades. Use the Pareto data from the DATA BLOCK.
Cross-platform link: connect power law to cascade activation probability.

### Finding 2 — The 3-Wave Cascade (Timestamped)
Use the most detailed timestamped event sequence in the DATA BLOCK.
Show HN → YouTube → Reddit → international spread with exact hours.
Distinguish pre-briefed vs organic YouTube pathway explicitly.
State which events were caused by HN traction vs pre-planned.

### Finding 3 — Spike Type Volume vs Engagement Inverted
Use the spike type classification data. Note which dataset subset was used if
applicable. Key insight: the most common content type is not the highest-floor
type. Map spike types to platforms — which types belong where.

### Finding 4 — Platform Timing Windows
Use HN hourly data and Reddit day-of-week data. Derive the optimal cross-platform
posting sequence: which day + time combination maximizes the HN→Reddit handoff
before HN engagement decays.

### Finding 5 — Title Word Lift
Use word lift data. Show high-lift AND low-lift words in separate tables.
Key insight: high-lift words cluster around a theme — name that theme.
Cross-platform link: high-lift HN titles are the social proof signal for organic
YouTube pickup (connect to Finding 2's organic pathway).

### Finding 6 — The Sustained Controversy or Halo Effect
Use the controversy/event timeline data if present in DATA BLOCK (e.g., a
multi-week event cluster). Show how sustained controversy elevates the baseline
for ALL content in the same period, not just individual posts.
Cross-platform: does the elevated HN baseline coincide with elevated Reddit/X
activity in the same window?

### Finding 7 — Community Creators vs Official Channel
Use YouTube channel comparison data. Show the community/official ratio.
Also compare X official vs X community performance — the contrast reveals
platform-specific budget allocation logic.
Cross-platform: do organic YouTube creators monitor HN as a coverage signal?

### Finding 8 — Engagement Decay by Platform
Use velocity/decay data. Show how decay curves interact across platforms.
Key insight: different decay rates create a sequencing window — map it explicitly.
What is the optimal posting day so HN→Reddit handoff happens before HN goes cold?

### Finding 9 — Competitor Attacks as Organic Growth Events
Use competitor-generated content data and the Claude discourse spikes it caused.
Key insight: external threats generate more reach than own launches via tribal
defense. Cross-platform: does a competitor attack on X also produce HN threads?

### Finding 10 — The Movement Naming Effect
Use data on a coined phrase (e.g., "vibe coding" or equivalent in DATA BLOCK)
that became the dominant framing for the product. Show the compound cross-platform
effect: a phrase coined on X creates YouTube search volume and HN discussion frames.

### Finding 11 — The Inside Engineer Effect
Use data comparing an internal engineer's personal posting to the official account.
Key insight: sustained multiplier across many post types, not one outlier.
Cross-platform link: do high-performing personal X posts generate HN secondary threads?

### Finding 12 — Small Accounts and Viral Outliers
Use follower-count vs views data. Key insight: outlier-to-median ratio is highest
in small-account bucket. Cross-platform: does elevated ambient HN activity lower
the viral threshold for small-account X posts in the same period?

### Finding 13 — Competitor Community Outperforms Home Community
Use subreddit comparison data. Key insight: competitor-community readers have
higher purchase intent. Cross-platform: does a viral competitor-subreddit post
generate X quote-tweets and HN threads in the same window?

### Finding 14 — The Switching Narrative as a Durable Cross-Platform Thread
Use cascade detector output. Show narrative clusters and spread patterns.
Key insight: what looks like independent posts is one continuous thread.
Produce two mini-playbooks at the end of this finding:
  - Amplification playbook: how to detect a nascent switching narrative and
    accelerate it without making it look manufactured
  - Defense playbook: how to detect an attack narrative early and prevent
    it from cascading to the next platform

---

## Strategic Synthesis — Three Playbooks

These are decision trees, not summaries. Reference specific finding numbers
at every decision point.

### Playbook A — The Launch Playbook
*Use when: you control the timing.*

Write as a numbered decision tree:
- T-72h: [action] → if [condition], then [branch]
- T-0h: [action] → if HN score < [threshold from data] at T+4h, then [escalation]
- T+2h through T+48h: [sequenced actions with decision rules]
- Contingency: if nothing is gaining traction at T+8h, what is the escalation path?

### Playbook B — The Rapid Response Playbook
*Use when: external event — competitor attack, controversy, or unplanned leak.*

Write as a numbered decision tree:
- First 30 min: [what to assess]
- First 2h: [which platform first, and why — cite cascade timing data]
- The "do not amplify" rule: [threshold below which staying silent is correct]
- T+12h to T+48h: [how response evolves across waves]

### Playbook C — The Ambient Narrative Playbook
*Use when: no launch, no crisis — maintaining long-term cross-platform presence.*

Write as a weekly/monthly cadence:
- Daily: [what to monitor, at what thresholds]
- Weekly: [switching narrative seeding in competitor communities]
- Monthly: [inside engineer posting support, naming event watch]
- Early warning: [specific signal that an attack narrative is starting to cascade]

---

## Limitations

| Limitation | Findings affected | Severity |
|---|---|---|
| [e.g., YouTube window only 2 weeks] | F7, F2 | Medium |
...4–6 rows total, derived from actual data gaps in the DATA BLOCK

---

=== DATA BLOCK ===
{data_block}
=== END DATA BLOCK ===
"""


# ── Gemini API ────────────────────────────────────────────────────────────────

def call_gemini(prompt: str, pass_label: str, max_retries: int = 3) -> str:
    """
    Call Gemini with retry logic and clear error messages.
    Uses the maximum output token budget available to avoid truncation.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("ERROR: google-genai not installed. Run: pip install google-genai")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY not set in environment or .env file")

    client = genai.Client(api_key=api_key)

    for attempt in range(1, max_retries + 1):
        try:
            print(f"  [api] {pass_label} — attempt {attempt}/{max_retries}...")
            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    # Use the maximum output budget. The model will stop when
                    # it finishes, not when it hits this limit — so setting it
                    # high does not force padding, it just removes the ceiling.
                    max_output_tokens=65536,
                ),
            )
            text = response.text or ""

            if not text.strip():
                raise ValueError("API returned empty response")

            # Collapse excessive whitespace from table alignment
            text = re.sub(r" {10,}", "  ", text)
            print(f"  [api] {pass_label} — received {len(text):,} chars")
            return text

        except Exception as e:
            print(f"  [api] {pass_label} — attempt {attempt} failed: {e}")
            if attempt < max_retries:
                wait = 2 ** attempt  # exponential backoff: 2s, 4s, 8s
                print(f"  [api] Retrying in {wait}s...")
                time.sleep(wait)
            else:
                sys.exit(f"ERROR: {pass_label} failed after {max_retries} attempts: {e}")


# ── Completion check ──────────────────────────────────────────────────────────

def check_completion(combined: str) -> list[str]:
    """
    Return a list of required sections that are missing from the output.
    An empty list means the document is complete.
    """
    return [s for s in REQUIRED_SECTIONS if s not in combined]


# ── Output ────────────────────────────────────────────────────────────────────

def write_output(pass1: str, pass2: str, metrics: dict) -> Path:
    now      = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total    = metrics.get("spike_stats", {}).get("total_posts", "?")
    plat     = metrics.get("platform_stats", {})
    plat_str = ", ".join(f"{p}: {v['count']}" for p, v in plat.items())

    header = f"""<!-- Generated: {now} -->
<!-- Model: gemini/models/gemini-2.5-flash -->
<!-- Source data: {total} classified posts — {plat_str} -->
<!-- Audit trail: data/processed/analysis_metrics.json -->
<!-- Generation: 2-pass (pass1: skeleton+causality, pass2: findings+playbooks) -->

"""
    # Pass 1 contains the front matter. Pass 2 picks up from findings.
    # Insert a clear divider so reviewers can see the join point.
    divider = "\n\n<!-- === PASS 2 START === -->\n\n"
    combined = header + pass1 + divider + pass2

    OUTPUT_MD.write_text(combined, encoding="utf-8")
    return OUTPUT_MD


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate AI playbook analysis from scraped data (2-pass)"
    )
    parser.add_argument("--dry-run",    action="store_true",
                        help="Build both prompts, save them, skip API calls")
    parser.add_argument("--pass1-only", action="store_true",
                        help="Run Pass 1 only; save output for inspection")
    args = parser.parse_args()

    # ── Load .env ──
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    # ── Load and slim metrics ──
    if not METRICS_FILE.exists():
        sys.exit(
            "ERROR: analysis_metrics.json not found — "
            "run compute_playbook_metrics.py first"
        )

    print("  [analysis] Loading metrics...")
    raw_metrics = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
    metrics     = slim_metrics(raw_metrics)
    data_block  = json.dumps(metrics, indent=2, ensure_ascii=False)
    print(f"  [analysis] Data block: {len(data_block):,} chars")

    # ── Build prompts ──
    prompt1 = build_pass1_prompt(data_block)
    print(f"  [analysis] Pass 1 prompt: {len(prompt1):,} chars")

    # ── Dry run ──
    if args.dry_run:
        dry1 = PROCESSED / "prompt_pass1_dry_run.txt"
        dry1.write_text(prompt1, encoding="utf-8")
        print(f"  [dry-run] Pass 1 prompt saved → {dry1}")

        # Build a placeholder pass2 prompt to verify it renders correctly
        placeholder_pass1 = "[Pass 1 output would appear here]"
        prompt2 = build_pass2_prompt(data_block, placeholder_pass1)
        dry2 = PROCESSED / "prompt_pass2_dry_run.txt"
        dry2.write_text(prompt2, encoding="utf-8")
        print(f"  [dry-run] Pass 2 prompt saved → {dry2}")
        print(f"  [dry-run] Pass 2 prompt: {len(prompt2):,} chars")
        return

    # ── Pass 1 ──
    print("\n  [pass1] Generating skeleton + causality analysis...")
    pass1_output = call_gemini(prompt1, "Pass 1")

    # Save pass1 output for inspection / debugging
    pass1_cache = PROCESSED / "pass1_output.txt"
    pass1_cache.write_text(pass1_output, encoding="utf-8")
    print(f"  [pass1] Saved to {pass1_cache.name}")

    if args.pass1_only:
        print(f"\n  [done] Pass 1 complete. Output → {pass1_cache}")
        return

    # ── Pass 2 ──
    print("\n  [pass2] Generating findings + strategic playbooks...")
    prompt2      = build_pass2_prompt(data_block, pass1_output)
    pass2_output = call_gemini(prompt2, "Pass 2")

    # ── Combine and write ──
    out      = write_output(pass1_output, pass2_output, raw_metrics)
    combined = pass1_output + pass2_output

    # ── Completion check ──
    missing = check_completion(combined)
    if missing:
        print(f"\n  [warning] OUTPUT IS INCOMPLETE — missing sections:")
        for s in missing:
            print(f"    ✗ {s}")
        print(
            "  [warning] Consider re-running with --pass1-only to debug, "
            "or check if the model hit a safety filter."
        )
    else:
        print("\n  [check] All required sections present ✓")

    # ── Stats ──
    lines = combined.count("\n")
    nums  = len(re.findall(r"\b\d[\d,.]+\b", combined))
    print(f"  [done] {out.name}  ({lines} lines, {nums} data citations)")


if __name__ == "__main__":
    main()