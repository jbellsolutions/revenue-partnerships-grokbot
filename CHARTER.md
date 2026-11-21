# Project charter: Revenue Partnerships 3.0

Every agent loads this page before its first run of the day. What is sold is in [OFFER.md](OFFER.md); what Justin has said must hold is in [MASTER-PROMPT.md](MASTER-PROMPT.md).

## Purpose

Two jobs, set by Justin on 2026-11-20. First, get Justin a fractional role: Dream 100, Dream 500 and cold leads send a plain email from a real person to a few companies he would work inside, and Lead Radar finds businesses hiring a virtual assistant or an AI role for that email ([fractional/MESSAGES.md](fractional/MESSAGES.md)). Second, keep the rest running as before: partners, collaborators and influencers, SpeakerAgent on podcasts, content, and AEO and SEO, on the partnerships message. The team runs everything in front of the call so Justin's time goes to calls, content and speaking.

Done well: owners replying about a fractional role, partners and hosts replying every day, calls on Justin's calendar, every conversation on record, and nothing sent, spent or posted that he didn't say yes to.

## The team: nine functions, nine agents, and the lead

Each function is its own Grok agent, and the lead is the tenth: the one Justin talks to ([TEAM.md](TEAM.md)). An agent works as one or more of the base kit's roles; a routine's first line names both (`Agent: dream-500. Role: dream.`).

| Function | Its agent | Roles the agent works as | Revenue Partnerships 3.0 ($2,000 + a percentage) | Revenue OS ($5,000) |
|---|---|---|---|---|
| Dream 100 | [dream-100](team/dream-100.md) | [dream](roles/dream.md) | on | on |
| Dream 500 | [dream-500](team/dream-500.md) | [dream](roles/dream.md) | on | on |
| Partners, collaborators, influencers | [partners](team/partners.md) | [partners](roles/partners.md), creator pull in [social](roles/social.md) | on | on |
| SpeakerAgent | [speaker](team/speaker.md) | [speaker](roles/speaker.md) | on | on |
| Sales agent (replies and the CRM) | [sales-crm](team/sales-crm.md) | [sales-crm](roles/sales-crm.md) | on | on |
| Content | [content](team/content.md) | [content-seo](roles/content-seo.md) (daily content), [channels](roles/channels.md), LinkedIn in [social](roles/social.md) | on | on |
| Cold leads | [cold-email](team/cold-email.md) | [cold-email](roles/cold-email.md) | | on |
| Lead Radar | [lead-radar](team/lead-radar.md) | [social](roles/social.md) | | on |
| AEO and SEO | [aeo-seo](team/aeo-seo.md) | [content-seo](roles/content-seo.md) | | on |

The [lead](team/lead.md) agent runs on every tier. The data lane (lists and scrapers) runs on the cold leads agent, or on the lead when cold leads is not on the tier. This install runs all nine (tier `revenue-os`): ten agents, 41 routines, at most 9 on one agent of the 50 a bot allows. The tier is one line in `context/owner.md`; `python3 repo/tools/team.py list --tier <tier>` lists its agents and `python3 repo/tools/tier.py <tier>` its routines and worker jobs. Each function's process, settings example and prompts are in `repo/agents/<function>/`.

## The loop

```
 FIND                              REACH (his yes per type)          REPLY           BOOK           CRM
 dream     Dream 100, Dream 500 ─┐
 partners  partners, collabs,    ├─▶ dream, partners, speaker,   ─▶ sales-crm   ─▶ sales-crm  ─▶ the CRM
           influencers, creators │   channels, social               (every reply,   (booked,       (one writer)
 speaker   shows, stages         │                                   the person's    call brief)
 Revenue OS tier adds:           │                                   note first)
 cold-email lists and sequences  │
 social     Lead Radar askers   ─┘
 content and channels feed every lane with posts and videos; on the Revenue OS tier content-seo gets the business named by AI engines and found in search.
 lead plans the day from the worker's digest, posts the scoreboard and writes the vault.
```

