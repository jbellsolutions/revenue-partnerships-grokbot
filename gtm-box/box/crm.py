#!/usr/bin/env python3
"""The one CRM writer. Every lane hands its people to this file, and nothing else on the box writes to GoHighLevel.

    crm.py add --lane podcast --name "Pat Doe" --email p@x.test --campaign "Podcast" [--apply]
    crm.py drain [--apply]        the closer's job: put what's queued into GoHighLevel
    crm.py drain --only p@x.test [--apply]   one person's rows only, so a tester goes in before the backlog
    crm.py status                 counts only, never a name or an address

The file crm/DRAIN_HOLD holds the backlog back: a plain drain does nothing while it's there, and `--only` still runs.

Lanes hold no GoHighLevel key. `add --apply` runs the suppression check, then writes the lead to a durable outbox in the
box's data folder. Only `drain` touches GoHighLevel, so a lead survives GoHighLevel being down, and the key stays on the
CRM profiles.

Two things have to be true before anything is written: the command says `--apply`, and Justin has turned writes on with
the file crm/WRITES_ON. STOP beats both. Without them every command reads and reports. There is no way to send a message
from this file: conversations and workflows aren't on the write list.
"""
import argparse
import collections
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suppression  # noqa: E402

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")  # Fixed on the box: a profile's shell may not see GTM_HOME or the real home folder.
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
API = "https://services.leadconnectorhq.com"
VERSION = "2021-07-28"
CONVERSATIONS_VERSION = "2021-04-15"
_ID = r"[A-Za-z0-9]{10,40}"
READ_POSTS = {"/contacts/search"}
# Everything that writes. Nothing here can message a person: no /conversations and no /workflow.
WRITES = [("POST", re.compile(r"^/contacts/$")), ("PUT", re.compile(rf"^/contacts/{_ID}$")),
          ("POST", re.compile(rf"^/contacts/{_ID}/tags$")), ("DELETE", re.compile(rf"^/contacts/{_ID}/tags$")),
          ("POST", re.compile(rf"^/contacts/{_ID}/notes$")), ("PUT", re.compile(rf"^/contacts/{_ID}/notes/{_ID}$")),
          ("POST", re.compile(rf"^/contacts/{_ID}/tasks$")), ("PUT", re.compile(rf"^/contacts/{_ID}/tasks/{_ID}$")),
          ("PUT", re.compile(rf"^/contacts/{_ID}/tasks/{_ID}/completed$")),
          ("POST", re.compile(r"^/opportunities/$")), ("PUT", re.compile(rf"^/opportunities/{_ID}$"))]
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")  # Never goes in the CRM. A note holding one is refused, not cleaned.
ACCOUNT = re.compile(r"\d{9,}")
EMAIL = re.compile(r"[\w.+%-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"\+?\d[\d\s().-]{8,}\d")
OPEN_OR_LOST = {"open", "lost"}  # Won is Justin's, and abandoned hides a card someone else may still own.


class Refused(PermissionError):
    """This file won't do that."""


class Unreachable(RuntimeError):
    """GoHighLevel didn't answer, or the location or key isn't working. Try again later: nothing is lost."""


class GhlError(RuntimeError):
    """GoHighLevel answered and said no."""


class MapError(RuntimeError):
    """The live location doesn't match crm-map.json, so stop instead of writing to the wrong place."""


_ENV_REF = re.compile(r"^<([A-Z][A-Z0-9_]*)>$")


def _resolve(value):
    """crm-map.json keeps private values out of the repo: a string "<NAME>" is read from the environment or box.env (set at intake).
    An unset name becomes "", and every check that uses it then refuses instead of matching."""
    if isinstance(value, dict):
        return {key: _resolve(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve(item) for item in value]
    if isinstance(value, str):
        match = _ENV_REF.match(value)
        if match:
            return _setting(match.group(1))
    return value


def _setting(name):
    """The environment first, then the box's own box.env (NAME=value lines), so a value set at intake reaches every run."""
    value = os.environ.get(name, "").strip()
    path = HOME / "box.env"
    if not value and path.is_file():
        for line in path.read_text().splitlines():
            if line.startswith(name + "="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
    return value


def load_map():
    here = Path(__file__).resolve().parent
    for path in (here / "crm-map.json", here.parent / "crm-map.json"):
        if path.is_file():
            cfg = _resolve(json.loads(path.read_text()))
            private = HOME / "campaigns" / "campaign-pages.json"  # real campaign names, given at intake
            if private.is_file():
                cfg["campaign_pages"] = {**cfg.get("campaign_pages", {}), **json.loads(private.read_text())}
            return cfg
    raise MapError("crm-map.json is missing")


CFG = load_map()


def stopped():
    return (HOME / "STOP").exists()


def writes_on():
    return (HOME / "crm" / "WRITES_ON").exists()


def backlog_held():
    return (HOME / "crm" / "DRAIN_HOLD").exists()


def data_dir():
    path = HOME / "crm"
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def vault():
    """The Obsidian vault on the box. People, sweeps and deals. Never an address or a phone number."""
    return Path(os.environ.get("GTM_VAULT") or HOME / "vault" / "projects" / "our-aios" / "gtm-box")


def scrub(text):
    """What leaves this file for a note, a heartbeat or a log. No address or phone number."""
    text = SSN.sub("[number]", EMAIL.sub("[email]", str(text or "")))
    return ACCOUNT.sub("[number]", PHONE.sub("[phone]", text)).strip()


def now():
    return dt.datetime.now(dt.timezone.utc)


def add_business_days(start, n):
    day = start
    while n > 0:
        day += dt.timedelta(days=1)
        n -= day.weekday() < 5
    return day


def when(value):
    """GoHighLevel dates are ISO strings or epoch milliseconds, sometimes as a string."""
    if value in (None, ""):
        return None
    text = str(value)
    if text.isdigit():
        return dt.datetime.fromtimestamp(int(text) / 1000, dt.timezone.utc)
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))


def real_name(value):
    """Live contacts from Instantly have their email address as their name. That isn't a name."""
    text = str(value or "").strip()
    return "" if not text or "@" in text else text


def display(contact):
    """First names only, and never an address. Anyone without a real first name is shown by their id."""
    first = real_name(contact.get("firstName")) or real_name(contact.get("contactName")).split(" ")[0]
    return first.title() if first else f"contact {str(contact.get('id'))[-6:]}"


def is_example(contact):
    return "(example)" in str(contact.get("contactName") or contact.get("firstName") or "").lower()


def tags_of(contact):
    return {str(t).lower() for t in contact.get("tags") or []}


def http_transport(token):
    def send(method, path, params, body, version):
        url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Version", version)
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "gtm-box-crm/1")  # GoHighLevel's Cloudflare rejects Python's default agent.
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, json.loads(resp.read() or b"null")
        except urllib.error.HTTPError as exc:
            return exc.code, {"detail": exc.read().decode(errors="replace")[:300]}
    return send


