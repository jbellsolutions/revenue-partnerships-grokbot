#!/usr/bin/env python3
"""The GTM box's side of the guarded sender (its own service, SENDER_URL). A draft-mode message becomes a row Justin ticks.

    sender_route.py retry      the "Sender retry" job: anything the sender missed, then where each draft stands
    sender_route.py status     counts only, never a name or an address

It can create a draft and read where it stands. It can't approve or send: box/sender_client.py holds no route for either.
The sender does the sending, on Justin's tick, into the contact's own GoHighLevel thread, so the Reply check and the sweep see
it. A draft counts as sent only when the sender says `sent`. Held, refused, test mode and unknown never count.

Three things have to be true before a row is made: SENDER_URL and SENDER_TOKEN are set, the run can write (`--apply` and
crm/WRITES_ON), and send_guard.why_no_draft says yes. Otherwise the draft stays in Justin's queue as a file, as before.
If the sender doesn't answer, the draft waits here under its idempotency key, so a retry can't make a second row.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crm  # noqa: E402
import send_guard  # noqa: E402
import sender_client  # noqa: E402
import suppression  # noqa: E402

CHANNEL = "ghl"  # With a subject, the email goes out in the contact's own thread. A ghl row with no subject is a note.
AGAIN = {429, 500, 502, 503, 504}  # The sender is busy or down: the draft waits. Anything else is its final answer.
SENT = "sent"
DONE = {SENT, "test-sent", "refused", "held", "withdrawn", "failed"}
UNFINISHED = ("new", "waiting")  # New means a run died between saving the draft and trying it.
TIMEOUT = 15


def configured():
    return bool(os.environ.get("SENDER_URL", "").strip() and os.environ.get("SENDER_TOKEN", "").strip())


def db():
    path = crm.data_dir() / "sender-drafts.sqlite3"
    conn = sqlite3.connect(path, timeout=30)
    path.chmod(0o600)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS drafts (key TEXT PRIMARY KEY, kind TEXT NOT NULL, contact_id TEXT NOT NULL,
        client TEXT NOT NULL, subject TEXT NOT NULL, body TEXT NOT NULL DEFAULT '', draft_id TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL, why TEXT NOT NULL DEFAULT '', tries INTEGER NOT NULL DEFAULT 0, added TEXT NOT NULL,
        updated TEXT NOT NULL)""")
    return conn


def key_for(kind, contact_id, body):
    """The same words to the same person are one draft, however many times a job runs."""
    return f"{kind}-{hashlib.sha256(f'{contact_id}|{body}'.encode()).hexdigest()[:32]}"


def who(contact):
    return " ".join(str(contact.get(k) or "") for k in ("email", "contactName", "companyName", "website"))


def blocked(kind, contact):
    return send_guard.why_no_draft(kind, who(contact))


def submit(conn, row):
    """One attempt. The answer updates the row, and a row that has its draft keeps no words."""
    try:
        out = sender_client.draft(row["client"], CHANNEL, f"contact:{row['contact_id']}", row["body"], bundle=row["kind"],
                                  subject=row["subject"], key=row["key"], timeout=TIMEOUT)
    except sender_client.SenderError as exc:
        reason = str((exc.payload or {}).get("reason") or (exc.payload or {}).get("error") or exc.status)
        if exc.status in AGAIN:
            state, draft_id, why = "waiting", "", reason
        else:
            state, draft_id, why = ("held" if exc.status == 409 else "refused"), "", reason
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        state, draft_id, why = "waiting", "", type(exc).__name__
    else:
        state, draft_id, why = "draft", str(out.get("id") or ""), ""
    keep = row["body"] if state == "waiting" else ""
    with conn:
        conn.execute("UPDATE drafts SET status = ?, draft_id = ?, why = ?, body = ?, tries = tries + 1, updated = ? WHERE key = ?",
                     (state, draft_id, crm.scrub(why)[:200], keep, crm.now().isoformat(), row["key"]))
    return state, why


