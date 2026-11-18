---
name: cold-email-quickstart
description: "First-run wizard that walks a user from zero to a launched cold email campaign, one phase at a time with a confirmation gate between phases: sending-tool setup, mailboxes, strategy, lead tracking, a lead list, verification, copy, A/B testing and deploy. Use when someone says 'set up cold email', 'cold email quickstart', 'start cold email from scratch', 'first cold email campaign' or 'launch my first campaign'. The wizard's content is member-only third-party material that loads from the private course folder given at intake."
---

# Cold email quickstart (loader)

The full wizard is member-only material from a third-party cold email program, so the pack holds only this loader.

## Load the material

1. Look for `$COURSE_MATERIAL_DIR/cold-email-quickstart/`, then `.secrets/course/cold-email-quickstart/` under
   the workspace. Justin gives it at intake.
2. If it's there, read its `SKILL.md`, `manifest.yaml` and `references/phase-prompts.md`, and follow them.
3. If it isn't, say the wizard material wasn't given, and run the same phases from our own skills instead:
   `cold-email-master` (strategy and copy), `consulti` and `scraper-forge` (lists), `verify-leads` (verification),
   `cold-copy` (copy check), `cold-campaigns` and `plusvibe` (deploy).

## Rules that always apply

- Every gate in GATES.md: no signup, purchase, mailbox order or launch without Justin's yes.
- Never publish the wizard's content, its links or its codes.