class Ghl:
    """One way in, closed by default. Reads pass. A write needs the allowlist, apply, and no STOP."""

    def __init__(self, token, location, apply=False, transport=None, pause=time.sleep):
        if not CFG["location"]:
            raise Refused("GHL_LOCATION_ID isn't set, so no location is trusted")
        if location != CFG["location"]:
            raise Refused("that isn't the Revenue Partners location")
        self.location = location
        self.apply = apply
        self.send = transport or http_transport(token)
        self.pause = pause
        self.counts = collections.Counter()
        self._pipeline = self._fields = self._owner = None

    def receipt(self):
        return f"GoHighLevel requests: {self.counts['read']} reads, {self.counts['write']} writes, {self.counts['refused']} refused"

    def _allowed(self, method, path):
        if method == "GET" or (method == "POST" and path in READ_POSTS):
            self.counts["read"] += 1
            return
        if not any(method == m and rx.match(path) for m, rx in WRITES):
            self.counts["refused"] += 1
            raise Refused(f"{method} {path} isn't on the write list")
        if not self.apply:
            self.counts["refused"] += 1
            raise Refused(f"{method} {path}: this run is read-only")
        if stopped():
            self.counts["refused"] += 1
            raise Refused("STOP is set")
        self.counts["write"] += 1

    def call(self, method, path, body=None, version=VERSION, **params):
        self._allowed(method, path)
        problem = "no answer"
        for attempt in range(5):
            try:
                status, data = self.send(method, path, params, body, version)
            except (OSError, ValueError) as exc:  # URLError and timeouts are OSErrors. A bad body is a ValueError.
                problem = str(exc)[:200]
            else:
                if status < 300:
                    return data
                detail = str((data or {}).get("detail") or (data or {}).get("message") or data)[:200]
                if status in (401, 403):
                    raise Unreachable(f"{status}: {detail}")  # A dead key or inactive location: keep the leads queued.
                if status not in (429, 500, 502, 503, 504):
                    raise GhlError(f"{method} {path} -> {status}: {detail}")
                problem = f"{status}: {detail}"
            if attempt < 4:
                self.pause(2 ** attempt)
        raise Unreachable(problem)

    # --- what's in the location -----------------------------------------------------------------------------------------

    def pipeline(self):
        """The Sales pipeline by name, every run. A renamed stage stops the job instead of writing to the wrong card."""
        if self._pipeline is None:
            rows = self.call("GET", "/opportunities/pipelines", locationId=self.location).get("pipelines", [])
            found = [p for p in rows if p.get("name") == CFG["pipeline"]]
            if len(found) != 1:
                raise MapError(f"expected one pipeline named {CFG['pipeline']}, found {len(found)}")
            stages = {s["name"]: s["id"] for s in found[0].get("stages", [])}
            missing = [s for s in CFG["stages"] if s not in stages]
            if missing:
                raise MapError(f"stages missing from {CFG['pipeline']}: {', '.join(missing)}")
            self._pipeline = {"id": found[0]["id"], "stages": stages, "names": {v: k for k, v in stages.items()}}
        return self._pipeline

    def field_ids(self):
        if self._fields is None:
            rows = self.call("GET", f"/locations/{self.location}/customFields").get("customFields", [])
            keys = {f.get("fieldKey"): f["id"] for f in rows}
            missing = [k for k in CFG["fields"].values() if k not in keys]
            if missing:
                raise MapError(f"custom fields missing: {', '.join(missing)}")
            self._fields = {name: keys[key] for name, key in CFG["fields"].items()}
        return self._fields

    def users(self):
        rows = self.call("GET", "/users/", locationId=self.location).get("users", [])
        return {u["id"]: (u.get("name") or "").strip() for u in rows}

    def owner(self):
        """The named owner, never the first user listed. A blank setting sent every task to the wrong person."""
        if self._owner is None:
            match = [uid for uid, name in self.users().items() if name == CFG["owner_user"]]
            if len(match) != 1:
                raise MapError(f"expected one user named {CFG['owner_user']}, found {len(match)}")
            self._owner = match[0]
        return self._owner

    def search(self, filters=None, query=None):
        out, page = [], 1
        while True:
            body = {"locationId": self.location, "page": page, "pageLimit": 100}
            if filters:
                body["filters"] = filters
            if query:
                body["query"] = query
            rows = self.call("POST", "/contacts/search", body=body).get("contacts", [])
            out += rows
            if len(rows) < 100:
                return out
            page += 1

    def tagged(self, tag):
        return self.search([{"field": "tags", "operator": "contains", "value": tag}])

    def contact(self, contact_id):
        found = (self.call("GET", f"/contacts/{contact_id}") or {}).get("contact") or {}
        if found.get("locationId") not in (None, self.location):
            raise Refused("that contact isn't in this location")
        return found

    def find(self, email="", phone="", url=""):
        """(contact, clash) by email, then phone, then a LinkedIn or web address. Two different matches is a clash."""
        hits = {}
        for key, value in (("email", email), ("number", phone)):
            if value:
                found = (self.call("GET", "/contacts/search/duplicate", locationId=self.location,
                                   **{key: value}) or {}).get("contact")
                if found:
                    hits[found["id"]] = found
        if not hits and url:
            slug = url.rstrip("/").rsplit("/", 1)[-1]
            hits = {c["id"]: c for c in self.search(query=slug) if str(c.get("website") or "").rstrip("/") == url.rstrip("/")}
        if len(hits) > 1:
            return None, True
        return (next(iter(hits.values()), None), False)

    def opportunities(self, status="open", contact_id=""):
        """Every Sales card, a page at a time. Search stops at 100 a page."""
        out, after = [], None
        while True:
            query = {"location_id": self.location, "pipeline_id": self.pipeline()["id"], "limit": 100, "status": status}
            if contact_id:
                query["contact_id"] = contact_id
            if after:
                query.update(startAfter=after[0], startAfterId=after[1])
            got = self.call("GET", "/opportunities/search", **query)
            rows, meta = got.get("opportunities", []), got.get("meta", {})
            out += rows
            if not rows or not meta.get("nextPage"):
                return out
            after = (meta.get("startAfter"), meta.get("startAfterId"))

    def tasks(self, contact_id):
        return [t for t in self.call("GET", f"/contacts/{contact_id}/tasks").get("tasks", []) if not t.get("completed")]

    def notes(self, contact_id):
        return self.call("GET", f"/contacts/{contact_id}/notes").get("notes", [])

    def appointments(self, contact_id):
        return self.call("GET", f"/contacts/{contact_id}/appointments").get("events", [])

    def conversations(self, contact_id="", **query):
        params = {"locationId": self.location, "limit": 20, **query}
        if contact_id:
            params["contactId"] = contact_id
        return self.call("GET", "/conversations/search", version=CONVERSATIONS_VERSION, **params).get("conversations", [])

    def messages(self, conversation_id):
        got = self.call("GET", f"/conversations/{conversation_id}/messages", version=CONVERSATIONS_VERSION, limit=60)
        return (got.get("messages") or {}).get("messages", [])

    def email(self, email_id):
        got = self.call("GET", f"/conversations/messages/email/{email_id}", version=CONVERSATIONS_VERSION)
        return got.get("emailMessage", got)

    # --- writes, each with its own guard ------------------------------------------------------------------------------

    def _clean(self, text, what):
        if SSN.search(str(text or "")):
            raise Refused(f"{what} looks like it holds an ID number")
        text = scrub(text)
        if not text:
            raise ValueError(f"{what} is empty")
        return text

    def _check_tags(self, tags):
        clean = [str(t).strip().lower() for t in tags]
        for tag in clean:
            if tag.startswith(tuple(CFG["tag_prefixes_refused"])) or not tag.startswith(CFG["tag_prefix_allowed"]):
                raise Refused(f"{tag}: the CRM team writes only {CFG['tag_prefix_allowed']} tags, so no workflow fires on us")
        return clean

    def add_tags(self, contact_id, tags):
        self.call("POST", f"/contacts/{contact_id}/tags", body={"tags": self._check_tags(tags)})

    def remove_tags(self, contact_id, tags):
        self.call("DELETE", f"/contacts/{contact_id}/tags", body={"tags": self._check_tags(tags)})

    def create_contact(self, fields):
        return self.call("POST", "/contacts/", body={"locationId": self.location, **fields}).get("contact", {})

    def update_contact(self, contact_id, fields):
        return self.call("PUT", f"/contacts/{contact_id}", body=fields)

    def set_dnd(self, contact_id):
        return self.update_contact(contact_id, {"dnd": True})

    def note(self, contact_id, body, title=None, pinned=False):
        payload = {"body": self._clean(body, "the note")}
        if title:
            payload.update(title=title, pinned=pinned)
        return self.call("POST", f"/contacts/{contact_id}/notes", body=payload)

    def update_note(self, contact_id, note_id, body, title=None, pinned=False):
        payload = {"body": self._clean(body, "the note"), "pinned": pinned}
        if title:
            payload["title"] = title
        return self.call("PUT", f"/contacts/{contact_id}/notes/{note_id}", body=payload)

    def task(self, contact_id, title, due, assigned_to, body=""):
        """One open task per job: the same title again does nothing, so a rerun can't double a person's list."""
        title = self._clean(title, "the task title")
        if title in {t.get("title") for t in self.tasks(contact_id)}:
            return None
        payload = {"title": title, "body": self._clean(body, "the task body") if body else "", "completed": False,
                   "dueDate": due.isoformat(), "assignedTo": assigned_to}
        return self.call("POST", f"/contacts/{contact_id}/tasks", body=payload)

    def complete_task(self, contact_id, task_id):
        return self.call("PUT", f"/contacts/{contact_id}/tasks/{task_id}/completed", body={"completed": True})

    def create_card(self, contact_id, name, stage_id, source, assigned_to):
        return self.call("POST", "/opportunities/", body={
            "locationId": self.location, "pipelineId": self.pipeline()["id"], "pipelineStageId": stage_id, "name": name,
            "status": "open", "contactId": contact_id, "source": source, "assignedTo": assigned_to}).get("opportunity", {})

    def update_card(self, card, **changes):
        """Sales only, and open or lost only. Client Onboarding belongs to whoever built ONB, and won is Justin's."""
        if card.get("pipelineId") != self.pipeline()["id"]:
            raise Refused("that card isn't in Sales: Client Onboarding is read-only here")
        if "status" in changes and changes["status"] not in OPEN_OR_LOST:
            raise Refused("won and abandoned are a person's to set")
        return self.call("PUT", f"/opportunities/{card['id']}", body=changes)


