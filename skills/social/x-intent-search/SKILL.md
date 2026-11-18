---
name: x-intent-search
description: >
  Find buyers on X with Grok's native X search: posts from the last 24 hours asking for AI or
  automation help or complaining about a tool, scored 1 to 10, logged with evidence, and handed to
  sales-crm. Read only. Use in the Radar sweep.
metadata:
  version: "0.1.0"
  play: "L1 (and C3) in the private plays research, PLAYS.md"
---

# x-intent-search

Role: `social`. Play L1 (and C3): why it is here, its proof and its risk are in `PLAYS.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Radar sweep and Needs-you `5 14 * * *`.

## Steps

1. Run the saved queries in `context/x-intent-queries.md` (create it with this start set if it is missing: "need help with AI", "looking for someone to automate", "anyone recommend an AI agency", "alternative to <tool>", "<tool> is so bad", "hire a VA" plus AI). Last 24 hours, English, not replies to our own posts.
2. Score each post 1 to 10: is this a business owner with a real need Justin's offer solves, now? Keep 7 and up.
3. Log each kept one in `daily/<date>/x-intent.md`: post URL, the quoted problem (one line), handle, bio, site, score, reason.
4. Dedupe against Lead Radar and `suppression.py`.
5. Find the site and a public contact email from the bio link or site (free pages only; Scrapebox rung 0).
6. Hand each one to sales-crm as a row in `requests/sales-crm/` with the evidence. Also log recurring questions as topics in `requests/channels/topics.md`.
7. Never reply, quote, like, follow or DM on X. A reply Justin may want is an `x_reply` draft in `requests/justin/`.

## Guards (every run, in this order)
1. `context/STOP` exists: do nothing that reaches a person or a record.
2. `python3 repo/guards/scripts/suppression.py check "<who>"` before drafting to anyone. Held: drop that person.
3. `python3 repo/guards/scripts/send_guard.py <type> --routine "<routine>"` before any send or post. Anything but `auto` is a draft in `requests/justin/`.
4. Any paid call: `python3 repo/guards/scripts/spend_guard.py <plan-id> <usd>` (scrape rungs add `--pool scrape`).
5. Never: paid enrichment (Clay, Apollo, Hunter, ZoomInfo and the like), CAPTCHAs, getting past a login wall or a limit, auto-likes, follows or DMs, stating a price or terms.
6. X and LinkedIn: the bot never posts, replies, comments, likes, follows or messages through a browser, and never signs its cloud browser into Justin's X or LinkedIn, even when a type is marked auto. Justin publishes there by hand from his own device.

## End of run

`python3 repo/guards/scripts/beat.py write social '<line>' found=N drafted=N sent=N`, then `daily/<date>/social.md` with only what this run did.

## KPI

Intent leads at 7+ a day; share that become conversations.
