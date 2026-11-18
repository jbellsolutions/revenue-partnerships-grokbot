#!/usr/bin/env python3
"""Turns Maildoso's account CSV into the file PlusVibe's Bulk Upload takes. Justin runs this himself, on his Mac.
The fallback: push_mailboxes.py moves the same mailboxes API to API with no file.

    python3 mailbox_csv.py                  newest Maildoso CSV in ~/Downloads, to ~/Downloads/plusvibe-mailboxes.csv
    python3 mailbox_csv.py <in.csv> <plan.json> <out.csv>

Maildoso's sequencer export only takes Google mailboxes, so its SMTP mailboxes move by CSV, and that CSV holds every
mailbox password. No agent runs this or opens either file: it prints counts and column names, never a value. Only the
mailboxes in the plan go in, which keeps out the inboxes the held campaign sends from. Delete both files after the upload.
"""
import csv
import json
from pathlib import Path
import re
import sys

COLUMNS = ["first_name", "last_name", "email", "daily_limit", "username", "password", "imap_host", "imap_port", "smtp_host",
           "smtp_port", "smtp_username", "smtp_password", "tags", "min_interval", "enable_camp_rampup", "camp_rampup_start",
           "camp_rampup_increment", "enable_warmup", "warmup_daily_limit", "enable_warmup_rampup", "warmup_rampup_start",
           "warmup_rampup_increment"]
SETTINGS = {"daily_limit": 10, "min_interval": 20, "enable_camp_rampup": "yes", "camp_rampup_start": 5, "camp_rampup_increment": 1,
            "enable_warmup": "yes", "warmup_daily_limit": 50, "enable_warmup_rampup": "no"}
FOUND = {"email": ("email", "email_account", "email_address", "mailbox", "account", "address"),
         "password": ("password", "imap_password", "smtp_password", "mailbox_password"),
         "imap_host": ("imap_host", "imap_server", "imap"),
         "imap_port": ("imap_port",),
         "smtp_host": ("smtp_host", "smtp_server", "smtp"),
         "smtp_port": ("smtp_port",)}
NAMES = {"first_name": ("first_name", "firstname", "first"), "last_name": ("last_name", "lastname", "last", "surname")}
DEFAULT_PLAN = Path.home() / ".config" / "gtm-box" / "mailbox-plan.json"
DEFAULT_OUT = Path.home() / "Downloads" / "plusvibe-mailboxes.csv"


class Refused(Exception):
    """A problem to show Justin. Its text holds column names and counts only."""


def key(header):
    return re.sub(r"[^a-z0-9]+", "_", header.strip().lower()).strip("_")


def columns(headers):
    """Which of Maildoso's columns holds each thing. A file it can't read stops here, showing only the column names."""
    keys = {key(header): header for header in headers}
    found = {need: next((keys[name] for name in names if name in keys), None) for need, names in FOUND.items()}
    missing = [need for need, column in found.items() if not column]
    if missing:
        raise Refused(f"can't find {', '.join(missing)} in the file. Its columns are: {', '.join(headers)}")
    found.update({need: next((keys[name] for name in names if name in keys), None) for need, names in NAMES.items()})
    return found


def name_of(row, found, email):
    first, last = row.get(found["first_name"] or "", ""), row.get(found["last_name"] or "", "")
    if first:
        return first.strip(), last.strip()
    parts = [part for part in re.split(r"[._-]+", email.split("@")[0]) if part]
    return parts[0].title(), " ".join(parts[1:]).title()


def convert(rows, headers, planned):
    """Rows for PlusVibe, in its sample file's order, for planned mailboxes only."""
    found, out, seen = columns(headers), [], set()
    for row in rows:
        email = (row.get(found["email"]) or "").strip().lower()
        if email not in planned or email in seen:
            continue
        seen.add(email)
        first, last = name_of(row, found, email)
        out.append({**dict.fromkeys(COLUMNS, ""), **SETTINGS, "first_name": first, "last_name": last, "email": email, "username": email,
                    "password": row[found["password"]], "imap_host": row[found["imap_host"]], "imap_port": row[found["imap_port"]],
                    "smtp_host": row[found["smtp_host"]], "smtp_port": row[found["smtp_port"]]})
    return out, sorted(planned - seen)


def newest_export(folder=None):
    """The newest CSV in Downloads that has Maildoso's columns. PlusVibe's own output is skipped."""
    folder = folder or Path.home() / "Downloads"
    for path in sorted(folder.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True):
        if path.name == DEFAULT_OUT.name:
            continue
        with path.open(newline="", encoding="utf-8-sig") as handle:
            headers = next(csv.reader(handle), [])
        try:
            columns(headers)
            return path
        except Refused:
            continue
    raise Refused("no Maildoso account CSV in Downloads. In Maildoso: Email accounts, Export accounts, Download all accounts as CSV")


def run(source, plan_path, target):
    plan = json.loads(Path(plan_path).read_text())
    planned = {email.lower() for emails in plan["emails"].values() for email in emails}
    with Path(source).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    out, absent = convert(rows, reader.fieldnames or [], planned)
    target = Path(target)
    with target.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, COLUMNS)
        writer.writeheader()
        writer.writerows(out)
    target.chmod(0o600)
    print(f"{len(rows)} mailboxes in Maildoso's file, {len(out)} written, {len(rows) - len(out)} left out, {len(absent)} planned but not in the file")
    print(f"Upload this one in PlusVibe: {target}")
    print("Then delete it and Maildoso's CSV. Both hold mailbox passwords.")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        if len(argv) == 3:
            run(*argv)
        elif argv:
            raise Refused("use no arguments, or: <maildoso.csv> <plan.json> <out.csv>")
        else:
            run(newest_export(), DEFAULT_PLAN, DEFAULT_OUT)
    except Refused as problem:
        print(f"STOPPED: {problem}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
