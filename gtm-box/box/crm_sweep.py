#!/usr/bin/env python3
"""The no-open-loops job. NO-OPEN-LOOPS.md is the policy; this enforces it. Ported from an earlier pipeline agent's pipeline_sweep.py.

    crm_sweep.py            reads GoHighLevel, writes Sweeps/latest.md and crm/board.json, changes nothing in GoHighLevel
    crm_sweep.py --apply    the "Open loops" job: also closes repeat tasks, fills blank owners, sets missing next steps
    crm_sweep.py --count    today's cards, leads and bookings, counted in GoHighLevel, with held cards left out

Every open record lands in one bucket, worst first, with an owner, the evidence, a next action and a date. `closer` works
the list ten minutes later. A date the sweep proposes is kept, so a loop can't slide forward one sweep at a time, and
beat.py raises an alarm on anything past it.
"""
import datetime as dt
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import beat  # noqa: E402
import crm  # noqa: E402

BUCKETS = ("held", "waiting on us", "overdue", "no owner", "no evidence", "no next step", "gone quiet", "not started", "on track")
NEXT = {"held": "Justin: close this card out of Sales. Nobody works it",
        "waiting on us": "Answer them on the channel they used",
        "overdue": "Do the task, or close it and say why",
        "no owner": "Assign a named owner",
        "no evidence": "Find the evidence for this stage, or put the card back",
        "no next step": "Set one dated next step",
        "gone quiet": "One personal follow-up on what they last said",
        "not started": "Build the card and draft the opener",
        "on track": "Nothing until the next date"}
WORKER = {"held": "Justin", "waiting on us": "replies", "not started": "opener"}
TODAY = {"waiting on us"}  # The clock on a reply is the same business day. Everything else gets the next business day.
TASK_FOR = {"no owner", "no evidence", "no next step", "gone quiet"}
DEAL_NOTE = "Deal file"
MANAGED_NOTES = ("Contact memory (Obsidian)", DEAL_NOTE)
QUIET_AFTER = crm.CFG["clocks"]["quiet_business_days"]
REST = crm.CFG["clocks"]["rest_business_days"]
TAGS = crm.CFG["tags"]


def business_days(start, end):
    day, n = start.date(), 0
    while day < end.date():
        day += dt.timedelta(days=1)
        n += day.weekday() < 5
    return n


def plain(note, limit=300):
    return crm.scrub(re.sub(r"<[^>]+>|\s+", " ", str(note.get("body") or "")))[:limit]


def task_key(task):
    return re.split(r"\s*[:—]\s*", str(task.get("title") or ""))[0].strip().lower()


def repeats(tasks):
    """The tasks to close: the same title twice, and a bare "Call Pat" next to a fuller "Call Pat: book a time". The newest stays."""
    groups = defaultdict(list)
    for t in sorted(tasks, key=lambda t: str(t.get("dueDate") or t.get("dateAdded") or ""), reverse=True):
        groups[task_key(t)].append(t)
    out = []
    for rows in groups.values():
        fuller = [t for t in rows if str(t.get("title") or "").strip().lower() != task_key(t)]
        seen = set()
        for t in rows:
            title = str(t.get("title") or "").strip().lower()
            if title in seen or (fuller and t not in fuller):
                out.append(t)
            seen.add(title)
    return out


def last_message(conv):
    """(who wrote last, when). TYPE_NO_SHOW is GoHighLevel's empty thread, not a missed call, and carries no direction."""
    if not conv or conv.get("lastMessageType") == "TYPE_NO_SHOW":
        return "", None
    way = conv.get("lastMessageDirection")
    if way not in ("inbound", "outbound"):
        return "", None
    return ("them" if way == "inbound" else "us"), crm.when(conv.get("lastMessageDate"))


def evidence(card, wrote, last, notes, campaign):
    """What proves this record is where it is. A hunch in a note proves nothing, so only these count."""
    if wrote == "them":
        return f"they wrote on {last:%b %d}"
    marked = [n for n in notes if str(n.get("body") or "").startswith(("Evidence", "Stage:"))]
    if marked:
        return plain(marked[0], 120)
    if card and str(card.get("source") or "").lower() == "instantly" and campaign:
        return f"Instantly marked them interested: {campaign}"
    return ""


def lane_of(contact, card):
    for tag in crm.tags_of(contact):
        if tag.startswith(crm.CFG["lane_tag_prefix"]):
            return tag[len(crm.CFG["lane_tag_prefix"]):]
    return "instantly" if str((card or {}).get("source") or "").lower() == "instantly" else "unknown"


