#!/usr/bin/env python3
"""PlusVibe from the GTM box: accounts, campaigns, leads, replies and stats, through PlusVibe's API.

    plusvibe.py status                     workspace, accounts by status, campaigns
    plusvibe.py setup                      creates the campaigns if missing. Nothing sends
    plusvibe.py tag-check                  how many inboxes each campaign has against what it needs
    plusvibe.py load <campaign>            adds that campaign's verified list, then queues the CRM push
    plusvibe.py blocklist                  loads the suppression list's emails and domains
    plusvibe.py replies                    new replies, into the inbox file cold-email sorts and hands to replies
    plusvibe.py stats                      each campaign against 5% replies and 1% deals
    plusvibe.py refresh <campaign>         sends a loaded list again so existing leads pick up cleaned fields
    plusvibe.py labels                     creates the Not Now label and sets which labels the AI applies
    plusvibe.py label <campaign> <email> <key>   sets a label the AI missed, which starts that person's subsequence
    plusvibe.py load-copy <campaign>       puts the sequence and subsequences in the draft. Nothing sends
    plusvibe.py copy-check <campaign>      what the copy still needs before it can go out
    plusvibe.py stop <campaign> <email>    takes one person out of the campaign and its subsequences
    plusvibe.py launch <campaign>          only with Justin's approval file for that campaign, no gaps in the copy, and no STOP
    plusvibe.py pause <campaign>

The key is PLUSVIBE_API_KEY. PlusVibe allows 5 requests a second. A webhook needs a public address and this computer has
none, so replies are polled.
"""
import argparse
import csv
import hashlib
from html import escape
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
HERE = Path(__file__).resolve().parent
API = "https://api.plusvibe.ai/api/v1"
TARGET_REPLY, TARGET_DEAL = 0.05, 0.01
BATCH = 500
GAP = 0.25  # Four requests a second, under the limit of five.
STATE = HOME / "cold" / "state.json"
EMAIL = re.compile(r"[\w.+%-]+@[\w-]+\.[\w.-]+")
DOMAIN = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$")
RANDOM = re.compile(r"\{\{\s*random\s*\|(.*?)\}\}", re.I | re.S)
TOKEN = re.compile(r"\{\{\s*([a-zA-Z_]+)\s*\}\}")
AI_LABELS = ("INTERESTED", "NOT_INTERESTED", "OUT_OF_OFFICE", "AUTOMATIC_REPLY", "NOT_NOW")
COMPANY_TAIL = re.compile(r"[\s,.]+(pty\.?|proprietary|ltd\.?|limited|llc\.?|l\.l\.c\.?|inc\.?|incorporated|corp\.?|corporation)$", re.I)
SMALL_WORDS = {"the", "and", "for", "of", "pro", "all", "one", "top", "our", "new", "big"}
LEAD_FIELDS = {"first_name", "last_name", "company_name", "city", "country", "sender_first_name", "sender_last_name", "custom_first_line"}
ACCEPTED = re.compile(r"^[a-z0-9._%-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$")  # PlusVibe refuses a whole batch over one plus address.


class Blocked(Exception):
    """Something this tool can't get past on its own, such as the plan or the key."""


def key():
    value = os.environ.get("PLUSVIBE_API_KEY", "")
    if not value:
        env = HOME / "box.env"
        for line in env.read_text().splitlines() if env.is_file() else []:
            if line.startswith("PLUSVIBE_API_KEY="):
                value = line.split("=", 1)[1].strip()
    if not value:
        raise Blocked("PLUSVIBE_API_KEY isn't on this computer. It needs PlusVibe's Business plan.")
    return value


def call(method, path, query=None, body=None, opener=urllib.request.urlopen):
    url = f"{API}{path}" + ("?" + urllib.parse.urlencode(query) if query else "")
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers={
        "x-api-key": key(), "Content-Type": "application/json", "User-Agent": "gtm-box/1.0"})
    time.sleep(GAP)
    try:
        with opener(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        said = EMAIL.sub("<address>", error.read()[:300].decode(errors="ignore"))  # This reaches an agent's notes.
        raise Blocked(f"PlusVibe said {error.code} on {path}: {said}")


def state():
    return json.loads(STATE.read_text()) if STATE.is_file() else {}


def save(data):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2))


