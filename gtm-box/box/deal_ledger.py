#!/usr/bin/env python3
"""The deal ledger: every potential and real deal, and who said what, when and how we know. Ported from an earlier deal-officer agent.

    deal_ledger.py sync          the "Deal sync" job: reads GoHighLevel, updates the ledger and Deals/ in the vault
    deal_ledger.py list          what's open, with the daily list written to Sweeps/deals.md

It reads GoHighLevel and never writes to it. The ledger is SQLite in the box's data folder, and its events are append-only:
triggers refuse every UPDATE and DELETE, so nobody can argue with the history.

What counts, the rule from the earlier deal officer: a partner who says they're interested or have deals coming is a Potential Deal, which
isn't a deal. It becomes a Deal when they bring a specific, named client. A person records that with a note on the partner's
contact that starts `DEAL:`, and the contact carries the tag gtm:deal, because GoHighLevel can't search notes across contacts.
Attribution is evidence, not a verdict. Amounts come only from the opportunity's value in GoHighLevel. This file doesn't work
out what's owed: referral terms are in channels/referrals/CONTEXT.md, and reactivation's commission is still open.
"""
import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crm  # noqa: E402

POTENTIAL, NOT_A_DEAL = "Potential Deal", "Not a Deal"
STAGES = (POTENTIAL, "Named", "Call booked", "Said yes", "Agreement sent", "Won", "Stalled", "Dead", NOT_A_DEAL)
CLOSED = {"Won", "Dead", NOT_A_DEAL}
FROM_SALES = {"Call booked": "Call booked", "Said yes": "Said yes", "Agreement sent": "Agreement sent"}
STALE_DAYS = 7
NO_CLIENT = "client not named yet"
DEAL_NOTE = re.compile(r"^DEAL:\s*(.*)", re.S | re.I)

SCHEMA = """
CREATE TABLE IF NOT EXISTS deals (id TEXT PRIMARY KEY, client TEXT NOT NULL, partner_id TEXT NOT NULL, partner TEXT NOT NULL,
    stage TEXT NOT NULL, amount REAL NOT NULL DEFAULT 0, card_id TEXT NOT NULL DEFAULT '', next_step TEXT NOT NULL DEFAULT '',
    next_due TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, deal_id TEXT NOT NULL REFERENCES deals(id), at TEXT NOT NULL,
    who TEXT NOT NULL, what TEXT NOT NULL, how TEXT NOT NULL DEFAULT '', dedupe TEXT UNIQUE);
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
"""


def connect(path=None):
    target = Path(path or crm.data_dir() / "deals.sqlite3")
    db = sqlite3.connect(target)
    target.chmod(0o600)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def stamp():
    return crm.now().isoformat(timespec="seconds")


def log(db, deal_id, who, what, how="", dedupe=None):
    """One event. `dedupe` keeps a rerun from adding it twice. True if it was added."""
    with db:
        added = db.execute("INSERT OR IGNORE INTO events (deal_id, at, who, what, how, dedupe) VALUES (?, ?, ?, ?, ?, ?)",
                           (deal_id, stamp(), crm.scrub(who), crm.scrub(what), crm.scrub(how), dedupe)).rowcount == 1
        if added:
            db.execute("UPDATE deals SET updated_at = ? WHERE id = ?", (stamp(), deal_id))
    return added


def open_deal(db, partner_id, partner, client=NO_CLIENT, stage=POTENTIAL):
    deal_id = "D" + hashlib.sha1(f"{partner_id}|{client}".encode()).hexdigest()[:7]
    with db:
        db.execute("INSERT OR IGNORE INTO deals (id, client, partner_id, partner, stage, created_at, updated_at) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?)", (deal_id, crm.scrub(client), partner_id, crm.scrub(partner), stage, stamp(), stamp()))
    return deal_id


def set_stage(db, deal_id, stage, who, why):
    """A stage change needs a reason, and leaves a line in the history. Nothing else moves a deal."""
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {', '.join(STAGES)}")
    if not str(why or "").strip():
        raise ValueError("a stage change needs a reason")
    row = db.execute("SELECT stage FROM deals WHERE id = ?", (deal_id,)).fetchone()
    if row is None:
        raise ValueError(f"no deal {deal_id}")
    if row["stage"] == stage:
        return False
    with db:
        db.execute("UPDATE deals SET stage = ?, updated_at = ? WHERE id = ?", (stage, stamp(), deal_id))
    return log(db, deal_id, who, f"Stage: {row['stage']} to {stage}", why, dedupe=f"{deal_id}:{stage}")


def is_deal(deal):
    return deal["client"] != NO_CLIENT and deal["stage"] != POTENTIAL


