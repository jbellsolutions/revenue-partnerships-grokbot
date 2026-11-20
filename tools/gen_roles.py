#!/usr/bin/env python3
"""Generates roles/*.md, TRIGGER-MAP.md (routine sections), skills.json and routines.json from one table.

    python3 tools/gen_roles.py

Edit ROLES / ACCOUNTS here, not the generated files. It also checks that no two routines start within
5 minutes of each other in any week (Grok wants routines at least 5 minutes apart)."""
import json, os, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.dirname(HERE)  # the pack root; this file is in tools/

ACCOUNTS = {  # order matters: check.py matches the first key a charter line starts with or contains
    "Slack": (None, ["SLACK_BOT_TOKEN"]),
    "Notion": (None, ["NOTION_TOKEN"]),
    "GoHighLevel": ("skills/sales-crm/gohighlevel-cli", ["GHL_API_KEY", "GHL_LOCATION_ID"]),
    "Guarded sender": ("gtm-box/box/sender_client.py", ["SENDER_URL", "SENDER_TOKEN"]),
    "Cal.com": (None, ["CAL_API_KEY"]),
    "Gmail": (None, ["SIGNIN"]),
    "Google Calendar": (None, ["SIGNIN"]),
    "Consulti": ("skills/cold-email/consulti", ["CONSULTI_API_KEY"]),
    "treg": ("skills/content-seo/treg", ["TREG_API_KEY"]),
    "PlusVibe": ("skills/cold-email/plusvibe", ["PLUSVIBE_API_KEY", "PLUSVIBE_WORKSPACE_ID"]),
    "Maildoso": ("gtm-box/cold/maildoso.py", ["MAILDOSO_API_KEY"]),
    "Instantly": ("skills/cold-email/winnr-instantly", ["INSTANTLY_API_KEY"]),
    "AgentMail": ("gtm-box/prospect/agentmail.py", ["AGENTMAIL_API_KEY"]),
    "One API": ("skills/cold-email/one-api", ["ONE_API_URL", "ONE_API_TOKEN"]),
    "Scrapebox": ("skills/cold-email/scrapebox", ["SCRAPEBOX_TOKEN"]),
    "Decodo": ("skills/cold-email/scraper-forge", ["DECODO_PROXY_USER", "DECODO_PROXY_PASSWORD"]),
    "LinkedIn dashboard": ("skills/social/linkedin-dashboard", ["LINKEDIN_DASH_TOKEN"]),
    "LinkedIn": (None, ["SIGNIN"]),
    "Lead Radar": ("skills/social/lead-radar", ["RADAR_APP_URL", "RADAR_DASHBOARD_PASSWORD"]),
    "Skool": ("skills/social/skool-inbound", ["SIGNIN"]),
    "SpeakerAgent": ("skills/speaker/speakeragent", ["SPEAKERAGENT_API_URL", "SPEAKERAGENT_API_KEY", "SPEAKERAGENT_SPEAKER_ID"]),
    "beehiiv": (None, ["BEEHIIV_API_KEY"]),
    "RankSpot": ("skills/content-seo/aeo-citations", ["RANKSPOT_API_KEY"]),
    "Medium": ("skills/content-seo/medium", ["SIGNIN"]),
    "GitHub": (None, ["SIGNIN"]),
    "X": ("skills/channels/x-channel", ["SIGNIN"]),
    "YouTube": ("skills/channels/youtube-channel", ["SIGNIN"]),
    "Worker": ("worker/server.py", ["WORKER_URL", "WORKER_TOKEN"]),
}

STD = ["no spend outside the guards", "no send without an approved template", "suppression first", "STOP stops everything", "price and terms go to Justin"]