def bucket(rec, now):
    if rec["hold"]:
        return "held"
    due = [crm.when(t["dueDate"]) for t in rec["tasks"] if t.get("dueDate")]
    if rec["wrote"] == "them":
        return "waiting on us"
    if any(d < now for d in due):
        return "overdue"
    if rec["card"] is None and TAGS["new"] in rec["tags"] and not rec["tasks"]:
        return "not started"
    if not rec["owner"]:
        return "no owner"
    if rec["card"] and not rec["evidence"]:
        return "no evidence"
    if not rec["tasks"]:
        return "no next step"
    if rec["wrote"] == "us" and not any(d >= now for d in due) and business_days(rec["last"], now) >= QUIET_AFTER:
        return "gone quiet"
    return "on track"


def allowed(rec, now):
    """May an agent write to this person now? An answer can't wait. A follow-up can."""
    if rec["hold"]:
        return f"no, held ({rec['hold']})"
    if TAGS["takeover"] in rec["tags"]:
        return "no, Justin has this conversation: send nothing, even if they wrote last"
    if TAGS["needs_justin"] in rec["tags"]:
        return "no, this one is Justin's"
    if rec["wrote"] == "us" and business_days(rec["last"], now) < REST:
        return "no, we just wrote"
    return "yes"


def loop_db():
    path = crm.data_dir() / "loops.sqlite3"
    db = sqlite3.connect(path)
    path.chmod(0o600)
    db.execute("CREATE TABLE IF NOT EXISTS loops (contact_id TEXT PRIMARY KEY, bucket TEXT NOT NULL, due TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS seen_notes (id TEXT PRIMARY KEY, contact_id TEXT, at TEXT)")
    return db


def kept_date(db, rec, now):
    """The date this loop was given when it opened. Only a new bucket gets a new date."""
    row = db.execute("SELECT bucket, due FROM loops WHERE contact_id = ?", (rec["id"],)).fetchone()
    if row and row[0] == rec["bucket"]:
        return dt.date.fromisoformat(row[1])
    due = (now if rec["bucket"] in TODAY else crm.add_business_days(now, 1)).date()
    db.execute("INSERT OR REPLACE INTO loops VALUES (?, ?, ?)", (rec["id"], rec["bucket"], due.isoformat()))
    db.commit()
    return due


def collect(ghl, lists):
    """Everyone the team owes a move: every open Sales card, whoever made it, and everyone with the cohort tag."""
    fields = ghl.field_ids()
    everyone = ghl.search()
    cards = {}
    for card in ghl.opportunities(status="open"):
        cards.setdefault(card.get("contactId", ""), card)
    ids = {c["id"] for c in everyone if TAGS["cohort"] in crm.tags_of(c)} | set(cards)
    census = Counter()
    for c in everyone:
        if c["id"] not in ids:
            census["examples" if crm.is_example(c) else "other"] += 1
    users = ghl.users()
    records = []
    for cid in sorted(ids):
        contact = ghl.contact(cid)
        if crm.is_example(contact):
            census["examples"] += 1
            continue
        card = cards.get(cid)
        convs = ghl.conversations(cid)
        wrote, last = last_message(convs[0] if convs else None)
        notes, tasks = ghl.notes(cid), ghl.tasks(cid)
        campaign = crm.field_value(contact, fields["campaign"]) or ""
        records.append({"id": cid, "name": crm.display(contact), "contact": contact, "card": card, "tags": crm.tags_of(contact),
                        "stage": ghl.pipeline()["names"].get((card or {}).get("pipelineStageId"), "no card"),
                        "owner": users.get((card or {}).get("assignedTo") or contact.get("assignedTo")
                                           or next((t.get("assignedTo") for t in tasks if t.get("assignedTo")), "") or "", ""),
                        "lane": lane_of(contact, card), "campaign": campaign, "wrote": wrote, "last": last, "notes": notes,
                        "tasks": tasks, "hold": crm.contact_hold(contact, fields, lists),
                        "evidence": evidence(card, wrote, last, notes, campaign)})
    return records, census


