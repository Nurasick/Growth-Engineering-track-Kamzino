# Claude's Viral Growth Playbook — Final Analysis
## HackNU 2026 · Growth Engineering Track · Part 2

> **This is the final non-generated analysis deliverable.**
>
> **Data provenance:** Every finding below is grounded in the repo's scraped CSV data and derived charts. No outside summaries were used to create the claims.
>
> **Challenge alignment:** This document is the answer to Part 2 of `GROWTH ENGINEERING TRACK.pdf` ("Decode the Playbook") and is also the evidence base used for the counter-playbook in Part 4.

---

## Methodology and engagement definitions

This repo now has **two different metric layers**, and this document uses them deliberately:

1. **Long-horizon platform-native analysis** — used for the big strategic findings in this file.  
   This keeps each platform's native signal when that signal is the real thing we care about:
   - **X historical findings:** mostly use **views** as reach, because the 16-month X dataset is about narrative spread and view-scale distribution.
   - **Reddit findings:** use **score** and **comment activity**.
   - **YouTube findings:** use **views** first, with likes/comments as supporting quality signals.
   - **HN findings:** use **points** and **comments**.

2. **Current unified pipeline scoring** — used elsewhere in the app for cross-platform ranking/velocity:
   - **X engagement score:** `likes + 2*retweets + 2*replies + bookmarks`
   - **Reddit engagement score:** `score + 3*num_comments`
   - **YouTube engagement score:** `view_count`

Why both exist: a single cross-platform score is useful for feeds and alerts, but the analysis in this file is stronger when it uses the platform's native reach signal directly.

**Dataset versions used in this analysis:** Findings 1–2 and 4–14 use the full multi-platform dataset assembled in the repo, including the long-range X historical scrape. Finding 3 (spike type engagement) uses the earlier 855-post balanced dataset because it is cleaner for comparing spike types across platforms with very different scale distributions.

---

## TL;DR

1. Claude growth is **not evenly distributed**; a tiny minority of posts creates most visible reach.
2. The strongest observed viral events spread as a **cross-platform cascade** rather than isolated per-platform spikes.
3. Different content formats do different jobs: breakthrough content ignites attention, tutorials explain, personal posts build trust, and meme formats expand cultural reach.
4. **Timing matters structurally** on HN and Reddit because early traction determines whether a post stays visible long enough to spread.
5. Word-lift is useful as a **frame detector**, not a bag of magic keywords.
6. The Pentagon saga shows that **values-aligned controversy** can behave like growth when it reinforces what the target audience already believes.
7. Platform decay differs sharply: HN is short-lived, Reddit is medium-lived, and YouTube keeps paying off longer.
8. Some of Claude's biggest discourse moments were **externally triggered**, so growth monitoring has to track competitor moves and narrative shocks, not just launches.
9. When the market names a behavior around the product, the product gains a **portable cultural handle** that others can spread.
10. Reach is concentrated in a small set of authors and voices, so growth strategy should identify and activate specific distribution nodes rather than assume the whole community carries equally.

---

## Three Questions Only Scraping Can Answer

The brief says: *"If your analysis could have been written by someone who never touched a scraper, that is a problem."* These three findings cannot be reached without the data.

**1. How does a 6,800-follower account generate 2.85M views?** (415x ratio)
You need author follower counts AND view counts in the same row. @MangoLassC doesn't appear in any "top influencer" list. Only by joining follower data (from fxtwitter enrichment) with view counts (from the Playwright scrape) does this account surface. Finding 12.

**2. What is the single most persistent cross-platform narrative in 16 months of Claude discourse?**
Not a product launch. Not the source code leak. It's "Why I Switched From ChatGPT to Claude" — 333 posts across all 4 platforms, running since February 2026. Invisible in per-post ranking. Only detectable by running `cascade_detector.py` across the full unified dataset. Finding 14.

**3. Did the source code leak reach Arabic YouTube — and how fast?**
Yes. "تسريب Claude كشف أسرار أخطر من الكود" appeared within the same weekly window as the HN ignition. Requires cross-referencing YouTube scrape data with HN timestamps across platforms — not findable from any single platform's data. Finding 2 + Finding 14.