ROLES = [
    dict(name="lead", title="Lead", folds="revenue-partner, gtm-lead, router",
         job="Plans the day from the worker's digest, routes work between roles and to the worker, posts the scoreboard to Slack and Notion, writes the vault daily note and keeps Justin's queue. The worker runs the watchdog.",
         inputs="Every role's daily file, requests/lead/, the heartbeat, GoHighLevel (read), the spend ledger",
         outputs="The morning plan, alarms, the evening scoreboard, vault/Daily/<date>.md, Justin's queue in Notion Drafts",
         accounts=["Slack", "Notion", "GoHighLevel (read only)", "Worker"],
         sched=[("Morning plan", "10 12 * * *"), ("Evening scoreboard and vault note", "40 23 * * *")],
         events=[],
         rules="Reports and routes; never sends to a lead. Counts only evidence. The worker's watchdog alarms Slack on any silent role or failing job; lead reads the digest counts, flags any send with no approved template, and the scrape or model pool hitting its cap two days running.",
         kpis="Scoreboard posted daily; no role silent over 26 hours; every number backed by a run-log line; leads and booked calls reported from GoHighLevel.",
         skills=["worker-plane", "gtm-role", "gtm-shared", "gtm-workflow", "ai-guy-agent-team"]),
    dict(name="sales-crm", title="Sales CRM", folds="opener, replies, closer, deals, warm",
         job="The one CRM writer: every reply from every lane, openers, warm reconnects, call prep, the pipeline sweep, the deal ledger and the daily close in GoHighLevel.",
         inputs="Replies (PlusVibe, Instantly, Gmail, GoHighLevel inbound), requests/sales-crm/ from every role, Cal.com bookings",
         outputs="Every reply recorded with a dated next step, reply drafts, call briefs, stage moves on evidence, the deal ledger",
         accounts=["GoHighLevel", "Guarded sender", "Cal.com", "Gmail", "Google Calendar"],
         sched=[("Call prep", "5 11 * * *"), ("Reply check (hot replies from the worker)", "15 13,17,21 * * *"), ("Pipeline sweep", "25 12,20 * * *"),
                ("Openers", "35 14 * * *"), ("Warm reconnects and referral asks", "45 15 * * *"), ("Deal ledger", "25 22 * * *"),
                ("Daily close and no-shows", "20 23 * * *")],
         events=[("Reply webhook", "The worker posts hot reply ids (interested, question, referral, angry) after its sort; GoHighLevel inbound may post here too", "Read those replies, record them, draft the next step"),
                 ("Booking webhook", "Cal.com posts a new booking", "Move to Call booked, write the call brief")],
         rules="Writes GoHighLevel only while `crm-writes: on`. Moves a stage only on evidence. Opt-outs are final at once (`suppression.py add`). `crm_opener` and warm reconnects stay draft until Justin approves them. Replies are pulled and sorted on the worker (opt-outs taken there at once); this role sees only hot ones, from the digest or the Reply webhook. The Reply check reads the digest as the backstop.",
         kpis="Booked calls a day; every reply recorded the same day; 0 open records without an owner, next action and date; show rate.",
         skills="*"),
    dict(name="cold-email", title="Cold Email and Data", folds="cold-email, plusvibe-operator, copywriter, data, prospector",
         job="Cold email end to end (inbox health, lists, copy, campaigns, one-to-one prospecting) and the data lane: specs scrapers and list builds, and orders them from the worker (Codex writes and repairs the scrapers there, cron runs them), so every role gets data at high volume and low cost without spending GrokBot's allowance.",
         inputs="Consulti, One API, Scrapebox, Decodo, PlusVibe and Instantly stats, requests/cold-email/ (lists and scraper requests)",
         outputs="Verified lists, campaign copy and variants, prospector drafts, scrapers in tools/scrapers/ with their REGISTRY, data files for every role",
         accounts=["Consulti", "PlusVibe", "Maildoso", "Instantly", "AgentMail", "One API", "Scrapebox", "Decodo", "treg"],
         sched=[("Lists, scrapers and worker orders", "35 12 * * *"), ("Campaign read and copy", "5 15 * * *"), ("Prospector research and drafts", "50 16 * * 1-5")],
         events=[],
         rules="No cold send until the health check passes on the exact domains. Consulti is the only paid data source. Paid scrape rungs and Decodo run only under the scrape pool (`spend_guard.py ... --pool scrape`, $5 a day). No link to the site in a first cold email. No sends from a domain Justin uses for real mail. Every prospector email approved by Justin. Copy names no price.",
         kpis="Lists verified and at target; inboxes healthy; reply rate by variant; booked from cold; scrapers `ok` in the REGISTRY; cost per 1,000 rows.",
         skills="*"),
    dict(name="speaker", title="Speaker", folds="podcast",
         job="Keeps Justin booked on podcasts, YouTube interviews, stages and summits: the worker researches and scores shows all day; this role pitches the 4s and 5s, fills guest forms and follows up.",
         inputs="SpeakerAgent persona and mission, show and event research, collab-blitz handoffs, `gtm-box/speaker/pitch-details.json`",
         outputs="Up to seven research cycles a day, pitches, guest-form submissions, follow-ups, conference applications",
         accounts=["SpeakerAgent", "Gmail"],
         sched=[("Show shortlist and pitches", "30 14 * * *"), ("Stages and conferences", "5 17 * * 1,3,5"), ("Follow-up", "50 20 * * *"), ("Pitch submit", "10 21 * * *")],
         events=[],
         rules="`podcast_pitch` is auto only once Justin re-confirms it on this bot; every other type drafts. A form that asks for payment, an account, a sign-in or a CAPTCHA is held, never pushed through. Every form uses `pitch-details.json`, never invented answers. Every pitch cites one specific recent episode; shows quiet for 90 days are dropped. Follow-ups (`podcast_follow_up`) at most twice (day 4 and day 10) and stop on any reply.",
         kpis="1 show or video booked a day; pitches sent; stages applied to.",
         skills="*"),
    dict(name="partners", title="Partners and Collabs", folds="access, affiliates, alliances, cause, channel, co-promotion, creators, house, referral, sponsorships, stages-media, revenue-partnerships-growth",
         job="Runs the aggressive collaboration campaign and every partner family: finds and qualifies collaborators daily, drafts personal notes, works partner tickets and replies, reviews the portfolio.",
         inputs="Partner families, collab-blitz targets, dream dossiers, link briefs from content-seo, partner replies",
         outputs="The collab pipeline, partner notes and replies, link outreach drafts, the portfolio review",
         accounts=["Gmail", "Consulti"],
         sched=[("Partner find", "50 11 * * *"), ("Work the tickets", "40 12,18 * * *"), ("Partner replies", "50 13,17,21 * * *"),
                ("Collab blitz", "20 18 * * *"), ("Portfolio review", "30 21 * * *")],
         events=[],
         rules="No price, commission, share or result except the terms message word for word, and only after interest. No link in a first touch. Never a partner: anyone selling the same thing, any group on the do-not-mention list (given at intake), anyone suppressed. Every collab type is ask-first until its replies prove good.",
         kpis="1 to 2 collaborations agreed a day; targets found and qualified; terms messages after interest; partners agreed; calls from partners' lists.",
         skills="*"),
    dict(name="dream", title="Dream 100 and 500", folds="dream-100, dream-500",
         job="The Dream 100 and the Dream 500, both about the fractional job: the companies Justin would most want to work inside as a fractional staff member. A researched dossier for each, one hand-written first touch per Dream 100 target, small waves with a true first line for the Dream 500, as plain email from a real person, then one follow-up. The words: repo/fractional/MESSAGES.md. Settings: repo/fractional/settings/dream-100.json and dream-500.json. The steps (dossier, score, first touch, follow-up) are the template's: repo/agents/dream-100/PROCESS.md and repo/agents/dream-500/PROCESS.md.",
         inputs="The Dream lists, public sources, the collab pipeline",
         outputs="Dossiers with a warm path, first-touch and follow-up drafts in Justin's queue, handoffs to partners or speaker",
         accounts=["Gmail"],
         sched=[("Dossiers", "20 16 * * *"), ("Dream 100 first touches and follow-up", "55 15 * * 1-5"), ("Dream 500 wave", "35 19 * * 1-5")],
         events=[],
         rules="The lists themselves are private, given at intake (data/dream/). Every message opens with one true, specific thing about them and why Justin reached out; with nothing true to say, the person waits. Plain text, no link, no figure; the ask is a reply. Every first touch is a draft for Justin until he approves the type. LinkedIn goes through OutFlo or his own computer (repo/LINKEDIN.md), never this computer.",
         kpis="Dossiers done; Dream 100 and Dream 500 targets reached; replies and conversations about a fractional role from each list.",
         skills="*"),
    dict(name="social", title="Social and Inbound", folds="linkedin, lead-radar, skool, rev-partner",
         job="Inbound and social: the worker reads Skool's non-AI groups and Lead Radar and scores every post; this role answers the real askers, works Justin's LinkedIn, and pulls creators over 10,000 followers.",
         inputs="Skool groups through Justin's signed-in session, the Lead Radar dashboard, the LinkedIn dashboard and his connections, creator lists",
         outputs="Judged leads with evidence handed to sales-crm, reply and owner-note drafts, groups joined, LinkedIn messages and posts, creator lists",
         accounts=["Skool", "Lead Radar", "LinkedIn dashboard", "LinkedIn", "Consulti", "treg"],
         sched=[("LinkedIn board, messages and post", "45 12 * * *"), ("Radar and Skool askers from the worker", "5 14 * * *"), ("Job site sweep", "15 15 * * *"),
                ("Skool join and owner notes", "40 16 * * *"), ("Creator pull and partner drafts", "10 17 * * *")],
         events=[],
         rules="Free non-AI Skool groups only, at most 5 joins a day, a person's pace. Stop the platform for the day on the first browser check, limit or account warning. The first public post and each message type wait for Justin. One browser profile per account. Lead Radar and the X intent search never contact anyone: read only, every lead goes to sales-crm with its evidence.",
         kpis="Skool askers found and handed off a day; Radar leads judged; first-degree LinkedIn messages a day (50 once approved); 100 creators a platform a day; leads in GoHighLevel from inbound.",
         skills="*"),
    dict(name="content-seo", title="Content, SEO and AEO", folds="content, seo-aeo",
         job="Gets the business named by AI engines and found in search, and publishes daily content: the AEO loop with RankSpot, articles through pull requests, Medium, the newsletter.",
         inputs="Calls and stories from every role, the content repo (`CONTENT_REPO_REMOTE`), Justin's SEO kit, RankSpot, the prompt panel, the citation queue",
         outputs="Daily content, the AI-visibility read, articles (as pull requests), Medium pieces, link and keyword briefs, newsletter drafts",
         accounts=["RankSpot", "Medium", "treg", "beehiiv", "GitHub"],
         sched=[("AI visibility read", "45 14 * * 1"), ("SEO daily", "25 15 * * *"), ("Article pick", "10 16 * * 2,4"),
                ("Links and keywords", "10 16 * * 5"), ("Medium", "5 19 * * 2,4"), ("Daily content", "5 22 * * *"), ("Channel read", "55 17 * * 5")],
         events=[],
         rules="Only the site named in campaign.json on this bot. RankSpot paid actions only through the spend guard; never its email-finding or outreach. The first post on each channel waits for Justin. Site changes only as pull requests Justin merges. Clients described, never named. The AEO audit ladder states no price until Justin writes one into `standing-approvals.md` (`aeo_audit_offer` is ask-first).",
         kpis="1 piece published a day with the live link; share of panel prompts that cite us, per engine, week over week; articles within the cap; Medium pieces live.",
         skills="*"),
    dict(name="channels", title="YouTube and X", folds="new on this bot",
         job="Builds Justin's own YouTube and X into an AI channel: daily X posts and replies, a weekly thread, video briefs and scripts, Shorts and descriptions, uploads as drafts, the weekly read.",
         inputs="Calls, builds and stories, the prompt panel, Skool and Lead Radar asks, Justin's recordings in requests/channels/",
         outputs="X posts, threads and reply drafts, video briefs, descriptions, Shorts cuts, private uploads, the weekly read",
         accounts=["X", "YouTube"],
         sched=[("X posts and replies", "25 14 * * *"), ("YouTube briefs and the weekly read", "25 18 * * 1,4"), ("X engagement", "45 19 * * *")],
         events=[],
         rules="Justin's own accounts, his voice. The first post on each channel waits for Justin; then `x_post`, `x_reply` and `youtube_publish` are drafts until he marks them auto. Uploads go up private or unlisted. No growth tools, no bulk follows or likes, no DMs. Stop on the first warning or limit.",
         kpis="1 X post a day and 1 thread a week live; 2 video briefs a week; videos published; leads from the channels in GoHighLevel.",
         skills="*"),
]


