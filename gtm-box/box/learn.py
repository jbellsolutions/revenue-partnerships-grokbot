#!/usr/bin/env python3
"""What the podcast lane has learned, rebuilt from the saved results before the day's first research cycle.

It writes two things: goal/lessons.md, which the research agent reads before it searches, and goal/settings.json, the
day's quotas. Nothing here touches persona.json or Justin's approved claims. Those are his words, not something to tune.

Learning is counted from the files, so it can't be argued with: which shows were turned down and why, what got accepted,
and once pitches go out, what got replies and bookings.
"""
import collections
import math
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or BOX_HOME)
sys.path.insert(0, str(HOME / "box" if (HOME / "box" / "goal.py").is_file() else HERE))

import goal  # noqa: E402

MAX_CYCLES = 6
COST_CEILING = 3.0  # Dollars a day for research, so the $5 gate still has room for every other lane.
COST_PER_CYCLE = 0.30  # Measured: $0.32 on 2026-11-05, about $0.25 on 2026-11-06.
SKIP = (("Turns away people who sell AI services", r"sell(s|ing)? (an )?ai|ai (vendor|service)|consultants? selling"),
        ("Charges guests to appear", r"\bfee\b|paid (slot|appearance|guest|package)|payment|pay to"),
        ("Audience or guests are limited in a way Justin doesn't fit", r"women|\buk\b|only|non-tech"),
        ("Trades and builder shows, which Justin ruled out", r"trades?\b|contractor|builder show|out of scope"),
        ("No working booking route", r"no (guest |official )?route|not found|404"),
        ("Feed looks stale", r"stale|recency|not visible"))


def bucket(reason):
    for label, pattern in SKIP:
        if re.search(pattern, reason or "", re.I):
            return label
    return "Other"


def cycle_quota(shows, rate, ceiling=COST_CEILING):
    """Cycles to find today's accepted shows at the measured rate, up to what the budget allows."""
    if not rate:
        return 3
    return max(1, min(MAX_CYCLES, int(ceiling / COST_PER_CYCLE), math.ceil(shows / rate)))


def lessons(cases, events, decisions=""):
    total = len(cases)
    took = [c for c in cases if c.get("qualification") == "accepted"]
    gone = [c for c in cases if c.get("qualification") == "rejected"]
    reasons = collections.Counter(bucket((c.get("fit") or {}).get("reason")) for c in gone)
    topics = collections.Counter((c.get("fit") or {}).get("best_topic") or "not recorded" for c in took)
    routes = collections.Counter((c.get("route") or {}).get("type") or "none" for c in took)
    out = ["# What the podcast lane has learned", "",
           "Written by learn.py from the saved cases and the goal ledger. Don't edit it. Use it to choose where you search.", "",
           f"{total} shows reviewed: {len(took)} accepted, {len(gone)} rejected.", ""]
    if reasons:
        out += ["## Don't spend time on these", *[f"- {name}: {n} so far" for name, n in reasons.most_common()], ""]
    if took:
        out += ["## What has been getting accepted", "Best topics: " + ", ".join(f"{t} ({n})" for t, n in topics.most_common()),
                "Booking routes: " + ", ".join(f"{t} ({n})" for t, n in routes.most_common()), ""]
    names = sorted(c.get("name") or "" for c in gone)
    if names:
        out += ["## Already rejected, so never reconsider", *[f"- {n}" for n in names], ""]
    pitched = sum(e["kind"] == "pitched" for e in events)
    booked = sum(e["kind"] == "booked" for e in events)
    out += ["## Outcomes", f"{pitched} pitches sent, {booked} booked."]
    if decisions.strip():
        out += ["", "## Justin's decisions", decisions.strip()]
    return "\n".join(out) + "\n"


def main():
    cases, events = goal.cases(), goal.ledger()
    cfg = goal.settings()
    decisions_file = HOME / "goal" / "decisions.md"
    decisions = decisions_file.read_text() if decisions_file.is_file() else ""
    text = lessons(cases, events, decisions)
    folder = HOME / "goal"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "lessons.md").write_text(text)
    vault = HOME / "vault" / "projects" / "our-aios" / "gtm-box"
    if vault.is_dir():
        (vault / "podcast-lessons.md").write_text(text)
    reviewed = max(len(cases), 1)
    rate = sum(c.get("qualification") == "accepted" for c in cases) / reviewed
    pitched = sum(e["kind"] == "pitched" for e in events)
    booked = sum(e["kind"] == "booked" for e in events)
    quotas = {"pitches": goal.quota_from_rate(pitched, booked)}
    # A cycle reviews about eight shows, so the accepted rate says how many cycles a day's shows take.
    quotas["cycles"] = cycle_quota(cfg["quotas"]["shows"], rate * 8)
    goal.write(folder / "settings.json", {"quotas": quotas, "accepted_rate": round(rate, 3), "reviewed": len(cases)})
    print(f"{len(cases)} shows, {rate:.0%} accepted, {quotas['cycles']} cycles a day, {quotas['pitches']} pitches a day")
    return 0


if __name__ == "__main__":
    sys.exit(main())
