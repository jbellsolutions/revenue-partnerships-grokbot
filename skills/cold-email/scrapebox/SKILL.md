---
name: scrapebox
description: Use for scraping and list jobs - fill in rows, look up businesses, pull a phone, email or price from many sites, read one page or crawl a site. Write and run your own script on the machine you are on first, pilot it on 20 rows, and spot-check before calling a list done. Send only the rows it cannot get to the hosted Scrapebox (scrape, crawl, saved scrapers, Google Maps places, Google results, a browser agent, Apify actors), where every paid call is quoted first and runs only after the user's yes, inside a cap. Also for calling Scrapebox's HTTP API or CLI from a script.
---

# Scrapebox

**On this GrokBot, the money rule is the spend guard.** Justin gave a standing $5 a day for paid scrape rungs (2026-11-12, "Yes, $5 a day cap"). Before any paid call, take the box's quote and run `python3 repo/guards/scripts/spend_guard.py <job-name> <quoted-usd> --pool scrape`. `approved`: call with `approve: true` and `max_cost_usd` set to the quote. `held`: the plan and its quote go to `requests/justin/`, and the run carries on with free rungs only. Never raise a cap, never split a job to fit under it.

Your own code does the work. The hosted Scrapebox is the fallback, for the rows your code could not get and for anything that needs a paid key or a proxy.

## Your own code first

For a list job (fill in rows, look up businesses, pull one field from many sites), write a plain script and run it on the machine you are on. That is what has worked at scale. A standard-library Python script filled phone numbers on a large list for $0, where a paid-first router produced far fewer leads. [references/proven-runs.md](references/proven-runs.md) has these runs with their sources.

1. **Write it plain.** Use Python's standard library (`urllib`, `re`, `json`, `concurrent.futures`), or `curl_cffi` when a site refuses a plain client. One function takes a row and returns the value, the URL it came from and a status (`found`, `not_found`, `unreachable`, `parked`).
2. **Make it resumable.** Keep results in a state file keyed by row. Write it to a temporary file and `os.replace` it after every batch, so a rerun skips the finished rows. Log every row with its value, source URL and status.
3. **Pilot it on 20 rows,** on the machine that will run the job.
   - Measure the hit rate: rows found ÷ rows tried.
   - Read the misses and a few of the hits. Fix the script and rerun the same 20 until the rate stops climbing.
   - Where it runs matters. The free fetch reads far more directory pages from a home address than from a datacenter box; an agent on a VPS has a datacenter address too.
4. **Scale with threads and resume.**
   - The gym run used 50 threads, because every row was a different site.
   - Against one site, use one connection and a delay between requests. Or use the box's `crawl` or `scraper`, which space requests per host.
5. **Retry the failures slowly.** Rerun the `unreachable` rows at a few threads before you count them as failed (the gym run retried at 8). A busy run causes some of its own failures.
6. **Send only what still fails to the box.** Put those rows in their own list. Try the box's free tools first, then the paid rungs through [the money rule](#the-money-rule).

### Two of those scripts are already written

Scrapebox ships two local commands for the most common list jobs. They are free, need no box or token, and are resumable (`--resume`, then `--retry` for the failures). Each writes `OUT.csv` with its columns added, never overwriting a filled cell, and `OUT.changes.csv` with every cell written and its source URL. `docs/local.md` in the Scrapebox source repo has every flag.

```bash
scrapebox enrich IN.csv --domain-col website --out OUT.csv          # phone, emails, socials, booking link from each site
scrapebox places IN.csv --name-col name --address-col street --city-col city --state-col state \
  --zip-col zip --out OUT.csv                                        # Google Maps: phone, website, category, verdict
```

- **Install:** `pip install -e .` from a clone (the Scrapebox source repo, given at intake).
- **Check `scrapebox enrich --help` first.** If it doesn't print the enrich usage, `scrapebox` on the PATH is another program; run the clone's own instead: `.venv/bin/scrapebox …`, or `.venv/bin/python -m scrapebox.cli …`.
- **`places` takes the rows one at a time, 2 s apart,** so 1,000 shops take about 45 minutes.
- **A `places` verdict of `none` means Maps has no place under that name and address.** It was 26% of Florida barber licenses. Use the website or the trade name for those rows, not a paid re-read.
- **Pilot both on 20 rows first,** as above, and spot-check before you call the list done (next section).

