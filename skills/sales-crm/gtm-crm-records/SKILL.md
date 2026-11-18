---
name: gtm-crm-records
description: "How every CRM profile on the AI Guy GTM box reads and writes GoHighLevel: the one writer, the stage map, the tags, and what's off limits. Load before touching any contact, card, tag, note or task."
---

# CRM records

Ported from the CRM Agent's `crm-agent-ghl-operations` and `LESSONS.md`. Where those differ, this page and the agent charter win. No SMS here: A2P isn't approved. No `affiliate_*` tools. Nothing sends.

## One door

Everything goes through the scripts in `/workspace/revenue-partnerships/gtm-box/box/`. Don't call the GoHighLevel API yourself, and don't use another tool for it.

| Do | Command |
|---|---|
| Add a person | `crm.py add --lane <lane> --name ... --email ... --campaign ... --apply` |
| See the queue | `crm.py status` |
| The one-screen brief | `crm_cards.py brief <contact id>` |
| Move a stage | `crm_stage.py move <contact id> "<stage>" --type <evidence> --ref <id> --apply` |
| Today's real numbers | `crm_sweep.py --count` |

## The location

GoHighLevel sub-account Revenue Partners. `crm-map.json` holds the map. Ids are looked up by name each run. If a run says a stage or field is missing, stop and say so.

## The pipeline, as it really is

The API can't create stages, so we build to what's live. `Sales` has four stages.

| Our word | Where it lives |
|---|---|
| New lead | A contact tagged `gtm:new`, no card |
| Engaged | `Interested`, tag `gtm:replied` |
| Qualified | `Interested`, with the facts on the card |
| Booked | `Call booked` |
| Showed | `Call booked`, tag `gtm:showed` |
| Follow-up | `Call booked`, tag `gtm:showed`, with a dated next step |
| Said yes | `Said yes`, on a note Justin wrote |
| Agreement | `Agreement sent`, on a note Justin wrote |
| Won | Justin marks it. Nobody else |
| Lost | Card status lost, with the reason in a note |
| Nurture | Tag `gtm:later`, with a dated task |

`Client Onboarding` is read-only. Someone else owns it.

## Rules

- A stage moves only on evidence: a reply, a public ask, a booking, or a note a person wrote. A note saying someone seems interested moves nothing.
- We write only `gtm:` tags. Never `src:` or `onb:`. Those belong to the `ONB` workflows, and a tag can fire a workflow.
- Never mark a card won. Never touch a card in another pipeline.
- `ONB 0` puts Instantly-interested leads in `Sales`. Don't add a second card.
- Another writer is live on this CRM. Fill blanks. Never overwrite a name or a field that has a value.
- A record marked held gets no message, no note and no task. Tell Justin.

## Live data traps

- A contact's name can be their email address. That isn't a name. Show `contact <last 6 of id>`.
- `TYPE_NO_SHOW` on a thread means the thread is empty. It doesn't mean someone missed a call.
- GoHighLevel's inbound email body can be our own email. The scripts read the message by id. Don't read the thread by hand.
- Five `(example)` contacts ship with the account. They aren't people.
- Tags come back lowercase.
