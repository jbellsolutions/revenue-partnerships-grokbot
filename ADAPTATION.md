# Adapting the skills to GrokBot

## How the bot loads a skill

A Grok bot keeps **private skills**: a `SKILL.md` with a `name` and `description` in its frontmatter. It loads one when a request matches the description. The bot also has its own cloud computer with a shell and files, so a skill's scripts run there from `/workspace/revenue-partnerships/repo/skills/<role>/<skill>/`.

1. **Upload** every `skills/<role>/<skill>/SKILL.md` as a private skill, plus `guards/SKILL.md` as `bot-guards`. Scripts and references stay next to it in the workspace.
2. **Engine.** HANDOFF Part 2 step 1 copies `repo/gtm-box/` to `/workspace/revenue-partnerships/gtm-box`, sets `GTM_HOME` to it, and links `gtm-box/suppression.csv` to `context/suppression.csv`, so the engine and the guards read one list.
3. **Keys** come from `.secrets/<system>.env` (mode 600), names in `.env.example`. Load one in a run's shell with `set -a; . .secrets/<system>.env; set +a`. Never print them.

## Mentions to read past

`python3 tools/check.py` lists five skills that still mention Mac or Hermes things. They are where the skill came from, not steps to run:

| What | Why | What the bot does instead |
|---|---|---|
| `gohighlevel-cli`: the `~/GHL-MCP` install and the Claude Code user config MCP server | The Mac install | Call the GoHighLevel API with `GHL_API_KEY` and `GHL_LOCATION_ID` from `.secrets/gohighlevel.env`, or install the CLI once on the bot's computer as the skill describes. Writes only through sales-crm and `crm-writes: on` |
| `cold-email-master`: the course corpus and source repos | Where its references were copied from | Its own summaries are in the pack; the licensed course material loads privately (NEEDS-JUSTIN item 17) |
| `scrapebox`: "from Justin's Mac" benchmark | A measured fact (home IPs read more directories than cloud IPs) | Expect the Decodo rung on this cloud computer; `scraper-forge` says how |
| `verify-leads`: a Mac default path in `tools/verify_leads.py` | Default only | Pass the input and output paths under `data/` |
| `winnr-instantly`: a Hermes command and a Mac repo path | The mailbox CLI lives on the Mac | Mailbox setup is Justin's step; the bot reads Instantly through `INSTANTLY_API_KEY` |
| `beat.py`, `heal.py`, `dispatch.py` in `gtm-box/box/` read Hermes cron files | No Hermes on GrokBot | `context/routines-on.md` is the switch; the heartbeat is `repo/guards/scripts/beat.py` |
| `speaker_queue.py` calls the SpeakerAgent Hermes runtime | Built for an earlier agent host | Use the SpeakerAgent API skills (`speakeragent-tools`) |
| `skool_scrape.py` and `skool_worker.py` expect a Skool Chrome on port 9224 | Built for an earlier agent host | The bot's own browser, signed in by Justin; `skool-inbound` reads through it when the port isn't there |
| `rankspot.py` knows two sites under the ids `findmemoney` and `aiguy` | Ids from the base kit; `aiguy` now points at truerevenuepartnerships.com and reads `RANKSPOT_API_KEY` | Use only `aiguy` |

## Dropped from the old pack, and why

- `crm-operator`, `slack-crm`: Attio, superseded 2026-10-15.
- `revenue-partner`, `orgo-fleet`, `orgo-computer-use`: they drive Hermes agents on Orgo computers. A GrokBot has its own computer and doesn't drive Hermes boxes.
- `gtm-box/box/write_env.py`: it wrote Hermes profile env files.
- The nine copies of `ai-guy-guards`: replaced by the one `bot-guards` skill with tested scripts.

## What still carries the base kit's wording (2026-11-18)

This pack was put together from the base kit, which was written for an earlier offer. The pages a role reads first (OFFER.md, the master prompt, the charter, the role charters, the eight message templates, the worker's three sorting prompts) are rewritten for this offer. These are not, and OFFER.md wins wherever they differ:

| Where | What it still says | What the bot does |
|---|---|---|
| `skills/lead/gtm-shared`, `gtm-role`, `ai-guy-agent-team`; the `gtm-crm-*` skills | Skill names and descriptions say "AI Guy" and "the GTM box" | They are names. The steps apply as written |
| `skills/cold-email/cold-campaigns`, `cold-copy` | The earlier offer's campaign table, measured rates and copy checks (one check fails the word "money") | Not used. Cold leads on this bot is the one `fractional` campaign in `fractional/settings/cold-email.json` |
| `gtm-box/campaigns/*.md` | Lane pages written for the earlier offer; the offer line in each now points to OFFER.md | Use the lane's steps, take the offer from OFFER.md |
| `gtm-box/cold/crm_sync.py`, `new_client.py`, `box/rankspot.py` | The CRM id `ai-guy` and the site id `aiguy` in code | Leave them: they are ids, and renaming them changes tested code |
| `PLAYS.md`, `CONTENT.md` | Research written for the earlier offer's audience | Use the plays, take the topic from OFFER.md |
| `agents/*/README.md`, and mentions of `STATUS.md` or `agents/reply/` | Each function's notes point at a `STATUS.md` (its chat's working notes) and the retired reply folder; both stay in the private factory, along with paths under `ideas/` | Background. `PROCESS.md` and the settings example in each folder are what a role works from |

Dropped from the base kit: the capital role, its four routines and its crowdfund skill (not in either offer).
