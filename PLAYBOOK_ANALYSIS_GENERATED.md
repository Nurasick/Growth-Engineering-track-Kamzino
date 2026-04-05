<!-- Generated: 2026-04-05 05:23 UTC -->
<!-- Model: gemini/models/gemini-2.5-flash -->
<!-- Source data: 2177 classified posts — hn: 1884, reddit: 125, x: 82, youtube: 86 -->
<!-- Audit trail: data/processed/analysis_metrics.json -->
<!-- Generation: 2-pass (pass1: skeleton+causality, pass2: findings+playbooks) -->

**Playbook type:** Hybrid — Cascade and Creator-driven. This indicates that our growth strategy must focus on rapid, multi-platform content dissemination while heavily investing in key individual creators and community amplification.

## SECTION 2 — TL;DR — 10 Rules (read this first)

1.  Prioritize pre-briefing YouTube creators for rapid response, as demonstrated by Matthew Berman's 0.1-hour reaction to the HN post (Content).
2.  Target Hacker News posts between 19-23 UTC, as these hours average 35-49 points, significantly higher than other times (Growth).
3.  Design content for Reddit with media, as media posts on Reddit show an 8.1x median lift over text posts (Content).
4.  Empower top-tier community creators, given that the top 5 authors generated 96.5% of total engagement across platforms (Growth).
5.  Frame content as "breakthroughs," which account for 50.5% of total posts and drive significant engagement (Content).
6.  Schedule Reddit amplification for Sundays, which average 4344.0 engagement, outperforming other weekdays (Growth).
7.  Focus on "leaks" or "leaked" framing for high-impact content, as these words show a lift of 15.2 and 13.18 respectively (Content).
8.  Recognize that community accounts on X can generate substantial reach, contributing 0.8x the total engagement of the official account (Comms).
9.  Be prepared for rapid decay on Reddit, where day0 engagement decay is 0.0597 (Growth).
10. Monitor HN for negative sentiment, which stands at 16.0%, higher than Reddit's 8.2% (Comms).

## SECTION 3 — Prioritized Action Stack

| # | Play | Why now | Impact | Effort | Owner | Done when |
|---|---|---|---|---|---|---|
| 1 | Establish a "Rapid Response Creator Network" for YouTube. | F1 — cascade window: Matthew Berman reacted in 0.1 hours to HN. Fireship peaked at 16 hours with 2592415 views. | High | Medium | Growth | 5 Tier-1 YouTube creators identified and pre-briefed for next major announcement. |
| 2 | Develop a "Community Amplifier Program" for X and YouTube. | F4 — top 5 authors account for 96.5% of total engagement; community accounts on X generated 0.8x official engagement; YouTube community views are 30.6x official baseline. | High | Medium | Comms | Top 10 community authors on X and YouTube engaged with a clear content sharing protocol. |
| 3 | Mandate media-rich content for all Reddit and X posts. | F3 — Reddit media posts have 8.1x median lift; X media posts have 9.7x median lift. | Medium | Low | Content | All new Reddit and X posts include at least one image or video asset. |
| 4 | Optimize HN post timing for peak engagement. | F2 — HN posts between 19-23 UTC average 35-49 points. | Medium | Low | Growth | All HN submissions scheduled to publish between 19-23 UTC. |
| 5 | Integrate "breakthrough" and "leak" framing into content strategy. | F5 — "breakthrough" spike type accounts for 50.5% of posts; "leaks" word lift is 15.2. | High | Medium | Content | Content calendar for next quarter includes 3 "breakthrough" or "leak"-framed narratives. |

## SECTION 4 — Launch Day Protocol (48h window)

| Window | Action | Platform | Owner | Finding |
|---|---|---|---|---|
| T-72h | Identify and pre-brief 3-5 Tier-1 YouTube creators with embargoed content. | YouTube | Content | F1 — Matthew Berman reacted in 0.1h to HN post. |
| T-24h | Draft initial HN post, ensuring "breakthrough" framing. | HN | Content | F5 — "breakthrough" spike type is 50.5% of posts. |
| T-0h | Publish HN post at 01:13 UTC, targeting 19-23 UTC window for peak visibility. | HN | Growth | F2 — HN peak hours 19-23 UTC average 35-49 pts. |
| T+0.1h | Confirm pre-briefed YouTube creators have published their content. | YouTube | Comms | F1 — Matthew Berman published 0.1h after HN. |
| T+3h | Monitor HN score; if above 2, prepare Reddit amplification. | HN, Reddit | Growth | F1 — HN score 2 led to cascade, Reddit joined at 12h. |
| T+12h | Post media-rich content on Reddit, targeting relevant subreddits. | Reddit | Growth | F3 — Reddit joins 12h after HN; media posts have 8.1x median lift. |
| T+16h | Monitor YouTube for organic peaks (e.g., Fireship). Engage with top comments. | YouTube | Comms | F1 — Fireship peak at 16h with 2592415 views. |
| T+24h | Prepare follow-up content for X, incorporating media and engaging top community authors. | X | Content, Comms | F4 — Community accounts on X generated 0.8x official engagement; F3 — X media posts have 9.7x median lift. |
| T+48h | Evaluate initial cascade reach and prepare for meme/international content amplification. | YouTube, X | Growth | F1 — Meme/international wave at 48h+. |