def workspace():
    saved = state()
    if saved.get("workspace_id"):
        return saved["workspace_id"]
    found = call("GET", "/authenticate").get("workspaces") or []
    if not found:
        raise Blocked("This key can see no workspace.")
    save({**saved, "workspace_id": found[0]["_id"], "workspace_name": found[0]["name"]})
    return found[0]["_id"]


def campaigns_spec():
    return json.loads((HERE / "campaigns.json").read_text())


def accounts():
    out, skip = [], 0
    while True:
        page = call("GET", "/account/list", {"workspace_id": workspace(), "skip": skip, "limit": 100}).get("accounts") or []
        out += page
        if len(page) < 100:
            return out
        skip += 100


def status():
    rows = accounts()
    by = {}
    for row in rows:
        by[row.get("status", "?")] = by.get(row.get("status", "?"), 0) + 1
    warm = sum(1 for row in rows if row.get("warmup_status") == "ACTIVE")
    camps = call("GET", "/campaign/list-all", {"workspace_id": workspace(), "limit": 100})
    camps = camps if isinstance(camps, list) else camps.get("campaigns") or camps.get("data") or []
    print(json.dumps({"workspace": state().get("workspace_name"), "accounts": len(rows), "by_status": by, "warming": warm,
                      "campaigns": [{"name": c.get("camp_name"), "status": c.get("status")} for c in camps]}, indent=2))


def setup():
    saved = state()
    ids = saved.get("campaigns", {})
    for slug, spec in campaigns_spec().items():
        if slug in ids:
            continue
        made = call("POST", "/campaign/add/campaign", body={"workspace_id": workspace(), "camp_name": spec["name"]})
        ids[slug] = made.get("id") or made.get("campaign_id") or made.get("_id")
        print(f"created {spec['name']}: nothing sends until Justin approves it")
    save({**state(), "campaigns": ids})


def campaign_id(slug):
    found = state().get("campaigns", {}).get(slug)
    if not found:
        raise Blocked(f"{slug} has no campaign yet. Run setup.")
    return found


def company(name):
    """A name in capitals, or one ending in Pty Ltd, reads as a mail merge in the first line of an email."""
    name = (name or "").strip()
    while COMPANY_TAIL.search(name):
        name = COMPANY_TAIL.sub("", name).strip()
    if name.isupper():
        name = " ".join(word if len(word) <= 3 and word.lower() not in SMALL_WORDS else word.capitalize() for word in name.split())
    return name


def lead_row(row):
    return {"email": row["email"], "first_name": row.get("first_name", ""), "last_name": row.get("last_name", ""),
            "company_name": company(row.get("company_name", "")), "company_website": row.get("company_domain", ""),
            "city": row.get("city", ""), "country": row.get("country", ""), "linkedin_person_url": row.get("linkedin_url", ""),
            "custom_variables": {"job_title": row.get("job_title", ""), "industry": row.get("industry", ""), "tier": str(row.get("tier", "")),
                                 **({"first_line": row["first_line"]} if row.get("first_line") else {})}}


def load(slug):
    path = HOME / "cold" / "lists" / f"{slug}.csv"
    if not path.is_file():
        raise Blocked(f"No list for {slug}. Run list_build.py build {slug}.")
    with path.open(newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if ACCEPTED.match(row["email"])]
    added = send_leads(slug, rows, {"skip_if_in_workspace": True})
    print(json.dumps({"campaign": slug, "in_list": len(rows), "added": added}))
    saved = state()
    done = saved.get("crm_queued", {}).get(slug, 0)  # A top-up only adds to the end of a list, so the CRM gets only the new rows.
    import crm_sync
    crm_sync.queue_leads(slug, rows[done:])
    save({**saved, "crm_queued": {**saved.get("crm_queued", {}), slug: len(rows)}})


def first_lines(slug):
    path = HOME / "cold" / "first-lines" / f"{slug}.json"
    return json.loads(path.read_text()) if path.is_file() else {}


def send_leads(slug, rows, how):
    added, lines = 0, first_lines(slug)
    rows = [{**row, "first_line": lines.get(row["email"], "")} for row in rows]
    for start in range(0, len(rows), BATCH):
        chunk = rows[start:start + BATCH]
        result = call("POST", "/lead/add", body={"workspace_id": workspace(), "campaign_id": campaign_id(slug), **how,
                                                 "leads": [lead_row(row) for row in chunk]})
        added += int(result.get("leads_uploaded") or 0)
    return added


