# Bright Data: Web Unlocker

*Copied from SuperBrowser's `providers/brightdata-unlocker.md` (commit 108816c) on 2026-10-20, and checked against Scrapebox's `config.py`, `docs/sources/brightdata.md` and `docs/PLAN.md`.*

**In Scrapebox:** rung 2, third in rung 2's order after Decodo's Web Data API and Firecrawl. SuperBrowser put it in tier 5 and made it its default crawl provider.

**What it does:** fetches a URL through Bright Data's unblocking network (rotating residential IPs, CAPTCHA solving, JavaScript rendering) and returns the page.
- Scrapebox calls `POST https://api.brightdata.com/request` with `{zone: BRIGHTDATA_UNLOCKER_ZONE, url, format: "raw"}`. Bright Data's own refusals come back in the `x-brd-error` and `x-luminati-error` headers.
- The unblocker zone name comes from `BRIGHTDATA_UNLOCKER_ZONE`, set at intake.

**Best for:** the hardest public pages: directories and listings behind Cloudflare, DataDome or aggressive rate limits, where the cheaper rungs are refused.
- **Measured from the box (2026-10-20):** it read Yelp after Decodo's API got a 403 and Firecrawl refused the site.
- **SuperBrowser's record:** 7 of its 10 completed engine runs went through the Unlocker (its `learnings.md`, 2026-06-20). Its "real anti-bot directory → 34 leads" is *unverified, 2026-10-20*.

**Cost:** $1.50 per 1,000 requests, $0.0015 each, at the list price (still a price to confirm). SuperBrowser's "~$0.02 a page" is out of date.
- The key has no billing scope (`GET /customer/balance` answers 403), so Bright Data's spend shows only in its dashboard. Scrapebox's ledger is the running record.

**Concurrency / scale:** Bright Data's network handles many unlocks at once (SuperBrowser's claim, *unverified, 2026-10-20*). The ladder fans out across a crawl's pages inside the cap.

**Auth / anti-bot:** strong anti-bot (rotating residential IPs and CAPTCHA solving). It is not a logged-in browser: deep logins and multi-step flows need rung 4.

**When to pick it:** you don't pick it by hand. The ladder reaches it, inside an approved plan, when the rungs below could not read the page.

**Gotchas:**
- Overkill, and dearer, for open pages that the free fetch or Firecrawl reads.
- It bundles its own residential rotation, so don't put a separate proxy under it.

**Env:** `BRIGHTDATA_API_KEY` and `BRIGHTDATA_UNLOCKER_ZONE`, on the box.
