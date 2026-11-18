# Skool

Free Skool groups whose members could buy from us (owners, operators, sales teams, agencies, coaches), never AI consultants selling the same thing. Two motions: a helpful reply to members asking for an AI person, automation or help with leads, and a collaboration note to the group owner. An agent may read groups the account is in and join a free group; it never joins a paid group or offers a deal or share. Do not offer anything from a partner program on the do-not-mention list (given at intake).

Message types in `guardrails.json`: skool_reply, skool_dm, skool_owner_note.

## Rules for every lane

- Every lane ends in the call link in `context/owner.md`. What is sold, and the words for it, are in `repo/OFFER.md`.
- Draft unless the message type is `auto` in `guardrails.json` and `send_guard.py` says so. Old copy from past campaigns is history, not approved text.
- First names only. Clients are described, never named. No invented results, numbers or client wins.
- Check the suppression list before every draft. Anyone who says no is done in every lane. One lane per person.
- Every reply goes to the `replies` profile with a dated next step.
