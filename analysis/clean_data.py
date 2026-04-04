"""
clean_data.py — Discourse master dataset builder
Reads raw CSVs from /data/raw, normalises to unified schema,
computes engagement scores and categories, writes to /data/clean.
"""

import os
import re
import logging

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename="c:/Users/Nurali/Hackathon/data/errors.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REDDIT_RAW = "c:/Users/Nurali/Hackathon/data/raw/reddit_posts_2026-04-04.csv"
HN_RAW = "c:/Users/Nurali/Hackathon/data/raw/hn_items_2026-04-04.csv"
YOUTUBE_RAW = "c:/Users/Nurali/Hackathon/data/raw/youtube_posts.csv"

MASTER_OUT = "c:/Users/Nurali/Hackathon/data/clean/discourse_master.csv"
HN_COMMENTS_OUT = "c:/Users/Nurali/Hackathon/data/clean/hn_comments.csv"

UNIFIED_COLUMNS = [
    "platform",
    "content_id",
    "title",
    "text_content",
    "author",
    "timestamp",
    "score",
    "num_comments",
    "upvote_ratio",
    "url",
    "subreddit_channel",
    "view_count",
    "like_count",
]

# ---------------------------------------------------------------------------
# Category classification
# ---------------------------------------------------------------------------
CATEGORY_PATTERNS = [
    (
        "Breakthrough / News",
        re.compile(
            r"leak|new model|release|launch|announce|ipo|fund",
            re.IGNORECASE,
        ),
    ),
    (
        "Tutorial / How-To",
        re.compile(
            r"how to|guide|tutorial|tips|setup|install|build with",
            re.IGNORECASE,
        ),
    ),
    (
        "Comparison",
        re.compile(
            r"\bvs\.?\b|versus|better than|switch(ed)? (from|to)|chatgpt|gemini|gpt",
            re.IGNORECASE,
        ),
    ),
    (
        "Showcase / Demo",
        re.compile(
            r"show hn|i built|i made|demo|open.?source|side project",
            re.IGNORECASE,
        ),
    ),
    (
        "Discussion / Opinion",
        re.compile(
            r"ask hn|why|think|opinion|thoughts|anyone else",
            re.IGNORECASE,
        ),
    ),
    (
        "Critique / Controversy",
        re.compile(
            r"fail|broken|bug|limit|ban|dmca|lawsuit|problem",
            re.IGNORECASE,
        ),
    ),
]


def classify_category(row):
    """Return the first matching category label, or 'Other'."""
    text = " ".join(
        [str(row.get("title", "") or ""), str(row.get("text_content", "") or "")]
    )
    for category, pattern in CATEGORY_PATTERNS:
        if pattern.search(text):
            return category
    return "Other"


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------
def log_norm(series):
    """Apply log1p then scale to 0-100."""
    logged = np.log1p(series.fillna(0).clip(lower=0))
    max_val = logged.max()
    if max_val == 0:
        return pd.Series(0.0, index=series.index)
    return (logged / max_val) * 100


def platform_engagement_score(df, platform):
    """Return engagement_score Series for a single-platform DataFrame."""
    if platform == "youtube":
        view_count = df["view_count"].replace(0, np.nan)
        like_rate = (df["like_count"] / view_count * 1000).fillna(0)
        return (
            0.5 * log_norm(df["like_count"])
            + 0.3 * log_norm(df["num_comments"])
            + 0.2 * log_norm(like_rate)
        ).round(2)
    elif platform == "reddit":
        return (
            0.6 * log_norm(df["score"])
            + 0.3 * log_norm(df["num_comments"])
            + 0.1 * log_norm(df["upvote_ratio"] * 10)
        ).round(2)
    elif platform == "hn":
        return (
            0.7 * log_norm(df["score"]) + 0.3 * log_norm(df["num_comments"])
        ).round(2)
    else:
        return pd.Series(0.0, index=df.index)


def add_viral_tier(df):
    """Bin engagement_score into Low / Mid / High / Viral labels."""
    df["viral_tier"] = pd.cut(
        df["engagement_score"],
        bins=[0, 25, 50, 75, 100],
        labels=["Low", "Mid", "High", "Viral"],
        include_lowest=True,
    )
    return df


