# Revenue Partnerships 3.0: the handoff

What Justin does, then what the lead agent does on its own. The install is ten agents: the lead, and one agent per function ([TEAM.md](TEAM.md)). Unverified platform facts are flagged *(unverified)*. Nothing in this pack has run on a Grok bot yet.

## Part 1: Justin

1. **The lead.** The bot you paste the line into is the lead: the one you plan with, and the one that holds your approval queue. Use your main Grok bot, or make a new one named **Revenue Partnerships** on the same account. Either way: Grok desktop app, the one-to-one chat with the bot (approval, secret and sign-in requests only show there), Settings → General → Bot → Timezone **UTC**.
2. **Nine more agents, one per function.** The lead sets up an agent for each function: Dream 100, Dream 500, partners, SpeakerAgent, sales agent, content, cold leads, Lead Radar, AEO and SEO. It asks you once before creating them, and creates every one with its routines off. If the app does not let a bot create a bot *(unverified)*, it gives you the nine names and the one message to paste into each; you make each bot (same account, time zone UTC) and paste. No agent holds more than 9 routines of the 50 a bot allows; the lead holds 2.
3. **Read the fractional email.** `fractional/MESSAGES.md` in the public repo is the core email Dream 100, Dream 500 and cold leads send. Say yes or mark changes when the bot shows it; nothing goes out before that.
4. **The pack: one link.** Paste this line into the lead. If it can't download, attach `revenue-partnerships.zip` from the same release instead *(zip route unverified)*:

   > You are the lead agent of Revenue Partnerships. Download https://github.com/jbellsolutions/revenue-partnerships-grokbot/releases/latest/download/revenue-partnerships.zip, unpack it into /workspace/revenue-partnerships/repo/ and follow HANDOFF.md, Part 2, from step 1. Read MASTER-PROMPT.md, TEAM.md, OFFER.md, fractional/MESSAGES.md and CHARTER.md first. Each of the nine functions gets its own agent; you are the lead. Ask me one thing at a time. Nothing sends, posts, spends or writes to a CRM until I say yes in this chat.

5. **Auto-review rules.** At Part 2 step 5, paste the Ask-first lines it shows into Auto-review → Custom Rules.
6. **Sign-ins and keys.** When it asks, sign in through Connect apps or the bot's browser, one at a time. Keys go only through a secure secret card or the hidden terminal prompt with **Take over**. Rotate first any key ever pasted in a chat.

## Part 2: the lead, then each agent

1. **Workspace.** You are the lead (`repo/team/lead.md`). Create `/workspace/revenue-partnerships/` with `context/`, `daily/`, `requests/` (one inbox per role: lead, sales-crm, cold-email, speaker, partners, dream, social, content-seo, channels, plus `justin`; TEAM.md says which agent reads each), `approved/`, `data/` (mode 600) with `data/dream/`, `tools/scrapers/` with an empty `REGISTRY.md`, `log/`, `vault/` (Obsidian: `Daily/`, `People/`, `Decisions.md`), `state/` and `state/test/`, `.secrets/` (mode 700).
   - Write `context/standing-approvals.md` and `context/spend-approvals.md`, both empty, and `context/team-registry.md`. Don't create `context/STOP`.
   - The engine: `cp -r repo/gtm-box gtm-box`, set `GTM_HOME=/workspace/revenue-partnerships/gtm-box`, run `python3 -m py_compile` over `gtm-box/**/*.py`, and link the suppression list: `ln -s ../context/suppression.csv gtm-box/suppression.csv`.
   - Start `log/setup.md`. Run these five and paste each last line there: `python3 repo/tools/check.py`, `python3 repo/tools/selftest.py`, `python3 repo/tools/tier.py --check`, `python3 repo/tools/team.py --check`, `python3 repo/tools/check_campaign.py repo/campaign.json`.
