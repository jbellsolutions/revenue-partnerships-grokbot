#!/usr/bin/env python3
"""Justin's daily goal: one show or video booked, one piece of content out, one collaboration agreed.

    goal.py record <kind> <who> --evidence <url or quote> [--note <text>]
    goal.py board                  the three goal lines
    goal.py report                 the evening report for Slack
    goal.py roll                   open today's research mission on the box

Justin, 2026-11-07: "booking in at least one podcast or one video, one content, one collaboration a day."

An outcome counts only with evidence, because each one ends with another person saying yes. A draft is never a booking.
The numbers come from the ledger and the files on the box, never from what an agent says it did.
"""
import argparse
import datetime as dt
import json
import math
import re
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
EASTERN = ZoneInfo("America/New_York")
OUTCOMES = {"booked": "Booked (show or video)", "published": "Content published", "collab": "Collaborations agreed"}
LEADING = {"pitched": "Pitches sent", "collab_sent": "Collaboration notes sent", "replied": "Replies"}
DEFAULTS = {"targets": {"booked": 1, "published": 1, "collab": 1},
            "quotas": {"shows": 5, "cycles": 3, "pitches": 10, "collab_notes": 3},
            "asks": []}


def now():
    return dt.datetime.now(dt.timezone.utc)


def today(when=None):
    """Justin's day, not the box's."""
    return (when or now()).astimezone(EASTERN).date().isoformat()


def read(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    scratch = path.with_suffix(path.suffix + ".tmp")
    scratch.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    os.replace(scratch, path)


def settings():
    """goal.json is what Justin set. learn.py may tune the quotas within it, and writes them to settings.json."""
    shipped = read(HOME / "goal" / "goal.json", {}) or {}
    tuned = read(HOME / "goal" / "settings.json", {}) or {}
    out = {**DEFAULTS, **shipped}
    out["quotas"] = {**DEFAULTS["quotas"], **shipped.get("quotas", {}), **tuned.get("quotas", {})}
    return out


def ledger():
    try:
        lines = (HOME / "goal" / "ledger.jsonl").read_text().splitlines()
    except FileNotFoundError:
        return []
    return [json.loads(line) for line in lines if line.strip()]


def record(kind, who, evidence="", note="", when=None):
    """True if it was added, False if it was already there. One person or show counts once for each kind."""
    if kind not in OUTCOMES and kind not in LEADING:
        raise ValueError(f"unknown kind: {kind} (use {', '.join([*OUTCOMES, *LEADING])})")
    if kind in OUTCOMES and not evidence.strip():
        raise ValueError(f"{kind} needs evidence: a link, a calendar entry or their reply")
    if any(e["kind"] == kind and e["who"].lower() == who.lower() for e in ledger()):
        return False
    when = when or now()
    event = {"at": when.isoformat(), "day": today(when), "kind": kind, "who": who, "evidence": evidence, "note": note}
    path = HOME / "goal" / "ledger.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return True


def count(kind, day=None, days=None, when=None):
    """Events of this kind today, or on the given day, or over the last `days` days."""
    events = [e for e in ledger() if e["kind"] == kind]
    if days:
        first = ((when or now()).astimezone(EASTERN).date() - dt.timedelta(days=days - 1)).isoformat()
        return sum(e["day"] >= first for e in events)
    return sum(e["day"] == (day or today(when)) for e in events)


def cases(workspace=None):
    out = []
    for path in sorted(Path(workspace or HOME / "speaker").glob("cases/*.json")):
        case = read(path)
        if case:
            out.append(case)
    return out


def made_today(folder, day):
    """Files in a queue folder written today, by Justin's clock."""
    made = 0
    for path in Path(folder).glob("*.md"):
        stamp = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc)
        made += today(stamp) == day
    return made


def supply(day=None, when=None):
    """What's on the box right now. Read from the files, so no agent can overstate it."""
    day = day or today(when)
    shows = cases()
    state = read(HOME / "goal" / f"research-{day}.json", {}) or {}
    queue = HOME / "queue"
    return {"shows": len(shows), "accepted": sum(c.get("qualification") == "accepted" for c in shows),
            "holds": sum(c.get("qualification") == "research_hold" for c in shows),
            "rejected": sum(c.get("qualification") == "rejected" for c in shows),
            "accepted_no_draft": sum(c.get("qualification") == "accepted" and not (c.get("draft") or {}).get("path")
                                     for c in shows),
            "cycles": state.get("cycles", 0), "new_shows": state.get("new_shows", 0),
            "pitches_ready": len(list((queue / "podcast").glob("*.md"))),
            "content_ready": len(list((queue / "content").glob(f"{day}*.md"))), "collab_ready": made_today(queue / "collab", day)}


def waiting(cfg=None):
    """What only Justin can unlock, read from the real gates so this list can't go stale."""
    rules = read(HOME / "guardrails.json", {}) or {}
    types = rules.get("message_types", {})
    standing = rules.get("standing_authorization", {}).get("present")
    out = []
    for name, label in (("podcast_pitch", "the podcast pitch"), ("collab_outreach", "the collaboration note")):
        rule = types.get(name, {})
        if not rule.get("copy_approved"):
            out.append(f"Approve {label} once")
        elif rule.get("mode") != "auto" or not (standing or rule.get("authorized")):
            out.append(f"Say go on {label}: the words are approved and it's still set to draft")
    if not (HOME / "goal" / "pitch-email").is_file():
        out.append("Say which email guest forms use, so pitches can go out")
    return out + list((cfg or settings()).get("asks", []))


