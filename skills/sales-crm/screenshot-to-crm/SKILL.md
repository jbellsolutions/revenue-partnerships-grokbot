---
name: screenshot-to-crm
description: >
  Turn a screenshot, business card, forwarded email or DM that Justin drops in Slack or chat into a
  clean GoHighLevel contact with a source tag and next step. Use whenever Justin shares a lead in any
  format.
metadata:
  version: "0.1.0"
  play: "M3 in the private plays research, PLAYS.md"
---

# screenshot-to-crm

Role: `sales-crm`. Play M3: why it is here, its proof and its risk are in `PLAYS.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Chat or Slack from Justin. Not a routine.

## Steps

1. Read the image or text. Pull out: name, company, role, email, phone, where they came from (source), what they want, and any date mentioned.
2. Mark every field you can see as seen, and every field you inferred as a guess. Never invent an email or phone.
3. `suppression.py check`, then search GoHighLevel for duplicates by email, phone and name.
4. New contact: draft the contact, source tag (`src:<channel>`), note with the context, and a task with a dated next step. Existing contact: draft a note and the next step on the existing card.
5. Write it only while `crm-writes: on`; otherwise put the row in `requests/sales-crm/` and show Justin the draft in one message.

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

Leads Justin shares that reach the CRM the same day.
