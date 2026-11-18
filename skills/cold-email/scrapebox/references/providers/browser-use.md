# Browser Use: hosted browsers, and the open-source agent

*Copied from SuperBrowser's `providers/browser-use.md` (commit 108816c) on 2026-10-20, and checked against Scrapebox's `config.py`, `docs/sources/browser-use.md` and `HANDOFF.md`.*

**In Scrapebox:**
- Browser Use Cloud's browsers run Scrapebox's own agent (rung 4, live, 6 of 10 on its goals) and will run rung 3 (a plain browser read, not built yet).
- The open-source browser-use agent is the fallback for what Scrapebox's agent cannot finish (M5).
- No browser ever runs on the box (CHARTER, invariant 6). SuperBrowser put Browser Use in tier 1, as its anti-bot browser.

**What it does:** hosted Chromium browsers, driven over CDP.
- `POST /api/v4/browsers` starts one and returns a `cdpUrl` and a `liveUrl`.
- `PATCH /api/v4/browsers/{id}` with `{"action": "stop"}` stops it. Always stop it in a `finally`: closing the websocket does not, and a lost browser bills until its `timeout`.

**Best for:** pages that need clicks, typing or choices before the content shows. For a list job that is rare. A browser on every page is the dearest way to read a list: fix the script, or write a `scraper` recipe, first.

**Cost:** $0.02 per browser-hour, billed by the minute (a run under a minute is billed as one minute, $0.000333).
- The whole `timeout` is charged up front and refunded pro rata at stop, so keep it small.
- `proxyCountryCode` defaults to "us", a residential proxy billed per GB. Send null unless a proxy is wanted.
- The open-source agent's own model calls come on top. Measured in browser-box (2026-09-23): 2 steps, about 10 s and $0.0011 to read a heading; 3 steps, 31 s and $0.0056 for a Hacker News comment count.
- SuperBrowser's "$0.10–$1.00 a run" is out of date.

**Concurrency:** many browsers at once. The plan's `concurrentSessionLimit` is 10 at $0 spent and 50 after $100, shared with browser-box and DemandGen. That is the plan's ceiling, not a lock of Scrapebox's. SuperBrowser's "single-session default" does not apply.

**Auth / anti-bot:** SuperBrowser's claims of verified Cloudflare, DataDome, PerimeterX and CAPTCHA handling are *unverified, 2026-10-20*.
- The screen size is fixed when the browser starts (`browserScreenWidth`, `browserScreenHeight`). Resizing afterwards is refused, because it makes a browser easier to detect.

**Gotchas:**
- Never send a `profileId`: other tools keep signed-in profiles on the same account.
- A background tab reports itself hidden, and scrolls and visibility checks fail there. Activate the tab first.
- The cost climbs with retries and long runs.

**Env:** `BROWSER_USE_API_KEY`, on the box. Scrapebox's agent also needs `TYPESAFE_API_KEY` (Jev) and `OPENROUTER_API_KEY` (the text model).

SuperBrowser sent REST scrapes to Hyperbrowser and full CDP work to Steel. Neither is part of Scrapebox.