## SECTION 5 — Dataset Summary

| Platform | Posts | Coverage | Method |
|---|---|---|---|
| HN | 1884 | Total engagement: 36054; Mean score: 19; Median score: 2 | Scraped intelligence dataset |
| Reddit | 125 | Total engagement: 305693; Mean score: 2445; Median score: 1050 | Scraped intelligence dataset |
| YouTube | 86 | Total engagement: 6012847; Mean score: 69916; Median score: 22709 | Scraped intelligence dataset |
| X | 82 | Total engagement: 110880028; Mean score: 1352195; Median score: 53868 | Scraped intelligence dataset |

## SECTION 6 — Cross-Platform Causality Analysis

**A. Does HN ignition reliably pull Reddit?**
For the "Claude source code leak" cascade narrative, Reddit joined 12 hours after the initial HN post. This is the only cascade narrative available in the dataset. The range of lags observed is 12 hours. The data suggests but does not confirm that lag is shorter for scandal/leak content compared to opinion/narrative content, as only one type of content (leak) is present in the cascade data. The initial HN score for the post that activated Reddit was 2. The dataset does not provide a HN score threshold above which Reddit activation appears near-certain. Platform-isolated: no cross-platform signal in this data to compare different content types or thresholds.

**B. Does HN ignition pull YouTube — and through which pathway?**
HN ignition pulls YouTube through two pathways:
1.  **Pre-briefed creators:** Matthew Berman reacted 0.1 hours after the HN post with an engagement score of 162576. Theo t3.gg reacted 3 hours after HN with 182642 engagement. This pathway demonstrates rapid, near-simultaneous content release.
2.  **Organic YouTube reaction:** Fireship peaked at 16 hours after HN with 2592415 engagement. A meme/international wave followed at 48 hours and 48.5 hours respectively. This pathway shows a delayed, organic amplification.
A growth team should rely on briefing for immediate impact and early narrative control (lag <2h), as seen with Matthew Berman. They should also prepare to support and amplify organic cascades (lag 10h+) once a story gains traction, as demonstrated by Fireship's peak at 16 hours.

**C. Is Reddit always downstream of HN?**
For the "Claude source code leak" cascade narrative, Reddit joined 12 hours after the initial HN post. The weekly platform correlation between HN and Reddit is 0.908, which is a strong positive correlation. This suggests that Reddit often moves in tandem with HN. The data does not contain other cascade narratives to confirm if all originate on HN, nor does it show any cascade narratives starting on Reddit.
Strategic implication: If Reddit is consistently downstream (as suggested by the 12-hour lag in the single cascade event and the 0.908 correlation), it functions primarily as an amplifier rather than an ignition source. Investment efforts should prioritize igniting narratives on HN, then focusing on optimizing Reddit for amplification through timely, media-rich content (Reddit media posts have a median lift of 8.1x).

**D. Does HN score determine organic cascade reach?**
The data suggests but does not confirm that HN score is *not* the sole social proof signal for organic YouTube creators. The "Claude source code leak" cascade originated with an HN post having a score of 2. Despite this low initial score, significant organic YouTube engagement followed, with Fireship peaking at 2592415 views 16 hours after the HN post. This indicates that other factors, such as the nature of the content (e.g., a "leak"), or pre-briefing of creators, can drive substantial organic cascade reach on YouTube even with a low initial HN score.

**E. Do simultaneous narratives compound or cannibalize reach?**
The platform weekly correlation data suggests that simultaneous narratives tend to compound reach across certain platform pairs, but can be independent or cannibalizing for others:
*   **Compounding:** HN vs. Reddit (0.908 correlation) and HN vs. X (0.595 correlation), and Reddit vs. X (0.558 correlation) show strong positive correlations, suggesting shared narratives drive engagement across these platforms simultaneously.
*   **Independent/Cannibalizing:** HN vs. YouTube (0.167 correlation), Reddit vs. YouTube (0.287 correlation), and X vs. YouTube (-0.034 correlation) show weak or negative correlations. This suggests that YouTube's reach is largely independent of, or potentially cannibalized by, simultaneous narratives on X, and weakly correlated with HN and Reddit.
Strategic implication for launch timing: Launching narratives simultaneously across HN, Reddit, and X appears to compound overall reach. However, for YouTube, a distinct launch timing or content strategy might be more effective to avoid independent or cannibalized reach, as its engagement does not strongly correlate with the other platforms.

**F. Cascade speed synthesis table**

| Narrative | HN→Reddit lag | HN→X lag | HN→YouTube lag | Platforms | Speed |
|---|---|---|---|---|---|
| Claude source code leak | 12 hours | not available in dataset | 0.1 hours | HN, YouTube, Reddit | Fast |

