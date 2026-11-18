# Bright Data: SERP API

*Copied from SuperBrowser's `providers/brightdata-serp.md` (commit 108816c) on 2026-10-20, and checked against Scrapebox's `config.py`, `docs/sources/brightdata.md` and `docs/tools.md`.*

**In Scrapebox:** the `search` tool. SuperBrowser put it in tier 4.

**What it does:** runs a Google search through Bright Data's SERP API and returns the results.
- Scrapebox's `search` takes `query`, or up to 100 `queries` at once, with `num` results each (default 20), and optionally `country` and `language`. Each row is `query`, `position`, `title`, `url`, `description`.
- The call is `POST https://api.brightdata.com/request` with `{zone, url: "https://www.google.com/search?q=…&brd_json=1", format: "raw"}`. The answer is Google's results as JSON.
- SuperBrowser said Google, Bing and Yandex. Scrapebox's `search` asks Google only.

**Best for:** finding what to scrape: the directories and listings for a job, or "all X" landing pages, before any crawling.

**Cost:** $1.50 per 1,000 searches, $0.0015 each, at the list price (still a price to confirm; `SCRAPEBOX_BRIGHTDATA_USD_PER_REQUEST` overrides it). SuperBrowser's "~$0.01 a query" is out of date. Every search is quoted first and runs only after the user's yes.

**Scale:** one page of results per query, with no pagination. For depth, send more and varied queries.

**When to pick it:** when you don't already have the list of sources. SuperBrowser ran it "always, at the start of a bulk scrape". In Scrapebox it is paid, so skip it when the user's list, a sitemap or a directory you know already gives the sources.

**Gotchas:**
- It returns search results, not the data itself.
- Google's result counts are unreliable. Use it to find sources, then crawl them for the real total.

**Env:** `BRIGHTDATA_API_KEY` and `BRIGHTDATA_SERP_ZONE`, on the box. The SERP zone name is set at intake. Without the zone, `search` is not offered.
