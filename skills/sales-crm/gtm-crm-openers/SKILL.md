---
name: gtm-crm-openers
description: "Start conversations on the AI Guy GTM box: build the card, write one first message from what's on it, and plan paced reactivation waves. Use for openers, first touches and waking up cold contacts."
---

# Openers and reactivation

Ported from the CRM Agent's `crm-agent-contact-cards`, `crm-agent-custom-messaging` and `crm-agent-reactivation`, and from an earlier pipeline agent's `queue_all.py`. Email and LinkedIn only: no texts, because A2P isn't approved. Everything is a draft. Justin approved `crm_opener` on 2026-11-08, so an opener that passes the check becomes a row he ticks in the guarded sender. If the sender can't take it, it's a file in his queue. Either way, it isn't a send.

## The order. Always this order.

1. **The card.** Card build makes one note per person in the vault's `people/` folder. No card, no message. Cards hold no address and no phone number.
2. **The brief.** `crm_cards.py brief <contact id>` says who they are, the last thing said, and the page to read.
3. **The page.** Read the campaign page it names, in `/workspace/revenue-partnerships/gtm-box/campaigns/`. If that page says nothing is approved, you may still draft, and it goes to Justin.
4. **The message.** One person, from what's on file.
5. **The check.** `crm_cards.py draft <contact id> --file F --apply` checks it and puts it in Justin's queue.

## A good message

1. One true detail from their record: what they asked, where the last conversation stopped.
2. Written as Justin, first person.
3. Exactly one question.
4. Short: 120 words at most. Plain words, their first name, no pitch.
5. Never: a price, a date, a result, a promise, or an earlier conversation that didn't happen. Never guilt anyone for going quiet. No em or en dashes.
6. No link except the site.

If it could go to anyone, it isn't finished.

## Who you don't write to

Openers are for people no lane already reaches. `podcast`, `linkedin`, `cold-email`, `rev-partner` and `warm` write their own first touch, so the wave leaves their people out. That's the one-lane-per-person rule. Say a person looks wrong and hold them, rather than guess.

## Reactivation

Wake up cold contacts: old leads and stalled opportunities.

- **Leave out:** held records, anyone with an opt-out, anyone a person handles, anyone on a later date, and current clients.
- **Order:** most recent activity first.
- **Size:** a tester, then 10, then a wave of 25. The next wave waits until the last one's replies are answered and opt-outs stay under 3%.
- **Stop on reply.** Anyone who replies leaves the wave. From then on it's a conversation.
- Propose each wave to Justin. You don't start one.

The approved reconnect email is `warm`'s, word for word. Don't rewrite it here.
