---
name: linkedin-ghostwriter
description: >
  Draft Justin's LinkedIn posts in his voice from a voice profile of his past posts and transcripts: a
  newsjacking queue from X and niche news, 2 to 3 drafts per idea, 3 first lines from the hook lab on
  each, and a check that someone outside his niche couldn't have written it. Drafts only: Justin posts
  by hand from his own device. Use for the LinkedIn post part of the LinkedIn routine and when Justin
  sends a post idea.
metadata:
  version: "0.1.0"
  play: "L1, L2, L3 and L9 in the private plays research, CONTENT.md"
---

# linkedin-ghostwriter

Role: `social`. Play L1, L2, L3 and L9: why it is here, its proof and its risk are in `CONTENT.md` of the private plays research (researched 2026-11-12). Evidence is thin; treat this as a test and report the numbers.

## When

LinkedIn board, messages and post `45 12 * * *`; chat "post idea: ..." from Justin.

## Steps

1. Read the latest `daily/<date>/channel-read.md`: this week's format test and cadence (start at 3 posts a week, test 3 against 5).
2. Voice profile: `context/linkedin-voice.md` from Justin's last 20 to 30 posts (he pastes them or exports them) and his transcripts: words he uses, openings he likes, rules he follows. Refresh it every 30 posts.
3. Newsjacking queue: X and news items in the niche from the last 24 hours that beat their source's usual reach (X runs a couple of days ahead of LinkedIn). Draft takes on what each means for a small-business owner. Read X and news only; never read or scrape LinkedIn itself.
4. For each idea, 2 to 3 drafts. Each carries one first-hand detail only Justin has (a build, a client described without the name, a number from his work). With none, ask Justin for one instead of drafting.
5. Hook lab on each draft: 3 first lines, one story (start mid-scene, hold back the outcome), one contrarian, one result with its surprising reason. Keep the opener short (40 characters or fewer does best); flag any over 200. A question opener only if it is specific and has stakes. (AuthoredUp, 309,614 posts.)
6. Niche check: could someone outside small-business AI have written this? If yes, rewrite it for one world or drop it. Links go in the first comment, not the body.
7. Put the drafts in `requests/justin/linkedin-<date>.md` with a proposed day (Tuesday to Thursday morning first). `linkedin_post` is ask-first; the first post waits for Justin.
8. Justin posts by hand from his own phone or computer. Never sign the bot's cloud browser into Justin's LinkedIn (a data-centre IP set off unusual-activity warnings in 2026), and never post, comment, like or message there through a browser, even if a type is marked auto.

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

Drafts Justin posts; impressions per follower and comments per 1,000 impressions (read Fridays).