def client(apply=False, transport=None):
    token, location = os.environ.get("GHL_API_KEY", "").strip(), os.environ.get("GHL_LOCATION_ID", "").strip()
    if not token or not location:
        raise Unreachable("GHL_API_KEY or GHL_LOCATION_ID isn't set")
    return Ghl(token, location, apply=apply and writes_on(), transport=transport)


# --- who may be touched ---------------------------------------------------------------------------------------------


def load_lists():
    return suppression.load(HOME / "suppression.csv")


def campaign_hold(text):
    """Independent of the list. suppression.csv is only as fresh as the last sync, and ONB 0 adds people as they reply."""
    low = str(text or "").lower()
    for rule in CFG["excluded_campaigns"]:
        if rule["id"].lower() == "none":  # set at intake: nothing is held (a client's own setup)
            continue
        if not rule["name"] and not rule["id"]:  # not set at intake: hold everyone rather than guess
            return "held-campaign-unset"
        # An unset name or id is "" here, and "" is in every string, so only a real value can match.
        if (rule["name"] and rule["name"].lower() in low) or (rule["id"] and rule["id"].lower() in low):
            return rule["reason"]
    return None


def who(lead):
    return " ".join(str(lead.get(k) or "") for k in ("email", "name", "company", "website", "linkedin", "skool"))


