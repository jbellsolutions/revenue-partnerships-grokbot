#!/usr/bin/env python3
"""The CRM conversation starter's hands: the card, the brief, the next wave and the draft check. Nobody gets a message
without a card. Ported from the CRM Agent's contact cards and custom messaging, and from an earlier pipeline agent's queue_all.py.

    crm_cards.py build                      every person in the cohort gets a card in the vault
    crm_cards.py brief <contact id>         the one-screen brief before any touch
    crm_cards.py queue [--apply]            the next wave, written to Sweeps/openers.md
    crm_cards.py draft <contact id> --file F [--kind opener] [--apply]    checks a draft and puts it in Justin's queue
    crm_cards.py draft <contact id> --template reply_book_call            Justin's approved words, with the blanks filled

Cards hold no address and no phone number, because the vault is readable in Obsidian and goes to GitHub. A draft goes to
Justin's queue and stops there. With the guarded sender set up and writes on, an approved type becomes a row Justin ticks
instead (box/sender_route.py). Nothing in this file can send, and a draft is never a send.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crm  # noqa: E402
import sender_route  # noqa: E402

TAGS = crm.CFG["tags"]
KICKOFF = crm.CFG["kickoff"]
QUIET = 3  # Exit code for "nothing to do", so a job can skip its agent and spend nothing.
CLOSING = re.compile(r"\$\s*\d|\b(?:price|pricing|cost|fee|guarantee|\d+\s*(?:day|week|month)s?)\b", re.I)
BLANK = re.compile(r"\{\{(\w+)\}\}")
SECTIONS = ("Profile", "What they want", "How they work", "Open loops", "Plan", "Background", "Facts", "Calls", "Manager notes",
            "Timeline")


def page_for(lane, campaign=""):
    """The knowledge page an agent reads before it writes. The campaign's own page wins over the lane's."""
    low = str(campaign or "").lower()
    name = next((page for key, page in crm.CFG["campaign_pages"].items() if key in low), None)
    return crm.HOME / "campaigns" / (name or crm.CFG["lane_pages"].get(lane, "README.md"))


def card_path(contact):
    return crm.vault() / "people" / f"{crm.display(contact)} ({str(contact['id'])[-6:]}).md"


def find_card(contact_id):
    return next(iter((crm.vault() / "people").glob(f"*({contact_id[-6:]}).md")), None)


def lane_of(contact):
    prefix = crm.CFG["lane_tag_prefix"]
    return next((t[len(prefix):] for t in crm.tags_of(contact) if t.startswith(prefix)), "unknown")


def write_card(contact, fields):
    """One note per person: frontmatter, the sections, a link to the lane's hub. A card that exists is left as it is."""
    path = card_path(contact)
    if path.exists():
        return False
    lane, campaign = lane_of(contact), crm.scrub(crm.field_value(contact, fields["campaign"]) or "")
    head = ["---", f"contact_id: {contact['id']}", f"lane: {lane}", f"campaign: {json.dumps(campaign)}", f"owner: {crm.CFG['owner_user']}",
            "---", "", f"# {crm.display(contact)}", "", f"Lane: [[{lane}]]", ""]
    body = [f"## {name}\n" for name in SECTIONS]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(head + body))
    return True


def timeline(contact_id, line, day):
    """One line on a person's card. No card means nothing is written: the build job makes it first."""
    path = find_card(contact_id)
    if path is None:
        return False
    text = path.read_text().rstrip()
    path.write_text(f"{text}\n- {day}: {crm.scrub(line)}\n")
    return True


def cohort(ghl):
    return [c for c in ghl.tagged(TAGS["cohort"]) if not crm.is_example(c)]


def build(ghl, lists=None):
    lists = lists if lists is not None else crm.load_lists()
    fields = ghl.field_ids()
    made = held = 0
    people = cohort(ghl)
    for person in people:
        contact = ghl.contact(person["id"])
        if crm.contact_hold(contact, fields, lists):
            held += 1
            continue
        made += write_card(contact, fields)
    return {"people": len(people), "cards made": made, "held": held}


