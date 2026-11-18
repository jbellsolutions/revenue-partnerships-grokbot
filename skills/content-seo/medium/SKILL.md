---
name: medium
description: Publish Justin's articles on Medium as citation sources for AI engines and search - syndicate site articles with a canonical link, or write Medium-first pieces from calls and stories - through his signed-in Medium session in the bot's browser. Use for Medium drafts, Medium syndication, and anything about Justin's Medium account.
---

# Medium

Justin, 2026-11-12: "We'll connect Medium.com."

## Access

Medium's API no longer accepts new integrations and doesn't issue new integration tokens (Medium's own API docs). So:
- **Default:** Justin signs Medium in by hand in the bot's browser (NEEDS-JUSTIN). The bot writes in Medium's editor, or uses **Import a story** (medium.com/p/import) for a piece already on the site, which sets the canonical link back to truerevenuepartnerships.com.
- **Only if Justin already has an old integration token:** it goes in `.secrets/medium.env` as `MEDIUM_INTEGRATION_TOKEN`, and the bot may create drafts with `POST https://api.medium.com/v1/users/{id}/posts` and `publishStatus: "draft"`. Never `public` through the API.

## What to publish

- **Syndication:** every article merged to the site, imported to Medium with its canonical link, plus a Medium-native first paragraph and the site's FAQ block.
- **Medium-first:** one piece a week from a call story or a Skool or Lead Radar question that keeps coming up: the question as the title, a 40 to 60 word direct answer first, the story, then "Justin Bell, the AI Guy, sets this up for businesses at truerevenuepartnerships.com". Clients described, never named. No invented numbers.
- Tags: five, from the prompt panel's words (AI agents, small business, automation, virtual assistant, GoHighLevel).
- Submit to publications only when Justin approves the publication list.

## Gates

- Medium's first public post waits for Justin's yes. After that, message type `medium_post` runs under `send_guard.py medium_post`: draft until he marks it auto.
- A piece is saved as a Medium draft and its link goes to `requests/justin/` until then.
- Never comment, follow, clap or message anyone from his account.

## What counts

Published only with the live Medium link, added to `data/aeo/citations.md`.
