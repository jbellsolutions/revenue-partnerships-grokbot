# Templates

One file per message type. `reply_book_call.txt` and `no_show_rebook.txt` are words Justin approved. The three `fractional_*` files are the core email, from Justin's words of 2026-11-20 (`fractional/MESSAGES.md`). The other six were rewritten on 2026-11-18 for the offer in `OFFER.md`. All nine are drafts until he approves them (`guardrails.json` says which). Once approved, a file is the copy of record: a new wording needs his yes again.

| File | Type | Used by | Blanks |
|---|---|---|---|
| `reply_book_call.txt` | `reply_book_call` | `replies` | `{{first_name}}`, `{{booking_link}}` |
| `booking_confirmation.txt` | `booking_confirmation` | `closer` | `{{first_name}}`, `{{call_time}}`, `{{reschedule_link}}` |
| `podcast_pitch.txt` | `podcast_pitch` | `podcast` | `{{hosts}}`, `{{opening}}`, `{{angles}}` |
| `collab_outreach.txt` | `collab_outreach` | `rev-partner` | `{{first_name}}`, `{{opening}}` |
| `linkedin_first_degree.txt` | `linkedin_first_degree` | `linkedin` | `{{first_name}}` |
| `crm_follow_up.txt` | `crm_follow_up` | `closer` | `{{first_name}}`, `{{booking_link}}` |
| `no_show_rebook.txt` | `no_show_rebook` | `closer` | `{{first_name}}`, `{{booking_link}}` |
| `fractional_first_touch.txt` | `cold_first_touch`, `dream500_first_touch` | `dream`, `cold-email` | `{{first_name}}`, `{{first_line}}` |
| `fractional_follow_up.txt` | `cold_follow_up`, `dream_follow_up` | `dream`, `cold-email` | `{{first_name}}` |
| `fractional_dm.txt` | `fractional_dm` | `dream` | `{{first_name}}`, `{{first_line}}` |
| `partner_outreach.txt` | `partner_outreach` | `deals`, `warm` | `{{first_name}}`, `{{booking_link}}` |

Which types are approved, and which are on auto, lives in `guardrails.json` (`copy_approved`, `mode`, `authorized`); the record of each approval is kept privately. In a podcast pitch, the opening and the angles change for each show and must stay true of it; everything else is fixed.

**Approved means the words, not the sending.** A type stays a draft in Justin's queue, or a row he ticks in the guarded sender, until its mode is `auto`. `crm_opener` has no template here: the opener writes each one fresh from the person's card. The collaboration note's `{{opening}}` is one true line about that creator's recent work, and `collab_send.py` sends only a note that matches the template word for word, with a first name and that line filled in.

## Using one

Don't retype a template. This fills the blanks and checks the person the same way every draft is checked:

```bash
python3 /workspace/revenue-partnerships/gtm-box/box/crm_cards.py draft <contact id> --template reply_book_call --apply
python3 /workspace/revenue-partnerships/gtm-box/box/crm_cards.py draft <contact id> --template booking_confirmation --call-time "<from the booking>" --reschedule-link <from the booking> --apply
```

A person with no real first name on file isn't filled in. That one goes to Justin.

## The blanks

- `{{booking_link}}` is `<BOOKING_LINK>`, in `crm-map.json`. Set it at intake.
- `{{reschedule_link}}` and `{{call_time}}` come from each Cal.com booking.

## The subject

These files hold the bodies. The sender needs a subject too, or a `ghl` row messages nobody, so `crm-map.json` holds one for each type. Each one shows on the row he ticks.
