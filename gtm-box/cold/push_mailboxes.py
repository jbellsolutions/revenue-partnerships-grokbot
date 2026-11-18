#!/usr/bin/env python3
"""Moves the planned Maildoso mailboxes into PlusVibe by API. Justin runs the push himself, on his Mac.

    python3 push_mailboxes.py check    counts only: planned, in Maildoso, already in PlusVibe, still to add. Keeps no password
    python3 push_mailboxes.py          adds the planned mailboxes PlusVibe doesn't have yet, 100 a call, then waits for them
    either one, then a plan file       a client's plan instead of ~/.config/gtm-box/mailbox-plan.json

Maildoso's one-click sync to a sequencer skips SMTP mailboxes, so the only way across carries each mailbox's password.
The push reads them from Maildoso's API into memory and sends them straight to PlusVibe: no file, and it prints counts
only. An agent may run `check`, never the push. Only the plan's mailboxes go in, and the held campaign's live senders are
read again from Instantly and held back. Mailboxes arrive with warmup off, so they never warm in two tools at once:
warmup.py instantly-off and warmup.py apply take it from there. Running it again is safe: PlusVibe's mailboxes are skipped.
Each run leaves ~/.config/gtm-box/push-last.json (time, step, counts, PlusVibe's answer, never an address or password),
so Claude can see whether a push ran and how far it got without reading the terminal.
"""
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from mailbox_csv import DEFAULT_PLAN, SETTINGS  # noqa: E402

ENV = Path.home() / ".config" / "gtm-box" / "box.env"
LAST = Path.home() / ".config" / "gtm-box" / "push-last.json"
MAILDOSO = "https://api.maildoso.com"
PLUSVIBE = "https://api.plusvibe.ai/api/v1"
INSTANTLY = "https://api.instantly.ai/api/v2"
BATCH = 100
ADD = {**SETTINGS, "enable_warmup": "no"}


class Refused(Exception):
    """A problem to show Justin. Its text holds counts, paths and status codes only."""


def env(name, path=ENV, needed=True):
    for line in path.read_text().splitlines() if path.is_file() else []:
        if line.startswith(name + "="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            if value:
                return value
    if needed:
        raise Refused(f"{name} isn't in {path}")
    return ""


def http(method, url, headers, body=None, opener=urllib.request.urlopen):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method,
                                     headers={**headers, "Content-Type": "application/json", "User-Agent": "gtm-box/1.0"})
    try:
        with opener(request, timeout=120) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise Refused(f"{method} {url.split('?')[0]} came back {error.code}")  # its body can repeat what was sent


def mailboxes(get, keep_password):
    """Every Maildoso mailbox. `check` drops each password as the page arrives."""
    out, offset = [], 0
    while True:
        page = get(f"/v1/user/accounts-lookup?limit=200&offset={offset}")
        for row in page["items"]:
            item = {key: row.get(key) for key in ("email_account", "first_name", "last_name", "imap", "smtp")}
            item["has_password"] = bool(row.get("password"))
            if keep_password:
                item["password"] = row.get("password")
            out.append(item)
        offset += 200
        if offset >= page["meta"]["total"]:
            return out


def in_plusvibe(get):
    out, skip = set(), 0
    while True:
        page = get(skip).get("accounts") or []
        out |= {(row.get("email") or "").lower() for row in page}
        if len(page) < 100:
            return out - {""}
        skip += 100


def names(row, email):
    parts = [part.title() for part in email.split("@")[0].replace("-", ".").replace("_", ".").split(".") if part]
    first = (row.get("first_name") or "").strip() or (parts[0] if parts else "Team")
    last = (row.get("last_name") or "").strip() or " ".join(parts[1:]) or first
    return first, last


def ready_to_add(row):
    return bool(row.get("has_password") and (row.get("imap") or {}).get("imap_host") and (row.get("smtp") or {}).get("smtp_host"))


def account(row):
    """PlusVibe's bulk-add body for one mailbox, or None when Maildoso gave no password or host."""
    email = row["email_account"].strip().lower()
    imap, smtp = row.get("imap") or {}, row.get("smtp") or {}
    if not (row.get("password") and imap.get("imap_host") and smtp.get("smtp_host")):
        return None
    first, last = names(row, email)
    return {**ADD, "first_name": first, "last_name": last, "email": email, "username": email, "password": row["password"],
            "imap_host": imap["imap_host"], "imap_port": int(imap.get("port") or 993), "smtp_host": smtp["smtp_host"],
            "smtp_username": email, "smtp_password": row["password"], "smtp_port": int(smtp.get("port") or 587)}


def answer(reply, secrets):
    """PlusVibe's status and message, cut short, with any password from the batch blanked out."""
    reply = reply if isinstance(reply, dict) else {"status": type(reply).__name__}
    status, message = str(reply.get("status") or ""), str(reply.get("message") or reply.get("error") or "")[:300]
    for secret in secrets:
        if secret:
            message = message.replace(secret, "***")
    return status, message