Your script makes free requests only. Never call Firecrawl, Decodo, Bright Data, Apify or any other paid API from your own code, even with keys you find on the machine. Paid reads go through the box, where the ledger reserves each one against an approved cap.

## Before you call a list done

Spot-check it, whoever filled it: your script, the box, or an actor.

1. Take 20 filled rows at random, or all of them if there are fewer.
2. Open each row's source URL with a free fetch (your own code, or `scrape` on rung 0). Check two things:
   - the value is on that page;
   - the page belongs to that row's business: its name, domain or address is on it.

   A page the box read on a paid rung may not open for free. Check that row against the page the box read instead: its `content` in `job results`. When neither is there, the row is unchecked, not failed. Draw another row in its place, and report how many were unchecked.
3. A row fails if:
   - the value is not on the page;
   - the source redirects to another domain, or to a parked or for-sale page;
   - the value belongs to someone else: a fax number, or the number of a web agency, a directory or a head office.
4. Report the hit rate (rows filled ÷ rows tried), the spot-check pass count (passed of 20) and a confidence level:
   - **high:** 20 of 20 pass;
   - **medium:** 17 to 19 pass. Name the failures and what they have in common;
   - **low:** 16 or fewer pass. The list is not done. Fix the script and run it again, or hand the list over marked unverified.

For example: "Phones: 312 of 650 rows filled (48%). Spot-check: 19 of 20 passed (one source redirected to a parked domain). Confidence: medium."

## The box: for the rows your code could not get

One hosted box that scrapes the public web. It reads each page up a ladder, cheapest first, and climbs only when a rung cannot read it:

