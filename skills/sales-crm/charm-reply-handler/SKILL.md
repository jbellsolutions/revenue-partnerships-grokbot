---
name: charm-reply-handler
description: >
  Handles replies to Charm Offensive outreach and moves them toward a booked call and a proposal —
  drafting the right response for positive, "not right now", and negative replies, plus a discovery-call
  playbook. Use when the user says "I got a positive reply, now what", "someone replied to my cold
  email/DM", "how do I respond to this reply", "book the call", "they said tell me more", "they said
  not right now", "prep me for the discovery call", or pastes/forwards a prospect's reply.
metadata:
  version: "0.1.0"
---

# Charm Offensive — Reply Handler

## Course material (load first)

The approach is adapted from Jon Buchan's Charm Offensive. Its template and playbook files are licensed course material, so they are not in this pack. Load them from `$COURSE_MATERIAL_DIR/charm/` or, failing that, `.secrets/course/charm/` (given at intake): `charm-offensive-foundation/` holds the voice, story and profile files, and each charm skill's own files sit in a folder named after it. If a file is missing, write from the principles on this page and say in your output that the templates weren't given.

Turn replies into booked calls without losing the charm. Read the reply, classify it, respond in the
right way, then help the user run a great discovery call that sets up a winning proposal.

## Step 0 — Load voice and profile (always)

1. Read `charm-offensive-foundation/voice-and-humour.md` from the course folder.
2. Get the user's `charm-profile.md` (offer, booking link, sign-off, proof points). Ask for it or
   build a quick one via `charm-offensive-foundation`.
3. Read `charm-reply-handler/playbook.md` from the course folder for the exact response templates and the on-call question bank.

## Step 1 — Classify the reply

Read the prospect's actual message and sort it:

- **Positive** — they're interested / want to talk / said "yes" or "tell me more".
- **"Not right now"** — positive in tone but they can't act yet (busy, under contract).
- **Negative** — not interested. (Polite vs. rude matters — see below.)

If they asked specific questions, answer those directly and warmly *in addition to* the template.

## Step 2 — Respond in the right way (drafts in `charm-reply-handler/playbook.md` from the course folder)

- **Positive → book the call.** Thank them, propose a short (7–15 min) call, and offer a booking link
  as the easy option. If they asked "tell me more", send the brief bulleted intro (who you are, where
  based, how you help — with the light humour) *and* the booking link. Keep it short and human.
- **"Not right now" → keep the door open (3 ways).** (1) Ask to follow up in 3/6/9 months with
  something light and interesting — set a CRM/diary reminder. (2) Offer your newsletter/list if
  you have one (a light, no-pressure close). (3) Send a LinkedIn invite to stay
  connected.
- **Negative → be gracious.** If cold emailing, ensure they're unsubscribed from future sends. If
  they're rude, don't reply. If polite, a one-liner: "Apologies, {name}. I won't contact you again.
  Best of luck with everything. Have a great week, {your name}." Don't be discouraged — everyone gets
  these; if you *only* get negatives, revisit your data, copy, and offer.

Always draft in the user's voice; keep positive responses genuinely warm and specific to what they said.

## Step 3 — After the call is booked: prep + run it

Use the discovery-call playbook in `charm-reply-handler/playbook.md` from the course folder:

- **Before the call:** research their website, socials, news, LinkedIn; note enough to avoid silly
  mistakes and find common ground. Offer/accept an NDA for bigger clients so you can ask more.
- **On the call:** keep *them* talking (goal: gather what you need); get permission before recording;
  take notes. Get them to introduce themselves, ask about goals/ambitions and past activity, then
  softly pitch (a thinking-aloud suggestion, not a pitch), land a small "yes" (a free mini-audit
  or "some ideas"), surface budgets/decision-makers/KPIs, and **propose sending a proposal** with a
  deadline and a booked follow-up call.
- **After the call:** send a prompt follow-up email summarising their goals/challenges, how you can
  help (link case studies), what'll be in the proposal, and when — then move the deal to "Qualified"
  in the CRM if connected.

## Step 4 — Hand off to the proposal

When the call yields a green light, hand off to `charm-proposal` to build the proposal, passing along
the goals, challenges, KPIs, budget signals, and decision-makers you gathered.

## Course files (loaded from the course folder)

- `charm-reply-handler/playbook.md` from the course folder — response templates (positive / tell-me-more / not-now / negative), the
  discovery-call question bank, and the post-call follow-up outline.
