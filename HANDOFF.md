# Revenue Partnerships 3.0: the handoff

What Justin does, then what the bot does on its own. Unverified platform facts are flagged *(unverified)*. Nothing in this pack has run on a Grok bot yet.

## Part 1: Justin

1. **The bot.** Use your main Grok bot, or make a new one named **Revenue Partnerships** on the same account. Either way: Grok desktop app, the one-to-one chat with the bot (approval, secret and sign-in requests only show there), Settings → General → Bot → Timezone **UTC**.
2. **Room for the routines.** A bot holds 50 routines. This bot runs all nine functions: 41 routines. (The Revenue Partnerships 3.0 tier alone is 31.) If the bot already runs routines from another pack, tell it how many before step 4.
3. **Read the fractional email.** `fractional/MESSAGES.md` in the public repo is the core email Dream 100, Dream 500 and cold leads send. Say yes or mark changes when the bot shows it; nothing goes out before that.
4. **The pack: one link.** Paste this line into the bot. If the bot can't download, attach `revenue-partnerships.zip` from the same release instead *(zip route unverified)*:

   > You are Revenue Partnerships. Download https://github.com/jbellsolutions/revenue-partnerships-grokbot/releases/latest/download/revenue-partnerships.zip, unpack it into /workspace/revenue-partnerships/repo/ and follow HANDOFF.md, Part 2, from step 1. Read MASTER-PROMPT.md, OFFER.md, fractional/MESSAGES.md and CHARTER.md first. Ask me one thing at a time. Nothing sends, posts, spends or writes to a CRM until I say yes in this chat.

5. **Auto-review rules.** At Part 2 step 5, paste the Ask-first lines it shows into Auto-review → Custom Rules.
6. **Sign-ins and keys.** When it asks, sign in through Connect apps or the bot's browser, one at a time. Keys go only through a secure secret card or the hidden terminal prompt with **Take over**. Rotate first any key ever pasted in a chat.

## Part 2: the bot

1. **Workspace.** Create `/workspace/revenue-partnerships/` with `context/`, `daily/`, `requests/` (one folder per role: lead, sales-crm, cold-email, speaker, partners, dream, social, content-seo, channels, plus `justin`), `approved/`, `data/` (mode 600) with `data/dream/`, `tools/scrapers/` with an empty `REGISTRY.md`, `log/`, `vault/` (Obsidian: `Daily/`, `People/`, `Decisions.md`), `state/` and `state/test/`, `.secrets/` (mode 700).
   - Write `context/standing-approvals.md` and `context/spend-approvals.md`, both empty, and `context/team-registry.md`. Don't create `context/STOP`.
   - The engine: `cp -r repo/gtm-box gtm-box`, set `GTM_HOME=/workspace/revenue-partnerships/gtm-box`, run `python3 -m py_compile` over `gtm-box/**/*.py`, and link the suppression list: `ln -s ../context/suppression.csv gtm-box/suppression.csv`.
   - Start `log/setup.md`. Run these four and paste each last line there: `python3 repo/tools/check.py`, `python3 repo/tools/selftest.py`, `python3 repo/tools/tier.py --check`, `python3 repo/tools/check_campaign.py repo/campaign.json`.
2. **Memory and skills.** Save MASTER-PROMPT.md to memory word for word, then each role's "System prompt section" from `roles/`. Save `guards/SKILL.md` and every `skills/<role>/<skill>/SKILL.md` as a private skill (ADAPTATION.md says what to read past). Put each key in `.env.example` into `.secrets/<system>.env` by hidden prompt, one at a time; skip any Justin says he doesn't have yet and list it as blocked.
3. **Intake.** Ask Justin, one at a time, and write each answer in `context/owner.md` with his words and the date:
   1. The tier. This bot runs all nine functions: write `tier: revenue-os` unless Justin says otherwise, then `python3 repo/tools/tier.py revenue-os --routines-on > context/routines-on.md`.
   1a. The fractional email: show Justin `repo/fractional/MESSAGES.md` sections 1 to 4 and ask for his yes or his changes, the subject line he picks, and which mailbox it goes from.
   1b. Who gets it: the Dream 100 and Dream 500 lists or the kind of company he would work inside, the cold leads audience, and how many a day.
   1c. The answer to "what's the base, what's the commission": his figures, or "I'll say it on the call".
   1d. The Lead Radar dashboard's address (`RADAR_APP_URL`), whether its job-board campaigns exist, and any job site to add to or drop from `repo/fractional/settings/lead-radar.json`.
   2. The call link every lane ends on (also `BOOKING_LINK` in the intake file).
   3. The percentage on Revenue Partnerships 3.0, and what counts as revenue that comes from a partnership.
   4. Whether outreach names the prices, or they are said only on a reply and on the call.
   5. The guarantee: whether "at least 5 new partners in 90 days, or you don't pay" goes with these offers, and how it sits beside $2,000 up front.
   6. How the business and Justin are named everywhere, and the proof the bot may point at (first names only).
   7. Save the Dream lists from 1b under `data/dream/`, mode 600.
   8. The Slack channel for reports (default `#revenue-partnerships`) and the Notion Scoreboard and Drafts pages.
   9. The suppression list file (header `kind,value,reason`). Save it as `context/suppression.csv`, mode 600. Then check one known name with `python3 repo/guards/scripts/suppression.py check`: it must say held.
   10. The scoreboard's targets, if he wants any set.
   11. Any standing spend he approves for this bot, written as lines in `context/spend-approvals.md`. An approval given to another bot does not carry over.
   12. The pitch details for shows (`gtm-box/speaker/pitch-details.json`): which email, and whether a phone may be given.