# Revenue and content plays (private plays research, PLAYS.md and CONTENT.md, 2026-11-12): which play skill each routine also runs, so the
# older skill that matches the same routine doesn't crowd it out.
PLAY_RULES = {
    "sales-crm": "Plays: Reply webhook and Reply check also run `reply-fast-lane`; Pipeline sweep and Call prep also run `quiet-thread-nudge`; a lead Justin shares in chat or Slack runs `screenshot-to-crm`.",
    "cold-email": "Plays: Inbox health and warmup and Lists and data top-up also run `dead-lead-recycle`; Prospector research and drafts also runs `ad-library-leads`.",
    "speaker": "Plays: Show research and Pitch submit run `show-rss-research`; Follow-up runs `podcast-follow-up-and-attribution`.",
    "social": "Plays: Radar sweep and Needs-you also runs `x-intent-search` (read only); LinkedIn board, messages and post runs `linkedin-ghostwriter` for posts and `linkedin-reply-desk` for the comment queue, and Justin's \"posted\" message runs `linkedin-reply-desk`. LinkedIn posts and comments are drafts Justin publishes by hand from his own device; never sign the bot's cloud browser into his LinkedIn for posting or reading the feed.",
    "content-seo": "Plays: Daily content runs `content-engine` when an idea or recording waits in requests/ (one source, drafts for YouTube, X and LinkedIn); Channel read runs `channel-weekly-read`, which every content skill reads before drafting; the AI visibility read and any audit request run `aeo-audit-ladder`.",
    "channels": "Plays: X posts and replies runs `x-outlier-drafts`; X engagement runs `x-reply-desk` (the bot writes briefs, Justin types replies); YouTube briefs and the weekly read runs `youtube-brief-loop`. X: the bot never posts, replies, likes or follows through a browser, even when a type is marked auto (an account doing that was locked read-only on 2026-09-25); Justin posts by hand, or the bot posts through the official X API only if Justin adds a key.",
}
for _r in ROLES:
    if _r["name"] in PLAY_RULES:
        _r["rules"] = _r["rules"] + " " + PLAY_RULES[_r["name"]]


