# Optional One API connection

The owner has a separate One API project (its own repo). This package does not install its server or inherit the owner's access. Provision the destination's own revocable credential and approved endpoint privately. Do not ship owner URLs, tokens, trial IDs or customer memory as client defaults.

Use installed `one_api_discover`, `one_api_call`, `one_api_job` tools when available, or the bundled standard-library client at `integrations/one-api/client.py` in the distribution. Its source is pinned to the One API revision in source-manifest.json. With the destination's own `ONE_API_URL` and `ONE_API_TOKEN` configured privately, run `python3 integrations/one-api/client.py discover` from the distribution directory; `--help` lists its call/job syntax. The installer records that directory as `distribution_root` in the profile's `speakeragent-install.json`. It does not copy the optional adapters into each profile.

Discover current `execution_status`, `input_schema` and provider readiness. `inventory_only` is not callable capability. Follow the live discovered schema and any installed One API skill rather than copying an old request body. Do not print connection configuration or paste credentials into a chat.

Map the work by capability:

| Research need | Candidate One API route; discover before use |
|---|---|
| Public text | `web.fetch`, `web.scrape` |
| Structured extraction | `crawl4ai.extract`, or versioned `scraper.test` then `scraper.run` |
| Web search | `web.search.quote` then `web.search`, or enabled `treg.web.search` |
| Rendered page | `browser.read`; fresh bounded read, not persistent click/type control |
| Contact discovery/verification | Enabled `treg.email.find` / `treg.email.verify`; capability and live status must be checked |
| Evidence/progress | `memory.write`, `goal.get`, local job receipts |

One API goals are caller-run. Create a finite research goal under an already authorized operator-configured trial, save its ID, then use stable request IDs and top-level goal IDs as required. Reuse the original request ID after a lost response with exactly the same arguments. For a deliberately fresh read use a new request ID.

Reserve paid work against the actual remaining shared budget. Unsettled reservations are not free balance. Use the route-specific result poller for remote pending work: the generic job read retrieves a local receipt and does not itself poll every provider. Preserve remote IDs and uncertain jobs. Do not reset a trial or change IDs to bypass limits. Read returned content before accepting it as evidence.

Use versioned memory with `expected_version`, and verify saved content. Complete a goal only when its criteria are checked and outstanding work is reconciled. None of this creates an unattended runner.

At the audited source snapshot, One API has bounded read/extraction/search routes, not arbitrary browser click/type or mail sending. Treg contact routes include contract/simulation coverage; their existence is not proof of a successful live verification for this client. Native fleet delegation has separate enrollment, identity and cost requirements. Use an independently available authorized browser when richer interaction is needed.

The existing One API prototype shares an owner's workspace across agent credentials. Namespaces are organization, not tenant isolation. For unrelated paying clients, provide properly isolated gateways/storage or another verified client boundary; do not connect every customer's profile to the owner's shared private workspace.

Without One API, use native search/browser/RSS and save the same case contract locally. Tool substitution changes acquisition, not evidence standards or the scoring method.
