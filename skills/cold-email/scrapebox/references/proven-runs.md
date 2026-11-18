# Proven runs: what the measured runs taught

The measured runs themselves (row counts, hit rates, costs) are kept privately. What they showed:

- **A plain script is often enough.** A standard-library script that reads each business's own site (`tel:` links first, then page text, then JSON-LD, then a few contact and about pages), with a resumable state file and sharded threads, filled phone numbers on a large list for $0, with no proxy, paid API or browser.
- **Verify before calling a list done.** Unchecked scrapes carry junk redirects and wrong matches, so spot-check a sample against the source pages.
- **Where the free fetch runs matters.** A home address reads far more directory pages than a datacenter box, which gets fast 403s. Your own script on a home address is the cheapest reader; send only the rows it can't read to the box's proxies and page APIs.
- **Climb the ladder only for what's left.** Free fetch, then proxies, then page APIs, then an unlocker for the hardest sites, read most of a directory benchmark for cents.
- **Maps lookups are free and steady on rung 0** at the default spacing. A `none` answer means Maps holds no place under that name and address; a paid re-read returns the same, so look for the business another way.
- **Paid-first routers cost more.** A design that sends every job to paid services first spends money the free rungs would have saved.