# Which of the nine Revenue OS functions (agents.json) each routine belongs to. `core` runs on every tier:
# the lead role and the data lane that feeds every function. tiers.json says which functions a tier has;
# tools/tier.py turns the two into the list of routines to create.
AGENT_BY_ROLE = {"lead": "core", "sales-crm": "sales-crm", "cold-email": "cold-email", "speaker": "speaker",
                 "partners": "partners", "dream": "dream-100", "social": "lead-radar", "content-seo": "aeo-seo",
                 "channels": "content"}
AGENT_BY_ROUTINE = {
    "Lists, scrapers and worker orders": "core",
    "Dream 500 wave": "dream-500",
    "LinkedIn board, messages and post": "content",
    "Creator pull and partner drafts": "partners",
    "Daily content": "content",
    "Channel read": "content",
}


def agent_of(role, routine):
    return AGENT_BY_ROUTINE.get(routine, AGENT_BY_ROLE[role])


# The Revenue OS function folders each role works from (the template's processes, settings examples and prompts).
PROCESS = {
    "sales-crm": "repo/agents/sales-crm/PROCESS.md (read the person's note before every reply)",
    "cold-email": "repo/agents/cold-email/PROCESS.md",
    "speaker": "repo/agents/speaker/PROCESS.md",
    "partners": "repo/agents/partners/PROCESS.md",
    "social": "repo/agents/lead-radar/PROCESS.md for the radar; LinkedIn only as repo/LINKEDIN.md says",
    "content-seo": "repo/agents/aeo-seo/PROCESS.md and repo/agents/content/PROCESS.md",
    "channels": "repo/agents/content/PROCESS.md",
}
FRACTIONAL = {
    "cold-email": "On this bot cold leads carry the fractional job (repo/fractional/MESSAGES.md, settings repo/fractional/settings/cold-email.json): a plain email from a real person with a true first line per row (repo/fractional/prompts/first-line.md), no link, reply only. Companies Lead Radar found hiring arrive in requests/cold-email/ with their post and first line. The earlier offer's campaigns in the cold skills are not used.",
    "social": "Lead Radar on this bot is the AI Guy Lead Radar plus job sites (repo/fractional/settings/lead-radar.json): people asking for AI, automation or VA help go to sales-crm; the Job site sweep reads the job sites for businesses hiring a virtual assistant or an AI role, judges each post with repo/fractional/prompts/job-fit.md through repo/engines/route.py --agent lead-radar, and hands every post scored 4 or 5 to requests/cold-email/ with its link and first line. Reads only: nothing applies to a job, answers a post or contacts anyone.",
    "sales-crm": "A reply to a fractional email is answered as the Replies table in repo/fractional/MESSAGES.md says: a yes gets a time on Justin's calendar; the base, the commission and \"is this a real person\" go to Justin.",
}
for _r in ROLES:
    if _r["name"] in FRACTIONAL:
        _r["rules"] = _r["rules"] + " " + FRACTIONAL[_r["name"]]
    _r["rules"] = _r["rules"] + " What is sold and the words for it: repo/OFFER.md. Every message drafted, sent or received is written to the conversation log (repo/CONVERSATION-LOG.md, `python3 repo/convlog/gate.py`)."
    if _r["name"] in PROCESS:
        _r["rules"] = _r["rules"] + " Process: " + PROCESS[_r["name"]] + "."


