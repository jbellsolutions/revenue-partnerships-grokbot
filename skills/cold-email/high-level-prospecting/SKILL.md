---
name: high-level-prospecting
description: One-to-one emails to senior people, a few a day, each researched and written for that person. Covers who to pick, how to research through One API and Consulti, how to write in Charm Offensive's voice, the checks a draft must pass, Justin's approval, and how approved emails reach PlusVibe. Use for anything in the high-level lane.
---

# High-level prospecting

Not a campaign with merge fields. Each email is written for one person, from what they and their company have actually done, and Justin approves it before it goes.

## Who

- Owners and chief executives of established companies, USD 10M a year and up, in the US and Australia. `prospect/config.json` holds the search.
- Partners who could send several clients: agency owners, fractional executives, consultancies with the right clients.
- Never: anyone suppressed, anyone already in a campaign, a current client, anyone on the do-not-mention list (given at intake), anyone in the held campaign.

## The loop

```bash
python3 /workspace/revenue-partnerships/gtm-box/prospect/prospect.py find --n 10     # Consulti, inside the day's credit cap
python3 /workspace/revenue-partnerships/gtm-box/prospect/prospect.py next --n 5      # who's waiting for research
python3 /workspace/revenue-partnerships/gtm-box/prospect/prospect.py draft <email> --subject "..." --body-file /tmp/b.txt --followup-file /tmp/f.txt --why "..."
python3 /workspace/revenue-partnerships/gtm-box/prospect/prospect.py status
python3 /workspace/revenue-partnerships/gtm-box/prospect/prospect.py load            # approved drafts into PlusVibe, up to the day's cap
```

## Research, before a word is written

1. Their site through One API `web.fetch` or `web.scrape`, free. `browser.read` only when the page needs JavaScript.
2. One `treg.web.search` on the person and the company: a launch, a hire, an interview, a post they wrote.
3. `consulti enrich-linkedin` when their LinkedIn URL is known and the role isn't clear.
4. Write `--why` as the two or three facts the email rests on, each from a source you read. If nothing specific turns up, don't draft. Mark them in your note and move on.

## Writing

Use `charm-offensive-foundation`, `charm-cold-email` and `jon-buchan-copywriter`. The shape:

- Open with their first name and one observation only someone who looked would make. No compliment about it.
- One line on why you're writing to them, specifically.
- What Justin does, in his own claims and words. His claims, exactly: he helped turn a struggling Sydney startup from $30k/mo to $700k/mo in less than a year, and what his AI workflows do is ranked in the top 0.02% globally. Nothing else with a number in it.
- A small, easy ask: whether it's worth a conversation. No link in the first email, no calendar.
- 50 to 150 words. A 1 to 7 word subject, lower case reads more personal, no "AI" in it.
- The follow-up, 15 to 90 words, adds one new thing: a relevant result, a thought on their situation. Never "just following up".

`prospect.py draft` refuses dashes, merge tags, links, prices that aren't his claims, timelines, guarantees and stock phrases. A refused draft says what to fix.

## Approval and sending

- A draft lands in Justin's queue as `/workspace/revenue-partnerships/gtm-box/queue/prospector/<id>.md`. He approves from his Mac with `prospect.sh approve <id>`. Nothing on this computer can approve.
- Later, once he trusts the lane, he can mark `prospect-first-touch` auto in guardrails.json. Then a draft that passes every check is approved by that rule. Until then, every one waits for him.
- `load` adds approved drafts to the PlusVibe campaign "High-level 1:1" as leads carrying their own subject, email and follow-up, up to `daily_max` a day. PlusVibe sends from the Google inboxes Justin attaches to that campaign, once he launches it.
- Replies arrive in PlusVibe like any campaign's. `cold-email` sorts them, `replies` records them, and `closer` works them to the call. A booking takes them out through booked-stop.

## AgentMail

AgentMail's terms forbid cold outreach, so it never sends a first email here. `prospect/agentmail.py` answers only a message someone sent us, and refuses anything else in code. Good uses: a person who wrote to one of our AgentMail addresses, a newsletter you subscribed to for research, an inbound question. An opt-out goes on its block list with `agentmail.py block`.
