# Runtime, scheduling and recovery contract

This file describes what the selected harness must implement. It is not an installed scheduler, database lock or budget controller. No runtime is verified by the mere presence of these files.

## One dispatcher

Use one recurring dispatcher per campaign, proposed hourly during an active launch and daily after stabilization. Only enable a cadence the owner grant permits and the host/account can sustain. Queue due times govern release checks, measurement, maintenance and reports. The dispatcher claims director ownership, reconciles state and advances a bounded batch. It exits quietly when nothing is due. Events can wake the same dispatcher with the same ownership rules; they do not start a second director.

The sample schedule plan in templates/schedules.json is desired state. Give each real job a stable campaign/purpose key, exact host job ID, owner, timezone, prompt version, work directory or storage reference, next scheduled instant, expiry, budget and cancellation route. List/reconcile jobs before any create/update. Use provider-supported management operations; do not edit internal scheduler stores. Keep actual handles in registry/jobs.json after successful setup.

## Fresh invocation algorithm

1. Read stop state, owner direction, grant expiry, config and latest valid checkpoint. Acquire exclusive director ownership using a mechanism the actual runtime enforces. A run that cannot obtain ownership exits without side effects.
2. Reconcile pending external effects, workers, resource reservations and scheduler state. Inspect the destination for uncertain actions before retry. An expired lease does not prove the old worker or network request is dead.
3. Select READY tasks with satisfied dependencies, or due evaluation/maintenance tasks. Blocked tasks do not freeze independent work. Resolve one task's necessary input as narrowly as possible.
4. Reserve worst-case resources from campaign/day/run/task limits and claim the task. Persist intent before dispatch or external mutation. Give the worker a bounded tool scope, deadline, output path and cancellation token.
5. Observe worker completion and inspect outputs. Run relevant independent verification. On failure choose a materially different repair when justified; do not repeat blindly. Keep uncertain consequential actions out of automatic retries.
6. Commit accepted state using atomic writes/transactions. Settle costs, release claims, persist pending effects and set exact next action. Advance due times only after their intended work is recorded. Exit before the invocation limit with a useful checkpoint.

## Ownership and stale-worker fencing

For a single host, an OS-supported lock held for the whole director invocation may satisfy exclusivity. Its lifecycle and crash release must be tested. Workers write isolated outputs and never share authoritative JSON writes. If the host's scheduler already serializes jobs, verify that events/manual runs cannot bypass that protection.

For multiple hosts/controllers use transactional compare-and-set claims with lease expiry and a monotonic generation/fencing token. Check ownership before applying accepted outputs and before privileged mutations. A stale worker's results cannot publish. Where external providers do not enforce fencing/idempotency, route mutations through the one active director and reconcile in-flight requests before replacement. Do not simulate a distributed lock with an owner field in JSON or a shared folder file.

## Action and cost records

Use append-only records modeled by templates/records.json. Before a handoff, deployment, DNS write, project mutation, submission, message, paid call or job creation, record action ID, operation, destination, payload fingerprint, dedupe/idempotency key, task ID, grant reference and expected receipt. Record confirmed, failed or uncertain outcome under the same ID. A successful API response still needs output inspection; a lost response is uncertain.

For paid work reserve a known upper bound across all running workers before dispatch. Include model usage, API calls, hosting, domain costs and optional placements. Zero means no new spend; null means unknown and blocks a new paid commitment. Count committed recurring expenses against the operating window. Enforce caps in tools/provider settings when possible; otherwise serialize paid actions through the director and use conservative reservations. If a relied-on cap cannot be enforced, do not claim cost-bounded unattended readiness.

Keep outstanding reservations until billing/outcome reconciliation. Do not release an uncertain charge just because the worker timed out. Do not regenerate an expensive result if it is retrievable by its existing receipt. Unknown costs never become zero in the report.

## Retry and failure behavior

Retry transient read/rate-limit failures with provider backoff and a bounded per-task attempt count. Correct invalid requests before retrying. For writes with unknown outcome, inspect records/releases/jobs by saved ID or fingerprint. Retry only after absence is established or the provider supports the same idempotency key with known semantics. Reconcile before requesting a new key.

Three materially different failed recovery approaches normally justify marking the affected task blocked with evidence, attempts and minimum intervention. Do not perform dangerous retries to meet this count. Corrupt state restores from the last valid checkpoint plus action/destination reconciliation. Authentication failures block only tasks needing that connection. A missing scheduler is a runtime gap; it does not erase completed drafts.

## Stop and renewal

Owner pause/cancel, grant expiry, explicit budget limit and critical unresolved release faults stop new affected work. Read stop state at every dispatch and before external mutations. Cancellation must reach active children; track worker IDs and terminate/cancel through supported tools. It cannot undo an already accepted external action; reconcile and report that outcome. Release reservations only after confirmed settlement.

On pause/cancel/expiry disable owned recurring jobs and event triggers, preserve receipts and current artifacts, reconcile in-flight effects, and write a handoff. Never delete unrelated jobs. A configuration flag alone does not prove a real job stopped. Verify native job states and that no owned active worker remains. Honor the owner's latest renewal grant; do not self-renew permissions or budgets.

## Suggested due work

The single dispatcher handles: immediate post-release functional checks; a next-day targeted recheck for fresh releases; weekly metrics and prioritization; weekly sampled AI panel when budget permits; event-based factual corrections; monthly meaningful inventory/content refresh; day-30/60/90 campaign decisions. Skip unnecessary checks when their inputs have not changed. Modify timing to fit evidence and data latency rather than refreshing every page on a clock.

## Unattended readiness proof

Demonstrate an actual scheduled invocation in a fresh context, durable state, exclusive ownership, saved-state resume, uncertain-write reconciliation, budget reservation/enforcement, expiry, cancellation propagation and live output verification. Save job/run IDs and receipts under registry/ and reports/. Test with harmless fixtures/previews before real production. If a capability is absent, say exactly which part remains interactive or staged. Reminders and skill memory alone do not constitute unattended execution.
