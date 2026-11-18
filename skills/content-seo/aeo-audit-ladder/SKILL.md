---
name: aeo-audit-ladder
description: >
  Turn RankSpot's free AI-visibility read into a short audit of how AI answer engines see a prospect's
  business, as the free first step of an audit ladder Justin prices. Use when sales-crm asks for an
  audit, and to draft the audit offer post.
metadata:
  version: "0.1.0"
  play: "M4 in the private plays research, PLAYS.md"
---

# aeo-audit-ladder

Role: `content-seo`. Play M4: why it is here, its proof and its risk are in `PLAYS.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

AI visibility read `45 14 * * 1`; any `requests/content-seo/audit-*.md`.

## Steps

1. For an audit request: run RankSpot's free reads for the prospect's brand and 5 buyer questions in their niche. Paid RankSpot actions only through `spend_guard.py`.
2. Write a 1-page audit: which engines mention them, who gets cited instead, the 3 gaps that matter most, and what fixing them would take. Describe; don't promise rankings.
3. Hand it to sales-crm as `requests/sales-crm/audit-<name>.md` for the reply. The offer note is type `aeo_audit_offer`.
4. Prices: none. The ladder (free audit, paid audit, fix sprint) has prices only when Justin writes them into `context/standing-approvals.md`; until then every mention of a paid step goes to `requests/justin/`.
5. Offer post: draft an X post offering a few free audits; `x_post` is ask-first and the first post on X waits for Justin. Answers to it go to sales-crm; no automated DMs.

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

Audits delivered; audits to calls; paid audits once priced.
