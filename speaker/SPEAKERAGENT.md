# SpeakerAgent on this bot: Justin's answers, 2026-11-24

For the SpeakerAgent agent (`speaker`) and the lead. It answers the four questions the agent asked Justin and sets the agent's day. Settings: [speaker.json](speaker.json). The method is unchanged: [../agents/speaker/PROCESS.md](../agents/speaker/PROCESS.md).

## His words

> "we shouldn't be sending a link anyway for them to book. We're trying to book it on their podcast, so we really just need to be checking using the SpeakerAgent dashboard and API to find the leads. SpeakerAgent.ai, as well as the process of how SpeakerAgent AI works, like the SpeakerAgent charter, to find 10, 20 podcasts a day: Go to their site. Apply. Send an email. Request to book. It's a prospecting agent. We're not asking them to book on our calendar most of the time, though. We're trying to find their calendar to book in, or where to apply, or sending them an email, letting them know that we want to potentially get on the show."

## The four questions

| # | The agent asked | The answer | Whose it is |
|---|---|---|---|
| 1 | A do-not-contact list | Start with an empty one. Create `context/suppression.csv` with the one line `kind,value,reason`, mode 600, and link it as HANDOFF Part 2 step 1 says. Check a made-up name: it must say clear. From then on, anyone who says no is added with `suppression.py add`. If Justin hands over a list later, its rows are added to the same file | Justin was asked and named nobody. Starting empty is this pack's choice, not his words |
| 2 | The booking link pitches end on | None. No pitch, form answer or follow-up carries Justin's calendar link, and the link the agent guessed is not used. The agent books on the show's side: the host's calendar, the show's application form, or an email asking to be on. Only when a host asks for Justin's calendar does the sales agent give the link saved as `SPEAKER_BOOKING_LINK` in the intake file. Justin gave that link on 2026-11-24; the lead saves it from his message | His words, above |
| 3 | Speaker details for guest forms | Do not ask him to write them. Read his SpeakerAgent persona (the bio and the three topics, in the dashboard and through the account), and fill `speaker.json` and `gtm-box/speaker/pitch-details.json` from it, word for word. The email is the Gmail account already connected to this agent. The website is the one in `campaign.json`. Social links and results come only from the persona and from OFFER.md; nothing is invented. Put the filled file in `requests/justin/` once, for one yes | The persona is his. Reading it instead of asking him again is this pack's choice |
| 4 | Whether pitches go on their own | His standing words (2026-11-07): "remove any blockers. no standing authorization", with `podcast_pitch` on auto. A yes given to another bot does not carry over, so this bot needs him to say it once here: "podcast pitches auto". Until that line is in `context/standing-approvals.md`, every pitch is a draft in his queue. A form or page that asks for payment is his spend, always | His, once he says it on this bot |

## The day

A prospecting agent. The goal is Justin on the show, booked on the show's side.

| # | Step | How |
|---|---|---|
| 1 | Pull the day's shows from SpeakerAgent | `python3 repo/skills/speaker/speakeragent/speakeragent.py podcasts --status New --json`, GREEN first, then YELLOW. Write each into the day's found file with its SpeakerAgent id |
| 2 | Fill a short day | If the account gives fewer than the day needs, or the key is not in yet: `speaker.py find` (free) and the agent's own search |
| 3 | Score and queue | `speaker.py score`. The account's match score is a claim to check, not a fact |
| 4 | Go to their site | Open the show's site and two recent episodes. Find, in this order: the host's booking calendar or an open booking page with no fee; the guest application form; the host's or the show's published address. Write what was seen into the case, each with its URL and the date |
| 5 | Request the booking by that route | A calendar: request a slot there. A form: apply, with answers from the pitch details only. An address: a short email saying he would like to be on the show, opening with one checked detail. For a show from the account, `speakeragent.py refresh <id>` gives the host's details and a first draft; it is checked against what was opened before it is used |
| 6 | Record it | `speaker.py mark`, the conversation log, and the show's status in SpeakerAgent: `speakeragent.py status <id> Contacted` |
| 7 | Follow up | Day 4 and day 10, then stop. Any reply goes to the sales agent. `Replied`, `Booked` or `Passed` is set in SpeakerAgent as it happens |

**The number:** 10 to 20 shows a day, each one opened and asked. His earlier number (2026-11-17) was 20 to 30 a day for 1 to 2 booked; the newer one is used, and `speaker.py report` prints what the booking rate says the goal needs.

**Held, never pushed through:** a route that asks for payment, a new account, a sign-in or a CAPTCHA. The show goes to `requests/justin/` with the page and what it asked.

## Setting SpeakerAgent up on this bot

The agent reported: "SpeakerAgent isn't set up yet because there's no login or API key for it."

1. Justin gives three values by hidden prompt in the SpeakerAgent agent's chat: `SPEAKERAGENT_API_URL`, `SPEAKERAGENT_API_KEY`, `SPEAKERAGENT_SPEAKER_ID`. They go in `.secrets/intake.env`, never in chat or a file in the pack.
2. Check: list one podcast lead with the command in step 1 of the day, and write its name into `log/setup-speaker.md`.
3. The dashboard: Justin signs in to SpeakerAgent.ai in this agent's browser himself. The agent reads the persona and the podcast list there; it never types his password.
4. A scout run for new matches uses the plan's allowance. Ask Justin before the first one, with what the dashboard says it uses.
5. Until the key is in, the day still runs on the free finder and the agent's own search (step 2 of the day).

## Not tested

Nothing on this page has run on the bot. The account's list has not been read with this pack's CLI on this bot, and what `refresh` or a scout run costs on Justin's plan is not known.
