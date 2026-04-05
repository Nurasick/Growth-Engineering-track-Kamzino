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

    return f"""# Claude Growth Playbook — Generation Prompt v2
## HackNU 2026 · Growth Engineering Track · Part 2

---

## SYSTEM ROLE

You are a senior growth engineer at a competing AI company. You have just received a
competitive intelligence dossier on how Claude (Anthropic's AI assistant) went viral across
Hacker News, Reddit, YouTube, and X/Twitter over 16 months (Jan 2025 – Apr 2026).

Your job: produce `PLAYBOOK_ANALYSIS.md` — a structured growth playbook that a new growth
engineer could pick up on Monday and act on immediately. This is not a research summary.
Every section must end in a concrete action, an owner, and a confidence level.

---

## STEP 1 — DETECT THE PLAYBOOK TYPE FIRST

Before writing a single heading, scan the DATA BLOCK and classify which growth pattern(s)
this dataset primarily represents. The detected type changes which sections get the most
depth and which plays are prioritized.

| Type | Signature | Action emphasis |
|---|---|---|
| **Cascade** | Events spread in waves across platforms in <48h | Timing windows, creator pre-briefing |
| **Community-led** | Organic switching narratives; competitor subs outperform home turf | Seeding channels, framing |
| **Creator-driven** | A handful of individual accounts generate disproportionate reach | Identifying + activating key voices |
| **Event-reactive** | External controversies and competitor moves generate biggest spikes | Monitoring, rapid response protocols |
| **Hybrid** | Multiple patterns contribute significantly | Name dominant + secondary |

State at the very top of the document:
> **Playbook type:** [type] — [one sentence on what this means for the action plan]

---

## STEP 2 — WRITE THE DOCUMENT

### STRICT DATA RULES

1. Every finding MUST cite at least one specific number from the DATA BLOCK. No invented figures.
2. Dataset versions matter: Findings on spike types must note they use the 855-post balanced
   dataset. All other findings use the full ~6,100-post dataset.
3. Each finding must include all five fields: **stat → insight → owner → action → confidence**.
4. Confidence levels: **High** (n > 500, multi-platform), **Medium** (n = 25–500),
   **Directional** (n < 25 or single event — useful signal, not betting money on it).
5. Lead with the number. Explain the implication after.
6. Keep each finding section under 250 words.

---

## STEP 3 — INCLUDE INLINE GRAPHICS

### Why charts fail and how to avoid it

The previous version of this prompt produced broken SVGs. The failures were:
1. **Truncation** — complex charts hit token limits mid-tag, producing invalid SVG.
2. **Wrong proportions** — bar widths were eyeballed, not computed from data.
3. **Dark mode breakage** — hardcoded `fill="#666"` and `fill="#ccc"` are invisible in dark mode.
4. **`<style>` blocks inside SVG** — these conflict with host CSS and render unpredictably.

Follow the rules below exactly. They are not stylistic preferences — they prevent the failures above.

---

### SVG rendering rules (mandatory)

**Rule 1 — No `<style>` blocks inside SVG.**
Use only inline `fill`, `stroke`, `font-size`, `font-family`, `text-anchor`, `dominant-baseline` attributes directly on each element. Never write `<style>.bar {{ fill: red }}</style>` inside SVG.

**Rule 2 — Dark mode safe colors only.**
For text: use `fill="#1a1a1a"` for labels (dark enough on white; readable on light gray).
For muted text/annotations: `fill="#6b7280"`.
For bar fills: use these exact hex values by category:
- Primary data bars: `#E8A000` (amber)
- Highlight/accent bars: `#D85A30` (coral)  
- Muted/low-value bars: `#9ca3af` (gray)
- Negative/warning: `#DC2626` (red)
Do NOT use `currentColor` — it inherits unpredictably in SVG embedded in markdown.
Do NOT use `fill="#ccc"` or `fill="#666"` — invisible in dark mode.

**Rule 3 — Compute bar widths from data, not by eye.**
For horizontal bars: `bar_width = (value / max_value) * MAX_BAR_PX` where MAX_BAR_PX = 320.
Show the calculation as an SVG comment before the rect: `<!-- 88.2/100 * 320 = 282 -->`.
For vertical bars: `bar_height = (value / max_value) * MAX_BAR_PX` where MAX_BAR_PX = 160.

**Rule 4 — Keep charts small enough to complete.**
Each chart must fit in a single SVG. Max viewBox height: 280px. Max viewBox width: 580px.
If a chart requires more than 15 SVG elements (rects + texts combined), simplify it.
No log scales — use linear scales with a note "scale truncated for readability" if needed.
No bubble charts — use horizontal bar charts instead (simpler, fewer coordinate calculations).

**Rule 5 — Validate coordinates before writing.**
For every `<rect>`: verify x + width ≤ viewBox width. Verify y + height ≤ viewBox height.
For every `<text>`: verify the text fits. At 11px, each character is ~6.5px wide.
A 20-character label needs ~130px of horizontal clearance.
Left-side labels with `text-anchor="end"` must have x ≥ 130 (to fit a 20-char label).

**Rule 6 — One chart per finding. No chart exceeds 30 SVG elements total.**
If a chart would require more elements, replace it with a styled HTML table using inline styles.

---

### Exact chart specifications

Write each chart in this exact location in the document: immediately after the finding's
data table and before the "Growth Insight" paragraph.

---

**CHART 1 — Finding 1 — HN Power Law (horizontal bar chart)**

ViewBox: `0 0 580 200`. Left margin for labels: x=0 to x=160. Bar area: x=165 to x=485.

Rows (top to bottom, 30px row height, 8px gap):
```
Row 1: y=20,  label="0–5 pts  (88.2%  · 3,334 posts)", bar_width = 88.2/100*320 = 282px, fill=#9ca3af
Row 2: y=58,  label="6–20 pts  (7.3%  · 276 posts)",   bar_width = 7.3/100*320  = 23px,  fill=#9ca3af
Row 3: y=96,  label="21–100 pts (2.6% · 99 posts)",    bar_width = 2.6/100*320  = 8px,   fill=#9ca3af
Row 4: y=134, label="101–300 pts (1.2% · 45 posts)",   bar_width = 1.2/100*320  = 4px,   fill=#9ca3af
Row 5: y=172, label="300+ pts   (0.7% · 25 posts)",    bar_width = 0.7/100*320  = 2px,   fill=#D85A30
```
After Row 1 bar, add annotation text at x=165+282+6, y=38: `"← volume noise"` fill=#6b7280 font-size=10
After Row 5 bar, add annotation text at x=165+2+6, y=190: `"← Dario 2,920pts · Sonnet 4.6 1,346pts"` fill=#D85A30 font-size=10
Chart title: `<text x="290" y="12" text-anchor="middle" font-size="13" font-weight="bold" fill="#1a1a1a">HN score distribution (n=3,779 posts, 90 days)</text>`

---

**CHART 2 — Finding 2 — 3-Wave Cascade (horizontal timeline)**

ViewBox: `0 0 580 220`. This is a timeline, not a dot plot. Use labeled rows instead of sized circles to avoid coordinate math errors.

Layout: 3 platform rows + time axis at bottom.
- Row heights: HN at y=60, YouTube at y=110, Reddit at y=160. Row label x=0–70, text-anchor=start.
- Time axis: x=80 (T=0h) to x=520 (T=50h). Scale: 1h = (520-80)/50 = 8.8px per hour.
- Axis label row at y=195. Tick marks at T=0, 2, 8, 16, 24, 40, 50h.

Events (compute x = 80 + hours * 8.8):
```
HN:      T+0h    → x=80,  y=60,  label="HN ignition"        fill=#E8A000  rect w=8 h=8
YT:      T+0.1h  → x=81,  y=110, label="M.Berman 162K"      fill=#E8A000  rect w=8 h=8
YT:      T+0.8h  → x=87,  y=110, label="Nate Herk 111K"     fill=#E8A000  rect w=8 h=8  (skip label if crowded)
YT:      T+3h    → x=106, y=110, label="Theo 183K"          fill=#E8A000  rect w=8 h=8
Reddit:  T+12h   → x=186, y=160, label="Reddit 337pts"      fill=#D85A30  rect w=8 h=8
YT:      T+16h   → x=221, y=110, label="Fireship 2.59M ★"   fill=#D85A30  rect w=16 h=16 (larger = bigger event)
YT:      T+39h   → x=423, y=110, label="SAMTIME 131K"       fill=#9ca3af  rect w=8 h=8
YT:      T+41h   → x=441, y=110, label="PT creators 89K"    fill=#9ca3af  rect w=8 h=8
```
Dashed vertical line at x=221 (T+16h): `stroke="#DC2626" stroke-dasharray="4 3" stroke-width="1"` from y=45 to y=175.
Label above it: x=221, y=40, text-anchor=middle, `"peak window closes"` fill=#DC2626 font-size=10.

Wave legend at bottom: three colored squares (8x8) with labels "Wave 1 (0–2h)", "Wave 2 (2–16h)", "Wave 3 (48h+)" at y=210.

---

**CHART 3 — Finding 3 — Spike Types (horizontal bar chart — NOT a bubble chart)**

Do NOT attempt a bubble chart. Use a horizontal bar chart on median engagement.
ViewBox: `0 0 580 220`. Left margin x=0–130. Bar area x=135–455. Right annotation area x=460–570.

Rows (bar_width = median / 914 * 320, capped at 320):
```
Row 1: y=20,  label="Personal    914 med",  bar_width=320, fill=#E8A000,  annotation="best floor → reliable"
Row 2: y=58,  label="Meme        337 med",  bar_width=118, fill=#D85A30,  annotation="high ceiling → lottery"
Row 3: y=96,  label="Comparison   32 med",  bar_width=11,  fill=#9ca3af,  annotation=""
Row 4: y=134, label="Tutorial      5 med",  bar_width=2,   fill=#9ca3af,  annotation="most posts"
Row 5: y=172, label="Breakthrough  4 med",  bar_width=1,   fill=#9ca3af,  annotation="45% of posts, med=4"
```
Chart title: `"Spike type median engagement — which format has the best floor? (n=855 balanced dataset)"`
Note below chart: `"Avg engagement: Meme 588K, Breakthrough 147K, Personal 28K — but median tells the reliable story."`

---

**CHART 4 — Finding 7 — YouTube: Community vs Official (horizontal bar chart)**

ViewBox: `0 0 580 160`. Bar area x=175–495 (max=320px). Scale: 1px = 5,816,231/320 = ~18,176 views.

Rows:
```
Row 1: y=20,  label="All community (85 videos)", bar_width=320,              fill=#E8A000, value_label="5.82M views"
Row 2: y=58,  label="Fireship alone (1 video)",  bar_width=2592415/18176=143, fill=#D85A30, value_label="2.59M views · 13× official"
Row 3: y=96,  label="Anthropic official (1 vid)", bar_width=196616/18176=11,  fill=#9ca3af, value_label="197K views"
```
Annotation after Row 2: draw an arrow or bracket comparing Row 2 to Row 3.
Chart title: `"YouTube reach: community creators vs Anthropic official (2-week window)"`

---

**CHART 5 — Finding 9 — Monthly X Views (vertical bar chart)**

ViewBox: `0 0 580 260`. Bottom axis y=210. Bar area y=30–210 (180px tall). Max value 70.6M.
Scale: 1M views = 180/70.6 = 2.55px per million.

8 bars, each 40px wide, 10px gap. Start x=50.
```
Jan25: x=50,  h=0.8*2.55=2,    fill=#9ca3af, label="Jan 25"
Feb25: x=100, h=9.4*2.55=24,   fill=#9ca3af, label="Feb 25",  top_note="Karpathy vibe coding"
Aug25: x=150, h=31.7*2.55=81,  fill=#E8A000, label="Aug 25",  top_note="Elon Grok threat"
Sep25: x=200, h=57.9*2.55=148, fill=#E8A000, label="Sep 25",  top_note="boltdotnew 56M"
Dec25: x=250, h=12.6*2.55=32,  fill=#9ca3af, label="Dec 25"
Jan26: x=300, h=18.1*2.55=46,  fill=#9ca3af, label="Jan 26"
Mar26: x=350, h=70.6*2.55=180, fill=#D85A30, label="Mar 26",  top_note="Source leak PEAK 70.6M"
Apr26: x=400, h=19.5*2.55=50,  fill=#9ca3af, label="Apr 26"
```
Bar y position: y = 210 - bar_height. (Bar grows upward from y=210.)
Amber bars = months >20M. Coral = peak month. Gray = below 20M.
Top notes: place above each tall bar, rotated or abbreviated to fit. font-size=9.

---

**CHART 6 — Finding 11 — @bcherny vs Official Accounts (horizontal bar chart)**

ViewBox: `0 0 580 160`. Bar area x=175–495 (max=320px). Scale: 44.3M/320 = 138,437 views per px.

Rows:
```
Row 1: y=20,  label="@bcherny (124 tweets)", bar_width=320,               fill=#D85A30, value="44.3M views"
Row 2: y=58,  label="@AnthropicAI (6 tweets)", bar_width=4.0/44.3*320=29, fill=#9ca3af, value="4.0M views"
Row 3: y=96,  label="@claudeai (6 tweets)",   bar_width=3.2/44.3*320=23,  fill=#9ca3af, value="3.2M views"
```
Annotation on Row 1: after bar, add `"= 11× both official accounts combined"` fill=#D85A30 font-size=11.
Chart title: `"X/Twitter reach: one engineer vs official accounts (Jan 2025–Apr 2026)"`

---

## DOCUMENT STRUCTURE

Produce the document in this exact order. Do not reorder sections.

---

```markdown
# Claude's Viral Growth Playbook — Decoded
## HackNU 2026 · Growth Engineering Track · Part 2

> **Playbook type:** [detected type] — [one sentence]
>
> **Data provenance:** All findings derived exclusively from our scraped dataset:
> ~6,100 posts across HN (3,779), Reddit (125 posts + 584 comments), X/Twitter
> (1,668 historical + 384 live + 82 enriched), YouTube (86 videos + 293 comments).
> Coverage: Jan 2025 – Apr 2026 (16 months). No external sources used.
>
> **Dataset note:** Finding 3 uses the 855-post balanced dataset for cross-platform
> spike classification. All other findings use the full dataset.

---

## TL;DR — 10 Rules (read this first)

[10 one-sentence rules. Every rule must:
 - Contain at least one number from the data
 - Name the platform it applies to
 - Name an owner in parentheses: (Growth), (Content), (Comms), (Engineering), (Leadership)
 
Example format:
1. **The power law is the whole game (HN):** 88.2% of posts get ≤5 pts — optimize for the
   top 0.7% that generate all reach, not for volume. (Growth)
]

---

## Prioritized Action Stack

The 5 highest-leverage plays right now, ranked by impact × execution speed.

| # | Play | Why now | Impact | Effort | Owner | Done when |
|---|---|---|---|---|---|---|
| 1 | Brief [creator names] 72h before next launch | Fireship alone = 13x official channel | Very High | Low | Growth | Creators confirm embargo receipt |
| 2 | ... | ... | ... | ... | ... | ... |
...

---

## Launch Day Protocol — The 48h Window

[Hour-by-hour checklist synthesizing the 3-wave cascade, timing data, and platform decay.
Every row must reference a specific finding number.]

| Window | Action | Platform | Owner | From finding |
|---|---|---|---|---|
| T-72h | Brief Fireship, Theo, Matthew Berman, NeetCode with embargo assets | YouTube | Growth | F7 |
| T-0h | Post on HN at 22:00 UTC (6pm ET) — 4x baseline score vs other hours | HN | Content | F4 |
| T+2h | Monitor HN velocity — if >50 pts, trigger Reddit seeding | HN → Reddit | Growth | F2, F8 |
| T+12h | Seed r/ChatGPT (not r/ClaudeAI) with switching-frame post | Reddit | Content | F13 |
| T+16h | Assess whether Fireship/Theo content landed — if not, outreach | YouTube | Growth | F2 |
| T+48h | Meme/satire wave starts — amplify or respond | X, Reddit | Comms | F2 |

---

## Dataset Summary

| Platform | Posts | Coverage | Method |
|---|---|---|---|
| Hacker News | 3,779 | 90 days Jan–Apr 2026 | Algolia API |
| Reddit | 125 posts + 584 comments | Last year, 5 subreddits | Reddit API |
| X / Twitter (historical) | 1,668 tweets | Jan 2025 – Apr 2026 (16 months) | Playwright + fxtwitter enrichment |
| X / Twitter (live) | 384 tweets | Last 48h | Playwright live feed |
| X / Twitter (enriched) | 82 tweets | Known handles, full engagement | fxtwitter API |
| YouTube | 86 videos + 293 comments | Last 2 weeks | YouTube Data API v3 |
| **Total** | **~6,100** | **Jan 2025 – Apr 2026** | Unified schema, deduped, velocity scored |

---

## Finding 1 — The Power Law Is the Whole Game

**Claim:** 88.2% of Claude posts on HN score ≤5 pts. The top 0.7% generate nearly all reach.

[INLINE CHART: HN score distribution bar chart — see chart spec above]

HN median: **2 pts.** HN mean: **19.1 pts.** The mean is 9.5x the median because 25 posts
(0.7%) — the Dario Pentagon statement (2,920 pts), Sonnet 4.6 launch (1,346 pts), and DoW
controversy cluster — pull the average up catastrophically. On X: median tweet views = 1,080;
mean = 180,251 (200x the median), driven by the @boltdotnew "vibe coding goes pro" tweet
(56.1M views) and source code leak posts.

**Growth Insight:** Volume is noise. The 3,334 posts scoring 0–5 pts combined reach
approximately the same audience as the single Dario statement. The question is never "how do
we post more" — it's "what conditions produce a top-0.7% post."

**Owner:** Growth (framing strategy), Content (title/format execution)
**Action:** Audit every planned post against the conditions of the top-25 HN posts before
publishing. If it doesn't have a controversy angle, a switching frame, or a named creator
attached, deprioritize it.
**Confidence:** High (n=3,779 HN posts, 16 months X data)

---

## Finding 2 — The 3-Wave Cascade: You Have 16 Hours

**Claim:** Claude content spreads in 3 waves. The peak impact window closes at hour 16.

[INLINE CHART: cascade timeline — see chart spec above]

The April 1 source code leak is the cleanest natural experiment in the dataset:
- **T+0h:** HN ignition (2 pts initial)
- **T+0.1h (7 min):** Matthew Berman YouTube (162,576 views) — pre-briefed
- **T+3h:** Theo t3.gg YouTube (182,642 views)
- **T+12h:** Reddit ignition (337 pts)
- **T+16h:** Fireship (2,592,415 views) — single largest event in 2-week YouTube window
- **T+39h:** SAMTIME satire wave (131,467 views)
- **T+41h:** International wave — Portuguese creators (89,249 views), Arabic YouTube

**Wave 1 (0–2h):** HN + pre-briefed technical creators.
**Wave 2 (2–16h):** Tutorial content, Reddit joins, peak reach.
**Wave 3 (48h+):** Satire, non-English creators, cultural commentary — no longer actionable
for competitor response.

**Growth Insight:** If creators haven't been briefed before hour 2, you're catching the
third wave. The platform mechanics don't reward late movers — HN gravity kills posts after
24h, and YouTube recommends what's already trending.

**Owner:** Growth (creator relationships), Comms (embargo management)
**Action:** No launch goes live without creator briefing 72h in advance. Fireship, Theo,
Matthew Berman, NeetCode are the four Wave 1 slots. Build and maintain a live contact list.
**Confidence:** Directional (single event — source code leak. Wave structure is consistent
with prior findings but generalization requires more events.)

---

## Finding 3 — Spike Type Volume vs Engagement Are Inverted

**From 855 classified posts (balanced dataset — used here for cross-platform fairness):**

[INLINE CHART: spike type scatter/bubble — see chart spec above]

| Spike Type | % of Posts | Avg Engagement | Median Engagement |
|---|---|---|---|
| Breakthrough | 45% | 146,931 | **4** |
| Tutorial | 26% | 33,796 | 5 |
| Personal | 10% | 28,177 | **914** |
| Meme | 9% | **588,136** | 337 |
| Comparison | 7% | 7,098 | 32 |

Breakthrough posts dominate in volume (45%) but have the lowest median (4). They're
bimodal: mostly ignored, occasionally massive. Meme content (9% of posts) has the highest
avg (588K) but high variance. Personal content has the best median-to-mean ratio — almost
never zero, rarely massive. The breakthrough mean (146K) vs median (4) gap is the starkest
power-law signature in the dataset.

**Growth Insight:** For a competing product, the reliable play is personal content (high
floor, consistent), not breakthrough announcements (low floor, high ceiling, mostly noise).
Meme content is a high-risk high-reward bet — worth investing in only if you have strong
community signal already.

**Owner:** Content (format strategy)
**Action:** Default content calendar: 50% personal/tutorial (reliable reach), 40%
breakthrough (required for launches), 10% meme experiments. Track median, not mean, to
measure content health.
**Confidence:** Medium (n=855 balanced dataset; spike classification is model-assisted)

---

## Finding 4 — Posting Time: 22:00 UTC Is Worth 4x

**HN score by hour UTC (n=3,779):**

| Hour (UTC) | Avg Score | US Time | vs Baseline |
|---|---|---|---|
| 22:00 | **39.7** | 6pm ET | **4.2x** |
| 23:00 | 16.9 | 7pm ET | 1.8x |
| 19:00 | 14.0 | 3pm ET | 1.5x |
| 01:00 | 16.2 | 9pm ET (prior night) | 1.7x |
| 04:00–10:00 | 1.6–5.7 | Night/morning ET | 0.2–0.6x |

**Reddit best days:** Sunday (avg score 4,344 — 2.7x Thursday baseline), Saturday (3,549 —
2.2x). Thursday is worst (1,625 baseline).

**Growth Insight:** HN at 22:00 UTC is the single highest-leverage scheduling optimization
in the dataset. West Coast engineers finish work, East Coast is post-dinner — the front page
is maximally contested. Reddit weekend posts survive longer before falling off the active
feed. These two facts should be baked into a calendar, not decided ad hoc.

**Owner:** Content (scheduling), Engineering (if posts are automated)
**Action:** All HN submissions at 22:00 UTC ±30min. All Reddit seeding on Saturday or
Sunday. Block these windows in the content calendar as non-negotiable.
**Confidence:** High (n=3,779 HN; Reddit n=125 — directional on Reddit)

---

## Finding 5 — Title Language: 15–36x Lift From the Right Words

**Word lift — top-20% HN posts vs baseline (min 15 occurrences):**

| Word | Lift | Avg Score | n | Why it works |
|---|---|---|---|---|
| "department" | **36x** | 344.8 | 15 | Pentagon/DoW controversy cluster |
| "war" | 25.6x | 244.4 | 26 | Dept of War framing |
| "supply" / "chain" | 15–16x | 144–151 | 22–23 | Supply chain risk designation |
| "leaked" / "leaks" | ~22x | — | — | Scandal framing |
| "chatgpt" | ~15x | — | — | Switching/comparison frame |
| "safety" | 6.7x | 64.2 | 21 | Ethics/values frame |

**Words that kill reach:**
"generated" (0.29x), "local" (0.22x), "powered" (0.25x), "server" (0.24x) — generic AI/LLM
terms that signal commodity posts. HN readers pattern-match these as noise.

**Growth Insight:** Lead with stakes, not features. "Leaked" and "ChatGPT" appear in titles
of posts that HN engineers feel are worth sharing. "Generated" and "powered" appear in
titles of posts nobody shares. The formula: [controversy/scandal/comparison frame] + [named
entity] + [stakes sentence].

**Owner:** Content (copywriting), Growth (title review before any HN post)
**Action:** All HN titles must pass a word-lift review. Maintain a 20-word approved list
(high-lift) and a 20-word blocked list (low-lift) pinned in your content Notion/Linear.
**Confidence:** High (n=3,779; lift calculated from full 90-day HN dataset)

---

## Finding 6 — The Pentagon Saga: 6 Weeks of Free Growth

**Claim:** The Anthropic–Pentagon conflict (Feb 13 – Mar 26, 2026) was the single largest
sustained organic growth event in the dataset — worth more than any paid campaign.

| Date | HN Score | Comments | Event |
|---|---|---|---|
| Feb 13 | 25 | 5 | Pentagon Used Claude in Venezuela Raid |
| Feb 26 | **2,920** | **1,580** | Dario: "Cannot in good conscience accede" |
| Feb 27 | 1,362 | 1,085 | DOW Designates Anthropic Supply-Chain Risk |
| Feb 28 | 1,170 | 357 | Hegseth Statement |
| Feb 28 | 42 | — | **Claude rises to #2 in App Store** |
| Mar 01 | 138 | — | **Claude #1 US App Store — dethrones ChatGPT** |
| Mar 04 | 805 | 425 | Dario calls OpenAI military stance "straight up lie" |
| Mar 06 | 630 | 788 | Most controversial post (comments > points ratio) |
| Mar 26 | 446 | 233 | Judge Blocks Pentagon Effort |

Pentagon cluster avg: **51.9 pts** vs 6.5 baseline (**8.0x lift**). Comments per post:
27.3 vs 3.9 (**7.0x**). This is the highest-lift topic cluster in the entire dataset.

**Growth Insight:** Controversy that aligns with your audience's values is
indistinguishable from organic growth. Anthropic's customers (developers) are already
skeptical of military AI. The Pentagon conflict didn't hurt Claude — it generated its
biggest App Store moment. For a competing product: identify one values-aligned controversy
your audience already cares about. Don't manufacture it. Position into it authentically.

**Owner:** Leadership (positioning), Comms (narrative response), Growth (monitoring)
**Action:** Monitor regulatory and ethical AI news for controversy opportunities that align
with your product's values positioning. Build a response playbook now, before a crisis.
**Confidence:** High (n=9 major events, 6 weeks, App Store ranking documented)

---

## Finding 7 — Community YouTube = 29x Official. Fireship Alone = 13x.

**YouTube data (86 videos, 2-week window):**

[INLINE CHART: community vs official YouTube bar chart — see chart spec above]

| | Videos | Total Views | Avg/Video |
|---|---|---|---|
| Anthropic official | 1 | 196,616 | 196,616 |
| All community creators | 85 | 5,816,231 | 68,426 |
| **Ratio** | — | **29x** | — |

**Top channels on the source code leak:**

| Channel | Views | Relationship to Anthropic |
|---|---|---|
| Fireship | 2,592,415 | Organic — not briefed |
| Theo (t3.gg) | 182,642 | Organic |
| Matthew Berman | 162,576 | Organic |
| NeetCode | 151,715 | Tutorial — organic |
| Anthropic official | 196,616 | Official |

Fireship was **not pre-briefed** for the leak — he reacted organically. His single video
beat Anthropic's entire YouTube presence by 13x on the same event.

**On X: official and community are roughly equal per tweet.** @AnthropicAI: 44 tweets,
62.4M total views (1.42M avg). Community: 38 tweets, 48.4M total views (1.27M avg).
Platform-specific strategy applies: YouTube → brief creators, skip own channel. X →
maintain official account, it punches at community weight.

**Growth Insight:** YouTube is a creator-distribution problem, not a channel-building
problem. A competing product should spend zero budget on its own YouTube channel and
100% of YouTube budget on creator relationships.

**Owner:** Growth (creator relationships)
**Action:** Identify your product's equivalent of Fireship, Theo, Matthew Berman, NeetCode.
Build relationships before you need them. Create an easy brief template (2-page PDF max)
for rapid creator activation.
**Confidence:** High (n=86 videos, 2-week window; channel attribution verified)

---

## Finding 8 — Engagement Decay: You Have 24h on HN, 6 Days on YouTube

| Platform | Day 0 velocity | Day 1 | Day 3 | Day 6 |
|---|---|---|---|---|
| HN | 0.033 | ~0 | 0.001 | 0.001 |
| Reddit | 0.240 | 0.027 | 0.008 | ~0 |
| YouTube | 0.055 | 0.024 | 0.010 | 0.004 |

HN uses a gravity formula that kills posts after ~24h. Reddit weekend posts survive into
Monday. YouTube retains meaningful velocity for 6+ days — tutorials gain views long after
publish. This has direct scheduling implications: HN requires same-day response. YouTube
gives a week to act. Reddit can be planned ahead for weekend drops.

**Growth Insight:** Cross-posting the same content simultaneously to all platforms is
suboptimal. Sequence by decay: publish to HN at 22:00 UTC, let it peak, seed Reddit on the
following weekend, let YouTube creators pick it up organically — or brief them to hit 7–10
days after HN when the YouTube recommendation engine is still warm.

**Owner:** Content (scheduling), Growth (platform sequencing)
**Action:** Build a platform sequencing SOP: HN (T+0) → X (T+0, parallel) → Reddit
(T+weekend) → YouTube outreach (T+3 days). Never release all platforms simultaneously.
**Confidence:** High (velocity data from full dataset, all platforms)

---

## Finding 9 — Competitor Attacks Drive 3x More Views Than Own Launches

**Monthly X views (Jan 2025 – Apr 2026):**

[INLINE CHART: monthly X views bar chart — see chart spec above]

| Month | Total Views | Key Driver |
|---|---|---|
| Feb 2025 | 9.4M | @karpathy "vibe coding" origin (6.9M) |
| Aug 2025 | 31.7M | @elonmusk Grok Code threat ×2 (27.3M combined) |
| Sep 2025 | **57.9M** | @boltdotnew "vibe coding goes pro" (56.1M) |
| Dec 2025 | 12.6M | @bcherny Claude Code origin story (4.6M) |
| Jan 2026 | 18.1M | @bcherny tips thread (9.1M) |
| Mar 2026 | **70.6M** | Source code leak cascade (34.8M) + community |
| Apr 2026 | 19.5M | Leak aftermath + official response |

The two @elonmusk Grok Code threat tweets alone = **27.3M views combined** — 3x more than
the biggest official Claude announcements. Claude's two biggest X months (Sep 2025: 57.9M,
Mar 2026: 70.6M) were both external events — not Claude product launches.

**Growth Insight:** Competitor attacks trigger tribal defense from your user base. Developers
who use Claude don't just watch — they retweet to argue, debunk, and reassure. For a
competing product: monitor competitor moves as closely as your own launch calendar. A well-
timed response to a competitor announcement can outperform your own launch content.

**Owner:** Growth (competitive monitoring), Comms (response playbook)
**Action:** Set up real-time alerts for competitor major announcements (Grok, GPT, Gemini).
Pre-write 3 response post templates: defensive, comparative, humor. Have approval chain
ready to publish within 2h of a competitor spike.
**Confidence:** High (1,668 tweets, 16 months; monthly attribution verified)

---

## Finding 10 — "Vibe Coding" and the Naming-the-Movement Effect

**Claim:** A single external creator coining a phrase for a behavior tied to your product
creates a category that nobody can take away.

| Date | Event | Views |
|---|---|---|
| Feb 2, 2025 | @karpathy: "There's a new kind of coding I call 'vibe coding'..." | 6.9M |
| Feb 2025 → Apr 2026 | "Vibe coding" dominates Claude Code framing | 346 tweets in dataset |
| Sep 30, 2025 | @boltdotnew: "Today vibe coding goes pro..." (uses Claude) | **56.1M** — highest tweet in dataset |
| Dec 2025 | @karpathy builds smart home with Claude Code | 3.0M |

**Content type total views and median:**

| Content Type | Tweets | Total Views | Median Views |
|---|---|---|---|
| Vibe-coding | 346 | 74.0M | 1,444 |
| Scandal/leak | 21 | 50.7M | **353,005** |
| Competitor framing | 720 | 46.8M | 381 |
| Personal demo | 63 | 27.5M | 2,231 |
| Tutorial | 61 | 8.2M | 4,382 |
| Launch/announcement | 26 | 7.6M | 4,642 |
| Meme | 31 | 1.4M | 1,942 |

Critical: competitor framing has the **most posts (720)** but **second-lowest median (381)**.
The category is almost entirely inflated by @elonmusk's two posts (27.3M combined). Without
those, competitor framing is the worst category. Scandal has a **353K median** — meaning
the average scandal post gets 353K views. The floor is high, not just the ceiling.

**Growth Insight:** Naming a movement is the highest-leverage external creator play. It's
not a tweet — it's a category. For a competing product: identify the behavior your users
already do that nobody has named yet. Facilitate the coinage; don't manufacture it.

**Owner:** Growth (creator seeding), Leadership (naming workshop)
**Action:** Run a naming workshop with your top 3 external advocates. Surface 2–3 behavior
names. Seed the best one organically with one high-credibility creator (Karpathy-equivalent).
Don't announce it — let it emerge.
**Confidence:** Medium (single naming event; generalization is behavioral, not statistical)

---

## Finding 11 — One Inside Engineer = 11x Official Account

[INLINE CHART: inside engineer vs official X bar chart — see chart spec above]

| Account | Type | Tweets | Total Views | Avg/Tweet |
|---|---|---|---|---|
| @bcherny | Claude Code creator | 124 | **44.3M** | 357,244 |
| @AnthropicAI | Official | 6* | 4.0M | 668,069 |
| @claudeai | Official product | 6* | 3.2M | 538,360 |

*Captured in dataset window. @bcherny's 124 tweets = 11x more total reach than both official
accounts combined. His top posts:

| Tweet type | Views |
|---|---|
| Tips thread: "I'm Boris and I created Claude Code..." | 9.1M |
| Origin story: "When I created Claude Code as a side project..." | 4.6M |
| Hidden features: "a bunch of my favorite under-utilized features..." | 3.8M |
| Feature announce: "In the next version of Claude Code..." | 2.5M |
| Relatable meme: "I feel this way most weeks tbh" | 1.76M |

This is sustained 2–9M view performance across 5 different post types — tips, origin story,
feature announcements, inside jokes. Not a single outlier.

**Why it works:** "I built this" is more credible than "we built this." No PR review = human
voice, typos, opinions — all of which the developer audience trusts. First-person inside
knowledge (tips, hidden features) signals access the community doesn't have.

**Growth Insight:** Finding and empowering one credible internal engineer to post with full
creative autonomy is the highest-leverage X play. Not the official handle. Not sponsored
content. One authentic voice with zero constraints.

**Owner:** Leadership (identify + empower), Growth (amplify)
**Action:** Identify your @bcherny equivalent — the engineer who built the core product and
can speak with authority. Give them a mandate: post freely, no approval required, we amplify
whatever you make. Measure by total views/month, not follower count.
**Confidence:** High (124 tweets over 16 months; pattern consistent across post types)

---

## Finding 12 — Small Accounts Can Go 415x: Follower Count Is Not the Constraint

**Top views-per-follower ratios in X dataset:**

| Account | Followers | Views | Ratio |
|---|---|---|---|
| @MangoLassC | 6,861 | 2,852,739 | **415x** |
| @iamfakeguru | 7,665 | 1,614,824 | 211x |
| @cgtwts | 19,958 | 2,246,056 | 112x |
| @altryne | 40,218 | 1,990,893 | 50x |
| @0xluffy | 23,181 | 927,696 | 40x |

**X follower bucket vs median views:**

| Followers | n | Median Views | Mean Views |
|---|---|---|---|
| <10K | 132 | 2,260 | 47,368 |
| 10K–100K | 375 | 4,816 | 190,113 |
| 100K–1M | 307 | 31,768 | 392,674 |
| 1M+ | 23 | 270,294 | 1,973,918 |

The outlier-to-median ratio is highest in the <10K bucket. When small accounts go viral
about Claude, they go more disproportionately viral than large accounts do. @MangoLassC's
"just switched from chatgpt to claude and oh my God" (6.8K followers, 2.85M views) hit
because message resonated with the moment (post-leak, post-Pentagon), not account reach.

**Growth Insight:** The platform distributes based on engagement velocity in the first hour,
not follower count. Seed the narrative; the algorithm does the amplification. Your job is to
create the conditions — timing, message resonance, cultural moment — not the audience.

**Owner:** Growth (narrative seeding), Content (message framing)
**Action:** Stop filtering community posts by follower count. Monitor engagement velocity
(views/hour in first 60 min) instead. A 5K-follower account at 10K views/hour needs
immediate amplification — engage, retweet, reply.
**Confidence:** High (1,668 tweets; follower data from fxtwitter enrichment)

---

## Finding 13 — Seed in the Competitor's House First

| Subreddit | n | Median Score | Mean Score | Max |
|---|---|---|---|---|
| r/ChatGPT | 25 | 2,300 | **5,770** | **29,926** |
| r/ClaudeAI | 25 | 4,056 | 4,593 | 8,143 |
| r/LocalLLaMA | 25 | 1,050 | 1,471 | 4,824 |
| r/artificial | 25 | 285 | 301 | 803 |
| r/MachineLearning | 25 | 62 | 94 | 235 |

r/ChatGPT has a higher mean score (5,770 vs 4,593) for Claude-related posts than r/ClaudeAI.
Top post: "Cancel your ChatGPT Plus, burn their compute on the way out, and switch to
Claude" — **29,926 upvotes.** r/ClaudeAI readers are already converted. r/ChatGPT readers
have purchase intent and are open to switching.

**Growth Insight:** For any competing product: don't build your own subreddit first. Seed
in the competitor's community, where the audience already has purchase intent and the
switching frame lands as discovery, not preaching.

**Owner:** Content (Reddit seeding), Growth (subreddit strategy)
**Action:** For next launch: r/ChatGPT and r/LocalLLaMA before r/your-own-subreddit.
Use a switching frame ("I tried X, here's what happened") not a feature announcement frame.
**Confidence:** Directional (n=25 per subreddit — directional, not statistically definitive)

---

## Finding 14 — The Competitor Switching Narrative Is the Most Durable Growth Engine

**From cascade_detector.py — 48 narrative clusters across 11,454 posts, 16 months:**

| Narrative | Posts | Platforms | Peak Engagement | First seen |
|---|---|---|---|---|
| "Why I Switched From ChatGPT to Claude" | **333** | **4/4** | 170,513 | Feb 2026 |
| Source code leak | 914 | 4/4 | 2,592,415 | Apr 2026 |
| "AI News: Anthropic Leak is Bigger Than You Think" | 245 | 4/4 | 55,639 | Apr 2026 |
| "the end of Claude Code" (attack narrative) | 23 | 3/4 | 85,756 | Mar 2026 |

The switching narrative: 333 posts, all 4 platforms, running since Feb 2026 — **not seeded
by Anthropic.** It started organically on HN, moved to r/ChatGPT, reached X, then YouTube
(across 8 weeks). Cascade spread: HN → Reddit (+188h) → X (+98h) → YouTube (+675h).

This is more sustained engagement than any single Anthropic announcement outside the source
code leak. The attack narrative ("end of Claude Code") also cascades — 23 posts, 3
platforms, 85K peak — meaning competitor attack narratives must be monitored early.

**Growth Insight:** The switching narrative doesn't need to be manufactured. For a competing
product: the equivalent is getting users to post "I switched from [competitor] to [you]" in
competitor communities. The cascade detector tells you when that narrative is starting —
watch for it, amplify it the moment it ignites.

**Owner:** Growth (narrative monitoring), Content (amplification)
**Action:** Build a saved search for "[competitor name] → [your product]" switching posts
across HN, Reddit, X, YouTube. When one gets >50 upvotes, engage immediately: like, retweet,
reply with genuine thanks. Velocity in the first hour determines whether it cascades.
**Confidence:** High (cascade_detector.py across 11,454 posts; 16-month dataset)

---

## Limitations

| # | Limitation | Findings affected | Severity |
|---|---|---|---|
| 1 | X historical data is Top-mode biased — low-engagement posts underrepresented | F9, F10, F12 | Medium |
| 2 | YouTube window is 2 weeks only (free API tier) — historical YouTube missing | F7, F2 | Medium |
| 3 | HN timing spike at 22:00 UTC is partially confounded by Pentagon posts (US evening) | F4 | Low |
| 4 | Reddit n=25 per subreddit — directional, not statistically definitive | F13 | High |
| 5 | Cascade timing based on one event (source code leak) — generalization requires more events | F2 | Medium |
| 6 | Instagram, LinkedIn, TikTok not scraped — significant blind spot for creator discovery | All | Medium |
| 7 | Spike type classification is model-assisted — human review not done at scale | F3 | Medium |

---

## Summary: Claude's Growth Playbook in 10 Rules

1. **The power law is the whole game (HN, X):** 88.2% of posts score ≤5 pts —
   optimize for the top 0.7% conditions, not volume. (Growth)
2. **The 16-hour window is not negotiable (all platforms):** Brief Fireship, Theo,
   Matthew Berman, NeetCode 72h before any launch — or you're catching the third wave.
   (Growth)
3. **Post HN at 22:00 UTC (HN):** 39.7 avg pts vs 9.5 baseline — 4x lift from
   timing alone. (Content)
4. **Lead with stakes, not features (HN):** "leaked" (22x lift) and "chatgpt" (15x
   lift) outperform any feature description word in the dataset. (Content)
5. **Controversy that aligns with values = free growth (all platforms):** The Pentagon
   saga drove Claude to #1 App Store without a dollar of paid media. (Leadership, Comms)
6. **One inside engineer beats the official account 11x (X):** @bcherny's 124 tweets
   = 44.3M views vs official accounts combined 7.2M — give your builder a mandate.
   (Leadership)
7. **Community YouTube is 29x official (YouTube):** Don't build a channel; build
   creator relationships. Fireship alone = 13x Anthropic's output on the same event.
   (Growth)
8. **Seed in the competitor's subreddit first (Reddit):** r/ChatGPT mean score 5,770
   vs r/ClaudeAI 4,593 — the audience with purchase intent is already there. (Content)
9. **The switching narrative runs itself (all platforms):** 333 posts, 4 platforms,
   running since Feb 2026 — not seeded by Anthropic. Monitor for it; amplify it. (Growth)
10. **Follower count is not the constraint (X):** @MangoLassC (6.8K followers) got
    2.85M views (415x ratio) — monitor engagement velocity in the first hour. (Growth)
```

---

## DATA BLOCK

Paste the full scraped data JSON or structured output here. The model will use these
numbers exclusively — no hallucinated figures.

```
=== SCRAPED DATA (use these numbers only) ===
{data_block}
=== END DATA ===
```

---

## FINAL CHECKLIST (model self-review before output)

**SVG anti-failure checks (check these first — they caused all failures in v1):**
- [ ] No `<style>` blocks inside any SVG element
- [ ] No `fill="#ccc"`, `fill="#666"`, `fill="gray"`, or `fill="currentColor"` anywhere
- [ ] Every bar width was computed with the formula shown in the chart spec (show the comment)
- [ ] Every SVG is complete — ends with `</svg>`. No truncated tags.
- [ ] No chart requires more than 30 SVG elements total
- [ ] No bubble charts, scatter plots, or log-scale axes — only horizontal/vertical bar charts and the cascade timeline
- [ ] Every `<text>` has explicit `fill`, `font-size`, and `text-anchor` attributes

**Document structure checks:**
- [ ] Playbook type declared at the top with one-sentence implication
- [ ] TL;DR 10 rules are at the TOP, not the bottom
- [ ] Every rule contains a number and names an owner
- [ ] Action stack table is present with 5 rows
- [ ] Launch Day Protocol has hour-by-hour rows
- [ ] All 6 required inline charts are present (no `data/charts/*.png` references)
- [ ] Every finding has: stat, insight, owner, action, confidence
- [ ] Limitations table is present with severity column
- [ ] No figures appear that are not in the DATA BLOCK"""


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