The data suggests but does not confirm that scandal cascades faster than opinion content, as only one scandal/leak narrative is provided in the cascade data. The "Claude source code leak" cascade demonstrated a very fast initial YouTube reaction (0.1 hours) and a 12-hour Reddit reaction. This suggests that fast cascades (like this leak) require a pre-briefed creator strategy for immediate impact. Slower organic cascades (e.g., Reddit joining at 12 hours, Fireship peaking at 16 hours) allow for more reactive amplification strategies, such as targeted Reddit posts with media. Therefore, the data suggests but does not confirm that fast and slow cascades should have different response playbooks, with fast cascades requiring proactive creator engagement and slower cascades benefiting from reactive amplification.

<!-- === PASS 2 START === -->

## Finding 1 — The Power Law Is the Whole Game

**Claim:** A small fraction of posts generate most of the engagement across platforms, and these high-impact events are critical for triggering cross-platform cascades.

| Platform | Total Posts (n) | Top 10% Posts Share of Engagement | Top 1% Posts Share of Engagement | % Posts for 80% Engagement |
|---|---|---|---|---|
| HN | 1884 | 85% | 43% | 6.4% |
| Reddit | 125 | 46% | 10% | 31.2% |
| X | 82 | 80% | not available in dataset | 8.5% |
| YouTube | 86 | 63% | not available in dataset | 22.1% |

**Cross-platform link:** The "Claude source code leak" cascade (F2) originated with an HN post scoring 2, but led to Fireship peaking at 2592415 views on YouTube. This suggests that while initial platform scores may be low, the inherent high-impact nature of the content (e.g., a "leak") has power-law potential that drives significant cross-platform engagement.

**Growth Insight:** Our growth strategy must focus on identifying and amplifying content with inherent power-law potential, rather than solely optimizing for initial platform scores. The event's impact, not just the initial post's score, dictates cascade reach.

**Strategy:**
1.  Prioritize content that aligns with "leak" or "breakthrough" framing (as established in TL;DR F5 and F7) for all initial posts, as these types have demonstrated high engagement potential.
2.  Implement a rapid response protocol (as per Launch Day Protocol T+3h) for content that shows early signs of high engagement (e.g., HN score > 2 within T+3h), regardless of its initial platform score, to capture cascade potential.
3.  Invest in creator relationships (F7) to ensure rapid amplification of high-potential narratives, as pre-briefed creators (Matthew Berman, Theo t3.gg) captured early YouTube engagement for the "Claude source code leak" cascade.

**Owner:** Growth
**Confidence:** High (n=1884 HN, n=125 Reddit, n=82 X, n=86 YouTube across multiple platforms)

---

## Finding 2 — The 3-Wave Cascade (Timestamped)

**Claim:** Viral events typically unfold in a three-wave cascade pattern across platforms, starting with rapid creator reactions, followed by organic amplification, and concluding with meme/international spread.

| Wave | Hours After HN Post | Platform | Engagement Score | Label |
|---|---|---|---|---|
| Wave 1 | 0 | HN | 2 | HN first post (01:13 UTC) |
| Wave 1 | 0.1 | YouTube | 162576 | Matthew Berman (7 min after HN) |
| Wave 1 | 3 | YouTube | 182642 | Theo t3.gg |
| Wave 2 | 12 | Reddit | 337 | Reddit joins (12h after HN) |
| Wave 2 | 16 | YouTube | 2592415 | Fireship peak (2.59M views) |
| Wave 3 | 48 | YouTube | 131467 | SAMTIME satire |
| Wave 3 | 48.5 | YouTube | 89249 | International wave (PT) |

**Cross-platform link:** This finding directly details the causal chain from HN ignition to YouTube and Reddit, distinguishing between rapid pre-briefed creator reactions (Matthew Berman at 0.1 hours) and delayed organic amplification (Fireship peak at 16 hours).

**Growth Insight:** Different cascade waves require distinct strategies: proactive engagement for Wave 1 (pre-briefed creators), reactive amplification for Wave 2 (organic spread), and broad cultural/localization efforts for Wave 3 (meme/international).

**Strategy:**
1.  For Wave 1 (T+0h to T+3h): Pre-brief Tier-1 YouTube creators with embargoed content, ensuring they can publish within 0.1-3 hours of an HN ignition, as Matthew Berman did at 0.1 hours.
2.  For Wave 2 (T+12h to T+16h): Prepare media-rich Reddit content for deployment at T+12h if an HN post shows early traction (e.g., score > 2), to amplify the organic cascade as Reddit joined at 12 hours.
3.  For Wave 3 (T+48h+): Develop localized and meme-friendly content templates for rapid deployment on YouTube and X, to capture international and satire waves as seen at 48 hours and 48.5 hours.

**Owner:** Growth, Content
**Confidence:** Directional (n=1 cascade event)

---

## Finding 3 — Spike Type Volume vs Engagement Inverted

**Claim:** The most frequent content types ("breakthrough") do not consistently yield the highest median engagement, while less frequent types like "meme" can have disproportionately high maximum engagement.

| Spike Type | Count (n) | % of Total Posts | Mean Engagement | Median Engagement | Max Engagement |
|---|---|---|---|---|---|
| breakthrough | 1099 | 50.5% | 52028 | 3 | 33637201 |
| tutorial | 633 | 29.1% | 12176 | 2 | 2592415 |
| meme | 171 | 7.9% | 288912 | 3 | 28862704 |
| personal | 152 | 7.0% | 16326 | 21 | 2298639 |
| comparison | 122 | 5.6% | 3790 | 4 | 94172 |

