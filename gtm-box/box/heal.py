#!/usr/bin/env python3
"""The box looks after itself. Supervisor keeps this running beside the gateway, so it still works if the gateway is down.

    heal.py serve     a pass every ten minutes
    heal.py once      one pass, printing what it did
    heal.py status    when the last pass ran

It fixes only what's safe to fix and can be undone: a stopped service, a job whose next run drifted or was missed, a
research run left stuck, a day's research that never fired. Everything else goes to Justin in Slack, once every six hours.

It never turns on a paused job, because a person may have paused it. It never sends, spends or deletes. With STOP set it
only watches. Slack goes straight to the API, so an alarm doesn't need the gateway it may be reporting.
"""
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = Path(__file__).resolve().parent
BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or BOX_HOME)
sys.path.insert(0, str(HOME / "box" if (HOME / "box" / "goal.py").is_file() else HERE))

import goal  # noqa: E402

PROFILES = Path(os.environ.get("HERMES_PROFILES", "/root/.hermes/profiles"))
HERMES = "/usr/local/bin/hermes"
RUNNER = os.environ.get("SPEAKER_RUNNER", str(Path.home() / "speakeragent" / "runtime" / "daily.py"))
SERVICES = ("hermes-gateway", "gtm-guard")
PASS_SECONDS = 600
RESTART_SECONDS = 15
LATE_MINUTES = 30  # Longer than a research cycle's 15-minute limit, so a run still going is never called missed.
ALARM_HOURS = 6
FAILED_HOURS = 3
CATCH_UP_HOUR_UTC = 20  # Past the last research slot, a day with no cycle gets one more try.
SUPPRESSION_DAYS = 7


def now():
    return dt.datetime.now(dt.timezone.utc)


def field_matches(expr, value):
    if expr == "*":
        return True
    if not re.fullmatch(r"\d+(,\d+)*", expr):
        return True  # A step or a range: not worth parsing here, so don't call it drift.
    return value in {int(part) for part in expr.split(",")}


def drifted(job, when=None):
    """Why an enabled cron job needs replanning, or None. The gateway plans in UTC, so a next run is judged in UTC."""
    schedule = job.get("schedule") or {}
    if not job.get("enabled") or schedule.get("kind") != "cron":
        return None
    when = when or now()
    if not job.get("next_run_at"):
        return "has no next run"
    planned = dt.datetime.fromisoformat(job["next_run_at"]).astimezone(dt.timezone.utc)
    if planned < when - dt.timedelta(minutes=LATE_MINUTES):
        return f"missed its run at {planned:%H:%M} UTC"
    minute, hour, *_ = schedule["expr"].split()
    if not (field_matches(minute, planned.minute) and field_matches(hour, planned.hour)):
        return f"is planned for {planned:%H:%M} UTC, off its schedule of {schedule['expr']}"
    return None


def failed(job, when=None):
    """An enabled job whose latest run ended in an error. Only a fresh one, so an old failure doesn't page anyone."""
    if not job.get("enabled") or job.get("last_status") != "error" or not job.get("last_run_at"):
        return False
    ran = dt.datetime.fromisoformat(job["last_run_at"]).astimezone(dt.timezone.utc)
    return (when or now()) - ran < dt.timedelta(hours=FAILED_HOURS)


def jobs():
    for path in sorted(PROFILES.glob("*/cron/jobs.json")):
        data = goal.read(path, {}) or {}
        for job in data.get("jobs", []):
            yield path.parent.parent.name, job


def supervised():
    """Services that aren't running, or None when supervisor can't be asked."""
    if not shutil.which("supervisorctl"):
        return None
    done = subprocess.run(["supervisorctl", "status", *SERVICES], capture_output=True, text=True, timeout=30)
    return [line.split()[0] for line in done.stdout.splitlines()
            if line.strip() and "RUNNING" not in line and "STARTING" not in line]


def replan(profile, job):
    env = {**os.environ, "HERMES_HOME": str(PROFILES / profile)}
    done = subprocess.run([HERMES, "cron", "edit", job["id"], "--schedule", job["schedule"]["expr"]], env=env,
                          capture_output=True, text=True, timeout=60)
    return done.returncode == 0


def stuck_run(workspace):
    """The run a recovery marker names, when nothing from it is alive. Research can't send, so clearing it is safe."""
    marker = goal.read(workspace / "RECOVERY_REQUIRED.json")
    if not marker:
        return None
    table = subprocess.run(["ps", "-eo", "pid,etime,command"], capture_output=True, text=True, timeout=30).stdout
    if marker["run_id"] in table:
        return None
    return marker["run_id"], table


def reconcile(workspace, run_id, table):
    folder = HOME / "goal" / "evidence"
    folder.mkdir(parents=True, exist_ok=True)
    evidence = folder / f"{run_id}.txt"
    evidence.write_text(f"No process carries run {run_id}, checked {now().isoformat()}.\n\n{table}")
    done = subprocess.run([sys.executable, RUNNER, "reconcile", "--workspace", str(workspace), "--run-id", run_id,
                           "--evidence-file", str(evidence)], capture_output=True, text=True, timeout=60)
    return done.returncode == 0


def research_missed(workspace, when=None):
    """True when today's slots have all passed and no cycle ran."""
    when = when or now()
    if when.hour < CATCH_UP_HOUR_UTC or not workspace.is_dir():
        return False
    day = goal.today(when)
    state = goal.read(HOME / "goal" / f"research-{day}.json", {}) or {}
    return not state.get("cycles") and not (HOME / "goal" / f"catch-up-{day}").exists()


