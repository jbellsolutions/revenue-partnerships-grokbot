---
name: bot-guards
description: The checks every role runs in code before it drafts, sends or spends, and the heartbeat it writes at the end. Load on every run.
---

# Guards

These are code, not advice. Run them; don't reason around them. Paths are relative to the workspace.

| Before you | Run | It answers |
|---|---|---|
| Draft to anyone | `python3 repo/guards/scripts/suppression.py check "<name, business, email or url>"` | `clear` or `held`. Held means stop on that person |
| Someone says no | `python3 repo/guards/scripts/suppression.py add "<who>" "<reason>"` | Done for every role |
| Send anything | `python3 repo/guards/scripts/send_guard.py <message-type> --routine <NAME>` | `auto`, `draft` or `stopped`. Draft means it goes to `requests/justin/` |
| Spend anything | `python3 repo/guards/scripts/spend_guard.py <plan-id> <usd>` | `approved` or `held`. Held means the plan and its cost go to `requests/justin/` |
| Paid scrape rung or Decodo | `python3 repo/guards/scripts/spend_guard.py <job> <quoted-usd> --pool scrape` | `approved` (reserved against the $5 a day pool) or `held` (pool spent: free rungs only) |
| See the pool | `python3 repo/guards/scripts/spend_guard.py today` | What each pool spent today (UTC) |
| End a run | `python3 repo/guards/scripts/beat.py write <role> '<line>' found=N drafted=N sent=N` | Your heartbeat. The watchdog alarms on a silent role |
| Write to an Orgo computer, remote box, agent or org | `python3 repo/guards/scripts/never_touch.py check "<target>"` | `clear` or `refused`. Refused, or no list, means stop |
| Watchdog | `python3 repo/guards/scripts/beat.py status --hours 26` | `SILENT <role>` lines to alarm on |

Never print the suppression list, read `.secrets/`, or edit a guard or a switch file to get past it.
