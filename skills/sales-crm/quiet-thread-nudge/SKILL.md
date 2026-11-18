---
name: quiet-thread-nudge
description: >
  In the pipeline sweep, find open deals where our message was last and the thread has been quiet 3
  business days, draft one short nudge (at most 3 a thread), tag records KEEP, HOLD or SKIP, and write
  tomorrow's call briefs. Use for the Pipeline sweep and Call prep.
metadata:
  version: "0.1.0"
  play: "M2 in the private plays research, PLAYS.md"
---

# quiet-thread-nudge

Role: `sales-crm`. Play M2: why it is here, its proof and its risk are in `PLAYS.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Pipeline sweep `25 13,17,21 * * *`; Call prep `5 11 * * *`.

## Steps

1. List open GoHighLevel opportunities (read only). For each one: who sent the last message, when, and how many nudges so far (tag `nudge:N`).
2. Tag it: KEEP (active, a next step is due), HOLD (waiting on them inside 3 business days, or a dated "later"), SKIP (suppressed, lost, or 3 nudges already sent).
3. KEEP with our message last and 3 business days quiet: draft a 2 to 3 line nudge that adds one new thing (a short case, a question, a resource). Never "just checking in". Type `crm_follow_up`.
4. Call prep: for each call on tomorrow's calendar, write a one-page brief in `daily/<date>/call-briefs.md`: who, company, what they said (quoted), the likely objection, the one outcome to aim for.
5. Write the stage moves only on evidence, and only while `crm-writes: on`.

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

Open records with an owner, next step and date (target 100%); nudges that get a reply; show rate.
