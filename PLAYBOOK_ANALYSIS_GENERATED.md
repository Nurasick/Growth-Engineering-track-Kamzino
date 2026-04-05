<!-- Generated: 2026-04-05 05:03 UTC -->
<!-- Model: gemini/models/gemini-2.5-flash -->
<!-- Source data: 2427 classified posts — hn: 1884, reddit: 400, x: 57, youtube: 86 -->
<!-- Audit trail: data/processed/analysis_metrics.json -->
<!-- Generation: 2-pass (pass1: skeleton+causality, pass2: findings+playbooks) -->

**Playbook type:** Hybrid — This indicates that growth strategy must balance rapid response to cascading events with sustained engagement of key creators and community amplifiers.

## SECTION 2 — TL;DR — 10 Rules (read this first)

1.  HN posts between 22:00 UTC and 01:00 UTC achieve significantly higher average scores (e.g., 72.1 at 22h UTC, n=87) compared to other hours. (Content)
2.  Community YouTube channels generated 30.6x more views (6,012,847 total community views vs 196,616 official views, n=86) than official channels. (Growth)
3.  X posts with media content have a 12.7x higher median engagement (290,617 vs 22,968 for text, n=57) than text-only posts. (Content)
4.  Reddit engagement is highest on weekends, with Saturday posts averaging 1819.8 and Sunday posts averaging 1760.5 (n=58 and n=52 respectively), compared to weekdays. (Comms)
5.  "Breakthrough" spike types account for 46.2% of total posts (n=1122) and have the highest maximum engagement at 33,638,947. (Content)
6.  On Hacker News, 6.4% of posts drive 80% of engagement (n=1884), indicating extreme concentration of impact. (Growth)
7.  Key YouTube creators like Matthew Berman reacted to HN ignition within 0.1 hours (n=1, single event), indicating a need for pre-briefing or immediate outreach. (Comms)
8.  The top 1 author on X (Anthropic) accounts for 84.0% of total engagement (n=1964 total unique authors), highlighting the importance of high-reach accounts. (Growth)
9.  Reddit posts with media content achieve a 1.8x higher median engagement (946 vs 519 for text, n=400) compared to text-only posts. (Content)
10. The maximum impact window for a cascade event, like the Claude source code leak, is approximately 16 hours after initial HN ignition (n=1, single event). (Growth)

## SECTION 3 — Prioritized Action Stack

| # | Play | Why now | Impact | Effort | Owner | Done when |
|---|---|---|---|---|---|---|
| 1 | Establish a "Rapid Response Creator Briefing" program for top 5 YouTube channels. | F7 — Rapid YouTube Reaction (0.1h lag) and F2 — YouTube Creator Leverage (30.6x views). | High | Medium | Comms | Top 5 YouTube creators (Fireship, Dan Martell, Theo, Matthew Berman) have signed NDAs and received a pre-briefing kit. |
| 2 | Optimize HN launch timing to 22:00-01:00 UTC. | F1 — HN Timing (72.1 mean score at 22h UTC). | High | Low | Content | All HN submissions are scheduled for 22:00-01:00 UTC unless critical real-time event. |
| 3 | Develop a "Media-First" content strategy for X and Reddit. | F3 — X Media Impact (12.7x median lift) and F9 — Reddit Media Lift (1.8x median lift). | Medium | Medium | Content | 80% of X and Reddit posts include rich media (images, videos, GIFs). |
| 4 | Implement a "Breakthrough Content" pipeline. | F5 — Breakthrough Content Dominance (46.2% of posts, highest max engagement). | High | High | Engineering | A dedicated team is formed to identify and productize breakthrough features. |
| 5 | Create a "Weekend Reddit Amplification" schedule. | F4 — Reddit Weekend Boost (Saturday/Sunday mean scores 1819.8/1760.5). | Medium | Low | Comms | Reddit posts are prioritized for Saturday/Sunday publication. |

## SECTION 4 — Launch Day Protocol (48h window)

