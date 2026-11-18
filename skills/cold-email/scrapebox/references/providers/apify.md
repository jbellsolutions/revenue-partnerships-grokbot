# Apify: the actor marketplace

*Copied from SuperBrowser's `providers/apify.md` (commit 108816c) on 2026-10-20, and checked against Scrapebox's `config.py`, `docs/sources/apify.md` and `docs/tools.md`.*

**In Scrapebox:** rung 5, the last resort, through the `actor` tool (`find`, `get`, `run`). SuperBrowser put it in tiers 2–6 and tried it first.

**What it does:** REST access to the Apify Store's ready-made "actors" (pre-built scrapers). There is one for most platforms (LinkedIn, Instagram, TikTok, X, Google Maps, Amazon, Zillow, YouTube and many niche sites), plus generic crawlers such as `apify/website-content-crawler` and `apify/cheerio-scraper`. You start a run, poll it, and read its dataset of records.
- **How many actors:** Scrapebox's snapshot (`catalog/apify`) lists 11,216, ranked by runs. data-box counted 65,004 through `GET /v2/store` on 2026-09-23. SuperBrowser's figure was "~11k+".

**Best for:** a named platform that has a maintained actor, when your own script, the box's free rung and the page APIs cannot get the records.

**Cost:** set by each actor: per result, per event, or per usage.
- Scrapebox quotes a run from the actor's own pricing. After the user's yes, Apify enforces the approved amount as the run's `maxTotalChargeUsd`.
- **Google Maps** (`compass/crawler-google-places`): $0.004 a place, plus paid add-ons that the quote lists apart (read 2026-10-19). For Maps lookups by name and address, `places` on the box is free: try it first.
- **The account:** the Free plan, $5 a month; $4.95 left on 2026-10-19.
- **Why runs are piloted:** an actor once spent $165 and returned nothing. That is SuperBrowser's record, repeated in `docs/tools.md`.

**Scale:** runs queue on the account's plan. 100 to 10,000 items a run through `maxItems` and paging the dataset (SuperBrowser's figure, *unverified, 2026-10-20*).

**Auth / anti-bot:** the actor deals with the target's anti-bot measures and logins. `APIFY_TOKEN` lives on the box. `find` and `get` are free.

**When to pick it:** last, when your own code and rungs 0 to 4 cannot get the records and an actor exists.
1. `actor find` to find one, then `actor get` to read its input fields and its quote.
2. `actor run` without `approve` for the quote. Show it to the user and wait for their yes.
3. A pilot of about 10 items, then the full run inside the approved cap.

**Gotchas:**
- Actor quality varies widely. Pilot before you scale, and never run an unknown actor big.
- Some actors get banned by their platform and spend money for nothing.
- Monthly-rental actors are refused by Scrapebox.

**Env:** `APIFY_TOKEN`, on the box. SuperBrowser's `APIFY_MAX_CHARGE_USD` and `APIFY_PILOT_ITEMS` are not Scrapebox's: the cap is the `max_cost_usd` the user approved.

---

## SuperBrowser's routing tiebreak: superseded

SuperBrowser picked, in this order:
1. Apify, for a named platform with an actor;
2. Bright Data datasets, for LinkedIn, Facebook and Google Maps in bulk;
3. Firecrawl, for a public directory at volume;
4. a browser, for interactive or logged-in pages.

That is the paid-first order Scrapebox replaces. Scrapebox's order, for "go get data from a site or platform":
1. **Your own script,** on the machine you are on, free (SKILL.md, "Your own code first").
2. **The rows it could not get,** through the box's free tools: `scrape` or `crawl` on rung 0, `places` for Google Maps, a `scraper` recipe for a directory.
3. **The paid rungs, quoted first:** Decodo's proxies (rung 1), the page APIs (rung 2: Decodo, Firecrawl, Bright Data), Scrapebox's agent (rung 4).
4. **An Apify actor** (rung 5), piloted small.

Kept from SuperBrowser: pilot before scale, respect the cap, and use the cheapest option that gets the job done. Before any bulk ask, ask how many.
