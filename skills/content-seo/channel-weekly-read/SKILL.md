---
name: channel-weekly-read
description: >
  Every Friday read the week's numbers for YouTube, X and LinkedIn, compare like with like, and write
  what to repeat, what to stop, next week's one format test per platform and whether cadence moves.
  Every content skill reads this file before it drafts. Use for the Channel read routine.
metadata:
  version: "0.1.0"
  play: "W1 (X5, X7, Y4, L8) in the private plays research, CONTENT.md"
---

# channel-weekly-read

Role: `content-seo`. Play W1 (X5, X7, Y4, L8): why it is here, its proof and its risk are in `CONTENT.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Channel read `55 17 * * 5`.

## Steps

1. YouTube: YouTube Studio read-only, or the numbers Justin pastes: per video the impressions click rate, the share still watching at 30 seconds, spikes and dips, traffic source, subscribers gained. Below a few hundred views a video, say the read is noise.
2. X: from X analytics screenshots or numbers Justin pastes: per post the hook, format, time, impressions, replies, profile clicks, follows; link versus no-link posts. Distance to Original Content Rewards (500 verified followers, 500,000 verified impressions in 90 days, replies excluded; confirm the terms on help.x.com).
3. LinkedIn: from the analytics CSV Justin downloads: rank posts by impressions per follower and comments per 1,000 impressions; tag each by opening style, format and topic; note 3-a-week against 5-a-week when that test runs.
4. Compare like with like (same format, same time slot). Pick one format test per platform for next week and say whether cadence goes up, holds or goes down.
5. Write `daily/<date>/channel-read.md`: per platform what to repeat, what to stop, the test, the cadence. Post the 6-line summary to Slack.
6. Read only. Never sign the bot's cloud browser into X or LinkedIn to get numbers; ask Justin for the export or a screenshot.

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

The read lands every Friday; tests run; per-platform follows and leads week over week.