| Window | Action | Platform | Owner | Finding |
|---|---|---|---|---|
| T-72h | Pre-brief top 5 YouTube creators with embargoed content and key messaging. | YouTube | Comms | F7 — Rapid YouTube Reaction (n=1, single event) |
| T-24h | Draft HN post, X thread, and initial Reddit post copy, including rich media assets. | HN, X, Reddit | Content | F3 — X Media Impact (n=57), F9 — Reddit Media Lift (n=400) |
| T-0h | Publish HN post at 22:00 UTC. | HN | Content | F1 — HN Timing (n=87) |
| T+0.1h | Monitor Matthew Berman and other pre-briefed YouTube creators for initial coverage. | YouTube | Comms | F7 — Rapid YouTube Reaction (n=1, single event) |
| T+1h | Cross-post HN link to relevant subreddits (e.g., r/programming, r/machinelearning) if HN score > 50. | Reddit | Growth | F1 — HN Timing (n=87) |
| T+2h | Draft follow-up X posts, incorporating early HN/YouTube sentiment. | X | Content | F3 — X Media Impact (n=57) |
| T+3h | Monitor Theo t3.gg and other mid-tier YouTube creators for organic reaction. | YouTube | Comms | Cascade: Theo t3.gg (n=1, single event) |
| T+6h | Prepare a summary of initial HN/YouTube/X sentiment for internal stakeholders. | All | Growth | F10 — Cascade Window (n=1, single event) |
| T+12h | Publish Reddit post (if not already done via cross-post) with media, targeting weekend if possible. | Reddit | Content | Cascade: Reddit joins (n=1, single event), F4 — Reddit Weekend Boost (n=58, n=52) |
| T+16h | Identify and amplify top-performing YouTube content (e.g., Fireship peak). | YouTube | Growth | Cascade: Fireship peak (n=1, single event) |
| T+24h | Review all platform engagement metrics; identify top-performing content types (e.g., "breakthrough"). | All | Growth | F5 — Breakthrough Content Dominance (n=1122) |
| T+36h | Plan for international/meme content amplification based on early signals. | YouTube, X | Comms | Cascade: SAMTIME satire, International wave (n=1, single event) |
| T+48h | Conduct a post-mortem analysis of cascade performance and identify key learnings. | All | Growth | F10 — Cascade Window (n=1, single event) |

## SECTION 5 — Dataset Summary

| Platform | Posts | Coverage | Method |
|---|---|---|---|
| hn | 1884 | Hacker News posts and comments | Scraped |
| reddit | 400 | Reddit posts and comments | Scraped |
| x | 57 | X/Twitter posts | Scraped |
| youtube | 86 | YouTube videos and views | Scraped |

## SECTION 6 — Cross-Platform Causality Analysis

**A. Does HN ignition reliably pull Reddit?**
*   **HN→Reddit lag:** For the "Claude source code leak" event, Reddit joined 12 hours after the initial HN post (n=1, single event). This is the only cascade narrative provided in the dataset with explicit HN→Reddit timing.
*   **Lag for scandal/leak vs opinion/narrative:** The dataset only provides one cascade event ("Claude source code leak"), which is a scandal/leak type. Therefore, it is not possible to compare lag times between different content types.
*   **HN score threshold for Reddit activation:** The initial HN post for the "Claude source code leak" had a score of 2. Reddit joined 12 hours later, but the dataset does not provide the HN score at the 12-hour mark, nor does it provide other cascade events to establish a threshold.
*   **Conclusion:** The data suggests but does not confirm that HN ignition can pull Reddit, with a 12-hour lag observed for a scandal/leak. A reliable HN score threshold for Reddit activation is not available in the dataset. (Confidence: Directional, n=1 for cascade timing)