def refresh(slug):
    """Sends a loaded list again so existing leads pick up cleaned fields. The CRM queue isn't touched."""
    path = HOME / "cold" / "lists" / f"{slug}.csv"
    with path.open(newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if ACCEPTED.match(row["email"])]
    print(json.dumps({"campaign": slug, "sent": len(rows), "new": send_leads(slug, rows, {"skip_if_in_workspace": False, "is_overwrite": True})}))


def labels():
    """The labels subsequences start from. Not Now is ours. The AI labels every first reply, so out-of-office isn't read as a person."""
    have = {row.get("key") for row in call("GET", "/workspace-settings/lead-labels", {"workspace_id": workspace()})}
    if "NOT_NOW" not in have:
        call("POST", "/workspace-settings/lead-labels/add", body={"workspace_id": workspace(), "name": "Not Now", "sentiment": "NEUTRAL"})
    call("PATCH", "/workspace-settings/update", body={"workspace_id": workspace(), "ai_lead_labeling": {"labels": list(AI_LABELS)}})
    print(json.dumps({"ai_labels": list(AI_LABELS)}))


def label(slug, email, key):
    """Sets a label the AI missed. Lenders often answer with a list of states, which doesn't read as Interested to it."""
    call("POST", "/lead/data/update", body={"workspace_id": workspace(), "campaign_id": campaign_id(slug), "email": email, "variables": {"label": key}})
    print(f"labelled {key}")


def blocklist_entry(value):
    """PlusVibe takes a plain email address or a domain, and refuses a whole batch over one that's neither."""
    return bool(ACCEPTED.match(value) or DOMAIN.match(value))


def blocklist():
    path = HOME / "suppression.csv"
    if not path.is_file():
        raise Blocked("No suppression list on this computer.")
    with path.open(newline="") as handle:
        wanted = {row["value"].strip().lower() for row in csv.DictReader(handle) if row["kind"] in ("email", "domain")}
    entries = sorted(value for value in wanted if blocklist_entry(value))
    added = known = refused = 0
    for start in range(0, len(entries), BATCH):
        chunk = entries[start:start + BATCH]
        try:
            result = call("POST", "/blocklist/add/entries", body={"workspace_id": workspace(), "entries": chunk})
        except Blocked as why:
            bad = {int(n) for n in re.findall(r"entries>(\d+)", str(why))}
            if not bad:
                raise
            refused += len(bad)
            result = call("POST", "/blocklist/add/entries", body={"workspace_id": workspace(), "entries": [v for i, v in enumerate(chunk) if i not in bad]})
        added += int(result.get("entries_added") or 0)
        known += int(result.get("already_in_blocklist") or 0)
    print(json.dumps({"on_the_list": len(wanted), "added": added, "already_there": known, "left_out_as_invalid": len(wanted) - len(entries) + refused}))


def replies():
    """Replies only: `email_type=received`. Each one goes to closer's inbox once, keyed by PlusVibe's id."""
    saved = state()
    known = set(saved.get("replies_seen", []))
    trail, fresh = None, []
    while True:
        query = {"workspace_id": workspace(), "email_type": "received", "preview_only": "true"}
        if trail:
            query["page_trail"] = trail
        page = call("GET", "/unibox/emails", query)
        rows = page.get("data") or []
        fresh += [row for row in rows if row.get("id") not in known]
        trail = page.get("page_trail")
        if not trail or not rows or all(row.get("id") in known for row in rows):
            break
    box = HOME / "cold" / "inbox.jsonl"
    box.parent.mkdir(parents=True, exist_ok=True)
    with box.open("a") as handle:
        for row in reversed(fresh):
            handle.write(json.dumps({"id": row.get("id"), "lead": row.get("lead"), "campaign_id": row.get("campaign_id"),
                                     "subject": row.get("subject"), "preview": row.get("content_preview") or row.get("snippet")}) + "\n")
    save({**state(), "replies_seen": sorted(known | {row.get("id") for row in fresh})[-5000:]})
    print(f"{len(fresh)} new replies" if fresh else "no new replies")
    return fresh


