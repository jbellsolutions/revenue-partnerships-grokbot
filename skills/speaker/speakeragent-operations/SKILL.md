---
name: speakeragent-operations
description: Onboard a SpeakerAgent client with an optional SaaS account, operate daily independent conference and podcast research, maintain local cases and reports, and recover interrupted Hermes runs on a supervised computer.
---

# Client onboarding and daily operations

Use [onboarding](references/onboarding.md) for a new client and [daily operation](references/daily-operation.md) for scheduled or resumed work. The distribution's ORGO-DEPLOYMENT.md covers the actual host setup. A skill alone is not a scheduler.

In the first interactive onboarding reply, explicitly ask: **“Do you want to create a SpeakerAgent.ai account, connect an existing account, or work independently without one?”** Saying “an account is optional” without asking the question does not complete onboarding. “I have not chosen yet” means the choice is unanswered, not that the client asked to skip the question. If it has already been asked or the client supplied a preference, do not repeat it. Save the answer in onboarding.json. Research is available while the choice is undecided; account creation must not become a prerequisite. Scheduled runs read the saved preference and never wait for an answer. Follow the [standalone capability map](references/standalone-capabilities.md).

Collect only the speaker facts and constraints needed to qualify results. Then run a useful first batch. For daily work, persist the client's authority, timezone, daily target, research limits, model/provider budget and delivery preference. Use one active mission writer. Default delivery is a saved brief; connecting messaging is separate from permission to contact organizers.

On every wake, read the persona, mission, account preference, previous cases, rejected/duplicate records, pending actions and next step. Resume valuable unfinished cases before expanding discovery. Rotate web, association, social and event-directory sources; use [social research](../speakeragent-social/SKILL.md). Recheck deadlines, find newly opened calls, improve contact routes and prepare truthful pitches. Learn from client feedback without changing verified facts or inflating scores.

Update stable case files, write a dated brief with new/changed/held/rejected counts and useful links, and save a concrete next action. A day with no qualified opportunities is valid only after actual research and an honest coverage/shortfall report. Do not invent a daily quota of paid leads or send a repetitive empty digest.

The bounded runtime validates the run's artifacts and enforces process ownership, daily deduplication and a wall-clock ceiling. Its checks do not verify every claim or guarantee a monetary spend cap. Tool/provider billing controls must enforce any hard currency limit. Unexpected provider effects remain pending until reconciled.