1. **Find.** The bot's own research and scrapers first. The Dream 100 and Dream 500 lists are private and given at intake.
2. **Reach.** A message goes out only with Justin's yes for its type; until then it is a draft in his queue. LinkedIn goes through OutFlo or his own computer.
3. **Reply.** Every reply from every lane goes to sales-crm, which reads the person's note, answers, and records a dated next step.
4. **Book.** sales-crm takes it to a booked call on Justin's calendar and writes the call brief.
5. **Record.** Every message drafted, sent or received is in the conversation log, and the person's note in `vault/People/` grows with every reply.

## The scoreboard

Posted daily by lead to the Slack channel and the Notion Scoreboard named at intake. No targets are set in this pack: Justin gives them at intake, and lead reports against them.

| Measure | Counts when |
|---|---|
| Dream 100, Dream 500 and cold leads reached with the fractional email, and replies from each | A logged send; a logged reply |
| Conversations about a fractional role | A calendar entry, reported only by sales-crm |
| Businesses found hiring a virtual assistant or an AI role | A judged post with its link |
| Partners, collaborators and influencers agreed | A reply or a signed note saying yes |
| Shows and stages booked | A host's confirmation or a calendar entry |
| Content published | A live link |
| Replies answered the same day | The conversation log |
| Calls booked | A calendar entry, reported only by sales-crm |
| A fractional role agreed; offers sold, by tier | Justin reports it |
| Lead Radar askers kept, AI engines naming the business | The sending tool's count; a judged lead with its post; a saved AI answer |
| Roles silent for more than 26 hours | The heartbeat |

A draft never counts.

## Handoffs between agents

Through files in the shared workspace only, never an agent's chat memory. The inboxes are named by role; [TEAM.md](TEAM.md) says which agent reads each.  `daily/<date>/<role>.md` for what each agent did (each appends its part under its agent id), `requests/<role>/<id>.md` for work handed over, `requests/justin/` for Justin's queue.

| From | What | To |
|---|---|---|
| Any role | A reply from anyone, or a new person for the CRM | sales-crm |
| Any role | A list, a scraper or a data question | cold-email (the data lane) |
| Any role | A show, a stage, a summit | speaker |
| Any role | A collaborator, partner, newsletter or community owner | partners |
| Any role | A creator or influencer | social |
| Any role | A good story, or a question many people ask | content-seo and channels |
| dream | A dossier with a warm path | partners or speaker |
| Any role | Price, terms, the percentage, the guarantee, an upset person, an account warning, a spend | `requests/justin/` |
| sales-crm | A booked call | lead (scoreboard) and Justin's calendar |

## Workspace

One workspace, shared by all ten agents. `/workspace/revenue-partnerships/`: `repo/` (this pack), `gtm-box/` (the engine's working copy), `context/` (owner, routines-on, standing-approvals, spend-approvals, team-registry, suppression), `daily/<date>/`, `requests/<role>/` and `requests/justin/`, `approved/`, `data/` (mode 600: lists, the Dream lists, pipelines), `tools/scrapers/`, `log/` (runs, the conversation log, engine calls), `vault/` (Obsidian: `Daily/`, `People/`, `Decisions.md`), `state/` and `state/test/`, `.secrets/` (mode 700).

## Milestones

| # | Milestone | Done when |
|---|---|---|
| K0 | The pack is on the lead | The lead unpacked it and wrote `log/setup.md` with the check results |
| K1 | Intake | The tier, the call link, the percentage and the rest of the intake answers are in `context/owner.md` |
| K2 | Read-only | Every app the tier needs is connected read-only, each with one real record read back |
| K3 | The team | The tier's agents exist, each has done its set-up page and written `log/setup-<agent>.md`, and each one's routines are created paused and read back into `team-registry.md` |
| K4 | Test day | The first-day run in HANDOFF.md passes with zero sends |
| K5 | Words approved | Justin has said yes to each message type's words and each channel's first post |
| K6 | Lanes on | Agents go on one at a time in the bring-up order |
| K7 | First result | A conversation from this bot's outreach ends in a fractional role agreed, or a paid Revenue Partnerships 3.0 or Revenue OS |