def spend_line():
    done = subprocess.run([sys.executable, str(HOME / "box" / "spend_guard.py"), "status"], capture_output=True, text=True,
                          timeout=30)
    return done.stdout.strip().splitlines()[-1] if done.stdout.strip() else ""


def spend_alarm(line):
    found = re.search(r"\$([\d.]+) of \$([\d.]+)", line)
    if found and float(found.group(2)) and float(found.group(1)) / float(found.group(2)) >= 0.8:
        return f"Spend is at {found.group(0)} today. At the cap the gate refuses every job until midnight UTC."
    return None


def machine_alarms(root="/"):
    out = []
    disk = shutil.disk_usage(root)
    if disk.used / disk.total > 0.85:
        out.append(f"Disk is {disk.used / disk.total:.0%} full.")
    try:
        info = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
        total, free = (int(info[k].split()[0]) for k in ("MemTotal", "MemAvailable"))
        if free / total < 0.15:
            out.append(f"Memory is {1 - free / total:.0%} used.")
    except (OSError, KeyError, ValueError):
        pass
    return out


def list_alarm(when=None):
    path = HOME / "suppression.csv"
    if not path.is_file():
        return "The suppression list is missing, so no draft reaches the queue. Run sync_suppression.sh on the Mac."
    age = ((when or now()).timestamp() - path.stat().st_mtime) / 86400
    if age > SUPPRESSION_DAYS:
        return f"The suppression list is {age:.0f} days old, and only the Mac can refresh it. Run sync_suppression.sh."
    return None


def log(what, when=None):
    path = HOME / "goal" / "heal.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps({"at": (when or now()).isoformat(), "what": what}) + "\n")


def secrets():
    out = {}
    try:
        lines = (HOME / "box.env").read_text().splitlines()
    except OSError:
        return out
    for line in lines:
        key, _, value = line.partition("=")
        if key in ("SLACK_BOT_TOKEN", "SLACK_HOME_CHANNEL"):
            out[key] = value.strip().strip('"')
    return out


def post(text):
    keys = secrets()
    if not keys.get("SLACK_BOT_TOKEN") or not keys.get("SLACK_HOME_CHANNEL"):
        return False
    body = urllib.parse.urlencode({"channel": keys["SLACK_HOME_CHANNEL"], "text": text}).encode()
    request = urllib.request.Request("https://slack.com/api/chat.postMessage", data=body,
                                     headers={"Authorization": "Bearer " + keys["SLACK_BOT_TOKEN"]})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return bool(json.load(response).get("ok"))
    except (OSError, ValueError):
        return False


def alarm(text, when=None, sender=post):
    """One message for one problem every ALARM_HOURS, so a stuck fault doesn't page Justin all night."""
    when = when or now()
    path = HOME / "goal" / "alarms.json"
    seen = goal.read(path, {}) or {}
    last = seen.get(text)
    if last and when - dt.datetime.fromisoformat(last) < dt.timedelta(hours=ALARM_HOURS):
        return False
    if sender(f"Box alarm: {text}"):
        seen[text] = when.isoformat()
        goal.write(path, seen)
        return True
    return False


def run_pass(when=None, sender=post):
    """One look at everything. Returns (what it fixed, what it raised)."""
    when = when or now()
    fixed, raised = [], []
    stopped = (HOME / "STOP").exists()
    workspace = HOME / "speaker"
    down = supervised()
    for name in down or []:
        if stopped:
            continue
        subprocess.run(["supervisorctl", "start", name], capture_output=True, timeout=60)
        time.sleep(RESTART_SECONDS)  # Give it time to come up, or a slow start reads as a failure and pages Justin.
        still = supervised() or []
        (raised if name in still else fixed).append(f"{name} was down" + (" and won't start" if name in still else ", restarted"))
    for profile, job in jobs():
        if failed(job, when):
            raised.append(f"{profile} {job.get('name') or job['id']} ended its last run in an error")
        problem = drifted(job, when)
        if not problem:
            continue
        label = f"{profile} {job.get('name') or job['id']}"
        if stopped:
            continue
        if replan(profile, job):
            fixed.append(f"{label} {problem}, replanned")
        else:
            raised.append(f"{label} {problem}, and replanning failed")
    stuck = stuck_run(workspace)
    if stuck and not stopped:
        if reconcile(workspace, *stuck):
            fixed.append(f"research run {stuck[0]} was left stuck, cleared")
        else:
            raised.append(f"research run {stuck[0]} is stuck and couldn't be cleared")
    if research_missed(workspace, when) and not stopped:
        (HOME / "goal" / f"catch-up-{goal.today(when)}").touch()
        subprocess.Popen([sys.executable, str(HOME / "box" / "speaker_cycle.py")], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        fixed.append("no research had run today, so one cycle was started")
    for problem in [list_alarm(when), spend_alarm(spend_line()), *machine_alarms()]:
        if problem:
            raised.append(problem)
    for item in fixed:
        log(item, when)
    for item in raised:
        alarm(item, when, sender)
    goal.write(HOME / "goal" / "heal.json", {"at": when.isoformat(), "fixed": fixed, "raised": raised})
    return fixed, raised


def main(argv):
    command = argv[1] if len(argv) > 1 else "once"
    if command == "status":
        print(json.dumps(goal.read(HOME / "goal" / "heal.json", {}), indent=2))
        return 0
    if command == "once":
        fixed, raised = run_pass()
        print("\n".join([*[f"fixed: {x}" for x in fixed], *[f"raised: {x}" for x in raised]]) or "all clear")
        return 0
    while True:
        try:
            run_pass()
        except Exception as problem:  # The healer must outlive whatever it's looking at.
            print(f"pass failed: {problem}", flush=True)
        time.sleep(PASS_SECONDS)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
