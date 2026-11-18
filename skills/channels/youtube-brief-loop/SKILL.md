---
name: youtube-brief-loop
description: >
  Twice a week list niche YouTube videos far above their channel's usual views, draft 2 briefs for
  Justin's channel (3 titles, 3 thumbnail concepts, a hook, an outline) to load into YouTube's own A/B
  test, and draft replies to comments on his own videos. Use for the YouTube briefs routine.
metadata:
  version: "0.1.0"
  play: "Y1, Y5 and Y6 in the private plays research, CONTENT.md"
---

# youtube-brief-loop

Role: `channels`. Play Y1, Y5 and Y6: why it is here, its proof and its risk are in `CONTENT.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

YouTube briefs and the weekly read `25 18 * * 1,4`.

## Steps

1. Read the latest `daily/<date>/channel-read.md`: what to repeat, which title or thumbnail to test, cadence.
2. Outliers: niche videos from the last 14 days with views far above their channel's median (3x or more), from public YouTube pages. Note the title pattern, the thumbnail (a frozen moment, four or five words), the first 30 seconds' hook, the length.
3. Draft 2 briefs: 3 titles, 3 thumbnail concepts, a hook for the first 30 seconds, an outline, built on Justin's own story and numbers. Never copy a title or thumbnail. Once a video is public, Justin loads the 3 titles and thumbnails into YouTube's A/B test, which picks by watch time.
4. Cadence to hold: 1 long video a week and 2 to 3 Shorts cut from it (content-engine writes the cuts). Judge titles in batches of 10 videos, not one.
5. Comment desk: new comments on Justin's own videos since the last run. Draft a reply to each worth answering (type `youtube_reply`, ask-first); questions go to `requests/content-seo/topics.md`; buyers go to sales-crm with the comment link. No auto-replies, no auto-hearts, no comments on other channels.
6. Put briefs and replies in `requests/justin/youtube-<date>.md`. `youtube_publish` is ask-first and uploads go up private.
7. Never make a mass-produced or templated video, re-post someone else's footage, or put an AI persona on camera giving business advice. Realistic synthetic content gets the AI-use setting in Studio.

## Guards (every run, in this order)
1. `context/STOP` exists: do nothing that reaches a person or a record.
2. `python3 repo/guards/scripts/suppression.py check "<who>"` before drafting to anyone. Held: drop that person.
3. `python3 repo/guards/scripts/send_guard.py <type> --routine "<routine>"` before any send or post. Anything but `auto` is a draft in `requests/justin/`.
4. Any paid call: `python3 repo/guards/scripts/spend_guard.py <plan-id> <usd>` (scrape rungs add `--pool scrape`).
5. Never: paid enrichment (Clay, Apollo, Hunter, ZoomInfo and the like), CAPTCHAs, getting past a login wall or a limit, auto-likes, follows or DMs, stating a price or terms.
6. X and LinkedIn: the bot never posts, replies, comments, likes, follows or messages through a browser, and never signs its cloud browser into Justin's X or LinkedIn, even when a type is marked auto. Justin publishes there by hand from his own device.

## End of run

`python3 repo/guards/scripts/beat.py write channels '<line>' found=N drafted=N sent=N`, then `daily/<date>/channels.md` with only what this run did.

## KPI

Briefs Justin films; title tests run; click rate and 30-second retention per video (read Fridays).
