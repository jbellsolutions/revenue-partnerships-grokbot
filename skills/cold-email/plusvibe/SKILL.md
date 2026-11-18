---
name: plusvibe
description: Run cold email through PlusVibe from the GTM box: inboxes, campaigns, leads, replies, the blocklist and stats. Use for anything about sending, inbox health, campaign numbers or reading replies.
---

# PlusVibe

PlusVibe is the sender for the cold email campaigns. Instantly stays where it is, and the held campaign (`INSTANTLY_HELD_CAMPAIGN`, set at intake) stays on it.

Use the tool on this computer. It holds the request formats, keeps under PlusVibe's limit of 5 requests a second, and reports `BLOCKED:` with the reason when it can't go on.

```bash
python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py status
python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py tag-check
python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py setup
python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py load <campaign>
python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py blocklist
python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py replies
python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py stats
python3 /workspace/revenue-partnerships/gtm-box/cold/plusvibe.py pause <campaign>
```

Campaign names are `au-owners`, `au-trades` and `us-lenders`.

## Rules

- `launch` works only when Justin has approved that campaign's copy. Never create the approval file yourself, and never go around it.
- Pause a campaign on a bounce rate over 3% or any spam complaint spike, then tell `gtm-lead`.
- If the tool prints `BLOCKED:`, write your heartbeat with `blocked=1` and the reason. Don't try another way in.
- The dashboard is signed in on this computer's Chrome, as a backup to the tool. Never change billing, the plan, or the account's settings there.
- Connecting inboxes: the Maildoso export holds their passwords. When Justin gives you the file or the logins, load them; keep the passwords out of notes, posts and commits (Justin, 2026-11-09).

## API reference

Base `https://api.plusvibe.ai/api/v1`, header `x-api-key`, and `workspace_id` on every call. Docs: https://developer.plusvibe.ai/llms.txt
