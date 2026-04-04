<!-- Generated: 2026-04-04 18:52 UTC -->
<!-- Model: gemini/models/gemini-2.5-flash -->
<!-- Source data: 855 classified posts — hn: 562, reddit: 125, x: 82, youtube: 86 -->
<!-- Audit trail: data/processed/analysis_metrics.json -->

# Claude's Viral Growth Playbook — Decoded
## HackNU 2026 · Growth Engineering Track · Part 2

> **Data provenance:** All findings derived from our scraped dataset: 855 posts across HN, Reddit, YouTube, X (April 2026). No external sources.

---

## Dataset Summary

| Platform | Posts | Coverage | Scraper method |
|:---------|:------|:---------|:---------------|
| HN       | 562   | Code/Tech| Competitive Intelligence Pipeline |
| Reddit   | 125   | General  | Competitive Intelligence Pipeline |
| X        | 82    | General  | Competitive Intelligence Pipeline |
| YouTube  | 86    | Video    | Competitive Intelligence Pipeline |
| **Total**| **855** |  |  |

---

## Finding 1 — The 3-Wave Cascade Is Real

The initial "Claude source code leak" event on April 1, 2026, triggered a distinct three-wave cascade, with the maximum impact observed within the first 16 hours. Hacker News served as the initial spark, with the first post appearing at 0 hours after the event. This was rapidly followed by YouTube creators, indicating a quick content production cycle. Reddit joined the conversation significantly later, suggesting a different audience engagement pattern.

| Time (hours after) | Platform | Score    | Event  |
|:-------------------|:---------|:---------|:------------------------------------|
| 0  | hn       | 2        | HN first post (01:13 UTC)  |
| 0.1  | youtube  | 162576   | Matthew Berman (7 min after HN)     |
| 3  | youtube  | 182642   | Theo t3.gg  |
| 12  | reddit   | 337      | Reddit joins (12h after HN)         |
| 16  | youtube  | 2592415  | Fireship peak (2.59M views)         |
| 48  | youtube  | 131467   | SAMTIME satire  |
| 48.5  | youtube  | 89249    | International wave (PT)  |

**Growth Insight:** For competing products, establishing an early presence on developer-centric platforms like Hacker News is crucial for igniting a viral cascade. Rapid follow-up by influential YouTube creators within the first 7 minutes to 3 hours is key to amplifying reach, especially within the critical 16-hour maximum impact window.

---

## Finding 2 — Community Creators Outperform Official Channel by 30x

Community-driven content on YouTube generated significantly more engagement than official channels. The total views from community creators reached 6,012,847, dwarfing Anthropic's official channel's 196,616 views. This resulted in a 30.6x engagement ratio in favor of community content. The top-performing community channel, Fireship, alone garnered 2,592,415 views, highlighting the power of external influencers.

| Channel        | Total Views |
|:---------------|:------------|
| Fireship       | 2592415     |
| Dan Martell    | 316127      |
| Anthropic      | 196616      |
| Theo - t3.gg   | 182642      |
| Matthew Berman | 162576      |

**Growth Insight:** Investing in community creator relations and enablement is paramount. Rather than solely focusing on in-house content production, growth teams should prioritize identifying and briefing key influencers, as they can deliver over 30 times the reach and engagement compared to official brand channels.

---

## Finding 3 — Spike Type Volume vs Engagement Are Inverted

While "breakthrough" posts constituted the largest share of content at 45.5% of total posts, their median engagement was a mere 4. In contrast, "meme" posts, representing only 9.8% of posts, had a significantly higher mean engagement of 588,136, despite a median of 332. This indicates that a few highly successful meme posts drove disproportionate engagement, while many breakthrough posts went unnoticed. "Tutorial" posts, at 26.8% of volume, also showed a large gap between mean (33648) and median (5) engagement.

