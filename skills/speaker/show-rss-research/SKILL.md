---
name: show-rss-research
description: >
  Find and rank podcasts for Justin from Apple's free iTunes Search API and each show's RSS feed:
  owner email, last episode date, last five titles, drop shows quiet for 90 days, and make every pitch
  cite one specific recent episode. Use for Show research and Pitch submit.
metadata:
  version: "0.1.0"
  play: "P1 in the private plays research, PLAYS.md"
---

# show-rss-research

Role: `speaker`. Play P1: why it is here, its proof and its risk are in `PLAYS.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Show research `30 13-19 * * *`; Pitch submit `10 21 * * *`.

## Steps

1. Query `https://itunes.apple.com/search?media=podcast&term=<topic>&limit=200` for each topic in `gtm-box/speaker/pitch-details.json` (AI for small business, automation, agencies, founders, sales). Dedupe on the feed URL and against SpeakerAgent's show list.
2. Read each RSS feed: `itunes:owner/itunes:email`, website, last episode date, the last 5 episode titles and descriptions.
3. Drop shows with no episode in 90 days, off-topic, non-English, or that say they don't take guest pitches. Note shows that only take a form.
4. Score: fit (weight 3), reachability (direct email or form), recency, audience signals (reviews, rank). Keep the top ones for SpeakerAgent.
5. Every pitch names one specific recent episode, what was good about it, and the one thing Justin adds next to it. No template phrases; 68% of producers reject pitches that read as AI-templated.
6. `podcast_pitch` goes through the send guard, which decides auto or draft from `context/standing-approvals.md`. A form asking for payment, an account, a sign-in or a CAPTCHA is held.

## Guards (every run, in this order)
1. `context/STOP` exists: do nothing that reaches a person or a record.
2. `python3 repo/guards/scripts/suppression.py check "<who>"` before drafting to anyone. Held: drop that person.
3. `python3 repo/guards/scripts/send_guard.py <type> --routine "<routine>"` before any send or post. Anything but `auto` is a draft in `requests/justin/`.
4. Any paid call: `python3 repo/guards/scripts/spend_guard.py <plan-id> <usd>` (scrape rungs add `--pool scrape`).
5. Never: paid enrichment (Clay, Apollo, Hunter, ZoomInfo and the like), CAPTCHAs, getting past a login wall or a limit, auto-likes, follows or DMs, stating a price or terms.
6. X and LinkedIn: the bot never posts, replies, comments, likes, follows or messages through a browser, and never signs its cloud browser into Justin's X or LinkedIn, even when a type is marked auto. Justin publishes there by hand from his own device.

## End of run

`python3 repo/guards/scripts/beat.py write speaker '<line>' found=N drafted=N sent=N`, then `daily/<date>/speaker.md` with only what this run did.

## KPI

Pitches citing an episode (100%); reply rate (plan on 5 to 18%); shows booked.
