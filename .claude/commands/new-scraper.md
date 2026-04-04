---
description: Scaffold a new platform scraper with all standard boilerplate
---

Create a new scraper for platform: $ARGUMENTS

Requirements:
- File: scrapers/[platform]_scraper.py
- Read @docs/platform-notes.md for this platform's API details
- Include: credentials from .env, rate limit handling, error logging, timestamped output
- Output schema: platform, content_id, text_content, score, engagement_signal, timestamp, url
- End with: if __name__ == "__main__": run with limit=5 smoke test