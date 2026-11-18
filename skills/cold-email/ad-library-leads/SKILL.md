---
name: ad-library-leads
description: >
  Find local businesses already paying for ads in the public Meta and Google ad libraries, score each
  1 to 10, flag weak ads and channel gaps (Meta but not Google), and draft a personal first line with
  a better sample ad attached. Use in Prospector research.
metadata:
  version: "0.1.0"
  play: "N1 (L5) in the private plays research, PLAYS.md"
---

# ad-library-leads

Role: `cold-email`. Play N1 (L5): why it is here, its proof and its risk are in `PLAYS.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Prospector research and drafts `50 16 * * 1-5`.

## Steps

1. Pick today's niche and city from `context/prospect-niches.md` (create it if missing with: roofers, plumbers, HVAC, dentists, med spas).
2. In the browser, read the public Meta Ad Library and Google Ads Transparency Center for that niche and city. Public pages only, at a person's pace; stop on any block or limit.
3. For each advertiser: how long the ad has run, format (text only, image, video), the offer, landing page, and whether they run on one channel only. Score 1 to 10: a real business spending money with an obvious gap scores high.
4. Find the site and a public contact email (free public pages only). Run `suppression.py check`.
5. Draft a 3 to 4 line first touch that names the specific ad and the one gap, and attach a short sample of a better ad. Type `prospector_email`, so it is a draft until Justin approves it. No price, no "pay per meeting" offer unless Justin wrote one into `standing-approvals.md`.
6. Write the sheet to `daily/<date>/ad-library-leads.md` (business, ad link, score, gap, contact, draft) and hand approved rows to sales-crm.

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

Advertisers scored a day; drafts approved; replies and calls from this lane.