---

## Dataset Summary

| Platform | Posts | Coverage |
|---|---|---|
| Hacker News | 3,779 | 90 days (Jan–Apr 2026), Algolia API |
| Reddit | 125 posts + 584 comments | Last year, top posts, 5 subreddits |
| X / Twitter (fxtwitter) | 82 tweets | Known handles, full engagement |
| X / Twitter (Playwright historical) | 1,668 tweets | **Jan 2025 → Apr 2026 — 16 months, enriched via fxtwitter** |
| X / Twitter (Playwright live) | 384 tweets | Live feed, last 48h |
| YouTube | 86 videos + 293 comments | Last 2 weeks, YouTube Data API v3 |
| **Total** | **~6,100 posts/tweets** | Unified schema, deduped, velocity scored |

*X historical collected via Playwright (real Chromium browser with auth cookies) to bypass x-client-transaction-id anti-scraping. Enriched via fxtwitter API for full engagement metrics.*

---

## Finding 1 — The Power Law Is the First Thing You Need to Know

**Claim:** Claude's viral presence is not broad-based growth — it's an extreme power-law distribution where a tiny minority of posts generate nearly all the reach.

**HN evidence (n=3,779 posts, 90 days):**

| Score Range | Posts | % of Total |
|---|---|---|
| 0–5 | 3,334 | **88.2%** |
| 6–20 | 276 | 7.3% |
| 21–100 | 99 | 2.6% |
| 101–300 | 45 | 1.2% |
| 300+ | 25 | **0.7%** |

Median score: **2 pts.** Mean score: 19.1. The top 25 posts (0.7%) account for a wildly disproportionate share of all engagement. The mean is so much higher than the median because of a handful of extreme outliers — the Dario Pentagon statement (2,920 pts), Claude Sonnet 4.6 launch (1,346 pts), and a cluster of DoW controversy posts.

![HN Power Law](data/charts/chart_hn_power_law.png)

**X evidence:** Same pattern. Median tweet views: 1,080 (140–280 char tweets). Mean: 180,251. The @boltdotnew "vibe coding goes pro" tweet (56.1M views) and source code leak posts pull the mean to 200x the median.

**Growth insight:** The question to ask is not "how do we get more posts" but "what are the specific conditions that produce a top-0.7% post." Volume is noise. The 3,334 posts with 0–5 pts add up to roughly the same reach as the single Dario statement.

---

## Finding 2 — The 3-Wave Cascade (Timestamped)

**Claim:** Claude discourse spreads in 3 waves: HN/X ignition → YouTube tutorials → Reddit/meme cultural lock-in.

**Evidence:** The April 1, 2026 source code leak gives us a clean natural experiment across all 4 platforms:

| Time (UTC) | Platform | Score/Views | Event |
|---|---|---|---|
| Apr 01 01:13 | HN | 2 pts | First post — "Anthropic goes nude, exposes Claude Code source" |
| Apr 01 01:20 | YouTube | 162,576 views | Matthew Berman: "Claude Code was just leaked... (WOAH)" — 7 min after HN |
| Apr 01 02:01 | YouTube | 111,462 views | Nate Herk: "Claude Code Source Code Just Leaked… 8 Things You Must Do" |
| Apr 01 04:15 | YouTube | 182,642 views | Theo (t3.gg): "BREAKING: Claude Code source leaked" |
| Apr 01 12:54 | Reddit | 337 pts | First Reddit post about the leak — 12h after HN |
| Apr 01 17:27 | YouTube | **2,592,415 views** | Fireship: "Tragic mistake... Anthropic leaks Claude's source code" — 16h after HN |
| Apr 03 16:30 | YouTube | 131,467 views | SAMTIME: "Claude Leaks its Source Code… then Files Copyright Claim" — satire wave |
| Apr 03 18:00 | YouTube | 89,249 views | Portuguese creators: "Em 48h recriaram o Claude Code de graça" — international wave |

![3-Wave Cascade](data/charts/chart_cascade_timeline.png)