def skills_for(r):
    if r["skills"] != "*":
        return ["bot-guards"] + r["skills"]
    d = os.path.join(B, "skills", r["name"])
    return ["bot-guards"] + sorted(x for x in os.listdir(d) if os.path.isfile(os.path.join(d, x, "SKILL.md")))


def expand(field, lo, hi):
    out = set()
    for part in field.split(","):
        step = 1
        if "/" in part:
            part, step = part.split("/"); step = int(step)
        if part == "*":
            a, b = lo, hi
        elif "-" in part:
            a, b = map(int, part.split("-"))
        else:
            a = b = int(part)
        out.update(range(a, b + 1, step))
    return out


def minutes(cron):
    m, h, _, _, dow = cron.split()
    days = expand(dow, 0, 6)
    return {d * 1440 + hh * 60 + mm for d in days for hh in expand(h, 0, 23) for mm in expand(m, 0, 59)}


def check_gaps():
    allr = [(r["name"], n, c) for r in ROLES for n, c in r["sched"]]
    bad = []
    for (r1, n1, c1), (r2, n2, c2) in itertools.combinations(allr, 2):
        a, b = minutes(c1), minutes(c2)
        for x in a:
            if any(min(abs(x - y), 10080 - abs(x - y)) < 5 for y in b):
                bad.append(f"{r1}/{n1} ({c1}) vs {r2}/{n2} ({c2})"); break
    return bad


