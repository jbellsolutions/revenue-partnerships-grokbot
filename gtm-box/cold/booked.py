#!/usr/bin/env python3
"""Anyone who books a call comes out of every sequence, in both GoHighLevel locations.

    booked.py sweep     the "Booked stop" job. Reads Cal.com and each location's calendars, and stops anyone on a list

A person can book from the link in an email without replying, so this reads the calendars, not the replies. Justin's sales
calls book through Cal.com, so its bookings need CAL_API_KEY. For AI Guy, crm_stage.py moves the card and closer's call-prep
job does the pre-call work. For lenders, crm_sync.py moves the card to Call Booked. This file reads GoHighLevel and never
writes to it. Booking ids are kept, addresses aren't.
"""
import csv
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
import crm_sync  # noqa: E402
import plusvibe  # noqa: E402

HOME = crm_sync.HOME
SEEN = HOME / "cold" / "booked.json"
API = crm_sync.API
DAY = 86_400_000
AHEAD = 90 * DAY
CAL = "https://api.cal.com/v2/bookings"
CAL_VERSION = "2026-05-01"
CANCELLED = {"cancelled", "invalid", "noshow"}


def fetch(path, token, version="2021-04-15", opener=urllib.request.urlopen):
    request = urllib.request.Request(API + path, headers={"Authorization": f"Bearer {token}", "Version": version, "User-Agent": "gtm-box/1.0"})
    time.sleep(crm_sync.GAP)
    with opener(request, timeout=30) as response:
        return json.load(response)


def locations(specs):
    """Each CRM the campaigns use, with its key and location."""
    out = {}
    for crm in {spec["crm"] for spec in specs.values()}:
        out[crm] = (crm_sync.env("GHL_API_KEY"), crm_sync.env("GHL_LOCATION_ID")) if crm == crm_sync.ONE_WRITER else crm_sync.credentials(crm)
    return out


def bookings(token, location, read=fetch, now=None):
    """Live bookings from yesterday forward, from every calendar in the location."""
    now = now or int(time.time() * 1000)
    events = []
    for calendar in read(f"/calendars/?locationId={location}", token).get("calendars", []):
        data = read(f"/calendars/events?locationId={location}&calendarId={calendar['id']}&startTime={now - DAY}&endTime={now + AHEAD}", token)
        events += [e for e in data.get("events", []) if str(e.get("appointmentStatus") or "").lower() not in CANCELLED]
    return events


def cal_bookings(key, opener=urllib.request.urlopen):
    """Upcoming Cal.com bookings. Cal.com's list call pages by cursor, and a cancelled booking isn't upcoming."""
    out, cursor = [], None
    while True:
        query = {"status": "upcoming", "limit": 100, **({"cursor": cursor} if cursor else {})}
        request = urllib.request.Request(f"{CAL}?{urllib.parse.urlencode(query)}", headers={
            "Authorization": f"Bearer {key}", "cal-api-version": CAL_VERSION, "User-Agent": "gtm-box/1.0"})
        with opener(request, timeout=30) as response:
            page = json.load(response)
        out += page.get("data") or []
        cursor = (page.get("pagination") or {}).get("nextCursor")
        if not cursor:
            return out


def on_lists(specs):
    """Address to campaign, for everyone on a campaign's list."""
    people = {}
    for slug in specs:
        path = HOME / "cold" / "lists" / f"{slug}.csv"
        if path.is_file():
            with path.open(newline="") as handle:
                people.update({row["email"].strip().lower(): slug for row in csv.DictReader(handle)})
    return people


def seen():
    return set(json.loads(SEEN.read_text())) if SEEN.is_file() else set()


def take_out(email, slug, stop, hand):
    """True once they're out. A person on a list who isn't in PlusVibe yet stays unhandled and is tried again next sweep,
    so one of them can't stop the sweep or be emailed after booking."""
    try:
        stop(email, slug)
    except plusvibe.Blocked:
        return False
    hand(email, slug)
    return True


def sweep(read=fetch, stop=plusvibe.stop, hand=crm_sync.booked, cal=cal_bookings):
    specs = crm_sync.campaigns()
    people, done, stopped, waiting, blocked = on_lists(specs), seen(), 0, 0, []
    for crm, (token, location) in sorted(locations(specs).items()):
        if not token or not location:
            blocked.append(crm)
            continue
        try:
            for event in bookings(token, location, read):
                if event.get("id") in done:
                    continue
                contact = read(f"/contacts/{event.get('contactId')}", token, "2021-07-28").get("contact") or {}
                email = (contact.get("email") or "").strip().lower()
                if email in people and not take_out(email, people[email], stop, hand):
                    waiting += 1
                    continue
                stopped += email in people
                done.add(event.get("id"))
        except urllib.error.URLError as error:
            print(f"{crm}: GoHighLevel didn't answer: {getattr(error, 'code', 'no connection')}")
            blocked.append(crm)
    key = crm_sync.env("CAL_API_KEY")
    if key:
        try:
            for booking in cal(key):
                seen_id = f"cal:{booking.get('uid')}"
                if seen_id in done:
                    continue
                listed = [email for email in ((p.get("email") or "").strip().lower() for p in booking.get("attendees") or []) if email in people]
                outcomes = [take_out(email, people[email], stop, hand) for email in listed]
                stopped += sum(outcomes)
                waiting += len(outcomes) - sum(outcomes)
                if all(outcomes):
                    done.add(seen_id)
        except urllib.error.URLError as error:
            print(f"Cal.com didn't answer: {getattr(error, 'code', 'no connection')}")
            blocked.append("cal.com")
    else:
        blocked.append("cal.com")
    SEEN.parent.mkdir(parents=True, exist_ok=True)
    SEEN.write_text(json.dumps(sorted(str(item) for item in done)))
    print(json.dumps({"stopped": stopped, "waiting_to_load": waiting, "blocked": blocked}))
    return 1 if blocked else 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] != ["sweep"]:
        print(__doc__)
        return 2
    try:
        return sweep()
    except plusvibe.Blocked as why:
        print(f"BLOCKED: {why}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