**Wave structure confirmed:**
- **Wave 1 (0–2h):** HN ignition + immediate YouTube reaction from pre-briefed technical creators
- **Wave 2 (2–16h):** Tutorial/breakdown content, Reddit joins, peak reach
- **Wave 3 (48h+):** Satire, non-English creators, cultural commentary

**Growth insight:** The window for maximum impact is **0–16 hours.** After 48h, content shifts from information to culture — still valuable but no longer actionable for a competitor response.

---

## Finding 3 — Spike Type Volume vs Engagement Inverted

**From 855 classified posts (balanced dataset — better platform distribution):**

| Spike Type | % of Posts | Avg Engagement | Median Engagement |
|---|---|---|---|
| Breakthrough | 45% | 146,931 | 4 |
| Tutorial | 26% | 33,796 | 5 |
| Personal | 10% | 28,177 | **914** |
| Meme | 9% | **588,136** | 337 |
| Comparison | 7% | 7,098 | 32 |

![Spike Types](data/charts/chart_spike_types.png)

**Key observations:**
1. **Meme content has the highest average engagement** (588K) despite being only 9% of posts. The ceiling is enormous when a meme lands.
2. **Breakthrough posts dominate in volume but have the lowest median** (4 pts). Most announcements get ignored; the ones that hit go massive.
3. **Personal stories have the best median-to-average ratio** — more consistent. They rarely go massive but almost never get zero.
4. The mean vs median gap for breakthrough (146K mean, 4 median) shows a classic power-law distribution — a few viral posts inflate the average.

---

## Finding 4 — Posting Time Matters More Than Most Growth Teams Think

**HN — score by hour (UTC), n=3,779:**

| Hour (UTC) | Avg Points | US Time | Notes |
|---|---|---|---|
| 22:00 | **39.7** | 6pm ET | Best by a large margin |
| 23:00 | 16.9 | 7pm ET | Strong |
| 19:00 | 14.0 | 3pm ET | Good |
| 01:00 | 16.2 | 9pm ET prior night | Strong (late posting) |
| 04:00–10:00 | 1.6–5.7 | Night/morning ET | Worst hours |

The 22:00 UTC hour (6pm ET) has an average of 39.7 pts vs a baseline of 9.5 — more than **4x** the baseline. This is not noise: the HN front page is most active in early US evening when West Coast engineers are finishing work and East Coast is post-dinner.

**Reddit — score by day of week:**

| Day | Avg Score | vs Thursday |
|---|---|---|
| Sunday | 4,344 | **2.7x** |
| Saturday | 3,549 | 2.2x |
| Wednesday | 2,799 | 1.7x |
| Monday | 1,981 | 1.2x |
| Thursday | 1,625 | baseline |

![Platform Timing](data/charts/chart_timing.png)

**Why this matters structurally:** HN requires live engagement in the first hours — posts voted on at 6pm ET go to the front page when US engineers are online to vote them up further. Reddit weekends work because r/ChatGPT, r/ClaudeAI users browse more leisurely on weekends and threads survive longer before falling off.

---

## Finding 5 — Title Language: Controversy and Comparison Dominate

**Word lift analysis — words overrepresented in top-20% HN posts vs baseline (min 15 occurrences):**

| Word | Lift | Avg Score | n | Interpretation |
|---|---|---|---|---|
| "department" | **36x** | 344.8 | 15 | Pentagon/DoW controversy |
| "war" | 25.6x | 244.4 | 26 | Dept of War framing |
| "supply" / "chain" | 15–16x | 144–151 | 22–23 | Supply chain risk designation |
| "leaked" / "leaks" | ~22x | — | — | Scandal framing |
| "chatgpt" | ~15x | — | — | Comparison framing |
| "safety" | 6.7x | 64.2 | 21 | Safety/ethics framing |
| "tutorial" | high | — | — | Actionable content signal |

**Words that hurt (low lift):**
- "generated" (0.29x), "local" (0.22x), "powered" (0.25x), "server" (0.24x) — generic AI/LLM terms that signal commodity posts

![Title Word Lift](data/charts/chart_word_lift.png)

**The Pentagon cluster specifically:** Pentagon/DoW-related posts average **51.9 pts** vs 6.5 for the rest of HN (**8.0x lift**). Comments per post: 27.3 vs 3.9 (**7.0x**). This is the highest-lift topic cluster in our entire dataset — higher than product launches, higher than funding, higher than comparison content.