def prompt(r):
    sk = ", ".join(f"`{s}`" for s in skills_for(r))
    return f"""Role: {r['name']}.

Your job in this role: {r['job']}

Skills for this role: {sk}. Load the one whose description matches the step.

When a routine names this role, or Justin asks for this work:
1. If context/STOP exists, do nothing that reaches a person or a record, and say so once.
2. If this routine's line in context/routines-on.md is not `on` or `test`, log SKIPPED_OFF and end with [SILENT].
3. Check every person with python3 repo/guards/scripts/suppression.py check "<who>" before drafting to them. Held means stop on that person.
4. Before sending, run python3 repo/guards/scripts/send_guard.py <type> --routine "<routine name>". Anything but auto is a draft: put it in requests/justin/ and stop there. In test mode it is always a draft.
5. Before any paid call, run python3 repo/guards/scripts/spend_guard.py <plan-id> <usd> (add --pool scrape for scrape rungs and Decodo). Held means the plan and its cost go to requests/justin/; carry on with the free work.
6. Hand work to another role through requests/<role>/. Every reply from anyone goes to sales-crm; every new person for the CRM goes to sales-crm as a row in requests/sales-crm/.
7. End with python3 repo/guards/scripts/beat.py write {r['name']} '<line>' found=N drafted=N sent=N, write daily/<date>/{r['name']}.md (only what this run really did), and one line in log/runs-<YYYY-MM>.md.
8. If nothing needs Justin, end with exactly [SILENT].

Role rules: {r['rules']}"""