def hold_reason(lead, lists):
    return campaign_hold(lead.get("campaign")) or lists.reason(who(lead))


def field_value(contact, field_id):
    return next((f.get("value") for f in contact.get("customFields") or [] if f.get("id") == field_id), None)


def contact_hold(contact, fields, lists):
    """Why this contact must not be worked, or None. Reads the record itself, so it works on cards other writers made."""
    why = campaign_hold(field_value(contact, fields["campaign"]))
    if why:
        return why
    if contact.get("dnd"):
        return "do-not-disturb"
    if CFG["tags"]["dnc"] in tags_of(contact):
        return "opted-out"
    if CFG["tags"]["not_interested"] in tags_of(contact):
        return "not-interested"
    # Another writer's opt-out counts too. Holding one costs a message, and missing one costs the person's trust.
    theirs = tags_of(contact) & set(CFG["hold_tags"])
    if theirs:
        return sorted(theirs)[0]
    text = " ".join(str(contact.get(k) or "") for k in ("email", "contactName", "companyName", "website"))
    return lists.reason(text) if lists else None


# --- the outbox -------------------------------------------------------------------------------------------------------


class Outbox:
    """SQLite in the box's data folder, mode 600. Commits before a lane moves on. A finished row keeps no contact data."""

    def __init__(self, path=None):
        path = Path(path or data_dir() / "outbox.sqlite3")
        fresh = not path.exists()
        self.db = sqlite3.connect(path, timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS outbox (key TEXT PRIMARY KEY, lane TEXT NOT NULL, campaign TEXT NOT NULL,
            payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'queued', tries INTEGER NOT NULL DEFAULT 0,
            why TEXT NOT NULL DEFAULT '', contact TEXT NOT NULL DEFAULT '', added TEXT NOT NULL, finished TEXT NOT NULL DEFAULT '')""")
        self.db.commit()
        if fresh:
            os.chmod(path, 0o600)

    def put(self, key, lane, campaign, payload, state="queued", why=""):
        with self.db:
            return self.db.execute("INSERT OR IGNORE INTO outbox (key, lane, campaign, payload, state, why, added) "
                                   "VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (key, lane, campaign, payload, state, why, now().isoformat())).rowcount == 1

    def queued(self, limit=200):
        return self.db.execute("SELECT * FROM outbox WHERE state = 'queued' ORDER BY added LIMIT ?", (limit,)).fetchall()

    def queued_for(self, who):
        """One person's queued rows, by email, phone, LinkedIn or Skool address."""
        who = str(who or "").strip().lower()
        rows = self.db.execute("SELECT * FROM outbox WHERE state = 'queued' ORDER BY added").fetchall()
        return [r for r in rows if who and who in {str(json.loads(r["payload"]).get(k, "")).lower()
                                                   for k in ("email", "phone", "linkedin", "skool")}]

    def finish(self, key, state, why="", contact=""):
        with self.db:
            self.db.execute("UPDATE outbox SET state = ?, why = ?, contact = ?, payload = '{}', finished = ? WHERE key = ?",
                            (state, scrub(why)[:200], contact, now().isoformat(), key))

    def retry(self, key, why):
        with self.db:
            self.db.execute("UPDATE outbox SET tries = tries + 1, why = ? WHERE key = ?", (scrub(why)[:200], key))

    def counts(self):
        return dict(self.db.execute("SELECT state, COUNT(*) FROM outbox GROUP BY state").fetchall())

    def oldest_hours(self):
        row = self.db.execute("SELECT MIN(added) FROM outbox WHERE state = 'queued'").fetchone()
        return (now() - dt.datetime.fromisoformat(row[0])).total_seconds() / 3600 if row[0] else 0

    def by_lane(self):
        return dict(self.db.execute("SELECT lane, COUNT(*) FROM outbox WHERE state = 'done' GROUP BY lane").fetchall())


def outbox_key(lead):
    who_it_is = lead.get("email") or lead.get("phone") or lead.get("linkedin") or lead.get("skool") or ""
    parts = (lead["lane"], who_it_is, lead.get("campaign") or "", lead.get("evidence_ref") or "")
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]


