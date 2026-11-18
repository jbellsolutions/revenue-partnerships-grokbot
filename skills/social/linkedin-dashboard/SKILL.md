---
name: linkedin-dashboard
description: Operate Justin's LinkedIn Engagement Dashboard (the Organic Flywheel, on Railway) through its agent API — check status, work the hot-post board (done / save / remove), add posts and AI-service influencers by URL, pull a post's commenters into the lead list, and read the leads. Use when asked to run, check, or work the LinkedIn dashboard, the influencer list, hot posts, or the daily lead list.
---

# LinkedIn Engagement Dashboard — agent operating guide

The dashboard tracks people who **sell AI services** (agencies, AI SDR/outbound,
automation, consulting, AI marketing) and average **50+ comments** a post. Their
fresh high-comment posts are where Justin's leads gather. Your job is to keep
that board worked: pull the good comment sections into the lead list, check
posts off, save the ones to revisit, clear the noise, and grow the list.

- Dashboard (humans): `<LINKEDIN_DASH_URL>/influencers` (set LINKEDIN_DASH_URL at intake)
- Agent API base: `<LINKEDIN_DASH_URL>/api/agent`
- Code: the dashboard's own repo (`dashboard/lib/radar.ts`
  holds the logic; `dashboard/app/api/agent/*` the routes)

## Auth

Every call needs `Authorization: Bearer <token>`. The token is `AGENT_API_TOKEN`
on the Railway `dashboard` service. Read it from `$LINKEDIN_DASH_TOKEN`, else from
`~/.config/linkedin-dashboard/agent-token`. Never print it, log it, or paste it
anywhere. The dashboard's browser password does **not** open the API.

```bash
DASH="${LINKEDIN_DASH_URL:?set LINKEDIN_DASH_URL at intake}/api/agent"
TOKEN=${LINKEDIN_DASH_TOKEN:-$(cat ~/.config/linkedin-dashboard/agent-token)}
dash() { curl -sS -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" "$@"; }
```

## Endpoints

| Call | What it does |
|---|---|
| `GET  $DASH/summary` | Counts: qualified influencers, hot / saved / done posts, jobs pending. Start here. |
| `GET  $DASH/posts?view=hot` | The board. `view` = `hot` (last 48h at 50+ comments, plus hand-added posts from the last 14 days), `saved`, `done`, `removed`. `limit` up to 200. |
| `POST $DASH/posts` `{"url": "<post url>"}` | Add a post. Returns `job_id` (HTTP 202). |
| `POST $DASH/posts/<id>` `{"action": "…"}` | `done`, `undone`, `save`, `unsave`, `remove`, `restore`, or `pull` (queue its commenters + likers into the lead list; returns `job_id`). |
| `GET  $DASH/influencers` | The measured list, highest average first. `?cat=ai_agency` filters; `?removed=1` lists removed people. |
| `POST $DASH/influencers` `{"url": "https://www.linkedin.com/in/…"}` | Add a person. They are measured and put on the list whatever their average. Returns `job_id`. |
| `POST $DASH/influencers/<id>` `{"action": "remove"\|"restore"}` | Remove = off the list for good (the daily radar won't re-add them). |
| `GET  $DASH/jobs/<job_id>` | `queued` → `running` → `done` (`stats`) or `failed` (`error`). The worker drains a job every 2 minutes. |
| `GET  $DASH/leads?days=7` | People pulled from comment sections, newest first: comment and qualify verdict (`icp_fit` true / false / null = review, `icp_reason`). Filter with `&fit=qualified\|review\|rejected`. |

Categories: `ai_agency`, `ai_sdr_outbound`, `ai_automation`, `ai_marketing`,
`ai_consulting`, `ai_voice`, `ai_training`, `ai_product`.

## The daily routine

The worker scans every listed influencer at 11:00 UTC and sends Justin a Slack
brief at 12:00 UTC. Work the board after that.

1. `GET summary`. If `jobs_pending` is high, let it drain before queueing more.
2. `GET posts?view=hot`. For each post, decide:
   - **Worth mining** (on-topic for buyers of AI services, real discussion in
     the comments) → `pull`, then `done` once the pull job finishes.
   - **Worth a second look later** (good author, thin comments so far) → `save`.
   - **Noise** (giveaway "comment X to get Y" bait, off-topic, hiring posts) →
     `remove`.
3. `GET posts?view=saved` — anything saved more than ~3 days ago: pull it or
   remove it. The saved list should not grow forever.
4. Grow the list when you find a strong seller: `POST influencers`, then check
   the job. A `failed` job saying the profile isn't public means it can't be
   measured from public data — don't retry it.
5. Check the leads: `GET leads?fit=qualified`. Note any that stand out, with the
   comment that makes them worth a look. The same people are in Justin's lead Sheet.
6. Report to Justin in a few lines: what you pulled, saved, removed and added,
   and which leads stand out, with post links. Never paste the token.

Leads land in Justin's Google Sheet, a plain list with no controls. Each morning
the worker also pulls up to three fresh discussions there by itself. Outreach is
separate: Justin adds post URLs to the OutFlo campaign and its native AI writes the
messages. A pull of a post that public scraping can't see falls back to a team
member's account scraping it (capped at one post per account per day); the job's stats say so
(`fallback.account_scrape`) and the leads arrive a few minutes later.

## Rules

- **Outreach is Justin's.** Never launch, resume or edit an OutFlo campaign.
  Everything here (pull, save, remove) only builds the list.
- **Pulls and adds spend credits.** A pull scrapes public data (Apify, with
  ScrapeCreators as backup); an influencer add costs ~7 ScrapeCreators
  credits, a post add 1. Pull the posts worth mining, not every post.
- **Public data only.** Never use a logged-in LinkedIn account to scrape or
  measure, and never Justin's session. The one exception is built in and
  capped: the worker's team-account fallback. Don't trigger it on purpose or
  try to raise its cap.
- **Removing is reversible** (`restore`), but a removed influencer stays off the
  automatic radar until restored. Don't remove someone just because a single
  post is weak.
- No paid enrichment services (Apollo, Hunter, ZoomInfo, Clay, GetLeads).

## Troubleshooting

| Response | Meaning |
|---|---|
| `401 missing or wrong bearer token` | Wrong or missing token. |
| `503 AGENT_API_TOKEN is not set` | The API is switched off on Railway. Tell Justin. |
| `400 That isn't a LinkedIn post URL` | Use `linkedin.com/posts/…` or `/feed/update/urn:li:activity:…`. |
| Job `failed`, "profile isn't public" | Not measurable from public data. Leave it. |
| Job stuck `queued` > 10 min | The worker may be down. Check Railway `worker` logs, or tell Justin. |
