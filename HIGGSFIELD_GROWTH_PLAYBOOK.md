# Higgsfield Growth Playbook
## Derived from 16-Month Multi-Platform Analysis of Claude's Viral Growth
### HackNU 2026 · Growth Engineering Track · Execution Document

> **Data provenance:** Every recommendation cites a specific finding number from `PLAYBOOK_ANALYSIS.md` or a documented metric from `COUNTER_PLAYBOOK.md`. No vague strategy. No hallucinated benchmarks.
>
> **Higgsfield context:** AI video generation platform. 20M+ creators, 5M videos/day. 846K Instagram followers, 35K TikTok. Celebrity organic adopters: Madonna, Snoop Dogg, Will Smith. Target audience: filmmakers and content creators — NOT developers. Competes with Sora, Runway, Pika.

---

## 1. Executive Summary: Three Growth Opportunities

### Opportunity A — Activate the Unused Celebrity Signal
**ICE Score: Impact 9 / Confidence 8 / Ease 7 → Total: 24**

Madonna, Snoop Dogg, and Will Smith used Higgsfield organically. Elon Musk shared Higgsfield content on X. None of this was activated into a sustained growth moment. Finding 10 shows that @karpathy's "vibe coding" tweet (6.9M views, Feb 2025) compounded into 74M total views across 346 downstream posts over 16 months — because the term was named and seeded, not just celebrated once. Higgsfield has an equivalent ignition moment sitting unused. The opportunity: package the celebrity proof into every creator outreach, coin a term for AI-assisted filmmaking from a credible creator's voice, and let the cascade do the rest.

### Opportunity B — Close the TikTok Gap Before a Competitor Does
**ICE Score: Impact 8 / Confidence 9 / Ease 8 → Total: 25**

Higgsfield has 846K Instagram followers and 35K TikTok followers — a 24x gap for a video-native product. TikTok's algorithm distributes based on completion rate and engagement velocity, not follower count (Finding 12: @MangoLassC, 6.8K followers, generated 2.85M views, a 415x ratio). The product already generates TikTok-native content; the distribution infrastructure is simply absent. This is the fastest-closable structural gap in Higgsfield's growth picture.

### Opportunity C — Engineer the "Switching Story" Narrative
**ICE Score: Impact 8 / Confidence 8 / Ease 6 → Total: 22**

Finding 14 documents the most persistent organic growth narrative in 16 months of Claude data: "Why I Switched From ChatGPT to Claude" — 333 posts across 4 platforms, running since February 2026, generating 170,513 peak engagement without a single Anthropic-seeded post. Finding 13 confirms that Claude content performs 25% better on r/ChatGPT (mean 5,770) than on r/ClaudeAI (mean 4,593). The equivalent for Higgsfield is seeding "I switched from Runway/Sora to Higgsfield" in r/VideoEditing, r/premiere, and r/AfterEffects — competitor-territory communities where the audience has purchase intent and is open to switching.

---

## 2. AARRR Funnel Analysis

### Acquisition — Seed the Cascade, Not the Content

**Claude finding cited:** Finding 7 — Community YouTube = 29x official channel reach. Fireship's single video on the source code leak (2.59M views) beat Anthropic's entire official YouTube output by 13x on the same event, with zero coordination.

**Higgsfield tactic:** Identify 3 Tier 1 creators in the filmmaker/VFX space (Corridor Crew at 8.8M subs, Film Riot at 1.3M subs, and one respected working cinematographer) and give them unrestricted Pro access 2 weeks before any major feature drop. No scripted deliverables. No embargo language. The goal is a genuine "this is what it can actually do" video — the credibility signal that Fireship provides for developer tools. Budget: ~$900 in Pro access (6-month licenses). Expected equivalent reach from one Corridor Crew video: 500K–2M views vs Higgsfield's current organic YouTube baseline.

**Secondary acquisition lever:** Finding 4 shows Reddit Sunday = 2.7x Thursday average score. Schedule all community-targeted Reddit drops — comparison posts, workflow showcases — for Saturday evening so they peak Sunday morning. Do not post on Thursday or Friday.

---

### Activation — Make the First Output Undeniable

**Claude finding cited:** Finding 3 — Shock/scandal-adjacent content has a median floor of 353,005 views on X — the highest consistent floor in the dataset. Feature-forward content (launches, announcements) has median views of 4,642. The gap is 76x.

