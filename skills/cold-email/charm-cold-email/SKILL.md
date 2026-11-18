---
name: charm-cold-email
description: >
  Writes Charm Offensive cold emails, full multi-step cold email sequences, the "magic" sales-call
  booking email, and the direct-mail-letter → follow-up-email combo — all personalized with research
  on the prospect. Use when the user asks to "write a cold email", "cold outreach", "email sequence",
  "book a sales call", "send a direct mail letter", "warm up a prospect", "reach out to {company}",
  or wants their outbound email to sound like Charm Offensive / disarming and funny rather than salesy.
metadata:
  version: "0.1.0"
---

# Charm Offensive — Cold Email

## Course material (load first)

The approach is adapted from Jon Buchan's Charm Offensive. Its template and playbook files are licensed course material, so they are not in this pack. Load them from `$COURSE_MATERIAL_DIR/charm/` or, failing that, `.secrets/course/charm/` (given at intake): `charm-offensive-foundation/` holds the voice, story and profile files, and each charm skill's own files sit in a folder named after it. If a file is missing, write from the principles on this page and say in your output that the templates weren't given.

Write cold emails and sequences that get opened, read, and replied to by being disarmingly honest and
funny instead of salesy. Every draft is grounded in the Charm voice AND in real research on the
prospect.

## Step 0 — Load the voice and the user's profile (always)

Before writing anything:

1. Read `charm-offensive-foundation/voice-and-humour.md` from the course folder.
2. Find the user's profile: look for a provided `charm-profile.md` (ask the user to point to it or
   paste it). If none exists, invoke the `charm-offensive-foundation` skill to build a quick one, or
   ask 3 fast questions: who do you help + what problem do you solve; your funny job-title trio /
   favourite-weapon photo; your booking link.

Read the template library in `charm-cold-email/templates.md` from the course folder to adapt, never copy.

## Step 1 — Understand the target

Confirm with the user (in one short batch): the specific prospect(s) or the list/segment; the goal
(a 7-minute call, a mini-audit, a reply); channel (cold email, a sequence, or the direct-mail combo);
volume (one bespoke email vs. a scalable template with merge fields).

## Step 2 — Research the prospect (this is what makes it personal)

Do real research before drafting. Prefer, in order:

- The user's connected tools (CRM, enrichment, LinkedIn scrapers, Apollo, etc.). If lead-enrichment
  or scraping skills are installed (e.g. `enrichment-agent`, `apify-specialist`, `scrapercity-specialist`),
  use them to pull role, company, recent activity, tech stack.
- WebSearch / WebFetch for the company site, recent news, a recent post, a genuine hook.

Capture only **true, specific, usable** hooks: a real reason you're reaching out, a genuine
compliment, a recent event, a relevant stat (with source). Never invent. For a scalable template,
research the *segment* and use safe merge fields ({{first_name}}, {{company}}) plus one segment-level
insight rather than fake per-person detail.

## Step 3 — Draft in the Charm voice

Adapt (don't blindly copy) the templates in `charm-cold-email/templates.md` from the course folder. A single cold email follows
the "magic email" skeleton:

- **Honest, funny opener** (a Reverse-style line, or a genuine hook from research).
- **Get to the point:** one plain line on who you help and with what — plus a risk-reversal / no-brainer line if they
  have one.
- **Give them an out:** an easy out if it isn't a problem for them.
- **Low-pressure CTA:** a short, low-pressure call, framed as useful ideas they keep either way.
- **The signature photo:** note where the pet/absurd photo attaches.
- **Signature:** the three job titles, warm sign-off.

For a **sequence**, use the 8-step arc in `charm-cold-email/templates.md` from the course folder (intro → a P.S. follow-up
→ sad-photo nudge → helpful-stat angle → light check-in → 3 convenient CTAs → amusing image → polite
final "breakup"). Space steps a few days apart; escalate charm, never pressure.

For the **direct-mail combo**: write a typewriter-style letter first (no logo, bright envelope, wax
seal or handwritten address, optional silly enclosure), then an email a few days later that references
the letter in the subject line and is *different but in the same style*. Two memorable touches beat one.

## Step 4 — Personalize and self-check

Run the self-check in `voice-and-humour.md`. Specifically: opener is a genuine pattern interrupt;
one honest admission + one (not five) jokes; value framed as a gift; CTA has an easy out; short and
scannable; every fact true; subject line intriguing (not "Quick question"); sounds like the user.

## Step 5 — Deliver

Output ready-to-send drafts with: a subject line (and 1–2 alternates), the body, a note of where the
photo/attachment goes, and the signature. For a sequence, label each step and its send-day offset.
If the user wants it saved or sent, offer to create Gmail drafts or write to a file — but never send
without explicit approval.

## Compliance

Cold email is legal in most places when done right: honest sender identity, a real reason, a genuine
way to opt out, and respect for unsubscribes (CAN-SPAM / GDPR / local law). Don't email people who've
opted out. Keep claims truthful. Flag to the user if a target segment looks like consumers/EU where
rules are stricter.

## Course files (loaded from the course folder)

- `charm-cold-email/templates.md` from the course folder — the 8-part sequence, the "magic" call-booking email, and the
  direct-mail → follow-up combo, with annotations on why each line works.
