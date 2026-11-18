---
name: reply-fast-lane
description: >
  Answer an interested reply fast: sort it, score the company from public pages, draft the reply with
  the booking link and post it to Slack for one-tap approval. Use on the Reply webhook, the Reply
  check, and for inbound podcast, speaking or sponsor invitations.
metadata:
  version: "0.1.0"
  play: "M1 (and P3) in the private plays research, PLAYS.md"
---

# reply-fast-lane

Role: `sales-crm`. Play M1 (and P3): why it is here, its proof and its risk are in `PLAYS.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Event: Reply webhook (PlusVibe, Instantly, GoHighLevel inbound). Fallback: Reply check `15 12-22/2 * * *`.

## Steps

1. Read the reply and its thread. Sort it: interested, question, not now (date), not interested, opt-out, out of office, invitation (podcast, stage, sponsor).
2. Opt-out or not interested: `suppression.py add` at once, record it, stop.
3. Interested or question: read the sender's site and LinkedIn headline (public pages only) and write a 3-line company score: fit 1 to 10, why, risk.
4. Invitation: vet it. Is the show or event real and active? Audience size, any pay-to-play ask (hold that for Justin), red flags.
5. Draft the answer in Justin's voice: answer the question, one line of value, the Cal.com link. No price, no terms.
6. Post to Slack: the reply, the score, the draft, and the approve or edit choice. The type is `reply_book_call`, so the send guard decides.
7. Record the reply and the next step with its date in GoHighLevel (only while `crm-writes: on`; otherwise a row in `requests/sales-crm/`).

## Guards (every run, in this order)
1. `context/STOP` exists: do nothing that reaches a person or a record.
2. `python3 repo/guards/scripts/suppression.py check "<who>"` before drafting to anyone. Held: drop that person.
3. `python3 repo/guards/scripts/send_guard.py <type> --routine "<routine>"` before any send or post. Anything but `auto` is a draft in `requests/justin/`.
4. Any paid call: `python3 repo/guards/scripts/spend_guard.py <plan-id> <usd>` (scrape rungs add `--pool scrape`).
5. Never: paid enrichment (Clay, Apollo, Hunter, ZoomInfo and the like), CAPTCHAs, getting past a login wall or a limit, auto-likes, follows or DMs, stating a price or terms.
6. X and LinkedIn: the bot never posts, replies, comments, likes, follows or messages through a browser, and never signs its cloud browser into Justin's X or LinkedIn, even when a type is marked auto. Justin publishes there by hand from his own device.

## End of run

`python3 repo/guards/scripts/beat.py write sales-crm '<line>' found=N drafted=N sent=N`, then `daily/<date>/sales-crm.md` with only what this run did.

## KPI

Minutes from reply to draft (target under 10); interested replies to booked calls.
