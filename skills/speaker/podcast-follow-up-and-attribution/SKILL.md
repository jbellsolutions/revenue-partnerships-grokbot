---
name: podcast-follow-up-and-attribution
description: >
  Follow up a podcast pitch once on day 4 and once on day 10, stop on any reply, and turn every booked
  appearance into leads: a tracked link, a GoHighLevel source tag, a how-did-you-hear option and a
  clip plan. Use for the speaker Follow-up routine.
metadata:
  version: "0.1.0"
  play: "P2 in the private plays research, PLAYS.md"
---

# podcast-follow-up-and-attribution

Role: `speaker`. Play P2: why it is here, its proof and its risk are in `PLAYS.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Follow-up `50 20 * * *`.

## Steps

1. For each pitch with no reply: on day 4 and day 10 draft one short follow-up that adds something new (a clip, a stat, a different angle). Type `podcast_follow_up`. Stop on any reply; a no goes to `suppression.py add`; a "later" becomes a dated task.
2. Booked or recorded: write `requests/content-seo/podcast-<show>.md` asking for the episode page or tracked link (`?src=podcast-<show>`), and hand sales-crm a row to create the GoHighLevel source tag `podcast:<show>` and add the show to the "how did you hear about us" options.
3. When the episode goes live: hand the recording link to content-seo (one recording, every channel) and to channels for clips; log the live date.
4. Weekly: count leads and calls with the `podcast:` tag per show, so Justin can see which shows paid off.

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

Follow-ups sent on time; bookings from follow-ups; leads per appearance.