**B. Does HN ignition pull YouTube — and through which pathway?**
*   **Pathway 1 (Pre-briefed creators):** Matthew Berman posted on YouTube 0.1 hours (7 minutes) after the HN post (n=1, single event). This very short lag strongly suggests pre-briefing or extremely rapid response. Theo t3.gg posted 3 hours after HN (n=1, single event), which could also fall into this category or be a very early organic reaction.
*   **Pathway 2 (Organic YouTube reaction):** Fireship peaked 16 hours after HN (2,592,415 views, n=1, single event), and SAMTIME satire and International wave videos appeared 48 hours and 48.5 hours after HN, respectively (n=1, single event). These longer lags are consistent with organic YouTube reaction, likely driven by the initial HN traction and subsequent early YouTube coverage.
*   **Reliance on briefing vs. organic:** The data suggests that for immediate impact and early amplification (within 0.1-3 hours), briefing key creators is essential. For broader, larger-scale reach (e.g., Fireship's 2,592,415 views at 16 hours), organic cascade is a powerful amplifier that follows initial ignition. A growth team should rely on briefing for *initial, controlled narrative push* and *simultaneously prepare to amplify organic cascades* once they gain traction. (Confidence: Directional, n=1 for cascade timing)

**C. Is Reddit always downstream of HN?**
*   **Origin of cascade narratives:** The "Claude source code leak" cascade explicitly states "HN first post (01:13 UTC)" and "Reddit joins (12h after HN)" (n=1, single event). The dataset only provides this single cascade narrative.
*   **Any start on Reddit?** Based on the provided data, no cascade narrative is shown to originate on Reddit.
*   **Strategic implication:** The data suggests but does not confirm that Reddit is always downstream of HN, acting as an amplifier rather than an ignition source. If this pattern holds, growth effort should focus on igniting narratives on HN (optimizing timing, content type) and then actively seeding and amplifying those narratives on Reddit once HN traction is established, rather than attempting to initiate a cascade directly on Reddit. Reddit's median engagement (688, n=400) is significantly lower than X (54128, n=57) or YouTube (22709, n=86), further supporting its role as an amplifier rather than a primary ignition source for broad reach. (Confidence: Directional, n=1 for cascade origin; Medium, n=400 for Reddit engagement)

**D. Does HN score determine organic cascade reach?**
*   **Argument:** The data suggests but does not confirm that HN score acts as a social proof signal for organic YouTube creators.
*   **Support:** The "Claude source code leak" cascade shows the initial HN post with a score of 2. However, the first YouTube reaction (Matthew Berman) occurred only 0.1 hours later (n=1, single event), too quickly for the HN score to have significantly accumulated or served as a strong social proof signal. This suggests Matthew Berman was likely pre-briefed or reacted to the *existence* of the leak, not its HN score.
*   **Counter-argument/Nuance:** The larger organic YouTube reactions, such as Fireship peaking at 16 hours (2,592,415 views, n=1, single event), occur much later. By this time, the HN post would have had 16 hours to accumulate a significant score, potentially serving as a social proof signal for these later, larger creators. The data does not provide the HN score at 16 hours, making a direct causal link difficult to establish. However, the sequence (HN ignition → early YouTube → Reddit joins → *peak* YouTube) is consistent with later-stage organic creators using earlier platform traction (including HN's growing score) as a signal.
*   **Conclusion:** While early YouTube reactions (within 3 hours) likely don't rely on HN score as social proof, the data suggests that later, larger organic YouTube coverage (10h+ lag) *could* be influenced by the accumulated HN score, though this is not directly confirmed by the available figures. (Confidence: Directional, n=1 for cascade timing)

**E. Do simultaneous narratives compound or cannibalize reach?**
*   Not available in dataset. The DATA BLOCK does not contain "monthly view data" or information about "periods where multiple narratives overlap".

**F. Cascade speed synthesis table**

| Narrative | HN→Reddit lag | HN→X lag | HN→YouTube lag | Platforms | Speed |
|---|---|---|---|---|---|
| Claude source code leak | 12h | not available in dataset | 0.1h (Matthew Berman), 3h (Theo t3.gg), 16h (Fireship peak), 48h (SAMTIME), 48.5h (International) | HN, YouTube, Reddit | Fast (initial YouTube), Medium (Reddit), Slow (later YouTube) |

*   **Scandal vs. opinion cascade speed:** The dataset only provides one cascade narrative, "Claude source code leak," which is a scandal/leak. Therefore, it is not possible to compare its cascade speed to opinion content.
*   **Different response playbooks:** The data suggests that different response playbooks are necessary for different cascade speeds.
    *   **Fast cascades (e.g., HN→YouTube in 0.1h, n=1, single event):** Require pre-briefing of creators and immediate monitoring/amplification. The "max_impact_window_hours" of 16 hours (n=1, single event) for the leak also points to a need for rapid response.
    *   **Medium cascades (e.g., HN→Reddit in 12h, n=1, single event):** Allow for more structured content preparation and strategic timing (e.g., leveraging Reddit's weekend peak, n=58, n=52).
    *   **Slow cascades (e.g., HN→YouTube in 48h+ for satire/international, n=1, single event):** Indicate opportunities for sustained content creation, localization, and meme generation.
*   **Conclusion:** While direct comparison of scandal vs. opinion content speed is not possible, the observed multi-speed nature of the "Claude source code leak" cascade (0.1h to 48.5h lags) strongly suggests that a nuanced, multi-stage response playbook is critical. (Confidence: Directional, n=1 for cascade timing)

<!-- === PASS 2 START === -->

## Finding 1 — The Power Law Is the Whole Game

**Claim:** A small fraction of posts generate the vast majority of engagement across platforms, and these high-impact posts are critical for triggering cross-platform cascades.

| Platform | Posts for 80% Engagement | Total Posts (n) |
|---|---|---|
| HN | 6.4% | 1884 |
| X | 7.0% | 57 |
| YouTube | 22.1% | 86 |
| Reddit | 35.2% | 400 |

**Cross-platform link:** The "Claude source code leak" cascade (n=1, single event) started with an HN post (score 2) that then led to significant YouTube and Reddit engagement, suggesting that even a low-scoring HN post can ignite a cascade if it's a "breakthrough" type. The data suggests but does not confirm that high-impact posts (as indicated by power law distribution) are the ones that trigger cross-platform cascades.

**Growth Insight:** Focus resources on identifying and amplifying potential "breakthrough" content that can achieve outlier status, rather than optimizing for average performance.

**Strategy:**
1.  Implement a "Breakthrough Content Identification" protocol: If a new HN post (n=1) reaches a score of 50 within 1 hour of publication, immediately trigger a cross-platform amplification sequence on X and Reddit, using rich media.
2.  Allocate content promotion budget: Allocate 80% of content promotion budget to the top 10% of posts (n=not available in dataset for budget, but based on Pareto principle) identified by initial engagement velocity (e.g., X posts with >200,000 engagement within 4 hours, n=57).

**Owner:** Growth, Content
**Confidence:** Medium (n=1884, 400, 57, 86 for Pareto; Directional for cascade link, n=1)

## Finding 2 — The 3-Wave Cascade (Timestamped)

**Claim:** Cross-platform virality occurs in distinct waves, with pre-briefed creators initiating the first wave, followed by organic amplification and international spread.

| Hours After HN Post | Platform | Score/Views | Label |
|---|---|---|---|
| 0 | HN | 2 | HN first post (01:13 UTC) |
| 0.1 | YouTube | 162576 | Matthew Berman (7 min after HN) |
| 3 | YouTube | 182642 | Theo t3.gg |
| 12 | Reddit | 337 | Reddit joins (12h after HN) |
| 16 | YouTube | 2592415 | Fireship peak (2.59M views) |
| 48 | YouTube | 131467 | SAMTIME satire |
| 48.5 | YouTube | 89249 | International wave (PT) |

**Cross-platform link:** HN ignition (0 hours) directly preceded and likely triggered the first YouTube wave (0.1h, 3h), which then preceded Reddit joining (12h) and the peak organic YouTube amplification (16h), followed by later international/meme content (48h, 48.5h). This is a causal cascade observed for a single event.

**Growth Insight:** A multi-stage amplification strategy is required, distinguishing between rapid, pre-planned creator engagement and sustained, organic amplification.

**Strategy:**
1.  Implement a "Wave 1 Creator Briefing" protocol: For any major product announcement or leak, pre-brief top-tier YouTube creators (e.g., Matthew Berman, Theo t3.gg, n=2, single event) with embargoed content 72 hours prior to HN launch (T-72h) to ensure 0.1-3 hour YouTube reaction.
2.  Establish a "Wave 2 Amplification" trigger: If an HN post (n=1) achieves a score >50 within 1 hour of publication, immediately cross-post to Reddit (n=1, single event for timing) and identify early organic YouTube content for amplification (e.g., via X retweets) within 12-16 hours.
3.  Develop a "Wave 3 Localization & Meme" pipeline: 48 hours after initial HN ignition (n=1, single event), task the content team with identifying and supporting international or satirical content (e.g., SAMTIME, n=1, single event) based on early sentiment.

**Owner:** Comms, Growth, Content
**Confidence:** Directional (n=1 for cascade event and timings)

## Finding 3 — Spike Type Volume vs Engagement Inverted

**Claim:** "Breakthrough" content, while not the most frequent, generates the highest maximum engagement, whereas "tutorial" content is common but has a lower engagement ceiling.

| Spike Type | % of Total Posts | Max Engagement | Median Engagement | Count (n) |
|---|---|---|---|---|
| breakthrough | 46.2% | 33638947 | 4 | 1122 |
| tutorial | 28.1% | 2592415 | 2 | 682 |
| personal | 11.3% | 19035 | 442 | 275 |
| meme | 7.8% | 2325713 | 4 | 189 |
| comparison | 6.6% | 94172 | 12 | 159 |

**Cross-platform link:** The "Claude source code leak" (n=1, single event) which triggered a multi-platform cascade (HN, YouTube, Reddit) aligns with the characteristics of a "breakthrough" type event, given its high impact. The Fireship peak (2,592,415 views, n=1, single event) was a "tutorial" type, showing that tutorials can also achieve high engagement, but the data suggests but does not confirm that "breakthrough" types have a higher ceiling for max engagement.

**Growth Insight:** Prioritize the creation and identification of "breakthrough" content for maximum impact, while also maintaining a steady stream of "tutorial" content for sustained, lower-ceiling engagement.

**Strategy:**
1.  Establish a "Breakthrough Content" sprint team: Dedicate resources to developing features that can generate "breakthrough" content (n=1122 posts of this type), aiming for 1 major launch per quarter.
2.  Develop a "Tutorial Content" pipeline: Maintain a continuous flow of "tutorial" content (n=682 posts of this type) for YouTube and Reddit, ensuring a minimum of 2 new tutorials per week to capture sustained interest.
3.  Map spike types to platforms: Prioritize "breakthrough" content for HN ignition (n=1122) and subsequent X amplification (n=57), and "tutorial" content for YouTube (n=86) and Reddit (n=400) for sustained engagement.

**Owner:** Engineering, Content
**Confidence:** Medium (n=2427 total posts for spike types; Directional for cascade link, n=1)

## Finding 4 — Platform Timing Windows

**Claim:** Optimal posting times vary significantly by platform, and strategic sequencing can maximize cross-platform handoff.

| Platform | Peak Timing | Mean Engagement | Count (n) |
|---|---|---|---|
| HN | 22:00 UTC | 72.1 | 87 |
| Reddit | Saturday | 1819.8 | 58 |
| Reddit | Sunday | 1760.5 | 52 |

**Cross-platform link:** The "Claude source code leak" cascade (n=1, single event) shows Reddit joining 12 hours after HN ignition. To maximize the HN→Reddit handoff, an HN post at 22:00 UTC (mean 72.1, n=87) on a Friday would allow Reddit to pick up the narrative on Saturday (mean 1819.8, n=58) or Sunday (mean 1760.5, n=52), leveraging both platform peaks.

**Growth Insight:** Align content publication schedules with platform-specific peak engagement windows to maximize initial traction and facilitate cross-platform narrative transfer.

**Strategy:**
1.  Implement "HN Prime Time" publishing: Schedule all HN posts (n=1884) for publication between 22:00 UTC and 01:00 UTC, prioritizing 22:00 UTC (mean 72.1, n=87) for major announcements.
2.  Establish "Weekend Reddit Amplification": If an HN post (n=1) achieves a score >50 within 4 hours, cross-post to relevant subreddits (n=400) on Saturday or Sunday to leverage the higher mean engagement (1819.8 and 1760.5 respectively, n=58, n=52).
3.  Optimize HN-Reddit Handoff: For critical narratives, aim to publish on HN on Friday at 22:00 UTC (n=87 for HN timing) to allow for 12 hours of HN traction before seeding on Reddit on Saturday (n=58 for Reddit timing), ensuring the narrative hits Reddit's peak weekend engagement.

**Owner:** Content, Growth
**Confidence:** Medium (n=87 for HN peak, n=58, 52 for Reddit peak; Directional for cascade timing, n=1)

## Finding 5 — Title Word Lift

**Claim:** Specific keywords in titles significantly increase engagement, clustering around themes of advanced AI capabilities and competitive comparisons.

| Top Lift Words | Lift Score | Bottom Lift Words | Lift Score |
|---|---|---|---|
| deepseek | 30.3 | show | 0.02 |
| kimi | 25.25 | agent | 0.14 |
| thinking | 20.2 | tool | 0.35 |
| uses | 20.2 | openai | 0.36 |
| qwen | 19.36 | zero | 0.4 |
| hard | 17.67 | | |
| plus | 17.67 | | |
| told | 15.15 | | |
| benchmarks | 15.15 | | |
| coder | 15.15 | | |

**Cross-platform link:** The data suggests but does not confirm that high-lift HN titles act as a social proof signal for organic YouTube pickup. The "Claude source code leak" (n=1, single event) was a "breakthrough" type event, and the high-lift words like "deepseek," "kimi," "qwen," "benchmarks," and "coder" suggest a theme of advanced AI models and competitive performance. This theme likely resonates with organic YouTube creators like Fireship (n=1, single event) who cover technical breakthroughs.

**Growth Insight:** Craft titles using high-lift keywords that signal advanced technical capabilities and competitive relevance to capture attention and act as a signal for broader amplification.

**Strategy:**
1.  Implement a "High-Lift Keyword Mandate": For all HN post titles (n=1884) and YouTube video titles (n=86), include at least one word from the top 10 lift words list (e.g., "deepseek," "kimi," "benchmarks"), especially for "breakthrough" content.
2.  Conduct A/B testing on titles: For X posts (n=57), A/B test titles incorporating high-lift words against control titles to confirm their impact on engagement (e.g., comparing "Deepseek Coder Benchmarks" vs. "New AI Tool").
3.  Avoid low-lift words: Prohibit the use of bottom-lift words like "show," "agent," "tool," "openai," and "zero" in primary titles for HN (n=1884) and X (n=57) to prevent dampening engagement.

**Owner:** Content
**Confidence:** Medium (n=not available in dataset for specific word counts, but method based on top 80% vs bottom 20% engagement posts, min 3 occurrences; Directional for cascade link, n=1)

## Finding 6 — The Sustained Controversy or Halo Effect

**Claim:** Not available in dataset. The DATA BLOCK does not contain "controversy/event timeline data" or "multi-week event cluster" information to assess how sustained controversy elevates baseline engagement.

**Data:** Not available in dataset.

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data.

**Growth Insight:** Not available in dataset.

**Strategy:** Not available in dataset.

**Owner:** Not available in dataset.
**Confidence:** Not available in dataset.

## Finding 7 — Community Creators vs Official Channel

**Claim:** Community YouTube channels generate significantly more views than official channels, highlighting the importance of external amplification.

| Channel Type | Total Views | Count (n) |
|---|---|---|
| Community Channels | 6012847 | 86 |
| Official Channel (Anthropic) | 196616 | 1 (single channel) |
| Ratio (Community:Official) | 30.6x | |

**Cross-platform link:** Organic YouTube creators like Matthew Berman reacted to HN ignition within 0.1 hours (n=1, single event), suggesting they monitor HN as a coverage signal. The data suggests but does not confirm that HN traction influences organic YouTube creators to cover topics, leading to a significant community-driven view count.

**Growth Insight:** Prioritize building relationships with and enabling community creators over solely relying on official channels for broad reach on YouTube.

**Strategy:**
1.  Establish a "Community Creator Partnership Program": Identify and onboard the top 5 community YouTube channels (e.g., Fireship, Dan Martell, Theo t3.gg, Matthew Berman, n=4 listed) with early access, briefings, and content support to leverage their 30.6x higher view potential.
2.  Shift YouTube content budget: Reallocate 80% of the YouTube content creation budget from official channels to supporting community creators (e.g., through sponsorships, content grants, n=not available in dataset for budget figures) to maximize reach.
3.  Monitor HN for creator signals: Growth team to monitor HN (n=1884) for emerging topics and high-scoring posts (e.g., score >100) and proactively share relevant information with community creators to prompt coverage.

**Owner:** Comms, Growth
**Confidence:** Medium (n=86 for YouTube views, n=1 for official channel baseline; Directional for HN monitoring, n=1)

## Finding 8 — Engagement Decay by Platform

**Claim:** Different platforms exhibit distinct engagement decay rates, creating a strategic window for cross-platform content sequencing.

| Platform | Day 0 Decay Rate | Day 1 Decay Rate | Day 3 Decay Rate | Day 6 Decay Rate |
|---|---|---|---|---|
| HN | 0.0039 | 0.0091 | 0.0004 | 0.0002 |
| Reddit | 0.078 | 0.0534 | 0.0054 | 0.0011 |
| YouTube | 0.0041 | 0.0251 | 0.0081 | 0.0033 |

**Cross-platform link:** The "Claude source code leak" cascade shows Reddit joining 12 hours after HN (n=1, single event). HN's engagement decay is relatively slow from Day 0 to Day 1 (0.0039 to 0.0091, which is an increase, implying initial growth before decay), while Reddit's decay starts immediately (0.078 to 0.0534). This suggests that the optimal posting day for HN to Reddit handoff should occur while HN is still gaining traction or at its peak, before its decay significantly impacts visibility.

**Growth Insight:** Content should be strategically timed across platforms to leverage initial platform peaks and transfer momentum before engagement significantly decays on the originating platform.

**Strategy:**
1.  Implement a "HN-Reddit Handoff Window": Publish HN content (n=1884) at 22:00 UTC on Friday (mean 72.1, n=87) and plan for Reddit cross-posting (n=400) within 12-24 hours (e.g., Saturday at 22:00 UTC) to transfer momentum before HN's Day 3 decay (0.0004) becomes significant.
2.  Prioritize YouTube for sustained reach: Given YouTube's slower decay rate (Day 1: 0.0251, Day 3: 0.0081, Day 6: 0.0033, n=86), ensure high-quality video content is produced for topics that gain traction on HN/Reddit, as it offers longer-term engagement.
3.  Rapid X amplification: Use X (n=57) for immediate amplification (within 0-2 hours of HN post) to capture initial attention, as X engagement is high but likely decays rapidly (decay rates not available in dataset for X, but implied by median engagement of 54128 for n=57 vs HN mean of 19 for n=1884).

**Owner:** Content, Growth
**Confidence:** Directional (n=1 for cascade timing, n=not available in dataset for X decay, n=1884, 400, 86 for platform counts)

## Finding 9 — Competitor Attacks as Organic Growth Events

**Claim:** Not available in dataset. The DATA BLOCK does not contain "competitor-generated content data" or "Claude discourse spikes it caused" to assess competitor attacks as growth events.

**Data:** Not available in dataset.

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data.

**Growth Insight:** Not available in dataset.

**Strategy:** Not available in dataset.

**Owner:** Not available in dataset.
**Confidence:** Not available in dataset.

## Finding 10 — The Movement Naming Effect

**Claim:** Not available in dataset. The DATA BLOCK does not contain "data on a coined phrase (e.g., 'vibe coding')" or "compound cross-platform effect" information.

**Data:** Not available in dataset.

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data.

**Growth Insight:** Not available in dataset.

**Strategy:** Not available in dataset.

**Owner:** Not available in dataset.
**Confidence:** Not available in dataset.

## Finding 11 — The Inside Engineer Effect

**Claim:** Not available in dataset. The DATA BLOCK does not contain "data comparing an internal engineer's personal posting to the official account."

**Data:** Not available in dataset.

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data.

**Growth Insight:** Not available in dataset.

**Strategy:** Not available in dataset.

**Owner:** Not available in dataset.
**Confidence:** Not available in dataset.

## Finding 12 — Small Accounts and Viral Outliers

**Claim:** Not available in dataset. The DATA BLOCK does not contain "follower-count vs views data" or "outlier-to-median ratio" for small accounts.

**Data:** Not available in dataset.

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data.

**Growth Insight:** Not available in dataset.

**Strategy:** Not available in dataset.

**Owner:** Not available in dataset.
**Confidence:** Not available in dataset.

## Finding 13 — Competitor Community Outperforms Home Community

**Claim:** Not available in dataset. The DATA BLOCK does not contain "subreddit comparison data" or "competitor-community readers have higher purchase intent" information.

**Data:** Not available in dataset.

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data.

**Growth Insight:** Not available in dataset.

**Strategy:** Not available in dataset.

**Owner:** Not available in dataset.
**Confidence:** Not available in dataset.

## Finding 14 — The Switching Narrative as a Durable Cross-Platform Thread

**Claim:** Not available in dataset. The DATA BLOCK does not contain "cascade detector output" or "narrative clusters and spread patterns" to identify switching narratives.

**Data:** Not available in dataset.

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data.

**Growth Insight:** Not available in dataset.

**Strategy:** Not available in dataset.

**Owner:** Not available in dataset.
**Confidence:** Not available in dataset.

---

## Strategic Synthesis — Three Playbooks

### Playbook A — The Launch Playbook
*Use when: you control the timing.*

1.  **T-72h:** Pre-brief top 5 YouTube creators (n=4 listed, F7) with embargoed content and key messaging (F2). If creators confirm participation, proceed with HN launch. If not, adjust launch timing or prepare for delayed YouTube pickup.
2.  **T-24h:** Draft HN post, X thread, and initial Reddit post copy, including rich media assets (F3, F9 from Pass 1).
3.  **T-0h:** Publish HN post at 22:00 UTC (F4).
    *   If HN score < 50 at T+4h (F1, F4), then escalate to Growth for manual X amplification (F3) and re-evaluation of Reddit cross-post timing.
4.  **T+0.1h:** Monitor pre-briefed YouTube creators (e.g., Matthew Berman, n=1, single event) for initial coverage (F2, F7).
5.  **T+1h:** Cross-post HN link to relevant subreddits (n=400) if HN score > 50 (F4).
6.  **T+2h:** Draft follow-up X posts (n=57), incorporating early HN/YouTube sentiment (F3).
7.  **T+3h:** Monitor mid-tier YouTube creators (e.g., Theo t3.gg, n=1, single event) for organic reaction (F2).
8.  **T+6h:** Prepare a summary of initial HN/YouTube/X sentiment for internal stakeholders (F2).
9.  **T+12h:** Publish Reddit post (n=400) (if not already done via cross-post) with media (F9 from Pass 1), targeting weekend if possible (F4).
10. **T+16h:** Identify and amplify top-performing YouTube content (e.g., Fireship peak, n=1, single event) via X (F2, F7).
11. **T+24h:** Review all platform engagement metrics; identify top-performing content types (e.g., "breakthrough," F3).
12. **T+36h:** Plan for international/meme content amplification based on early signals (F2).
13. **T+48h:** Conduct a post-mortem analysis of cascade performance and identify key learnings (F2).
14. **Contingency:** If nothing is gaining traction (HN score < 20 at T+8h, n=1884 for HN posts) and no YouTube coverage (n=86) has emerged:
    *   Pause all further cross-platform amplification.
    *   Analyze HN comments (n=1884) for negative sentiment (HN negative 16.0%, n=not available in dataset for specific post) or lack of interest.
    *   Re-evaluate content framing and consider a new HN post with a revised title (F5) at the next optimal timing window (F4).

### Playbook B — The Rapid Response Playbook
*Use when: external event — competitor attack, controversy, or unplanned leak.*

1.  **First 30 min:**
    *   Assess origin platform: If HN (n=1884), check initial score (e.g., Claude source code leak started at score 2, n=1, single event). If X (n=57), check engagement (median 54128).
    *   Identify content type: Is it a "breakthrough" (n=1122) or "meme" (n=189) type event? (F3)
    *   Determine sentiment: Analyze initial comments (n=3567 total comments analyzed) for negative keywords (e.g., "bad", "wrong", "problem", negative 12.4% overall, F-sentiment from Pass 1).
2.  **First 2h:**
    *   If HN ignition (n=1, single event) with score > 50 (F1) and negative sentiment < 10% (n=not available in dataset for specific post, but using overall negative 12.4% as baseline, F-sentiment from Pass 1):
        *   Immediately brief pre-approved YouTube creators (F7) for rapid response (0.1h lag, F2).
        *   Draft an X response (n=57) with rich media (F3 from Pass 1) within 1 hour, focusing on clarification or positive reframing.
    *   If HN ignition (n=1, single event) with score < 50 (F1) or negative sentiment > 20% (n=not available in dataset for specific post, F-sentiment from Pass 1):
        *   Do not amplify on X or Reddit immediately. Monitor for 6 hours.
3.  **The "do not amplify" rule:** If an event's initial engagement (e.g., HN score < 20, n=1884) or reach (e.g., X engagement < 10,000, n=57) is below the median for its platform, and sentiment is predominantly negative (e.g., >20% negative comments, n=not available in dataset for specific post, F-sentiment from Pass 1), staying silent is correct to prevent further amplification.
4.  **T+12h to T+48h:**
    *   If the narrative gains traction (e.g., Fireship peak at 16h, n=1, single event):
        *   Prepare a detailed response for Reddit (n=400) to be posted during weekend peak (F4), addressing key community concerns.
        *   Engage with international community creators (F2) for localized content (48.5h lag, n=1, single event).
    *   If the narrative fades (e.g., HN score drops below 10, n=1884, and no YouTube coverage, n=86):
        *   Continue monitoring but do not actively engage or amplify.
        *   Prepare internal post-mortem.

### Playbook C — The Ambient Narrative Playbook
*Use when: no launch, no crisis — maintaining long-term cross-platform presence.*

1.  **Daily:**
    *   Monitor HN (n=1884) for emerging topics related to AI/tech (e.g., new "breakthrough" (n=1122) or "comparison" (n=159) posts) with scores > 20 (F1).
    *   Monitor X (n=57) for mentions of our product or competitors, especially from top authors (e.g., Anthropic, n=1, single author, 84.0% engagement, F-author concentration from Pass 1).
    *   Identify potential "tutorial" (n=682) content opportunities based on search trends or community questions on Reddit (n=400).
2.  **Weekly:**
    *   **Switching narrative seeding in competitor communities:** Not available in dataset (F14).
    *   Publish 2-3 "tutorial" (n=682) videos on YouTube (n=86) and cross-post to Reddit (n=400), ensuring titles use high-lift keywords (F5).
    *   Engage with community creators (F7) to discuss potential content ideas and provide early access to minor updates.
3.  **Monthly:**
    *   **Inside engineer posting support:** Not available in dataset (F11).
    *   **Naming event watch:** Not available in dataset (F10).
    *   Review overall sentiment across platforms (n=3567 total comments analyzed) to identify shifts (F-sentiment from Pass 1). If negative sentiment on HN (16.0%) or Reddit (8.3%) increases by >5% month-over-month, trigger a content strategy review.
4.  **Early warning:**
    *   **Specific signal that an attack narrative is starting to cascade:** Not available in dataset (F14).
    *   However, if an HN post (n=1884) related to our product or a competitor receives >100 score within 2 hours (F1) and has >20% negative comments (n=not available in dataset for specific post, F-sentiment from Pass 1), this indicates a potential rapid response scenario (Playbook B).
    *   If a YouTube video (n=86) from a top community creator (F7) gains >100,000 views within 6 hours and has >15% negative comments (n=not available in dataset for specific video, F-sentiment from Pass 1), this also signals a potential rapid response scenario.

---

## Limitations

| Limitation | Findings affected | Severity |
|---|---|---|
| Reliance on single cascade event for timing and causality | F2, F4, F8, Causality Analysis A, B, C, D, F (from Pass 1) | High |
| Absence of competitor-generated content and community data | F9, F13, Playbook B, Playbook C | High |
| Lack of data on sustained narratives, halo effects, and individual influencer impact | F6, F10, F11, F14, Playbook C | Medium |
| Limited X/Twitter post count (n=57) and absence of decay data | F3, F8, Playbook A, Playbook B, Playbook C | Medium |
| No granular sentiment data linked to specific posts or cascade triggers | Playbook A, Playbook B, Playbook C | Medium |
| Absence of follower count data for small accounts and viral outliers | F12 | Low |