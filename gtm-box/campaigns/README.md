# Campaign pages

These pages tell the CRM agents (`closer`, `deals`, `opener`, `replies`) what each lane is: the offer, the audience and how a reply is handled. Before drafting for a lead, read the page for that lead's lane. A campaign can have its own page: `crm_cards.py` looks it up in the private campaign map (`campaign-pages.json` in this folder, given at intake), and falls back to the lane page, then to this one.

This is also the cold-email lane's page: cold campaigns run in the sending tools under the cold-email role, with copy checked by `cold-copy/check.py` and approved by Justin before anything sends.

## Rules for every lane

- Every lane ends in the call link in `context/owner.md`. What is sold, and the words for it, are in `repo/OFFER.md`.
- Draft unless the message type is `auto` in `guardrails.json` and `send_guard.py` says so. Old copy from past campaigns is history, not approved text.
- First names only. Clients are described, never named. No invented results, numbers or client wins.
- Check the suppression list before every draft. Anyone who says no is done in every lane. One lane per person.
- Every reply goes to the `replies` profile with a dated next step.