**Cross-platform link:** "Breakthrough" content, accounting for 50.5% of posts, is a primary ignition source for HN (as established in TL;DR F5). "Meme" content, despite its lower frequency (7.9%), demonstrates high maximum engagement (28862704), indicating its critical role in the later stages of a YouTube cascade (e.g., SAMTIME satire at 48 hours, F2).

**Growth Insight:** While "breakthrough" content is a reliable volume driver and ignition source, "meme" content, despite lower frequency, holds significant viral potential for peak engagement, particularly on platforms like YouTube and X.

**Strategy:**
1.  For HN, prioritize "breakthrough" framing for initial posts, aiming for consistent ignition, as "breakthrough" accounts for 50.5% of total posts.
2.  For YouTube and X, develop a dedicated content stream for "meme" and "personal" content, ready for rapid deployment during organic cascade amplification (T+16h to T+48h), given "meme" content's max engagement of 28862704 and "personal" content's max engagement of 2298639.
3.  Avoid over-reliance on "tutorial" content for viral growth, as it has a low median engagement of 2 despite high volume (29.1%).

**Owner:** Content
**Confidence:** High (n=2177 total posts across platforms)

---

## Finding 4 — Platform Timing Windows

**Claim:** Optimal posting times vary significantly by platform, with HN peaking in the evening UTC and Reddit on Sundays, creating a specific sequencing window for cross-platform amplification.

| Platform | Optimal Window | Mean Engagement in Window | Count (n) |
|---|---|---|---|
| HN | 22 UTC | 72.1 | 87 |
| HN | 19-23 UTC | 35-49 | 334 (sum of counts for 19, 21, 22, 23 UTC) |
| Reddit | Sunday | 4344.0 | 11 |

**Cross-platform link:** The 12-hour HN→Reddit lag (F2) combined with HN's peak hours (19-23 UTC) and Reddit's peak day (Sunday) suggests that an HN ignition on a Saturday evening UTC is optimally positioned for a Sunday Reddit amplification.

**Growth Insight:** To maximize the HN→Reddit cascade, an HN post needs to be timed such that its peak engagement coincides with the optimal Reddit posting window, accounting for the 12-hour lag.

**Strategy:**
1.  Schedule initial HN posts between 19-23 UTC, specifically targeting 22 UTC for highest mean score (72.1), to maximize initial HN traction.
2.  If an HN post is published on a Saturday between 19-23 UTC and achieves an initial score > 2 (as per Launch Day Protocol T+3h), prepare Reddit amplification for Sunday (T+12h to T+17h window) to align with Reddit's peak mean engagement of 4344.0.
3.  Avoid publishing HN posts that require Reddit amplification on weekdays that would lead to a Reddit post on Thursday (mean 1625.7) or Tuesday (mean 1684.8), as these are the lowest performing Reddit days.

**Owner:** Growth
**Confidence:** Medium (n=1884 HN posts, n=125 Reddit posts)

---

## Finding 5 — Title Word Lift

**Claim:** Specific keywords in titles significantly increase engagement, clustering around themes of novelty, access, and urgency, while generic terms perform poorly.

| Word | Lift |
|---|---|
| deepseek | 21.29 |
| back | 18.25 |
| mythos | 18.25 |
| nano | 15.2 |
| safeguards | 15.2 |
| gives | 15.2 |
| leaks | 15.2 |
| leaked | 13.18 |
| update | 12.16 |
| accidentally | 12.16 |

| Word | Lift |
|---|---|
| show | 0.15 |
| agents | 0.26 |
| local | 0.26 |
| built | 0.29 |
| agent | 0.34 |

**Cross-platform link:** High-lift words like "leaks" and "leaked" directly relate to the "Claude source code leak" cascade (F2), which generated significant organic YouTube pickup (Fireship peak at 16 hours with 2592415 views). This suggests these words act as a social proof signal for organic creators and contribute to cross-platform virality.

**Growth Insight:** Framing content with high-lift words, especially those implying "exclusive access," "novelty," or "urgency," is crucial for both initial ignition on platforms like HN and subsequent organic amplification across platforms.

**Strategy:**
1.  Mandate the use of high-lift words such as "leaks," "leaked," "update," or "accidentally" in HN and Reddit titles for content related to new information or discoveries, aiming for a lift of 12.16 or higher.
2.  Conduct A/B testing on X post copy to identify platform-specific high-lift words, focusing on terms related to "exclusive access" or "novelty" to maximize engagement.
3.  Train content creators to avoid low-lift words like "show," "agents," or "built" in titles and descriptions across all platforms, as these have lifts as low as 0.15.

**Owner:** Content
**Confidence:** Medium (n=not available in dataset for word lift calculation, but "top 80% vs bottom 20% engagement posts, min 3 occurrences" suggests a substantial sample size)

---

## Finding 6 — The Sustained Controversy or Halo Effect

**Claim:** The data does not provide sufficient evidence to confirm a halo effect where sustained controversy elevates the baseline engagement for all content in the same period.

