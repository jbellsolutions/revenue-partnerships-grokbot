---
name: cold-campaigns
description: The four cold email campaigns and how each day runs: lists, sends, replies, bookings, and keeping the CRM agent in sync. Use for anything about the Australian owner, Australian trades, US lender or US affiliate campaigns.
---

# The cold email campaigns

Justin, 2026-11-07: 1,000 a day to the Australian crowd, 1,000 a day to American targets, 1,000 a day to affiliates. Every Maildoso inbox goes in except the 100 the held campaign (`INSTANTLY_HELD_CAMPAIGN`) sends from, so 900, shared by each campaign's part of the volume.

| Campaign | Who | Inboxes | Emails a day | CRM |
|---|---|---|---|---|
| `au-owners` | Australian business owners over AUD 1M a year | 150 | 500 | AI Guy |
| `au-trades` | Australian trades. Justin's list of about 7,000 replaces the starter list when he uploads it | 150 | 500 | AI Guy |
| `us-lenders` | US hard money brokers and real estate and business lenders | 300 | 1,000 | Funding |
| `affiliates` | US coaches, consultants, marketers and others who could refer | 300 | 1,000 | AI Guy |

Targets, tracked per campaign: 5% replies and 1% deals. They're targets, not forecasts. Measured so far: AI Guy / Everybody 0.91% human replies and 0.06% interested, Trades 2.0 AU/NZ 3.28% human replies.

## Lists

```bash
python3 /workspace/revenue-partnerships/gtm-box/cold/list_build.py build <campaign>
python3 /workspace/revenue-partnerships/gtm-box/cold/list_build.py import <campaign> <file.csv>
python3 /workspace/revenue-partnerships/gtm-box/cold/list_build.py report
```

Lists are in `/workspace/revenue-partnerships/gtm-box/cold/lists/`, mode 600. Read counts with `report`. Never put a row in a note, a Slack post or a commit.

## Every lead reaches the CRM

Loading a list queues every lead for GoHighLevel. AI Guy's leads go straight to `box/crm.py`'s outbox, and the CRM drain writes them. Funding's wait in this folder until `python3 /workspace/revenue-partnerships/gtm-box/cold/crm_sync.py flush` pushes them, and `status` shows what's waiting. A lead counts as in the CRM only after GoHighLevel has answered for it. If a location is down, it stays queued and nothing is lost.

## Every reply

You pull the reply. `replies` records it and `closer` works the deal. All three see the same record.

1. `python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py replies` writes new replies to `/workspace/revenue-partnerships/gtm-box/cold/inbox.jsonl`.
2. Sort each one: yes, question, not now, no, out of office.
3. A no goes on the blocklist and is done everywhere.
4. Record every reply except out of office: `python3 /workspace/revenue-partnerships/gtm-box/cold/crm_sync.py reply <email> <label> "<their words>" <campaign>`. An AI Guy reply goes to the `replies` profile, which decides the intent. A Funding reply goes to `replies-inbox.jsonl`, the Reply check puts it in Justin's queue, and a yes or a question opens a card at `Contacted` in `Partner Recruiting`.
5. Reply only under an approved type. Each campaign's reply lines are in `cold/sequences/<campaign>.json`. Anything about price or terms, anyone upset, and anything unclear goes to Justin.

A reply stops that person's sequence on its own. PlusVibe's AI labels it, and a subsequence starts from the label for someone who said yes but hasn't booked. If the AI missed it, such as a lender answering with a list of states, set it yourself: `python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py label <campaign> <email> INTERESTED`, or `NOT_NOW`.

## Every booking

The Booked stop job reads Cal.com and both GoHighLevel locations' calendars every 15 minutes. Anyone on a campaign's list who booked comes out of the campaign and its subsequences, whether or not they replied first. Cal.com needs `CAL_API_KEY`, and the job reports blocked without it. To stop one person by hand: `python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py stop <campaign> <email>`.

- AI Guy: `crm_stage.py` moves the card to `Call booked` on the booking itself. `closer` drafts the confirmation and writes the pre-call brief in its Call prep job.
- Funding: the card moves to `Call Booked` in `Partner Recruiting`. The confirmation and pre-call work go to Justin's queue, because `closer` can't write to that location.

## Before any campaign sends

`plusvibe.py launch` refuses without these first two.

- Justin has approved its copy once, and `cold/approved/<campaign>` exists.
- `plusvibe.py copy-check <campaign>` shows no gaps. Copy is written with `{{first_line}}`; PlusVibe fills a custom field only as `{{custom_first_line}}`, and `load-copy` does that swap. Read step 1 in PlusVibe's Preview Email before approving. The booking link, postal address and business name live in `cold/copy-vars.json`, and `load-copy` fills them in.
- The inboxes have had the warmup Maildoso calls for after a move between tools.
- The sending health check passed.
- The footer has a real postal address and a working way to opt out.
- For Australia: each address has a consent basis under the Spam Act 2003, and the email identifies the sender. A bought list isn't the same as an address the business published itself.
