---
name: worker-plane
description: How the bot uses its worker (a Hermes and cron server, with a Codex subscription) so volume work never runs on GrokBot - read the worker's digest, place orders for list builds, scraper writes and runs, and reply sorts, and keep the bot to orchestration and judgment. Use at the start of every run that touches replies, leads, lists, shows, Skool or scrapers, and whenever a job would be repetitive or high volume.
---

# The worker plane

Justin, 2026-11-13: "always - what can we push to the hermes on a digital ocean server or a orgo computer? grokbot is just the orchestrator and automator. that way we can go super hard an still be profitable with keeping costs down." And: "we will not just use hermes on VPS/Orgo but also we can use a CLI subscription like codex to subsidize usage on grokbot".

**The rule.** GrokBot decides; the worker does. If a step is the same every time, runs on many rows, or only needs a cheap yes/no, it belongs on the worker. GrokBot keeps the plan, the judgment on anything that reaches a person, copy, approvals, the CRM write, and the scoreboard.

## Who does what

| Brain | Where | Pays with | Use for |
|---|---|---|---|
| Code (cron, scripts) | The worker | Nothing | Pulls, syncs, list builds, verification, scraper runs and re-tests, the watchdog, the digest |
| Codex CLI | The worker, signed in with Justin's ChatGPT plan | His subscription, not GrokBot's allowance | Writing and repairing scrapers, batch sorting (replies, leads, shows), bulk first drafts |
| Hermes, cheap model | The worker (or a computer that keeps a signed-in browser for Skool) | Metered, under the `model` spend pool | The same batch judgments when Codex is out of quota |
| GrokBot | Its own computer | The Grok allowance | The few items the worker marked hot, copy, approvals, CRM writes, the plan, the scoreboard |

`worker/think.py` tries them cheapest first (`THINK_TIERS`, default `codex,hermes,api`). Items no brain could judge come to you unjudged: you are the last resort, never the first.

## Every run

1. Load the worker: `set -a; . .secrets/worker.env; set +a`. The guards already use it (suppression, spend pools, STOP and standing approvals live on the worker; if it can't be reached, every guard holds).
2. Refresh the engine's copy of the list once: `python3 repo/guards/scripts/suppression.py sync`.
3. Read the digest, never the raw files:
   ```
   curl -s -H "Authorization: Bearer $WORKER_TOKEN" "$WORKER_URL/v1/digest?max=40" > state/digest.json
   python3 repo/usage/scripts/pick.py state/digest.json --path items --fields job,kind,id,intent,score,why,angle,url
   ```
   `counts` tells you the volume (replies sorted, leads kept, shows scored, opt-outs taken). `items` are only what needs you.
4. Act on the items in your role (draft the reply, the pitch, the comment), through the normal guards.
5. Hand volume back as an order instead of doing it:
   ```
   curl -s -H "Authorization: Bearer $WORKER_TOKEN" -H "Content-Type: application/json" -X POST "$WORKER_URL/v1/orders" \
     -d '{"type":"list-build","params":{"campaign":"<name>"},"by":"cold-email"}'
   ```
   Orderable jobs: `list-build`, `list-load` (only while `cold_email` is auto), `replies-sort`, `scraper-write` (write `tools/scrapers/<name>/SPEC.md` on the worker first, through an order note), `scraper-run`. Follow one with `GET /v1/orders/<id>`; never re-order the same thing.
6. End with the usual beat; it also reaches the worker, whose watchdog alarms Slack on a silent role. You run no watchdog of your own.

## STOP

`python3 repo/guards/scripts/stop.py on "<who>"` stops both sides. If it says the worker didn't get it, tell Justin in Slack at once so he can pause the sending tools by hand.

## Never

- Run a volume job on GrokBot because the worker is slow or down. Report blocked, do the judgment work you can, and let the watchdog alarm.
- Ask the worker to send, post or write the CRM. It sorts, builds, scrapes, scores and loads approved lists; people are reached only by the sending tools under approved templates, and the CRM has one writer (sales-crm).
- Put the worker's address or token in a note, a post, a file in `repo/`, or chat.
