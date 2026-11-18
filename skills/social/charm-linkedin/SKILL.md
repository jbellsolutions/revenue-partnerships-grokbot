---
name: charm-linkedin
description: >
  Writes Charm Offensive LinkedIn connection invites and follow-up messages that get accepted and
  start conversations — personalized with research on the prospect. Use when the user asks to "write
  a LinkedIn invite", "LinkedIn connection request", "LinkedIn message", "LinkedIn outreach", "DM this
  person on LinkedIn", "follow up after they accept", set up a LinkedIn lead-gen sequence (e.g. for
  LinkedHelper), or wants their LinkedIn messaging to sound human and funny instead of salesy.
metadata:
  version: "0.1.0"
---

# Charm Offensive — LinkedIn

## Course material (load first)

The approach is adapted from Jon Buchan's Charm Offensive. Its template and playbook files are licensed course material, so they are not in this pack. Load them from `$COURSE_MATERIAL_DIR/charm/` or, failing that, `.secrets/course/charm/` (given at intake): `charm-offensive-foundation/` holds the voice, story and profile files, and each charm skill's own files sit in a folder named after it. If a file is missing, write from the principles on this page and say in your output that the templates weren't given.

Write LinkedIn invites and follow-ups that feel human, get accepted at scale, and open a real
conversation — using disarming honesty and humour, then a soft, gain-framed pitch.

## Step 0 — Load the voice and profile (always)

1. Read `charm-offensive-foundation/voice-and-humour.md` from the course folder.
2. Get the user's `charm-profile.md` (ask for it or build a quick one via `charm-offensive-foundation`).
   You need: what they do / who they help, the sector(s) they love, and their sign-off style.
3. Read `charm-linkedin/templates.md` from the course folder for the exact invite + follow-up copy.

## Step 1 — Scale vs. key prospect

Ask which mode:

- **At scale** (a segment / LinkedHelper campaign): use the light, human, non-personalised invite —
  a plain, human invite gets accepted far more than a salesy one. Then a sector-specific follow-up after they
  connect. Use safe merge fields ({firstname}) only.
- **Key prospect** (someone they *really* want): fully personalise. Research them and reference a
  genuine, specific detail. This is worth the extra effort and always beats the scale template.

## Step 2 — Research

For key prospects (and to sharpen segment messaging): use connected tools / LinkedIn scrapers /
enrichment skills if installed, plus WebSearch, to find role, what they post about, shared interests,
recommendations, the sector they're in. Capture only genuine hooks. For the sector follow-up, you
mainly need to name their sector convincingly and show you love working in it (the Liking principle).

## Step 3 — Draft

**Invite** — keep it short, human, and a little cheeky. Two proven shapes (see `charm-linkedin/templates.md` from the course folder):
the "not-the-generic-invite" line, or the "one/two punch" (a curiosity hook + a funny escape hatch
that sets up the follow-up). Character-limit aware.

**Follow-up (after they accept)** — reference the humour in the invite, make light of the sudden
pitch, show you love their sector, and frame it as *them* gaining (useful ideas they keep either way), not
a hard sell. Low-pressure CTA to chat.

Keep LinkedIn messages shorter than emails. One hook, one soft ask.

## Step 4 — Self-check and deliver

Run the voice self-check. Then output: the invite text (with character count if near the limit), the
accept-follow-up, and, for a sequence, any second nudge — each labelled. If the user runs LinkedHelper
or similar, format with the right merge fields. Never automate sending without the user's approval;
respect LinkedIn's limits and terms.

## Course files (loaded from the course folder)

- `charm-linkedin/templates.md` from the course folder — invite copy (generic-human + one/two punch), the sector-specific
  follow-up, and the post-accept message, with annotations.
