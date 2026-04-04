# Task Tracker

## Part 1: Scrapers
- [x] Reddit scraper (posts + comments)
- [ ] YouTube scraper (video metadata)
- [x] HN scraper (stories + comments)
- [ ] Data cleaning + merge to master CSV

## Part 2: Analysis
- [ ] Volume over time chart
- [ ] Platform breakdown chart
- [ ] Top content by score
- [ ] Word frequency (high vs low engagement)
- [ ] Controversy map (Reddit)
- [ ] Written playbook analysis (README or separate doc)

## Part 3: Pipeline
- [ ] APScheduler weekly job
- [ ] Run history logging
- [ ] Alert logic (volume anomaly detection)
- [ ] Architecture diagram (Mermaid)
- [ ] Cost estimate (current + 10x)

## Part 4: Counter-Playbook
- [ ] Channel recommendations with rationale
- [ ] Content format specs
- [ ] Timing strategy
- [ ] Metrics to track
- [ ] Tie every recommendation back to data found in Part 2

## Known Issues / Blockers
- PRAW not used: Reddit public JSON API chosen instead (no auth overhead, sufficient for hackathon read-only needs).
- YouTube scraper not yet started.