def normalize(raw):
    lead = {k: str(v).strip() for k, v in raw.items() if v not in (None, "")}
    if lead.get("lane") not in CFG["lanes"]:
        raise ValueError(f"unknown lane: {lead.get('lane')}")
    if lead.get("email"):
        lead["email"] = lead["email"].lower()
    if lead.get("phone"):
        lead["phone"] = re.sub(r"[^\d+]", "", lead["phone"])
    # Skool hides every email, even from a signed-in member, so a Skool profile address counts as who someone is.
    if not (lead.get("email") or lead.get("phone") or lead.get("linkedin") or lead.get("skool")):
        raise ValueError("a lead needs an email, a phone, a LinkedIn address or a Skool profile")
    if not real_name(lead.get("name")):
        lead.pop("name", None)
    if lead.get("evidence_type") and lead["evidence_type"] not in CFG["evidence"]["Interested"]:
        raise ValueError(f"{lead['evidence_type']} isn't evidence for {CFG['stages'][0]}")
    return lead


def add(raw, apply=False, box=None, lists=None):
    """A lane hands over one person. Suppression first. Nothing is stored without apply. Pass `lists` for a big batch."""
    lead = normalize(raw)
    lists = lists if lists is not None else load_lists()
    why = campaign_hold(lead.get("campaign")) or (lists.reason(who(lead)) if lists else None)
    if why:
        if apply:
            (box or Outbox()).put(outbox_key(lead), lead["lane"], lead.get("campaign") or "", "{}", state="held", why=why)
        return {"status": "held", "reason": why}
    if not apply:
        return {"status": "dry run", "reason": "no list yet: it would wait in the queue" if lists is None else "clear"}
    new = (box or Outbox()).put(outbox_key(lead), lead["lane"], lead.get("campaign") or "", json.dumps(lead))
    return {"status": "queued" if new else "already queued", "reason": "" if lists else "no list yet: it waits in the queue"}


