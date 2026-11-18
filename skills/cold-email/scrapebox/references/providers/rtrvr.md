# Rtrvr.ai

*Copied from SuperBrowser's `providers/rtrvr.md` (commit 108816c) on 2026-10-20, and checked against Scrapebox's `config.py`, `docs/sources/rtrvr.md` and `docs/PLAN.md`.*

**In Scrapebox: never called (2026-10-20).** It is named for rung 3 (`/scrape`, not built) and as a fallback agent on rung 4 (`/agent`, M5), and the box's ledger shows $0 spent there. Whether to keep the subscription until M5 needs `/agent` is an open question for Justin. SuperBrowser had it as documentation only.

## What it is

- **A Chrome extension** that drives the user's own signed-in Chrome. Its strength is identity: a real fingerprint, real cookies and a real session, the things headless and cloud browsers fake.
- **An API,** `https://api.rtrvr.ai`, with `Authorization: Bearer $RTRVR_API_KEY`:
  - `POST /scrape`: a page's content and its accessibility tree, from Rtrvr's cloud browsers;
  - `POST /agent`: a cloud browser agent that runs a goal. It can run many agents at once, and replay a flow recorded in the extension;
  - `/mcp`: drives the signed-in Chrome the extension runs in, or the cloud tools. The calling agent (Claude Code, Hermes) connects to it directly.
- **A CLI,** `rtrvr` (SuperBrowser's note: v0.2.1 and later, for scripts, schedules and triggers; *unverified, 2026-10-20*).

## Where it fits

- Logged-in pages in the user's real session: social platforms, admin pages, SaaS behind single sign-on. In Scrapebox's plan this is how posts on logged-in platforms are reached (M8), through its MCP from the calling agent.
- Sites that fail headless or cloud fingerprints: a real Chrome passes basic checks.
- A CAPTCHA or login step that a person can do by hand in the visible window.

## Where it does not fit

- Bulk or parallel crawling: use your own script, or the box's `crawl`.
- An unattended server: there is no Chrome window on a VPS.

## Out of date in SuperBrowser

- **"No API key required":** that holds only for the extension and its local MCP. The API needs `RTRVR_API_KEY`, and API and MCP agent runs, schedules and triggers need a paid plan. Its unit is credits.
- **The key:** the old key was exposed in Hermes backups. A new key was put in place on 2026-10-19.
- **"Free, bring your own Gemini key"**, the MCP being installed on the Mac and exposed to Hermes, and the June 2026 anti-detection results: all *unverified, 2026-10-20*.
