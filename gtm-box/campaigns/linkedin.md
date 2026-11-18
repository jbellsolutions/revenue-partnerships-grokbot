# LinkedIn

Justin's first-degree connections, minus suppression, and the comment sections of high-engagement posts tracked on the LinkedIn dashboard. First-degree messages go through the LinkedIn tool only once the type is approved.

Message types in `guardrails.json`: linkedin_first_degree.

## Rules for every lane

- Every lane ends in the call link in `context/owner.md`. What is sold, and the words for it, are in `repo/OFFER.md`.
- Draft unless the message type is `auto` in `guardrails.json` and `send_guard.py` says so. Old copy from past campaigns is history, not approved text.
- First names only. Clients are described, never named. No invented results, numbers or client wins.
- Check the suppression list before every draft. Anyone who says no is done in every lane. One lane per person.
- Every reply goes to the `replies` profile with a dated next step.
