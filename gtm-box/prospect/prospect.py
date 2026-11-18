#!/usr/bin/env python3
"""High-level prospecting: a few one-to-one emails a day to senior people, each researched and written for that person.

    prospect.py find [--n 10]       new targets from Consulti: owners only, suppressed, one lane, verified
    prospect.py add <file.csv>      targets from a file Justin or the data agent made, checked the same way
    prospect.py next [--n 5]        targets waiting for research, as JSON
    prospect.py draft <email> --subject S --body-file F --followup-file G --why "<what the email rests on>"
    prospect.py status              counts only, never a name or an address
    prospect.py setup               creates the PlusVibe campaign and loads its two-step shell. Nothing sends
    prospect.py load [--max N]      approved drafts into PlusVibe, up to the day's cap
    prospect.py stop <email>        out of the campaign

An email goes out only once Justin has approved it. Either approved/<id> exists, made from his Mac with prospect.sh, or
he has approved the type and guardrails.json marks prospect-first-touch auto with his authorization, and the draft passed
every check here. Nothing on this computer can make either true. PlusVibe sends from the Google inboxes Justin attaches to
the campaign, and only after he launches it. AgentMail never sends these: its terms forbid cold outreach.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
SLUG = "high-level"
for path in (HOME / "cold", HERE.parent / "cold", HOME / "box", HERE.parent / "box"):
    sys.path.insert(0, str(path))

DASH = re.compile(r"[‒-―]")
LINK = re.compile(r"https?://|www\.|\.com/|\.io/", re.I)
TAG = re.compile(r"\{\{|\}\}|<[a-z/]")
MONEY = re.compile(r"\$\s?\d|\b\d+\s?(k|K)\b|per month|/mo\b|a month\b", re.I)
TIMELINE = re.compile(r"\b(in|within|under)\s+(\d+|a|one|two|three)\s+(days?|weeks?|months?)\b|\bguarantee", re.I)
STALE = re.compile(r"hope (this|you're|you are)|quick question|circle back|touch base|just following up|synerg|game.?chang|"
                   r"revolutionar|cutting.?edge|i wanted to reach out|picking your brain|pick your brain|10x|leverage ai", re.I)


def config():
    return json.loads((HERE / "config.json").read_text())


def folder():
    path = HOME / "prospect"
    path.mkdir(parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    return path


def private_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    scratch = path.with_suffix(path.suffix + ".tmp")
    with os.fdopen(os.open(scratch, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as handle:
        handle.write(text)
    os.replace(scratch, path)


def targets():
    path = folder() / "targets.json"
    return json.loads(path.read_text()) if path.is_file() else {}


def save_targets(data):
    private_write(folder() / "targets.json", json.dumps(data, indent=1))


def target_id(email):
    return hashlib.sha256(email.lower().encode()).hexdigest()[:10]


def words(text):
    return len(re.findall(r"[A-Za-z0-9'$%.]+", text))


def problems(subject, body, followup, row, claims=()):
    """What stops a draft reaching Justin. Each rule is one that a senior reader, or a spam filter, would hold against it."""
    found = []
    first = (row.get("first_name") or "").strip()
    whole = "\n".join([subject, body, followup])
    if DASH.search(whole):
        found.append("an em or en dash")
    if TAG.search(whole):
        found.append("a merge tag or HTML left in")
    if LINK.search(body):
        found.append("a link in the first email")
    if not 1 <= len(subject.split()) <= 7 or "!" in subject:
        found.append("a subject over 7 words or with !")
    if not 50 <= words(body) <= 150:
        found.append(f"a first email of {words(body)} words, not 50 to 150")
    if not 15 <= words(followup) <= 90:
        found.append(f"a follow-up of {words(followup)} words, not 15 to 90")
    if first and not body.strip().startswith(first):
        found.append("a first email that doesn't open with their first name")
    unclaimed = MONEY.findall(re.sub("|".join(map(re.escape, claims)) or r"(?!)", "", whole))
    if unclaimed:
        found.append("a number with money in it that isn't one of Justin's claims")
    if TIMELINE.search(whole):
        found.append("a timeline or a guarantee")
    if STALE.search(whole):
        found.append("a stock phrase: " + STALE.search(whole).group(0))
    if re.search(r"\b(AI|artificial intelligence)\b", subject):
        found.append("AI in the subject")
    return found


def lists_module():
    import list_build
    return list_build


def held_reason(row, lists, used):
    email = row["email"].lower()
    if email in used:
        return "already in a campaign"
    return lists.reason(f"{email} {row.get('company_domain') or ''}") if lists else "no suppression list on this computer"


def still_held(row, lists=None):
    """Days can pass between adding someone and their email going. A new client or a no in another lane stops it here."""
    if lists is None:
        lists = lists_module().suppression().load()
    if lists is None:
        return "no suppression list on this computer"
    return lists.reason(f"{row['email']} {row.get('company_domain') or ''}")


def add_rows(rows, source, check=None):
    """Suppression, one lane, then Consulti's verifier. Only a good address becomes a target."""
    lb = lists_module()
    lists = lb.suppression().load()
    used = lb.already_used(SLUG)
    have = targets()
    fresh, held = [], {}
    for row in rows:
        row = {**row, "email": row["email"].strip().lower()}
        if row["email"] in have:
            held["already a target"] = held.get("already a target", 0) + 1
            continue
        why = held_reason(row, lists, used)
        if why:
            held[why] = held.get(why, 0) + 1
            continue
        fresh.append(row)
    good, checks = lb.verify(fresh, check or lb.verify_one)
    for row in good:
        have[row["email"]] = {**{k: row.get(k, "") for k in lb.FIELDS}, "email": row["email"], "id": target_id(row["email"]),
                              "status": "new", "source": source, "added": dt.date.today().isoformat()}
    save_targets(have)
    print(json.dumps({"added": len(good), "held": held, "verification": checks, "targets": len(have)}))
    return len(good)