def stats():
    rows = call("GET", "/campaign/stats/all", {"workspace_id": workspace()})
    rows = rows if isinstance(rows, list) else rows.get("data") or []
    names = {spec["name"] for spec in campaigns_spec().values()}
    report = {}
    for row in rows:
        if row.get("camp_name") not in names:
            continue
        sent = int(row.get("lead_contacted_count") or row.get("sent_count") or 0)
        replied = int(row.get("replied_count") or 0)
        report[row["camp_name"]] = {"contacted": sent, "replies": replied}
        print(f"{row.get('camp_name')}: contacted {sent}, replies {replied}, {replied / sent if sent else 0:.2%} against {TARGET_REPLY:.0%}")
    (HOME / "cold" / "stats.json").write_text(json.dumps(report, indent=2))  # copywriter reads this. It holds no PlusVibe key.


def copy_of(slug):
    return json.loads((HERE / "sequences" / f"{slug}.json").read_text())


def copy_values(slug):
    """Filled in when the copy loads, because PlusVibe can't: the booking link, the postal address, the business name.
    The file has a "default" block, and a block for any campaign that differs, such as the lenders' own calendar."""
    path = HOME / "cold" / "copy-vars.json"
    saved = json.loads(path.read_text()) if path.is_file() else {}
    return {**saved.get("default", {}), **saved.get(slug, {})}


CUSTOM = ("first_line",)  # PlusVibe stores a custom variable as custom_<name>, and only that name fills. {{first_line}} went out as written.


def fill(text, values):
    for name, value in values.items():
        text = text.replace("{{%s}}" % name, value)
    for name in CUSTOM:
        text = text.replace("{{%s}}" % name, "{{custom_%s}}" % name)
    return RANDOM.sub(lambda m: "{{random|" + "|".join(part.strip() for part in m.group(1).split("|")) + "}}", text)


def html(text):
    """PlusVibe stores a body as HTML, one div a line. Without this, every line break in the copy is lost."""
    return "".join(f"<div>{escape(line, quote=False)}</div>" if line.strip() else "<div><br></div>" for line in text.split("\n"))


def steps_body(steps, values):
    return [{"step": step["step"], "wait_time": max(step["wait_time"], 1),  # PlusVibe's docs say 0 is fine. Its API refuses it.
             "variations": [{"variation": row["variation"], "name": row["variation"], "subject": fill(row.get("subject", ""), values), "body": html(fill(row["body"], values))}
                            for row in step["variations"]]} for step in steps]


def copy_gaps(slug):
    """Words in double braces PlusVibe won't fill. Each one would stop leads, or reach someone with the braces showing."""
    doc = copy_of(slug)
    text = json.dumps([doc["steps"], doc.get("subsequences", [])])
    used = set(TOKEN.findall(fill(text, copy_values(slug))))
    return sorted(used - LEAD_FIELDS)


def lines_missing(slug):
    """Leads with no first line, if the copy uses one. An empty field pauses the lead, and five of those pause the campaign."""
    path = HOME / "cold" / "lists" / f"{slug}.csv"
    if "{{first_line}}" not in json.dumps(copy_of(slug)) or not path.is_file():
        return 0
    lines = first_lines(slug)
    with path.open(newline="") as handle:
        return sum(1 for row in csv.DictReader(handle) if ACCEPTED.match(row["email"]) and row["email"] not in lines)


def copy_print(slug):
    """A fingerprint of the copy as it would load, so launch can tell the draft in PlusVibe is the current one."""
    doc, values = copy_of(slug), copy_values(slug)
    bodies = [steps_body(doc["steps"], values), [steps_body(sub["steps"], values) for sub in doc.get("subsequences", [])]]
    return hashlib.sha256(json.dumps(bodies, sort_keys=True).encode()).hexdigest()