| Spike Type   | % of Posts | Avg Engagement | Median Engagement |
|:-------------|:-----------|:---------------|:------------------|
| breakthrough | 45.5       | 146931         | 4  |
| tutorial     | 26.8       | 33648  | 5  |
| personal     | 10.3       | 28177  | 912  |
| meme         | 9.8        | 588136         | 332  |
| comparison   | 7.6        | 7098  | 32  |

**Growth Insight:** A high volume of "breakthrough" content doesn't guarantee engagement. To maximize viral potential, growth strategies should balance content types, aiming for high-impact "meme" or "tutorial" content that, while potentially lower in volume, can achieve significantly higher average engagement, even if median performance remains modest.

---

## Finding 4 — Platform Timing Windows

Optimal posting times vary significantly by platform. On Hacker News, posts made between 19-23 UTC (2-6 pm ET) achieved an average score of 35-49 points, substantially higher than the approximately 10 points at other hours. For Reddit, Sunday posts showed the highest average engagement at 4344.0, nearly triple the average of Thursday posts (1625.7).

**Hacker News Top 5 UTC Hours**

| Hour | Mean Score | Count |
|:-----|:-----------|:------|
| 22   | 49.4       | 23    |
| 19   | 36.4       | 27    |
| 23   | 34.8       | 24    |
| 6    | 18.7       | 21    |
| 21   | 18.7       | 26    |

**Reddit Average Score by Weekday**

| Weekday   | Mean Score | Count |
|:----------|:-----------|:------|
| Sunday    | 4344.0     | 11    |
| Saturday  | 3549.6     | 22    |
| Wednesday | 2799.3     | 20    |
| Monday    | 1981.9     | 9     |
| Friday    | 1720.5     | 24    |
| Tuesday   | 1684.8     | 22    |
| Thursday  | 1625.7     | 17    |

**Growth Insight:** Strategic scheduling is critical. For developer-focused content, target Hacker News during 19-23 UTC for peak visibility. For broader community engagement on Reddit, prioritize Sunday postings to leverage the 4344.0 average score, significantly outperforming weekday averages.

---

## Finding 5 — Title Word Lift

Analysis of high-engagement posts reveals specific keywords that significantly boost visibility. Words like "leaks" and "insane" showed a 22.7x lift in engagement, while "tutorial" also had a 22.7x lift. Conversely, generic or brand-focused terms like "anthropic" (0.5x lift) and "source" (1.46x lift) were associated with lower engagement.

**Top Lift Words (High Engagement)**

| Word     | Lift  | Interpretation  |
|:---------|:------|:----------------------------------|
| leaks    | 22.7  | Urgency, exclusivity, controversy |
| insane   | 22.7  | Hyperbole, excitement  |
| tutorial | 22.7  | Utility, practical value  |
| deepseek | 17.02 | Specific competitor/context       |
| powerful | 17.02 | Strong benefit, capability        |
| most     | 17.02 | Superlative, comparison  |
| best     | 17.02 | Superlative, quality  |
| leaked   | 13.62 | Urgency, exclusivity  |
| sonnet   | 9.46  | Product feature/version  |
| chatgpt  | 8.77  | Competitor comparison  |

**Bottom Lift Words (Low Engagement)**

| Word      | Lift | Interpretation  |
|:----------|:-----|:-------------------------------|
| anthropic | 0.5  | Brand name, generic  |
| source    | 1.46 | Technical, less exciting       |
| models    | 1.89 | Generic technical term         |
| gemini    | 3.15 | Competitor, but less impactful |
| code      | 3.41 | Technical, less exciting       |

**Growth Insight:** Crafting titles with high-lift words is essential for maximizing reach. Focus on words that convey urgency ("leaks," "leaked"), strong benefits ("insane," "powerful," "best"), or practical value ("tutorial"). Avoid overly generic or brand-centric terms like "anthropic" or "source" which show significantly lower lift.

---

## Finding 6 — Engagement Decay by Platform

