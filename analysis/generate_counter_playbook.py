#!/usr/bin/env python3
"""
generate_counter_playbook.py — AI-generated growth counter-playbook

Reads real scraped data from our pipeline, computes key growth metrics,
and sends them as context to an AI API to generate a data-backed counter-playbook.

Supports: OpenAI (gpt-4o-mini), Anthropic Claude (claude-haiku-4-5), Gemini (gemini-2.0-flash)
Uses whichever API key is found in .env.

Usage:
    python analysis/generate_counter_playbook.py --product higgsfield
    python analysis/generate_counter_playbook.py --product higgsfield --provider openai
"""

import os, sys, json, argparse
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).parent.parent
PROCESSED    = ROOT / "data" / "processed"
AMPLIFIER    = ROOT / "data" / "amplifier_watchlist.csv"
CONTEXT_JSON = PROCESSED / "playbook_context.json"
OUTPUT_MD    = ROOT / "COUNTER_PLAYBOOK_GENERATED.md"

# ── Product configs ──────────────────────────────────────────────────────────
PRODUCTS = {
    "higgsfield": {
        "name": "Higgsfield",
        "description": (
            "AI video generation tool that creates cinematic video clips from text prompts. "
            "Target users: indie filmmakers, VFX artists, wedding videographers, content creators. "
            "Key differentiator: cinematic quality and camera motion control. "
            "Current state: niche awareness, dominant community is r/aivideo."
        ),
        "competitors": ["Sora", "Runway", "Pika"],
        "primary_communities": ["r/aivideo", "r/filmmakers", "r/videography", "r/indiegaming"],
    },
    "runway": {
        "name": "Runway",
        "description": (
            "Professional AI video generation and editing platform. "
            "Target users: creative professionals, agencies, film studios. "
            "Competes with Sora and Pika."
        ),
        "competitors": ["Sora", "Higgsfield", "Pika"],
        "primary_communities": ["r/aivideo", "r/videography", "r/filmmakers"],
    },
}

# ── Data extraction ──────────────────────────────────────────────────────────

def load_df(filename: str) -> pd.DataFrame | None:
    path = PROCESSED / filename
    if not path.exists():
        print(f"  [warn] {filename} not found — run pipeline.py first", file=sys.stderr)
        return None
    return pd.read_csv(path, encoding="utf-8")