def find(n, search_fn=None, check=None):
    """Consulti search inside the day's lead credit cap, shared with every other pull on this computer."""
    lb = lists_module()
    left = lb.room()
    if left <= 0:
        print(json.dumps({"added": 0, "stopped": "today's lead credit cap is used"}))
        return 0
    spec = {**config()["search"], "owner_titles": True}
    list_id = lb.seen_list()
    rows, credits = lb.pull(spec, min(n, max(1, left // lb.MAX_COST)), search_fn, mark=lambda emails: lb.mark_seen(list_id, emails), exclude=list_id)
    lb.spent(credits)
    return add_rows(rows[:n * 2], "consulti", check)


def add_file(path):
    return add_rows(lists_module().read_upload(path), "upload")


def waiting(n):
    rows = [row for row in targets().values() if row["status"] == "new"]
    print(json.dumps([{k: row.get(k, "") for k in ("id", "email", "first_name", "last_name", "job_title", "company_name",
                                                       "company_domain", "linkedin_url", "city", "country", "industry")} for row in rows[:n]], indent=1))


def draft(email, subject, body, followup, why):
    data = targets()
    row = data.get(email.lower())
    if not row:
        raise SystemExit(f"{email} isn't a target. Add them first.")
    if row["status"] not in ("new", "drafted"):
        raise SystemExit(f"Their draft is already {row['status']}. It can't change now.")
    if (folder() / "approved" / row["id"]).is_file():
        raise SystemExit("Justin approved the draft he read. It can't change now; ask him to drop it first.")
    if (HOME / "STOP").exists():
        raise SystemExit("STOP is set")
    held = still_held(row)
    if held:
        data[row["email"]] = {**row, "status": "held", "held": held}
        save_targets(data)
        print(json.dumps({"draft": "refused", "held": held}))
        return 1
    found = problems(subject, body, followup, row, config().get("claims", []))
    if found:
        print(json.dumps({"draft": "refused", "fix": found}))
        return 1
    record = {"id": row["id"], "email": row["email"], "subject": subject.strip(), "body": body.strip(), "followup": followup.strip(),
              "why": why.strip(), "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    private_write(folder() / "drafts" / f"{row['id']}.json", json.dumps(record, indent=1))
    page = (f"# {row.get('first_name', '')} {row.get('last_name', '')}, {row.get('job_title', '')} at {row.get('company_name', '')}\n\n"
            f"Draft {row['id']}. Approve from the Mac: `bash agents/gtm-box/prospect.sh approve {row['id']}`\n\n"
            f"**Why them:** {record['why']}\n\n**Subject:** {record['subject']}\n\n{record['body']}\n\n**Follow-up, 4 days later:**\n\n"
            f"{record['followup']}\n")
    private_write(HOME / "queue" / "prospector" / f"{row['id']}.md", page)
    data[row["email"]] = {**row, "status": "drafted"}
    save_targets(data)
    print(json.dumps({"draft": row["id"], "queued_for": "Justin"}))
    return 0


def auto_approved():
    """Justin's standing yes for the type, in his own guardrails. Each field is his; nothing here writes them."""
    try:
        rules = json.loads((HOME / "guardrails.json").read_text()).get("message_types", {})
    except (OSError, ValueError):
        return False
    rule = rules.get("prospect-first-touch") or {}
    return bool(rule.get("authorized") and rule.get("copy_approved") and rule.get("mode") == "auto")


def draft_hash(target_id_):
    path = folder() / "drafts" / f"{target_id_}.json"
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def approved(target):
    """Justin's yes is for the exact words he read: the marker holds that draft's sha256, written by prospect.sh."""
    marker = folder() / "approved" / target["id"]
    if marker.is_file():
        return marker.read_text().strip() == draft_hash(target["id"]) != ""
    return target["status"] == "drafted" and auto_approved()


def loaded_today(data, day):
    return sum(1 for row in data.values() if row.get("loaded") == day)


def load(limit=None, pv=None, crm=None, today=None):
    """Approved drafts become PlusVibe leads carrying their own words. A lead in a campaign that isn't launched waits there."""
    if (HOME / "STOP").exists():
        raise SystemExit("STOP is set")
    if pv is None:
        import plusvibe as pv
    if crm is None:
        import crm_sync as crm
    pv.campaign_id(SLUG)  # Refuses before anything moves if setup hasn't run.
    day = today or dt.date.today().isoformat()
    data = targets()
    room = max(0, config()["daily_max"] - loaded_today(data, day))
    if limit is not None:
        room = min(room, limit)
    ready = [row for row in data.values() if row["status"] == "drafted" and approved(row)][:room]
    lists = lists_module().suppression().load()
    sent, skipped, held = [], 0, 0
    for row in ready:
        why = still_held(row, lists)
        if why:
            data[row["email"]] = {**row, "status": "held", "held": why}
            save_targets(data)
            held += 1
            continue
        record = json.loads((folder() / "drafts" / f"{row['id']}.json").read_text())
        lead = pv.lead_row(row)
        lead["custom_variables"].update({"hl_subject": record["subject"], "hl_body": record["body"], "hl_followup": record["followup"]})
        answer = pv.call("POST", "/lead/add", body={"workspace_id": pv.workspace(), "campaign_id": pv.campaign_id(SLUG),
                                                    "skip_if_in_workspace": True, "leads": [lead]}) or {}
        if int(answer.get("leads_uploaded") or 0) < 1:  # Already somewhere in PlusVibe: one lane per person.
            data[row["email"]] = {**row, "status": "skipped", "why": "already in PlusVibe"}
            save_targets(data)
            skipped += 1
            continue
        data[row["email"]] = {**row, "status": "loaded", "loaded": day}
        save_targets(data)
        sent.append(row)
    if sent:
        lb = lists_module()
        lb.write(SLUG, lb.existing(SLUG) + [{k: row.get(k, "") for k in lb.FIELDS} for row in sent])
        crm.queue_leads(SLUG, sent)
    print(json.dumps({"loaded": len(sent), "skipped": skipped, "held": held, "waiting_for_justin": sum(1 for r in data.values() if r["status"] == "drafted" and not approved(r)),
                      "cap_left_today": room - len(sent)}))
    return len(sent)


def shell(values):
    """The campaign's two steps. Each lead carries its own subject, email and follow-up; the shell adds the sign-off and footer."""
    footer = "\n\nReply stop and I won't email again.\n" + values.get("postal_address", "{{postal_address}}")
    return [{"step": 1, "wait_time": 4, "variations": [{"variation": "A", "name": "A", "subject": "{{custom_hl_subject}}",
             "body": "{{custom_hl_body}}\n\n{{sender_first_name}}" + footer}]},
            {"step": 2, "wait_time": 1, "variations": [{"variation": "A", "name": "A", "subject": "",
             "body": "{{custom_hl_followup}}\n\n{{sender_first_name}}" + footer}]}]


def setup(pv=None):
    if pv is None:
        import plusvibe as pv
    saved = pv.state()
    ids = saved.get("campaigns", {})
    if SLUG not in ids:
        made = pv.call("POST", "/campaign/add/campaign", body={"workspace_id": pv.workspace(), "camp_name": config()["campaign_name"]})
        ids[SLUG] = made.get("id") or made.get("campaign_id") or made.get("_id")
        pv.save({**pv.state(), "campaigns": ids})
    values = pv.copy_values(SLUG)
    steps = [{**step, "variations": [{**row, "body": pv.html(row["body"])} for row in step["variations"]]} for step in shell(values)]
    pv.call("PATCH", "/campaign/update/campaign", body={"workspace_id": pv.workspace(), "campaign_id": ids[SLUG], "var_sel_type": "R_ROBIN",
                                                        "sequences": steps})
    gaps = [] if values.get("postal_address") else ["postal_address"]
    print(json.dumps({"campaign": config()["campaign_name"], "steps": 2, "gaps": gaps, "launched": False}))


def status():
    data = targets()
    counts = {}
    for row in data.values():
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(json.dumps({"targets": len(data), **counts, "auto": auto_approved(), "daily_max": config()["daily_max"]}))


def stop(email, pv=None):
    if pv is None:
        import plusvibe as pv
    pv.stop(email.lower(), SLUG)
    data = targets()
    if email.lower() in data:
        data[email.lower()]["status"] = "stopped"
        save_targets(data)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("find").add_argument("--n", type=int, default=10)
    sub.add_parser("add").add_argument("file")
    sub.add_parser("next").add_argument("--n", type=int, default=5)
    d = sub.add_parser("draft")
    d.add_argument("email")
    d.add_argument("--subject", required=True)
    d.add_argument("--body-file", required=True)
    d.add_argument("--followup-file", required=True)
    d.add_argument("--why", required=True)
    sub.add_parser("status")
    sub.add_parser("setup")
    sub.add_parser("load").add_argument("--max", type=int)
    sub.add_parser("stop").add_argument("email")
    a = ap.parse_args(argv)
    if a.cmd == "find":
        find(a.n)
    elif a.cmd == "add":
        add_file(a.file)
    elif a.cmd == "next":
        waiting(a.n)
    elif a.cmd == "draft":
        return draft(a.email, a.subject, Path(a.body_file).read_text(), Path(a.followup_file).read_text(), a.why)
    elif a.cmd == "status":
        status()
    elif a.cmd == "setup":
        setup()
    elif a.cmd == "load":
        load(a.max)
    elif a.cmd == "stop":
        stop(a.email)
    return 0


if __name__ == "__main__":
    sys.exit(main())
