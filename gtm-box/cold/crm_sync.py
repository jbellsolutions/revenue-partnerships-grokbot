#!/usr/bin/env python3
"""Keeps GoHighLevel in step with cold email. Every lead and reply lands in one durable queue first, so nothing is lost while a location is down.

    crm_sync.py status          what's queued and whether each campaign's location answers
    crm_sync.py flush           pushes the queue to GoHighLevel: contacts, tags, reply notes
    crm_sync.py reply <email> <label> "<summary>"   records a reply and hands it to the replies profile

Each campaign names a CRM in campaigns.json. AI Guy's location has one writer and one queue, box/crm.py and its outbox, so its
leads and replies go straight there: suppression first, no upsert, and replies to the `replies` profile. Any other CRM uses
GHL_API_KEY_<CRM> and GHL_LOCATION_ID_<CRM> and the queue in this file, for example GHL_API_KEY_FUNDING, because box/crm.py
refuses every other location. A lead counts as in the CRM only after GoHighLevel has answered for it.

Every lead becomes a tagged contact. A reply also becomes an opportunity in the campaign's pipeline, at its first stage, so
closer works people who answered and the pipeline isn't buried under everyone who was emailed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
HERE = Path(__file__).resolve().parent
QUEUE = HOME / "cold" / "crm-queue.jsonl"
REPLIES = HOME / "cold" / "replies-inbox.jsonl"
API = "https://services.leadconnectorhq.com"
GAP = 0.15  # GoHighLevel allows 100 requests in 10 seconds.
ONE_WRITER = "ai-guy"  # box/crm.py owns this location.


def env(name):
    value = os.environ.get(name, "")
    if value:
        return value
    path = HOME / "box.env"
    for line in path.read_text().splitlines() if path.is_file() else []:
        if line.startswith(name + "="):
            return line.split("=", 1)[1].strip()
    return ""


def credentials(crm):
    suffix = crm.upper().replace("-", "_")
    return env(f"GHL_API_KEY_{suffix}"), env(f"GHL_LOCATION_ID_{suffix}")


def campaigns():
    """The bulk campaigns and the one-to-one lane. Both reach the CRM and booked-stop the same way."""
    extra = HERE / "one-to-one.json"
    return {**json.loads((HERE / "campaigns.json").read_text()), **(json.loads(extra.read_text()) if extra.is_file() else {})}


def append(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a") as handle:
        handle.write(json.dumps(record) + "\n")


def queue_leads(slug, rows):
    crm = campaigns()[slug]["crm"]
    items = [{"kind": "lead", "campaign": slug, "crm": crm, "email": row["email"], "first_name": row.get("first_name", ""),
              "last_name": row.get("last_name", ""), "company": row.get("company_name", ""), "website": row.get("company_domain", ""),
              "city": row.get("city", ""), "country": row.get("country", "")} for row in rows]
    if crm == ONE_WRITER:
        hand_over(items)
    else:
        for item in items:
            append(QUEUE, item)
    print(json.dumps({"queued_for_crm": len(rows), "crm": crm}))


def contact_body(item, location):
    return {"locationId": location, "email": item["email"], "firstName": item.get("first_name"), "lastName": item.get("last_name"),
            "companyName": item.get("company"), "website": item.get("website"), "city": item.get("city"), "country": item.get("country"),
            "source": "cold-email", "tags": ["cold-email", f"campaign-{item['campaign']}"]}


def post(path, body, token, opener=urllib.request.urlopen):
    request = urllib.request.Request(API + path, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {token}", "Version": "2021-07-28", "Content-Type": "application/json",
        "User-Agent": "gtm-box/1.0"})  # GoHighLevel's Cloudflare refuses Python's default name.
    time.sleep(GAP)
    with opener(request, timeout=30) as response:
        return json.load(response)


def first_stage(name, location, token, opener=urllib.request.urlopen, stage=None):
    """The pipeline's id and the id of the named stage, or its first stage, or None if the location doesn't have it."""
    request = urllib.request.Request(f"{API}/opportunities/pipelines?locationId={location}", headers={
        "Authorization": f"Bearer {token}", "Version": "2021-07-28", "User-Agent": "gtm-box/1.0"})
    time.sleep(GAP)
    with opener(request, timeout=30) as response:
        for pipeline in json.load(response).get("pipelines", []):
            if pipeline.get("name") == name and pipeline.get("stages"):
                chosen = next((row for row in pipeline["stages"] if row["name"] == stage), pipeline["stages"][0])
                return pipeline["id"], chosen["id"]
    return None


def open_opportunity(item, contact_id, location, token, opener=urllib.request.urlopen, stage=None):
    """One card per person. Upsert moves the card they have, so a booking doesn't open a second one."""
    spec = campaigns()[item["campaign"]]
    name = spec.get("pipeline")
    found = first_stage(name, location, token, opener, stage or spec.get("reply_stage")) if name else None
    if found:
        post("/opportunities/upsert", {"locationId": location, "pipelineId": found[0], "pipelineStageId": found[1], "contactId": contact_id,
                                       "name": item["email"], "status": "open", "source": f"cold-email {item['campaign']}"}, token, opener)


def writer():
    """box/crm.py and box/crm_replies.py, in the pack on the Mac and in the data folder on the box."""
    sys.path.insert(0, str(next(p for p in (HERE.parent / "box", HOME / "box") if (p / "crm.py").is_file())))
    import crm
    import crm_replies
    return crm, crm_replies


