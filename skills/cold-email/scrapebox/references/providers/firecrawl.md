# Firecrawl

*Copied from SuperBrowser's `providers/firecrawl.md` (commit 108816c) on 2026-10-20, and checked against Scrapebox's `config.py`, `docs/sources/firecrawl.md` and `docs/PLAN.md`.*

**In Scrapebox:** rung 2, a page API, second in rung 2's order after Decodo's Web Data API (`SCRAPEBOX_RUNG2_ORDER`). SuperBrowser put it in tier 2.

**What it does:** a REST API (`api.firecrawl.dev`) that fetches a URL with JavaScript rendering and its own proxies, so there is no browser to manage.
- Scrapebox calls `POST /v2/scrape` (SuperBrowser named `/v1/scrape`). It asks for `rawHtml`, the page as served, so recipes run on it, with `proxy: "auto"`. Moving up to enhanced proxies costs no extra credit.
- The same key opens map, crawl, extract and search. Scrapebox has not wired those yet (the Firecrawl and Decodo charter).

**Best for:** public pages and directory or listing pages that the free fetch and the residential proxy could not read, and that need no login.
- **Measured from the box (2026-10-20):** it read G2, Glassdoor and Crunchbase, where Decodo's API came back empty.

**Cost:** 1 credit a page, settled on the answer's `metadata.creditsUsed`.
- $0.0038 a credit at the Hobby plan's list rate ($19 for 5,000 credits). This account shows a 1,000-credit plan, so the rate is still a price to confirm. About 947 of 1,000 credits were left on 2026-10-20.
- SuperBrowser's "~$0.002–0.003 a page" is out of date.

**Concurrency:** at most 5 calls at once (`SCRAPEBOX_FIRECRAWL_CONCURRENCY`). That is the Hobby plan's limit, recorded as the plan's limit, not Scrapebox's design. SuperBrowser's "fan out many concurrent requests" does not hold on this plan.
- The key is shared with other tools, and a Hermes pull once took its balance to −330 credits. A balance floor stops any call that could take it below 0.

**Auth / anti-bot:** light. It handles JavaScript and basic bot walls, but not logins, and not hardened Cloudflare or DataDome.
- It refuses some sites outright: Yelp answered "we do not support this site" on 2026-10-20. Bright Data's Web Unlocker read it.

**When to pick it:** you don't pick it by hand. The ladder reaches it inside an approved plan, after rung 0, the proxies and Decodo's API.

**Gotchas:** not for logged-in portals or multi-step flows. Those need clicks: rung 4.

**Env:** `FIRECRAWL_API_KEY`, on the box.
