---
name: seo-campaign
description: Runs the AEO and SEO campaign for truerevenuepartnerships.com from Justin's autonomous SEO kit. Use for any SEO or AEO work on the site, the daily SEO job, or a question about where we rank or get cited.
---

# The SEO campaign

Justin's two kits are here. `kit/` is the operating system and `library/` is the research behind it.

## Where things are

| What | Where |
|---|---|
| The operating charter | `kit/AUTONOMOUS-SEO-CHARTER.md`. It's the whole method in one file |
| Your role as director | `kit/roles/campaign_director.md`. You own the campaign and do the specialist roles one task at a time |
| Each specialist role | `kit/roles/` |
| The campaign's state | `/workspace/revenue-partnerships/gtm-box/seo/`: `checkpoint.json`, `board.json`, `knowledge/`, `work/`, `metrics/`, `reports/` |
| The research | `library/playbook/`, `library/agent/`, `library/source-notes/` (152 video notes) |
| Page templates | `library/templates/` |

## Each run

1. Check STOP.
2. Read `checkpoint.json` and `board.json`, then the owner direction in this skill.
3. Take the next READY task on the board, the one nearest the bottleneck. Do that task only.
4. Read its role in `kit/roles/`, and check the result against its acceptance line.
5. Save the work in `work/`, update the board and `checkpoint.json`, and say what the next task is.
6. Write your heartbeat, counting what really happened: `found=` for pages or queries read, `drafted=` for finished drafts.

If nothing is ready because something's missing, say exactly what's missing and put `blocked=1` in your heartbeat.

## Justin's rules win over the kit

The kit is generic. Where it differs from these, these win.

- **Scope:** the kit's board is truerevenuepartnerships.com. findmemoneyapp.com is worked through RankSpot alone, under the charter's findmemoneyapp.com rules. Never touch DNS, or the forwards from the old site.
- **Live changes:** the box has no write access to the site. Finished work stays in `work/` as a release package, with the exact files and checks. Claude Code or Justin deploys it. Every deploy is his yes.
- **New spend:** none beyond RankSpot within the charter's cap. Articles only through `box/rankspot.py`. Unknown cost means no.
- **Messages and submissions:** none. Directory listings, citations and outreach stay as drafts until he approves that type.
- **Copy:** Justin's claims exactly as he states them. No em or en dashes. First names only. No invented results. No prices on the main pages.
- **`/ai-revenue-os/`:** it's `noindex` on purpose. Leave it out of the sitemap.
- **No timelines:** ignore the kit's "three working days" and its day-30, day-60 and day-90 reviews. Plan by what's ready and what it waits on, and never promise a ranking, a citation or a date.

## Owner grant

There isn't one yet, so this runs in the kit's local-draft mode: research, plans and drafts, with nothing live and nothing spent. `/workspace/revenue-partnerships/gtm-box/seo/config/authority.json` records that. Only Justin can widen it.

## Missing, and what each one gives

| Missing | Gives |
|---|---|
| Search Console | Real queries, impressions and the AI reporting. Without it, say the baseline is a gap. Never invent one |
| `TREG_API_KEY` on the box | Search data, backlinks and AI visibility checks |
| Write access to the site repo | Release packages become pull requests |
