#!/usr/bin/env python3
"""The GTM box's heartbeat and scoreboard. Every profile writes one line a run; gtm-lead reads them.

    beat.py write <profile> "<one line>" found=3 drafted=2 sent=0 replies=0 leads=0 booked=0 blocked=0
    beat.py check                 silent, blocked or idle profiles with a job on, and STOP; exits 1 when something needs Slack
    beat.py board                 one scoreboard line per profile, then today against the KPI
"""
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")  # Fixed on the box: a profile's shell may not see GTM_HOME or the real home folder.
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
JOBS = Path(os.environ.get("HERMES_PROFILES", "/root/.hermes/profiles"))
PROFILES = ["gtm-lead", "closer", "replies", "opener", "deals", "warm", "linkedin", "rev-partner", "skool", "lead-radar",
            "podcast", "seo-aeo", "content", "plusvibe-operator", "copywriter", "cold-email", "data", "prospector", "lead", "speaker", "sales-crm", "outbound", "social", "content-seo", "partners", "dream", "capital"]
SILENT_HOURS = 26
COUNTS = ("found", "drafted", "sent", "replies", "leads", "booked", "overdue", "blocked")
WORK = ("found", "drafted", "sent", "replies", "leads", "booked")
IDLE_RUNS = 3  # A status of ok proves nothing. A profile that ran this many times in a day and counted no work is an alarm.
IDLE_HOURS = 24
KPI = {"leads": 100, "booked": 8}
STALE_BOARD_HOURS = 8  # The sweep runs three times a day, so a board older than this means it stopped.
OUTBOX_HOURS = 2  # GoHighLevel down for this long is an alarm. The leads are safe, but nobody is working them.


def now():
    return dt.datetime.now(dt.timezone.utc)


def path(profile):
    return HOME / "heartbeat" / f"{profile}.json"


def write(profile, line, metrics, when=None):
    if profile not in PROFILES:
        raise SystemExit(f"unknown profile: {profile}")
    numbers = {}
    for pair in metrics:
        key, _, value = pair.partition("=")
        if key not in COUNTS or not value.isdigit():
            raise SystemExit(f"bad count: {pair} (use {', '.join(COUNTS)}, whole numbers)")
        numbers[key] = int(value)
    path(profile).parent.mkdir(parents=True, exist_ok=True)
    record = {"profile": profile, "at": (when or now()).isoformat(), "line": line, **numbers}
    path(profile).write_text(json.dumps(record))
    with (HOME / "heartbeat" / "history.jsonl").open("a") as f:
        f.write(json.dumps(record) + "\n")


def read(profile):
    try:
        return json.loads(path(profile).read_text())
    except (FileNotFoundError, ValueError):
        return None


def working():
    """Profiles with a job switched on. A paused agent isn't silent, it's off, so only these can raise an alarm.
    Off the box, or with a jobs file that can't be read, a profile counts as working: a bad read must alarm, not hide."""
    if not JOBS.is_dir():
        return set(PROFILES)
    out = set()
    for p in PROFILES:
        try:
            jobs = json.loads((JOBS / p / "cron" / "jobs.json").read_text())["jobs"]
        except (OSError, ValueError, KeyError):
            out.add(p)
            continue
        if any(job.get("enabled") for job in jobs):
            out.add(p)
    return out


def silent(when=None, on=None):
    """Working profiles that never wrote a heartbeat, or wrote their last one more than SILENT_HOURS ago.
    gtm-lead runs this check, so it can't report itself, and it writes no heartbeat of its own."""
    when = when or now()
    on = working() if on is None else on
    out = []
    for p in PROFILES:
        if p == "gtm-lead" or p not in on:
            continue
        beat = read(p)
        if not beat:
            out.append((p, "no heartbeat yet"))
            continue
        hours = (when - dt.datetime.fromisoformat(beat["at"])).total_seconds() / 3600
        if hours > SILENT_HOURS:
            out.append((p, f"silent {hours:.0f} hours"))
    return out


def history():
    try:
        lines = (HOME / "heartbeat" / "history.jsonl").read_text().splitlines()
    except FileNotFoundError:
        return []
    return [json.loads(line) for line in lines if line.strip()]


def blocked(on=None):
    """A run that says it couldn't do its work. Hermes still calls that run ok, so the heartbeat has to say it."""
    on = working() if on is None else on
    return [(p, beat["line"]) for p in PROFILES if p in on and (beat := read(p)) and beat.get("blocked")]


def idle(past=None, when=None, on=None):
    """Profiles that ran at least IDLE_RUNS times in the last day and counted no work. Reply loops run every 30 minutes,
    so going by the last few runs would raise an alarm every quiet afternoon."""
    past = history() if past is None else past
    since = (when or now()) - dt.timedelta(hours=IDLE_HOURS)
    on = working() if on is None else on
    out = []
    for p in PROFILES:
        if p == "gtm-lead" or p not in on:  # gtm-lead reports on the others and counts nothing of its own.
            continue
        runs = [r for r in past if r.get("profile") == p and dt.datetime.fromisoformat(r["at"]) >= since]
        if len(runs) >= IDLE_RUNS and not any(r.get(k) for r in runs for k in WORK):
            out.append(p)
    return out