def charter(r):
    acc = "\n".join(f"- {a}" for a in r["accounts"]) or "None of its own: it works from files and the public web."
    rows = "\n".join(f"| {n} | `{c}` |" for n, c in r["sched"]) + "".join(f"\n| {n} | Event: {w} |" for n, w, _ in r["events"])
    sk = ", ".join(f"`{s}`" for s in skills_for(r))
    return f"""# Role charter: {r['title']}

**Folds in the old profiles:** {r['folds']}

## Job

{r['job']}

## Inputs

{r['inputs']}

## Outputs

{r['outputs']}

## Skills

{sk}. Which skill does what: [SKILLS-MAP.md](../SKILLS-MAP.md).

## Accounts it needs (names only)

{acc}

## Routines

UTC (the bot's time zone). Created paused. Each prompt starts `Role: {r['name']}.`

| Routine | Cron or trigger |
|---|---|
{rows}

## Guardrails

- {r['rules']}
- Plus every gate in [GATES.md](../GATES.md): {", ".join(STD)}.

## KPIs

{r['kpis']}

## System prompt section to paste

```
{prompt(r)}
```
"""


def trigger_sections():
    out = []
    for r in ROLES:
        out.append(f"### {r['name']}\n\n| Kind | When or what | Does | Function |\n|---|---|---|---|")
        out += [f"| Schedule | `{c}` | {n} | {agent_of(r['name'], n)} |" for n, c in r["sched"]]
        out += [f"| Event | {w} | {n}: {d} | {agent_of(r['name'], n)} |" for n, w, d in r["events"]]
        out.append("")
    return "\n".join(out)


def main():
    bad = check_gaps()
    if bad:
        print("Routines closer than 5 minutes:\n  " + "\n  ".join(bad)); raise SystemExit(1)
    os.makedirs(os.path.join(B, "roles"), exist_ok=True)
    for r in ROLES:
        open(os.path.join(B, "roles", r["name"] + ".md"), "w").write(charter(r))
    cfg = {"_doc": "Which role uses which skill and which account. Generated by tools/gen_roles.py; tools/check.py reads it. skills: role -> skill folders under skills/<role>/ ('bot-guards' means guards/). accounts: name a role charter uses -> path in the pack that serves it (or null), and key names (SIGNIN for a sign-in Justin does).",
           "skills": {r["name"]: skills_for(r) for r in ROLES},
           "accounts": {k: {"path": p, "keys": ks} for k, (p, ks) in ACCOUNTS.items()}}
    json.dump(cfg, open(os.path.join(B, "skills.json"), "w"), indent=2)
    routines = [{"role": r["name"], "routine": n, "cron": c, "function": agent_of(r["name"], n)} for r in ROLES for n, c in r["sched"]]
    routines += [{"role": r["name"], "routine": n, "event": w, "function": agent_of(r["name"], n)} for r in ROLES for n, w, _ in r["events"]]
    json.dump({"_doc": "Every routine, its role and the Revenue OS function it belongs to. Generated by tools/gen_roles.py; tools/tier.py reads it with tiers.json.", "routines": routines},
              open(os.path.join(B, "routines.json"), "w"), indent=1)
    tm = os.path.join(B, "TRIGGER-MAP.md")
    t = open(tm).read()
    head = t.split("## Every schedule and event, by role")[0]
    n_s = sum(len(r["sched"]) for r in ROLES); n_e = sum(len(r["events"]) for r in ROLES)
    runs = sum(len(minutes(c)) for r in ROLES for _, c in r["sched"])
    open(tm, "w").write(head + f"## Every schedule and event, by role\n\n{n_s} schedules and {n_e} event routines: {n_s + n_e} of the 50 a bot allows, leaving {50 - n_s - n_e} spare. No two start within 5 minutes of each other (checked by `tools/gen_roles.py`). Chat requests from Justin are not routines. Scheduled bot runs with every function on: {runs} a week; the volume work runs on the worker (WORKERS.md). The Function column is the Revenue OS function a routine belongs to (`core` runs on every tier); `python3 tools/tier.py <tier>` lists the routines a tier creates.\n\n" + trigger_sections())
    print(f"ok: {len(ROLES)} roles, {n_s} schedules + {n_e} events = {n_s + n_e} routines, {runs} scheduled bot runs a week")


if __name__ == "__main__":
    main()