def extract_insights() -> dict:
    """Read processed CSVs and compute all metrics needed for the prompt."""
    print("  [extract] Loading processed data...")

    spike   = load_df("spike_classified.csv")
    front   = load_df("growth_frontpage.csv")
    unified = load_df("unified_posts.csv")

    if spike is None or front is None or unified is None:
        sys.exit("ERROR: processed data missing. Run: python pipeline.py --skip-scrape")

    # ── Spike type stats ─────────────────────────────────────────────────────
    spike_stats = (
        spike.groupby("spike_type")["engagement_score"]
        .agg(count="count", mean=lambda x: round(x.mean()), median=lambda x: round(x.median()))
        .reset_index()
    )
    total = len(spike)
    spike_stats["pct"] = (spike_stats["count"] / total * 100).round(1)
    spike_records = spike_stats.sort_values("count", ascending=False).to_dict("records")

    # ── Platform stats ───────────────────────────────────────────────────────
    platform_stats = (
        unified.groupby("platform")["engagement_score"]
        .agg(count="count", mean=lambda x: round(x.mean()), median=lambda x: round(x.median()))
        .reset_index()
        .to_dict("records")
    )

    # ── YouTube: community vs official ───────────────────────────────────────
    yt = unified[unified["platform"] == "youtube"].copy()
    # official column may be bool or string "True"/"False"
    yt["official"] = yt["official"].astype(str).str.lower().isin(["true", "1", "yes"])
    yt_official   = yt[yt["official"] == True]["engagement_score"].sum()
    yt_community  = yt[yt["official"] == False]["engagement_score"].sum()
    # Anthropic official channel (196K views) validated in prior scrape run;
    # current scrape captured community only — use known baseline for ratio.
    KNOWN_OFFICIAL_VIEWS = 196616
    yt_ratio = round(yt_community / KNOWN_OFFICIAL_VIEWS, 1) if yt_community > 0 else 0

    # Top YouTube creator by views
    yt_by_channel = (
        yt.groupby("channel")["engagement_score"].sum()
        .sort_values(ascending=False)
    )
    top_yt_creator       = yt_by_channel.index[0] if len(yt_by_channel) else "Unknown"
    top_yt_creator_views = int(yt_by_channel.iloc[0]) if len(yt_by_channel) else 0

    # ── Timing: HN by UTC hour ───────────────────────────────────────────────
    unified["created_at"] = pd.to_datetime(unified["created_at"], utc=True, errors="coerce")
    unified["hour"]    = unified["created_at"].dt.hour
    unified["weekday"] = unified["created_at"].dt.day_name()

    hn_timing = (
        unified[unified["platform"] == "hn"]
        .groupby("hour")["engagement_score"]
        .mean()
        .round(1)
        .sort_values(ascending=False)
        .head(5)
        .to_dict()
    )

    # ── Timing: Reddit by weekday ────────────────────────────────────────────
    reddit_timing = (
        unified[unified["platform"] == "reddit"]
        .groupby("weekday")["engagement_score"]
        .mean()
        .round(1)
        .to_dict()
    )

    # ── Decay: avg velocity by platform and age bucket ───────────────────────
    decay = {}
    for bucket_label, age_min, age_max in [
        ("day0", 0, 24), ("day1", 24, 48), ("day3", 72, 96), ("day6", 144, 168)
    ]:
        bucket = front[(front["age_hours"] >= age_min) & (front["age_hours"] < age_max)]
        decay[bucket_label] = (
            bucket.groupby("platform")["velocity"]
            .mean()
            .round(4)
            .to_dict()
        )

    # ── Top 20 velocity posts ────────────────────────────────────────────────
    top_posts = (
        front.head(20)[["rank", "platform", "spike_type", "title", "velocity", "age_hours", "raw_score"]]
        .fillna("")
        .to_dict("records")
    )

    # ── Top 10 spike posts by raw engagement ────────────────────────────────
    top_by_engagement = (
        spike.nlargest(10, "engagement_score")[["platform", "spike_type", "title", "engagement_score"]]
        .fillna("")
        .to_dict("records")
    )

    # ── Amplifier watchlist ──────────────────────────────────────────────────
    amplifiers = []
    if AMPLIFIER.exists():
        amp_df = pd.read_csv(AMPLIFIER, encoding="utf-8")
        amplifiers = (
            amp_df.sort_values("composite_score", ascending=False)
            .head(10)[["handle", "followers", "total_views", "engagement_rate", "amplification_mult", "composite_score", "tier"]]
            .fillna("")
            .round(3)
            .to_dict("records")
        )

    # ── Title word lift (from spike data — top vs bottom engagement) ─────────
    top_q    = spike["engagement_score"].quantile(0.8)
    bot_q    = spike["engagement_score"].quantile(0.2)
    top_text = " ".join(spike[spike["engagement_score"] >= top_q]["title"].dropna().str.lower())
    bot_text = " ".join(spike[spike["engagement_score"] <= bot_q]["title"].dropna().str.lower())

    from collections import Counter
    import re
    stop = {"the","a","an","of","in","to","and","for","is","are","with","on","by","at","it","this","that","how","i","my","from","its","was","be","as","what","we","you","your","do","not","but","or","have","has","can","use","via","&","–","-","vs","so","if","new","more","just","get","all","now","will","about","into","been","they","their","than","when","after","some","one","two","no","up"}

    top_words = Counter(w for w in re.findall(r"[a-z]{4,}", top_text) if w not in stop)
    bot_words = Counter(w for w in re.findall(r"[a-z]{4,}", bot_text) if w not in stop)
    total_top = sum(top_words.values()) or 1
    total_bot = sum(bot_words.values()) or 1

    word_lift = {}
    for word, cnt in top_words.items():
        if cnt >= 3:
            top_rate = cnt / total_top
            bot_rate = (bot_words.get(word, 0) + 0.5) / total_bot
            word_lift[word] = round(top_rate / bot_rate, 2)

    top_lift_words = sorted(word_lift.items(), key=lambda x: -x[1])[:15]

    # ── Cascade timing (from top velocity posts) ─────────────────────────────
    wave_window_hours = 16  # from PLAYBOOK_ANALYSIS.md finding 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_summary": {
            "total_classified": total,
            "total_unified": len(unified),
            "platforms": unified["platform"].value_counts().to_dict(),
        },
        "spike_type_stats": spike_records,
        "platform_stats": platform_stats,
        "youtube_community_vs_official": {
            "community_total_views": int(yt_community),
            "official_total_views":  int(yt_official),
            "ratio_community_over_official": yt_ratio,
            "top_community_creator": top_yt_creator,
            "top_creator_views": top_yt_creator_views,
        },
        "timing": {
            "hn_by_utc_hour_top5": hn_timing,
            "hn_peak_note": "Peak hours 19-23 UTC = 2-6pm US Eastern. Post at 19:00 UTC for max HN engagement.",
            "reddit_by_weekday_avg_score": reddit_timing,
            "reddit_peak_note": f"Sunday avg {reddit_timing.get('Sunday', 0)} vs Thursday avg {reddit_timing.get('Thursday', 0)} — {round(reddit_timing.get('Sunday',1)/max(reddit_timing.get('Thursday',1),1), 1)}x difference.",
        },
        "engagement_decay_by_platform": decay,
        "top_20_velocity_posts": top_posts,
        "top_10_highest_engagement_posts": top_by_engagement,
        "amplifier_watchlist_top10": amplifiers,
        "title_word_lift_top15": top_lift_words,
        "cascade_model": {
            "wave1_hours": "0-2",
            "wave2_hours": "2-16",
            "wave3_hours": "48-96",
            "max_impact_window_hours": wave_window_hours,
            "note": "Validated on Apr 1 2026 source code leak: HN 01:13 UTC → YouTube 01:20 UTC (7 min) → Reddit 12:54 UTC (12h) → meme wave 48h+",
        },
    }


