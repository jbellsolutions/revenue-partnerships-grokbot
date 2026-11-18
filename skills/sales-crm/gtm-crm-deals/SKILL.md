---
name: gtm-crm-deals
description: "Keep the deal ledger on the AI Guy GTM box: what counts as a deal, how one is recorded, and who it came from. Use for partner deals, reactivation deals and anything about what's owed."
---

# Deals

Ported from an earlier deal-officer agent. The ledger is `deal_ledger.py`, and the Deal sync job keeps it up to date from GoHighLevel. It only reads GoHighLevel. Its history is append-only, so nobody can argue with it.

## What counts

- A partner who says they're interested, or have deals coming, is a **Potential Deal**. That isn't a deal.
- It's a **Deal** when they bring a specific, named client.
- Attribution is evidence, not a verdict.

## How a deal gets in

- The tag `gtm:deal` on the partner's contact opens a Potential Deal.
- A note a person writes on that contact, starting `DEAL:` then the client's name, makes it a Deal. GoHighLevel can't search notes across contacts, so the tag has to be there too.
- A note from an agent names nothing.

## Stages

Potential Deal, Named, Call booked, Said yes, Agreement sent, Won, Stalled, Dead, Not a Deal. Sales moves them. Every change leaves a line in the history with its reason.

## Money

- Amounts come only from the card's value in GoHighLevel. Change no amount by hand.
- Referral terms are set: `channels/referrals/CONTEXT.md`, 2026-11-06. Reactivation's commission is still open. The ledger doesn't work out what's owed, so `Owed` stays blank and Justin reads it from the terms.
- Outreach still never names a payout, a price or a share.

## Daily

Read `Sweeps/deals.md`. Every open deal gets a next step. A deal quiet for 7 days goes on Justin's list.
