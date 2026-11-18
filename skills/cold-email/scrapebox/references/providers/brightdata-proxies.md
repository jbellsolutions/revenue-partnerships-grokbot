# Bright Data: proxies

*Copied from SuperBrowser's `providers/brightdata-proxies.md` (commit 108816c) on 2026-10-20, and checked against Scrapebox's `config.py`, `docs/sources/brightdata.md` and `docs/sources/decodo.md`.*

**In Scrapebox: not wired (2026-10-20).** Rung 1 is Decodo's residential proxies ([decodo-http.md](decodo-http.md)). Bright Data's proxy login (`BRIGHTDATA_PROXY_USER`, `BRIGHTDATA_PROXY_PASSWORD`) has never been supplied. SuperBrowser put these proxies in tier 3.

**What it does:** Bright Data's residential and datacenter proxy network: rotating IPs under a scraper or a browser, so that volume doesn't get throttled or blocked. It is a layer, not a scraper.
- **The endpoint:** `brd.superproxy.io:44445`, with the zone, country and session in the username (data-box's note). The old ports 22225 and 33335 are refused, because their certificates expired on 2026-09-25.

**Best for:** high-volume crawls where one IP would be throttled, and geo-targeting. SuperBrowser treated it as interchangeable with Decodo's proxies, to be picked on price and coverage.

**Cost:** per GB of traffic. No Scrapebox price exists, because nothing calls it.

**Gotchas:**
- Not needed under the Web Unlocker, which already rotates residential IPs.
- Billed by bandwidth: heavy pages cost more.

---

## Proxy tiers: datacenter or residential (the cost lever)

Kept from SuperBrowser, because the rule still holds.

Proxy networks sell at least two kinds of IP, and the price gap is large: datacenter IPs cost much less per GB than residential ones. Residential IPs come from real consumer ISPs, so they get past hardened anti-bot and geo checks. Datacenter IPs are cheap and fast, and fine for any site that was never going to block you. (SuperBrowser's reference point, Browserless pricing datacenter at 2 units a MB against 6 for residential, is *unverified, 2026-10-20*.)

**Escalate on evidence, not on fear:**
1. **No proxy** (free): most public pages. From a home address, this is your own script.
2. **Datacenter proxy** (cheap): volume crawls of ordinary sites.
3. **Residential proxy** (dearer): the site blocks datacenter ranges, or you need a consumer location.
4. **Unlocker, full anti-bot** (dearest): hardened Cloudflare or DataDome. It bundles residential rotation, so don't stack a proxy under it.

Paying residential rates for a site that would accept a datacenter IP is waste. So is spending a long crawl on datacenter IPs against a site that blocks them. Pilot a few pages on each tier.

**What Scrapebox has today (2026-10-20):**
- Rung 1 has one tier: Decodo's residential proxies, sticky per host on `DECODO_PROXY_PORTS` (10001–10010 on this account) or rotating on port 7000. There is no datacenter tier.
- A rung 1 read is priced at $4 a GB, an estimate.
- The box itself is a datacenter address: rung 0 reads far fewer benchmark directory pages from it than from a home address. A script on a home address is the cheapest residential IP there is.
- SuperBrowser's note that it had no datacenter zone and no tier parameter described SuperBrowser's code (`src/super_browser/proxy.py`). It does not apply here.