---

## Finding 6 — The Pentagon Saga Was a 6-Week Free Growth Campaign

**Claim:** The Anthropic–Pentagon conflict (Feb 13 – Mar 26, 2026) was the single largest sustained organic growth event in our dataset — across multiple platforms simultaneously.

**HN evidence — controversy cluster timeline:**

| Date | Score | Comments | Event |
|---|---|---|---|
| Feb 13 | 25 | 5 | Pentagon Used Claude in Venezuela Raid |
| Feb 26 | **2,920** | **1,580** | Dario: "Cannot in good conscience accede" |
| Feb 27 | 1,362 | 1,085 | DOW Designates Anthropic Supply-Chain Risk |
| Feb 28 | 1,170 | 357 | Hegseth Statement |
| Feb 28 | 42 | — | **Claude rises to #2 in App Store** |
| Mar 01 | 138 | — | **Claude dethrones ChatGPT as top US app** |
| Mar 04 | 805 | 425 | Dario calls OpenAI's military stance "straight up lie" |
| Mar 06 | 630 | 788 | Most controversial post (ratio: comments > points) |
| Mar 26 | 446 | 233 | Judge Blocks Pentagon Effort |

![Pentagon Controversy](data/charts/chart_pentagon_controversy.png)

**The App Store effect is documented in our data:** After Dario's Feb 26 statement, Claude went from #2 to #1 in the US App Store (HN: 138 pts, "Claude dethrones ChatGPT as top US app after Pentagon saga"). This is a controversy-to-download conversion that no paid campaign could engineer.

**Why the controversy worked as growth:** HN upvotes are a proxy for "what developers care about." Developers care deeply about AI ethics and government interference. Every Pentagon escalation was a new reason for Claude's audience to engage, share, and take a side. The controversy *credentialed* Claude as the AI company willing to say no to military pressure — which is a positioning statement worth more than any ad.

**Growth insight:** Controversy that aligns with your audience's values is indistinguishable from organic growth. Anthropic's actual customers (developers) were already skeptical of military AI applications. The Pentagon conflict didn't hurt Claude — it generated its biggest App Store moment.

---

## Finding 7 — Community YouTube = 29x Official, and Fireship Alone = 13x

**YouTube data (86 videos, 2-week window):**

| | Videos | Total Views | Avg/Video |
|---|---|---|---|
| Anthropic official | 1 | 196,616 | 196,616 |
| Community creators | 85 | 5,816,231 | 68,426 |
| **Ratio** | — | **29x** | — |

**Channel breakdown (top performers on single events):**

| Channel | Views | Context |
|---|---|---|
| Fireship | 2,592,415 | Source code leak reaction — organic, not briefed |
| Dan Martell | 316,127 (3 videos) | Avg 105K each |
| Anthropic | 196,616 | Official channel |
| Theo - t3.gg | 182,642 | Leak reaction |
| Matthew Berman | 162,576 | Leak reaction |
| NeetCode | 151,715 | Tutorial |

Fireship's single video on the source code leak (2.59M views) beat Anthropic's entire YouTube output by **13x** on the same event.

![YouTube Community vs Official](data/charts/chart_youtube_reach.png)

**On X/Twitter — official vs community is different:**

| | Tweets | Total Views | Avg/Tweet |
|---|---|---|---|
| @AnthropicAI (official) | 44 | 62,426,126 | 1,418,775 |
| Community accounts | 38 | 48,446,883 | 1,274,917 |

On X, official and community are **roughly equal per tweet** — suggesting the official account is genuinely effective on X, unlike YouTube.

**Growth insight:** Platform-specific strategy. YouTube: brief creators, skip building own channel. X: maintain official account, it punches at community weight.

---

## Finding 8 — Engagement Decay by Platform

From velocity rankings (HN gravity formula, normalized):

| Platform | Day 0 avg velocity | Day 1 | Day 3 | Day 6 |
|---|---|---|---|---|
| HN | 0.033 | ~0 | 0.001 | 0.001 |
| Reddit | 0.240 | 0.027 | 0.008 | ~0 |
| YouTube | 0.055 | 0.024 | 0.010 | 0.004 |

