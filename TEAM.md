# The team: one lead and one agent per function

Justin, 2026-11-20: "nine functions = 9 agents", and "just like we have subchats here for each role so it should be in grokbot with each role being its own agent".

So the install is ten Grok agents, not one bot: the **lead**, which is the bot Justin pastes the one line into and the one he plans with, and **one agent for each of the nine functions**. It is the same shape as the chats the pack was built in: a main chat, and a chat per function under it.

Unverified on Grok *(nothing in this pack has run there)*: whether a bot can create another bot, and whether bots on one account see the same `/workspace`. HANDOFF.md, Part 2, step 9 tests both with the first agent before making the rest, and says what to do if either is not so.

## The ten agents

| Agent id | Bot name | What it does | Roles it works as | Routines | Engine |
|---|---|---|---|---|---|
| `lead` | Revenue Partnerships | Creates and checks the team, plans the day, keeps Justin's one queue, posts the scoreboard, writes the vault note | lead | 2 | the bot's own run |
| `dream-100` | RP Dream 100 | A dossier and one hand-written fractional first touch per company, then one follow-up | dream | 2 | the bot's own run |
| `dream-500` | RP Dream 500 | Small waves of the plain fractional email, each with a true first line | dream | 1 | the bot's own run |
| `partners` | RP Partners | Partners, collaborators and influencers on the partnerships message; the creator pull | partners, social | 6 | the bot's own run |
| `speaker` | RP SpeakerAgent | Podcasts, interviews, stages: pitches, guest forms, follow-up | speaker | 4 | Codex |
| `sales-crm` | RP Sales agent | The one answerer and the one CRM writer | sales-crm | 9 | Codex |
| `content` | RP Content | Daily content, X, YouTube, LinkedIn | content-seo, channels, social | 6 | Claude Code |
| `cold-email` | RP Cold leads | Cold leads on the fractional email, and the data lane every agent orders lists from | cold-email | 3 | the bot's own run |
| `lead-radar` | RP Lead Radar | The AI Guy Lead Radar, Skool and the job sites; reads only | social | 3 | Codex |
| `aeo-seo` | RP AEO and SEO | AI visibility, SEO, articles, links, Medium | content-seo | 5 | Codex |

41 routines in all. A bot holds 50; the most on one agent is 9. Each agent's page is in [team/](team/lead.md): its first message, its set-up steps, its routines and the section it saves to memory. `python3 tools/team.py list` prints this table from [team.json](team.json); `python3 tools/team.py <agent>` prints one agent's routines.

On the Revenue Partnerships 3.0 tier only seven agents are created (no cold leads, Lead Radar, or AEO and SEO), and the data lane's one routine runs on the lead: `python3 tools/team.py list --tier revenue-partnerships`.

## Roles and agents

The base kit is written as nine **roles** (`roles/*.md`): each is a numbered procedure with its guard steps and skills. The team is ten **agents**. An agent works as one or more roles, and a routine's first line names both: `Agent: lead-radar. Role: social.` Three roles are shared, so their work is split by routine:

| Role | Agents that work as it |
|---|---|
| dream | `dream-100` (Dossiers; Dream 100 first touches and follow-up), `dream-500` (Dream 500 wave) |
| social | `lead-radar` (Radar and Skool askers; Job site sweep; Skool join), `partners` (Creator pull), `content` (LinkedIn) |
| content-seo | `aeo-seo` (AI visibility, SEO daily, Article pick, Links and keywords, Medium), `content` (Daily content, Channel read) |

## How the agents work together

Only through files in the one shared workspace, `/workspace/revenue-partnerships/`. No agent relies on another agent's chat.

| File | Who writes | Who reads |
|---|---|---|
| `requests/<role>/<id>.md` | Any agent handing work over | The agent that owns that inbox (below) |
| `requests/justin/<agent>-<id>.md` | Any agent: a draft, a question, a spend | The lead, which shows Justin and records his answer |
| `context/standing-approvals.md`, `context/spend-approvals.md`, `context/owner.md` | The lead, with Justin's words and the date | Every agent, through the guard scripts |
| `context/routines-on.md` | The lead, on Justin's word | Every routine, at its start |
| `daily/<date>/<role>.md` | Each agent appends its part under `## <agent id>` | The lead, for the plan and the scoreboard |
| `state/heartbeat.jsonl` | Every run (`beat.py write <role> ... agent=<id>`) | The worker's watchdog and the lead |
| `log/setup-<agent>.md`, `context/team-registry.md` | Each agent at set-up | The lead |

| Inbox | Read by |
|---|---|
| `requests/lead/` | lead |
| `requests/sales-crm/` | sales-crm (every reply and every new person, from every agent) |
| `requests/cold-email/` | cold-email (list and scraper orders; hiring posts from Lead Radar) |
| `requests/speaker/` | speaker |
| `requests/partners/` | partners |
| `requests/dream/` | dream-100 or dream-500, by the list the item names |
| `requests/social/` | lead-radar (askers, Skool, job posts), partners (creators), content (LinkedIn) |
| `requests/content-seo/` | content (stories, recordings, posts), aeo-seo (articles, keywords, links, citations) |
| `requests/channels/` | content |

## What stays one

- **One approval queue.** Words, sends, posts and spends are approved once, with the lead, and written to the workspace where every agent's guard script reads them. An agent's own chat is used only for what only that chat can show: its sign-ins, its secret prompts, an approval card the app raises there.
- **One answerer and one CRM writer:** the sales agent.
- **One conversation log, one suppression list, one STOP file,** all in the workspace. `context/STOP` stops all ten.
- **One worker**, if Justin sets one up (WORKERS.md).

## What it costs

The number of routine runs does not change (272 scheduled runs a week with everything on). Each agent keeps its own memory, and holds only its own function's sections and skills instead of all nine roles'. The Grok plan's usage is counted for the account *(unverified whether ten bots draw on one allowance or each has its own)*: the usage ledger in HANDOFF.md reads it before and after the test day.
