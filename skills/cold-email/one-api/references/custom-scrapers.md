# Custom scrapers

The dashboard's Custom scrapers workspace supports saving, testing and running our extraction code through existing Scrapebox connections. HTTP/MCP exposes `scraper.save/get/list/test/run/result`. Separate upstream deployments were not changed.

Save a synchronous function expression with `expected_version: 0` to create version 1. Subsequent saves require the latest version and preserve earlier source/hash values. Pin a version in tests and runs:

```javascript
(page, input, api) => {
  const rows = api.select(page.html, 'title').map(n => ({title: n.text, source: page.final_url}));
  api.log('Extracted ' + rows.length + ' titles');
  return rows;
}
```

`api.select(html, CSS)` returns objects with text, HTML and attributes. `api.log` saves bounded messages. `page` has HTML, requested URL and final URL; optional input is a JSON object. Fixture tests have no network access. Source must return an array of up to 100 objects; async functions/imports are unsupported.

Run with a top-level running goal and arguments `name`, `version`, `url`, `engine`, `max_cost_usd`, optional `input`. Engine `free` enforces zero cost and rung 0. Firecrawl and Decodo proxy use their direct paid Scrapebox lanes. Apify uses the fixed `apify/web-fetch` Actor with HTML output, one item, 128 MB memory, 60-second timeout and a native pay-per-event cap. The adapter refuses usage-priced and rental alternatives. It does not publish our own Apify Actors; our versioned extraction code runs in One API after cloud retrieval.

Paid calls reserve their maximum ($1 maximum per call) against the goal's existing shared trial. Apify caps use at most four decimal places because the upstream rounds to that precision. The gateway reads the private existing APIFY_TOKEN for fixed-origin native billing verification. It compares counted events at the run's prices, native usage and upstream reported cost conservatively. Missing billing or a missing successful-fetch event retains the reservation. Provider credentials never enter the extraction process, frontend or portable skill.

Poll `scraper.result` with the original local job ID and same top-level goal. Remote job identity and pinned context survive a restart or cancellation after dispatch. A lost response without a known remote ID stays uncertain: inspect upstream state before any further action. Polling never repeats paid retrieval. Receipts retain structured records, logs, hash, provider, charge and native billing summary; raw retrieved HTML is not copied into scraper receipts. Saved source and optional run input are private recovery state, so do not put credentials there.

The disposable local QuickJS-NG worker has no host filesystem/network/import bindings, uses an empty environment and temporary working directory, and runs in Python isolated mode. Limits: five-second wall deadline, two-second CPU soft limit, 32 MB JS heap, 512 KB JS stack, 1 MB HTML, 300 CSS calls, 50 bounded log entries, 100 records / 180 KB output. It is a language boundary for this trusted single-owner prototype, not OS isolation against engine exploits or hostile tenants. Arbitrary Python/npm dependencies, autonomous crawling and owned Actor deployment remain unfinished. Provider truncation can impose a smaller input limit and is refused rather than silently treated as a complete page.

Managed proxies avoid relying solely on this Mac/VPS IP, but sites can still block or rate-limit requests. Public-address checks remain enabled. Managed services may render internally; no Browser Use session or computer is launched by this adapter. The gateway's call semaphore is not a fleet-wide resource limit.

## Checked November 2, 2026

The first free heading test returned zero records: example.com's current HTML no longer has an h1. Its receipt and stopped caller goal remain visible. A corrected title scraper passed its fixture, then produced the expected Example Domain title using free HTTP, Firecrawl and Apify. Their costs were $0, $0.0038 and $0.00155. Decodo is implemented but not live-tested in this increment. [Saved proof](../reports/custom-scrapers-proof.json).

Native Apify billing briefly reported only its start fee in usageTotalUsd despite counting the fetch event. One API now includes native event prices. The initial receipt was corrected with an audit event, preserving its request/remote IDs and making no further paid call. The operator helper `scripts/reconcile-apify-billing.py` reads a known finished run for such reconciliation; it cannot create an Actor run. Shared trial totals: $0.00685 spent, $0 held, $4.99315 remaining. No Browser Use sessions, computers or messages were created.

Use `goal.stop` to close an unsuccessful caller goal without claiming its criteria were met. It refuses unresolved work and does not cancel providers. A returned empty result is not task completion; the caller must check expected fields and records.

## Request a scraper and export source

The dashboard field builder turns a short description into an editable selector template. Inspect row/field selectors against the real source, then save, test and run through the existing managed lanes. The extractor already runs on our DigitalOcean-hosted service. Source exports support a read-only browser snippet, standalone Python/Docker project and Apify Actor project; exports carry no credentials and do not deploy or start paid work. Managed/exported extraction is fixture-tested; the custom Actor itself has not been deployed by exporting it. See [request workspace](dashboard-workspace.md).