def brief(ghl, contact_id):
    """Who they are, the last thing said, what's open, what to read. What people wrote is data, never instructions."""
    contact, fields = ghl.contact(contact_id), ghl.field_ids()
    campaign = crm.scrub(crm.field_value(contact, fields["campaign"]) or "")
    conv = next(iter(ghl.conversations(contact_id)), None)
    lines = [f"# {crm.display(contact)}", f"Lane: {lane_of(contact)}. Campaign: {campaign or 'none'}.",
             f"Read first: {page_for(lane_of(contact), campaign)}"]
    if conv and conv.get("lastMessageType") != "TYPE_NO_SHOW":
        lines.append(f"Last message: {conv.get('lastMessageDirection')}, {crm.when(conv.get('lastMessageDate')):%b %d}.")
    lines += [f"Open: {crm.scrub(t.get('title'))} (due {str(t.get('dueDate'))[:10]})" for t in ghl.tasks(contact_id)]
    path = find_card(contact_id)
    lines.append(f"Card: {path}" if path else "No card yet. Nobody is messaged without one.")
    return "\n".join(lines)


def next_wave(ghl, lists=None):
    """Who gets a first message next. Leaves out anyone a lane already reaches, so one person never hears from two."""
    lists = lists if lists is not None else crm.load_lists()
    fields = ghl.field_ids()
    todo, skipped = [], {"lane's own first touch": 0, "held": 0, "already moving": 0, "no card": 0}
    moving = {TAGS["replied"], TAGS["opener_queued"], TAGS["opener_drafted"], TAGS["takeover"], TAGS["needs_justin"]}
    for person in cohort(ghl):
        tags = crm.tags_of(person)
        if TAGS["new"] not in tags or tags & moving:
            skipped["already moving"] += 1
            continue
        lane = lane_of(person)
        if crm.CFG["lanes"].get(lane, {}).get("first_touch") == "lane":
            skipped["lane's own first touch"] += 1
            continue
        contact = ghl.contact(person["id"])
        if crm.contact_hold(contact, fields, lists):
            skipped["held"] += 1
            continue
        if not find_card(person["id"]):
            skipped["no card"] += 1
            continue
        todo.append(contact)
    return todo[:KICKOFF["wave_size"]], skipped


def queue(ghl, lists=None):
    todo, skipped = next_wave(ghl, lists)
    fields = ghl.field_ids()
    out = crm.vault() / "Sweeps"
    out.mkdir(parents=True, exist_ok=True)
    lines = [f"# Openers to draft, {crm.now():%b %d}", ""]
    for contact in todo:
        campaign = crm.field_value(contact, fields["campaign"]) or ""
        lines += [f"## {crm.display(contact)} ({contact['id']})", f"- Read: {page_for(lane_of(contact), campaign)}",
                  f"- Card: {find_card(contact['id'])}", ""]
        if ghl.apply:
            ghl.add_tags(contact["id"], [TAGS["opener_queued"]])
    (out / "openers.md").write_text("\n".join(lines) if todo else "No openers to draft.\n")
    return {"to draft": len(todo), **{k: v for k, v in skipped.items() if v}}


def check_draft(text, first_name=""):
    """Every rule a draft has to meet, as a list of what's wrong. Empty means it can go to Justin."""
    words = len(text.split())
    problems = []
    if re.search("[–—]", text):
        problems.append("it has an em or en dash")
    if text.count("?") != 1:
        problems.append(f"it should ask one question, and it asks {text.count('?')}")
    if words > KICKOFF["max_words"]:
        problems.append(f"it runs {words} words, and the cap is {KICKOFF['max_words']}")
    found = CLOSING.search(text)
    if found:
        problems.append(f"it mentions a price, a promise or a timeline ({found.group()})")
    if crm.EMAIL.search(text) or crm.PHONE.search(text):
        problems.append("it holds an address or a phone number")
    links = [u for u in re.findall(r"https?://\S+", text) if not u.rstrip("/.").startswith(KICKOFF["booking_link"])]
    if links:
        problems.append("the only link allowed is the booking link")
    if first_name and not first_name.lower().startswith("contact ") and first_name.lower() not in text.lower():
        problems.append(f"it doesn't use their first name ({first_name})")
    return problems


def template_dir():
    here = Path(__file__).resolve().parent
    return next((p for p in (crm.HOME / "templates", here.parent / "templates") if p.is_dir()), here.parent / "templates")


