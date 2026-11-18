# Podcast

Getting Justin interviewed on other people's shows whose audience is business owners. The research job finds shows, checks recent episodes and guests, finds the booking route and drafts a pitch; the follow-up job checks each draft against the suppression list and queues it for Justin. A pitch never accepts a show's fee or a paid slot. A booking counts only as a time on Justin's calendar.

Message types in `guardrails.json`: podcast_pitch.

## Rules for every lane

- Every lane ends in the call link in `context/owner.md`. What is sold, and the words for it, are in `repo/OFFER.md`.
- Draft unless the message type is `auto` in `guardrails.json` and `send_guard.py` says so. Old copy from past campaigns is history, not approved text.
- First names only. Clients are described, never named. No invented results, numbers or client wins.
- Check the suppression list before every draft. Anyone who says no is done in every lane. One lane per person.
- Every reply goes to the `replies` profile with a dated next step.