def lines(when=None):
    cfg = settings()
    day = today(when)
    out = [f"{label}: {count(kind, day)} of {cfg['targets'].get(kind, 1)} today" for kind, label in OUTCOMES.items()]
    return out


def healed(when=None):
    """What the box fixed by itself in the last day."""
    since = (when or now()) - dt.timedelta(days=1)
    try:
        rows = [json.loads(x) for x in (HOME / "goal" / "heal.jsonl").read_text().splitlines() if x.strip()]
    except FileNotFoundError:
        return []
    return [r["what"] for r in rows if dt.datetime.fromisoformat(r["at"]) >= since]


def spend():
    day = now().date().isoformat()
    data = read(HOME / "spend" / f"{day}.json", {}) or {}
    return data.get("spent") if isinstance(data, dict) else None


def report(when=None):
    cfg = settings()
    day = today(when)
    have = supply(day, when)
    quotas = cfg["quotas"]
    head = (when or now()).astimezone(EASTERN).strftime("%A, %B %-d")
    out = [f"*Daily goal, {head}*", *lines(when), ""]
    out.append("*Getting there*")
    out.append(f"Pitches sent: {count('pitched', day)} of {quotas['pitches']}. "
               f"Collaboration notes sent: {count('collab_sent', day)} of {quotas['collab_notes']}. "
               f"Replies: {count('replied', day)}.")
    out.append(f"Pitches ready for you: {have['pitches_ready']}. Content ready for today: {have['content_ready']}. "
               f"Collaboration notes drafted today: {have['collab_ready']}.")
    out.append(f"Research: {have['cycles']} cycles, {have['new_shows']} new shows. On file: {have['shows']} shows, "
               f"{have['accepted']} accepted, {have['holds']} on hold, {have['rejected']} rejected.")
    if have["accepted_no_draft"]:
        out.append(f"Accepted shows still missing a draft: {have['accepted_no_draft']}.")
    week = [f"{label.lower()} {count(kind, days=7, when=when)}" for kind, label in OUTCOMES.items()]
    out += ["", "*Last 7 days:* " + ", ".join(week) + "."]
    fixed = healed(when)
    if fixed:
        out += ["", f"*Fixed on its own ({len(fixed)}):*", *[f"- {item}" for item in fixed[-5:]]]
    gates = waiting(cfg)
    if gates:
        out += ["", "*Waiting on you:*", *[f"- {item}" for item in gates]]
    return "\n".join(out)


def reply(who, evidence, note="", sender=None):
    """A host or creator wrote back. It's a reply, not an outcome: booked or agreed still needs the reply itself as proof,
    so Justin reads it and says. The Mac's reply_watch.py calls this; the post goes to the team's Slack channel."""
    note = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", "[address]", note)
    note = re.sub(r"\+?\d[\d ().-]{8,}\d", "[number]", note)[:300]
    if not record("replied", who, evidence, note):
        return "already on the ledger"
    if sender is None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import heal
        sender = heal.post
    sender(f"*Reply from {who}*\n> {note}\nIf it's a yes, tell me here and I'll count it (booked or agreed).")
    return "recorded and posted"


def accepted(workspace=None):
    return sum(c.get("qualification") == "accepted" for c in cases(workspace))


def roll(workspace=None, day=None, cfg=None):
    """A mission that says "find five" stops at five. This one asks for today's shows on top of what's already accepted.
    Exclusions and limits stay as Justin set them."""
    workspace = Path(workspace or HOME / "speaker")
    cfg = cfg or settings()
    path = workspace / "mission.json"
    mission = read(path)
    have = accepted(workspace)
    want = cfg["quotas"]["shows"]
    mission["accepted_target"] = have + want
    mission["as_of"] = day or today()
    mission["objective"] = (f"Keep Justin's podcast pipeline full. {have} shows are accepted so far. Add {want} more current "
                            "podcasts whose listeners include business owners, entrepreneurs or business leaders, each with "
                            "a checked booking route and a drafted pitch. Respect the exclusions. Never reconsider a rejected "
                            "show. No outreach.")
    mission["status"] = "ready"
    write(path, mission)
    return mission["accepted_target"]


def quota_from_rate(pitched, booked, floor=10, ceiling=25, least=30):
    """Pitches a day for one booking a day, once there are enough pitches to measure. Until then, the proposal."""
    if pitched < least or not booked:
        return floor
    return max(floor, min(ceiling, math.ceil(pitched / booked)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("record")
    add.add_argument("kind")
    add.add_argument("who")
    add.add_argument("--evidence", default="")
    add.add_argument("--note", default="")
    said = sub.add_parser("reply")
    said.add_argument("who")
    said.add_argument("--evidence", required=True)
    said.add_argument("--note", default="")
    sub.add_parser("board")
    sub.add_parser("report")
    sub.add_parser("roll")
    args = ap.parse_args(argv)
    if args.cmd == "record":
        try:
            added = record(args.kind, args.who, args.evidence, args.note)
        except ValueError as problem:
            print(f"refused: {problem}")
            return 1
        print("recorded" if added else "already on the ledger")
    elif args.cmd == "reply":
        print(reply(args.who, args.evidence, args.note))
    elif args.cmd == "board":
        print("\n".join(lines()))
    elif args.cmd == "report":
        print(report())
    else:
        print(f"mission target is now {roll()} accepted shows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