![Engagement Decay](data/charts/chart_decay.png)

HN has the steepest decay — a post is effectively dead after 24 hours. YouTube retains velocity longest — videos continue gaining views 6+ days later. Reddit is in between — weekend posts can survive into Monday.

**Scheduling implication:** For HN, same-day response is required. For YouTube, a week window to act. For Reddit, weekend seeding can be planned ahead.

---

## Finding 9 — The Threat Catalyst: Competitor Attacks Drive 3x More Views Than Own Launches

**Claim:** When a competitor threatens Claude's position, it generates more organic discourse than Claude's own product launches.

**Evidence from X historical data (1,668 tweets, Jan 2025–Apr 2026):**

| Tweet | Author | Views | Type |
|---|---|---|---|
| "Grok Code just hit #1 on OpenRouter, beating Claude Sonnet" | @elonmusk | 22.1M | External threat |
| "Grok Code lead increased to 60% higher usage than Claude Sonnet" | @elonmusk | 5.2M | External threat |
| "New Anthropic research: Emotion concepts..." | @AnthropicAI | 3.4M | Official |
| Boris tips thread: "I'm Boris and I created Claude Code..." | @bcherny | 9.1M | Creator personal |

Two Grok Code threat tweets = **27.3M views combined** — 3x more than the biggest official Claude announcements in our dataset.

**Monthly view distribution (1,668 tweets, Jan 2025 – Apr 2026):**

| Month | Total Views | Key Driver |
|---|---|---|
| Jan 2025 | 0.8M | Early community |
| Feb 2025 | 9.4M | @karpathy "vibe coding" origin (6.9M) |
| Aug 2025 | 31.7M | @elonmusk Grok Code threat x2 (27.3M combined) |
| Sep 2025 | 57.9M | @boltdotnew "vibe coding goes pro" (56.1M) |
| Dec 2025 | 12.6M | @bcherny Claude Code origin story (4.6M) + Karpathy demo (3M) |
| Jan 2026 | 18.1M | @bcherny tips thread (9.1M) |
| Mar 2026 | **70.6M** | @Fried_rice source leak (34.8M) + community cascade |
| Apr 2026 | 19.5M | Leak aftermath + @AnthropicAI response content |

![Monthly X Views](data/charts/chart_monthly_x_views.png)

**Why this happens:** Threat content triggers tribal defense response. Developers who use Claude don't just watch — they retweet to argue, debunk, and reassure themselves. Every defensive action amplifies the original threat post further. The mechanism is the same as the Pentagon saga but faster.

**Growth insight:** Claude's two biggest X months (Sep 2025: 57.9M, Mar 2026: 70.6M) were both driven by external events — not product launches. Monitoring competitor launches is as important as planning your own.

---

## Finding 10 — The "Naming the Movement" Effect

**Claim:** A single external creator coining a phrase for a behavior associated with your product creates a compound category that nobody can take away.

**Evidence:**

| Date | Event | Views |
|---|---|---|
| Feb 2, 2025 | @karpathy: "There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes..." | 6.9M |
| Feb 2025 → Apr 2026 | "Vibe coding" becomes dominant framing for Claude Code usage | 346 collected tweets in our dataset |
| Sep 30, 2025 | @boltdotnew: "Today vibe coding goes pro. Introducing Bolt v2: World's best agents (Claude…)" | **56.1M** — highest-viewed tweet in our dataset |
| Dec 2025 | @karpathy builds smart home controller with Claude Code | 3.0M |

Karpathy's Feb 2025 tweet did not announce a product. It named a *behavior* — coding by feel, letting Claude write the code — and tied it to a cultural identity. Bolt's "vibe coding goes pro" tweet then appropriated the term for their own launch, generating the single highest-viewed tweet in our 16-month dataset.

**Content type breakdown — total vs median reveals the real pattern:**