def add_week(df):
    """Add a week column (start-of-week Monday) derived from timestamp."""
    df["week"] = df["timestamp"].dt.to_period("W").dt.start_time
    return df


def _empty_unified():
    """Return an empty DataFrame with the unified schema."""
    return pd.DataFrame(columns=UNIFIED_COLUMNS)


# ---------------------------------------------------------------------------
# Platform loaders
# ---------------------------------------------------------------------------
def load_reddit():
    """Load and normalise the Reddit raw CSV to the unified schema."""
    try:
        raw = pd.read_csv(REDDIT_RAW, dtype=str)
    except FileNotFoundError:
        logging.error("[REDDIT] Raw file not found: %s", REDDIT_RAW)
        print("  [reddit] raw file not found, skipping")
        return _empty_unified()
    except Exception as exc:
        logging.error("[REDDIT] Failed to load raw file: %s", exc)
        print(f"  [reddit] load error: {exc}")
        return _empty_unified()

    try:
        df = pd.DataFrame({
            "platform":         "reddit",
            "content_id":       raw["post_id"],
            "title":            raw["title"],
            "text_content":     raw["selftext"],
            "author":           raw["author"],
            "timestamp":        pd.to_datetime(raw["created_utc"], utc=True, errors="coerce"),
            "score":            pd.to_numeric(raw["score"], errors="coerce").fillna(0),
            "num_comments":     pd.to_numeric(raw["num_comments"], errors="coerce").fillna(0),
            "upvote_ratio":     pd.to_numeric(raw["upvote_ratio"], errors="coerce").fillna(0),
            "url":              raw["url"],
            "subreddit_channel": raw["subreddit"],
            "view_count":       0,
            "like_count":       0,
        })
        return df[UNIFIED_COLUMNS]
    except Exception as exc:
        logging.error("[REDDIT] Failed to normalise data: %s", exc)
        print(f"  [reddit] normalise error: {exc}")
        return _empty_unified()


def load_hn():
    """Load and normalise the HN raw CSV; split into stories and comments.

    Returns:
        (stories_df, comments_df) — both in unified schema.
    """
    try:
        raw = pd.read_csv(HN_RAW, dtype=str)
    except FileNotFoundError:
        logging.error("[HN] Raw file not found: %s", HN_RAW)
        print("  [hn] raw file not found, skipping")
        return _empty_unified(), _empty_unified()
    except Exception as exc:
        logging.error("[HN] Failed to load raw file: %s", exc)
        print(f"  [hn] load error: {exc}")
        return _empty_unified(), _empty_unified()

    try:
        # A row is a comment when comment_text is not null and not empty string.
        is_comment = raw["comment_text"].notna() & (raw["comment_text"].str.strip() != "")

        def _normalise_hn(subset, use_comment_text=False):
            df = pd.DataFrame()
            df["platform"] = "hn"
            df["content_id"] = subset["object_id"].astype(str)
            df["title"] = subset["title"]
            if use_comment_text:
                df["text_content"] = subset["comment_text"]
            else:
                df["text_content"] = subset["story_text"]
            df["author"] = subset["author"]
            df["timestamp"] = pd.to_datetime(
                subset["created_at"], utc=True, errors="coerce"
            )
            df["score"] = pd.to_numeric(subset["points"], errors="coerce").fillna(0)
            df["num_comments"] = pd.to_numeric(
                subset["num_comments"], errors="coerce"
            ).fillna(0)
            df["upvote_ratio"] = 0
            df["url"] = subset["url"]
            df["subreddit_channel"] = subset["tags"]
            df["view_count"] = 0
            df["like_count"] = 0
            return df[UNIFIED_COLUMNS].reset_index(drop=True)

        stories_df = _normalise_hn(raw[~is_comment], use_comment_text=False)
        comments_df = _normalise_hn(raw[is_comment], use_comment_text=True)
        return stories_df, comments_df
    except Exception as exc:
        logging.error("[HN] Failed to normalise data: %s", exc)
        print(f"  [hn] normalise error: {exc}")
        return _empty_unified(), _empty_unified()