Engagement velocity decays rapidly across all platforms, but with varying patterns. Reddit shows the highest initial velocity on Day 0 (0.2011), but also the most severe decay by Day 6 (0.0001). YouTube, while starting lower (0.025), sees a slight increase on Day 1 (0.0349) before decaying, suggesting a longer tail for video content. HN's velocity is consistently low after Day 0.

| Platform | Day 0 velocity | Day 1  | Day 3  | Day 6  |
|:---------|:---------------|:-------|:-------|:-------|
| hn       | 0.0294         | 0.0004 | 0.0004 | 0.0002 |
| reddit   | 0.2011         | 0.0239 | 0.0095 | 0.0001 |
| youtube  | 0.025  | 0.0349 | 0.0121 | 0.0036 |

**Growth Insight:** Content strategy must account for platform-specific decay rates. For Reddit, rapid initial engagement is key, as content quickly becomes irrelevant after Day 0. YouTube content, with its longer tail, benefits from sustained promotion. Hacker News content requires immediate impact, as its engagement drops sharply after the first day.

---

## Finding 7 — The 10/80 Rule: Engagement is Pareto-Concentrated

Engagement across platforms is highly concentrated, with a small percentage of posts driving the vast majority of interaction. On X, the top 10% of posts accounted for 80% of all engagement, requiring only 8.5 posts to capture this share. Hacker News showed similar concentration, with the top 10% of posts generating 78% of engagement from 12.1 posts. YouTube's top 10% captured 63% of engagement from 22.1 posts.

| Platform | Posts | Top 10% share | Posts needed for 80% of engagement |
|:---------|:------|:--------------|:-----------------------------------|
| hn       | 562   | 78  | 12.1  |
| reddit   | 125   | 46  | 31.2  |
| x        | 82    | 80  | 8.5  |
| youtube  | 86    | 63  | 22.1  |

**Growth Insight:** Success is not about average performance but about creating a few highly impactful pieces of content. Growth teams should focus resources on producing a small number of extremely high-quality, high-potential posts that can capture 78-80% of engagement on platforms like HN and X, rather than spreading efforts thinly across many average posts.

---

## Finding 8 — Author Concentration: Top 5 Accounts = 96.5% of Engagement

Despite 702 unique authors contributing content, a staggering 96.5% of total engagement was driven by just the top 5 authors. Anthropic's official X account alone contributed 53.4% of engagement (62,622,817 score), followed by Ilya Sutskever with 38.1% (44,698,308 score). This highlights an extreme concentration of influence, particularly on X.

| Author  | Platform | Engagement Score | % of Total |
|:----------------|:---------|:-----------------|:-----------|
| Anthropic       | x        | 62622817         | 53.4       |
| Ilya Sutskever  | x        | 44698308         | 38.1       |
| Fireship        | youtube  | 2592415  | 2.2        |
| Amjad Masad     | x        | 2038052  | 1.7        |
| Y Combinator    | x        | 1207511  | 1.0        |

**Growth Insight:** The "organic" viral narrative often masks a highly concentrated reality. For any competing product, identifying and engaging the top 5 key influencers or official accounts (which collectively drive 96.5% of engagement) is a critical growth lever, especially on X where brand and key individual accounts dominate.

---

## Finding 9 — Media Posts Drive 8–10x Higher Engagement

Posts containing media (images, videos) significantly outperform text-only posts in terms of engagement. On Reddit, media posts achieved an 8.1x higher median engagement (2310 vs 285) compared to text-only posts. Similarly, on X, media posts saw a 9.7x higher median engagement (196356 vs 20306). YouTube, being a video platform, inherently relies on media, with a median engagement of 22709.

| Platform | Media Count | Text Count | Media Median | Text Median | Lift |
|:---------|:------------|:-----------|:-------------|:------------|:-----|
| reddit   | 59  | 66         | 2310         | 285         | 8.1  |
| x        | 39  | 43         | 196356       | 20306       | 9.7  |
| youtube  | 86  | 0  | 22709        | 0  | 22709.5 |