| Content Type | Tweets | Total Views | Median Views |
|---|---|---|---|
| Vibe-coding | 346 | 74.0M | 1,444 |
| Scandal/leak | 21 | 50.7M | **353,005** |
| Competitor framing | 720 | 46.8M | 381 |
| Personal demo | 63 | 27.5M | 2,231 |
| Tutorial | 61 | 8.2M | 4,382 |
| Launch/announcement | 26 | 7.6M | 4,642 |
| Meme | 31 | 1.4M | 1,942 |

**Critical observation:** Competitor framing has 720 tweets (the most of any category) for 46.8M total views, but a **381 median** — the second lowest. Almost all of the competitor content goes nowhere. The category is inflated by @elonmusk's two 22M+5M tweets. Without those outliers, competitor framing is the worst-performing category.

Scandal content, by contrast, has a **353,005 median** — meaning the *average* scandal post gets 353K views. The floor is high, not just the ceiling.

---

## Finding 11 — The Inside Engineer Effect: One Authenticated Voice = 11x Official Reach

**Claim:** A single engineer posting authentically about their own product generates more views than the official company account — not because of one viral tweet, but consistently over time.

**Evidence from X historical data:**

| Account | Type | Tweets Captured | Total Views | Avg Views/Tweet |
|---|---|---|---|---|
| @bcherny | Engineer (Claude Code creator) | 124 | **44.3M** | 357,244 |
| @AnthropicAI | Official | 6 | 4.0M | 668,069 |
| @claudeai | Official product | 6 | 3.2M | 538,360 |

@bcherny's **124 tweets** generated 44.3M views — **11x more total reach** than both official accounts combined. His top 5 posts:

| Tweet | Views | Date |
|---|---|---|
| "I'm Boris and I created Claude Code. I wanted to quickly share a few tips..." | 9.1M | Jan 2026 |
| "When I created Claude Code as a side project back in September 2024..." | 4.6M | Dec 2025 |
| "I wanted to share a bunch of my favorite hidden and under-utilized features..." | 3.8M | Mar 2026 |
| "In the next version of Claude Code.. introducing two new Skills..." | 2.5M | Feb 2026 |
| "Today we're excited to announce NO_FLICKER mode..." | 2.4M | Apr 2026 |

This is not one outlier tweet. It's **sustained 2–9M view performance** across multiple tweet types: tips, origin story, feature announcements, memes ("I feel this way most weeks tbh" — 1.76M views).

![Inside Engineer Effect](data/charts/chart_inside_engineer.png)

**Why this works structurally:**
1. "I built this" is more credible than "we built this" — authenticity signal that official accounts cannot replicate
2. First-person framing on inside knowledge (tips, hidden features) signals access the community doesn't have
3. No PR review = human voice, typos, opinions — all of which the developer audience trusts over polished corporate copy
4. @bcherny's posts generate discussion, not just views — the 1,424K "100% of my contributions to Claude Code in the last 30 days" reply became its own conversation thread

**Growth insight:** Finding and empowering one credible internal engineer to post with full creative autonomy is the highest-leverage X play. Not optimizing the official handle. Not running sponsored content. One authentic voice.

---

## Finding 12 — Small Accounts Can Go Massive: Follower Count Is Not the Constraint

**The anti-intuitive finding from our X data:**

| Account | Followers | Views | Views/Follower ratio |
|---|---|---|---|
| @MangoLassC | 6,861 | 2,852,739 | **415x** |
| @cgtwts | 19,958 | 2,246,056 | 112x |
| @altryne | 40,218 | 1,990,893 | 50x |
| @iamfakeguru | 7,665 | 1,614,824 | 211x |
| @0xluffy | 23,181 | 927,696 | 40x |

@MangoLassC (6,861 followers) got 2.85M views on "just switched from chatgpt to claude and oh my God." — a genuine reaction tweet with no media, no thread, no tactics. The tweet hit because the message resonated with the moment (post-leak, post-Pentagon, Claude was trending), not because of the account's reach.

**X follower buckets vs median views:**

| Follower Count | n | Median Views | Mean Views |
|---|---|---|---|
| <10K | 132 | 2,260 | 47,368 |
| 10K–100K | 375 | 4,816 | 190,113 |
| 100K–1M | 307 | 31,768 | 392,674 |
| 1M+ | 23 | 270,294 | 1,973,918 |