def load_youtube():
    """Load and normalise the YouTube raw CSV; return empty DataFrame if absent."""
    if not os.path.exists(YOUTUBE_RAW):
        print("  [youtube] raw file not found, returning empty DataFrame")
        return _empty_unified()

    try:
        raw = pd.read_csv(YOUTUBE_RAW, dtype=str)
    except Exception as exc:
        logging.error("[YOUTUBE] Failed to load raw file: %s", exc)
        print(f"  [youtube] load error: {exc}")
        return _empty_unified()

    try:
        df = pd.DataFrame()
        df["platform"] = "youtube"
        df["content_id"] = raw["id"]
        df["title"] = raw["title"]
        df["text_content"] = raw["body_text"]
        df["author"] = raw["author"]
        df["timestamp"] = pd.to_datetime(
            raw["created_utc"], utc=True, errors="coerce"
        )
        df["score"] = pd.to_numeric(raw["score"], errors="coerce").fillna(0)
        df["num_comments"] = pd.to_numeric(raw["num_comments"], errors="coerce").fillna(0)
        df["upvote_ratio"] = 0
        df["url"] = raw["url"]
        df["subreddit_channel"] = raw["subreddit_or_channel"]
        df["view_count"] = pd.to_numeric(raw["view_count"], errors="coerce").fillna(0)
        df["like_count"] = pd.to_numeric(raw["like_count"], errors="coerce").fillna(0)
        return df[UNIFIED_COLUMNS]
    except Exception as exc:
        logging.error("[YOUTUBE] Failed to normalise data: %s", exc)
        print(f"  [youtube] normalise error: {exc}")
        return _empty_unified()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def run():
    os.makedirs("c:/Users/Nurali/Hackathon/data/clean", exist_ok=True)

    # 1. Load
    print("Loading platforms...")
    yt_df = load_youtube()
    reddit_df = load_reddit()
    hn_stories_df, hn_comments_df = load_hn()

    # 2. Engagement scores (per platform)
    dropped_total = 0
    all_stories = []
    for platform, df in [
        ("youtube", yt_df),
        ("reddit", reddit_df),
        ("hn", hn_stories_df),
    ]:
        if df.empty:
            print(f"  [{platform}] no data, skipping")
            continue
        df = df.copy()
        df["engagement_score"] = platform_engagement_score(df, platform)
        all_stories.append(df)

    master_df = (
        pd.concat(all_stories, ignore_index=True)
        if all_stories
        else pd.DataFrame()
    )

    if master_df.empty:
        print("No data loaded across any platform. Exiting.")
        return

    # 3. Category
    master_df["content_category"] = master_df.apply(classify_category, axis=1)

    # 4. Viral tier
    master_df = add_viral_tier(master_df)

    # 5. Week
    master_df = add_week(master_df)

    # 6. Save
    master_df.to_csv(MASTER_OUT, index=False)
    print(f"\nSaved discourse_master.csv ({len(master_df)} rows) -> {MASTER_OUT}")

    if not hn_comments_df.empty:
        hn_comments_df.to_csv(HN_COMMENTS_OUT, index=False)
        print(f"Saved hn_comments.csv ({len(hn_comments_df)} rows) -> {HN_COMMENTS_OUT}")

    # 7. Print summary
    print("\n=== ROW COUNTS PER PLATFORM ===")
    print(master_df.groupby("platform").size().to_string())

    print("\n=== CATEGORY DISTRIBUTION ===")
    print(master_df["content_category"].value_counts().to_string())

    print("\n=== VIRAL TIER PER PLATFORM ===")
    print(
        master_df.groupby(["platform", "viral_tier"])
        .size()
        .unstack(fill_value=0)
        .to_string()
    )

    print("\n=== HN COMMENTS ===")
    print(f"  Saved {len(hn_comments_df)} HN comments to hn_comments.csv")

    print("\n=== DROPPED ROWS ===")
    print(f"  Total dropped: {dropped_total} (see errors.log for details)")


if __name__ == "__main__":
    run()