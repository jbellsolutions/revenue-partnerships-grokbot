# The front desk: handing operating work to the Operator and the Co-Founder agent

For the sales agent (`sales-crm`) and the lead. Settings: [handover.json](handover.json). The sales agent's own method is unchanged: [../agents/sales-crm/PROCESS.md](../agents/sales-crm/PROCESS.md).

**This mode is off in this pack.** It goes on, one part at a time, when Justin says so in the lead's chat. Until then the sales agent works as PROCESS.md says and writes the CRM itself.

## Where this comes from

Justin's words of 2026-11-24, dictated in another chat and passed to this pack by the chat that works on his call follow-up. They were not typed to this pack's chat, so every part below waits on his yes here:

> "you kind of need to have a sales and CRM agent on GrokBot for the purposes of me saying, 'Hey, let's run this campaign' ... At the end of the day, it really should be just a facilitator. It's passing it off to the co-founder and the operator to do the work. Those two agents should be the ones operating."

> "instead of us doing a check three times a day, it should automatically update via webhook ... when new actions happen that are relevant."

Everything else on this page is design, not a rule of his. Any of it can change.

## Who does what when the mode is on

| Agent | Where | Does |
|---|---|---|
| The sales agent | This bot | Takes Justin's order, writes it down as one request, reads the result and tells him. Keeps each person's note in the vault |
| The Operator | His own computer, outside this bot | The operating work: CRM changes, campaigns, follow-up drafts, sends after Justin's yes |
| The Co-Founder agent | His own computer, outside this bot | Client success and builds |

This bot never signs in to, changes or restarts either of those two agents. It only writes a request row they can read.

## The four parts, each with its own switch

| Part | Switch in `handover.json` | Off (today) | On |
|---|---|---|---|
| 1. Orders | `orders.on` | An order from Justin is worked by this bot's own agents | The order becomes one row in the Requests table of his Notion Command Center, and the sales agent reads the result from that row |
| 2. Who writes the CRM | `crm_writer` | `sales-crm`: this bot writes GoHighLevel | `operator`: `crm.writer` in `campaign.json` is set to `none`, and the day file goes to the Operator, as PROCESS.md already describes for a CRM that is not the bot's to write |
| 3. Capture | `capture.on` | The bot's work is not in the single brain | One line per agent session goes to the single brain, like his other computers |
| 4. Events before timers | `events_first.on` | Reply check three times a day; Pipeline sweep twice a day | Once the Reply webhook is seen firing, Reply check runs once a day as the catch-up |

### 1. An order becomes a request row

1. Justin tells the sales agent, or the lead, what he wants ("run this campaign", "follow up with this person").
2. The sales agent adds one row to Requests: what he asked in his words, for whom, which agent (`operator` or `cofounder`), and the link to the person's note. Operating work (the CRM, campaigns, sends, follow-ups) names the Operator. A client check-in or a build names the Co-Founder agent. An order it cannot place goes to `requests/justin/` with the question.
3. It logs the order in `log/handover.jsonl` with the row's link, and tells Justin it is handed over.
4. On its next run it reads the rows it wrote. A row with a result is reported to Justin once and marked reported in the log. A row set to Needs Justin goes to `requests/justin/` with the draft attached. A row with no result after `orders.stale_after_hours` is reported as waiting, once.
5. It never asks the other agent what happened, and never does the handed-over work itself while the row is open.

The table's id is saved at intake in `context/owner.md` (`NOTION_REQUESTS_TABLE`), never in this pack. The row's fields are read from the table before the first write; a table whose fields do not fit is reported, not changed.

Not built on the other side as of 2026-11-24: nothing wakes the Operator or the Co-Founder agent when a row is added; the table is read on a timer by another agent. With `orders.on` and no reader, an order would sit. So part 1 goes on only after a test row comes back with a result.

### 2. The CRM write goes to the Operator

When Justin says the Operator writes GoHighLevel: set `crm_writer` to `operator` here and `crm.writer` to `none` in `campaign.json`. PROCESS.md's steps 5 and 10 then write the day file (`convlog.py daily --mark`) and the sales agent adds one Requests row a day naming the Operator with the day file's path. The vault, the answers and the follow-up still run on this bot.

As of 2026-11-24 the Operator has the GoHighLevel skills and no key. Turning this on before he has one would mean nobody writes the CRM. It stays `sales-crm` until Justin says the Operator is connected.

**Not decided:** whether the sales agent keeps answering replies while the Operator writes the CRM. This pack leaves replies with the sales agent.

### 3. Capture to the single brain

At each agent's day close, the lead writes one line per agent to the single brain's `activity/` folder, in a folder named for this bot, in the same shape as the lines his other computers write there (read one before the first write and match it): the date, the agent, what it finished, what is waiting on Justin. No transcript, no person's contact details, no key. This needs the path Justin picks in NEEDS-JUSTIN A9 (a deploy key on the bot, or his Mac pulling the daily notes).

### 4. Events before timers

The pack already wakes the sales agent by event: the worker posts hot replies to the Reply webhook, and a booking posts to the Booking webhook. The timers are the catch-up for an event that never arrived.

With `events_first.on`: when `team-registry.md` shows the Reply webhook's address and `log/runs` shows it fired on two different days, the sales agent asks the lead to move Reply check to once a day. Pipeline sweep stays twice a day until something posts the events it looks for (a quiet thread, an overdue step); nothing does today. A webhook that goes a full day with replies in the digest and no firing puts Reply check back to three and tells Justin.

## Turning it on

Justin says it in the lead's chat; the lead writes his words and the date to `vault/Decisions.md` and changes the one switch.

| He says | The lead does |
|---|---|
| "hand-over orders on" | Writes one test row to Requests, waits for a result, then sets `orders.on` |
| "the Operator writes the CRM" | Sets `crm_writer` to `operator` and `crm.writer` to `none` |
| "capture on" | Sets `capture.on` once the single brain path works |
| "events first" | Sets `events_first.on` |
| "hand-over off" | Sets every switch back and `crm.writer` to `sales-crm` |

## Not tested

Nothing here has run on a bot. No row has been written to the Requests table from this pack, and no line to the single brain.