# --- the drain ----------------------------------------------------------------------------------------------------------


def split_name(name):
    first, _, last = str(name or "").partition(" ")
    return {k: v for k, v in (("firstName", first), ("lastName", last.strip())) if v}


def plan(ghl, lead, lists, when=None):
    """What this lead would change in GoHighLevel. Reads only, so a dry run can show it."""
    profile = lead.get("linkedin") or lead.get("skool") or ""
    found, clash = ghl.find(lead.get("email", ""), lead.get("phone", ""), profile)
    if clash:
        return {"state": "review", "why": "the email and phone match two different contacts", "steps": []}
    fields, lane = ghl.field_ids(), CFG["lanes"][lead["lane"]]
    values = {"campaign": lead.get("campaign"), "offer": lead.get("offer"), "stream": lane.get("stream")}
    wanted = {fields[k]: v for k, v in values.items() if v}
    # A cold list is thousands of people a sequence is already emailing. They're contacts until they reply, not open records.
    quiet = lane.get("bulk") and not lead.get("drafted") and not lead.get("evidence_type")
    tags = [CFG["lane_tag_prefix"] + lead["lane"]] if quiet else [CFG["tags"]["cohort"], CFG["lane_tag_prefix"] + lead["lane"]]
    if lead.get("drafted"):
        tags.append(CFG["tags"]["first_touch"])
    elif not lead.get("evidence_type") and not quiet:
        tags.append(CFG["tags"]["new"])
    steps, contact_id, cards = [], "", []
    if found:
        why = contact_hold(found, fields, lists)
        if why:
            return {"state": "held", "why": why, "steps": []}
        contact_id = found["id"]
        cards = ghl.opportunities(status="all", contact_id=contact_id)
        have = {f.get("id") for f in found.get("customFields") or [] if f.get("value") not in (None, "")}
        blanks = {k: v for k, v in split_name(lead.get("name")).items() if not real_name(found.get(k))}
        for key, source in (("companyName", "company"), ("website", "website"), ("email", "email"), ("phone", "phone")):
            if lead.get(source) and not found.get(key):
                blanks[key] = lead[source]
        custom = [{"id": k, "value": v} for k, v in wanted.items() if k not in have]
        if custom:
            blanks["customFields"] = custom
        if blanks:
            steps.append(("fill", blanks))
    else:
        data = {**split_name(lead.get("name")), "source": f"gtm:{lead['lane']}",
                "customFields": [{"id": k, "value": v} for k, v in wanted.items()]}
        for key, source in (("email", "email"), ("phone", "phone"), ("companyName", "company"),
                            ("website", "website")):
            if lead.get(source):
                data[key] = lead[source]
        if profile and "website" not in data:
            data["website"] = profile
        steps.append(("create_contact", data))
    steps.append(("tags", tags))
    opened = [c for c in cards if c.get("status") == "open"]
    note = None
    if lead.get("evidence_type"):
        note = f"Evidence ({lead['lane']}, {lead['evidence_type']}): {lead.get('evidence') or lead.get('evidence_ref') or 'no detail'}"
    if opened:
        pass  # ONB 0, or an earlier lane, already has the card.
    elif any(c.get("status") == "lost" for c in cards):
        note = None  # An opt-out or a no stays lost.
    elif lane.get("card_owner"):
        pass  # ONB 0 makes this lane's cards. Two writers would make two cards, so the sweep watches for a missing one.
    elif lead.get("evidence_type"):
        title = f"{split_name(lead.get('name')).get('firstName') or 'Contact'} | {lead['lane']}"
        steps.append(("create_card", {"name": title, "stage_id": ghl.pipeline()["stages"][CFG["stages"][0]],
                                      "source": f"gtm:{lead['lane']}", "assigned_to": ghl.owner()}))
    if note:
        steps.append(("note", note))
    if lead.get("drafted") and not opened:
        # A lane's own send never shows in a GoHighLevel thread, so its clock has to live here.
        due = add_business_days((when or now()).replace(hour=21, minute=0, second=0, microsecond=0), CFG["clocks"]["quiet_business_days"])
        first = split_name(lead.get("name")).get("firstName") or "Contact"
        steps.append(("check_back", {"title": f"{first}: check back ({lead['lane']})", "due": due, "assigned_to": ghl.owner()}))
    return {"state": "ok", "why": "", "steps": steps, "contact": contact_id}