def fill(records, now, db, users):
    """Give every record its four things, and say what's still only proposed."""
    for rec in records:
        rec["bucket"] = bucket(rec, now)
        due = [crm.when(t["dueDate"]) for t in rec["tasks"] if t.get("dueDate")]
        rec["action"] = NEXT[rec["bucket"]]
        if rec["bucket"] in ("overdue", "on track") and rec["tasks"]:
            rec["action"] = rec["tasks"][0].get("title") or rec["action"]
        rec["date"] = min(due).date() if due and rec["bucket"] != "held" else kept_date(db, rec, now)
        rec["past_due"] = rec["date"] < now.date()
        rec["worker"] = WORKER.get(rec["bucket"], "deals" if TAGS["deal"] in rec["tags"] else "closer")
        if rec["bucket"] == "not started" and crm.CFG["lanes"].get(rec["lane"], {}).get("first_touch") == "lane":
            rec["worker"], rec["action"] = rec["lane"], "Draft the first touch in this lane, then mark it with `crm.py add --drafted`"
        rec["allowed"] = allowed(rec, now)
        rec["fresh_notes"] = new_notes(db, rec["notes"])


def new_notes(db, notes):
    """The team's notes the agent hasn't been shown yet."""
    seen = {r[0] for r in db.execute("SELECT id FROM seen_notes")}
    return [n for n in notes if n.get("userId") and n.get("id") not in seen and n.get("title") not in MANAGED_NOTES]


def deal_file(rec, users):
    """Everything about a deal in one pinned note: the calls, the team's notes, what's still open."""
    day = lambda n: str(n.get("dateAdded") or "")[:10]  # noqa: E731
    team = [n for n in rec["notes"] if n.get("userId") and n.get("title") not in MANAGED_NOTES]
    out = [f"DEAL FILE. Stage: {rec['stage']}", "", "NOTES ON FILE"]
    out += [f"- {day(n)} {users.get(n['userId'], 'the team')}: {plain(n)}" for n in team] or ["- none yet"]
    out += ["", "FOLLOW-UPS STILL OPEN"]
    out += [f"- {t.get('title')} (due {str(t.get('dueDate'))[:10]})" for t in rec["tasks"]] or ["- none"]
    return "\n".join(out)


def fix(ghl, rec, now, owner_id, users):
    """Writes for one record. Held records aren't touched: that's Justin's call, and another writer made them."""
    if rec["hold"]:
        return Counter()
    done = Counter()
    extra = repeats(rec["tasks"])
    for t in extra:
        ghl.complete_task(rec["id"], t.get("id") or t.get("_id"))
        done["repeat tasks closed"] += 1
    rec["tasks"] = [t for t in rec["tasks"] if t not in extra]
    if rec["card"] and not rec["card"].get("assignedTo"):
        ghl.update_card(rec["card"], assignedTo=owner_id)
        rec["owner"] = users.get(owner_id, "")
        done["owners set"] += 1
    if rec["bucket"] in TASK_FOR and not rec["tasks"]:
        due = dt.datetime.combine(rec["date"], dt.time(21), dt.timezone.utc)
        if ghl.task(rec["id"], f"{rec['name']}: {rec['action']}", due, owner_id):
            done["next steps set"] += 1
    if rec["card"] and rec["stage"] != crm.CFG["stages"][0]:
        text = deal_file(rec, users)
        mine = next((n for n in rec["notes"] if n.get("title") == DEAL_NOTE), None)
        if mine is None:
            ghl.note(rec["id"], text, title=DEAL_NOTE, pinned=True)
        elif str(mine.get("body") or "").strip() != text.strip():
            ghl.update_note(rec["id"], mine["id"], text, title=DEAL_NOTE, pinned=True)
    return done


def worklist(records, now):
    rows = sorted(records, key=lambda r: (BUCKETS.index(r["bucket"]), r["name"]))
    lines = [f"# Open loops, {now:%b %d %H:%M} UTC", ""]
    if not rows:
        lines.append("No open records.")
    for r in rows:
        lines.append(f"## {r['bucket']}: {r['name']} ({r['id']})")
        card = f"Sales, {r['stage']}" if r["card"] else "no card"
        lines.append(f"- Record: {card}. Lane: {r['lane']}." + (f" Campaign: {r['campaign']}." if r["campaign"] else ""))
        lines.append(f"- Owner: {r['owner'] or 'NOBODY'}. Worked by: {r['worker']}.")
        lines.append(f"- Evidence: {r['evidence'] or 'NONE ON FILE'}")
        lines.append(f"- Next action: {r['action']}")
        lines.append(f"- Date: {r['date']}{' PAST DUE' if r['past_due'] else ''}")
        wrote = {"them": "They wrote last", "us": "We wrote last"}.get(r["wrote"], "Nothing has been said in GoHighLevel")
        stamp = f", {r['last']:%b %d}" if r["last"] else ""
        lines.append(f"- {wrote}{stamp}. Follow-up allowed now: {r['allowed']}")
        for t in r["tasks"]:
            lines.append(f"- Task {t.get('id') or t.get('_id')}: {crm.scrub(t.get('title'))} (due {str(t.get('dueDate'))[:10]})")
        for n in r["fresh_notes"]:
            lines.append(f"- New note on file: {plain(n)}")
        lines.append("")
    return "\n".join(lines)


