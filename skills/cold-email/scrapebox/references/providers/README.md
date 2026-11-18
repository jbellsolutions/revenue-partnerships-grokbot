# Providers: the scrape lane

One profile per paid service Scrapebox reaches, or may reach: what it is good for, what it costs, how it is called, and what has been measured.

Read these to understand a quote or a failure. You don't pick a provider by hand: your own code goes first, and the box's ladder picks the rung, inside a plan the user approved.

## Where they came from

These profiles were copied from SuperBrowser (its knowledge vault, `providers/`) on 2026-10-20. They are copies, not links. Then each one was checked against Scrapebox's `src/scrapebox/config.py` and `docs/sources/`:
- a claim that was out of date is corrected in place, with Scrapebox's figure and its date;
- a claim nobody in Scrapebox has checked is marked *unverified, 2026-10-20*;
- SuperBrowser's own tools, paths and tiers are replaced with Scrapebox's.

| Profile | Provider | In Scrapebox (2026-10-20) |
|---|---|---|
| [decodo-http.md](decodo-http.md) | Decodo: residential proxies, and the Web Data API | rung 1 (proxies), rung 2 (first page API) |
| [firecrawl.md](firecrawl.md) | Firecrawl | rung 2 |
| [brightdata-unlocker.md](brightdata-unlocker.md) | Bright Data Web Unlocker | rung 2 |
| [brightdata-serp.md](brightdata-serp.md) | Bright Data SERP API | the `search` tool |
| [brightdata-dataset.md](brightdata-dataset.md) | Bright Data datasets and ready-made scrapers | not wired |
| [brightdata-proxies.md](brightdata-proxies.md) | Bright Data proxies | not wired; Decodo is rung 1 |
| [browser-use.md](browser-use.md) | Browser Use Cloud browsers, and the open-source browser-use agent | rung 4 (live), rung 3 (not built) |
| [rtrvr.md](rtrvr.md) | Rtrvr.ai | rungs 3 and 4, not built; never called |
| [apify.md](apify.md) | Apify Store actors | rung 5, the last resort |

## What was left behind

- **SuperBrowser's browser fleet:** Airtop, Browserbase, Hyperbrowser, Steel, Orgo and local Playwright. Scrapebox runs no browser on its box and drives Browser Use Cloud's browsers instead (CHARTER, invariant 6).
- **Its routing orders:** Apify first, then Bright Data, then Firecrawl, then a browser; and for directory crawls, Firecrawl, then Bright Data's Web Unlocker, then Browserbase. Both start with a paid service. Scrapebox goes the other way: your own code, then the box's free rung, then the paid rungs, and Apify last.
- **Paid enrichment services:** none are profiled here, and none are ever proposed (Clay, Apollo, Hunter, ZoomInfo and the like). Your code and the box do the gathering.
