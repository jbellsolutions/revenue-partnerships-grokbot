#!/usr/bin/env python3
"""On the box: bring each profile's cron jobs up to the pack. `hermes profile install --force` left dropped jobs behind.

Prompts, schedules and names come from the pack. Whether a job is on stays as it is, so a rerun never turns a job on or
off. A job the pack dropped goes, except script jobs, such as the one SpeakerAgent's schedule.py creates.

    python3 sync_jobs.py <pack build dir> <profiles dir>
    python3 sync_jobs.py scripts <profiles.json> <profiles dir> <crm_job.py>     one copy of the shim per CRM job, by name
"""
import json
import os
import shutil
import sys
from pathlib import Path

FROM_PACK = ("name", "prompt", "schedule", "schedule_display", "deliver", "script", "no_agent")


def merge(shipped, current):
    known = {job["id"]: job for job in current}
    merged = [{**known[job["id"]], **{key: job.get(key) for key in FROM_PACK}} if job["id"] in known else job
              for job in shipped]
    ids = {job["id"] for job in shipped}
    # A script job someone else made stays. The preflight every pack job gets doesn't make a dropped job one of those.
    return merged + [job for job in current if job["id"] not in ids and job.get("script") not in (None, "preflight.py")]


def sync(build, profiles):
    changed = {}
    for pack in sorted(Path(build).glob("*/cron/jobs.json")):
        name = pack.parent.parent.name
        target = Path(profiles) / name / "cron" / "jobs.json"
        if not target.is_file():
            continue
        data = json.loads(target.read_text())
        before = data["jobs"]
        data["jobs"] = merge(json.loads(pack.read_text())["jobs"], before)
        if data["jobs"] != before:
            scratch = target.with_suffix(".tmp")
            scratch.write_text(json.dumps(data, indent=2))
            os.replace(scratch, target)
            changed[name] = len(data["jobs"])
    return changed


def job_scripts(specs, shim_names):
    """(profile, script) for every job that runs the shim. Other scripts, such as preflight.py, are installed on their own."""
    return [(name, job["script"]) for name, spec in specs.items() for job in spec["jobs"]
            if job.get("script") and job["script"].removesuffix(".py") in shim_names]


def install_scripts(specs_path, profiles, shim):
    sys.path.insert(0, str(Path(shim).parent))
    from crm_job import JOBS
    pairs = job_scripts(json.loads(Path(specs_path).read_text()), JOBS)
    for name, script in pairs:
        folder = Path(profiles) / name / "scripts"
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copy(shim, folder / script)
    return pairs


if __name__ == "__main__":
    if sys.argv[1] == "scripts":
        print("job scripts:", len(install_scripts(*sys.argv[2:5])))
    else:
        print("jobs updated:", sync(sys.argv[1], sys.argv[2]) or "none")