def sync(ghl, db=None):
    """What happened since the last run. Reads tagged contacts and their notes, and each deal's card."""
    db = db or connect()
    pipeline = ghl.pipeline()
    stats = Counter()
    for person in ghl.tagged(crm.CFG["tags"]["deal"]):
        partner_id, partner = person["id"], crm.display(person)
        named = [n for n in ghl.notes(partner_id) if DEAL_NOTE.match(str(n.get("body") or "").strip()) and n.get("userId")]
        if not named:
            deal_id = open_deal(db, partner_id, partner)
            stats["opened"] += log(db, deal_id, partner, "Tagged as bringing a deal", "the tag gtm:deal", dedupe=f"{deal_id}:tag")
        for note in named:
            client = DEAL_NOTE.match(str(note["body"]).strip()).group(1).strip().split("\n")[0][:80] or NO_CLIENT
            deal_id = open_deal(db, partner_id, partner, client, "Named")
            stats["noted"] += log(db, deal_id, partner, f"A person named the client: {client}", "a DEAL: note",
                                  dedupe=f"note:{note['id']}")
        for card in ghl.opportunities(status="all", contact_id=partner_id):
            stage = FROM_SALES.get(pipeline["names"].get(card.get("pipelineStageId"), ""))
            status = card.get("status")
            for row in db.execute("SELECT * FROM deals WHERE partner_id = ? AND stage NOT IN ('Won', 'Dead', 'Not a Deal')",
                                  (partner_id,)).fetchall():
                with db:
                    db.execute("UPDATE deals SET amount = ?, card_id = ? WHERE id = ?",
                               (float(card.get("monetaryValue") or 0), card["id"], row["id"]))
                if status == "won":
                    stats["moved"] += set_stage(db, row["id"], "Won", "GoHighLevel", "the card was marked won")
                elif status == "lost":
                    stats["moved"] += set_stage(db, row["id"], "Dead", "GoHighLevel", "the card was marked lost")
                elif stage and is_deal(dict(row)):
                    stats["moved"] += set_stage(db, row["id"], stage, "GoHighLevel", "the card moved in Sales")
    write_notes(db)
    return dict(stats)


def daily(db=None):
    """Every open deal, worst first: no next step, then gone stale. What's owed is blank until the terms are set."""
    db = db or connect()
    rows = [dict(r) for r in db.execute("SELECT * FROM deals WHERE stage NOT IN ('Won', 'Dead', 'Not a Deal') ORDER BY updated_at")]
    now = crm.now()
    lines = [f"# Deals, {now:%b %d}", ""]
    for deal in rows:
        age = (now - crm.when(deal["updated_at"])).days
        flag = "no next step" if not deal["next_step"] else f"quiet {age} days" if age >= STALE_DAYS else "moving"
        lines.append(f"- {deal['id']}: {deal['client']}, from {deal['partner']}. {deal['stage']}. {flag}. Owed: not set")
    out = crm.vault() / "Sweeps"
    out.mkdir(parents=True, exist_ok=True)
    (out / "deals.md").write_text("\n".join(lines) + "\n")
    return {"open": len(rows), "real deals": sum(is_deal(d) for d in rows)}


def write_notes(db):
    """Deals/ in the vault, rebuilt from the database. It links to the person's card and never edits it."""
    folder = crm.vault() / "Deals"
    folder.mkdir(parents=True, exist_ok=True)
    for deal in db.execute("SELECT * FROM deals").fetchall():
        events = db.execute("SELECT at, who, what, how FROM events WHERE deal_id = ? ORDER BY at, id", (deal["id"],)).fetchall()
        lines = [f"# {deal['client']} (from {deal['partner']})", "", f"Stage: {deal['stage']}", f"Partner: [[{deal['partner']} ({deal['partner_id'][-6:]})]]",
                 f"Amount: {deal['amount'] or 'not set'}", "Owed: not set", "", "## History", ""]
        lines += [f"- {e['at'][:10]} {e['who']}: {e['what']} ({e['how']})" for e in events]
        name = re.sub(r"[^\w .-]", "", f"{deal['client']} - {deal['partner']} ({deal['id']})")
        (folder / f"{name}.md").write_text("\n".join(lines) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("sync", "list"))
    args = ap.parse_args(argv)
    if args.cmd == "list":
        print(json.dumps(daily()))
        return 0
    if crm.stopped():
        print("STOP is set.")
        return 0
    try:
        ghl = crm.client()
        print(json.dumps(sync(ghl)))
        print(json.dumps(daily()))
        print(ghl.receipt())
    except (crm.Unreachable, crm.MapError) as exc:
        print(f"not done: {crm.scrub(exc)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