def create(kind, contact, body):
    """Make the row, once. Returns the same shape as the queue: a status and a reason."""
    subject = crm.CFG["templates"]["subjects"].get(kind, "")
    if not subject:
        return {"status": "refused", "reason": f"{kind} has no subject, and a ghl row with no subject messages nobody"}
    conn = db()
    key = key_for(kind, contact["id"], body)
    stamp = crm.now().isoformat()
    client = str(contact.get("companyName") or crm.display(contact))
    with conn:
        fresh = conn.execute("INSERT OR IGNORE INTO drafts (key, kind, contact_id, client, subject, body, status, added, updated) "
                             "VALUES (?, ?, ?, ?, ?, ?, 'new', ?, ?)",
                             (key, kind, contact["id"], client, subject, body, stamp, stamp)).rowcount == 1
    row = conn.execute("SELECT * FROM drafts WHERE key = ?", (key,)).fetchone()
    if not fresh and row["status"] not in UNFINISHED:
        return {"status": "already", "reason": f"this draft is already {row['status']}"}
    state, why = submit(conn, row)
    return {"status": {"draft": "drafted"}.get(state, state), "reason": why}


def refresh(conn):
    """Where each draft stands now, from the sender. Nothing here decides anything."""
    changed = 0
    for row in conn.execute("SELECT * FROM drafts WHERE draft_id != ''").fetchall():
        if row["status"] in DONE:
            continue
        try:
            state = str(sender_client.status(row["draft_id"], timeout=TIMEOUT).get("status") or "unknown").strip().lower()
        except (sender_client.SenderError, urllib.error.URLError, TimeoutError, OSError, ValueError):
            continue
        if state != row["status"]:
            with conn:
                conn.execute("UPDATE drafts SET status = ?, updated = ? WHERE key = ?", (state, crm.now().isoformat(), row["key"]))
            changed += 1
    return changed


def sent_count(conn=None, day=None):
    """Only what the sender says went. A draft isn't a send, and neither is a held row or a test."""
    conn = conn or db()
    if day:
        return conn.execute("SELECT COUNT(*) FROM drafts WHERE status = ? AND updated LIKE ?", (SENT, f"{day}%")).fetchone()[0]
    return conn.execute("SELECT COUNT(*) FROM drafts WHERE status = ?", (SENT,)).fetchone()[0]


def counts(conn=None):
    conn = conn or db()
    return dict(conn.execute("SELECT status, COUNT(*) FROM drafts GROUP BY status").fetchall())


def write_state(conn):
    """For the watchdog, which holds no sender key. It reads this and raises an alarm only if the sender is really in use."""
    held = suppression.opt_outs_waiting(crm.HOME / "suppression.csv")
    target = crm.data_dir() / "sender-state.json"
    target.write_text(json.dumps({"at": crm.now().isoformat(), "configured": configured(), "opt_outs_waiting": held["count"],
                                  "opt_outs_oldest": held["oldest"], "drafts": counts(conn)}))
    target.chmod(0o600)


def retry():
    """Opt-outs first, whatever else is going on: STOP stops sending, and a person's no isn't a send. Then drafts, then status."""
    told = suppression.flush_opt_outs(crm.HOME / "suppression.csv")
    conn = db()
    done = {"opt-outs told": told}
    if configured() and not crm.stopped():
        rows = conn.execute("SELECT * FROM drafts WHERE status IN ('new', 'waiting') ORDER BY added").fetchall()
        for row in rows:
            if submit(conn, row)[0] == "waiting":
                break  # Still down. Everything left waits for the next run.
        done.update({"drafts retried": len(rows), "statuses changed": refresh(conn)})
    write_state(conn)
    return done


def status():
    held = suppression.opt_outs_waiting(crm.HOME / "suppression.csv")
    drafts = ", ".join(f"{k} {v}" for k, v in sorted(counts().items())) or "none"
    try:  # gtm-lead asks this too, and holds no sender key. The retry job's last word is what counts for it.
        known = json.loads((crm.data_dir() / "sender-state.json").read_text()).get("configured")
    except (OSError, ValueError):
        known = False
    return (f"sender {'set' if configured() or known else 'not set'}. Drafts: {drafts}. Sent, by the sender's word: {sent_count()}. "
            f"Opt-outs waiting to reach it: {held['count']}.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("retry", "status"))
    args = ap.parse_args(argv)
    print(json.dumps(retry()) if args.cmd == "retry" else status())
    return 0


if __name__ == "__main__":
    sys.exit(main())