| Platform | Interpretation |
|---|---|
| Reddit | During weeks when HN spikes, reddit engagement is nanx higher than during normal HN weeks — no clear halo effect. |
| X | During weeks when HN spikes, x engagement is nanx higher than during normal HN weeks — no clear halo effect. |
| YouTube | During weeks when HN spikes, youtube engagement is nanx higher than during normal HN weeks — no clear halo effect. |

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data. The data suggests but does not confirm that there is no clear halo effect across platforms.

**Growth Insight:** Without a clear halo effect, each piece of content must be optimized for its own virality rather than relying on ambient elevated attention from broader controversies.

**Strategy:**
1.  Continue to evaluate each content piece on its individual merit and optimize for platform-specific best practices (e.g., media-rich for Reddit, specific timing for HN) rather than assuming a general uplift from external events.
2.  Implement A/B testing for content published during periods of high external discourse to definitively measure any potential halo effect on specific content types or platforms.
3.  Focus on direct amplification strategies (e.g., creator network, targeted Reddit posts) for individual high-potential content, as a general "halo" cannot be relied upon.

**Owner:** Growth, Analytics
**Confidence:** Directional (n=not available in dataset for halo effect calculation, due to NaN values)

---

## Finding 7 — Community Creators vs Official Channel

**Claim:** Community creators significantly outperform official channels in total engagement on YouTube, while on X, community accounts generate substantial, but slightly less, total engagement compared to the official account.

| Platform | Entity | Total Engagement | Number of Posts | Mean Engagement per Post |
|---|---|---|---|---|
| YouTube | Community | 6012847 | 86 (total YouTube posts) | 69916 |
| YouTube | Official | 196616 | not available in dataset | not available in dataset |
| X | Official | 62426201 | 44 | 1418777 |
| X | Community | 48453827 | 38 | 1275100 |

**Cross-platform link:** Organic YouTube creators (e.g., Fireship, F2) reacted to the HN ignition, suggesting they monitor HN as a signal for content coverage. The rapid reaction of Matthew Berman (0.1 hours after HN, F2) further supports this, even if pre-briefed.

**Growth Insight:** Community-driven content is a critical, high-leverage growth channel, especially on YouTube (30.6x ratio over official baseline), and a significant amplifier on X (0.8x official engagement).

**Strategy:**
1.  Establish a formal "Community Creator Partnership Program" for YouTube, identifying and regularly engaging top community channels like Fireship and Dan Martell, aiming to achieve a 30.6x multiplier over official content.
2.  For X, cultivate relationships with top community authors (e.g., Ilya Sutskever, Amjad Masad) and provide them with early access to content and data, aiming to generate at least 0.8x the official account's total engagement.
3.  Implement a monitoring system for HN to detect emerging narratives that community creators might pick up, allowing for proactive engagement and support for organic YouTube content creation.

**Owner:** Comms, Growth
**Confidence:** Medium (n=86 YouTube posts, n=82 X posts)

---

## Finding 8 — Engagement Decay by Platform

**Claim:** Engagement decay rates vary significantly by platform, with Reddit showing rapid day-0 decay, while YouTube and HN have slower initial decay, creating a specific sequencing window for cross-platform amplification.

| Platform | Day 0 Decay | Day 1 Decay | Day 3 Decay | Day 6 Decay |
|---|---|---|---|---|
| HN | 0.0037 | 0.0083 | 0.0004 | 0.0003 |
| Reddit | 0.0597 | 0.049 | 0.0047 | 0.001 |
| YouTube | 0.0032 | 0.0218 | 0.0069 | 0.0035 |

**Cross-platform link:** The rapid decay on Reddit (0.0597 day-0) combined with the 12-hour HN→Reddit lag (F2) and Reddit's optimal Sunday timing (F4) defines a critical window for handoff.

**Growth Insight:** Reddit requires immediate amplification once a narrative gains traction on HN to capitalize on its initial engagement before rapid decay. YouTube offers a longer tail for content.

**Strategy:**
1.  If an HN post is published between 19-23 UTC on a Saturday and achieves an initial score > 2 (as per Launch Day Protocol T+3h), trigger Reddit amplification at T+12h on Sunday, ensuring the Reddit post is live before its day-0 decay of 0.0597 significantly impacts reach.
2.  For YouTube content, plan for sustained promotion and engagement over several days, as its day-0 decay (0.0032) is significantly slower than Reddit's, allowing for a longer content lifecycle.
3.  Implement a "decay alert" system for Reddit posts: if a post's engagement velocity drops below 0.0597 within the first 12 hours, consider immediate follow-up amplification on X or through community creators.

**Owner:** Growth
**Confidence:** Directional (n=not available in dataset for decay calculation, but implies a time-series analysis across multiple posts)

---

## Finding 9 — Competitor Attacks as Organic Growth Events

**Claim:** The data does not provide specific competitor-generated content data to confirm that external threats generate more reach than own launches via tribal defense. However, "attack frame" narratives do spread cross-platform and achieve significant engagement on Reddit and YouTube.