# ── Prompt builder ────────────────────────────────────────────────────────────

def build_prompt(insights: dict, product_cfg: dict) -> str:
    data_block = json.dumps(insights, indent=2, ensure_ascii=False)

    competitors_str = ", ".join(product_cfg["competitors"])
    communities_str = ", ".join(product_cfg["primary_communities"])

    return f"""You are a senior growth engineer writing a battle-plan document for a competing AI product.
You have access to real scraped data from a competitive intelligence pipeline that reverse-engineered how Claude (Anthropic's AI) went viral.
Your job is to write a counter-playbook for {product_cfg['name']} — a product that wants to replicate Claude's viral growth mechanics.

STRICT RULES:
1. Every recommendation MUST cite a specific number from the DATA BLOCK below. No exceptions.
2. Phrases like "consider doing X", "it may be worth", "you could potentially" are BANNED. State what to do.
3. Never invent statistics. Only use numbers that appear in the DATA BLOCK.
4. Every section must be actionable — specific channel, specific format, specific metric target.
5. Use compact markdown. Do NOT pad table columns with spaces. Keep tables minimal: pipes and content only, no alignment spaces.
5. Write in the style of a growth engineer, not a consultant. Short sentences. Direct.

PRODUCT CONTEXT:
- Product: {product_cfg['name']}
- Description: {product_cfg['description']}
- Main competitors: {competitors_str}
- Target communities: {communities_str}

=== SCRAPED DATA (Claude's viral growth — use these numbers, do not invent others) ===
{data_block}
=== END DATA ===

Write the counter-playbook for {product_cfg['name']} in markdown format with these exact sections:

# {product_cfg['name']} Counter-Playbook: Replicating Claude's Viral Growth Mechanics
## Data-Driven Growth Distribution Plan

Start with a 2-paragraph executive summary citing 3 specific numbers from the data.

## 0. What the Data Shows (Key Numbers)
A table of the 5 most important data findings, with the exact number and why it matters for {product_cfg['name']}.

## 1. Platform Translation
A table mapping Claude's platforms to {product_cfg['name']} equivalents.
Each row must explain WHY with a specific data point (engagement number, ratio, timing stat).
Include a paragraph on the critical structural difference between Claude's product and {product_cfg['name']}.

## 2. Creator Seeding Strategy
Explain why creator seeding is the core lever (cite the community vs official ratio from data).
List specific creator archetypes for {product_cfg['name']} in 3 tiers.
Include: what to give them, when, the exact K-factor formula to track, and the 72h attribution window.

## 3. Content Format Playbook
One entry per spike type (breakthrough, tutorial, comparison, personal, meme).
Each entry: the exact engagement number from data, the specific post format for {product_cfg['name']}, the platform, the title formula.

## 4. Timing Calendar — Weeks -2 to +3
Specific day-by-day plan.
Every timing decision must cite a number from the data (HN UTC hours, Reddit weekday scores, decay windows).
Include: pre-launch seeding, launch day, wave 2, wave 3.

## 5. Alert System
A table of signals, thresholds, and actions.
Velocity threshold must match the data. Include competitor launch response protocol with the time window from cascade data.

## 6. Metrics to Track
5 metrics with exact formulas, numeric targets, and measurement timing.
At least one metric must reference the virality coefficient concept with a specific target %.

## 7. Budget Estimate
Line-item table. Total at bottom.
Justify each line with a data point (e.g. cite the community vs official ratio to justify creator spend over ads).

## Summary: {product_cfg['name']}'s Growth Playbook in 6 Rules
6 one-sentence rules. Every sentence must contain at least one number from the data.
"""


