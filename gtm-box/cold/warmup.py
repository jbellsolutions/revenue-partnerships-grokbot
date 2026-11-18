#!/usr/bin/env python3
"""Tag each campaign's inboxes, set warmup and sending limits, and attach them to the campaign. Nothing launches.

    warmup.py check     how many planned inboxes are in PlusVibe, and their warmup state
    warmup.py apply     applies the baseline in skills/plusvibe-operator/SKILL.md. Rerunning is safe
    warmup.py instantly-off    pauses Instantly's warmup on inboxes that are now in PlusVibe. Rerunning is safe
"""
import datetime
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
sys.path.insert(0, str(HERE))
import plusvibe  # noqa: E402

PLAN = HOME / "cold" / "mailboxes.json"
CHUNK = 100
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
ACCOUNT = {"warmup_initial_daily_limit": 40, "warmup_pace_increment": 10, "warmup_max_daily_limit": 50, "warmup_randomize": "yes",
           "warmup_randomize_num": 20, "warmup_reply_rate": 0.45, "bulk_warmup_is_slow_rampup": "no", "daily_limit": 10,
           "interval_limit_in_min": 20, "bulk_is_slow_rampup": "yes", "bulk_rampup_daily_limit": 5, "bulk_rampup_daily_inc": 1}
CAMPAIGN = {"send_as_txt": "yes", "is_emailopened_tracking": "no", "stop_on_lead_replied": "yes", "is_pause_on_bouncerate": "yes",
            "bounce_rate_limit": 3, "unsub_blocklist": "yes"}


def plans():
    if not PLAN.is_file():
        raise plusvibe.Blocked("No mailbox plan. Run maildoso.py plan.")
    return json.loads(PLAN.read_text())["emails"]


def in_plusvibe():
    return {row["email"].lower(): row for row in plusvibe.accounts()}


def settings_for(spec):
    body = {**ACCOUNT, "warmup_schedule": {"tz": spec["timezone"], "from_time": spec["hours"][0], "to_time": spec["hours"][1], "days": DAYS}}
    if spec.get("business_type"):
        body["warmup_business_type"] = spec["business_type"]
    if spec.get("sender"):
        body["first_name"], body["last_name"] = spec["sender"], ""  # Only a campaign that names a sender. Justin's four use each inbox's own name.
    return body


def campaign_body(spec, account_ids, today=None):
    """PlusVibe's API is stricter than its docs: schedules is a list, start_date is required, and a day is listed only
    when it sends (a false day is refused). The start date doesn't launch anything; launch.py does that."""
    days = {str(day): True for day in range(1, 6)}
    start = today or datetime.date.today().isoformat()
    return {**CAMPAIGN, "email_accounts": account_ids, "schedules": [{"daily_limit": spec["per_day"], "days": days, "start_date": start,
            "timezone": spec["timezone"], "timing": {"from": spec["hours"][0], "to": spec["hours"][1]}}]}


def apply():
    specs = plusvibe.campaigns_spec()
    found = in_plusvibe()
    report, attach = {}, {}
    for slug, emails in plans().items():
        ids = [found[email.lower()].get("id") or found[email.lower()].get("_id") for email in emails if email.lower() in found]
        if not all(ids):
            raise plusvibe.Blocked(f"{ids.count(None)} {slug} inboxes came back from PlusVibe without an id. Nothing more was changed.")
        report[slug] = {"planned": len(emails), "in_plusvibe": len(ids)}
        if ids:
            attach[slug] = ids
    # Warmup first, on every inbox, so a refused campaign update can't leave some inboxes warming in two tools.
    for slug, ids in attach.items():
        for start in range(0, len(ids), CHUNK):
            chunk = ids[start:start + CHUNK]
            plusvibe.call("PUT", "/account/bulk-update", body={"workspace_id": plusvibe.workspace(), "ids": chunk, **settings_for(specs[slug])})
            plusvibe.call("PATCH", "/account/bulk-update-warmup", body={"workspace_id": plusvibe.workspace(), "ids": chunk, "warmup_status": "ACTIVE"})
    print(json.dumps({"warming": report}))
    for slug, ids in attach.items():
        plusvibe.call("PATCH", "/campaign/update/campaign", body={"workspace_id": plusvibe.workspace(), "campaign_id": plusvibe.campaign_id(slug),
                                                                  **campaign_body(specs[slug], ids)})
    print(json.dumps({"attached": {slug: len(ids) for slug, ids in attach.items()}}))


INSTANTLY = "https://api.instantly.ai/api/v2"


def instantly_post(emails, key, sleep=time.sleep, tries=30):
    """Instantly answers 409 to a warmup call it can't take yet; waiting and asking again gets it through."""
    for _ in range(tries):
        request = urllib.request.Request(f"{INSTANTLY}/accounts/warmup/disable", data=json.dumps({"emails": emails}).encode(), method="POST",
                                         headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "gtm-box/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.status
        except urllib.error.HTTPError as error:
            if error.code != 409:
                raise plusvibe.Blocked(f"Instantly said {error.code} to the warmup pause")
            sleep(20)
    raise plusvibe.Blocked(f"Instantly still said 409 after {tries} tries")


def instantly_warming(key):
    """Emails Instantly is warming now (warmup_status 1). On 2026-11-07 a pause that also named inboxes Instantly didn't
    have, or had already paused, came back 409; one naming only warming inboxes went through."""
    warming, after = set(), None
    while True:
        url = f"{INSTANTLY}/accounts?limit=100" + (f"&starting_after={after}" if after else "")
        request = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "User-Agent": "gtm-box/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            page = json.load(response)
        warming |= {(row.get("email") or "").lower() for row in page.get("items", []) if row.get("warmup_status") == 1}
        after = page.get("next_starting_after")
        if not after:
            return warming - {""}


def instantly_off(send=instantly_post, held=None, warming=None):
    """Two warmup tools on one inbox push it past Maildoso's daily limit. Only inboxes PlusVibe already has, and Instantly is
    still warming, are paused. A sender of the held campaign stops the whole run: that campaign stays as it is."""
    import maildoso
    found = in_plusvibe()
    emails = [email for rows in plans().values() for email in rows if email.lower() in found]
    held = maildoso.held_campaign_senders() if held is None else held
    if held & {email.lower() for email in emails}:
        raise plusvibe.Blocked("A sender of the held campaign is in the plan. Nothing was paused.")
    key = maildoso.env("INSTANTLY_API_KEY")
    warming = instantly_warming(key) if warming is None else warming
    emails = [email for email in emails if email.lower() in warming]
    for start in range(0, len(emails), CHUNK):
        send(emails[start:start + CHUNK], key)
    print(json.dumps({"instantly_warmup_paused": len(emails)}))


def check():
    found = in_plusvibe()
    report = {}
    for slug, emails in plans().items():
        rows = [found[email.lower()] for email in emails if email.lower() in found]
        report[slug] = {"planned": len(emails), "in_plusvibe": len(rows), "active": sum(1 for r in rows if r.get("status") == "ACTIVE"),
                        "warming": sum(1 for r in rows if r.get("warmup_status") == "ACTIVE")}
    print(json.dumps(report))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        {"check": check, "apply": apply, "instantly-off": instantly_off}[argv[0]]()
    except plusvibe.Blocked as why:
        print(f"BLOCKED: {why}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