**Growth Insight:** To maximize engagement on Reddit and X, always include rich media. Posts with images or videos can expect 8-10 times the median engagement of text-only posts, making visual content a non-negotiable component of a viral growth strategy.

---

## Finding 10 — Comment Sentiment Signals Spike Type

Analyzing 1,163 comments reveals distinct sentiment patterns across different spike types. "Tutorial" posts generated the highest positive sentiment at 27.6%, with a relatively moderate negative sentiment of 11.5%. "Comparison" posts also showed strong positive sentiment (21.0%) and the lowest negative sentiment (4.9%). "Meme" posts, while high in mean engagement, had a higher negative sentiment (12.7%) compared to "breakthrough" posts (10.8%).

| Spike Type   | Positive % | Neutral % | Negative % |
|:-------------|:-----------|:----------|:-----------|
| breakthrough | 16.2       | 73.0      | 10.8       |
| comparison   | 21.0       | 74.1      | 4.9        |
| meme         | 15.9       | 71.4      | 12.7       |
| personal     | 13.9       | 79.1      | 7.0        |
| tutorial     | 27.6       | 60.9      | 11.5       |

**Growth Insight:** Comment sentiment can serve as an early indicator of content quality and audience reception. High positive sentiment (e.g., 27.6% for tutorials) suggests content that resonates deeply and provides value, indicating strong potential for sustained engagement. Monitoring sentiment can help identify successful content types before overall engagement peaks.

---

## Limitations
- Data is derived from a single, specific event (Claude source code leak), limiting generalizability to other product launches or viral events.
- Sentiment analysis relies on keyword matching across 1,163 comments, which may not capture the full nuance of human emotion compared to advanced NLP models.
- "Engagement score" is a composite metric and its exact weighting across platforms (e.g., likes, shares, comments, views, upvotes) is not specified, potentially affecting cross-platform comparisons.
- The dataset is a snapshot from a competitive intelligence pipeline, and may not represent 100% of all relevant posts or authors across all platforms.
- The analysis window is limited to the immediate aftermath of the event, potentially missing long-term decay or sustained engagement patterns.

---

## Summary: Claude's Growth Playbook in 10 Rules

1.  **Ignite Early:** Leverage developer-centric platforms like HN, where the first post appeared at 0 hours, to kickstart the viral cascade.
2.  **Amplify with Creators:** Prioritize community creators, who generated 30.6x more views than official channels, with Fireship alone reaching 2,592,415 views.
3.  **Strategize Content Types:** Balance content volume, as 45.5% of "breakthrough" posts had a median engagement of only 4, while "meme" posts, despite being 9.8% of volume, achieved a mean engagement of 588,136.
4.  **Optimize Timing:** Schedule HN posts between 19-23 UTC for 35-49 average points, and Reddit posts on Sunday for an average score of 4344.0.
5.  **Craft Viral Titles:** Use high-lift words like "leaks" (22.7x lift) and "tutorial" (22.7x lift), while avoiding low-lift terms like "anthropic" (0.5x lift).
6.  **Account for Decay:** Prepare for rapid engagement decay, especially on Reddit, which showed a Day 0 velocity of 0.2011 but dropped to 0.0001 by Day 6.
7.  **Focus on Pareto Winners:** Concentrate efforts on creating high-impact content, as the top 10% of posts on X captured 80% of engagement from just 8.5 posts.
8.  **Engage Key Influencers:** Identify and collaborate with the top 5 authors, who collectively drove 96.5% of total engagement across 702 unique authors.
9.  **Prioritize Media:** Always include media in posts on Reddit and X, as they drive 8.1x and 9.7x higher median engagement, respectively, compared to text-only posts.
10. **Monitor Sentiment:** Use comment sentiment, such as the 27.6% positive sentiment for "tutorial" posts, as an early signal for content that resonates strongly with the audience.