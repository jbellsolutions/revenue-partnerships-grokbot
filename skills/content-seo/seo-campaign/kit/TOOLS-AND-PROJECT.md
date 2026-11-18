# Tool contract and automatic project creation

## Minimum practical stack

| Capability | Minimal implementation | What access enables |
|---|---|---|
| Agent and scheduler | The chosen Hermes or Grok Bot environment | Reasoning, bounded workers, fresh scheduled sessions |
| Durable state | Private project folder; Git for code and versioned documents | Resume, artifacts, change history, rollback |
| Public research | Browser/HTTP fetch plus search | Site audit, competitors, cited-source inspection |
| Website write/release | Existing CMS editing connection or repository plus hosting connection | Drafts, previews, scoped production releases |
| Measurement | Search Console plus existing analytics; conversion/lead outcomes if available | Diagnose discovery and evaluate business impact |

One harness, one private folder and the existing website stack are the core. A custom backend is unnecessary for a single director. A local queue works without paid project software. Search Console and analytics improve measurement but their absence must not block public research and staged work.

Conditional tools: DNS for permitted new subdomains; keyword/SERP/backlink data for scale; AI-answer observation tools for reproducible testing; real business-profile access for eligible businesses; mail/post/submission tools for explicitly authorized authority work; a transactional database if controllers run across hosts. Do not request every tool before useful work begins.

Use available connected tools first. For new research capacity, one metered provider or gateway such as treg can cover several capabilities if the owner chooses it. Inspect available endpoints, current price, account limits and permitted use before calls. Provider-key charges still count in campaign spending even when a gateway does not meter them. No provider price or endpoint is guaranteed by this kit. Never register a new service or top up funds from this recommendation alone.

Prefer the site's current CMS/host. If no stack exists, choose a simple supported static deployment for content, or a CMS when the owner needs editorial controls. Record the choice and maintenance implications. DNS is optional; it is not needed to improve existing pages. Domain registration and email infrastructure are optional separate decisions.

## Capability inventory

For each available connection record: connection reference, service, account/project identity, permitted resources and operations, read/write status, price basis, limits, safe read probe, mutation receipt behavior, idempotency support, rollback mechanism, health status, checked date and missing scopes. Save this to connections.json. Store references only; secrets stay in the host's secret store. Use scoped credentials where the service supports them.

Do not declare a tool available because it appears in a prompt. A harmless live read proves only the specific capability checked. Test a draft write in the intended project and a preview release before relying on production. Record denied capabilities as missing; continue work that can be completed without them.

## Canonical project model

Project key: the normalized owner-approved website scope, not a guessed brand name. Reconcile aliases and redirects before creating a second project. A brand rename does not create a new campaign.

Required local layout (created by bootstrap helper):

```text
campaign/
  config/                 campaign.json, authority.json
  mission.md              goal, ownership, operating window
  checkpoint.json         exact next action, pending effects
  board.json              epics, tasks and dependencies
  registry/               roles, workers, external IDs, jobs
  knowledge/              brief, facts, inventory, page map
  research/               timestamped observations and opportunities
  work/                   task-specific briefs and candidate artifacts
  releases/               candidate manifests, checks, receipts, rollback
  metrics/                baselines, observations, experiments
  operations/             action ledger, budget ledger, stop state
  reports/                owner reports and decisions
```

JSON files are a portable interchange, not a multiwriter database. The director is their sole writer; worker outputs are isolated. Native transactional task tools may replace local storage when their claim and history semantics meet the same contract.

## Project-management adapter

If a project system is connected and authorized, create the live project and linked tasks automatically after discovery. For ClickUp, map a campaign to an existing owner-specified Space and a campaign Folder with phase Lists; use available task dependencies, custom fields and Docs. For other systems, map to their equivalent concepts. Discover the actual hierarchy and API schemas first; never invent IDs, statuses, fields or assignees. A role name is not a real user account. Do not invite people or send assignment notifications without scope.

Default epics: operations/setup; business truth/baseline; technical foundations; architecture; content/evidence; build/release; entity/authority; AI visibility; measurement/experiments. Create only relevant tasks. Seed templates are starter tasks, not a requirement to publish every content type.

Task fields: stable task ID, external ID, epic, title, outcome, owner role, status, priority, dependencies, authority reference, input versions, output paths, acceptance checks, due/evaluation dates, estimate/resource reservation, worker ID, attempts, evidence, blocker and cancellation token. Use states INBOX, READY, RUNNING, VERIFYING, DONE, BLOCKED, CANCELLED. Native statuses may differ if mapping is explicit.

Default views: ready work by priority; blocked/dependency graph; release candidates; scheduled evaluations; budget/capacity; outcomes. Keep the owner-facing view brief and link evidence. Do not use a dashboard's existence as proof the campaign works.

Choose one authoritative queue. If local is authoritative, mirror selected fields to the project service with a stable external-ID map and a documented one-way write contract; poll owner comments/directions separately and reconcile them deliberately. If native is authoritative, treat local board as a snapshot. Never allow two-way blind overwrites. Record each create/update intent and dedupe key; on timeout search by external ID before retrying. Reuse existing project objects.

## Website and infrastructure adapter

Required operations: inspect current version; create/edit a draft or branch; preview; export or version backup; publish an exact approved revision; inspect deployed revision and URLs; restore prior revision. If the provider cannot restore, prepare an alternative backup/restore method before live work. Match capabilities to task risk rather than assuming every CMS works like Git.

Subdomain plan: exact hostname, useful purpose, scope evidence, host destination, DNS record type/value, affected existing records, TLS, redirects, canonical origin, indexability, cross-site navigation, search property coverage, analytics, resource cost and rollback. Read-before-write and change only scoped records. Wait for actual DNS/TLS readiness; a provider's accepted change is not public availability. Do not modify MX, SPF, DKIM, DMARC, nameservers or apex routing as a side effect of adding a content subdomain.

## Prioritization

Default heuristic: expected business impact × evidence confidence × bottleneck relevance, divided by effort and operational risk. Use ordinal scores with a written reason, not false revenue precision. Compliance and broken core behavior can override the score. Distinguish missing access from low priority. Do not let the director repeatedly plan instead of completing ready tasks.

Split a task when its output cannot be verified independently, it requires unrelated permissions, or its execution exceeds the per-task time budget. Reuse coherent templates; avoid a task for every trivial sentence. Work-in-progress limits and ready dependencies govern concurrency.
