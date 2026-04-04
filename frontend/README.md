# Frontend — Growth Intelligence Dashboard

Next.js + Tailwind frontend for triggering scrapers, running the pipeline, and downloading CSVs.

## Requirements

- Node.js 18+
- Backend running on `http://localhost:8000` (see `../backend/README.md`)

## Setup

```bash
cd frontend
npm install
```

## Start

```bash
npm run dev
```

Opens at `http://localhost:3000`.

## Environment variables

By default the frontend proxies `/api/*` to `http://localhost:8000`. If your backend runs on a different port or host, create a `.env.local` file:

```bash
cp .env.local.example .env.local
# edit NEXT_PUBLIC_API_URL if needed
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard — health status, file counts, recent jobs, quick-download processed files |
| `/scrapers` | Run HN / Reddit / X / YouTube scrapers individually with live job status |
| `/pipeline` | Run full pipeline or individual analysis steps (normalize → classify → rank → visualize) |
| `/downloads` | Browse and download all CSV and HTML output files |

## Other commands

```bash
npm run build   # production build
npm run start   # serve production build
```
