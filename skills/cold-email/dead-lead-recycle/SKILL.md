---
name: dead-lead-recycle
description: >
  Recycle leads that finished a campaign with no reply (fresh angle at 15, 30 and 45 days) and check
  sending-inbox health every morning, pausing any inbox over the limits. Use for Lists and data top-up
  and Inbox health.
metadata:
  version: "0.1.0"
  play: "L2 in the private plays research, PLAYS.md"
---

# dead-lead-recycle

Role: `cold-email`. Play L2: why it is here, its proof and its risk are in `PLAYS.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Inbox health and warmup `20 11 * * *`; Lists and data top-up `35 12 * * *`.

## Steps

1. Inbox health: for every sending inbox in PlusVibe and Instantly, read bounce rate, spam placement and warmup score. Over 3% bounce, under 80% inbox placement or a warmup drop: pause that inbox (reducing sends is allowed) and tell lead.
2. Dead leads: list leads whose sequence finished 15, 30 or 45 days ago with no reply, no bounce, no opt-out.
3. Run `suppression.py check` on each. Drop anyone bounced, unsubscribed, suppressed, or already in GoHighLevel as a conversation.
4. Write a new angle per wave (15 days: a different problem; 30 days: a short case; 45 days: a one-line breakup). New copy is `cold_email`, so it is a draft until Justin marks it auto.
5. Re-enrol only from healthy inboxes, never from a domain Justin uses for real mail. Log counts in `daily/<date>/cold-email.md`.

## Guards (every run, in this order)
1. `context/STOP` exists: do nothing that reaches a person or a record.
2. `python3 repo/guards/scripts/suppression.py check "<who>"` before drafting to anyone. Held: drop that person.
3. `python3 repo/guards/scripts/send_guard.py <type> --routine "<routine>"` before any send or post. Anything but `auto` is a draft in `requests/justin/`.
4. Any paid call: `python3 repo/guards/scripts/spend_guard.py <plan-id> <usd>` (scrape rungs add `--pool scrape`).
5. Never: paid enrichment (Clay, Apollo, Hunter, ZoomInfo and the like), CAPTCHAs, getting past a login wall or a limit, auto-likes, follows or DMs, stating a price or terms.
6. X and LinkedIn: the bot never posts, replies, comments, likes, follows or messages through a browser, and never signs its cloud browser into Justin's X or LinkedIn, even when a type is marked auto. Justin publishes there by hand from his own device.

## End of run

`python3 repo/guards/scripts/beat.py write cold-email '<line>' found=N drafted=N sent=N`, then `daily/<date>/cold-email.md` with only what this run did.

## KPI

Replies from recycled leads per 1,000; inboxes healthy; bounce under 3%.
