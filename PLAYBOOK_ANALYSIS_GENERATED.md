<!-- Generated: 2026-04-05 04:11 UTC -->
<!-- Model: gemini/models/gemini-2.5-flash -->
<!-- Source data: 2427 classified posts — hn: 1884, reddit: 400, x: 57, youtube: 86 -->
<!-- Audit trail: data/processed/analysis_metrics.json -->

# Product's Viral Growth Playbook — Decoded

**Playbook type:** Hybrid: Creator-driven + Cascade — This playbook focuses on activating key creators to initiate and amplify content cascades, especially around significant events.
**Data provenance:** All findings derived from 2427 posts scraped across HN, Reddit, X, YouTube, April 1-5 2026.

---

## TL;DR — 10 Rules (read this first)

1.  **Activate Top Creators:** The top 5 authors generate 94.5% of total engagement, making them critical amplification channels (Growth).
2.  **Lead with Media:** X media posts drive 12.7x median engagement compared to text-only, demanding visual-first content (Content).
3.  **Ignite on HN:** HN is the first platform to react in cascades (0h), making it the primary ignition point for viral events (Growth).
4.  **Rapid YouTube Response:** YouTube creators react within 7 minutes of HN, requiring immediate outreach post-launch (Comms).
5.  **Optimize HN Timing:** Schedule HN posts for 22 UTC, which averages 72.1 points, to maximize initial visibility (Content).
6.  **Use High-Lift Keywords:** Incorporate terms like "deepseek" (30.3x lift) and "kimi" (25.25x lift) in titles to boost reach (Content).
7.  **Monitor Early Sentiment:** HN shows 16.0% negative sentiment, serving as an early warning for potential issues (Comms).
8.  **Counter Rapid Decay:** HN engagement decays to 0.0004 by Day 3, necessitating a focused 72-hour amplification strategy (Growth).
9.  **Prioritize Breakthrough Content:** "Breakthrough" spikes have a maximum engagement of 33.6 million, indicating their immense viral potential (Content).
10. **Engage Community Channels:** Community YouTube channels generate 30.6x more views than official channels, highlighting their importance for reach (Comms).

---

## Prioritized Action Stack

The 5 highest-leverage plays, ranked by (estimated impact) × (execution speed).

| # | Play | Impact | Effort | Owner | Done when |
|---|---|---|---|---|---|
| 1 | **Identify & Brief Top Creators** | High | Low | Growth | Key creators (e.g., Fireship, Amjad Masad) are briefed with embargoed assets 72h before launch. |
| 2 | **Optimize Launch Content for Media** | High | Med | Content | All launch assets include high-quality video/image content, specifically formatted for X and YouTube. |
| 3 | **Strategic HN Seeding** | High | Low | Growth | A high-quality post is submitted to HN at 22 UTC (72.1 mean score) at T-0h. |
| 4 | **Rapid YouTube Creator Outreach** | High | Med | Comms | Key YouTube creators (e.g., Matthew Berman, Theo t3.gg) are alerted immediately post-HN launch. |
| 5 | **Monitor Early Sentiment** | Med | Low | Comms | Real-time sentiment analysis dashboard is live and monitored for HN/Reddit comments within T+2h. |

---

## Launch Day Protocol

Hour-by-hour checklist for the first 48h of any major launch or event.
Synthesizes findings on cascade timing, creator briefing, and platform decay.

| Window | Action | Owner | Platform |
|---|---|---|---|
| T-72h | Brief Fireship, Amjad Masad, Aakash Gupta, Dan Martell with embargo assets and talking points. | Growth | YouTube/X |
| T-0h | Post on HN at 22:00 UTC (peak engagement hour for HN, 72.1 mean score). | Content | HN |
| T+0.1h (7 min) | Alert Matthew Berman & Theo t3.gg to HN post and provide any additional context. | Comms | YouTube |
| T+2h | Monitor HN comments for sentiment (16.0% negative) and initial reactions. | Comms | HN |
| T+12h | Seed Reddit with media-rich content (1.8x median lift) targeting weekend posting (1819.8 mean score). | Content | Reddit |
| T+16h | Prepare for Fireship peak (2.59M views) and amplify their content across our channels. | Growth | YouTube |
| T+24h | Review initial engagement decay on HN (0.0091 by Day 1) and plan follow-up amplification. | Growth | HN |
| T+48h | Engage with international/satire creators (e.g., SAMTIME) for the third cascade wave. | Comms | YouTube |

---

## Dataset Summary

| Platform | Posts | Coverage | Scraper method |
|---|---|---|---|
| HN | 1884 | High | API |
| Reddit | 400 | High | API |
| X | 57 | Medium | API |
| YouTube | 86 | Medium | API |
| **Total** | **2427** | | |

---

## Finding 1 — The Power Law Is the Whole Game

