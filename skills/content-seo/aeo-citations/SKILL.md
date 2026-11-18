---
name: aeo-citations
description: Get truerevenuepartnerships.com and Justin cited in AI answers (Google AI Overviews and AI Mode, ChatGPT, Claude, Perplexity, Grok) and ranked in search, with RankSpot for AI-visibility checks, keywords, backlinks and articles, and Medium, podcasts, partner sites and forum threads as citation sources. Use for the AI visibility read, article picks, the citation queue, links and keywords, and any question about where we rank or get cited.
---

# AEO: get cited by AI

Justin, 2026-11-12: "AEO being AI engine optimization: getting found in the Google Answers, ChatGPT results, and Claude results. I want to get cited by AI." "We'll connect the tool called Rank Spot."

The playbook is `../seo-campaign/` (Justin's SEO kit and the source-linked library). This skill is the AEO loop on top of it, and the money rules for RankSpot.

## How AI engines pick who to cite (what we act on)

1. They cite pages that answer the exact question in the first lines, with a plain answer, a named source and a date. Every page and article we write opens with a 40 to 60 word direct answer.
2. They cite what many independent places say. One claim on our site is weak; the same claim on Medium, a podcast page, a partner's blog, a directory, a Reddit or forum thread and a YouTube description is strong. Every role's public work is a citation source: speaker's shows, partners' guest posts, channels' videos, Medium.
3. They read structure: FAQ blocks, `FAQPage` and `Organization`/`Person` schema, `llms.txt`, clean headings, a fast page a crawler can read.
4. They name entities. The business and its owner, named the one way `context/owner.md` gives, and "truerevenuepartnerships.com" said the same way everywhere.

## The prompt panel

`data/aeo/prompts.md` holds 30 to 50 questions a buyer asks an AI ("who can set up an AI agent for my small business", "how do I automate lead follow up in GoHighLevel", "best AI consultant for a plumbing company"). Build it from call transcripts, Skool posts, Lead Radar asks and People Also Ask. Keep it; add only questions real people ask.

## RankSpot

RankSpot is the AI-visibility and SEO execution layer (MCP `https://mcp.rankspot.ai`, key `RANKSPOT_API_KEY`, one workspace per site; this bot has only truerevenuepartnerships.com). Prices from rankspot.ai/pricing (read 2026-11-12): reading data, tracking competitors and edits with our own AI are free; an AI visibility check is $0.004 per prompt per engine; keyword update $0.15 and backlink update $0.07 per site; an article $3; indexing $0.01; a Google search $0.0025; a page read $0.004. It spends only its prepaid credit, minimum top-up $10 (Justin's, on NEEDS-JUSTIN).

Rules:
- Reading is free: do it every run.
- Every paid RankSpot action goes through `python3 repo/guards/scripts/spend_guard.py rankspot-<action>-<date> <usd>` and needs a `rankspot` line in `context/spend-approvals.md`. Articles go only through `python3 gtm-box/box/rankspot.py generate aiguy <action id>`, which holds the month's cap.
- **Never** use RankSpot's "email found" or its outreach sends. That is paid enrichment and a send to a person. Link outreach is drafted by partners, from public contact pages, under an approved template.
- RankSpot's own schedules (daily prompt checks, keyword and backlink updates) bill the credit by themselves: set them in RankSpot's Settings > Schedules only with Justin's yes, and say the monthly estimate (its default settings come to about $90 a month; 50 prompts daily is most of it).

## The routines

| Routine | Does |
|---|---|
| AI visibility read (weekly) | Read the last 7 days of AI-visibility results: which prompts name a competitor and not us, which pages the engines cite, which fanout questions we have no page for. Write `data/aeo/visibility-<date>.md` with the three biggest gaps and a fix for each (page, Medium piece, guest post, video, forum answer). Hand fixes to the role that owns them |
| SEO daily | One task from `../seo-campaign/` board nearest the bottleneck. One task, checked against its acceptance line |
| Article pick (twice a week) | Pick the one write_article action with the best real-person question, under the month's cap. Never publish: an article reaches the site only through a pull request Justin merges |
| Links and keywords (weekly) | Archive keywords nobody asks; add up to 10 from calls and People Also Ask. Rank backlink gaps by how earnable they are; top 5 as briefs to `requests/partners/` |
| Citation queue | `data/aeo/citations.md`: every place we could be mentioned (podcast show notes, directories, partner pages, Medium, YouTube, forum threads RankSpot spots). Each row: source, status (idea, drafted, live with link), owner role |

## What counts

Cited counts only with a saved AI answer that names us or links to us (the RankSpot check, the prompt, the engine, the date). Published counts only with a live link. Track the share of panel prompts that cite us, per engine, week over week.
