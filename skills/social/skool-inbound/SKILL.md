---
name: skool-inbound
description: Find inbound leads on Skool - sweep the non-AI groups Justin's account is in for members asking for help with AI, automation or a virtual assistant, or describing a problem a VA or an AI agent would fix; judge each one, hand real askers to sales-crm with the post as evidence, draft replies, join new free non-AI groups, and draft collaboration notes to group owners. Use for the Skool sweep, joining groups, and anything about Skool leads.
---

# Skool inbound

**Worker mode (WORKERS.md).** The read and the first judgment run on the worker: `skool-read` on the browser host Justin picked, then `skool-score` (Codex). This role reads only the 4s and 5s from the digest and writes the replies and owner notes. The steps below are the same, with steps 1 to 3 done for you.

Justin, 2026-11-12: "Generate inbound leads on SKOOL.com by searching all the groups, finding all the different potential opportunities, specifically in the non-AI groups obviously. We'd find everybody who's talking about needing help, talking about AI, potentially needing help, or a virtual assistant."

Read `repo/gtm-box/campaigns/skool.md` for the offer and what is approved.

## The account

Justin signs Skool in by hand in the bot's own browser (NEEDS-JUSTIN). That one session is the only way in: no copied cookie, no password, no second account. Read with GETs from inside the signed-in page, at a person's pace (a page every 5 to 15 seconds). The first browser check, 403, 429, sign-in prompt or account warning stops Skool for the day: write `blocked=1`, tell lead, and never work around it.

## Which groups

- **In:** free groups whose members run or work in a business that could buy from us: trades, local services, agencies, coaches, e-commerce, real estate, lending, health and fitness businesses, creators, operators, sales teams.
- **Out:** AI, automation, "agency launch" and prompt groups (their members sell what we sell), paid groups, and any group whose rules ban promotion or DMs. Keep the group's rules in `data/skool/groups.md`.
- **Joining:** at most 5 free groups a day from https://www.skool.com/discovery. A join form that asks for an email, a phone, a card or answers about Justin: fill nothing, list the group for Justin.

## The sweep

1. List the groups the account is in. For each, read posts and comments newer than the last sweep (keep the cursor in `data/skool/cursor.json`). `gtm-box/box/skool_scrape.py` does this read when the signed-in Chrome answers on debug port 9224 (it prints `blocked` otherwise); if it doesn't answer, read the same pages through the browser yourself.
2. Keyword pass (code, free): keep any post or comment with a need signal. Start from these and grow the list in `data/skool/signals.txt` from what really converts:
   - AI: "use AI for", "ChatGPT for my business", "AI agent", "automate", "automation", "Zapier", "GoHighLevel workflow", "chatbot", "AI receptionist", "missed calls", "follow up with leads".
   - VA: "virtual assistant", "need a VA", "hire an assistant", "overwhelmed", "can't keep up", "drowning in admin", "no time for", "who do you use for", "looking for someone to".
   - Pain: "leads going cold", "no one follows up", "spending hours on", "inbox", "scheduling", "data entry".
3. Judgment pass (you): is this a real business owner or operator asking, or venting about a problem a VA or an agent fixes? Not a job seeker, not a seller, not a how-to question with no need behind it. Score 1 to 5. Keep 3 and up.
4. For each kept person: `python3 repo/guards/scripts/suppression.py check "<name> <group> <profile url>"`. Held means drop them.
5. Hand each 4 or 5 to sales-crm as `requests/sales-crm/skool-<date>-<n>.md`: name, group, the post link, the exact words they used (quoted, short), score, and the reply draft. sales-crm writes the CRM.
6. Draft a reply (message type `skool_reply`: a helpful public comment answering their question first, then one line that Justin does this for businesses) and, only where the group allows DMs, a DM (`skool_dm`). Run `send_guard.py skool_reply --routine "<routine>"`. Until Justin marks it auto, it is a draft in `requests/justin/`.
7. Group owners: pick the 3 best groups of the day and draft a collaboration note (`skool_owner_note`) from what the group is really about: a free workshop for their members, a guest post, a co-hosted call. No deal, share or price.

## Copy

Plain, short, first names, no em or en dashes. Answer the person's real question first. Never name a price, never promise a result, never say "DM me" in a group that bans it. Clients described, never named.

## What counts

A lead counts only when sales-crm has the person in GoHighLevel and they engaged (replied, booked). A post found is `found`, a draft is `drafted`. End with `beat.py write social '<line>' found=N drafted=N sent=N leads=N blocked=N`.
