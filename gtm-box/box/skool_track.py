#!/usr/bin/env python3
"""Every Skool lead, in the CRM and the sheet. It spends no model money.

The radar's pipeline is the record of who was found and what happened. This copies it out: each person goes through crm.py,
the one writer, so suppression holds them and closer's drain does the writing once Justin's CRM yes is in place. A sheet file
goes next to it for the Mac to put in his Google Sheet, because Google sign-ins don't live on this box.

    skool_track.py run       hand new people to the CRM, write the sheet file
    skool_track.py report    the charter's scoreboard line, for Slack
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
sys.path.insert(0, str(HOME / "box" if (HOME / "box" / "goal.py").is_file() else Path(__file__).resolve().parent))

import beat  # noqa: E402
import crm  # noqa: E402
import skool_worker  # noqa: E402

CAMPAIGN = "Skool"
COLUMNS = ("Name", "Intent", "Stage", "Group", "What they need", "Their words", "Profile", "Their post", "Last seen", "Next",
           "Note", "Grade")
ANSWERED = ("answered", "call", "won")
GROUP_COLUMNS = ("Group", "Last read", "Read from", "New posts", "New comments", "Note")


def pipeline(cfg, http=skool_worker.http):
    return http("GET", cfg["RADAR_URL"].rstrip("/") + "/api/pipeline?platform=skool",
                {"Authorization": f"Bearer {cfg['RADAR_DASHBOARD_PASSWORD']}"}, timeout=60)[1]


def group(person):
    parts = urlsplit(person.get("url") or "").path.strip("/").split("/")
    return person.get("community") or (parts[0] if parts and parts[0] else "")


def lead(person):
    """What crm.py needs. Skool keeps every email empty, so the profile address is who they are.

    Everyone becomes a contact with the lane's tag, so everyone is tracked. A card is a promise of a dated next step, and the
    no-open-loops sweep holds the team to it, so only someone we owe a move gets one: high intent, or anyone who answered.
    """
    out = {"lane": "skool", "name": person.get("name"), "skool": str(person.get("profile_url") or "").split("?")[0],
           "campaign": CAMPAIGN}
    answered = person.get("stage") in ANSWERED
    if answered or person.get("intent") == "high":
        need = " ".join(str(person.get("need") or "").split())[:240]
        out |= {"evidence_type": "reply" if answered else "public-ask", "evidence_ref": person.get("url"),
                "evidence": f"{person.get('intent')} intent. {need}".strip()}
    return out


def row(person, grade="pipeline"):
    return [person.get("name") or "", person.get("intent") or "", person.get("stage") or "", group(person),
            person.get("need") or "", person.get("quote") or "", person.get("profile_url") or "", person.get("url") or "",
            person.get("last_seen") or "", person.get("next") or "", person.get("note") or "", grade]


def group_rows(report):
    return [[g.get("name") or g.get("slug") or "", g.get("status") or "", g.get("since") or "", g.get("posts") or 0,
             g.get("comments") or 0, g.get("note") or ""] for g in (report or {}).get("groups") or []]


def sheet(people, report=None, path=None, when=None):
    """The whole list, highest intent first. Written whole each time, so a row always matches the pipeline."""
    path = Path(path or HOME / "skool" / "sheet.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {"updated": (when or dt.datetime.now(dt.timezone.utc)).isoformat(timespec="seconds"), "columns": list(COLUMNS),
            "rows": [row(p) for p in people], "group_columns": list(GROUP_COLUMNS), "groups": group_rows(report)}
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(body))
    os.replace(tmp, path)
    return len(body["rows"])


def track(people, add=crm.add, lists=None):
    """Counts of what the CRM did with each person. One bad row never stops the rest."""
    counts = {"queued": 0, "already queued": 0, "held": 0, "skipped": 0}
    for person in people:
        if not person.get("profile_url") or "no-contact" in (person.get("next") or ""):
            counts["skipped"] += 1
            continue
        try:
            status = add(lead(person), apply=True, lists=lists)["status"]
        except ValueError:
            status = "skipped"
        counts[status] = counts.get(status, 0) + 1
    return counts


def scoreboard(data):
    report = data.get("sweep") or {}
    counts = report.get("counts") or {}
    return (f"groups {report.get('groups_done', 0)} of {report.get('groups_total', 0)} | new posts {counts.get('skool_posts_new', 0)} | "
            f"new comments {counts.get('skool_comments_new', 0)} | joined today {joined_today()} | leads {data.get('total', 0)}")


def joined_today(path=None, day=None):
    """The join job logs one line per group it joined."""
    path = Path(path or HOME / "skool" / "joined.log")
    if not path.is_file():
        return 0
    day = day or dt.datetime.now(dt.timezone.utc).date().isoformat()
    return sum(line.startswith(day) for line in path.read_text().splitlines())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("run", "report"))
    args = ap.parse_args(argv)
    cfg = skool_worker.keys(HOME / "box.env")
    try:
        data = pipeline(cfg)
    except skool_worker.GONE:
        beat.write("skool", "couldn't read the radar's pipeline", ["blocked=1"])
        print("Couldn't read the radar's pipeline.")
        return 0
    if args.cmd == "report":
        print(scoreboard(data))
        return 0
    people = data.get("people") or []
    counts = track(people, lists=crm.load_lists())
    rows = sheet(people, data.get("sweep"))
    beat.write("skool", f"pipeline {data.get('total', 0)}, sheet {rows} rows, CRM {counts}",
               [f"found={data.get('total', 0)}", f"leads={counts['queued']}"])
    print(json.dumps({"sheet_rows": rows, **counts}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