4. **Function settings.** Copy `repo/fractional/settings/*.json` (Dream 100, Dream 500, cold leads, Lead Radar) into `context/functions/`. For the other five functions, copy the settings example from `repo/agents/<function>/` and fill it from OFFER.md. Fill what intake answered. Names of things only.
5. **Approval rules.** Show Justin the Ask-first lines from GATES.md to paste.
6. **Engines.** Install the Claude Code and Codex CLIs on this computer, ask Justin to sign each in (`claude setup-token`; `codex login --device-auth`, as the user the routines run as), then run `python3 repo/engines/route.py --check` and paste its output into `log/setup.md`. A function whose engine is missing falls to the bot's own run and is reported.
7. **Connect, read-only, one at a time.** Each gets a check that reads one real record into `log/setup.md`. Skip the rows for functions not on the tier.

   | App | Function | Check |
   |---|---|---|
   | Slack, Notion | core | Read the last message; read the Scoreboard's newest row |
   | GoHighLevel (read-only key) | sales agent | Read one contact's name and stage |
   | Gmail and Google Calendar | sales agent, SpeakerAgent, partners, Dream 100 and 500 | Read the newest thread's subject; read tomorrow's events |
   | Cal.com, the guarded sender | sales agent | List the event types; the sender's health endpoint |
   | SpeakerAgent | SpeakerAgent | List one podcast lead |
   | OutFlo | Dream 100 and 500, partners, content | `python3 repo/linkedin/lane.py route connection_request` prints `outflo`; OutFlo itself is read as LINKEDIN.md says. Never sign this computer's browser into LinkedIn |
   | X, YouTube | content | Open the signed-in home page and read the account name; nothing else |
   | One API, Scrapebox, Decodo, Consulti, treg | core (the data lane) | The free status or balance call for each |
   | PlusVibe, Instantly, Maildoso, AgentMail | cold leads (Revenue OS tier); partners at volume | List campaigns or inboxes |
   | Lead Radar, Skool | Lead Radar (Revenue OS tier) | Campaign names; the signed-in home page |
   | RankSpot, Medium, beehiiv, the site's GitHub repo | AEO and SEO (Revenue OS tier) | The free AI-visibility summary; the account name; the latest commit title |

8. **Other systems.** If another agent or pack already answers replies or writes the same CRM, two systems never do the same thing: before sales-crm goes `on`, Justin says which one answers. Webhooks point at this bot's event routines only when Justin repoints them.
9. **Routines, switched off.** Create the tier's routines from `python3 repo/tools/tier.py <tier>`, paused. Each prompt starts `Role: <role>.` and names the routine. Record each in `team-registry.md` with role, cron or trigger, next run and, for the two events, the webhook URL Grok gives *(webhook routines seen live, not in docs)*. A next run an hour or more off means the time zone isn't set.
10. **Report.** Send Justin the routine list, the two webhook URLs, the check results, and what isn't done and why.

## Usage kit (usage-mastery v1.0.0)

Do these right after the workspace and memory steps.

1. Run `bash repo/usage/scripts/install.sh` (free, pinned, no keys) and paste its last line into `log/setup.md`.
2. Save `repo/usage/SKILL.md` as a private skill named usage-saver.
3. Copy `repo/usage/LEDGER.md` to `log/usage-ledger.md`. Ask Justin for the baseline reading (Settings → Usage: % used and reset date) before the first test day, and again after it.
4. The weekly audit (`repo/usage/AUDIT.md`) runs inside the Monday evening report; it adds no routine.
5. Show Justin the owner-only steps once and record the answers in `log/setup.md`: a spending cap or Auto top-up off at grok.com/dashboard/billing (the bot never changes billing), and three more lines for Auto-review → Custom Rules:

   ```
   Ask first before opening more than 5 web pages for one task.
   Ask first before starting a sub-agent or a second bot on a job.
   Ask first before re-running a step that has already failed twice.
   ```