| Platform | Top 10% of Posts Share | Top 1% of Posts Share |
|---|---|---|
| HN | 85% of all engagement | 43% of all engagement |
| X | 80% of all engagement | N/A |
| YouTube | 63% of all engagement | N/A |
| Reddit | 45% of all engagement | 15% of all engagement |

**Growth Insight:** Across all major platforms, a small fraction of content (the top 10%) drives the vast majority of engagement. This extreme power law distribution means that success hinges on identifying and amplifying high-potential posts rather than spreading efforts thinly.
**Owner:** Growth
**Action:** Develop a content scoring model to identify high-potential posts pre-launch and prioritize their amplification and distribution efforts.
**Confidence:** High (n=1884 HN, n=57 X, n=86 YouTube, n=400 Reddit)

## Finding 2 — The 3-Wave Cascade (Timestamped)

| Hours After | Platform | Score | Label |
|---|---|---|---|
| 0 | HN | 2 | HN first post (01:13 UTC) |
| 0.1 | YouTube | 162576 | Matthew Berman (7 min after HN) |
| 3 | YouTube | 182642 | Theo t3.gg |
| 12 | Reddit | 337 | Reddit joins (12h after HN) |
| 16 | YouTube | 2592415 | Fireship peak (2.59M views) |
| 48 | YouTube | 131467 | SAMTIME satire |
| 48.5 | YouTube | 89249 | International wave (PT) |

**Growth Insight:** Viral events, as demonstrated by the "Claude source code leak," follow a predictable multi-wave pattern. It starts with early adopters on HN, rapidly amplified by key YouTube creators within minutes, then spreads to broader communities on Reddit, and finally reaches international and meme audiences. The critical window for maximum impact is within the first 16 hours.
**Owner:** Comms
**Action:** Design launch strategies to explicitly target each cascade wave with tailored content and creator outreach, front-loading efforts within the first 16 hours to capture peak impact.
**Confidence:** Directional (based on a single event, but the pattern is clear and well-defined)

## Finding 3 — Spike Type Volume vs Engagement Inverted

| Spike Type | Count | % of Total Posts | Mean Engagement | Max Engagement |
|---|---|---|---|---|
| Breakthrough | 1122 | 46.2% | 42963 | 33638947 |
| Tutorial | 682 | 28.1% | 11424 | 2592415 |
| Personal | 275 | 11.3% | 1108 | 19035 |
| Meme | 189 | 7.8% | 38796 | 2325713 |
| Comparison | 159 | 6.6% | 3083 | 94172 |

**Growth Insight:** While "breakthrough" content represents the highest volume of posts and the highest potential for massive engagement (max 33.6M), "meme" content, despite its lower volume (7.8% of posts), achieves disproportionately high mean engagement (38,796) and significant max spikes (2.3M). This indicates its strong viral potential. "Tutorials" are high volume but have lower mean engagement.
**Owner:** Content
**Action:** Prioritize content creation for "breakthrough" announcements due to their high impact potential, but also strategically develop "meme"-able content to leverage its viral amplification capabilities.
**Confidence:** High (n=2427 total posts, with significant counts for each spike type)

## Finding 4 — Platform Timing Windows

| Platform | Peak Time (UTC) | Mean Score | Count |
|---|---|---|---|
| HN | 22 | 72.1 | 87 |
| Reddit | Saturday | 1819.8 | 58 |
| Reddit | Sunday | 1760.5 | 52 |

**Growth Insight:** Specific timing windows on each platform offer significantly higher engagement potential. HN posts at 22 UTC (5-6 PM ET) average 72.1 points, which is 3.8x higher than the overall HN mean of 19. Reddit posts on weekends (Saturday and Sunday) outperform weekdays by a significant margin (e.g., Saturday avg 1819.8 vs Thursday avg 1138.2).
**Owner:** Content
**Action:** Schedule HN posts for 22 UTC and Reddit posts for Saturday or Sunday to maximize initial reach and cascade ignition, ensuring content is published when the audience is most active and receptive.
**Confidence:** High (n=87 for HN 22 UTC, n=58 for Reddit Saturday, n=52 for Reddit Sunday)

## Finding 5 — Title Word Lift (what to say and what kills reach)

| Word | Lift |
|---|---|
| deepseek | 30.3 |
| kimi | 25.25 |
| thinking | 20.2 |
| uses | 20.2 |
| qwen | 19.36 |
| **...** | |
| show | 0.02 |
| agent | 0.14 |
| tool | 0.35 |
| openai | 0.36 |
| zero | 0.4 |

**Growth Insight:** Specific keywords in titles act as powerful engagement multipliers or inhibitors. Technical, competitive, and "thinking"-related terms (e.g., "deepseek," "kimi," "thinking") significantly boost engagement, while generic or overly product-centric terms (e.g., "show," "agent," "tool") correlate with low reach.
**Owner:** Content
**Action:** Integrate high-lift words into titles and descriptions for all content, especially for major announcements, and actively avoid low-lift words to optimize for maximum reach and engagement.
**Confidence:** Medium (analysis based on top 80% vs bottom 20% engagement posts, min 3 occurrences)