def board(records, census, done, box, now):
    counts = Counter(r["bucket"] for r in records)
    return {"at": now.isoformat(), "open": len(records), "buckets": {b: counts[b] for b in BUCKETS if counts[b]},
            "past_due": sum(r["past_due"] for r in records), "held": counts["held"],
            "missing": {"owner": sum(not r["owner"] for r in records if r["card"]),
                        "evidence": sum(not r["evidence"] for r in records if r["card"])},
            "lanes": dict(Counter(r["lane"] for r in records)), "outside": dict(census), "done": dict(done),
            "outbox": box.counts(), "outbox_oldest_hours": round(box.oldest_hours(), 1)}


def render(b):
    lines = [f"Open records: {b['open']}"]
    lines += [f"  {name}: {count}" for name, count in b["buckets"].items()]
    lines.append(f"Past due: {b['past_due']}. Held out of the pipeline: {b['held']}.")
    lines.append(f"Cards missing an owner: {b['missing']['owner']}. Cards missing evidence: {b['missing']['evidence']}.")
    outside = ", ".join(f"{k} {v}" for k, v in sorted(b["outside"].items())) or "none"
    lines.append(f"Contacts outside the loops: {outside}.")
    lines.append("Outbox: " + (", ".join(f"{k} {v}" for k, v in sorted(b["outbox"].items())) or "empty") + ".")
    if b["done"]:
        lines.append("This sweep: " + ", ".join(f"{k} {v}" for k, v in sorted(b["done"].items())) + ".")
    return "\n".join(lines)


def sweep(ghl, lists=None, box=None, when=None):
    now = when or crm.now()
    lists = lists if lists is not None else crm.load_lists()
    box = box or crm.Outbox()
    db = loop_db()
    users = ghl.users()
    records, census = collect(ghl, lists)
    fill(records, now, db, users)
    done = Counter()
    if ghl.apply and not crm.stopped():
        owner_id = ghl.owner()
        for rec in records:
            done += fix(ghl, rec, now, owner_id, users)
        for rec in records:
            rec["bucket"] = bucket(rec, now)
    out = crm.vault() / "Sweeps"
    out.mkdir(parents=True, exist_ok=True)
    (out / "latest.md").write_text(worklist(records, now))
    result = board(records, census, done, box, now)
    target = crm.data_dir() / "board.json"
    target.write_text(json.dumps(result, indent=1))
    target.chmod(0o600)
    for rec in records:
        db.executemany("INSERT OR IGNORE INTO seen_notes VALUES (?, ?, ?)",
                       [(n["id"], rec["id"], now.isoformat()) for n in rec["fresh_notes"]])
    db.commit()
    return result


def counts(ghl, lists=None, when=None):
    """Today's numbers from GoHighLevel itself, for the daily close and the proof audit. A held card never counts."""
    lists = lists if lists is not None else crm.load_lists()
    day, fields, pipeline = (when or crm.now()).date().isoformat(), ghl.field_ids(), ghl.pipeline()
    out = Counter(cards=0, leads=0, booked=0, held=0)
    for card in ghl.opportunities(status="open"):
        if crm.contact_hold(ghl.contact(card["contactId"]), fields, lists):
            out["held"] += 1
            continue
        out["cards"] += 1
        out["leads"] += str(card.get("createdAt") or "").startswith(day)
        booked = pipeline["names"].get(card.get("pipelineStageId")) == "Call booked"
        out["booked"] += booked and str(card.get("lastStageChangeAt") or "").startswith(day)
    return dict(out)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    beat.HOME = crm.HOME
    try:
        ghl = crm.client(apply="--apply" in argv)
        if "--count" in argv:
            print(json.dumps(counts(ghl)))
            print(ghl.receipt())
            return 0
        result = sweep(ghl)
    except (crm.Unreachable, crm.MapError) as exc:
        line = f"open loops blocked: {crm.scrub(exc)}"
        print(line)
        beat.write("closer", line, ["blocked=1"])
        return 1
    print(render(result))
    print(ghl.receipt())
    read = result["open"] + sum(result["outside"].values())  # What it read, so an empty pipeline isn't an idle job.
    beat.write("closer", f"open loops: {result['open']} open, {result['past_due']} past due, {result['held']} held",
               [f"found={read}", f"overdue={result['past_due']}"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
