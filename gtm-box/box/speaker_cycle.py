#!/usr/bin/env python3
"""One podcast research slot. Hermes runs this hourly through the working day, with no model of its own.

It stops as soon as today's shows are found or today's cycles are spent, so a spare slot costs nothing. SpeakerAgent's
runner allows one cycle a day, which is the runner's limit and not the goal's, so later cycles pass --force.

STOP stops this job too. The runner has its own stop file and doesn't read the box's.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or BOX_HOME)
sys.path.insert(0, str(HOME / "box" if (HOME / "box" / "goal.py").is_file() else HERE))

import goal  # noqa: E402
import speaker_cases  # noqa: E402

RUNNER = os.environ.get("SPEAKER_RUNNER", str(Path.home() / "speakeragent" / "runtime" / "daily.py"))


def run(*args, timeout=1200):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, timeout=timeout)


def beat(line, **counts):
    script = HOME / "box" / "beat.py"
    if script.is_file():
        run(script, "write", "podcast", line, *[f"{k}={v}" for k, v in counts.items()], timeout=30)


def cycle(workspace=None, day=None, runner=RUNNER, cfg=None):
    """Returns one plain line saying what happened. It always says whether research really ran."""
    workspace = Path(workspace or HOME / "speaker")
    cfg = cfg or goal.settings()
    day = day or goal.today()
    if (HOME / "STOP").exists():
        return "stopped: STOP is set, so no research ran"
    preflight = HOME / "box" / "preflight.py"
    if preflight.is_file():
        result = run(preflight, "podcast", timeout=60).stdout
        if "PREFLIGHT FAILED" in result:
            return f"blocked: {result.strip()}"
    # One case with a pay word the validator refuses fails the whole run, and the model writes them, so mend them first.
    speaker_cases.repair(workspace / "cases")
    path = HOME / "goal" / f"research-{day}.json"
    state = goal.read(path, {"cycles": 0, "new_shows": 0, "accepted_start": goal.accepted(workspace)})
    quotas = cfg["quotas"]
    found = goal.accepted(workspace) - state["accepted_start"]
    if found >= quotas["shows"]:
        return f"done: {found} new accepted shows today, so this slot was skipped"
    if state["cycles"] >= quotas["cycles"]:
        return f"done: all {quotas['cycles']} cycles ran today, {found} new accepted shows"
    if state["cycles"] == 0:
        learn = HOME / "box" / "learn.py"
        if learn.is_file():
            run(learn, timeout=60)
            cfg = goal.settings()
        goal.roll(workspace, day, cfg)
    before = len(goal.cases(workspace))
    args = [runner, "run", "--workspace", workspace]
    if (workspace / "days" / f"{day}.json").exists():
        args.append("--force")
    done = run(*args)
    try:
        outcome = json.loads(done.stdout)
    except ValueError:
        outcome = {"status": "failed", "reason": (done.stderr or done.stdout).strip()[-300:]}
    status = outcome.get("status")
    if status == "already_ran":
        return f"already_ran: the runner did no research for {day}"
    new = len(goal.cases(workspace)) - before
    state["cycles"] += 1
    state["new_shows"] += new
    state.setdefault("runs", []).append({"run_id": outcome.get("run_id"), "status": status, "new": new,
                                         "seconds": outcome.get("elapsed_seconds")})
    goal.write(path, state)
    scan = HOME / "box" / "suppression.py"
    if scan.is_file():
        run(scan, "scan", timeout=120)
    if status in ("failed", "blocked", "timed_out", "interrupted"):
        return f"failed: research {status}: {outcome.get('reason') or 'see the run log'}"
    return f"ran: cycle {state['cycles']}, {status}, {new} new shows, {goal.accepted(workspace)} accepted on file"


def main():
    line = cycle()
    print(line)
    kind = line.split(":")[0]
    if kind in ("blocked", "failed"):
        beat(f"Research {line}", blocked=1)
    elif kind == "ran":
        have = goal.supply()
        beat(f"Research {line}", found=have["new_shows"], drafted=have["pitches_ready"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
