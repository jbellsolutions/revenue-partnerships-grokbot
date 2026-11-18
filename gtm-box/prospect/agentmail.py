#!/usr/bin/env python3
"""AgentMail, for threads someone else started. Its terms (section 8(h)) forbid cold outreach, including one-to-one email
an LLM wrote, so nothing here can write first or to anyone new.

    agentmail.py inboxes                         each inbox: address and display name
    agentmail.py threads [--inbox ID] [--limit 20]    recent threads: who wrote, subject, how many messages
    agentmail.py read <inbox> <message id>       the new text of one message, without the quoted history
    agentmail.py reply <inbox> <message id> --text-file F    answers that message, and only if they wrote it to us
    agentmail.py block <email> "<why>"           an opt-out: AgentMail rejects every later send to them, from every inbox

AGENTMAIL_API_KEY comes from box.env. A reply carries a plain opt-out line, as AgentMail's terms ask, and is refused under
STOP, for anyone on the suppression list, and for any message our own inbox sent.
"""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.agentmail.to/v0"
BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
ADDRESS = re.compile(r"[\w.+%-]+@[\w-]+(?:\.[\w-]+)+")
OPT_OUT = "\n\nIf you'd rather I didn't write again, just say so."


class Blocked(Exception):
    pass


def key():
    value = os.environ.get("AGENTMAIL_API_KEY", "").strip()
    if not value:
        raise Blocked("AGENTMAIL_API_KEY isn't set on this computer. Justin adds it with add-secret.")
    return value


def call(method, path, query=None, body=None, opener=urllib.request.urlopen, tries=3):
    url = API + path + ("?" + urllib.parse.urlencode({k: v for k, v in (query or {}).items() if v is not None}) if query else "")
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(tries):
        request = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": f"Bearer {key()}", "Content-Type": "application/json", "User-Agent": "gtm-box/1.0"})
        try:
            with opener(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 429 and attempt + 1 < tries:
                time.sleep(float(error.headers.get("Retry-After") or 1))
                continue
            said = ADDRESS.sub("<address>", error.read()[:300].decode(errors="ignore"))
            raise Blocked(f"AgentMail said {error.code} on {path}: {said}")
    raise Blocked(f"AgentMail kept saying 429 on {path}")


def address(text):
    found = ADDRESS.search(text or "")
    return found.group(0).lower() if found else ""


def inboxes(opener=urllib.request.urlopen):
    rows = call("GET", "/inboxes", {"limit": 100}, opener=opener).get("inboxes") or []
    return [{"inbox_id": row.get("inbox_id"), "email": row.get("email"), "display_name": row.get("display_name")} for row in rows]


def threads(inbox=None, limit=20, opener=urllib.request.urlopen):
    path = f"/inboxes/{urllib.parse.quote(inbox)}/threads" if inbox else "/threads"
    rows = call("GET", path, {"limit": limit}, opener=opener).get("threads") or []
    return [{"inbox_id": row.get("inbox_id"), "thread_id": row.get("thread_id"), "subject": row.get("subject"), "senders": row.get("senders"),
             "messages": row.get("message_count"), "last_message_id": row.get("last_message_id"), "labels": row.get("labels")} for row in rows]


def message(inbox, message_id, opener=urllib.request.urlopen):
    return call("GET", f"/inboxes/{urllib.parse.quote(inbox)}/messages/{urllib.parse.quote(message_id)}", opener=opener)


def suppressed(who):
    for folder in (HOME / "box", Path(__file__).resolve().parent.parent / "box"):
        sys.path.insert(0, str(folder))
    try:
        import suppression
    except ImportError:
        return "no suppression check on this computer"
    lists = suppression.load(HOME / "suppression.csv")
    return "the suppression list is missing" if lists is None else lists.reason(who)


def why_not_reply(inbox, found):
    """Why this message can't be answered, or None. They must have written it, to this inbox, and not be held."""
    if (HOME / "STOP").exists():
        return "STOP is set"
    labels = {str(label).lower() for label in found.get("labels") or []}
    sender = address(found.get("from"))
    own = address(inbox) if "@" in inbox else ""
    if "sent" in labels or "received" not in labels or not sender or sender == own:
        return "we didn't receive this message, so a reply would be us writing first"
    held = suppressed(sender)
    return f"they're on the suppression list ({held})" if held else None


def reply(inbox, message_id, text, opener=urllib.request.urlopen):
    found = message(inbox, message_id, opener)
    why = why_not_reply(inbox, found)
    if why:
        raise Blocked(why)
    body = text.rstrip() + OPT_OUT
    sent = call("POST", f"/inboxes/{urllib.parse.quote(inbox)}/messages/{urllib.parse.quote(message_id)}/reply", body={"text": body}, opener=opener)
    return {"replied": True, "message_id": sent.get("message_id"), "thread_id": sent.get("thread_id")}


def block(email, why, opener=urllib.request.urlopen):
    call("POST", "/lists/send/block", body={"entry": email.strip().lower(), "reason": why}, opener=opener)
    return {"blocked": True}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("inboxes")
    t = sub.add_parser("threads")
    t.add_argument("--inbox")
    t.add_argument("--limit", type=int, default=20)
    r = sub.add_parser("read")
    r.add_argument("inbox")
    r.add_argument("message_id")
    y = sub.add_parser("reply")
    y.add_argument("inbox")
    y.add_argument("message_id")
    y.add_argument("--text-file", required=True)
    b = sub.add_parser("block")
    b.add_argument("email")
    b.add_argument("why")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "inboxes":
            out = inboxes()
        elif a.cmd == "threads":
            out = threads(a.inbox, a.limit)
        elif a.cmd == "read":
            found = message(a.inbox, a.message_id)
            out = {"from": found.get("from"), "subject": found.get("subject"), "labels": found.get("labels"),
                   "text": found.get("extracted_text") or found.get("text")}
        elif a.cmd == "reply":
            out = reply(a.inbox, a.message_id, Path(a.text_file).read_text())
        else:
            out = block(a.email, a.why)
    except Blocked as error:
        print(json.dumps({"blocked": str(error)}))
        return 2
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
