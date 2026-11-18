#!/usr/bin/env python3
"""The gate for podcast pitches and collaboration notes. pitch-submit stops here. Other lanes have their own rules.

For the CRM team's message types, this is the local policy for creating a draft, and nothing more: `why_no_draft`. Sending
those is the guarded sender's, on Justin's tick, and nothing here can send them or decide that they go.

    send_guard.py check <message type> "<who: show, host, email, url>"    prints ok, or blocked and why
    send_guard.py sent <message type> "<who>" --evidence <what proves it>
    send_guard.py ready                  the shows cleared to pitch right now, as JSON
    send_guard.py message <case id>      the only text that may go to that host
    send_guard.py hold <case id> "<why>" take a show out of the run and say why
    send_guard.py start <case id>        run this before a submission, so a lost answer can't lead to a second one

It says no until Justin has done all of this himself: authorized that type in his own words (its authorized field, or
the standing authorization), approved its words once (copy_approved), and said to send it on its own (mode auto). Nothing
here can change any of them, and no agent may edit guardrails.json. The box's copy comes from the Mac.

A show goes out only when it's cleared: on goal/pitch-status.json, or its draft asks Justin nothing (no line starting
"Question for Justin:" or "For Justin:"). A question in a draft that nobody answered must never reach a host.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or BOX_HOME)
sys.path.insert(0, str(HOME / "box" if (HOME / "box" / "goal.py").is_file() else HERE))

import goal  # noqa: E402
import suppression  # noqa: E402

LEDGER_KIND = {"podcast_pitch": "pitched", "collab_outreach": "collab_sent"}
DRAFT_TYPES = ("reply_book_call", "booking_confirmation", "crm_opener")  # These become rows in the sender, for Justin to tick.
# The radar's sender keeps its own caps and people rules, so these two stop here only for what the box alone knows.
GATE_ONLY = ("radar_public_reply", "radar_skool_dm")
ADDRESS = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}")
PHONE = re.compile(r"\+?\d[\d ().-]{8,}\d")


def scrub(text):
    return PHONE.sub("[number]", ADDRESS.sub("[address]", text))


def email():
    """The address for guest forms is Justin's to name. It lives in one private file, never in the pack or a note."""
    try:
        return (HOME / "goal" / "pitch-email").read_text().strip()
    except OSError:
        return ""


def phone():
    """The number guest forms use, when Justin gives one. Same rule as the address: one private file, never in the pack."""
    try:
        return (HOME / "goal" / "pitch-phone").read_text().strip()
    except OSError:
        return ""


def cleared(kind, who, kinds):
    """STOP, Justin's approval of the type, the suppression list. In this order, so the reason shown is the one he can act on."""
    if (HOME / "STOP").exists():
        return "STOP is set"
    rules = goal.read(HOME / "guardrails.json", {}) or {}
    rule = rules.get("message_types", {}).get(kind)
    if rule is None or kind not in kinds:
        return f"{kind} isn't a message type this box can send"
    if not rules.get("standing_authorization", {}).get("present") and not rule.get("authorized"):
        return "the standing authorization isn't in place"
    if not rule.get("copy_approved"):
        return f"Justin hasn't approved {kind} once"
    if rule.get("mode") != "auto":  # Approved means the words, not the sending. Going to auto is its own yes.
        return f"{kind} is approved but still set to draft"
    if kind == "podcast_pitch" and not email():
        return "Justin hasn't said which email guest forms use"
    lists = suppression.load(HOME / "suppression.csv")
    if lists is None:
        return "the suppression list is missing"
    held = lists.reason(who)
    if held:
        return f"on the suppression list ({held})"
    return None


def why_no_draft(kind, who):
    """The reason this can't become a row for Justin's tick, or None. Needs his yes on the words, and not `mode: auto`: the
    tick is the send decision, and it's his. A type he hasn't approved stays a file in his queue."""
    if (HOME / "STOP").exists():
        return "STOP is set"
    rule = (goal.read(HOME / "guardrails.json", {}) or {}).get("message_types", {}).get(kind)
    if rule is None or kind not in DRAFT_TYPES:
        return f"{kind} isn't a message type this box drafts in the sender"
    if not rule.get("copy_approved"):
        return f"Justin hasn't approved {kind} once"
    lists = suppression.load(HOME / "suppression.csv")
    if lists is None:
        return "the suppression list is missing"
    held = lists.reason(who)
    return f"on the suppression list ({held})" if held else None


def gate(kind, who):
    """The reason the radar's sender may not touch this person, or None. Reads only: its sends are logged in the radar."""
    return cleared(kind, who, GATE_ONLY)


