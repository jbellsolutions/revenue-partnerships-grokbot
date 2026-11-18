---
name: gtm-crm-sweep
description: "Work the open-loop list on the AI Guy GTM box: read Sweeps/latest.md, worst first, and leave every record with an owner, evidence, a next action and a date. Use for the pipeline sweep, stuck records, and who needs follow-up."
---

# Pipeline sweep

Ported from the CRM Agent's `crm-agent-sales-follow-up` and an earlier pipeline agent's pipeline sweep. `NO-OPEN-LOOPS.md` is the policy.

The Open loops job builds `Sweeps/latest.md` ten minutes before you run. There are no canned messages here: each one is written for that person from what's on file.

## Worst first

| Bucket | Do |
|---|---|
| **held** | Nothing. Put it in Justin's queue with the reason. Write nothing to the record |
| **waiting on us** | `replies` answers it. If it's been a business day, say so to Justin |
| **overdue** | Read the task. Done? Close it and say why. Yours? Do it now. A person's? Leave it and put it on today's list |
| **no owner** | The job sets the named owner. If it couldn't, tell Justin |
| **no evidence** | Find the evidence for the stage, or tell Justin the card shouldn't be there |
| **no next step** | Set one dated next step |
| **gone quiet** | One personal follow-up on what they last said, if the list says it's allowed, then set the next check |
| **not started** | `opener` has it |
| **on track** | Nothing, unless a new note needs reading |

## Clocks

| Stage | When | Next step |
|---|---|---|
| Interested | They wrote last | Answer the same business day |
| Interested | 5 business days of silence | A personal follow-up on what they last said |
| Later | Their date arrives | Check in on that date, never before |
| Wants a call, no time | 1 business day | Offer the booking link |
| Call booked | The day before | The brief to Justin |
| Call booked | 24 hours after, no notes | Ask Justin what happened |
| Said yes | 2 business days, no movement | Ask Justin what's needed |

## Limits

At most 15 follow-ups a sweep, worst first. Never follow up a record marked held, a takeover, or anyone with `gtm:needs-justin`. Never close a task to make a number look better. Every follow-up is a draft in Justin's queue. Follow-ups aren't on the guarded sender's route yet.

## Confirming a call

`crm_cards.py draft <contact id> --template booking_confirmation --call-time "<from the booking>" --reschedule-link <from the booking> --apply`. Those are Justin's approved words, in `/workspace/revenue-partnerships/gtm-box/templates/booking_confirmation.txt`. Never retype or change them.

## End of the run

Write your heartbeat with `found=N drafted=N overdue=N`, and one line per record you touched in your daily note. If the list is empty, say so.