def hand_over(items):
    """AI Guy's leads and replies go to the writer's outbox, in one go, so the suppression list is only read once."""
    tools = writer()
    box, lists = tools[0].Outbox(), tools[0].load_lists()
    for item in items:
        to_writer(item, tools, box, lists)


def to_writer(item, tools, box, lists):
    """Hand one AI Guy lead or reply to the one writer. A held person's reply goes no further."""
    crm, crm_replies = tools
    name = " ".join(x for x in (item.get("first_name"), item.get("last_name")) if x)
    lead = {"lane": "cold-email", "email": item["email"], "name": name, "company": item.get("company"), "website": item.get("website"),
            "campaign": campaigns()[item["campaign"]]["name"]}
    if crm.add(lead, apply=True, box=box, lists=lists)["status"] == "held" or item["kind"] != "reply":
        return
    key = hashlib.sha256(f"{item['email']}|{item['label']}|{item['summary']}".encode()).hexdigest()[:24]
    crm_replies.ingest(item["email"], f"plusvibe{key}", "cold-email", item["summary"])


def writes_open():
    """The same locks box/crm.py keeps. A cold list is thousands of people, and a CRM's workflows can fire on each one."""
    return (HOME / "crm" / "WRITES_ON").is_file() and not (HOME / "STOP").exists()


def flush(opener=urllib.request.urlopen):
    if not QUEUE.is_file():
        print("nothing queued")
        return 0
    items = [json.loads(line) for line in QUEUE.read_text().splitlines() if line.strip()]
    left, done, blocked = [], 0, set()
    older = [item for item in items if item["crm"] == ONE_WRITER]  # Anything queued here before AI Guy moved to the outbox.
    if older:
        hand_over(older)
        done += len(older)
    if not writes_open() and len(older) < len(items):
        print("writes are locked: crm/WRITES_ON is absent or STOP is set, so everything stays queued")
    for item in items:
        if item["crm"] == ONE_WRITER:
            continue
        token, location = credentials(item["crm"])
        if not writes_open() or not token or not location or item["crm"] in blocked:
            blocked.add(item["crm"])
            left.append(item)
            continue
        try:
            contact = post("/contacts/upsert", contact_body(item, location), token, opener)
            if item["kind"] == "reply":
                contact_id = (contact.get("contact") or {}).get("id")
                post(f"/contacts/{contact_id}/notes", {"body": f"Reply, {item['label']}: {item['summary']}"}, token, opener)
                if item["label"] in ("yes", "question"):
                    open_opportunity(item, contact_id, location, token, opener)
            elif item["kind"] == "booked":
                open_opportunity(item, (contact.get("contact") or {}).get("id"), location, token, opener, campaigns()[item["campaign"]].get("booked_stage"))
            done += 1
        except urllib.error.HTTPError as error:
            blocked.add(item["crm"])
            left.append(item)
            print(f"{item['crm']}: GoHighLevel said {error.code}")
    fd = os.open(QUEUE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as handle:
        handle.writelines(json.dumps(item) + "\n" for item in left)
    print(json.dumps({"in_crm_now": done, "still_queued": len(left), "blocked_crms": sorted(blocked)}))
    return 2 if blocked else 0


def reply(email, label, summary, slug):
    crm = campaigns()[slug]["crm"]
    record = {"kind": "reply", "campaign": slug, "crm": crm, "email": email, "label": label, "summary": summary}
    if crm == ONE_WRITER:
        hand_over([record])
    else:
        append(QUEUE, record)
        append(REPLIES, record)
    print("queued for the CRM and handed to replies")


def booked(email, slug):
    """AI Guy's card moves through crm_stage.py on the booking itself. Funding's team can't write there, so it moves here."""
    crm = campaigns()[slug]["crm"]
    if crm != ONE_WRITER:
        append(QUEUE, {"kind": "booked", "campaign": slug, "crm": crm, "email": email})


def status():
    counts = {}
    if QUEUE.is_file():
        for line in QUEUE.read_text().splitlines():
            if line.strip():
                crm = json.loads(line)["crm"]
                counts[crm] = counts.get(crm, 0) + 1
    crms = sorted({spec["crm"] for spec in campaigns().values()})
    report = {}
    for crm in crms:
        if crm == ONE_WRITER:
            report[crm] = "box/crm.py"
            continue
        token, location = credentials(crm)
        if not (token and location):
            report[crm] = "no key on this computer"
            continue
        try:
            names = [p for p in {spec.get("pipeline") for spec in campaigns().values() if spec["crm"] == crm} if p]
            report[crm] = {"answers": True, **{p: bool(first_stage(p, location, token)) for p in names}}
        except urllib.error.HTTPError as error:
            report[crm] = f"GoHighLevel said {error.code}"
    print(json.dumps({"queued": counts, "crms": report}))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("flush")
    r = sub.add_parser("reply")
    for name in ("email", "label", "summary", "campaign"):
        r.add_argument(name)
    a = ap.parse_args(argv)
    if a.cmd == "status":
        status()
    elif a.cmd == "flush":
        return flush()
    else:
        reply(a.email, a.label, a.summary, a.campaign)
    return 0


if __name__ == "__main__":
    sys.exit(main())