Follower count correlates with median (expected), but the outlier-to-median ratio is *highest* in the <10K bucket — meaning when small accounts go viral about Claude, they go more disproportionately viral than large accounts do.

**Growth insight:** The conditions for virality are more about timing and message framing than account size. A product launch that generates genuine "oh wow" reactions will surface small-account posts that go massive. The platform distributes based on engagement velocity, not follower count. Seed the narrative; the platform does the amplification.

---

## Finding 13 — Reddit: Bigger in Competitor's House

**Claim:** Claude content performs better on r/ChatGPT than on r/ClaudeAI.

**Evidence:**

| Subreddit | n | Median Score | Mean Score | Max |
|---|---|---|---|---|
| r/ChatGPT | 25 | 2,300 | **5,770** | 29,926 |
| r/ClaudeAI | 25 | 4,056 | 4,593 | 8,143 |
| r/LocalLLaMA | 25 | 1,050 | 1,471 | 4,824 |
| r/artificial | 25 | 285 | 301 | 803 |
| r/MachineLearning | 25 | 62 | 94 | 235 |

r/ChatGPT has a **higher mean score** (5,770 vs 4,593) for Claude-related posts. The top r/ChatGPT post about Claude in our dataset: "Cancel your ChatGPT Plus, burn their compute on the way out, and switch to Claude" — **29,926 upvotes.**

![Reddit Subreddits](data/charts/chart_reddit_subreddits.png)

**Why this happens:** r/ClaudeAI readers are already converted. r/ChatGPT readers are open to switching — Claude content lands as discovery, not preaching to the choir. The comparison/switching frame that underperforms on HN (developers evaluate tools independently) *overperforms* on Reddit (users want social proof for tool choices).

**Growth insight:** For a competing product, seeding in a competitor's community is more effective than building your own community first. The audience in competitor communities already has purchase intent — they're paying for a similar product. Organic content that addresses switching framing will outperform in-community content at early stage.

---

## Finding 14: The Competitor Switching Narrative Is the Most Persistent Cross-Platform Thread

**Method:** `analysis/cascade_detector.py` — cross-platform narrative correlator run on 11,454 posts across 16 months. Groups posts by shared keyword overlap within sliding time windows, detects when the same story spreads across multiple platforms.

**What the data shows:**

Running the cascade detector on the full dataset surfaces 48 distinct narrative clusters. The single most persistent sustained narrative across the entire 16-month dataset is not a product launch, not the Pentagon controversy, and not a viral meme. It is the competitor switching story:

| Narrative | Posts | Platforms | Peak engagement | Spread pattern |
|---|---|---|---|---|
| "Why I Switched From ChatGPT to Claude" | **333** | **4/4** | 170,513 pts | HN → Reddit (+188h) → X (+98h) → YouTube (+675h) |
| Source code leak (anthropic_news cluster) | 914 | 4/4 | 2,592,415 pts | HN → Reddit (+35h) → X (+103h) → YouTube (+958h) |
| "AI News: Anthropic Leak is Bigger Than You Think" | 245 | 4/4 | 55,639 pts | HN → Reddit (+30h) → X (+364h) → YouTube (+757h) |
| "the end of Claude Code" (attack narrative) | 23 | 3/4 | 85,756 pts | HN → Reddit (+79h) → YouTube (+686h) |

**The ChatGPT switching narrative is significant for three reasons:**

1. **It ran all 4 platforms spontaneously.** No official Anthropic post seeded it. It started on HN as an organic user comparison, moved to Reddit (competitor territory, r/ChatGPT), reached X, and eventually YouTube — across 8 weeks of discourse. This is the same organic competitor-seeding pattern that drives growth for tools like Linear and Notion.

2. **It outperforms most launch content.** 333 posts with 170K peak engagement across all platforms — this is more sustained engagement than any single Anthropic announcement in our dataset outside of the source code leak.

3. **The attack narrative spreads too.** "the end of Claude Code" — 23 posts, 3 platforms, 85K peak — demonstrates that competitor attack narratives also cascade. A growth team needs to monitor for these early (Finding 9 threat catalyst applies here).

