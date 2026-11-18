#!/usr/bin/env python3
"""gtm-lead gives another profile work, so Justin gives one instruction and the right agent runs it.

    dispatch.py start <profile> "<instruction>"   prints a job id. The answer goes to #revenue-partnerships when the run ends
    dispatch.py result <job>                      the state of a job, and its answer once it's done
    dispatch.py list                              jobs still running

A paused cron job can't be run on demand, so each job is its own one-shot Hermes run in that profile. It loads that
profile's charter and its rules, and it can only do what that profile can do: this hands over work, not permissions.
The instruction goes through a file, so nothing a chat says is ever part of a shell command.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

BOX_HOME = Path("/workspace/revenue-partnerships/gtm-box")
HOME = Path(os.environ.get("GTM_HOME") or (BOX_HOME if BOX_HOME.is_dir() else Path.home() / ".gtm-box"))
PROFILES_DIR = Path(os.environ.get("HERMES_PROFILES", "/root/.hermes/profiles"))
HERMES = os.environ.get("HERMES_BIN", "hermes")
JOB_ID = re.compile(r"^[a-f0-9]{16}$")
PROFILE = re.compile(r"^[a-z][a-z0-9-]{1,40}$")
MAX_RUNNING = 2  # This computer has one vCPU.
MAX_REQUEST = 8000
MAX_POST = 3500
RUN_LIMIT = 1800  # Seconds. A job past this is stopped and reported.
HEADER = ("[From gtm-lead, passing on Justin's instruction. Your charter and every gate still apply. "
          "If it needs something your charter forbids, say so and stop.]\n\n")


def jobs_dir():
    return HOME / "dispatch"


def known(profile):
    return bool(PROFILE.match(profile)) and profile != "gtm-lead" and (PROFILES_DIR / profile / "SOUL.md").is_file()


def running():
    root = jobs_dir()
    return sorted(p.name for p in root.iterdir() if p.is_dir() and not (p / "exit").exists()) if root.is_dir() else []


def spawn(job):
    """Detached, so it outlives gtm-lead's turn."""
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "_run", job], start_new_session=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd="/tmp")


def start(profile, instruction, launch=spawn):
    instruction = (instruction or "").strip()
    if (HOME / "STOP").exists():
        return {"status": "refused", "why": "STOP is set: nothing runs"}
    if not known(profile):
        return {"status": "refused", "why": f"no profile called {profile}"}
    if not instruction or len(instruction) > MAX_REQUEST:
        return {"status": "refused", "why": f"say what to do, in under {MAX_REQUEST} characters"}
    if len(running()) >= MAX_RUNNING:
        return {"status": "refused", "why": f"{MAX_RUNNING} jobs are already running: try again when one ends"}
    job = uuid.uuid4().hex[:16]
    folder = jobs_dir() / job
    folder.mkdir(parents=True, mode=0o700)
    (folder / "request.txt").write_text(HEADER + instruction)
    (folder / "meta.json").write_text(json.dumps({"profile": profile, "at": time.time(), "instruction": instruction[:200]}))
    launch(job)
    return {"status": "running", "job": job, "profile": profile}


def report(profile, code, answer):
    head = f"{profile} finished" if code == 0 else f"{profile} failed (exit {code})"
    text = answer.strip()
    if len(text) > MAX_POST:
        text = text[:MAX_POST] + "\n\n(cut short. The full answer is in the job's folder.)"
    return f"{head}:\n\n{text or '(no answer)'}"


def run(job):
    folder = jobs_dir() / job
    meta = json.loads((folder / "meta.json").read_text())
    profile = meta["profile"]
    try:
        done = subprocess.run([HERMES, "-p", profile, "chat", "--query-file", str(folder / "request.txt"), "--oneshot", "-Q"],
                              capture_output=True, text=True, timeout=RUN_LIMIT, cwd="/tmp")
        code, answer, log = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired as late:
        code, answer, log = 124, (late.stdout or b"").decode(errors="ignore"), "stopped at the time limit"
    answer = "\n".join(line for line in answer.splitlines() if not line.startswith(("session_id:", "⚠")))
    (folder / "answer.txt").write_text(answer)
    (folder / "log.txt").write_text(log[-20000:])
    (folder / "exit").write_text(str(code))
    post = folder / "post.txt"
    post.write_text(report(profile, code, answer))
    subprocess.run([HERMES, "-p", "gtm-lead", "send", "-t", "slack", "-q", "-f", str(post)], capture_output=True, timeout=120, cwd="/tmp")


def result(job):
    folder = jobs_dir() / job
    if not JOB_ID.match(job or "") or not folder.is_dir():
        return {"status": "error", "why": "no such job"}
    meta = json.loads((folder / "meta.json").read_text())
    if not (folder / "exit").exists():
        return {"status": "running", "job": job, "profile": meta["profile"]}
    code = int((folder / "exit").read_text())
    return {"status": "done" if code == 0 else "failed", "job": job, "profile": meta["profile"], "exit": code,
            "answer": (folder / "answer.txt").read_text()[-12000:]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("profile")
    s.add_argument("instruction")
    r = sub.add_parser("result")
    r.add_argument("job")
    sub.add_parser("list")
    i = sub.add_parser("_run")
    i.add_argument("job")
    a = ap.parse_args(argv)
    if a.cmd == "_run":
        run(a.job)
        return 0
    out = start(a.profile, a.instruction) if a.cmd == "start" else result(a.job) if a.cmd == "result" else {"running": running()}
    print(json.dumps(out))
    return 0 if out.get("status") not in ("refused", "error") else 1


if __name__ == "__main__":
    sys.exit(main())
