---
name: collab-blitz
description: The aggressive collaboration campaign - every day find and qualify people to collaborate with (podcast hosts, YouTubers, newsletter writers, Skool and community owners, agencies and software partners, event hosts), research each, draft a personal first note, and track every one through to an agreed collab with a live link. Use for the daily collab list, collab notes, and the collab pipeline.
---

# Collab blitz

Justin, 2026-11-12: "put together a pretty aggressive campaign that will aggressively find collaborations, partners, podcasts, and get cited on engines and SEO." KPI from the charter: 1 to 2 collaborations agreed a day (Justin, 2026-11-09), 1 show or video booked a day (2026-11-07).

Aggressive means volume of good research and fast follow-up, not volume of messages to strangers. Every note is personal and every type is ask-first until its replies prove good.

## The pipeline

`data/collabs/pipeline.csv` (mode 600), one row per target: id, name, kind, audience, link, why them (one line with a source), warm path, owner role, stage, next step, date.

Stages: `found` > `qualified` > `drafted` > `sent` > `replied` > `agreed` > `live` (with the link). `no` is final: run `suppression.py add`.

## Who, by kind, and which role owns the note

| Kind | Where to find them (scrapers first) | Owner |
|---|---|---|
| Podcast and YouTube interview shows | SpeakerAgent, podcast directories, YouTube search for small-business, trades, agency, sales and AI topics | speaker |
| Newsletters (beehiiv, Substack) for business owners | beehiiv and Substack directories and recommendations | partners |
| Skool, Circle and Facebook community owners (non-AI) | skool-inbound's group list | social |
| Agencies, consultants and software tools that serve our buyers and don't sell AI build-outs | partner-opportunity-research | partners |
| YouTubers and creators over 10,000 followers in our buyers' niches | creator pull | social |
| Event and summit hosts, virtual summits, workshops | speakeragent-conferences | speaker |
| Dream 100 | dream dossiers | dream |

## Every day

1. Find at least 50 new targets across kinds (code and free rungs first, `scraper-forge` for any list). Dedupe against the pipeline and run every one through `suppression.py check`.
2. Qualify: real audience of our buyers (owners and operators), active in the last 60 days, not an AI-agency competitor. Keep the best 20.
3. Research each in a few lines: a recent episode, post or issue, what their audience struggles with, the exact collab that helps them (a guest episode, a free workshop for their members, a guest post, a co-hosted live, a swap feature in each other's newsletter, a joint video).
4. Hand each to its owner role through `requests/<role>/collab-<id>.md`; the owner drafts in its own skill's voice. Types: `collab_outreach`, `podcast_pitch`, `skool_owner_note`, `partner_outreach`.
5. Follow up: one nudge at day 4, one at day 10, then stop. Every reply goes to sales-crm.

## Copy rules

Personal first line about their actual work, the collab idea in one sentence, what their audience gets, one easy yes. No price, payout, share or promise of results. No link in the first note. Plain, first names, no em or en dashes.

## What counts

Agreed only with their written yes. Live only with the link (it goes in `data/aeo/citations.md` too). A draft never counts.