| Rung | What reads the page | Cost |
|---|---|---|
| 0 | A Chrome-TLS fetch from the box (curl_cffi, Scrapling's transport) | free |
| 1 | The same fetch through Decodo's residential proxies | per GB |
| 2 | A page API: Decodo's Web Data API and Firecrawl first, then Bright Data Web Unlocker | per page |
| 4 | Scrapebox's own agent: Jev picks every click on a Browser Use Cloud browser | per step |
| 5 | An Apify Store actor (Google Maps, Instagram, marketplaces) | per result or event |

The provider keys live on the box. A session needs only the box's address and its bearer token (see Connect). [references/providers/](references/providers/README.md) has a profile of each paid provider: what it is good for, what it costs, and what has been measured.

Call **`status`** first, and again when anything fails. Its `guide.now` says which rungs can run on the box today, and why the others cannot.

| Tool | Use it for | Paid? |
|---|---|---|
| `scrape` | One URL as markdown, text, HTML or links; `format: contacts` for emails, phones, socials and booking links from the whole page and its contact pages | rung 0 free; above it, gated |
| `crawl` | URLs, sitemaps or a whole site as one resumable job (`format: contacts` too) | rung 0 free; blocked pages re-read gated |
| `scraper` | Save a recipe (`item`, `fields`, `next_page`); `test` its fill rate free; `run` it over many pages | `run` above rung 0 gated |
| `places` | Google Maps by name and address, up to 5,000 per job: phone, website, category, rating, and a `verdict` on whether it is the same business | free; blocked lookups re-read through proxies, gated |
| `job` | Follow a slow call: `get`, `results`, `export` (csv/json/jsonl), `cancel` | free |
| `search` | Google results as rows (Bright Data SERP), up to 100 queries at once | gated |
| `agent` | A goal and a start URL, for pages that need clicks, typing or choices first | gated |
| `actor` | `find` and `get` an Apify actor (free); `run` it | `run` gated |

Free tools for the rows your script missed:
- **Businesses with no website yet:** `places` with each business's name and address gives the phone, the website and a `verdict`. Keep the `yes` rows, and look at the `address_only` rows yourself.
- **Emails and social links from a site:** `crawl` with `format: contacts` over the websites, or `scrape` with `format: contacts` for a few. To read each site's contact and about pages too, add `follow: true, max_depth: 1, include: ["contact|about"]`.
- **A directory or list site:** write a `scraper` recipe, `test` it until the fields fill, then `run` it. Build it once and run it many times. Don't put an agent on every page.

None of these needs an agent, a browser or a paid rung unless Google or a site blocks rung 0.

## The money rule

Before you quote a bulk ask, ask the user how many they want: that number sets the quote and the cap.

Every paid call works the same way:
1. Call it without `approve`. Nothing paid runs; the answer is a quote (the worst case, per rung).
2. **Show the quote to the user and wait for their yes.** Never approve for them, and never raise a cap they did not name.
3. Call again with `approve: true` and `max_cost_usd` set to the amount they approved. That is the job's cap. Each step reserves its worst case first and settles to what it really cost. A step that does not fit is never started.

On top of each job's cap, the box has a **daily ceiling** (`status.daily_ceiling`, UTC day), shared by every caller. A step past it is refused with code `daily_cap`. Only the box's owner can raise it.

## Connect

- **On this GrokBot:** `SCRAPEBOX_TOKEN` (and optionally `SCRAPEBOX_URL`) come from `/workspace/revenue-partnerships/.secrets/scrapebox.env`; load them with `set -a; . .secrets/scrapebox.env; set +a` in the run's shell. Never print them.
- **Anywhere else:** set `SCRAPEBOX_TOKEN` (the box's bearer token) in the environment Claude Code starts from. `SCRAPEBOX_URL` names the box (no default: set SCRAPEBOX_URL at intake). Use one or the other: a machine with `scrapebox-cloud` and this plugin has two servers for one box.
- **Scripts, other agents and servers:** the HTTP/JSON door, below.

## Calling the box from a script

Your own script can hand its failed rows to the box. Every tool is also `POST <box>/api/v1/<tool>` with the tool's arguments as JSON. `GET /openapi.json` describes all of them (no token needed). `GET /api/v1/status` is status. The bearer token goes in `Authorization` on every other call.

```bash
curl -s -H "Authorization: Bearer $SCRAPEBOX_TOKEN" -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "format": "text"}' "$SCRAPEBOX_URL/api/v1/scrape"
```

```python
import json, os, urllib.request

BOX = os.environ["SCRAPEBOX_URL"]  # set at intake; no default

def call(tool: str, **args):
    req = urllib.request.Request(f"{BOX}/api/v1/{tool}", data=json.dumps(args).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + os.environ["SCRAPEBOX_TOKEN"],
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())

run = call("crawl", sitemaps=["https://example.com/sitemap.xml"], max_pages=500, wait_seconds=0)
done = call("job", action="get", job_id=run["job_id"], wait_seconds=60)
rows = call("job", action="results", job_id=run["job_id"], limit=200)
```

The `scrapebox` CLI does the same from a shell. Install it from the repo with `pip install -e .`, set `SCRAPEBOX_URL` and `SCRAPEBOX_TOKEN`, then run for example `scrapebox scrape https://example.com --format text` or `scrapebox job export <job_id> --format csv > rows.csv`.

Long calls take `wait_seconds` and a `request_id`. They return a `job_id` when they are not done in time; follow it with `job get`. Sending the same `request_id` again returns the same job, never a second run. Send one on every paid call: if your client gives up waiting, the job keeps running on the box, and a retry with the same `request_id` returns it instead of paying twice. A refusal is `{"error", "tool", "code"}` (HTTP 422). Its `code` is `invalid_input`, `provider_down`, `daily_cap` or another machine-readable reason.

## Never

- Approve a paid call without the user's yes on that call's quote, or loop paid calls without a cap.
- Call a paid API from your own script. Paid reads go through the box and its ledger.
- Call a list done without the spot-check above.
- Put the bearer token in a URL, a log, a file in a repo, a chat message or a job's arguments.
- Ask Scrapebox for contact or lead databases: they are not here (data-box has them). Scrapebox scrapes public pages, including directories and maps, with the tools above. Never propose a paid enrichment service (Clay, Apollo, Hunter, ZoomInfo and the like): your code and these tools do the gathering.
- Point it at private, loopback or metadata addresses. They are refused on every rung and every redirect, and the box's firewall drops them too.

## More

- [references/proven-runs.md](references/proven-runs.md): measured runs, their numbers and where each number comes from.
- [references/providers/](references/providers/README.md): the paid providers, copied from SuperBrowser and checked against Scrapebox on 2026-10-20.
- `docs/tools.md` in the repo: every tool, its arguments and examples.
- `docs/deploy.md`: where the box runs, how it is shipped, and its limits.
- `GET /openapi.json` on the box: the schemas, generated from the same tool cards.