2. **Memory and skills.** Save MASTER-PROMPT.md to memory word for word, then the "Agent section" in `team/lead.md`, then the "System prompt section" in `roles/lead.md`. The lead saves no other role's section: each agent saves its own at step 9. Save `guards/SKILL.md` and the lead's skills (`skills.json`) as private skills (ADAPTATION.md says what to read past). Put each key in `.env.example` into `.secrets/<system>.env` by hidden prompt, one at a time; skip any Justin says he doesn't have yet and list it as blocked.
3. **Intake.** Ask Justin, one at a time, and write each answer in `context/owner.md` with his words and the date:
   1. The tier. This install runs all nine functions, as ten agents: write `tier: revenue-os` unless Justin says otherwise, then `python3 repo/tools/tier.py revenue-os --routines-on > context/routines-on.md`.
   1a. The fractional email: show Justin `repo/fractional/MESSAGES.md` sections 1 to 4 and ask for his yes or his changes, the subject line he picks, and which mailbox it goes from.
   1b. Who gets it: the Dream 100 and Dream 500 lists or the kind of company he would work inside, the cold leads audience, and how many a day.
   1c. The answer to "what's the base, what's the commission": his figures, or "I'll say it on the call".
   1d. The Lead Radar dashboard: its address is in `repo/fractional/settings/lead-radar.json` (set `RADAR_APP_URL` to it); ask only for the password, by hidden prompt in the Lead Radar agent's chat, then read `/api/data` once. Also ask whether its job-board campaigns exist, the Skool and Whop group links, and any job site to add to or drop from `repo/fractional/settings/lead-radar.json`.
   2. The call link every lane ends on (also `BOOKING_LINK` in the intake file).
   3. The percentage on Revenue Partnerships 3.0, and what counts as revenue that comes from a partnership.
   4. Whether outreach names the prices, or they are said only on a reply and on the call.
   5. The guarantee: whether "at least 5 new partners in 90 days, or you don't pay" goes with these offers, and how it sits beside $2,000 up front.
   6. How the business and Justin are named everywhere, and the proof the bot may point at (first names only).
   7. Save the Dream lists from 1b under `data/dream/`, mode 600.
   8. The Slack channel for reports (default `#revenue-partnerships`) and the Notion Scoreboard and Drafts pages.
   9. The suppression list file (header `kind,value,reason`). Save it as `context/suppression.csv`, mode 600. Then check one known name with `python3 repo/guards/scripts/suppression.py check`: it must say held. If he has no list, do not wait on it: create the file with only that header line, check a made-up name (it must say clear), and add people as they say no.
   10. The scoreboard's targets, if he wants any set.
   11. Any standing spend he approves for this bot, written as lines in `context/spend-approvals.md`. An approval given to another bot does not carry over.
   12. The pitch details for shows (`gtm-box/speaker/pitch-details.json`): filled from Justin's SpeakerAgent persona and shown to him once, as `repo/speaker/SPEAKERAGENT.md` says; ask him only whether a phone may be given. Save the link he gave for a host who asks for his calendar as `SPEAKER_BOOKING_LINK` in the intake file; it goes in no pitch.
4. **Function settings.** Copy `repo/fractional/settings/*.json` (Dream 100, Dream 500, cold leads, Lead Radar) and `repo/speaker/speaker.json` (SpeakerAgent) into `context/functions/`. For the other four functions, copy the settings example from `repo/agents/<function>/` and fill it from OFFER.md. Fill what intake answered. Names of things only.
5. **Approval rules.** Show Justin the Ask-first lines from GATES.md to paste.
6. **Engines.** Install the Claude Code and Codex CLIs on this computer, ask Justin to sign each in (`claude setup-token`; `codex login --device-auth`, as the user the routines run as), then run `python3 repo/engines/route.py --check` and paste its output into `log/setup.md`. Each agent whose engine is Claude Code or Codex (`team.json`) runs the same check at its own set-up; if it does not see the CLIs the lead installed *(unverified whether agents share one computer)*, it installs them and asks Justin for the same two sign-ins in its own chat. A function whose engine is missing falls to the bot's own run and is reported.
7. **Connect the lead's own accounts, read-only.** Slack, Notion, GoHighLevel (read-only key) and the worker, each with the check in the table at step 10, one real record read into `log/setup.md`. Every other account is connected by the agent that uses it, at step 10.
8. **Other systems.** If another agent or pack already answers replies or writes the same CRM, two systems never do the same thing: before the sales agent goes `on`, Justin says which one answers. Webhooks point at the sales agent's event routines only when Justin repoints them.
9. **The team, every routine off.** `python3 repo/tools/team.py list` names the agents for the tier. Ask Justin once: "Create the nine function agents now, all with routines off?" On his yes:
   1. **One agent first, as the test.** Create `sales-crm` (bot name in `team.json`, same account, time zone UTC) and give it the "First message" from `repo/team/sales-crm.md`. If you cannot create a bot *(unverified)*, give Justin the bot name and that message to paste, and wait.
   2. **The shared-workspace check.** The new agent's first set-up step reads `context/team-registry.md` and writes `log/setup-sales-crm.md`. When that file appears, the workspace is shared. If the agent says it cannot see the workspace *(unverified whether bots on one account share it)*, stop: tell Justin in one message that the agents need a folder they all read and write, what you tried, and that the other eight wait. Create no more until that is settled.
   3. **The other eight**, the same way, in this order: `cold-email`, `dream-100`, `dream-500`, `partners`, `speaker`, `content`, `lead-radar`, `aeo-seo`. Each does its own page's set-up steps: its memory (the master prompt, its agent section, its roles' sections), its skills, its time zone, its accounts read-only, and one line back in `requests/lead/setup-<agent>.md`.
   4. **Record the team.** In `context/team-registry.md`: each agent's id, bot name, the date it was created, and what its set-up line says is blocked.
