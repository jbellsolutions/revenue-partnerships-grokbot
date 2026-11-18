---
name: x-reply-desk
description: >
  Every evening list 5 to 15 fresh posts from accounts 2 to 20 times Justin's size in his niche and
  write a one-line brief for each (what it claims, the data point or counter-case Justin has). The bot
  writes briefs, not replies: Justin types each reply himself. Use for the X engagement routine.
metadata:
  version: "0.1.0"
  play: "X3 in the private plays research, CONTENT.md"
---

# x-reply-desk

Role: `channels`. Play X3: why it is here, its proof and its risk are in `CONTENT.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

X engagement `45 19 * * *`.

## Steps

1. Keep `context/x-reply-targets.md`: 15 to 25 accounts 2 to 20 times Justin's follower count that his buyers read (create it from the outlier authors in `x-<date>.md` if missing; Justin edits it).
2. Native X search: their posts under 1 hour old (under 3 hours on a quiet day). Skip giveaways, bait and anything off-topic.
3. For each of 5 to 15 posts write a brief: post link, what it claims in one line, the one thing Justin actually has to add (a number, a client case described without the name, a counter-example). No reply text.
4. Put the list in `requests/justin/x-replies-<date>.md`. Justin writes each reply in his own words, varied length, no links, no pitch, never the same reply twice. Type `x_reply` stays ask-first and is never marked auto for bot-written text (X removed about 42,000 AI-reply accounts in 2026).
5. People in those threads asking for help go to social's Lead Radar evidence row for sales-crm, read only.
6. Never reply, like, follow or DM on X through the browser.

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

Replies Justin sends a day (target 10 to 25 once he chooses); profile clicks and follows from replies (read Fridays).