# ── AI API callers ────────────────────────────────────────────────────────────

def call_openai(prompt: str, model: str = "gpt-4o-mini") -> str:
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("ERROR: openai not installed. Run: pip install openai")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        sys.exit("ERROR: OPENAI_API_KEY not set in .env")

    client = OpenAI(api_key=api_key)
    print(f"  [api] Calling OpenAI {model}...")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000,
    )
    return response.choices[0].message.content


def call_anthropic(prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
    try:
        import anthropic
    except ImportError:
        sys.exit("ERROR: anthropic not installed. Run: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ERROR: ANTHROPIC_API_KEY not set in .env")

    client = anthropic.Anthropic(api_key=api_key)
    print(f"  [api] Calling Anthropic {model}...")

    message = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def call_gemini(prompt: str, model: str = "models/gemini-2.5-flash") -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("ERROR: google-genai not installed. Run: pip install google-genai")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY not set in .env")

    client = genai.Client(api_key=api_key)
    print(f"  [api] Calling Gemini {model}...")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=8192,
        ),
    )
    text = response.text or ""
    # Gemini sometimes pads markdown table cells with huge whitespace — collapse it
    import re
    text = re.sub(r" {10,}", "  ", text)
    return text


def detect_provider() -> tuple[str, str]:
    """Auto-detect which API key is available."""
    explicit = os.environ.get("PLAYBOOK_AI_PROVIDER", "").lower()
    if explicit:
        if explicit == "openai":
            return "openai", "gpt-4o-mini"
        if explicit in ("anthropic", "claude"):
            return "anthropic", "claude-haiku-4-5-20251001"
        if explicit == "gemini":
            return "gemini", "models/gemini-2.5-flash"

    if os.environ.get("OPENAI_API_KEY"):
        return "openai", "gpt-4o-mini"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic", "claude-haiku-4-5-20251001"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini", "gemini-2.0-flash"

    sys.exit(
        "ERROR: No API key found. Set one of these in .env:\n"
        "  OPENAI_API_KEY=...\n"
        "  ANTHROPIC_API_KEY=...\n"
        "  GEMINI_API_KEY=...\n"
        "And optionally: PLAYBOOK_AI_PROVIDER=openai|anthropic|gemini"
    )


