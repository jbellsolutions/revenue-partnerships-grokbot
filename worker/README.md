# The revenue worker

The volume half of the bot: a small server that runs cron jobs, the `gtm-box` engine, the Codex CLI and (optionally) Hermes, so GrokBot only orchestrates. Why and what runs where: [../WORKERS.md](../WORKERS.md).

| File | What |
|---|---|
| `install.sh` | Installs on a fresh Ubuntu server (UTC): the service, the crontab, every job off. Nothing paid |
| `server.py` | The API the bot calls (bearer token): guard state, digest, orders. Standard library only |
| `run_job.py` | Runs one job with its switches (`context/worker-jobs-on.md`), STOP and approvals; `--crontab`, `--list` |
| `jobs.json` | Every job: cron, command, tier (code, subscription, api, browser), guarded, orderable |
| `jobs/` | The worker's own jobs: reply sort, radar poll, scoring, scrapers, watchdog, digest, orders |
| `think.py`, `prompts/` | The model router (Codex, then Hermes, then a metered API) and the judgment prompts |
| `selftest.py` | The local self-test above |
| `worker.env.example` | Key names only; values go in `/etc/revenue-worker.env` |

Self-test, no server, keys, model or spend: `python3 worker/selftest.py` (70 checks: the API, the bot's guards in worker mode and with the worker down, every one of the worker's own jobs on fixtures with stub brains, orders, the digest, the watchdog). It does not cover the engine's calls to PlusVibe, Consulti or SpeakerAgent, the Skool browser, or a real Codex answer.

By hand: `WORKER_HOME=$(mktemp -d) WORKER_TOKEN=<24+ chars> python3 worker/server.py --port 18787`, then point a scratch bot workspace's `.secrets/worker.env` at it.

The HTTPS front (Caddy or a Cloudflare tunnel) is Justin's step: the server listens on 127.0.0.1 only.
