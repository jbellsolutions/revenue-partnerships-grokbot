---
name: charm-offensive-foundation
description: >
  The shared voice, story, and offer engine for all Charm Offensive outreach skills. Use this
  when the user wants to "set up my Charm Offensive profile", "define my story", "define my offer",
  "define my ideal clients", capture their brand voice for outreach, or when ANY other charm-* skill
  needs the user's story/offer/voice and no profile exists yet. Produces and stores a reusable
  charm-profile.md and teaches the Charm Offensive humour and voice rules that every draft must follow.
metadata:
  version: "0.1.0"
---

# Charm Offensive — Foundation (Voice, Story & Offer)

## Course material (load first)

The approach is adapted from Jon Buchan's Charm Offensive. Its template and playbook files are licensed course material, so they are not in this pack. Load them from `$COURSE_MATERIAL_DIR/charm/` or, failing that, `.secrets/course/charm/` (given at intake): `charm-offensive-foundation/` holds the voice, story and profile files, and each charm skill's own files sit in a folder named after it. If a file is missing, write from the principles on this page and say in your output that the templates weren't given.

This skill does two jobs:

1. It **captures the user's Charm Offensive profile** (their story, ideal clients, and offer) and
   stores it as a reusable file the other skills read.
2. It is the **canonical reference for the Charm Offensive voice and humour** — every other
   `charm-*` skill loads `charm-offensive-foundation/voice-and-humour.md` from the course folder and `charm-offensive-foundation/story-formula.md` from the course folder from
   here before writing a single word.

The whole method comes from Jon Buchan's Charm Offensive: win attention with disarming honesty and
humour, be human, offer useful ideas they keep either way, and never sound like a corporate sales robot.

## When another skill calls you

If a `charm-*` skill needs the user's story/offer/voice and there is no profile yet, do the fast
version: read `charm-offensive-foundation/profile-template.md` from the course folder, ask the user the minimum questions to fill it, save
`charm-profile.md`, then hand control back. Do not block a drafting task for longer than necessary.

## Building the profile (the full flow)

Read `charm-offensive-foundation/profile-template.md` from the course folder for the exact structure. Walk the user through it, but keep it
light — ask in small batches, not one giant form. Capture:

**Your Story** — what you're great at (up to 5 things); what you stand for (3 values); what you're
against (up to 3 issues in your sector); obstacles you've faced (a struggle that resonates); your
ambitions (not about money). This becomes the raw material for the Identity → Struggle → Discovery →
Surprise story arc used in podcast, PR and speaking pitches. If something isn't genuine, leave it out.

**Your Ideal Clients** — who you help most (roles/titles); sectors you're excited about; where they
are; the attributes you look for (so we can lean on the "Liking" principle).

**Your Offer** — the pain points you solve (general + problems with existing solutions); the pain
points you help them AVOID (e.g. no long contracts, no sleazy tactics); your risk-reversal or
"no-brainer" hook if you have one.

**Your Voice Assets** — the concrete props that make Charm emails land: a photo of a pet / animal
doing something silly (the signature absurd photo); a self-deprecating photo for follow-ups; three job
titles for the signature (serious / descriptive / funny); the URL and Calendly/booking link; the
sign-off style (warm, with a touch of personality).

## Saving the profile

Write the completed profile to `charm-profile.md` and deliver it to the user with SendUserFile. Tell
them to keep it handy — they can point any charm skill at it, or paste its contents, so drafts sound
like them and use their real details instead of placeholders. If a desktop folder is connected, offer
to save it there too.

## The non-negotiable voice rules

Before writing anything in ANY channel, load and apply `charm-offensive-foundation/voice-and-humour.md` from the course folder. The essentials:

- **Disarming honesty beats slick selling.** Admit the awkward truth (say plainly, and lightly, how you came across them).
- **Humour is the pattern interrupt.** Use the ten humour formulas (the Reverse, Triples, Lists,
  Understatement, Exaggeration, Incongruent Absurdity, Funny Words, Oxymorons, Parody). One or two
  well-placed laughs, not a comedy routine.
- **Make it look like they gain**, not like they're being hard-sold. Offer useful ideas they keep either way.
- **Low-pressure CTAs** with a humorous escape hatch (an easy, playful way to reply or to say no).
- **Be human and warm.** Sign off with personality. Never corporate, never jargon, never a wall of text.
- **Genuine only.** Never fabricate a shared interest, a fake stat, or a compliment you don't mean.

## Guardrails

Keep it ethical and compliant: real reasons, real facts, honest claims. For cold email, respect
opt-outs and local law (CAN-SPAM/GDPR) — see the note in `charm-cold-email`. Never invent testimonials,
metrics, or client names. If the user hasn't given you a real detail, ask or leave a clearly marked
`{placeholder}` rather than making something up.

## Course files (loaded from the course folder)

- `charm-offensive-foundation/voice-and-humour.md` from the course folder — the full voice rules + ten humour formulas with examples.
- `charm-offensive-foundation/story-formula.md` from the course folder — the Identity/Struggle/Discovery/Surprise arc + IMPACT and the six
  persuasion principles.
- `charm-offensive-foundation/profile-template.md` from the course folder — the exact profile structure to fill and save.