| Narrative Type | Posts (n) | Platforms | Total Engagement | Mean Engagement | Median Engagement |
|---|---|---|---|---|---|
| Attack Frame | 27 | 3 | 120504 | 4463 | 3 |

| Platform (Attack Frame) | Posts (n) | Total Engagement | Mean Engagement |
|---|---|---|---|
| HN | 23 | 531 | 23 |
| Reddit | 2 | 31068 | 15534 |
| YouTube | 2 | 88905 | 44452 |

**Cross-platform link:** The "attack frame" narrative appears on HN (23 posts), Reddit (2 posts), and YouTube (2 posts), suggesting cross-platform spread. Reddit and YouTube show significantly higher mean engagement for these narratives (15534 and 44452 respectively) compared to HN (23).

**Growth Insight:** Attack narratives, regardless of their origin, can gain cross-platform traction, particularly on Reddit and YouTube where they achieve higher mean engagement than on HN.

**Strategy:**
1.  Establish a real-time monitoring system for "attack frame" keywords (e.g., "\\bend of\\b", "\\bdead\\b") across HN, Reddit, and YouTube.
2.  If an "attack frame" narrative gains traction on Reddit (mean engagement > 15534) or YouTube (mean engagement > 44452), prepare a rapid response strategy involving pre-briefed community creators to counter or reframe the narrative.
3.  For HN, monitor attack narratives, but prioritize engagement on Reddit and YouTube for response, as these platforms show higher engagement for such content.

**Owner:** Comms, Growth
**Confidence:** Directional (n=27 attack narrative posts, but lacks comparative data on "own launches" and origin of attack)

---

## Finding 10 — The Movement Naming Effect

**Claim:** The data does not provide specific information on a coined phrase (e.g., "vibe coding") that became a dominant framing for the product. However, the weekly trend of specific keywords like "claude" and "anthropic" shows how a narrative can gain compound cross-platform effect.

| Keyword | Year-Week | Posts (n) | Total Engagement |
|---|---|---|---|
| claude | 2026-W13 | 77 | 801758 |
| claude | 2026-W14 | 133 | 4918167 |
| anthropic | 2026-W13 | 57 | 134441 |
| anthropic | 2026-W14 | 63 | 2795974 |

**Cross-platform link:** The weekly trends for "claude" and "anthropic" show simultaneous growth across HN, Reddit, and YouTube in weeks like 2026-W13 and 2026-W14, suggesting a compound cross-platform effect for these key terms. For example, in 2026-W14, "claude" had 133 posts with 4918167 total engagement, while "anthropic" had 63 posts with 2795974 total engagement, indicating a shared narrative.

**Growth Insight:** Consistent use and amplification of key product/brand terms can create a strong, compounding cross-platform narrative, driving significant engagement.

**Strategy:**
1.  Identify and consistently use a core set of product-defining keywords (e.g., "claude," "anthropic") across all official communications and encourage community creators to adopt them.
2.  Monitor the weekly trend of these keywords across platforms, and if a keyword's total engagement shows a significant weekly increase (e.g., "claude" from 801758 in W13 to 4918167 in W14), amplify content using that keyword across all platforms.
3.  Incorporate these keywords into YouTube video titles and descriptions to enhance search visibility and reinforce the narrative, leveraging the high engagement seen for these terms.

**Owner:** Content, Comms
**Confidence:** Medium (n=multiple weeks of keyword data for "claude" and "anthropic" across platforms)

---

## Finding 11 — The Inside Engineer Effect

**Claim:** The data does not provide a direct comparison between an internal engineer's personal posting and the official account across multiple post types. However, top community authors on X, who may include engineers, show significant engagement.

| Author | Platform | Total Engagement | Posts (n) | Mean Engagement per Post |
|---|---|---|---|---|
| Ilya Sutskever | X | 44698308 | 12 | 3724859 |
| Amjad Masad | X | 2038052 | 14 | 145575 |
| Y Combinator | X | 1207511 | 1 | 1207511 |

