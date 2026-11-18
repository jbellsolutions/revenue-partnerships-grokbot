# Hermes adapter

Documentation checked 2026-11-04; inspect the installed version's actual schemas before use. Nothing in this package was installed into Hermes.

Hermes documents `delegate_task` for isolated work and `cronjob` for scheduled tasks. Its cron sessions need the correct absolute work directory to load project instructions. Agent cron execution depends on the gateway. Use supported job-management operations, list existing jobs first, and save exact job IDs. Cron status/history help establish actual execution. A task/turn stopping is not sufficient evidence that delegated work stopped. [Official cron documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron), [official delegation documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation).

## Mapping procedure

1. Put the complete kit and campaign state in a private durable project directory. Load AGENTS.md and the director prompt. Normalize existing owner authority into the config and verify tools with harmless reads. Run website discovery and a small staged task before automating.
2. Map each ready task to the host's current delegation schema. Include its individual role file, complete task envelope, input versions, output destination, limits and stop token. Prefer leaf workers; this charter authorizes no recursive fan-out. Use a different context for release verification. When leaf workers cannot manage schedules, the runtime specialist prepares/verifies the plan and the director performs native job mutations.
3. Use the local canonical board initially. If the installed native board provides the required claims, dependencies and receipts, it may become authoritative after a deliberate migration. Keep only one queue and one owner for mutations. The native board is optional. [Official native-board documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban).
4. If recurrence is granted, map templates/schedules.json to one actual owned dispatcher job. Resolve timezone, workdir, prompt, expiry and notification destination against live tools. Do not paste a guessed API payload or edit a private scheduler file. Persist the returned job ID before creating anything else.
5. Run ACCEPTANCE.md's runtime drills. In particular test overlapping manual/scheduled wakes, saved-state access, a worker timeout, missing permissions, uncertain release reconciliation, budget reservations and child cancellation. Select native mechanisms that actually enforce these requirements. Add a small adapter only for a demonstrated gap.
6. Report the real scheduled run receipt and remaining gaps. If recurrence or independent review is unsupported in the current installation, keep the project interactive/staged and say which requirement is unmet.

Use the campaign's proposed limits even when the host supports more parallelism. Do not change host approval/security settings to increase autonomy. Keep privileged changes with the active director when worker credential isolation is unavailable.
