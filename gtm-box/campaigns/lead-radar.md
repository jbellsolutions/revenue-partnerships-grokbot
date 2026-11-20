# Lead Radar

Public posts and comments from people asking for help with AI, automation or a virtual assistant, and job posts from businesses hiring a virtual assistant or an AI role (`repo/fractional/settings/lead-radar.json`). The radar finds and scores them; a high-intent asker gets a helpful public reply, and at most one direct message after it. The radar's own sender and caps apply.

Message types in `guardrails.json`: radar_public_reply, radar_skool_dm.

## Rules for every lane

- Every lane ends in the call link in `context/owner.md`. What is sold, and the words for it, are in `repo/OFFER.md`.
- Draft unless the message type is `auto` in `guardrails.json` and `send_guard.py` says so. Old copy from past campaigns is history, not approved text.
- First names only. Clients are described, never named. No invented results, numbers or client wins.
- Check the suppression list before every draft. Anyone who says no is done in every lane. One lane per person.
- Every reply goes to the `replies` profile with a dated next step.
