# The worker plane: GrokBot orchestrates, the worker does the volume

Justin, 2026-11-13: "good just also think of usage. always - what can we push to the hermes on a digital ocean server or a orgo computer? grokbot is just the orchestrator and automator. that way we can go super hard an still be profitable with keeping costs down. we want 20+ collb videos/podcasts, 2000 emails a day going out getting responses, lead radar bringing in deals daily, and linkedin campaigns rocking"

And: "we will not just use hermes on VPS/Orgo but also we can use a CLI subscription like codex to subsidize usage on grokbot"

## The split

Every job goes to the cheapest place that can do it well. GrokBot's allowance is the most expensive resource here, so it does only what needs its judgment.

| Layer | Runs on | Pays with | Does |
|---|---|---|---|
| Sending tools | PlusVibe and Instantly inboxes; the LinkedIn tool Justin picks | Their own plans | Every cold email and follow-up, at volume, on their own schedule |
| Code | The worker: cron plus `worker/jobs/` and the `gtm-box` engine | Nothing | Pulls, list builds and verification, syncs, scraper runs and re-tests, the watchdog, the digest |
| Codex CLI | The worker, signed in with Justin's ChatGPT plan | His subscription | Writing and repairing scrapers; batch sorting of replies, leads, Skool posts and shows; first-draft personalization lines |
| Hermes | The worker (and the browser host for Skool) | A cheap metered model, under the `model` spend pool | The same batch judgments when Codex is out of quota, and Hermes skills the engine already has |
| GrokBot | Its own computer | The Grok allowance | The plan, judgment on what reaches a person, copy, approvals, the one CRM writer, the scoreboard, the vault |

`worker/think.py` picks the brain, cheapest first (`THINK_TIERS=codex,hermes,api`). Anything no brain could judge comes to the bot unjudged, so the bot is the last resort and never the first.

## Where each target's volume runs

The rates below are **assumptions** to size the work. The weekly usage audit and the scoreboard replace them with measured numbers.

