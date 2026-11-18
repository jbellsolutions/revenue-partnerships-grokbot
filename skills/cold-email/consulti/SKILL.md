---
name: consulti
description: Consulti on this computer, end to end. Search B2B leads, verify and catch-all verify, enrich by email or LinkedIn, Instagram search, saved lists, placement tests and credits, through the consulti CLI and this computer's list tools. Use for any lead pull, verification, enrichment or credit question.
---

# Consulti

Consulti is this computer's lead source and its verifier. Justin, 2026-11-07: Consulti and treg are all the data we need for now, and Consulti verifies everything. No paid enrichment service beyond those two, ever.

## The CLI (consulti 0.2.1, from `consulti skill`)

Every command prints JSON on stdout. Run `consulti <command> --help` for flags.

| Command | What it does | Cost |
|---|---|---|
| `consulti credits` | Lead and verification credits left | Free |
| `consulti whoami` | Key prefix, base URL, spendable credits | Free |
| `consulti meta-filter <filter>` (`meta`) | Canonical values for a filter: titles, industries, countries | Free |
| `consulti leads-search` (`search`) | Search B2B leads. `--body '{...}'` for a full JSON body | 1 lead credit a row |
| `consulti verify --email E` | Verify one address | 1 verification credit |
| `consulti verify-catchall --email E` | Second check on a catch-all address | Billed |
| `consulti enrich --email E` | Enrich one lead by email | Billed |
| `consulti enrich-linkedin --linkedin-url U` | Enrich by LinkedIn URL, live | Billed |
| `consulti instagram-search` | Instagram profiles (rev-partner's creators) | Billed |
| `consulti lists-get` (`lists`), `lists-create --name N`, `lists-add-leads <id>` | Saved lists | Create free, add billed |
| `consulti placement-tests-create`, `-sent <id>`, `-get <id>`, `-list` | Inbox placement tests | Create billed |

List flags take repeated values or commas (`--titles CEO,CTO`). `--jsonl` on search prints a row a line and writes `{"meta": {credits_used, has_more, total}}` to stderr.

Exit codes: 0 ok. 1 unexpected (run `consulti credits` before retrying a billed call). 2 bad flag or 400/422. 3 auth: no key, malformed key or 401. 4 plan or credits: 402. 5 rate limited or blocked: wait `retry_after`. 6 network or timeout: run `consulti credits` before retrying.

**The CLI never retries, and a retried billed call bills again.** After exit 1 or 6, read credits first and compare.

## How this computer pulls

Never call `consulti search` in a loop yourself for a campaign. Use the tools, which carry the lessons that cost credits:

```bash
python3 /workspace/revenue-partnerships/gtm-box/cold/list_build.py report                 # every campaign: verified against target
python3 /workspace/revenue-partnerships/gtm-box/cold/list_build.py build <campaign>       # top up to target, inside the day's credit cap
python3 /workspace/revenue-partnerships/gtm-box/cold/list_build.py import <campaign> <file.csv>   # Justin's list into a campaign
python3 /workspace/revenue-partnerships/gtm-box/cold/list_build.py clean <file.csv> --name <name> # a database for no campaign yet
python3 /workspace/revenue-partnerships/gtm-box/cold/list_build.py prune <campaign>       # take staff off an owners list, in PlusVibe first
python3 /workspace/revenue-partnerships/gtm-box/cold/first_lines.py build <campaign>      # a first line for each new lead
python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py load <campaign>          # new leads into the draft campaign and the CRM queue
```

- **Seen list.** Every search names the saved list `gtm-cold-seen` in `excludeListId`. Without it page 1 is the same rows, paid for again. That cost about 5,100 credits on 2026-11-07.
- **Owners only.** Principal, Director, Partner and Broker are staff grades too. The owner rule refuses a weak title with a staff word (engineer, manager, officer, product, school) and every school or government body.
- **Verification.** Only `good`: deliverable, not a role address, not catch-all. Catch-all runs about a third of some pulls; `verify-catchall` is a second paid check, worth it only for a short, valuable list.
- **The cap.** All pulls together stop at `LEAD_CREDIT_CAP` lead credits a day, default 3,000. A build that hits it stops and says so. Justin raises it; you never work around it.
- **The target is a floor.** A verified row past it was paid for and stays.
- **Rows never leave this computer.** Lists are mode 600 in `/workspace/revenue-partnerships/gtm-box/cold/lists` and `/workspace/revenue-partnerships/gtm-box/data/clean`. Counts go in notes and Slack, never a row.

## treg and One API

treg reaches people and company data Consulti doesn't: a work email from a name and domain, a web search, a page read. Use it through One API, which holds the treg connection, so no treg key sits on this computer:

```bash
python3 /workspace/revenue-partnerships/repo/skills/cold-email/one-api/scripts/client.py discover
```

Then `treg.email.find`, `treg.email.verify`, `treg.web.search` and `treg.web.extract`, each inside a running One API goal with `max_cost_usd` of $1 or less. A treg email is unconfirmed until Consulti verifies it. Read the one-api skill before the first call.

## The dashboard

The API covers almost everything. The dashboard at consulti.ai, in this computer's Chrome once Justin has signed in, covers the rest: reading the members of a saved list, the account's plan and usage, and what Consulti sells, such as mailboxes.

- Reading is fine. Buying anything, changing the plan, or creating or revoking an API key is Justin's.
- The key this computer uses is CONSULTI_API_KEY in box.env. Consulti's own guidance is that a person creates keys and runs `consulti login` themselves. If a call exits 3, report blocked=1 and say the key failed. Don't create one.
- One Chrome profile for Consulti. Stop at the first warning or sign-in prompt and tell Justin.
