---
name: scraper-forge
description: Write, test, run and repair the bot's own scrapers and data scripts, cheapest rung first - own Python on this computer, then One API and Scrapebox free rungs, then Decodo residential proxies and paid rungs under the $5 a day scrape pool. Use whenever any role needs data from many pages (Skool groups, podcast directories, partner lists, grant programs, creator lists, SERPs) or a request lands in requests/cold-email/scraper-*.md.
---

# Scraper forge

**Worker mode (WORKERS.md).** When the worker is set up, scrapers live and run there, not on GrokBot: write `tools/scrapers/<name>/SPEC.md` (target, fields, rows, rung), order `scraper-write` (Codex writes and tests it on Justin's ChatGPT plan), then `scraper-run`. The nightly re-test runs on the worker too. Write a scraper here only when the worker is down and the job can't wait, and say so in the daily file.

Justin, 2026-11-12: "great at writing custom code and scrapers all the time", "high volume and low cost", "if we need to use proxies with Decodo, we should be using proxies with Decodo. We have those already paid for."

The bot writes code first and buys pages last. Every scraper is a small program kept in the workspace, tested on a saved page, and reused. An agent clicking through pages is the last rung, never the plan.

## Where things live

| Path | What |
|---|---|
| `tools/scrapers/<name>/scrape.py` | The scraper. Standard library first (`urllib`, `html.parser`, `json`, `csv`); `requests`, `beautifulsoup4` or `selectolax` only if they're already installed |
| `tools/scrapers/<name>/fixture.html` | One saved page it must parse. The test runs on this, with no network |
| `tools/scrapers/<name>/README.md` | Who asked, the target, fields, rung it needs, last good run, known breaks |
| `tools/scrapers/REGISTRY.md` | One line per scraper: name, owner role, target, rung, status (`ok`, `broken`, `retired`), last run, rows |
| `data/<role>/<name>-<date>.csv` | Output (mode 600). Never in `repo/`, never posted |
| `requests/cold-email/scraper-<id>.md` | A request from another role: target, fields, how many, by which milestone |

## The ladder (climb only when the rung below fails on that page)

| Rung | How | Cost |
|---|---|---|
| 0 | Your own script, direct fetch, a person's pace (1 request every 2 to 5 seconds per site), a normal browser User-Agent | Free |
| 0b | One API `web.fetch` / `web.scrape`, or Scrapebox rung 0 (Chrome-TLS fetch): `python3 repo/skills/cold-email/one-api/scripts/client.py call web.scrape --arguments '{"url":"...","format":"text"}' --request-id <id>` | Free |
| 0c | One API `crawl4ai.extract` for Markdown or CSS records from one page | Free |
| 1 | Decodo residential proxy: your script through `DECODO_PROXY_USER`/`DECODO_PROXY_PASSWORD` (in `.secrets/decodo.env`), or Scrapebox rung 1, or a One API saved scraper with engine `decodo-proxy` | Prepaid balance; counts against the scrape pool |
| 2 | Page APIs (Decodo Web Data API, Firecrawl, Bright Data) through Scrapebox | Paid, scrape pool |
| 3+ | Browser or agent rungs, Apify actors | Paid, scrape pool, only for a page nothing else reads |

Datacenter IPs get refused by many directories (Scrapebox's benchmark: 14 of 20 pages read from a home Mac, 3 of 20 from a cloud box). This computer is a cloud computer, so expect rung 1 for directories and marketplaces. That is what the Decodo balance is for.

## Money

Every paid call, including Decodo traffic from your own script, goes through the scrape pool first:

```
python3 repo/guards/scripts/spend_guard.py <scraper-name>-<date> <worst-case-usd> --pool scrape
```

- `approved`: run it, with the provider's cap set to that amount.
- `held`: the pool is spent for today (or STOP is set). Write the plan and cost to `requests/justin/`, run the free rungs only, and say so in the daily file.
- Decodo from your own script: estimate the worst case as pages x 0.5 MB x the per-GB rate in `context/owner.md` (ask Justin for the rate at intake; until then use $8 per GB). Record the real bytes in the scraper's README after the run.
- `python3 repo/guards/scripts/spend_guard.py today --pool scrape` shows what's left. Never split a job to fit under the cap, never raise it.

## Build a scraper

1. Read the request. Name the scraper after the target (`skool-groups`, `podcast-directory-x`).
2. Look for an API, a sitemap, an RSS feed or a JSON endpoint the page already loads (open the page, read its network calls). Those beat HTML.
3. Save one real page as `fixture.html` (rung 0 or 0b). Write `scrape.py` with a `parse(html) -> list[dict]` and a `fetch(url)` that takes `--proxy decodo` as an option.
4. Test: `python3 tools/scrapers/<name>/scrape.py --test` parses the fixture and prints the rows and how full each field is. Fix until the fields you were asked for are at least 90% full on the fixture.
5. Pilot 20 rows live. Spot-check 5 by eye against the pages. Only then run the full job.
6. Write the README and the REGISTRY line. Hand the output path back to the role that asked through `requests/<role>/`.

For a site you'll scrape many times from One API's sandbox instead, use its saved scrapers: `scraper.save`, `scraper.test` on the fixture, `scraper.run` with engine `free` first (see `../one-api/references/custom-scrapers.md`).

## Keep them working

The nightly scraper run re-tests every `ok` scraper on its fixture and on 3 live rows. A scraper whose fields drop below 90% is `broken`: repair it in the same run if you can (new selectors from a fresh fixture), else note it for the role that owns it.

## Never

- Sign in to scrape, or scrape behind a login with someone else's account. Skool is read only through Justin's own signed-in session, by the social role.
- Solve a CAPTCHA, or keep going after a CAPTCHA, a login wall or an account warning. Stop that site for the day and tell lead. A proxy is for reading public pages at a person's pace, not for getting past a site that said no.
- Scrape private personal data, or use a paid enrichment service (Clay, Apollo, Hunter, ZoomInfo and the like). Emails come from Consulti or from the person's own public page, and are verified before use.
- Put a key in a scraper, a fixture, a README or the output.