| Target (Justin, 2026-11-13) | Volume work on the worker | GrokBot's part | What it needs |
|---|---|---|---|
| **20+ collab videos and podcasts** (read as 20+ booked a week, shows plus collab videos, which matches the charter's 1 show and 1 to 2 collabs a day) | `show-research` every 2 hours (SpeakerAgent cycles, no model) and `show-score` (Codex scores fit and writes the episode angle). The collab blitz's lists are built by scrapers on the worker | One "Show shortlist and pitches" run a day: pitch the 4s and 5s with the worker's angles, then Follow-up and Pitch submit. At an **assumed 10% booking rate** that is about 200 pitches a week, or about 30 a day | `podcast_pitch` re-confirmed auto; SpeakerAgent keys on the worker |
| **2000 emails a day going out, getting responses** | `list-build` (Consulti, free scrapers such as ad libraries and Google Maps places, then verification), `list-load` once `cold_email` is auto, `replies-pull` every 15 minutes, `replies-sort` (opt-outs suppressed at once; only hot replies reach the bot), `inbox-health`, `campaign-stats`, the nightly `blocklist` | Campaign read and copy once a day, and hot replies only. At the **5% reply target** (the plusvibe skill's number) that is about 100 replies a day sorted on the worker; the bot sees the hot share | **200 warmed sending inboxes** at Justin's 10 a day per inbox (`plusvibe-operator`), about **67 domains** at 3 inboxes a domain. PlusVibe Business includes 150,000 sends a month (about 5,000 a day). With a 3-step sequence that is about 670 new verified contacts a day, roughly 14,000 a month: Consulti credits plus free scrapers |
| **Lead Radar bringing in deals daily** | Lead Radar runs its daily campaigns on its own server. `radar-poll` reads new leads every 4 hours, and Codex judges each one; only 4s and 5s reach the digest | One "Radar and Skool askers" run a day: draft the helpful reply for each kept lead, and hand real askers to sales-crm | Radar keys on the worker; more campaigns in Lead Radar (it bills its own credits) |
| **LinkedIn campaigns rocking** | Not on the worker. A data-centre IP (DigitalOcean or Orgo) is still a data-centre IP, and LinkedIn's User Agreement 8.2 bans bots. The campaign runs in the LinkedIn tool Justin picks. Third-party listings say OutFlo gives each profile its own residential IP; check that with OutFlo | Campaign copy, audience lists (built on the worker), the daily read of results and replies | NEEDS-JUSTIN 18: how LinkedIn messages run |
| Skool inbound | `skool-read` needs a signed-in browser that stays up: a computer Justin picks (`SKOOL_HOST` at intake), never one on the never-touch list. `skool-score` judges the posts | Answer the real askers and write owner notes | Justin signs Skool in on that host; `skool/ON` |
| Scrapers, "all the time" | `scraper-write` (Codex writes and repairs from the bot's SPEC.md), `scraper-run`, the nightly `scraper-retest` | Write the spec, check the pilot | Codex signed in; Decodo under the $5 a day pool |

## GrokBot runs, before and after

`tools/gen_roles.py` counts every scheduled bot run in a week from the crons:

| | Routines | Scheduled bot runs a week |
|---|---|---|
| v1 (everything on GrokBot) | 46 | 474 |
| v2 (worker plane) | 42 | 278 (down 41%) |

What moved: the watchdog (now on the worker, 56 runs a week), Reply check (42 → 21), show research (49 → 7), partner tickets and replies (70 → 35), the Skool sweep (21, now on the worker), the scraper forge and inbox health (14, now on the worker), and one pipeline sweep (21 → 14).

**What a run costs on Grok is not known yet.** Fewer runs and smaller reads should use less allowance. That stays a claim until `usage/LEDGER.md` has a reading before and after (the usage kit's rule: a creator's percentage is not a measurement).

## The one home of the guard state

In worker mode the worker holds the suppression list (and the engine's opt-out overlay), the spend pools and ledger, STOP, and the standing approvals. The bot's guards ask it through `WORKER_URL` and fail closed: if the worker can't be reached, every suppression check is held, every spend is held, and every send is stopped. The bot keeps its own `routines-on.md`; the worker keeps `worker-jobs-on.md`. The CRM has one writer: sales-crm on GrokBot. The worker never writes the CRM, never sends to a person and never posts.

These were tested locally from an unpacked pack, with a real server process: a suppression add on the bot is held by the worker's engine; an opt-out recorded by the worker's engine is held on the bot; the scrape pool caps across both sides; STOP on the bot stops the worker's next guarded job; and with the server killed, the bot's guards hold. On 2026-11-15 `worker/selftest.py` was added and passes 70 of 70 on this Mac and on Ubuntu 24.04, and `install.sh` was run in a throwaway local Ubuntu container (no systemd there, so the service was started by hand as the unit would start it): the unit, the 16 cron lines, the key file and a cron line run exactly as cron runs it all work, and a second install run is safe. That run found and fixed: the key file was root-only, so every cron job (which runs as `revworker`) started with no keys; cron's PATH hid an npm-installed `codex`; a second `install.sh` run died on the suppression link; a bad request body dropped the connection instead of answering 400; an order for a job that was off or held was reported `done`; a non-number score from a model stopped a job; a broken line in the reply inbox wedged the reply sort; scraper re-tests ran outside the scraper's folder; and the watchdog's pool alarm was described but missing. **Not deployed:** no droplet exists, and no Orgo computer was touched. **Not tested:** systemd starting the service on a real server, a real Codex or Hermes answer, and the engine's live calls (PlusVibe, Consulti, SpeakerAgent, Lead Radar's real `/api/data` shape).

## Bring-up (after Justin's steps on NEEDS-JUSTIN)

1. Create the server (Ubuntu, UTC), unpack the pack to `/opt/revenue-worker/repo`, and run `bash repo/worker/install.sh`. Every job starts off.
2. Put HTTPS in front of the worker's port (Caddy with a name Justin owns, or a Cloudflare tunnel), and give the bot `WORKER_URL` and `WORKER_TOKEN` by hidden prompt.
3. Justin gives the worker its keys (`worker/worker.env.example`, into `/etc/revenue-worker.env`) and signs the Codex CLI in as the job user: `sudo -u revworker -H codex login --device-auth` (a sign-in as root is invisible to the jobs).
4. Move the suppression list, `standing-approvals.md` and `spend-approvals.md` to the worker's `context/`. The bot then runs `suppression.py sync`.
5. Switch jobs on in `context/worker-jobs-on.md`, `test` first, one lane at a time: the watchdog and digest first, then replies, radar, shows, Skool and lists. `list-load` goes last.
6. Point the PlusVibe and Instantly reply webhooks at nothing new: the worker pulls replies itself. Set `BOT_REPLY_WEBHOOK_URL` to the bot's Reply webhook routine so hot replies wake it.

## Never

- The worker never sends, posts, writes the CRM, solves a CAPTCHA, or gets past a block. A paid call goes through the spend guard on the worker like everywhere else.
- No host names, addresses, tokens or computer names in this pack. They are intake values.