def load_copy(slug):
    values, doc = copy_values(slug), copy_of(slug)
    call("PATCH", "/campaign/update/campaign", body={"workspace_id": workspace(), "campaign_id": campaign_id(slug), "var_sel_type": "R_ROBIN",
                                                     "sequences": steps_body(doc["steps"], values)})
    saved = state()
    made = saved.setdefault("subsequences", {}).setdefault(slug, {})
    for sub in doc.get("subsequences", []):
        if sub["name"] not in made:
            result = call("POST", "/campaign/add/subsequence", body={
                "workspace_id": workspace(), "name": sub["name"], "parent_camp_id": campaign_id(slug),
                "events": [{"name": "LEAD_LABEL_UPDATED", "val": [sub["trigger"]]}]})
            made[sub["name"]] = result.get("id") or result.get("_id") or result.get("campaign_id")
            save(saved)
        call("PATCH", "/campaign/update/campaign", body={"workspace_id": workspace(), "campaign_id": made[sub["name"]], "first_wait_time": sub["first_wait_time"],
                                                         "first_wait_time_unit": "days", "sequences": steps_body(sub["steps"], values)})
    save({**state(), "copy_loaded": {**state().get("copy_loaded", {}), slug: copy_print(slug)}})
    print(json.dumps({"campaign": slug, "steps": len(doc["steps"]), "subsequences": len(made), "gaps": copy_gaps(slug)}))


def copy_check(slug):
    print(json.dumps({"campaign": slug, "gaps": copy_gaps(slug), "first_lines_missing": lines_missing(slug), "approved": approved(slug)}))


def stop(email, slug):
    """One person out of a campaign and everything under it. Most people are in only one of those, so a miss isn't an error."""
    done = 0
    for camp in [campaign_id(slug), *state().get("subsequences", {}).get(slug, {}).values()]:
        try:
            call("POST", "/lead/update/status", body={"workspace_id": workspace(), "campaign_id": camp, "email": email, "new_status": "COMPLETED"})
            done += 1
        except Blocked:
            continue
    if not done:
        raise Blocked(f"{slug}: PlusVibe has no such lead in the campaign or its subsequences")
    return done


def approved(slug):
    return (HOME / "cold" / "approved" / slug).is_file()


def launch(slug):
    if (HOME / "STOP").exists():
        raise Blocked("STOP is set.")
    if not approved(slug):
        raise Blocked(f"{slug} isn't approved. Justin approves the copy once, then Claude Code writes cold/approved/{slug}.")
    if copy_gaps(slug):
        raise Blocked(f"{slug}'s copy still needs: {', '.join(copy_gaps(slug))}. Add them to cold/copy-vars.json and run load-copy.")
    if lines_missing(slug):
        raise Blocked(f"{lines_missing(slug)} leads in {slug} have no first line. Run first_lines.py build {slug}, then refresh.")
    if state().get("copy_loaded", {}).get(slug) != copy_print(slug):
        raise Blocked(f"The draft in PlusVibe isn't the current copy for {slug}. Run load-copy.")
    call("POST", "/campaign/launch", body={"workspace_id": workspace(), "campaign_id": campaign_id(slug)})
    print(f"launched {slug}")


def pause(slug):
    call("POST", "/campaign/pause", body={"workspace_id": workspace(), "campaign_id": campaign_id(slug)})
    print(f"paused {slug}")


def tag_check():
    need = {slug: spec["inboxes"] for slug, spec in campaigns_spec().items()}
    live = sum(1 for row in accounts() if row.get("status") == "ACTIVE")
    print(json.dumps({"need": need, "total_needed": sum(need.values()), "active_accounts": live, "short_by": max(0, sum(need.values()) - live)}))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("status", "setup", "tag-check", "blocklist", "replies", "stats", "labels"):
        sub.add_parser(name)
    for name in ("load", "refresh", "load-copy", "copy-check", "launch", "pause"):
        sub.add_parser(name).add_argument("campaign")
    one = sub.add_parser("stop")
    one.add_argument("campaign")
    one.add_argument("email")
    tag = sub.add_parser("label")
    tag.add_argument("campaign")
    tag.add_argument("email")
    tag.add_argument("key")
    a = ap.parse_args(argv)
    plain = {"status": status, "setup": setup, "tag-check": tag_check, "blocklist": blocklist, "replies": replies, "stats": stats, "labels": labels}
    named = {"load": load, "refresh": refresh, "load-copy": load_copy, "copy-check": copy_check, "launch": launch, "pause": pause}
    try:
        if a.cmd == "stop":
            print(f"stopped in {stop(a.email, a.campaign)} campaigns")
        elif a.cmd == "label":
            label(a.campaign, a.email, a.key)
        elif a.cmd in plain:
            plain[a.cmd]()
        else:
            named[a.cmd](a.campaign)
    except Blocked as why:
        print(f"BLOCKED: {why}")
        return 2
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    sys.exit(main())
