---
name: x-channel
description: Run Justin's own X account as an AI channel - daily posts and threads from his calls, builds and stories, replies to business owners asking about AI in his niche, and a weekly read of what landed - as drafts Justin posts by hand. Use for X posts, threads, replies and the X channel plan.
---

# X channel

Justin, 2026-11-12: "I want to build the YouTube and X AI channel." Asked whose accounts, he chose "My own accounts" (2026-11-12). So every post speaks as Justin, from his account.

## Access

- **The bot does not post or reply on X through a browser** (2026-11-12). A GrokBot that did was locked read-only on 2026-09-25, and X's developer rules allow automation only through the official API. The GrokBot X connector is read only (search, timeline, mentions, trends, bookmarks). Justin posts the drafts by hand from his own device.
- X's API has no free tier for new developers in 2026 and charges per post (third-party reports, unverified against docs.x.com). So the default is drafts Justin posts by hand. The bot posts through the API only if Justin adds a key, and every API call is spend through `spend_guard.py`.

## What to post (the plan in `data/channels/x-plan.md`)

- **One post a day and one thread a week**, built from real material: a call (client described, never named), something the bot built that day, a Skool or Lead Radar question many people ask, a podcast clip, a Medium piece.
- Formats that work for an AI operator: "here's the agent I set up for a plumber and what it does", a before and after of a workflow, a short how-to answering a real question, a lesson from a call.
- Every post: plain, first person, no em or en dashes, no invented numbers or results, no price. One link at most, and not in every post.
- **Replies:** each day find 10 posts from business owners (not AI people) asking how to use AI, automate, or hire help. Write a brief for each (what they ask, what Justin can add); Justin types the reply himself (`x-reply-desk`). Replies are type `x_reply`.

## Gates

- **The first post waits for Justin's yes.** After that, `x_post` and `x_reply` run under `send_guard.py`: drafts in `requests/justin/` until he marks each auto.
- Never DM, follow in bulk, like in bulk, or use any growth tool. Stop on the first warning, lock or limit, and tell Justin.
- Never post about a client by name, a price, or anything from a private call that the client didn't agree to share.

## Weekly read

Every Monday: posts and replies, impressions, profile visits, link clicks, follows, and any DM or reply that is a lead (to sales-crm). Write `data/channels/x-week-<date>.md`: what to do more of, what to stop.

## What counts

Published only with the post's link. A lead only when sales-crm has them in GoHighLevel and they engaged.