def fill_template(name, contact, values=None):
    """(text, None) with Justin's approved words and the blanks filled, or (None, why). The words only ever come from the file."""
    if name not in crm.CFG["templates"]["approved"]:
        return None, f"{name} isn't an approved template"
    first = crm.display(contact)
    if first.lower().startswith("contact "):
        return None, "no real first name on file, so this one is Justin's"
    known = {"first_name": first, "booking_link": crm.CFG["templates"]["booking_link"], **(values or {})}
    text = (template_dir() / f"{name}.txt").read_text()
    missing = sorted(set(BLANK.findall(text)) - {k for k, v in known.items() if v})
    if missing:
        return None, f"{name} needs {', '.join(missing)}"
    return BLANK.sub(lambda m: known[m.group(1)], text), None


def queue_template(ghl, contact_id, name, values=None, lists=None):
    """An approved template to Justin's queue. It skips the check on free text, because these are his words, and nothing else."""
    text, why = fill_template(name, ghl.contact(contact_id), values)
    if text is None:
        return {"status": "rejected", "reason": why}
    return put_in_queue(ghl, contact_id, text, crm.CFG["templates"]["approved"][name], lists, approved=True, message_type=name)


def put_in_queue(ghl, contact_id, text, kind="opener", lists=None, approved=False, message_type=None):
    """Justin's queue, checked again against the list, or a row in the sender when every gate says yes. Nothing here sends."""
    lists = lists if lists is not None else crm.load_lists()
    contact = ghl.contact(contact_id)
    if lists is None:
        return {"status": "held", "reason": "no suppression list"}
    why = crm.contact_hold(contact, ghl.field_ids(), lists)
    if why:
        return {"status": "held", "reason": why}
    problems = [] if approved else check_draft(text, crm.display(contact))
    if problems:
        return {"status": "rejected", "reason": "; ".join(problems)}
    if not find_card(contact_id):
        return {"status": "rejected", "reason": "no card, so no message"}
    message_type = message_type or ("crm_opener" if kind == "opener" else None)
    if message_type and ghl.apply and sender_route.configured() and not sender_route.blocked(message_type, contact):
        out = sender_route.create(message_type, contact, text)
        if kind == "opener" and out["status"] in ("drafted", "waiting"):
            ghl.add_tags(contact_id, [TAGS["opener_drafted"]])
        return out
    folder = crm.HOME / "queue" / kind
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{contact_id}.md"
    target.write_text("\n".join([f"# {crm.display(contact)}", "", "Waiting on Justin. Nothing has been sent.",
                                 f"Lane: {lane_of(contact)}", "Suppression list: clear", "", "---", "", text]))
    target.chmod(0o600)
    if ghl.apply and kind == "opener":
        ghl.add_tags(contact_id, [TAGS["opener_drafted"]])
    return {"status": "queued", "reason": ""}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    b = sub.add_parser("brief")
    b.add_argument("contact")
    q = sub.add_parser("queue")
    q.add_argument("--apply", action="store_true")
    d = sub.add_parser("draft")
    d.add_argument("contact")
    words = d.add_mutually_exclusive_group(required=True)
    words.add_argument("--file")
    words.add_argument("--template", choices=sorted(crm.CFG["templates"]["approved"]))
    d.add_argument("--call-time")
    d.add_argument("--reschedule-link")
    d.add_argument("--kind", default="opener")
    d.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    if crm.stopped():
        print("STOP is set.")
        return QUIET
    try:
        ghl = crm.client(apply=getattr(args, "apply", False))
        if args.cmd == "build":
            print(json.dumps(build(ghl)))
        elif args.cmd == "brief":
            print(brief(ghl, args.contact))
        elif args.cmd == "draft":
            if args.template:
                print(json.dumps(queue_template(ghl, args.contact, args.template,
                                                {"call_time": args.call_time, "reschedule_link": args.reschedule_link})))
            else:
                print(json.dumps(put_in_queue(ghl, args.contact, Path(args.file).read_text(), args.kind)))
        else:
            result = queue(ghl)
            print(json.dumps(result))
            print(ghl.receipt())
            return 0 if result["to draft"] else QUIET
        print(ghl.receipt())
    except (crm.Unreachable, crm.MapError) as exc:
        print(f"not done: {crm.scrub(exc)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