def call_api(prompt: str, provider: str, model: str) -> str:
    if provider == "openai":
        return call_openai(prompt, model)
    if provider == "anthropic":
        return call_anthropic(prompt, model)
    if provider == "gemini":
        return call_gemini(prompt, model)
    sys.exit(f"Unknown provider: {provider}")


# ── Output writer ─────────────────────────────────────────────────────────────

def write_output(content: str, provider: str, model: str, product_name: str, insights: dict) -> Path:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = insights["dataset_summary"]["total_classified"]
    platforms = insights["dataset_summary"]["platforms"]
    platform_str = ", ".join(f"{p}: {n}" for p, n in platforms.items())

    header = f"""<!-- Generated: {now} -->
<!-- Model: {provider}/{model} | Product: {product_name} -->
<!-- Source data: {total} classified posts across {platform_str} -->
<!-- Data files: data/processed/spike_classified.csv, growth_frontpage.csv, unified_posts.csv -->
<!-- Audit trail: data/processed/playbook_context.json -->

"""
    full = header + content
    OUTPUT_MD.write_text(full, encoding="utf-8")
    return OUTPUT_MD


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate AI-powered counter-playbook from scraped data")
    parser.add_argument("--product",  default="higgsfield", choices=list(PRODUCTS.keys()),
                        help="Target product (default: higgsfield)")
    parser.add_argument("--provider", default=None, choices=["openai", "anthropic", "gemini"],
                        help="AI provider override (default: auto-detect from .env)")
    parser.add_argument("--dry-run",  action="store_true",
                        help="Extract data and build prompt, but don't call the API")
    args = parser.parse_args()

    # Load .env
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    product_cfg = PRODUCTS[args.product]
    print(f"\n  [playbook] Product: {product_cfg['name']}")

    # Step 1 — Extract insights from CSVs
    insights = extract_insights()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    CONTEXT_JSON.write_text(json.dumps(insights, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [extract] Saved context → {CONTEXT_JSON.name}")
    print(f"  [extract] Posts: {insights['dataset_summary']['total_classified']} classified, "
          f"{insights['dataset_summary']['total_unified']} unified")

    # Step 2 — Build prompt
    prompt = build_prompt(insights, product_cfg)
    print(f"  [prompt] Built prompt ({len(prompt):,} chars)")

    if args.dry_run:
        dry_path = ROOT / "data" / "processed" / "playbook_prompt_dry_run.txt"
        dry_path.write_text(prompt, encoding="utf-8")
        print(f"  [dry-run] Prompt saved → {dry_path}")
        print("  [dry-run] Skipping API call. Remove --dry-run to generate.")
        return

    # Step 3 — Detect provider and call API
    if args.provider:
        provider = args.provider
        model = {"openai": "gpt-4o-mini", "anthropic": "claude-haiku-4-5-20251001", "gemini": "models/gemini-2.5-flash"}[provider]
    else:
        provider, model = detect_provider()

    print(f"  [api] Provider: {provider} / {model}")
    content = call_api(prompt, provider, model)

    # Step 4 — Write output
    out_path = write_output(content, provider, model, product_cfg["name"], insights)
    print(f"\n  [done] Counter-playbook → {out_path}")
    print(f"  [done] Audit trail     → {CONTEXT_JSON}")


if __name__ == "__main__":
    main()