10. **Each agent connects its own accounts, read-only, one at a time.** Each check reads one real record into `log/setup-<agent>.md`. Keys are in the shared `.secrets/`; a sign-in is done in the chat of the agent that needs it *(unverified whether a sign-in made on one bot is seen by the others)*. Skip the agents not on the tier.

   | App | Agent | Check |
   |---|---|---|
   | Slack, Notion | lead | Read the last message; read the Scoreboard's newest row |
   | GoHighLevel (read-only key) | sales-crm; lead (read only) | Read one contact's name and stage |
   | Gmail and Google Calendar | sales-crm, speaker, partners, dream-100, dream-500 | Read the newest thread's subject; read tomorrow's events |
   | Cal.com, the guarded sender | sales-crm | List the event types; the sender's health endpoint |
   | SpeakerAgent | speaker | List one podcast lead |
   | OutFlo | dream-100, dream-500, partners, content | `python3 repo/linkedin/lane.py route connection_request` prints `outflo`; OutFlo itself is read as LINKEDIN.md says. Never sign any agent's browser into LinkedIn |
   | X, YouTube | content | Open the signed-in home page and read the account name; nothing else |
   | One API, Scrapebox, Decodo, Consulti, treg | cold-email (the data lane) | The free status or balance call for each |
   | PlusVibe, Instantly, Maildoso, AgentMail | cold-email | List campaigns or inboxes |
   | Lead Radar, Skool | lead-radar | Campaign names; the signed-in home page |
   | RankSpot, Medium, the site's GitHub repo | aeo-seo | The free AI-visibility summary; the account name; the latest commit title |
   | beehiiv | content | The publication's name |