**Higgsfield tactic:** Redesign the new-user onboarding flow so the first output is a demonstrably "impossible" clip — something that makes new users immediately say "this shouldn't work." This is not a marketing decision; it is an activation decision. The first output a user generates determines whether they post it or delete it. If they post it, Higgsfield gets a free shock-adjacent organic post with a 353K median floor. If they delete it, the acquisition spend was wasted. Measure: % of users who generate and share their first output within 48 hours of signup (target: >15%). If under 5%, the problem is the default prompt, not the distribution.

---

### Retention — The Personal Story Engine

**Claude finding cited:** Finding 3 — Personal story content has the most consistent median engagement ratio (median 914 vs breakthrough's median of 4). Finding 11 — @bcherny's personal, unreviewed tweets generated 44.3M views vs @AnthropicAI's 7.2M combined. The inside voice is the retention driver because it creates an ongoing relationship, not a one-time announcement.

**Higgsfield tactic:** Identify one founder or lead engineer willing to post raw — no PR review, no approval loop. Content types that work from Finding 11: "I've been training this model for 8 months and here's what surprised me," hidden feature reveals, genuine failure stories. This person needs full creative autonomy. The constraint is not content guidelines — it is that the posts must be written in the first person and must not read like marketing copy. Target: 2M+ views/month from a single internal voice within 60 days of activation.

---

### Revenue — Comparison Content Drives High-Intent Conversion

**Claude finding cited:** Finding 13 — r/ChatGPT (competitor community) delivered mean score 5,770 for Claude content vs r/ClaudeAI's 4,593. Finding 5 — "chatgpt" in a post title = 15x lift on HN. Comparison framing works because the audience in competitor communities already has purchase intent — they are paying for a similar product.

**Higgsfield tactic:** Run a "same prompt" comparison series — identical prompts submitted to Higgsfield, Runway, and Sora, output shown side-by-side without voiceover. Post in r/VideoEditing and r/premiere (competitor territory, not r/aivideo where the audience is already converted). Frame: "I tested all three on the same scene." Do not post from the official Higgsfield account — post from a creator account with a genuine filmmaking history. Track conversion: UTM-tagged Pro trial links in every comparison post. Target: >50 signups per post within 72 hours. If under 10, the quality comparison is not winning — fix the product, not the distribution.

**Warning from the data:** Finding 10 shows comparison framing has a 381 median on X — the second-worst category. The format works when the quality clearly wins. Running comparison content before the product is demonstrably superior is a conversion liability, not an asset.

---

### Referral — The Cascade Mechanical Design

**Claude finding cited:** Finding 14 — The "Why I Switched" narrative ran 333 posts across 4 platforms organically, generating more sustained engagement than most official launches. Finding 2 — The 3-wave cascade structure means content that ignites on one platform predictably spreads to others within 12–48 hours if the ignition is strong enough.

**Higgsfield tactic:** Build referral into the output UX, not the invite flow. Every Higgsfield video should have a minimal, tasteful attribution in the corner ("Made with Higgsfield") that is easy to leave on and hard to perceive as watermarking. When a video generated with Higgsfield goes viral on TikTok or Instagram, the attribution becomes a passive referral engine — exactly the mechanism behind "vibe coding" spreading for Claude (Finding 10). Complement with an explicit program: any user whose Higgsfield output crosses 100K views gets a free Pro upgrade. This creates aligned incentives — users want to post quality outputs, which is also Higgsfield's acquisition mechanism.

---

## 3. Top 5 Growth Experiments

### Experiment 1 — Corridor Crew Pre-Brief

**Hypothesis:** If we give Corridor Crew unrestricted Pro access 14 days before the next major Cinema Studio feature drop and brief them on the specific capability, then their organic reaction video will generate >500K views within 7 days because community creators beat official channels 29x (Finding 7) and the VFX-expert credibility transfer is the equivalent of Fireship for developer tools.

**Success metric:** Single community video >500K views within 7 days of posting.
**Traffic/budget estimate:** $300 in Pro access (6-month license). Zero paid distribution.
**Timeline:** Initiate outreach 21 days before feature drop. Brief at 14 days. Video posted at launch day.
**ICE Score: Impact 9 / Confidence 7 / Ease 8 → Total: 24**

---

### Experiment 2 — TikTok Velocity Sprint

**Hypothesis:** If we post the top 5 highest-performing user-generated Higgsfield outputs (proven on Instagram/Reddit) natively to @higgsfield_ai TikTok weekly for 30 days, then TikTok followers will grow from 35K to >150K because TikTok's algorithm distributes based on completion rate not follower count (Finding 12), and content that already proved on other platforms is pre-validated.

**Success metric:** TikTok followers >150K at day 30. Completion rate >40% on posted clips.
**Traffic/budget estimate:** $0 additional (repurposing existing high-performing content). 1 hour/week of curation and upload time.
**Timeline:** Starts immediately. Evaluate at day 30. Scale to 500K target by day 90 if traction confirmed.
**ICE Score: Impact 8 / Confidence 9 / Ease 9 → Total: 26**

---

### Experiment 3 — Inside Engineer Account Launch

**Hypothesis:** If a Higgsfield founder or lead engineer posts 3x/week on X without PR review for 60 days, then total reach from that account will exceed the official @higgsfield.ai account because Finding 11 shows @bcherny (engineer, 124 tweets) generated 44.3M views vs @AnthropicAI + @claudeai combined 7.2M views — a 6x ratio that held across multiple tweet types.

**Success metric:** Inside account total views/month > official account total views/month by day 60.
**Traffic/budget estimate:** $0. Time cost: ~3 hours/week for the engineer.
**Timeline:** Account active within 7 days. Evaluate at 30 days (minimum sample). Commit or pivot at 60 days.
**ICE Score: Impact 9 / Confidence 8 / Ease 6 → Total: 23**

---

### Experiment 4 — Competitor-Territory Reddit Seeding

**Hypothesis:** If a creator with genuine filmmaking history posts a "same prompt" comparison of Higgsfield vs Runway vs Sora in r/VideoEditing and r/premiere on Sunday morning, then the post will generate >500 upvotes and >30 Pro trial signups within 72 hours because Finding 13 shows competitor-territory communities deliver 25% higher mean scores than own-community posts, and the switching-frame narrative is the most durable organic growth engine in our dataset (Finding 14).

**Success metric:** >500 upvotes, >30 UTM-attributed Pro signups within 72 hours.
**Traffic/budget estimate:** $0 budget. Requires a real creator account with post history (not a throwaway).
**Timeline:** First post within 14 days. Run monthly. Evaluate 3-post sample before scaling.
**ICE Score: Impact 7 / Confidence 7 / Ease 7 → Total: 21**

---

### Experiment 5 — Cascade Alert System Activation

**Hypothesis:** If we deploy the trigger detection pipeline (monitoring Runway/Sora/Pika/Kling launches with velocity >0.3, age <4h) and auto-generate creator briefs within 30 minutes of a competitor launch, then at least 1 in 3 competitor launches will generate a Higgsfield comparison post within the 0–6h cascade window because Finding 2 shows the maximum impact window is 0–16 hours and Finding 9 shows competitor launches generate 3x more discourse than own-product launches.

**Success metric:** Response content live within 6h of competitor trigger on ≥60% of monitored launches. Compare signups in weeks with response vs weeks without.
**Traffic/budget estimate:** $0 pipeline cost (open APIs). 15 minutes human review per trigger.
**Timeline:** Pipeline deployable within 7 days (adapting existing architecture from ARCHITECTURE.md). Evaluate at 60 days (minimum 3 trigger events).
**ICE Score: Impact 8 / Confidence 7 / Ease 7 → Total: 22**

---

## 4. Platform-Specific Playbook

### YouTube
**Key finding:** Finding 7 — Community YouTube = 29x official channel. Fireship alone beat Anthropic official 13x on the same event.

**Tactical breakdown:**
- Do not invest in the official Higgsfield YouTube channel as a primary distribution mechanism. Community creators are the channel.
- Pre-brief tier system: Corridor Crew (8.8M, VFX experts), Film Riot (1.3M, indie filmmakers), one respected working DP. These are the filmmaking equivalents of Fireship/Theo/Matthew Berman for Claude Code.
- Brief protocol: access 14 days early, no required deliverable, single-angle briefing document (one capability, not a feature list), zero embargo.
- Publish official tutorials only for searchable "how to do X in Higgsfield" long-tail queries — not for launch moments. Official channel = SEO. Community channel = virality.
- Timing: From Finding 8, YouTube retains velocity 6+ days (vs HN's 24h cliff). Publish community videos at launch; they compound. Publish official tutorials mid-week (Tuesday–Thursday) for sustained search-driven discovery.

---

### Reddit
**Key finding:** Finding 13 — r/ChatGPT mean score 5,770 vs r/ClaudeAI 4,593 for Claude content. Claude content performs better in competitor communities.

**Tactical breakdown:**
- Primary targets: r/VideoEditing, r/premiere, r/AfterEffects (competitor territory — users are paying for alternative products and are open to switching). Secondary: r/aivideo (already converted audience, lower leverage at early stage).
- Avoid: r/videography and r/filmmakers. Higgsfield scraper data confirms hostile sentiment there: "Disgusting how many creators sell out to AI" (103 upvotes). Do not seed a hostile community — fix product perception first.
- Post format: Comparison (same-prompt side-by-side) or personal workflow story. Never brand-forward posts. Finding 3: personal story median = 914; feature announcement median = 4.
- Timing: Saturday evening post → Sunday peak. Finding 4: Sunday = 2.7x Thursday average score. This is the single most reliable scheduling optimization available at zero cost.
- Account requirement: Real account with post history in relevant communities. New accounts with no karma history get downvoted as spam regardless of content quality.

---

### X / Twitter
**Key finding:** Finding 12 — @MangoLassC (6.8K followers) got 2.85M views (415x ratio). Finding 11 — inside engineer @bcherny generated 44.3M views vs official accounts' 7.2M combined.

**Tactical breakdown:**
- Official account: Maintain and post 3–5x/week. Finding 7 shows X is the one platform where official accounts perform at parity with community (unlike YouTube). Use the official account for same-day response, competitor comparisons, and amplifying creator posts.
- Inside voice: One founder/engineer with full autonomy. Content categories from Finding 11 that consistently performed for @bcherny: origin stories, hidden features, failure stories, tips threads, meme formats. No PR review. Target: 2M+ total monthly views from the inside account within 60 days.
- Celebrity activation: The Elon mention and Madonna/Snoop Dogg usage are the most credible cold-open available. Quote-tweet celebrity organic use with feature attribution ("This is Higgsfield's Soul ID feature — see how it maps Madonna's expression"). Do not just retweet — attribute to the capability.
- Small account amplification: Monitor for non-mega accounts posting about Higgsfield with early velocity (500+ views in first 2 hours). Comment from the official account within the first hour. Finding 12: TikTok and X both distribute based on early engagement velocity — official engagement is interpreted as a quality signal.

---

### Hacker News
**Key finding:** Finding 4 — 22:00 UTC = 4x baseline (39.7 avg pts vs 9.5). Finding 5 — "leaked", "war", "department" = 22–36x title lift. Finding 1 — 88% of posts get ≤5 pts.

**Important caveat from the data:** Higgsfield currently has zero real posts on HN. Claude's HN presence is developer-shaped; Higgsfield's audience is not on HN. HN is not a primary channel. However, it functions as the ignition surface for the cascade (Finding 2), and one high-scoring HN post triggers the YouTube → Reddit cascade.

**Tactical breakdown:**
- Only post to HN for genuinely technical events: a research paper on the video generation model, an open-source component release, a technical architecture post from an engineer. These have authentic HN audience fit. Marketing posts will not score.
- When posting: 22:00 UTC on a weekday (US 6pm ET). Do not post between 04:00–10:00 UTC (Finding 4: 1.6–5.7 avg pts).
- Title language: Lead with stakes, not features. "Higgsfield vs Runway on the same prompt" (comparison, 7,098 avg engagement from Finding 3) beats "Introducing Higgsfield Cinema Studio 2.0." "We open-sourced our video diffusion pipeline" beats "Higgsfield launches new AI video features."
- Alternative: ProductHunt as the ignition surface (more creator-audience aligned than HN). Same cascade mechanic applies — brief YouTube creators before the ProductHunt launch drops.

---

## 5. Growth Levers Prioritized

**Ranked for Higgsfield's specific situation — a video-native product with strong Instagram presence, weak TikTok presence, and an unused celebrity signal:**

### Rank 1 — Improve Conversion Rate
The data shows Higgsfield has 20M+ creators and 5M videos/day generated. If the activation funnel is converting even 1% of output sharers into Pro users, the volume available is massive. Finding 3: shock-adjacent content has a 353K median floor on X. If users are generating shareable outputs and not sharing them, the conversion problem is in onboarding (first output quality) not traffic. Fix this before buying more traffic.

### Rank 2 — Increase Traffic (via Creator Seeding, Not Paid)
Finding 7: community creators = 29x official channel. The budget to reach equivalent impressions via paid is not competitive with one Corridor Crew video. Creator seeding is the highest-ROI traffic lever available. Cost: ~$2,400–$2,600 for a 90-day creator program (per COUNTER_PLAYBOOK.md budget analysis). Equivalent paid media cost for the same impression volume: estimated $50,000–$200,000.

### Rank 3 — Increase Frequency (via TikTok Gap Closure)
The 35K TikTok / 846K Instagram gap means the highest-frequency video platform is being ignored. TikTok's algorithm creates organic repeat exposure (suggested videos, "For You" page) that Instagram Reels does not match. Closing this gap increases the frequency at which existing potential users encounter Higgsfield outputs, without requiring new acquisition spend.

### Rank 4 — Increase LTV (via Comparison Content Conversion)
Finding 13 shows that comparison content in competitor communities delivers the highest conversion intent because the audience is already paying for a competing product. Users who switch after a side-by-side comparison are higher-LTV customers than top-of-funnel signups — they have demonstrated willingness to pay and are making an active product choice, not a curiosity-driven trial.

### Rank 5 — Reduce Churn (via Inside Voice Retention)
Finding 11: @bcherny's sustained 2–9M view performance across multiple tweet types maintained a consistent engaged audience around Claude Code. The mechanism: first-person "I built this" content creates an ongoing relationship. Users who follow the inside engineer account churn less because they feel product investment from the team, not just marketing. This is not measurable in standard churn dashboards — measure it by comparing 90-day retention rates for users who follow the inside account vs those who don't.

---

## 6. Timing & Cascade Strategy: Major Feature Drop Launch Sequence

**Based on Finding 2 — 3-wave cascade: HN fires first (01:13 UTC) → YouTube (7 min) → Reddit (12h) → meme/international (48h+)**

**Designed for Higgsfield's creator-audience shape, not the developer-shaped Claude cascade:**

### T-21 Days: Creator Seeding
- Send pro access to Tier 1 creators (Corridor Crew, Film Riot, target cinematographer) with single-page capability brief. No required deliverable, no embargo.
- Send access to Tier 2 creators (MattVidPro AI, AI Explained, Dequine on TikTok, Yenlik on Instagram) with UTM-tagged Pro trial links.
- Goal: creators have 3 weeks of genuine hands-on time before launch. Authentic reactions come from real use, not rushed demos.

### T-7 Days: Inside Engineer Seeding
- Inside engineer posts a teaser thread on X: "Been working on something for 8 months. Shipping next week. Here's why it's harder than it looks." No feature reveal. Stakes-forward, personal-voice framing (Finding 11 format).
- Expected reach from a properly activated inside account: 500K–2M views for a well-framed teaser.

### T-0 (Launch Day): Multi-Platform Ignition
- **07:00 UTC:** Official X post with best-quality output clip. No feature list — one output, shock-adjacent framing ("We've been trying to make this shot possible for 8 months").
- **08:00 UTC:** Inside engineer posts personal take. First-person, unreviewed.
- **12:00 UTC:** TikTok post of the same clip (native upload, not cross-posted link). Engage with early comments within first hour.
- **22:00 UTC:** ProductHunt launch (not HN — Higgsfield has zero HN presence and a creator audience). If pursuing HN, submit here at exactly 22:00 UTC for 4x baseline (Finding 4).
- Brief Soul ID ambassadors (Dequine and Yenlik) to post their outputs today.

### T+2h to T+16h: Wave 2 — Tutorial and Comparison
- Monitor for creator posts. When Tier 1 or Tier 2 posts, amplify via official account within 30 minutes.
- Post official "same prompt vs Runway/Sora" comparison on X. Finding 3: comparison avg 7,098 vs feature announcements median 4.
- Share to r/aivideo (the primary AI video community — converted audience, fastest initial upvotes).

### T+12h to T+24h: Reddit Activation
- If launch day is not Saturday, schedule Reddit seeding for the following Saturday evening → Sunday peak.
- Post in r/VideoEditing and r/premiere (competitor territory). Personal story or comparison format. Finding 13 principle: reach users who are already paying for competing products.
- Community manager monitors r/aivideo, r/filmmakers, r/videography for organic mentions. One authentic comment from a team account on any thread >50 upvotes.

### T+48h to T+7 Days: Wave 3 — Satire, International, Long-Tail
- YouTube tutorials from Tier 2 creators will surface in this window (Finding 8: YouTube retains velocity 6+ days).
- Monitor for international creator coverage — Higgsfield has a demonstrated international signal (Yenlik, Kazakhstan). Brief Portuguese, Spanish, Arabic-language creators with pro access if the feature is internationally applicable.
- Satire/meme content cannot be manufactured — identify it when it appears and amplify via official channels (quote-tweet, repost to Instagram Stories).

### T+7 Days: Attribution Window Close
- Pull all UTM data from creator links.
- Calculate K-factor per creator: signups / 72h window post-publish.
- Identify which creator/format/platform delivered the highest signup velocity. Replicate that creator and format for the next launch.

---

## 7. 30/60/90 Day Roadmap

### Days 1–30: Infrastructure and Ignition

**Week 1:**
- Deploy trigger detection pipeline (adapt existing `pipeline.py` architecture from ARCHITECTURE.md). Add Runway/Sora/Pika/Kling to competitor watchlist. Connect Slack webhook for alerts. Time: 2 engineering days.
- Identify and reach out to Tier 1 creator targets (Corridor Crew, Film Riot). Lead outreach with: "Elon Musk shared content made with Higgsfield. Madonna and Snoop Dogg used it without being paid. We're giving you access because you'll make something we haven't seen before." Finding 11 principle: lead with social proof and specific work reference.
- Establish inside engineer account. First post within 7 days. No guidelines document — the constraint is authenticity, not compliance.

**Week 2:**
- Begin TikTok velocity sprint: identify top 5 highest-performing Instagram Reels from the past 30 days. Upload natively to TikTok with creator credits. Post schedule: 5x/week minimum.
- Identify real creator account (or creator partner) for Reddit seeding. Build posting history in target subreddits with genuine comments before any promotional post.

**Week 3–4:**
- First competitor-territory Reddit post (r/VideoEditing or r/premiere). Comparison format. Sunday morning. UTM-tagged.
- Review inside engineer account performance at 14 days. If under 50K views/post, adjust voice — more raw, less polished.
- Build creator watchlist CSV: 50 creators scored by views/follower ratio, topic overlap, posting velocity. Top 5 get direct outreach. Update weekly.

**30-day targets:** TikTok >75K followers. Inside account >500K total monthly views. At least 1 Tier 1 creator relationship initiated. Cascade alert system live.

---

### Days 31–60: Scale and Validate

- Launch pre-briefed major feature drop using the T-21 day cascade sequence (Section 6).
- Run 3 Reddit comparison posts in competitor-territory communities. Evaluate signup conversion per post. Kill the format if <10 signups/post. Scale if >30.
- Inside engineer: measure monthly views at day 60. Target: exceed official @higgsfield.ai account total views.
- Activate first "same prompt" comparison campaign on X and TikTok simultaneously. Find out which platform drives higher signup conversion.
- Identify which Tier 2 creator generated the highest K-factor in the launch window. Give them Tier 1 status for next drop.

**60-day targets:** TikTok >200K followers. One community video >500K views from a Tier 1 creator. K-factor >50 signups from at least one seeded creator within a 72h window.

---

### Days 61–90: Name the Movement

- With 60 days of creator relationships built, identify any creator who has naturally described AI-assisted filmmaking in a new way. If a term surfaces: amplify immediately (quote-tweet, embed in feature naming, reference in press kit). This is the "vibe coding" opportunity (Finding 10) — it cannot be manufactured but can be caught and amplified.
- Run the Yenlik entertainment press pitch: "First Kazakhstani female vocalist at COLORSxSTUDIOS used Higgsfield to visualize her performance." Target Variety, Billboard, The Verge culture section — different audience than the tech press already covering Higgsfield.
- Evaluate virality coefficient: % of signups who post publicly about Higgsfield within 30 days. Target: >15%. If <5%, the problem is activation (first output quality), not distribution.
- Run full attribution analysis: which creator, which platform, which format, which day-of-week delivered the highest-converting signups in the 90-day window. Rebuild the Tier 1/2/3 creator list based on actual K-factor data, not assumed fit.

**90-day targets:** TikTok >500K followers. Monthly organic reach >10M across all platforms. Virality coefficient >15%. One cultural moment (term coined, entertainment press hit, or Fireship-equivalent video) documented.

---

## 8. Metrics Dashboard

Track weekly. Baselines derived from Claude data where applicable.

| Metric | Baseline (Claude data) | Higgsfield Week-1 Baseline | 90-Day Target |
|---|---|---|---|
| Community creator views / official channel views | 29x (Finding 7) | Measure at first Tier 1 post | >10x community/official ratio |
| TikTok followers | N/A (different product) | 35K (current) | 500K |
| TikTok follower velocity (weekly) | N/A | ~0 (stagnant) | +15K/week by day 60 |
| Inside account monthly views | @bcherny: 2–9M/post (Finding 11) | 0 (account not yet active) | >2M/month at day 60 |
| Reddit score in competitor communities | r/ChatGPT mean 5,770 for Claude (Finding 13) | Measure first post | >1,000 avg score/post |
| Reddit post timing win rate | Sunday 2.7x Thursday (Finding 4) | Track by day of week | >80% of posts on Saturday/Sunday |
| Creator K-factor (signups per creator / 72h) | Not in dataset (new metric) | Measure from first seeded post | >50 signups from top creator |
| Virality coefficient (% of signups who post within 30d) | Not in dataset | Measure at day 30 | >15% |
| Comparison content win rate (% positive comments) | Not tracked in dataset | Measure on first comparison post | >60% before scaling |
| Response time to competitor launch trigger | Claude example: 7 min (YouTube, Finding 2) | Not measured yet | <6h from trigger to live content |
| Monthly X views (inside account + official combined) | Claude: 70.6M peak (Mar 2026, Finding 9) | Measure at month 1 | >5M by month 3 |
| TikTok clip completion rate | N/A | Measure from first week | >40% |
| Time to "Fireship moment" | Fireship: 2.59M views, same-day (Finding 7) | Not yet triggered | 1 community video >500K views within 90 days |

---

## Execution Checklist (Print and Pin)

**Before every launch:**
- [ ] Tier 1 creators briefed 14+ days early with Pro access
- [ ] Inside engineer post scheduled for T-7 days
- [ ] UTM links generated for every creator
- [ ] Reddit post scheduled for Saturday evening (not launch day if launch day is a weekday)
- [ ] Cascade alert system running; Slack webhook live
- [ ] X post copy uses stakes-forward language, not feature-list language

**Weekly recurring:**
- [ ] Top 5 Instagram Reels uploaded natively to TikTok
- [ ] Creator watchlist updated (50 creators, rescored by weekly velocity)
- [ ] Trigger detection confirmed running (check Slack for any misfires)
- [ ] Attribution dashboard pulled: UTM signups per creator, per format, per platform

**Monthly:**
- [ ] Inside account views vs official account views (must exceed official by day 60)
- [ ] Virality coefficient calculated (target >15%)
- [ ] Reddit comparison win rate audited (target >60% positive before continuing)
- [ ] Creator tier list revised based on actual K-factor, not assumed influence

---

## Summary: 7 Rules for Higgsfield Growth

1. **Close the TikTok gap first.** 35K TikTok vs 846K Instagram is the biggest distribution failure for a video product. Five native TikTok posts per week with proven content costs nothing.

2. **Activate the celebrity signal immediately.** Madonna, Snoop Dogg, Will Smith, and Elon Musk already validated the product. Lead every creator outreach with this. It is the most credible cold open available and nobody is using it.

3. **One inside voice beats the official account 6x.** Finding 11: @bcherny 44.3M views, official Anthropic accounts combined 7.2M. Find the Higgsfield engineer who will post raw, and get entirely out of their way.

4. **Seed competitor communities, not your own.** Finding 13: r/ChatGPT mean 5,770 for Claude content vs r/ClaudeAI 4,593. The Higgsfield equivalent is r/VideoEditing and r/premiere, not r/aivideo. Converted users don't need persuading.

5. **Automate the trigger detection; humanize the response.** The 0–6h window after a competitor launch is the highest-leverage moment (Finding 9: competitor launches generate 3x more discourse than own launches). The pipeline detects it, auto-generates the brief. Human approves in 15 minutes. Without the pipeline, you miss the window every time.

6. **The power law is the whole game.** Finding 1: 88% of posts get ≤5 pts. The question is never "how do we post more" — it is "what creates a top-0.7% post." Volume is noise. One Corridor Crew video outperforms 100 official social posts.

7. **Name the movement before a competitor does.** Finding 10: "vibe coding" compounded to 74M views. "Prompt cinema," "vibe filmmaking," "AI cinematography" are unclaimed. Give credible filmmakers genuine access, zero content requirements, and catch the term when it surfaces.