**Cross-platform link:** The data suggests but does not confirm that high-performing personal X posts (e.g., Ilya Sutskever's) generate HN secondary threads, as the dataset does not explicitly link individual X posts to HN threads. However, the strong HN vs X correlation (0.595) suggests that high activity on X may coincide with HN discussions.

**Growth Insight:** Empowering prominent individuals, potentially including internal experts, to post on X can generate engagement comparable to or exceeding official channels, acting as a significant multiplier.

**Strategy:**
1.  Identify and empower prominent individuals within the company (e.g., engineers, researchers) to post on X, providing them with content guidelines and support, aiming to replicate engagement levels seen by top community authors like Ilya Sutskever (mean 3724859 per post).
2.  Cross-promote high-performing personal X posts from these individuals through official channels and community networks to amplify their reach and potentially spark discussions on HN.
3.  Monitor the engagement of these personal accounts on X, and if a post exceeds a threshold (e.g., 1,000,000 engagement), consider drafting a related HN post to capture secondary discussion.

**Owner:** Comms, Growth
**Confidence:** Directional (n=12 posts for Ilya Sutskever on X, but lacks direct comparison to official account across multiple post types or direct HN linkage)

---

## Finding 12 — Small Accounts and Viral Outliers

**Claim:** The data on follower-count vs. views is not available in the dataset to assess the outlier-to-median ratio in small-account buckets.

**Data:** `follower_count_vs_reach.available`: false. `follower_count_vs_reach.reason`: "'follower_count' column not found in unified_posts.csv."

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data.

**Growth Insight:** Not available in dataset.

**Strategy:**
1.  Implement data collection for 'follower_count' in the X scraper to enable future analysis of small account viral outliers.
2.  Until data is available, focus on established community creators (F7) and high-lift content (F5) for viral amplification, as these strategies are supported by existing data.

**Owner:** Data Engineering, Growth
**Confidence:** Not available in dataset (n=0)

---

## Finding 13 — Competitor Community Outperforms Home Community

**Claim:** The data on subreddit comparison is not available in the dataset to assess if competitor-community readers have higher purchase intent or if viral competitor-subreddit posts generate cross-platform activity.

**Data:** `subreddit_breakdown.available`: false. `subreddit_breakdown.reason`: "'subreddit' column not found in unified_posts.csv."

**Cross-platform link:** Platform-isolated: no cross-platform signal in this data.

**Growth Insight:** Not available in dataset.

**Strategy:**
1.  Implement data collection for the 'subreddit' column in the Reddit scraper to enable future analysis of competitor communities and their impact.
2.  Until data is available, focus on optimizing content for general Reddit engagement (F3, F4, F8) and monitoring for "attack frame" narratives (F9) within existing Reddit data.

**Owner:** Data Engineering, Growth
**Confidence:** Not available in dataset (n=0)

---

## Finding 14 — The Switching Narrative as a Durable Cross-Platform Thread

**Claim:** "Switching frame" narratives represent a durable cross-platform thread, appearing across HN, Reddit, and YouTube, with significant total engagement. "Attack frame" narratives also spread cross-platform, albeit with lower total engagement.

| Narrative Type | Posts (n) | Platforms | Total Engagement | Mean Engagement | Median Engagement |
|---|---|---|---|---|---|
| Switching Frame | 73 | 3 | 566258 | 7756 | 4 |
| Attack Frame | 27 | 3 | 120504 | 4463 | 3 |

| Platform (Switching Frame) | Posts (n) | Total Engagement | Mean Engagement |
|---|---|---|---|
| HN | 52 | 762 | 14 |
| Reddit | 7 | 37168 | 5309 |
| YouTube | 14 | 528328 | 37737 |

| Platform (Attack Frame) | Posts (n) | Total Engagement | Mean Engagement |
|---|---|---|---|
| HN | 23 | 531 | 23 |
| Reddit | 2 | 31068 | 15534 |
| YouTube | 2 | 88905 | 44452 |

**Cross-platform link:** Both "switching frame" and "attack frame" narratives explicitly show spread across HN, Reddit, and YouTube, confirming they are durable cross-platform threads. The weekly trends for both narratives show simultaneous activity across platforms (e.g., "switching frame" in 2026-W13 and W14, "attack frame" in 2026-W14).

**Growth Insight:** Narratives focused on "switching" or "attacking" are not isolated events but continuous threads that require consistent monitoring and strategic intervention across platforms.

**Strategy:**
*   **Amplification playbook (Switching Narrative):**
    1.  **Detection:** Monitor HN, Reddit, and YouTube daily for "switching frame" keywords (e.g., "\\bswitch(ed|ing)?\\b", "\\bmigrat(ed|ing)?\\b"). If a post containing these keywords on HN or Reddit exceeds 100 engagement within 6 hours, flag it as a nascent switching narrative.
    2.  **Acceleration:** If a nascent switching narrative is detected, immediately brief community creators (F7) on YouTube and X with content that reinforces the positive switching narrative, aiming for publication within 12 hours.
    3.  **Framing:** Frame amplification content as a "comparison" or "personal" story (F3), highlighting benefits of switching, to drive engagement on YouTube (mean 37737 for switching narrative).
*   **Defense playbook (Attack Narrative):**
    1.  **Early Warning:** Monitor HN daily for "attack frame" keywords (e.g., "\\bend of\\b", "\\bfail(ed|ing|ure)?\\b"). If an HN post with these keywords reaches a score of 5 within 3 hours, consider it an early warning.
    2.  **Containment:** If an "attack frame" narrative begins to gain traction on Reddit (mean engagement > 15534) or YouTube (mean engagement > 44452), immediately engage pre-briefed community managers and official channels on X to provide factual corrections or positive counter-narratives.
    3.  **De-amplification:** Avoid direct engagement with low-engagement "attack frame" posts on HN (mean 23) to prevent accidental amplification. Focus resources on platforms where the narrative is gaining significant traction.

**Owner:** Growth, Comms, Content
**Confidence:** Medium (n=73 switching narrative posts, n=27 attack narrative posts across 3 platforms)

---

## Strategic Synthesis — Three Playbooks

### Playbook A — The Launch Playbook
*Use when: you control the timing.*

1.  **T-72h:** Identify and pre-brief 3-5 Tier-1 YouTube creators with embargoed content (F2). → If no Tier-1 creators are available, then identify 5-10 Tier-2 creators and provide them with a detailed content brief and early access to assets.
2.  **T-0h:** Publish HN post at 01:13 UTC, targeting 19-23 UTC window for peak visibility (F4), using "breakthrough" or "leak" framing (F5). → If HN score < 2 at T+4h, then prepare a follow-up HN post with a different framing (e.g., "personal" or "tutorial" from F3) for publication at T+12h, and notify pre-briefed YouTube creators to hold publication.
3.  **T+2h through T+48h:**
    *   **T+0.1h:** Confirm pre-briefed YouTube creators have published their content (F2).
    *   **T+3h:** Monitor HN score; if above 2, prepare Reddit amplification (F2).
    *   **T+12h:** Post media-rich content on Reddit (F3), targeting Sunday if HN was published on Saturday (F4), to capitalize on Reddit's 0.0597 day-0 decay (F8).
    *   **T+16h:** Monitor YouTube for organic peaks (e.g., Fireship, F2). Engage with top comments and share organic content on X.
    *   **T+24h:** Prepare follow-up content for X, incorporating media (F3) and engaging top community authors (F7).
    *   **T+48h:** Evaluate initial cascade reach and prepare for meme/international content amplification on YouTube and X (F2).
4.  **Contingency:** If nothing is gaining traction at T+8h (HN score remains low, no YouTube creator pickup), the escalation path is to re-evaluate the content's framing (F5), consider a new HN post with a different angle, and activate the "Ambient Narrative Playbook" (Playbook C) to maintain long-term presence rather than forcing a cascade.

### Playbook B — The Rapid Response Playbook
*Use when: external event — competitor attack, controversy, or unplanned leak.*

1.  **First 30 min:** Assess the nature of the external event (competitor attack, controversy, unplanned leak) and identify keywords (F5, F9). Determine if it's an "attack frame" or "switching frame" narrative (F14).
2.  **First 2h:** If it's a "leak" or "accidentally" framed event (F5), prioritize immediate briefing of Tier-1 YouTube creators for rapid response (0.1h reaction, F2) to control the narrative. If it's an "attack frame" narrative, prioritize a factual response on X through official or top community accounts (F7) within 2 hours.
3.  **The "do not amplify" rule:** If an "attack frame" narrative on HN has a score below 5 within 3 hours (F14), do not engage directly on HN to avoid accidental amplification.
4.  **T+12h to T+48h:**
    *   **T+12h:** If the event has gained traction on HN (score > 2) and YouTube (initial creator engagement), prepare media-rich Reddit content (F3) for amplification, especially if it aligns with Reddit's peak Sunday timing (F4).
    *   **T+16h:** Monitor organic YouTube reactions (Fireship, F2). Engage with top comments and identify potential community creators for further amplification.
    *   **T+24h:** Deploy follow-up content on X, engaging top community authors (F7) to reinforce positive narratives or correct misinformation.
    *   **T+48h:** Prepare for meme/international wave on YouTube (F2) by developing localized content or satire responses.

### Playbook C — The Ambient Narrative Playbook
*Use when: no launch, no crisis — maintaining long-term cross-platform presence.*

1.  **Daily:**
    *   Monitor HN for negative sentiment (16.0%, TL;DR F10) and "attack frame" keywords (F14). If negative sentiment exceeds 20% or an "attack frame" post reaches a score of 5 within 3 hours, trigger the "Rapid Response Playbook" (Playbook B).
    *   Monitor top community authors on X (F7) for organic content that can be amplified.
2.  **Weekly:**
    *   Identify nascent "switching frame" narratives (F14) in competitor communities (if data becomes available, F13) or on HN/Reddit. Seed positive switching narratives through community creators on YouTube and X, framing them as "comparison" or "personal" stories (F3).
    *   Analyze weekly keyword trends (F10) for "claude" and "anthropic." If a significant increase in engagement is observed, plan content to reinforce these terms.
3.  **Monthly:**
    *   Support internal prominent individuals (e.g., engineers, F11) with content ideas and amplification for their X presence, aiming to achieve high engagement.
    *   Review "breakthrough" and "tutorial" content performance (F3) to ensure a consistent pipeline of ignition and evergreen content.
4.  **Early warning:** A sudden spike in "attack frame" keyword mentions on Reddit (mean engagement > 15534) or YouTube (mean engagement > 44452) within a 24-hour period (F14) is a signal that an attack narrative is starting to cascade, requiring immediate activation of the "Rapid Response Playbook" (Playbook B).

---

## Limitations

| Limitation | Findings affected | Severity |
|---|---|---|
| Single cascade event for detailed timing | F2, F6, F8, F14 | Medium |
| Lack of 'subreddit' column in Reddit data | F13 | High |
| Lack of 'follower_count' in X data | F12 | High |
| Halo effect calculation resulted in NaN values | F6 | Medium |
| Word lift calculation sample size not explicitly stated | F5 | Low |
| YouTube official channel data from prior scrape | F7 | Low |
| "Inside Engineer Effect" lacks direct comparison to official account across multiple post types | F11 | Medium |
| "Competitor Attacks" lacks origin data (competitor-generated vs. organic community criticism) | F9 | Medium |