def run(push, planned, held, maildoso_get, plusvibe_list, plusvibe_add, workspace, say=print, sleep=time.sleep, polls=30,
        note=lambda **fields: None):
    overlap = planned & held
    planned = planned - held
    rows = {row["email_account"].strip().lower(): row for row in mailboxes(maildoso_get, keep_password=push)}
    have = in_plusvibe(plusvibe_list)
    todo = [rows[email] for email in sorted(planned & set(rows)) if email not in have]
    ready = [row for row in todo if ready_to_add(row)]
    say(json.dumps({"planned": len(planned), "held_campaign_senders_dropped": len(overlap), "in_maildoso": len(planned & set(rows)),
                    "already_in_plusvibe": len(planned & have), "to_add": len(todo), "ready": len(ready),
                    "missing_from_maildoso": len(planned - set(rows)),
                    "smtp": sorted({f"{(row.get('smtp') or {}).get('smtp_host')}:{(row.get('smtp') or {}).get('port')}" for row in todo}),
                    "imap_ports": sorted({str((row.get("imap") or {}).get("port")) for row in todo}),
                    "imap_hosts": len({(row.get("imap") or {}).get("imap_host") for row in todo})}))
    note(step="counted", push=push, planned=len(planned), already_in_plusvibe=len(planned & have), to_add=len(todo), ready=len(ready))
    if not push or not todo:
        return 0
    bodies = [body for body in map(account, todo) if body]
    if len(bodies) < len(todo):
        say(f"{len(todo) - len(bodies)} mailboxes had no password or host in Maildoso and were left out")
    answers = []
    for start in range(0, len(bodies), BATCH):
        batch = bodies[start:start + BATCH]
        status, message = answer(plusvibe_add({"workspace_id": workspace, "accounts": batch}), [row["password"] for row in batch])
        answers.append(status)
        if status != "success":
            say(f"PlusVibe didn't accept the batch at {start}: status {status or 'blank'}. {message}".strip())
            note(step="refused", sent=start, of=len(bodies), status=status, message=message)
            return 1
        say(f"sent {start + len(batch)} of {len(bodies)}")
        note(step="sending", sent=start + len(batch), of=len(bodies), answers=answers)
    del bodies, todo, rows, batch
    for _ in range(polls):
        sleep(30)
        count = len(planned & in_plusvibe(plusvibe_list))
        say(f"PlusVibe has {count} of {len(planned)}")
        note(step="waiting", in_plusvibe=count, planned=len(planned))
        if count >= len(planned):
            break
    count = len(planned & in_plusvibe(plusvibe_list))
    if count < len(planned):
        say(f"{len(planned) - count} not in yet. PlusVibe emails the upload result to its account address; run this again to retry them.")
        note(step="short", in_plusvibe=count, planned=len(planned))
        return 1
    say("All planned mailboxes are in PlusVibe, with warmup off. Tell Claude: the inboxes are in.")
    note(step="done", in_plusvibe=count, planned=len(planned))
    return 0


def held_senders():
    """The held campaign's live senders, read again so one added since the plan was made still stays out. A failed read stops
    the push. A client's setup holds nothing back: new_client.py sets INSTANTLY_HELD_CAMPAIGN to none."""
    campaign = env("INSTANTLY_HELD_CAMPAIGN", needed=False) or os.environ.get("INSTANTLY_HELD_CAMPAIGN", "").strip()
    if not campaign:
        raise Refused("INSTANTLY_HELD_CAMPAIGN isn't set (the held campaign's id, or none). Set it at intake.")
    if campaign == "none":
        return set()
    found = http("GET", f"{INSTANTLY}/campaigns/{campaign}", {"Authorization": f"Bearer {env('INSTANTLY_API_KEY')}"})
    return {address.lower() for address in found.get("email_list", [])}


def recorder(path=LAST):
    """Writes the run's latest step over the last one. Counts and statuses only."""
    started, kept = datetime.now(timezone.utc).isoformat(timespec="seconds"), {}

    def note(**fields):
        kept.update({key: fields[key] for key in ("push",) if key in fields})  # every step says whether it was a push
        try:
            path.write_text(json.dumps({"started": started, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), **kept, **fields}))
        except OSError:
            pass
    return note


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    push = argv[:1] != ["check"]
    rest = argv if push else argv[1:]
    if len(rest) > 1 or rest[:1] and rest[0].startswith("-"):
        print(__doc__)
        return 1
    try:
        plan = json.loads(Path(rest[0] if rest else DEFAULT_PLAN).read_text())
        planned = {email.lower() for emails in plan["emails"].values() for email in emails}
        md = {"Authorization": f"Bearer {env('MAILDOSO_API_KEY')}"}
        pv = {"x-api-key": env("PLUSVIBE_API_KEY")}
        workspace = env("PLUSVIBE_WORKSPACE_ID")
        note = recorder()
        note(step="started", push=push)
        held = held_senders()
        return run(push=push, planned=planned, held=held, workspace=workspace, note=note,
                   maildoso_get=lambda path: http("GET", MAILDOSO + path, md),
                   plusvibe_list=lambda skip: http("GET", f"{PLUSVIBE}/account/list?workspace_id={workspace}&skip={skip}&limit=100", pv),
                   plusvibe_add=lambda body: http("POST", f"{PLUSVIBE}/account/bulk-add-regular-accounts", pv, body))
    except Refused as problem:
        print(f"STOPPED: {problem}")
        recorder()(step="stopped", push=push, reason=str(problem))
        return 1
    except OSError as problem:
        print(f"STOPPED: can't read {problem.filename}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