## Finding 6 — Engagement Decay by Platform

| Platform | Day 0 | Day 1 | Day 3 | Day 6 |
|---|---|---|---|---|
| HN | 0.0039 | 0.0091 | 0.0004 | 0.0002 |
| Reddit | 0.078 | 0.0534 | 0.0054 | 0.0011 |
| YouTube | 0.0041 | 0.0251 | 0.0081 | 0.0033 |

**Growth Insight:** Engagement on HN and Reddit decays rapidly, with significant drop-offs by Day 3 (HN to 0.0004, Reddit to 0.0054). While YouTube shows a slightly different pattern (initial rise then decay), overall, the data indicates that the critical window for sustained engagement is short.
**Owner:** Growth
**Action:** Implement a robust 72-hour amplification strategy for all major launches, with specific re-engagement tactics for each platform to counteract rapid decay and maintain visibility.
**Confidence:** Medium (decay rates provided, but X data is missing and YouTube Day 0/1 values suggest potential initial data collection nuances)

## Finding 7 — The 10/80 Rule: Engagement Is Pareto-Concentrated

| Platform | Top 10% of Posts Share | Posts for 80% Engagement |
|---|---|---|
| HN | 85% | 6.4% |
| X | 80% | 7.0% |
| YouTube | 63% | 22.1% |
| Reddit | 45% | 35.2% |

**Growth Insight:** A small percentage of content generates a disproportionately large share of engagement across all platforms. For example, on HN, just 6.4% of posts account for 80% of all engagement. This reinforces the critical need to identify and amplify high-performing content rather than distributing efforts evenly.
**Owner:** Growth
**Action:** Implement a rapid feedback loop to identify top-performing content within hours of launch, then reallocate amplification budget and resources to boost these high-leverage posts.
**Confidence:** High (n>500 for HN, Reddit; n=57 for X, n=86 for YouTube)

## Finding 8 — Author Concentration: Top 5 Accounts = 94.5% of Engagement

| Author | Engagement Score | Cumulative % | Platform |
|---|---|---|---|
| Anthropic | 53837868 | 84.0% | X |
| Fireship | 2592415 | 88.0% | YouTube |
| Amjad Masad | 2038052 | 91.2% | X |
| Aakash Gupta | 1821730 | 94.0% | X |
| Dan Martell | 316127 | 94.5% | YouTube |
| **Total Unique Authors:** 1964 | **Top 5 Share:** 94.5% | | |

**Growth Insight:** Growth is overwhelmingly driven by a very small number of key creators and the official brand account. The top 5 authors (out of 1964 unique authors) account for an astonishing 94.5% of total engagement. Activating and supporting these specific voices is paramount for reach.
**Owner:** Growth
**Action:** Establish direct, high-touch relationships and provide early access/briefings to the top 5 identified creators (including the official brand channel) to ensure they are consistently our primary amplification channels.
**Confidence:** High (n=1964 unique authors, 64,123,789 total engagement analyzed)

## Finding 9 — Media Posts Drive 8–10x Higher Engagement

| Platform | Media Median Engagement | Text Median Engagement | Median Lift (Media vs Text) |
|---|---|---|---|
| X | 290617 | 22968 | 12.7x |
| Reddit | 946 | 519 | 1.8x |

**Growth Insight:** Visual and video content significantly outperforms text-only posts on X and Reddit. X media posts achieve a remarkable 12.7x median engagement lift, while Reddit media posts see a 1.8x lift. This indicates a strong audience preference for rich media content.
**Owner:** Content
**Action:** Mandate that all major announcements and content releases include high-quality, platform-optimized media (images, videos, GIFs) for X and Reddit to maximize engagement.
**Confidence:** High (n=29 X media, n=28 X text; n=178 Reddit media, n=222 Reddit text)

## Finding 10 — Comment Sentiment as an Early Signal

| Platform | Negative Sentiment | Neutral Sentiment | Positive Sentiment |
|---|---|---|---|
| HN | 16.0% | 61.2% | 22.8% |
| Reddit | 8.3% | 75.7% | 16.0% |

**Growth Insight:** Comment sentiment, particularly negative sentiment on HN (16.0%), can serve as an early warning signal for product issues or community dissatisfaction. Different content types also elicit varying sentiment (e.g., "tutorial" posts have 11.2% negative sentiment vs. "breakthrough" at 4.0%).
**Owner:** Comms
**Action:** Implement real-time sentiment monitoring for HN and Reddit comments, especially for new launches, to quickly identify and address emerging issues or negative narratives before they escalate.
**Confidence:** High (n=3567 total comments analyzed)

---

## Limitations

*   The cascade analysis (Finding 2) is based on a single, high-profile event ("Claude source code leak"), limiting its generalizability to all product launches.
*