---
name: content-engine
description: >
  Turn one idea or one recording (a YouTube video, a podcast guest spot, a consented call, a voice
  memo) into a week of drafts for YouTube, X and LinkedIn in one file: a video brief or upload prep,
  Shorts cut points, a thread, 3 single posts, an X Article, 2 LinkedIn posts with hook-lab first
  lines, a document carousel and the newsletter section, with a proposed calendar. Drafts only. Use
  for Daily content when an idea or recording waits in requests/.
metadata:
  version: "0.1.0"
  play: "E1 (replaces G1) in the private plays research, CONTENT.md"
---

# content-engine

Role: `content-seo`. Play E1 (replaces G1): why it is here, its proof and its risk are in `CONTENT.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Daily content `5 22 * * *` when an idea or recording waits in `requests/channels/` or `requests/content-seo/`; chat "engine: <idea or link>" from Justin.

## Steps

1. Read the latest `daily/<date>/channel-read.md` for this week's format tests and cadence.
2. Get the source: captions or transcript (Whisper if needed). A call needs the client's consent on file; describe clients, never name them. A podcast clip needs the host's OK when the host owns the recording.
3. Pull the 5 strongest moments: a number, a story, a mistake, a how-to, a contrarian take, with start and end times. Each piece below carries one of them as its first-hand detail.
4. YouTube: for a finished video, upload prep (3 titles, description, chapters, tags, the AI-use setting if realistic synthetic content is in it); for an idea, a brief (3 titles, 3 thumbnail concepts, a 30-second hook, an outline). Shorts: 3 to 5 cuts of 20 to 45 seconds from Justin's own footage only, each with a hook line and on-screen words, cut with Studio's "Edit into a Short" so it links back.
5. X: 1 thread, 3 single posts with different hooks from the same source, and 1 Article of 1,000+ words when the source is long. Run the ranker check from `x-outlier-drafts` on each (replies and shares, read to the end, no bait, no link in the body).
6. LinkedIn: 2 posts with the hook lab's 3 first lines each and the niche check from `linkedin-ghostwriter`; 1 document carousel of 8 to 12 slides (cover hook, one point a slide, a closing question) rendered to PDF from `context/brand/`; the newsletter section for the weekly edition. Links in the first comment.
7. Calendar: a proposed slot per piece, spread so no platform gets two of Justin's posts within 3 hours. Start at 1 long video and 2 to 3 Shorts a week, 1 to 3 X posts a day, 3 LinkedIn posts a week; the Friday read moves these.
8. Write it all to `requests/justin/content-<date>-<slug>.md` (one section a channel) and a row per piece in each owner's queue (`requests/channels/`, `requests/social/`). Types `youtube_publish`, `x_post`, `linkedin_post` are ask-first; the first post on each channel waits for Justin. Justin publishes X and LinkedIn by hand from his own device; uploads go up private.
9. Log what was made and from which source in `daily/<date>/content-seo.md`.

## Guards (every run, in this order)
1. `context/STOP` exists: do nothing that reaches a person or a record.
2. `python3 repo/guards/scripts/suppression.py check "<who>"` before drafting to anyone. Held: drop that person.
3. `python3 repo/guards/scripts/send_guard.py <type> --routine "<routine>"` before any send or post. Anything but `auto` is a draft in `requests/justin/`.
4. Any paid call: `python3 repo/guards/scripts/spend_guard.py <plan-id> <usd>` (scrape rungs add `--pool scrape`).
5. Never: paid enrichment (Clay, Apollo, Hunter, ZoomInfo and the like), CAPTCHAs, getting past a login wall or a limit, auto-likes, follows or DMs, stating a price or terms.
6. X and LinkedIn: the bot never posts, replies, comments, likes, follows or messages through a browser, and never signs its cloud browser into Justin's X or LinkedIn, even when a type is marked auto. Justin publishes there by hand from his own device.

## End of run

`python3 repo/guards/scripts/beat.py write content-seo '<line>' found=N drafted=N sent=N`, then `daily/<date>/content-seo.md` with only what this run did.

## KPI

Pieces drafted per source; pieces Justin publishes; impressions, follows and leads tagged per source (read Fridays).