def crm_board():
    """What the open-loops job last found. gtm-lead and the CRM team read this same record."""
    try:
        return json.loads((HOME / "crm" / "board.json").read_text())
    except (FileNotFoundError, ValueError):
        return None


def crm_problems(when=None):
    """Anything past its date, held in the pipeline or stuck in the outbox. No board yet means the job isn't on: no alarm."""
    board_now = crm_board()
    if not board_now:
        return []
    out = []
    hours = ((when or now()) - dt.datetime.fromisoformat(board_now["at"])).total_seconds() / 3600
    if hours > STALE_BOARD_HOURS:
        out.append(f"crm: the open-loops sweep hasn't run in {hours:.0f} hours")
    if board_now.get("past_due"):
        out.append(f"crm: {board_now['past_due']} open loops are past due")
    if board_now.get("held"):
        out.append(f"crm: {board_now['held']} held records are in the Sales pipeline")
    # With writes off, or the backlog held while a tester goes first, the outbox is meant to wait.
    should_drain = (HOME / "crm" / "WRITES_ON").exists() and not (HOME / "crm" / "DRAIN_HOLD").exists()
    if board_now.get("outbox_oldest_hours", 0) > OUTBOX_HOURS and should_drain:
        out.append(f"crm: the outbox has waited {board_now['outbox_oldest_hours']:.0f} hours")
    return out


def healer_problems(when=None):
    """heal.py watches the jobs and this check watches heal.py. No record yet means it was never installed: no alarm."""
    try:
        last = json.loads((HOME / "goal" / "heal.json").read_text())["at"]
    except (OSError, ValueError, KeyError):
        return []
    minutes = ((when or now()) - dt.datetime.fromisoformat(last)).total_seconds() / 60
    return [f"heal.py last ran {minutes:.0f} minutes ago"] if minutes > 30 else []


def sender_problems(when=None):
    """A STOP that hasn't reached the sender, and a send nobody can vouch for. Quiet until the sender is really in use."""
    try:
        state = json.loads((HOME / "crm" / "sender-state.json").read_text())
    except (FileNotFoundError, ValueError):
        return []
    if not state.get("configured"):
        return []
    out = []
    oldest = state.get("opt_outs_oldest")
    if oldest and ((when or now()) - dt.datetime.fromisoformat(oldest)).total_seconds() / 3600 > OUTBOX_HOURS:
        out.append(f"crm: {state['opt_outs_waiting']} opt-outs haven't reached the sender")
    if (state.get("drafts") or {}).get("unknown"):
        out.append(f"crm: {state['drafts']['unknown']} sends may have gone, and the sender can't say: check by hand")
    return out


def check(when=None):
    on = working()
    problems = [f"{p}: {why}" for p, why in silent(when, on)]
    problems += [f"{p}: blocked: {line}" for p, line in blocked(on)]
    problems += [f"{p}: no work counted in {IDLE_HOURS} hours" for p in idle(when=when, on=on)]
    if "closer" in on:  # closer's open-loops job writes the board, so a paused CRM team leaves an old board behind.
        problems += crm_problems(when)
    problems += sender_problems(when)
    problems += healer_problems(when)
    if (HOME / "STOP").exists():
        problems.insert(0, "STOP is set: nothing sends")
    return problems


def today(when=None):
    """The day's totals by UTC date. Lanes count leads and only closer counts booked, so a booking isn't counted twice."""
    day = (when or now()).date().isoformat()
    runs = [r for r in history() if r.get("at", "").startswith(day)]
    return {"leads": sum(r.get("leads", 0) for r in runs),
            "booked": sum(r.get("booked", 0) for r in runs if r.get("profile") == "closer")}


def board():
    rows = []
    for p in PROFILES:
        beat = read(p)
        if not beat:
            rows.append(f"{p}: no heartbeat yet")
            continue
        counts = " ".join(f"{k} {beat[k]}" for k in COUNTS if k in beat)
        rows.append(f"{p}: {beat['line']}" + (f" ({counts})" if counts else ""))
    totals = today()
    rows.append(f"today: leads {totals['leads']} of {KPI['leads']}, booked {totals['booked']} of {KPI['booked']} to 10")
    try:
        import goal
        rows += goal.lines()
    except Exception as problem:  # The board must still print if the goal ledger can't be read.
        rows.append(f"goal: can't read it ({problem})")
    crm = crm_board()
    if crm:
        lanes = ", ".join(f"{k} {v}" for k, v in sorted(crm.get("lanes", {}).items())) or "none"
        rows.append(f"crm: {crm['open']} open, {crm['past_due']} past due, {crm['held']} held. By lane: {lanes}. As of {crm['at'][:16]}")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("profile")
    w.add_argument("line")
    w.add_argument("metrics", nargs="*")
    sub.add_parser("check")
    sub.add_parser("board")
    a = ap.parse_args(argv)
    if a.cmd == "write":
        write(a.profile, a.line, a.metrics)
    elif a.cmd == "board":
        print("\n".join(board()))
    else:
        problems = check()
        print("\n".join(problems) if problems else "every agent with a job on has checked in")
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