def why_not(kind, who, day=None):
    """The reason this send can't go, or None."""
    why = cleared(kind, who, LEDGER_KIND)
    if why:
        return why
    rule = goal.read(HOME / "guardrails.json", {})["message_types"][kind]
    ledger_kind = LEDGER_KIND[kind]
    if any(e["kind"] == ledger_kind and e["who"].lower() == who.lower() for e in goal.ledger()):
        return "already sent to them"
    cap = rule.get("per_day")
    if cap is not None and goal.count(ledger_kind, day) >= cap:
        return f"today's cap of {cap} is used"
    return None


# Where the words for a host start. A form draft has no subject: the drafter heads it "Form message (paste into ...)"
# or "Pitch:". Until 2026-11-09 only "Subject:" was known, and message() crashed on every form draft.
START = re.compile(r"^(Subject:|Form message\b.*$|Pitch:\s*$)", re.M)
# Headers the drafter puts on every draft. Any other line starting "For Justin" asks him something.
HEADERS = ("For Justin's review only", "For Justin (read first")


def split(draft):
    """(notes for Justin and the submitter, the words for the host)."""
    found = START.search(draft)
    if not found:
        return draft, ""
    rest = draft[found.start():] if found.group(0).startswith("Subject:") else draft[found.end():]
    return draft[:found.start()], rest


def message(draft):
    """Subject (if any) through signature. The notes above it and the bracket lines are for Justin, never for a host."""
    body = split(draft)[1]
    return "\n".join(line for line in body.splitlines() if not line.startswith("[")).strip()


def open_question(text):
    """A line that asks Justin something only he can answer: "Question for Justin: ...", "For Justin: ...", "For Justin,
    before anything is submitted: ...". The drafter's own headers are notes for whoever submits. Until 2026-11-09 any
    "For Justin" text blocked, so every draft waited; the first fix then let "For Justin, before ..." through."""
    for line in split(text)[0].splitlines():
        line = re.sub(r"^\W+", "", line)
        if line.startswith("Question for Justin") or (line.startswith("For Justin") and not line.startswith(HEADERS)):
            return True
    return False


def holds():
    return goal.read(HOME / "goal" / "pitch-holds.json", {}) or {}


def ready(day=None):
    status = goal.read(HOME / "goal" / "pitch-status.json", {}) or {}
    cleared, held = status.get("cleared", {}), {**status.get("held", {}), **holds()}
    out = []
    for case in goal.cases():
        name = case.get("case_id")
        queued = HOME / "queue" / "podcast" / f"{name}.md"
        if case.get("qualification") != "accepted" or not queued.is_file() or name in held:
            continue
        if name not in cleared and open_question(queued.read_text()):
            continue
        if why_not("podcast_pitch", case.get("name"), day):
            continue
        out.append({"case_id": name, "who": case.get("name"), "url": (case.get("route") or {}).get("url")})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ask = sub.add_parser("check")
    ask.add_argument("kind")
    ask.add_argument("who")
    done = sub.add_parser("sent")
    done.add_argument("kind")
    done.add_argument("who")
    done.add_argument("--evidence", required=True)
    sub.add_parser("ready")
    text = sub.add_parser("message")
    text.add_argument("case_id")
    begin = sub.add_parser("start")
    begin.add_argument("case_id")
    stop = sub.add_parser("hold")
    stop.add_argument("case_id")
    stop.add_argument("why")
    args = ap.parse_args(argv)
    if args.cmd == "ready":
        print(json.dumps(ready(), indent=2))
        return 0
    if args.cmd == "message":
        path = HOME / "queue" / "podcast" / f"{Path(args.case_id).name}.md"
        if not path.is_file():
            print("refused: no such draft")
            return 1
        print(message(path.read_text()))
        return 0
    if args.cmd == "start":
        goal.write(HOME / "goal" / "pitch-holds.json",
                   {**holds(), args.case_id: f"A submission started {goal.now().isoformat()[:16]} UTC. Don't submit again."})
        print("started")
        return 0
    if args.cmd == "hold":
        goal.write(HOME / "goal" / "pitch-holds.json", {**holds(), args.case_id: scrub(args.why)})
        print("held")
        return 0
    reason = why_not(args.kind, args.who)
    if args.cmd == "check":
        print(f"blocked: {reason}" if reason else "ok")
        return 1 if reason else 0
    if reason:  # A send the gate refused must never count, whatever happened.
        print(f"refused: {reason}")
        return 1
    goal.record(LEDGER_KIND[args.kind], args.who, scrub(args.evidence))
    print("recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