def run(ghl, chosen):
    contact_id = chosen.get("contact", "")
    for verb, data in chosen["steps"]:
        if verb == "create_contact":
            contact_id = ghl.create_contact(data)["id"]
        elif verb == "fill":
            ghl.update_contact(contact_id, data)
        elif verb == "tags":
            ghl.add_tags(contact_id, data)
        elif verb == "create_card":
            ghl.create_card(contact_id, **data)
        elif verb == "note":
            ghl.note(contact_id, data)
        elif verb == "check_back":
            ghl.task(contact_id, **data)
    return contact_id


def drain(ghl, box=None, lists=None, limit=200, when=None, only=None):
    """Put what's queued into GoHighLevel. Dry run unless the client can write. GoHighLevel down leaves everything queued.
    `only` takes one person's rows and leaves the rest, even while DRAIN_HOLD keeps the backlog back."""
    box = box or Outbox()
    stats = collections.Counter()
    if stopped():
        return {"stopped": 1}
    if not only and backlog_held():
        return {"backlog held": 1}
    items = box.queued_for(only) if only else box.queued(limit)
    if only and not items:
        return {"nothing queued for that person": 1}
    lists = lists if lists is not None else load_lists()
    for item in items:
        lead = json.loads(item["payload"])
        if lists is None:
            stats["waiting on the list"] += 1
            continue
        try:
            why = hold_reason(lead, lists)
            chosen = {"state": "held", "why": why} if why else plan(ghl, lead, lists, when)
            if chosen["state"] != "ok":
                stats[chosen["state"]] += 1
                if ghl.apply:
                    box.finish(item["key"], chosen["state"], chosen["why"])
                continue
            if not ghl.apply:
                stats["would write"] += 1
                continue
            box.finish(item["key"], "done", contact=run(ghl, chosen))
            stats["done"] += 1
        except Unreachable as exc:
            box.retry(item["key"], str(exc))
            stats["unreachable"] += 1
            break  # Everything left stays queued for the next run.
        except GhlError as exc:
            box.finish(item["key"], "review", str(exc))
            stats["review"] += 1
    return dict(stats)


