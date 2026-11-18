---
name: x-outlier-drafts
description: >
  Every day find the X posts in Justin's niche that beat their author's usual engagement, explain why
  they worked, and draft 1 to 3 posts from Justin's own material, each rewritten for replies and
  shares by the open-source X ranker. Drafts only: Justin posts by hand. Use for the X posts and
  replies routine and for breaking niche news.
metadata:
  version: "0.1.0"
  play: "X1, X2 and X6 (was C1) in the private plays research, CONTENT.md"
---

# x-outlier-drafts

Role: `channels`. Play X1, X2 and X6 (was C1): why it is here, its proof and its risk are in `CONTENT.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

X posts and replies `25 14 * * *`; breaking niche news Justin flags in chat.

## Steps

1. Read the latest `daily/<date>/channel-read.md` first: this week's X format test and cadence.
2. Native X search (the GrokBot X connector: search, timeline, mentions, trends; read only) over `context/x-niche.md` (create it if missing with: AI agents, automation for small business, agency owners, AI for sales, GrokBot, Claude Code). Last 48 hours, like floor 500, raised to 2,000 when a niche is noisy.
3. For each outlier: why a stranger stops scrolling, 5 hook options, the format (list, story, screenshot, thread, Article), the claims that need checking. Restate the idea; never reuse wording.
4. Trend scout: niche news under 2 hours old (model launches, agent tools, pricing changes) where Justin has a real view gets a take. No unrelated trending hashtags.
5. Draft 1 to 3 posts from Justin's own material (a build, a call described without the client's name, a number from his work). Every draft carries one first-hand detail; with none, ask Justin for one instead of drafting.
6. Ranker check (xai-org/x-algorithm on GitHub): shares (copy link, DM), replies, quotes and follows weigh far more than likes; reports, mutes, "not interested" and blocks weigh strongly against; posts read to the end are rewarded; a second post from the same author in one feed is discounted. Rewrite each draft for one idea, a specific claim worth answering, no bait. No link in the body unless this week's test says so.
7. Put drafts in `requests/justin/x-<date>.md` with a proposed time spaced at least 3 hours from Justin's last post. `x_post` is ask-first; the first post waits for Justin.
8. Justin posts by hand. The bot never posts, replies, likes or follows on X through the browser (an account doing that was locked read-only on 2026-09-25), even if `x_post` is marked auto. Posting by the bot is only ever through the official X API, and only if Justin adds a key (spend).

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

Drafts Justin posts; impressions, replies, profile clicks and follows per post (read Fridays).
