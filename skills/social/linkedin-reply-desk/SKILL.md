---
name: linkedin-reply-desk
description: >
  When Justin says he posted on LinkedIn, draft a reply to each comment from the notification emails
  so he can answer inside the first 90 minutes; and each day draft one angle per new post from the 30
  to 50 people he wants to be seen by, for him to comment on by hand. Use when Justin says "posted"
  and in the LinkedIn routine.
metadata:
  version: "0.1.0"
  play: "L5 and L4 in the private plays research, CONTENT.md"
---

# linkedin-reply-desk

Role: `social`. Play L5 and L4: why it is here, its proof and its risk are in `CONTENT.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

Chat or Slack "posted <link>" from Justin; LinkedIn board, messages and post `45 12 * * *` for the comment queue.

## Steps

1. On "posted": for the next 90 minutes, on each of Justin's messages or on his Gmail notification digests (never the LinkedIn site), list each new comment and draft a reply that adds something: answer, a detail, a question back to that person. Type `linkedin_comment`, ask-first.
2. Justin sends the replies himself, the sooner the better (aim for 15 minutes). He may message 5 to 8 real contacts that it is up; a standing group that trades comments is an engagement pod and is out.
3. Comment queue: `context/linkedin-seen-by.md` lists 30 to 50 people (buyers, agency owners, podcast hosts). From Justin's notification emails, for each new post of theirs write one line: what it says and the angle Justin could add. He writes a few substantive comments a day himself.
4. Commenters on Justin's posts who show buying intent go to sales-crm as a row with the comment link.
5. Never comment, like or reply on LinkedIn through a browser, and never use an auto-comment tool (User Agreement 8.2; LinkedIn blocks automated comments and cuts reach on AI comments).

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

Share of comments answered inside 90 minutes; comments per 1,000 impressions; buyers from comments.
