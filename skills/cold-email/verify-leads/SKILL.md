---
name: verify-leads
description: >-
  On-demand email verification, list status, and list download for a cold-email
  agent, through the self-hosted Reacher gateway using the agent's OWN revocable
  key. Submitting new addresses shares ONE 10k/24h cap with the dashboard;
  checking status or pulling a list is a free read and works for ANY job on the
  stack, not just ones this agent submitted — including lists uploaded through the
  dashboard. Triggers: "verify these leads", "check this list before I send", "are
  these emails good", "how's the [name] list doing", "how many leads got verified",
  "pull the sendable list for job N", "send this list to verification". Does NOT
  send email and is NOT an automatic pre-send step.
---

> **Retired 2026-10-07:** the old Reacher backend was deleted to cut cost. Calls fail until a Reacher backend is redeployed and `REACHER_URL` is set at intake. Tell the user verification is offline instead of retrying.

# Verify Leads (agent gateway → self-hosted Reacher)

Talks to the Reacher gateway at `$REACHER_URL/verify*` using the
**agent's own `x-consumer-key`** — a separate, revocable credential from the
dashboard's `x-reacher-secret`. Three things it does:

1. **Submit** a list for verification — SMTP-probes each address without sending
   mail. Counts against the **same hard 10,000/24h budget** as the dashboard; if
   that's spoken for, the gateway returns **429** and this tool says so plainly
   instead of exceeding the cap (which would blacklist the single proxy IP).
2. **List / status** — every job on the whole stack, including ones uploaded
   through the dashboard (Marketing, Men's Health, whatever), not just ones this
   key submitted. No SMTP spend, doesn't touch the cap.
3. **Pull** — download any job's full CSV: the original spreadsheet's own columns
   (name/company/whatever) rejoined with the verdict and any enrichment data,
   filterable by bucket. Same output the dashboard produces.

**When to submit vs. not:** only submit when explicitly handed a raw list to
verify. Lists are normally verified on the dashboard *before* they reach the
agent — this is an occasional on-demand capability, not an automatic pre-send
step. Checking status or pulling a list, though, is safe to do anytime — it's
read-only.

## Commands

```bash
python3 tools/verify_leads.py leads.csv --json          # submit + poll + sendable set
python3 tools/verify_leads.py --jobs                     # list every job + daily cap
python3 tools/verify_leads.py --pull 50                  # any job's full CSV, any bucket
python3 tools/verify_leads.py --pull 50 --bucket SENDABLE -o sendable.csv
python3 tools/verify_leads.py --status 123                # re-poll a job THIS key submitted
```

- Submit input can be a **CSV/TXT file** (auto-extracts + de-dupes emails),
  **emails as arguments**, or **`-` for stdin**.
- `--json` on any command prints machine-readable output.
- `-o path` writes to a file instead of stdout (works with submit and `--pull`).
- `--bucket X` on `--pull` filters to `DELIVERABLE` / `ACCEPT_ALL` / `UNDELIVERABLE`
  / `RETRY` / `SENDABLE` (deliverable + accept-all); omit for every row.

Submit returns the **sendable** set — addresses whose verdict is **deliverable**
(`safe`) or **accept-all** (a catch-all domain or role account that still receives
mail). Undeliverable (`invalid`/disposable) and retry (`unknown`/greylisted)
addresses are excluded. `--pull` returns every row regardless, unless you filter.

## Auth (REACHER_CONSUMER_KEY, by hidden prompt)

The consumer key resolves in this order:
1. `REACHER_CONSUMER_KEY` environment variable (overrides everything), else
2. `config.json` next to this skill (one level up from `tools/`) → `{"consumer_key": "..."}`. Never commit it: the pack ships without one; put the key in `.secrets/` by hidden prompt.

The endpoint is `REACHER_URL` (no default; set it at intake)
(e.g. an SSH tunnel to the droplet) if DNS isn't resolving.

## What the result means

| In `summary` | Reacher verdict | Sendable? | Meaning |
|--------------|-----------------|-----------|---------|
| `deliverable` | `safe` | ✅ yes | Mailbox exists and accepts mail |
| `accept_all` | `risky` (catch-all / role) | ✅ yes | Domain accepts everything or it's `info@`-style — still receives your mail |
| `undeliverable` | `invalid` / disposable | ❌ no | Dead mailbox or throwaway — **hard bounces**, excluded |
| `retry` | `unknown` (greylisted / blocked) | ❌ not yet | Provider blocked the probe — re-run later with `--status` or resubmit |

**Honest limits:** catch-all domains accept every address, so no probe can confirm an
individual mailbox — those land in `accept_all` (still counted sendable, per Justin's
deliverable-first policy). `unknown` isn't "bad", it's "no answer this time".

## The shared cap (why 429 happens)

There is **one** 10,000-checks-per-rolling-24h budget for the whole stack, enforced
server-side by Reacher's throttle and mirrored by the gateway in real time
(completed-in-24h + live queue depth). The dashboard and this agent draw from the
**same pool** — "if the agent uses it, the dashboard doesn't, and vice-versa." A 429
means the pool is used up; wait for older checks to roll off, or verify the rest
tomorrow. To go beyond 10k/day requires adding proxy IPs — it is not a software limit.

## Anti-triggers (do NOT use this skill for)

- **Automatic pre-send verification** — do not wire this into the send pipeline;
  lists are verified on the dashboard before they reach the agent.
- Sending email / running campaigns (this only verifies).
- Finding or guessing addresses (no enrichment/discovery here — that's the dashboard's
  ✨Enrich).
- Bulk-processing a list the agent has no permission to handle.