def status(box=None):
    box = box or Outbox()
    counts = box.counts()
    line = ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "empty"
    oldest = box.oldest_hours()
    return f"outbox: {line}" + (f", oldest queued {oldest:.0f} hours" if oldest >= 1 else "") + \
           f". Writes are {'on' if writes_on() else 'off'}." + (" The backlog is held." if backlog_held() else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--lane", required=True)
    for name in ("name", "email", "phone", "company", "website", "linkedin", "skool", "campaign", "offer", "evidence-type", "evidence",
                 "evidence-ref"):
        a.add_argument(f"--{name}")
    a.add_argument("--drafted", action="store_true", help="this lane drafted its own first touch for them")
    a.add_argument("--apply", action="store_true")
    d = sub.add_parser("drain")
    d.add_argument("--apply", action="store_true")
    d.add_argument("--only", metavar="EMAIL", help="this one person's queued rows, and nothing else")
    sub.add_parser("status")
    args = ap.parse_args(argv)
    if args.cmd == "add":
        raw = {k: v for k, v in vars(args).items() if k not in ("cmd", "apply") and v}
        print(json.dumps(add(raw, args.apply)))
        return 0
    if args.cmd == "status":
        print(status())
        return 0
    if args.apply and not writes_on():
        print("Writes are off, so this run only reads. Justin's yes is the file crm/WRITES_ON.")
    try:
        ghl = client(apply=args.apply)
        print(json.dumps(drain(ghl, only=args.only)))
        print(ghl.receipt())
    except Unreachable as exc:
        print(f"GoHighLevel isn't answering: {scrub(exc)}. Everything stays queued.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