**A finding only reachable with cross-platform cascade detection:**

A per-post analysis would show this as 333 separate posts. The cascade detector reveals it as one narrative thread that has been running since February 2026 across every platform simultaneously. That distinction matters: it means the switching narrative is not a one-time viral moment — it is a structural feature of how users discuss Claude. Anthropic doesn't manufacture it. Users do it unprompted. The growth team's job is to make switching stories easy to find and share.

**Additional cascade finding — international spread:**

The source code leak cascade includes Arabic-language YouTube coverage: "تسريب Claude كشف أسرار أخطر من الكود" (Claude leak reveals secrets more dangerous than the code) — appearing in the `claude_code + ai_safety` cluster alongside HN posts from the same week. This required cross-referencing YouTube scrape data with HN timestamps — not detectable from any single platform's data alone.

**Growth insight:** The competitor switching narrative is Claude's most durable organic growth engine. It requires no seeding, no launches, and no budget — it runs because users are genuinely migrating and talking about it. For a competing product like Higgsfield, the equivalent is getting users to post "I switched from Runway/Sora to Higgsfield" in video creator communities. The cascade detector is how you know when that narrative is starting.

---

## Limitations

- **X historical data is Top-mode biased.** Search returns high-engagement tweets preferentially — low-engagement posts are underrepresented. The dataset is a reliable sample of *what went viral*, not a complete census.
- **YouTube window is 2 weeks only.** Historical YouTube data requires paid API quotas; we used the free tier limit.
- **HN timing analysis has a noise component.** The 22:00 UTC spike is real but partially confounded by the Pentagon posts (many filed in US evening hours by journalists). Direction is correct; magnitude should not be over-indexed.
- **We did not force one unified engagement score for the long-horizon analysis.** Different platforms expose different primary signals — HN gives points/comments, Reddit gives score/comments/upvote ratio, X gives views plus interaction counts, and YouTube gives views/likes/comments. For the strategic findings in this document, we kept platform-native inputs where that preserved meaning better than flattening everything into one artificial score.
- **Instagram, LinkedIn, TikTok** — not scraped. Public API access requires login or paid tier.
- **The cascade timing is from one event** (source code leak). Generalizing to all launch types requires more events.
- **n per Reddit bucket is 25.** Subreddit comparisons are directionally reliable, not statistically definitive.

---

## Summary: Claude's Growth Playbook in 9 Rules

1. **The power law is the whole game.** 88% of posts get ≤5 pts. The question is never "how do we post more" — it's "what creates a top-0.7% post." Volume is noise.

2. **The 3-wave cascade runs 0–48h.** HN ignites, YouTube tutorials follow in hours, Reddit/meme content cements at 48h+. If you haven't briefed creators before hour 2, you're catching the third wave.

3. **Brief Fireship/Theo/Matthew Berman before launch.** Community YouTube = 29x official channel. Fireship alone beat Anthropic's entire channel 13x on the same event with zero coordination.

4. **"Leaked", "war", "supply chain", "chatgpt"** — these words in HN titles have 15–36x lift over baseline. "generated", "local", "powered" hurt. Lead with the stakes, not the features.

5. **Controversy that aligns with your audience's values is indistinguishable from organic growth.** The Pentagon saga drove Claude to #1 in the App Store. 6 weeks of controversy = 8x average HN score on every post.

6. **Scandal has the highest floor on X (353K median), not just ceiling.** Competitor content has 381 median — almost all competitor framing goes nowhere unless you're @elonmusk. Scandal-adjacent content is the most reliable format.

7. **External events dominate your biggest months.** Claude's top X months (Sep 2025: 57.9M, Mar 2026: 70.6M) were both external events. No product launch in our dataset comes close.

8. **One inside engineer beats the official account by 11x.** @bcherny's 124 tweets = 44.3M views. @AnthropicAI + @claudeai combined = 7.2M. Authentic first-person "I built this" content is the highest-leverage X play.

9. **Follower count is not the constraint.** @MangoLassC (6.8K followers) got 2.85M views. The platform distributes based on engagement velocity in the first hour. Seed the narrative; the algorithm does the rest.