## Bring-up order

One role goes `on` at a time, after its test-day row passed. Rows marked Revenue OS apply only on that tier.

| # | Role | Turned on first |
|---|---|---|
| 0 | the worker | Watchdog and digest, then replies and shows (WORKERS.md, Bring-up). Revenue OS: radar, Skool, lists |
| 1 | lead | Morning plan, evening scoreboard |
| 2 | cold-email (the data lane) | Lists, scrapers and worker orders |
| 3 | dream | Dossiers, then Dream 100 first touches as drafts, then the Dream 500 wave: the fractional email |
| 4 | partners, social (creator pull) | Partner find, collab blitz, creator pull |
| 5 | speaker | Show shortlist and pitches, then pitch submit |
| 6 | channels, content-seo (content), social (LinkedIn) | After each channel's first post has Justin's yes |
| 7 | sales-crm | Reply check, then openers and the event routines; CRM writes after Justin says `crm-writes: on` |
| 8 | social (Lead Radar and the Job site sweep), content-seo (AEO and SEO) | Reads first |
| 9 | cold-email (the fractional campaign) | Ten rows with their first lines for Justin to read, then the daily number he gave |

## The first-day test run

Every routine is `test` in `context/routines-on.md`, so nothing reaches a person. **Test on a routine does real work**: the `test` line goes in before every Test press.

| Step | Role | Do | Pass when |
|---|---|---|---|
| 1 | lead | Morning plan | A plan for every role on the tier in `daily/<date>/lead.md` and in Slack |
| 2 | cold-email | Lists, scrapers and worker orders | One list file in `data/` for a real request (podcast shows or partner targets), every row suppression-checked; no paid pull without a plan in `requests/justin/` |
| 3 | dream | Dossiers | One Dream 100 dossier with a warm path |
| 4 | dream | Dream 100 first touches and follow-up | One hand-written fractional first touch as a draft in `requests/justin/`, its five points in order, logged as a draft in the conversation log |
| 5 | dream | Dream 500 wave | Five rows on `fractional_first_touch.txt`, each with a true first line, as drafts; a row with nothing true to say is held, not filled; nothing sent |
| 6 | partners | Collab blitz | Targets found and qualified, notes as drafts |
| 7 | social | Creator pull and partner drafts | A creator list with links; drafts only |
| 8 | speaker | Show shortlist and pitches | Scored shows pitched as drafts in `requests/justin/` |
| 9 | channels, content-seo | X posts and replies; Daily content | One post and one master piece as drafts; nothing posted |
| 10 | sales-crm | Reply check | A test reply is sorted, the person's note is read and updated, an answer is drafted, and no CRM write happens (`crm-writes: off`) |
| 11 | All | The conversation log | `python3 repo/convlog/convlog.py audit` names no send without a logged draft |
| 12 | All | Suppression | A known suppressed name is held by every drafting role |
| 13 | social | Radar askers; Job site sweep | Askers handed to sales-crm; at least one job post for a virtual assistant or an AI role judged with `job-fit.md` and handed to `requests/cold-email/` with its link and first line; nothing applied to, nothing posted |
| 13a | cold-email, content-seo | Campaign read and copy; AI visibility read | The fractional campaign's ten rows as drafts; a visibility read from free reads only |
| 14 | lead | Evening scoreboard | Every role on the tier has a line; today's vault note exists; nothing was sent or posted |

The day passes when every row for the tier passes and `state/` shows 0 sends. Then Justin says yes to each message type's words and each channel's first post, and roles go `on` one at a time in the order above.

## Reporting back

| Where | What | Written by |
|---|---|---|
| Slack (the channel named at intake) | Morning plan, alarms (silent roles, a send with no yes, account warnings), evening scoreboard, Justin's queue | lead |
| Notion | A Scoreboard row a day; Drafts waiting on Justin | lead |
| The workspace vault | `vault/Daily/<date>.md`, `People/`, `Decisions.md` | lead writes the daily note; each role adds its section |
| The single brain | A scrubbed status line and the daily summary, no raw transcripts or contact data | Justin's Mac pulls it, or a deploy key: his choice on NEEDS-JUSTIN |
