#!/usr/bin/env python3
"""Stages move only on evidence, and only here. Ported from an earlier pipeline agent's stage_sync.py, with one rule changed.

    crm_stage.py sync [--apply]        the "Stage sync" job
    crm_stage.py move <contact> "<stage>" --type <evidence type> --ref <id or url> [--apply]

    stage            evidence that moves a card here
    Interested       a reply, a public ask, or Instantly marking them interested
    Call booked      a booking on file
    Said yes         a note a person wrote from the call
    Agreement sent   a note a person wrote saying it went out

The earlier version let any tag move a card. Here a tag with no evidence moves nothing and gets reported. A card a person dragged is
evidence that a person moved it, so it gets its tag, the way the earlier version did. The furthest stage wins. Won and lost by hand are
Justin's. This file never touches the Client Onboarding pipeline or a held record.
"""
import argparse
import datetime as dt
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crm  # noqa: E402

CANCELLED = {"cancelled", "invalid", "noshow"}
LADDER = crm.CFG["stages"]
STAGE_TAGS = crm.CFG["stage_tags"]


def reply_on_file(ref, contact_id):
    """A reply a lane handed over: it's in the reply agent's own record, not in a GoHighLevel thread."""
    path = crm.data_dir() / "replies.sqlite3"
    if not path.exists():
        return False
    db = sqlite3.connect(path)
    try:
        row = db.execute("SELECT 1 FROM replies WHERE id = ? AND contact_id = ?", (ref, contact_id)).fetchone()
    except sqlite3.OperationalError:
        return False
    return row is not None


def inbound_message(ghl, contact_id, ref):
    for conv in ghl.conversations(contact_id):
        if any(m.get("id") == ref and m.get("direction") == "inbound" for m in ghl.messages(conv["id"])):
            return True
    return False


def booking_on_file(ghl, contact, ref=""):
    """A booking that's real: an appointment that wasn't cancelled, or the booking id a booking page wrote on the contact."""
    uid = crm.field_value(contact, ghl.field_ids()["booking_uid"])
    if uid and (not ref or uid == ref):
        return f"booking {uid}"
    for event in ghl.appointments(contact["id"]):
        status = str(event.get("appointmentStatus") or event.get("status") or "").lower()
        if status not in CANCELLED and (not ref or event.get("id") == ref):
            return f"appointment {event.get('id')}"
    return ""


def person_note(ghl, contact_id, ref, word=""):
    """A note a person wrote. A note from an agent saying someone seems interested moves nothing."""
    note = next((n for n in ghl.notes(contact_id) if n.get("id") == ref), None)
    return bool(note and note.get("userId") and word in str(note.get("body") or "").lower())


def verify(ghl, contact, kind, ref):
    if kind == "reply":
        return reply_on_file(ref, contact["id"]) or inbound_message(ghl, contact["id"], ref)
    if kind == "booking":
        return bool(booking_on_file(ghl, contact, ref))
    if kind == "call-note":
        return person_note(ghl, contact["id"], ref)
    if kind == "agreement":
        return person_note(ghl, contact["id"], ref, "agreement")
    if kind == "public-ask":
        return str(ref).startswith("http")
    if kind == "instantly-interested":
        return bool(crm.field_value(contact, ghl.field_ids()["campaign"]))
    return False


def open_card(ghl, contact_id):
    return next(iter(ghl.opportunities(status="open", contact_id=contact_id)), None)


def move(ghl, contact_id, stage, kind, ref, by, lists=None):
    """One card, one stage, on proof. Returns what happened. Refuses rather than guesses."""
    if stage not in LADDER:
        raise crm.Refused(f"{stage} isn't a Sales stage")
    if kind not in crm.CFG["evidence"][stage]:
        raise crm.Refused(f"{kind} isn't evidence for {stage}")
    contact = ghl.contact(contact_id)
    lists = lists if lists is not None else crm.load_lists()
    held = crm.contact_hold(contact, ghl.field_ids(), lists)
    if held:
        raise crm.Refused(f"this contact is held ({held})")
    if not verify(ghl, contact, kind, ref):
        raise crm.Refused(f"no {kind} found for {ref}")
    pipeline, card = ghl.pipeline(), open_card(ghl, contact_id)
    if card is None:
        raise crm.Refused("no open card in Sales for this contact")
    now_at = pipeline["names"].get(card.get("pipelineStageId"), "")
    if LADDER.index(stage) <= (LADDER.index(now_at) if now_at in LADDER else -1):
        return f"already at {now_at}: the furthest stage wins"
    if not ghl.apply:
        return f"would move {now_at} to {stage} on {kind}"
    ghl.update_card(card, pipelineStageId=pipeline["stages"][stage])
    if stage in STAGE_TAGS:
        ghl.add_tags(contact_id, [STAGE_TAGS[stage]])
    ghl.note(contact_id, f"Stage: {now_at} to {stage}. Evidence: {kind} {ref}. Moved by {by}.")
    return f"moved {now_at} to {stage}"


def sync(ghl, lists=None):
    """Tags and stages say the same thing. A booking moves its card. Nobody else's records are touched."""
    pipeline, fields = ghl.pipeline(), ghl.field_ids()
    lists = lists if lists is not None else crm.load_lists()
    stats = Counter()
    report = []
    for card in ghl.opportunities(status="open"):
        contact = ghl.contact(card["contactId"])
        if crm.is_example(contact) or crm.contact_hold(contact, fields, lists):
            stats["held, left alone"] += 1
            continue
        at = pipeline["names"].get(card.get("pipelineStageId"), "")
        rank = LADDER.index(at) if at in LADDER else -1
        tags = crm.tags_of(contact)
        wanted = STAGE_TAGS.get(at)
        if wanted and wanted not in tags:
            stats["tag added for a moved card"] += 1
            if ghl.apply:
                ghl.add_tags(contact["id"], [wanted])
        booked = LADDER.index("Call booked")
        found = booking_on_file(ghl, contact) if rank < booked else ""
        if found:
            stats["moved on a booking"] += 1
            if ghl.apply:
                ghl.update_card(card, pipelineStageId=pipeline["stages"]["Call booked"])
                ghl.add_tags(contact["id"], [STAGE_TAGS["Call booked"]])
                ghl.note(contact["id"], f"Stage: {at} to Call booked. Evidence: {found}. Moved by stage sync.")
            rank = booked
        for stage, tag in STAGE_TAGS.items():
            if tag in tags and LADDER.index(stage) > rank:
                stats["tag with no evidence"] += 1
                report.append(f"{crm.display(contact)} ({contact['id']}) has {tag} but the card is at {at}. Nothing moved.")
    return dict(stats), report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync")
    s.add_argument("--apply", action="store_true")
    m = sub.add_parser("move")
    m.add_argument("contact")
    m.add_argument("stage")
    m.add_argument("--type", required=True)
    m.add_argument("--ref", required=True)
    m.add_argument("--by", default="closer")
    m.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)
    if crm.stopped():
        print("STOP is set: nothing moves.")
        return 0
    try:
        ghl = crm.client(apply=args.apply)
        if args.cmd == "move":
            print(move(ghl, args.contact, args.stage, args.type, args.ref, args.by))
        else:
            stats, report = sync(ghl)
            print(stats or "nothing to do")
            print("\n".join(report))
        print(ghl.receipt())
    except (crm.Unreachable, crm.MapError, crm.Refused) as exc:
        print(f"not done: {crm.scrub(exc)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