11. **Routines, switched off, each on its own agent.** When Justin says to create them, write one file to each agent's inbox saying so, with his words and the date. Each agent then creates the routines `python3 repo/tools/team.py <agent>` lists, paused. Each prompt starts `Agent: <agent>. Role: <role>.` and names the routine. Each is recorded in `team-registry.md` with agent, role, cron or trigger, next run and, for the sales agent's two events, the webhook URL Grok gives *(webhook routines seen live, not in docs)*. A next run an hour or more off means that agent's time zone isn't set. The lead creates only its own two.
12. **Report.** Send Justin the team (ten agents, what each one's set-up line says), the routine list by agent, the two webhook URLs, the check results, and what isn't done and why.

## If this pack was already installed as one bot (v1.1.0 or earlier)

1. That bot becomes the lead. Download the zip again into `repo/` (keep `context/`, `data/`, `vault/`, `log/`, `state/` and `.secrets/` as they are), run the five checks from Part 2 step 1, and save the new MASTER-PROMPT.md and the lead's agent section to memory in place of the old ones.
2. Every answer Justin already gave stays: `context/owner.md` and the approvals files are read by all ten agents.
3. Go on from Part 2 step 9. Any routine the lead already created for another function is created again on that function's agent, paused, and removed from the lead only after Justin says so.

## Usage kit (usage-mastery v1.0.0)

Do these right after the workspace and memory steps.

1. Run `bash repo/usage/scripts/install.sh` (free, pinned, no keys) and paste its last line into `log/setup.md`.
2. Save `repo/usage/SKILL.md` as a private skill named usage-saver.
3. Copy `repo/usage/LEDGER.md` to `log/usage-ledger.md`. Ask Justin for the baseline reading (Settings → Usage: % used and reset date) before the first test day, and again after it.
4. The weekly audit (`repo/usage/AUDIT.md`) runs inside the Monday evening report; it adds no routine.
5. Show Justin the owner-only steps once and record the answers in `log/setup.md`: a spending cap or Auto top-up off at grok.com/dashboard/billing (the bot never changes billing), and three more lines for Auto-review → Custom Rules:

   ```
   Ask first before opening more than 5 web pages for one task.
   Ask first before starting a sub-agent or a bot that is not one of the ten agents in team.json.
   Ask first before re-running a step that has already failed twice.
   ```

## Bring-up order

One agent goes `on` at a time, after its test-day row passed. The lead changes the lines in `context/routines-on.md` on Justin's word; no agent switches itself on. Rows marked Revenue OS apply only on that tier.

| # | Agent | Turned on first |
|---|---|---|
| 0 | the worker | Watchdog and digest, then replies and shows (WORKERS.md, Bring-up). Revenue OS: radar, Skool, lists |
| 1 | lead | Morning plan, evening scoreboard |
| 2 | cold-email (the data lane) | Lists, scrapers and worker orders |
| 3 | dream-100, then dream-500 | Dossiers, then Dream 100 first touches as drafts; then the Dream 500 wave: the fractional email |
| 4 | partners | Partner find, collab blitz, creator pull |
| 5 | speaker | Show shortlist and pitches, then pitch submit |
| 6 | content | After each channel's first post has Justin's yes |
| 7 | sales-crm | Reply check, then openers and the event routines; CRM writes after Justin says `crm-writes: on` |
| 8 | lead-radar, aeo-seo (Revenue OS) | Reads first |
| 9 | cold-email (the fractional campaign) | Ten rows with their first lines for Justin to read, then the daily number he gave |

## The first-day test run

Every routine is `test` in `context/routines-on.md`, so nothing reaches a person. **Test on a routine does real work**: the `test` line goes in before every Test press.

| Step | Agent | Do | Pass when |
|---|---|---|---|
| 0 | All | The team | Every agent on the tier has a line in `requests/lead/setup-<agent>.md` and a file `log/setup-<agent>.md`; a routine run on the wrong agent does nothing and says so |
| 1 | lead | Morning plan | A plan for every agent on the tier in `daily/<date>/lead.md` and in Slack |
| 2 | cold-email | Lists, scrapers and worker orders | One list file in `data/` for a real request (podcast shows or partner targets), every row suppression-checked; no paid pull without a plan in `requests/justin/` |
| 3 | dream-100 | Dossiers | One Dream 100 dossier with a warm path |
| 4 | dream-100 | Dream 100 first touches and follow-up | One hand-written fractional first touch as a draft in `requests/justin/`, its five points in order, logged as a draft in the conversation log |
| 5 | dream-500 | Dream 500 wave | Five rows on `fractional_first_touch.txt`, each with a true first line, as drafts; a row with nothing true to say is held, not filled; nothing sent |
| 6 | partners | Collab blitz | Targets found and qualified, notes as drafts |
| 7 | partners | Creator pull and partner drafts | A creator list with links; drafts only |
| 8 | speaker | Show shortlist and pitches | Scored shows pitched as drafts in `requests/justin/` |
| 9 | content | X posts and replies; Daily content | One post and one master piece as drafts; nothing posted |
| 10 | sales-crm | Reply check | A test reply is sorted, the person's note is read and updated, an answer is drafted, and no CRM write happens (`crm-writes: off`) |
| 11 | All | The conversation log | `python3 repo/convlog/convlog.py audit` names no send without a logged draft |
| 12 | All | Suppression | A known suppressed name is held by every drafting agent |
| 13 | lead-radar | Radar askers; Job site sweep | Askers handed to sales-crm; at least one job post for a virtual assistant or an AI role judged with `job-fit.md` and handed to `requests/cold-email/` with its link and first line; nothing applied to, nothing posted |
| 13a | cold-email, aeo-seo | Campaign read and copy; AI visibility read | The fractional campaign's ten rows as drafts; a visibility read from free reads only |
| 14 | lead | Evening scoreboard | Every agent on the tier has a line; today's vault note exists; nothing was sent or posted |

The day passes when every row for the tier passes and `state/` shows 0 sends. Then Justin says yes to each message type's words and each channel's first post, and agents go `on` one at a time in the order above.

## Reporting back

| Where | What | Written by |
|---|---|---|
| Slack (the channel named at intake) | Morning plan, alarms (silent agents, a send with no yes, account warnings), evening scoreboard, Justin's queue | lead |
| Notion | A Scoreboard row a day; Drafts waiting on Justin | lead |
| The workspace vault | `vault/Daily/<date>.md`, `People/`, `Decisions.md` | lead writes the daily note; each agent adds its section |
| The single brain | A scrubbed status line and the daily summary, no raw transcripts or contact data | Justin's Mac pulls it, or a deploy key: his choice on NEEDS-JUSTIN |
