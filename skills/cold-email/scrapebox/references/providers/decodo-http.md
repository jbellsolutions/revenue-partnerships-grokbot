# Decodo: two products, two rungs

*Copied from SuperBrowser's `providers/decodo-http.md` (commit 108816c) on 2026-10-20, and checked against Scrapebox's `config.py`, `docs/sources/decodo.md` and `docs/PLAN.md`.*

Decodo (decodo.com) sells two separate things, and Scrapebox uses both. They have different credentials and answer different questions: don't mix them up.

## Lane A: the residential proxy gateway (rung 1)

**In Scrapebox:** rung 1, the first paid rung. It is rung 0's own Chrome-TLS fetch (curl_cffi), sent through `gate.decodo.com`. SuperBrowser kept it as a separate raw-HTTP lane, outside its browser fallbacks.

**What it does:** routes a request through Decodo's residential IPs.
- Every hop's address is resolved and checked by Scrapebox before the proxy connects, because DNS resolves at the proxy.
- No JavaScript rendering, but the Chrome-TLS fingerprint under it is rung 0's.

**Ports:**
- `gate.decodo.com:7000` rotates: a new IP per request.
- `10001` and up are sticky: one IP per port, for the session length set in Decodo's dashboard (10 minutes on this account). This account uses 10001–10010, and Scrapebox keeps each host on one port, so a site sees one visitor.

**Best for:** pages that refuse a datacenter address but open to a residential one.
- **Measured from the box (2026-10-20):** rung 1 read 6 of the 20 benchmark directory pages (Indeed, Clutch, Manta, Upwork, Product Hunt, NerdWallet).
- Your own script on a home address does the same job for free.

**Cost:** bytes brought back, plus 24 kB a hop for headers and TLS, at $4 a GB (`SCRAPEBOX_DECODO_PROXY_USD_PER_GB`, an estimate still to confirm).
- At that rate a heavy page (Clutch, 183 kB) costs $0.005 to $0.008, more than Decodo's API at $0.001.
- The plan has 3 GB, valid until 2026-11-12 (read 2026-10-19 through Decodo's account API).
- SuperBrowser's "$0.01–$0.10 a fetch" is out of date.

**Env:** `DECODO_PROXY_USER` and `DECODO_PROXY_PASSWORD` (plus `DECODO_PROXY_HOST` and `DECODO_PROXY_PORTS`), on the box. The credentials go to curl as the proxy's login, never into a URL. SuperBrowser's single `DECODO_PROXY=http://USER:PASS@…` variable is not used here.

**Gotchas:** no rendering, so a page built by JavaScript comes back empty. That one goes to rung 2.

## Lane B: the Web Data API (rung 2)

**Out of date in SuperBrowser.** SuperBrowser called Decodo's Web Scraping API through the `decodo` CLI, with a basic-auth `DECODO_AUTH_TOKEN`. Decodo replaced that API with the **Web Data API**, and the legacy token does not work on it.

**In Scrapebox:** rung 2, first in rung 2's order (Justin, 2026-10-19: Decodo and Firecrawl are the first go-to).

**What it does:** one Bearer key (`DECODO_DATA_API_KEY`) opens `https://data.decodo.com/v1` `/scrape`, `/search`, `/map` and `/crawl`.
- Scrapebox calls `POST /scrape` with `{"url", "proxy_pool", "headless"?}`. The answer is `results[0].content`, its `status_code` and headers. A real-time request is held open for up to 150 s.
- It always sends `proxy_pool`: premium by default (anti-bot), or standard at half the price (`SCRAPEBOX_DECODO_POOL`). JavaScript rendering (`headless: "html"`) is off unless `SCRAPEBOX_DECODO_JS` is set.
- **Not wired yet:** `/search`, `/map`, `/crawl`, and the target templates with parsers (Amazon, Walmart, Google, Reddit, TikTok, YouTube and others; the list is mirrored in `docs/sources/vendor-docs/decodo/`). SuperBrowser listed those targets as a strength; they are on the Web Data API too, but no Scrapebox tool reaches them yet.

**Cost**, per 1,000 successful requests on the Free and $19 plans (list): $1.00 premium, $0.50 standard, $1.50 and $0.75 with JavaScript; `/search` $0.75.
- **What is billed:** a result, whatever the target's own status, and an error when the response is not empty. Only 429, 500, 524 and 613 are never billed.
- **Measured from the box (2026-10-20):** it read 5 benchmark pages (Yellow Pages, Angi, Houzz, Thumbtack, HomeAdvisor) at about $0.001 each.
- **Empty answers:** it answered with no content on G2, Glassdoor and Crunchbase. The ladder moved on to Firecrawl, but each empty answer is charged in full until it is known to be free.
- SuperBrowser's "free tier, 2K requests, no card" is *unverified, 2026-10-20*.

**Env:** `DECODO_DATA_API_KEY`, on the box. A third key, `DECODO_API_KEY`, reads the proxy plan's traffic (free) for `status`. It is not a scraping key.

**Gotchas:**
- Whether the `@decodo/cli` that SuperBrowser used speaks the Web Data API is *unverified, 2026-10-20*, and so are its exit codes (3 auth, 5 rate limited, 6 and 7 timeout or network). Scrapebox calls the HTTP API directly.
- Never print a key or the proxy password.
