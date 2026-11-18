# Bright Data: datasets and ready-made scrapers

*Copied from SuperBrowser's `providers/brightdata-dataset.md` (commit 108816c) on 2026-10-20, and checked against Scrapebox's `config.py`, `docs/sources/brightdata.md` and `docs/charters/rung3-brightdata-bench.md`.*

**In Scrapebox: not wired (2026-10-20).** Justin added Bright Data's ready-made scrapers on 2026-10-19, and the work is part 3 of the rung 3 and Bright Data charter. No Scrapebox tool calls them yet, so nothing here can run today. SuperBrowser put them in tier 6 and called them through its engine.

**What it does:** filter-search or URL-scrape Bright Data's pre-indexed platform datasets (LinkedIn people, companies, jobs and posts; Facebook; Google Maps reviews) and return structured records.
- **How many datasets:** 1,762, counted through `GET /datasets/list` by data-box on 2026-09-23.
- **The calls:** `POST /datasets/v3/trigger` starts a collection, and `GET /datasets/v3/snapshot/{id}` reads it. Marketplace datasets are previewed by default; a purchase needs `confirm_purchase: true` and a cap.

**Best for:** bulk structured records from a big platform, where the data is already indexed.
- For Google Maps by name and address, `places` on the box is free on rung 0. Try it first.

**Cost:** per record, from Bright Data's list price for each dataset. SuperBrowser's "~$0.05 a record batch" is *unverified, 2026-10-20*. When it is wired, a run is quoted as `max_items` × the price and runs only after the user's yes.

**Scale:** SuperBrowser says a filter search returns about 10 records a request, so bulk means many looped requests (*unverified, 2026-10-20*).

**Auth / anti-bot:** Bright Data's side; no login to the target.

**When to pick it:** once it is wired, for a supported platform when your own code and the box's free tools cannot get the records. Not for an ordinary directory site: those go up the page ladder.

**Env:** `BRIGHTDATA_API_KEY`, on the box.
